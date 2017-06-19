# imports - standard imports
import os

# imports - third-party imports
from flask import request, jsonify
import addict

# imports - module imports
from candis.config              import CONFIG
from candis.util                import (
    assign_if_none, get_rand_uuid_str, json_load, get_timestamp_str
)
from candis.resource            import R
from candis.data                import cdata
from candis.app.server.app      import app
from candis.app.server.response import Response

FFORMATS         = json_load(os.path.join(R.Path.DATA, 'file-formats.json'))
ABSPATH_STARTDIR = os.path.abspath(CONFIG.App.STARTDIR)

def get_file_format(file_):
    format_ = None

    if not file_:
        _, ext = os.path.splitext(file_)

        for metadata in FFORMATS:
            for extension in metadata['extensions']:
                if ext == extension:
                    format_ = metadata['name']

                    break

    return format_

def discover_resource(path, level = None, filter_ = None):
    tree      = addict.Dict()
    tree.path = path
    tree.dirs, tree.files = [ ], [ ]

    for file_ in os.listdir(path):
        relpath = os.path.join(path, file_)
        abspath = os.path.abspath(relpath)

        if os.path.isfile(abspath):
            if filter_:
                format_ = get_file_format(file_)

                if format_ in filter_:
                    size        = os.path.getsize(abspath)

                    wrap        = addict.Dict()
                    wrap.name   = file_
                    wrap.size   = size
                    wrap.format = format_

                    tree.files.append(wrap)

        if os.path.isdir(abspath):
            resource    = discover_resource(
                path    = relpath,
                level   = level,
                filter_ = filter_
            )

            wrap          = addict.Dict()
            wrap.resource = resource

            tree.dirs.append(wrap)

    return tree

@app.route(CONFIG.App.Routes.RESOURCE, methods = ['GET', 'POST'])
def resource(filter_ = ['CDATA', 'CEL'], level = None):
    response  = Response()

    startdir  = CONFIG.App.STARTDIR

    tree      = discover_resource(
      path    = startdir,
      level   = level,
      filter_ = filter_
    )

    response.set_data(tree)

    dict_     = response.to_dict()
    json_     = jsonify(dict_)
    code      = response.code

    return json_, code

@app.route(CONFIG.App.Routes.READ, methods = ['GET', 'POST'])
def read():
    response    = Response()

    path        = request.args.get('path')
    name        = request.args.get('name')

    if not path:
        if not name:
            relpath = os.path.join(path, name)

            # TODO: check if file exists, set error if not.

            format_ = get_file_format(name)

            if format_ == 'CDATA':
                pass
        else:
            # TODO: set response error: filename not provided
            pass
    else:
        # TODO: set response error: path not provided
        pass

    dict_       = response.to_dict()
    json_       = jsonify(dict_)
    code        = response.code

    return json_, code

@app.route(CONFIG.App.Routes.WRITE, methods = ['POST'])
def write():
    response   = Response()

    filename   = request.args.get('name', get_timestamp_str())
    format_    = request.args.get('format')
    buffer_    = request.args.get('buffer')

    if format_ == 'CDATA':
        file_  = '{name}.{ext}'.format(name = filename, ext = '.cdata')
        path   = os.path.join(ABSPATH_STARTDIR, file_)

        try:
            cdata.write(path, buffer_)
        except TypeError as e:
            # TODO: set response error: invalid buffer
            pass
    else:
        # TODO: set response error: cannot write file, invalid file format.
        pass

    dict_      = response.to_dict()
    json_      = jsonify(dict_)
    code       = response.code

    return json_, code
