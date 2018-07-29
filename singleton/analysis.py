from pyramid.view import view_config
import os
import json
import numpy as np
import csv
from pyramid.response import FileResponse

# @view_config(route_name='analysis',
#              renderer='analysis.html')
# def analysis_view(request):
#
#     # TODO ensure the formatting of the file is a-ok!
#
#     # TEMPORARY: location of test files
#     file = os.path.abspath(os.path.dirname(__file__)) + "/tmp/mdp.sampleDist.1.0.full.csv"
#     samples_info_file = os.path.abspath(os.path.dirname(__file__)) + "/tmp/mdp.rpkm.1.0.samples.csv"
#
#     # get the number of columns containing data in the csv file
#     with open(file, 'r') as f:
#         num_cols = len(f.readline().split(','))
#
#     data = np.genfromtxt(file, delimiter=',', names=True, usecols=range(1,num_cols), dtype=float)
#     samples = np.genfromtxt(samples_info_file, delimiter=',', skip_header=1, dtype=str)
#
#     return { 'data'     :   json.dumps(data.tolist()),
#              'labels'   :   json.dumps(data.dtype.names),
#              'samples'  :   json.dumps(dict(samples))}

@view_config(route_name='lasso',
             renderer='json')
def lasso(request):
    # lassoData is an array containing the sample ids selected
    # ["sample1", "sample2", ...]
    lassoData = json.loads(request.body.decode())['lassoData']
    data = get_matrix(lassoData)
    gene_expression_data = data[0]
    highest_ave = data[1]
    return { 'matrix' : gene_expression_data,
            'average' : highest_ave }


def get_matrix(lassoData):
    file = os.path.abspath(os.path.dirname(__file__)) + "/tmp/mdp.rpkm.1.0.csv"
    expression = list(csv.reader(open(file), delimiter=','))
    #expression:
    #   [[''     , 'sample1', 'sample2', 'sample3', 'sample4', ...],
    #    ['gene1', '0'      ,      '1' ,     '100',     '2.2', ...],
    #    ['gene2', '5.5'    ,     '20' ,       '0',     '2.5', ...],
    #    ...]]

    cols = []   # store the index of the relevant sample ids
    index = 1 # start at 1 to account for first column containing row names
    # Get the index of the columns containing the data for the lassoed sample ids
    for sample_id in expression[0][1:]:
        if sample_id in lassoData:
            cols.append(index)
        index += 1

    averages = [ { 'average' : row_average(row, cols), 'gene' : row[0] } for row in expression[1:]]

    # sorted_list is of the form [ { 'average' : 2.2, 'gene' : gene1 }, ... ]
    sorted_list = sorted(averages, key=lambda k: k['average'], reverse=True)

    # matrix is of the form { sample_id : { gene_id1 : exp1, gene_id2 : exp2... }, ... }
    matrix = { expression[0][col] : { row[0] : float(row[col]) for row in expression[1:] } for col in cols }

    return [matrix, sorted_list]




def row_average(row, indexes):
    sum = 0

    for index in indexes:
        sum += float(row[index])

    return sum/len(indexes)



# EXPORT

## MDS SCATTERPLOT (.png)
## TABLE (.csv)
@view_config(route_name='exportGeneExpressions',
             renderer='csv')
def export_gene_expression(request):
    """
    Export to a csv file the samples lassoed, against the
    gene expressions ordered from highest average to lowest.
    """

    # Get file
    file = os.path.abspath(os.path.dirname(__file__)) + "/tmp/new.csv"

    # matrix is of the form { sample_id : { gene_id1 : exp1, gene_id2 : exp2... }, ... }
    matrix = json.loads(request.body.decode())['matrix']

    # average_data is of the form [ { 'average' : 2.2, 'gene' : gene1 }, ... ]
    # sorted from largest average to smallest
    average_data = json.loads(request.body.decode())['average']


    # Get header
    sampleIDs = [sampleID for sampleID in matrix.keys()]

    # Get rows
    gene_expressions = []
    for data in average_data:
        new_row = []
        new_row.append(data['gene'])
        for sampleID in sampleIDs:
            new_row.append(matrix[sampleID][data['gene']])
        gene_expressions.append(new_row)

    # account for row names
    sampleIDs.insert(0, '')

    return {
        'header' : sampleIDs,
        'rows'   : gene_expressions,
        'file'   : file
    }
