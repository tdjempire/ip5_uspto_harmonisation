"""
.. module:: mysql_tools
.. moduleauthor:: T'Mir D. Julius <tjulius@swin.edu.au>

:Copyright: T'Mir D. Julius for The Centre for Transformative Innovation
Swinburne University of Technology, 2015
:Contact: T'Mir D. Julius <tdj@tdjulius.com>
:Updated: 20/12/2020
"""
# In the port from Python2 to Python3, rather than update the references to MySQLdb,
# it was easier to import the old library with the new name
import pymysql as MySQLdb

password = ''
host = ''
prodhost = ''
user = ''


def get_db1():
    """
    Get the db1 database object

    :return:
        A MySQL db object for the database. You should put your own MySQL server username/password in
    """
    return MySQLdb.connect(host=prodhost,
                           user=user,
                           passwd=password,
                           charset='utf8',
                           use_unicode=True,
                           db="ip5")
