import os
import uuid
import shutil
import swiftclient as swc
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from .processing.gen_uid import gen_uid
from .users import logged_in

import logging
log = logging.getLogger(__name__)

@view_config(route_name="upload", renderer='upload.html')
def upload(request):
    if not logged_in(request):
        return HTTPFound(request.route_url('login'))
    return {}


@view_config(route_name="store_csv_file", renderer='upload.html')
def store_csv_file(request):
    if not request.POST:
        return HTTPFound(request.route_url("upload"))

    tmp_folder = os.path.abspath(os.path.dirname(__file__)) + '/tmp'

    #  TODO resolve warning
    #  WARNING: Internet Explorer is known to send an absolute file
    # *path* as the filename.  This example is naive; it trusts
    # user input.
    filename = request.POST['dataset'].filename
    file = request.POST['dataset'].file

    # TODO verify a file was uploaded


    # We first write to a temporary file to prevent incomplete files from
    # being used.
    file_path = os.path.join(tmp_folder, filename)
    temp_file_path = file_path + '~'

    # Using the filename like this without cleaning it is very
    # insecure so please keep that in mind when writing your own
    # file handling.
    file.seek(0)

    with open(temp_file_path, 'wb') as output_file:
        shutil.copyfileobj(file, output_file)

    # Now that we know the file has been fully saved to disk move it into place.
    os.rename(temp_file_path, file_path)

    # now, handle upload to Object Storage
    if not logged_in(request):
        file.close()
        request.session.flash("Temporary upload to server OK, but no upload to Object "
                              "Storage as you are not logged in")
        return HTTPFound(request.route_url("new"))

    swconn = get_object_storage_conn(request)

    uid = request.session['user']['id']
    container_names = [cntr['name'] for cntr in swconn.get_account()[1]]
    if uid not in container_names:
        swconn.put_container(uid)

    dataset_id = gen_uid()
    dbsess = request.dbsession
    try:
        swconn.get_object(uid, dataset_id)
        request.session.flash("Upload failed: a file of that ID already exists.")
        return HTTPFound(request.route_url("upload"))
    except swc.exceptions.ClientException:
        # filename does not already exist, can proceed with the upload
        file.seek(0)
        try:
            if filename.endswith('.csv'):
                content_type = 'text/csv'
            elif filename.endswith('.hdf5'):
                content_type = 'application/x-hdf'
            else:
                request.session.flash("Upload failed: invalid file type")
                return HTTPFound(request.route_url("upload"))

            swconn.put_object(uid,
                              dataset_id,
                              contents=file.read(),
                              content_type=content_type)

            dataset_name = request.POST['name']

            dataset_desc = ''
            if request.POST['desc']:
                dataset_desc = request.POST['desc']

            public_access = 1 if request.POST['public'] == "Yes" else 0

            dataset_sql = ("INSERT INTO dataset(id, user_id, name, {} public_access, upload_date) "
                          "VALUE (:dsid, :uid, :name, {} :public, NOW());")
            if dataset_desc:
                dataset_sql = dataset_sql.format("description,", ":desc,")
            else:
                dataset_sql = dataset_sql.format("", "")

            values = dict(dsid=dataset_id, uid=uid,
                          name=dataset_name, desc=dataset_desc,
                          public=public_access)

            dbsess.execute(dataset_sql, values)
            dbsess.commit()
            request.session.flash('Dataset upload successful!')
            return HTTPFound(request.route_url("dashboard"))
        except swc.exceptions.ClientException as e:
            log.error(str(e))
            request.session.flash("Upload failed: Swift error")
            return HTTPFound(request.route_url("upload"))
        except Exception as e:
            log.error(str(e))
            swconn.delete_object(uid, dataset_id)
            dbsess.rollback()
            request.session.flash("Upload failed: unexpected error")
            return HTTPFound(request.route_url("upload"))
    finally:
        file.close()

def get_object_storage_conn(request):
    url = request.registry.settings['swift.url']
    username = request.registry.settings['swift.username']
    projname = request.registry.settings['swift.projname']
    password = request.registry.settings['swift.password']

    return swc.client.Connection(authurl=url,
                                 user=username,
                                 key=password,
                                 tenant_name=projname,
                                 auth_version='2')





