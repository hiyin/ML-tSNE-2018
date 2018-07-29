import csv

try:
    from StringIO import StringIO # python 2
except ImportError:
    from io import StringIO # python 3

class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        file = value.get('file')

        # Open output csv file
        with open(file, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(value.get('header', []))
            writer.writerows(value.get('rows', []))

        request = system.get('request')
        response = request.response

        response.content_type = 'text/csv'
        response.content_disposition = 'attachment; filename=' + file

        return