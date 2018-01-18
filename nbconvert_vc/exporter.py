# -*- coding: utf-8 -*-

import io
import json
import os

from nbconvert.exporters.exporter import Exporter
from nbconvert.exporters.notebook import NotebookExporter
import nbformat
from traitlets import default
import yaml

from . import output_types
from . import util


class _Cell(dict):
    pass


def _cell_representer(dumper, data):
    """
    A custom YAML representer for notebook cells.

    Ensures that the source code uses literal ("|") form.
    """
    util.handle_metadata(data)
    if 'outputs' in data and len(data['outputs']) == 0:
        del data['outputs']

    node = dumper.represent_mapping(
        'tag:yaml.org,2002:map', data, flow_style=False)

    for key, val in node.value:
        if key.value == 'source':
            val.style = '|'

    CELL_ORDER = (
        'cell_type', 'source', 'outputs', 'metadata', 'execution_count'
    )
    util.reorder(node.value, CELL_ORDER)
    return node


class _Output(dict):
    pass


def _get_output_representer(output_dir):
    """
    A custom YAML representer for output entries. Saves non-inline outputs to
    separate files. Ensures that inline outputs are written out in literal
    style.
    """

    def output_representer(dumper, data):
        util.handle_metadata(data)

        if 'data' in data:
            if data['output_type'] in ('display_data', 'execute_result'):
                for key, val in data['data'].items():
                    if key not in output_types.INLINE_TYPES:
                        filename = output_types.save_output(
                            output_dir, key, val)
                        data['data'][key] = filename
            data['data'] = dict(data['data'])

        node = dumper.represent_mapping(
            'tag:yaml.org,2002:map', data, flow_style=False)

        if data['output_type'] == 'stream':
            for key, val in node.value:
                if key.value == 'text':
                    val.style = '|'
        elif data['output_type'] in ('display_data', 'execute_result'):
            for key, val in node.value:
                if key.value == 'data':
                    util.reorder(val.value, ('text/plain',))
                    for key, val in val.value:
                        if key.value in output_types.INLINE_TYPES:
                            val.style = '|'

        OUTPUT_ORDER = (
            'output_type', 'data', 'metadata', 'execution_count'
        )
        util.reorder(node.value, OUTPUT_ORDER)
        return node
    return output_representer


def _node_representer(dumper, data):
    """
    Custom YAML representer for all other NotebookNode instances. Basically
    just a hint to the YAML dumper that NotebookNode objects can be used like
    dictionaries.
    """
    return dumper.represent_mapping(
        'tag:yaml.org,2002:map', dict(data), flow_style=False)


def _make_dumper(output_dir):
    """
    Make a custom YAML Dumper with all of the custom representers defined
    above.
    """
    class NbDumper(yaml.SafeDumper):
        pass
    yaml.add_representer(
        _Output,
        _get_output_representer(output_dir),
        Dumper=NbDumper)
    yaml.add_representer(
        _Cell,
        _cell_representer,
        Dumper=NbDumper)
    yaml.add_representer(
        nbformat.notebooknode.NotebookNode,
        _node_representer,
        Dumper=NbDumper)
    return NbDumper


class VCExporter(Exporter):
    """
    A custom exporter for the ipynb.yaml format.
    """

    @default('file_extension')
    def _file_extension_default(self):
        return '.ipynb.yaml'

    def from_notebook_node(self, nb, resources=None, **kw):
        # Convert the input file to nbformat version 4, so we only have to deal
        # with one format.
        if nb.nbformat < 4:
            nb = nbformat.convert(nb, 4)

        nb, resources = super().from_notebook_node(nb, resources, **kw)

        output_dir = resources['output_files_dir']
        util.ensure_new_directory(output_dir)

        dumper = _make_dumper(output_dir)

        out = {}
        out['cells'] = []
        for cell in nb.cells:
            out_cell = _Cell(cell)
            if hasattr(cell, 'outputs'):
                out_cell['outputs'] = [
                    _Output(x) for x in cell.outputs]
            out['cells'].append(out_cell)

        out['nbformat'] = nb.nbformat
        out['nbformat_minor'] = nb.nbformat_minor
        out['metadata'] = dict(nb.metadata)

        return (
            yaml.dump(out, Dumper=dumper, default_flow_style=False),
            resources)


class VCImporter(Exporter):
    """
    An exporter that converts the .ipynb.yaml format back into a standard
    .ipynb file.
    """

    @default('file_extension')
    def _file_extension_default(self):
        return '.ipynb'

    def from_filename(self, filename, resources=None, **kw):
        root_dir = os.path.dirname(filename)

        with io.open(filename, encoding='utf-8') as f:
            tree = yaml.load(f)

        for cell in tree['cells']:
            if 'metadata' not in cell:
                cell['metadata'] = {}
            if 'outputs' in cell:
                for output in cell['outputs']:
                    if (output['output_type'] != 'stream' and
                            'metadata' not in output):
                        output['metadata'] = {}
                    if 'data' in output:
                        for key, val in list(output['data'].items()):
                            output['data'][key] = output_types.load_output(
                                root_dir, key, val)
            elif cell['cell_type'] == 'code':
                cell['outputs'] = []

        output_file = io.StringIO()
        json.dump(tree, output_file)
        output_file.seek(0)

        # Send the above ad-hoc JSON through nbconvert's built-in notebook
        # exporter so all of the formatting details are the same as for
        # standard notebooks.
        notebook_exporter = NotebookExporter()
        return notebook_exporter.from_file(
            output_file, resources=resources, **kw)
