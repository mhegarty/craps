import os
basedir = os.path.abspath(os.path.dirname(__file__))

DB_URL = os.environ['CRAPS_DB_URL']  or \
         'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')