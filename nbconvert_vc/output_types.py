# -*- coding: utf-8 -*-

import codecs
import hashlib
import mimetypes
import os
import tempfile


mimetypes.add_type('text/latex', '.ltx')


BINARY_TYPES = set(['image/png', 'image/jpeg'])
INLINE_TYPES = set(['text/plain'])


def encode_content(mime, content):
    if mime in BINARY_TYPES:
        return codecs.decode(content.encode('ascii'), 'base64')
    else:
        return content.encode('utf-8')


def save_output(output_dir, mime, content):
    encoded_content = encode_content(mime, content)

    with tempfile.NamedTemporaryFile(
             dir=output_dir, delete=False) as fout:
        fout.write(encoded_content)

    ext = mimetypes.guess_extension(mime)
    m = hashlib.sha256()
    m.update(encoded_content)
    filename = os.path.join(output_dir, m.hexdigest()[:16] + ext)

    os.replace(fout.name, filename)
    return filename


def load_output(root_dir, mime, content):
    if mime in INLINE_TYPES:
        return content
    with open(os.path.join(root_dir, content), 'rb') as f:
        loaded_content = f.read()
    if mime in BINARY_TYPES:
        return codecs.encode(loaded_content, 'base64').decode('ascii')
    else:
        return loaded_content.decode('utf-8')
