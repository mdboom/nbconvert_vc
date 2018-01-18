# -*- coding: utf-8 -*-


import os
import shutil


def handle_metadata(data):
    """
    Remove empty metadata dictionaries on nodes.
    """
    if 'metadata' in data:
        metadata = dict(data['metadata'])
        if len(metadata):
            data['metadata'] = metadata
        else:
            del data['metadata']


def ensure_new_directory(path):
    """
    Ensures that a directory exists and is empty.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)
    if not os.path.isdir(path):
        os.makedirs(path)


_ORDER_MAP_CACHE = {}


def reorder(node, order):
    """
    Reorder a given YAML map node so that the keys appear in the specified
    order.
    """
    order_map = _ORDER_MAP_CACHE.get(order)
    if order_map is None:
        order_map = dict((key, i) for (i, key) in enumerate(order))
        _ORDER_MAP_CACHE[order] = order_map

    node.sort(key=lambda x: order_map.get(x[0].value, len(order_map)))
