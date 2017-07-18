#!/usr/bin/env python

# -*- coding: utf-8 -*-
#
"""vertex.py - convert your SQL table or query to JSON/CSV/XML format."""

# python stdlib imports
import csv
import sys
import json
import argparse
from itertools import izip
from datetime import time, date, datetime

# The HPE Vertica Python driver
import hp_vertica_client as adapter


__version__ = '0.0.1a'


class Arguments(argparse.Namespace):

    def __init__(self, **kwargs):
        super(Arguments, self).__init__(**kwargs)

    @property
    def conn_options(self):
        options = dict()
        options['database'] = self.database
        options['host']     = self.host
        options['user']     = self.user
        options['password'] = self.password
        return options

    @property
    def io_options(self):
        return {}

    @property
    def general_options(self):
        return {}


def parse_args(args=None, namespace=Arguments()):
    """Parse sys.argv options."""

    parser = argparse.ArgumentParser(
        prog='vertex.py',
        description=__doc__,
        conflict_handler='resolve'
    )

    # CONNECTION OPTIONS
    group = parser.add_argument_group(title='CONNECTION OPTION',
        description='Specifies all settings required to make a connection.')

    group.add_argument('-h', '--host', dest='host', default='localhost',
        help='the name of the host. (default localhost)') 

    group.add_argument('-p', '--port', dest='port', default=5433, type=int,
        help='the port number on which HP Vertica listens. (default 5433)')

    group.add_argument('-d', '--database', dest='database', required=False,
        help='specifies the name of the database to connect to.')

    group.add_argument('-u', '--user', dest='user', default='dbadmin',
        help='connects to the database as the user username instead of the ' \
             'default user.')

    group.add_argument('-P', '--password', dest='password', required=False,
        help='the password for the user\'s account.')

    group.add_argument('-s', '--sslmode', dest='sslmode', default='prefer',
        choices=['require', 'prefer', 'allow', 'disable'], 
        help='specifies how (or whether) clients use SSL when connecting '   \
             'to servers. The default value is prefer, meaning to use SSL '  \
             'if the server offers it.')

    group.add_argument('-l', '--label', dest='sessionlabel', default='python',
        help='Sets a label for the connection on the server. This value '    \
             'appears in the session_id column of the V_MONITOR.SESSIONS '   \
             'system table.')

    # INPUT AND OUTPUT OPTIONS
    group = parser.add_argument_group(title='INPUT AND OUTPUT OPTIONS',
        description='Specifies options to control how your request is '      \
                    'interpreted and how the response is generated.')

    mutual_args = group.add_mutually_exclusive_group(required=True)

    mutual_args.add_argument('-i', '--input', dest='input',
        help='query to exeport.')

    mutual_args.add_argument('-t', '--table', dest='table',
        help='table to exeport.')

    group.add_argument('-o', '--output', dest='filename', required=False,
        help='writes all query output into file filename.')

    group.add_argument('-F', '--format', dest='format', default='json',
        choices=['csv', 'json', 'xml'], help='output format for query.')

    # GENERAL OPTIONS
    group = parser.add_argument_group(title='GENERAL OPTIONS')

    group.add_argument('-V', '--version', action='version', 
        version='%(prog)s {}'.format(__version__))

    group.add_argument('-?', '--help', action='help',
        help='displays help about line arguments and exits.')

    return parser.parse_args(args=args, namespace=namespace)


def json_serial(field):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(field, (time, date)):
        return field.isoformat()
    raise TypeError("Type %s not serializable" % type(field))
    

def to_json(cursor):
    """Convert your SQL table or query to JSON format."""
    colnames =  tuple(colmeta.name for colmeta in cursor.description)
    if len(colnames) != len(set(colnames)):
        raise ValueError('columns names are not unique')
    sys.stdout.write('[')
    while True:
        row = cursor.fetchone()
        if not row:
            break
        sys.stdout.write(json.dumps(dict(izip(colnames, row)), default=json_serial))
        writer(',\n')
    writer(']\n')


if __name__ == '__main__':
    if not sys.argv[1:]:
        parse_args(args=['--help',])
    args = parse_args()
    print args.conn_options
   # database, user, password, host, port = args.database, args.user, args.password, args.host, args.port
   # query = args.command

   # connection = adapter.connect(database=database, user=user, password=password, host=host, port=port)
   # cursor = connection.cursor()
   # cursor.execute(query)

   # if args.format == 'json':
   #     to_json(cursor)
   # elif args.format == 'csv':
   #     to_csv(cursor)
   # elif args.format == 'xml':
   #     to_xml(cursor)
   # else:
   #     to_html(cursor)

   # cursor.close()
   # connection.close()

# EOF
