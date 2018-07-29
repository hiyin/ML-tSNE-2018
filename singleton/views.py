from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import colander
import swiftclient as swc

import os
import json
import numpy as np
import csv
from io import BytesIO

from .mailers import send_email
from .users import logged_in
from .upload import get_object_storage_conn

import logging
log = logging.getLogger(__name__)

DATASET_ENCODING = 'utf-8'

# Look for files under templates
@view_config(route_name="home",
             renderer="home.html")
def home_view(request):
    return {}


@view_config(route_name='new',
             renderer='new.html')
def new_view(request):
    if not logged_in(request):
        return HTTPFound(request.route_url('login'))

    dashboard_url = request.route_url('dashboard')

    if 'dataset_id' not in request.params:
        msg = "Error: analysis requested, but no dataset specified. Please select 'Analyse' for your chosen dataset"
        request.session.flash(msg)
        return HTTPFound(dashboard_url)

    dataset_id = request.params['dataset_id']

    # Check samples file has been included
    if 'samples_info_file' in request.params:
        samples_fpath = request.params['samples_info_file']
        samples = dict(np.genfromtxt(samples_fpath, delimiter=',', skip_header=1, dtype=str))
    else:
        samples = None

    if not dataset_exists(request, dataset_id):
        msg = "Error: requested dataset does not exist."
        request.session.flash(msg)
        return HTTPFound(dashboard_url)

    if not correct_analysis_permissions(request, dataset_id):
        msg = "Error: you do not have permission to analyse requested dataset."
        request.session.flash(msg)
        return HTTPFound(dashboard_url)

    sample_data, dataset_name = get_sample_dataset(request, dataset_id)

    if not valid_sample_dataset(sample_data):
        msg = "Error: the requested dataset is not a valid sample file"
        request.session.flash(msg)
        return HTTPFound(dashboard_url)

    # get the number of columns containing data in the csv file
    reader = csv.reader(sample_data.decode(DATASET_ENCODING).splitlines())
    header = next(reader)
    num_cols = len(header)

    dataset = BytesIO(sample_data)
    data = np.genfromtxt(dataset, delimiter=',', names=True, usecols=range(1,num_cols), dtype=float)

    return { 'dataset_name': json.dumps(dataset_name),
             'data': json.dumps(data.tolist()),
             'labels': json.dumps(data.dtype.names),
             'samples': json.dumps(samples)}

# Start: enable the sample population display
# @view_config(route_name='new',
#                  renderer='new.html')
# def new_view(request):
#     file = os.path.abspath(os.path.dirname(__file__)) + "/tmp/mdp.sampleDist.1.0.full.csv"
#     samples_info_file = os.path.abspath(os.path.dirname(__file__)) + "/tmp/mdp.rpkm.1.0.samples.csv"
#     # get the number of columns containing data in the csv file
#     with open(file, 'r') as f:
#         num_cols = len(f.readline().split(','))
#     data = np.genfromtxt(file, delimiter=',', names=True, usecols=range(1, num_cols), dtype=float)
#     samples = np.genfromtxt(samples_info_file, delimiter=',', skip_header=1, dtype=str)
#     return {'data': json.dumps(data.tolist()),
#             'labels': json.dumps(data.dtype.names),
#             'samples': json.dumps(dict(samples))}
# End: enable the sample population display

def dataset_exists(request, dataset_id):
    """
    Return whether the specified dataset exists.
    """
    dbsess = request.dbsession
    query = "SELECT * FROM dataset WHERE id = :dataset_id"
    result = dbsess.execute(query, {'dataset_id':dataset_id})
    if not result.fetchone():
        return False
    else:
        return True


def correct_analysis_permissions(request, dataset_id):
    """
    Return whether the logged in user has permission to analyse
    the requested dataset. Assumes specified dataset does exist.
    """
    if not logged_in(request):
        return False

    user_id = request.session['user']['id']
    dbsess = request.dbsession
    query = "SELECT user_id FROM dataset WHERE id = :dataset_id"
    result = dbsess.execute(query, {'dataset_id':dataset_id}).fetchone()
    try:
        owner_id = result['user_id']
        return user_id == owner_id
    except TypeError:
        # fetchone returned None, so the dataset was not found
        return False


def get_sample_dataset(request, dataset_id):
    """
    Get dataset from server / database.
    """
    uid = request.session['user']['id']

    dbsess = request.dbsession
    query = "SELECT name FROM dataset WHERE id = :dataset_id"
    result = dbsess.execute(query, {'dataset_id':dataset_id})
    name = result.fetchone()['name']

    swconn = get_object_storage_conn(request)
    try:
        headers, dataset = swconn.get_object(uid, dataset_id)
        log.info("got dataset {} from Swift with headers: ".format(dataset_id))
        log.info(headers)
        return dataset, name
    except swc.exceptions.ClientException:
        # object does not exist
        return None, None


def valid_sample_dataset(dataset):
    """
    Validate the contents of a sample dataset.

    A valid dataset should be a string representing
    the contents of a valid csv file, with column and
    row headers, where all data is numeric.

    This function does not do any validation of
    the column or row header format.
    """
    try:
        dataset = dataset.decode(DATASET_ENCODING)
    except TypeError:
        return False

    reader = csv.reader(dataset.splitlines())

    header = next(reader)
    ncols = len(header)

    for row in reader:
        if len(row) != ncols:
            return False

        for data in row[1:]:
            try:
                float(data)
            except ValueError:
                # value is not a float
                return False
    return True


@view_config(route_name='past',
             renderer='past.html')
def past_view(request):
    if not logged_in(request):
        return HTTPFound(request.route_url('login'))
    return {}

@view_config(route_name='dashboard',
             renderer='dashboard.html')
def dashboard_view(request):
    if not logged_in(request):
        return HTTPFound(request.route_url('login'))

    dbsess = request.dbsession
    uid = request.session['user']['id']
    query = "SELECT * FROM dataset WHERE user_id = :uid;"
    datasets = dbsess.execute(query, {'uid': uid}).fetchall()
    return dict(all_datasets=datasets)

@view_config(route_name='features',
             renderer='features.html')
def features_view(request):
    return {}

@view_config(route_name='about',
             renderer='about.html')
def about_view(request):
    return {}

@view_config(route_name='contact',
             renderer='contact.html')
def contact_view(request):
    return {}

@view_config(context=colander.Invalid, renderer="json")
def validation_error_view(exc, request):
    request.response.status_int = 400
    return exc.asdict()
