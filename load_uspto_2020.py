#!/usr/bin/python3
# -*- coding: utf_8 -*-

"""
.. module:: load_uspto_2020
.. moduleauthor:: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Contact: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Updated: 23/12/2020

"""


def main():
    """
    :Description: A script to import USPTO Attorney data into a MySQL db from the data at
    https://bulkdata.uspto.gov/data/patent/pair/economics/2014/csv.zip
    """
    db = mt.get_db1()
    cur = db.cursor()
    in_corr = open('data/correspondence_address_2014.csv')
    in_corr = csv.reader(in_corr)
    next(in_corr)
    count = 0
    rows = 0

    for line in in_corr:
        rows += 1
        if rows % 10000 == 0:
            db.commit()
            print(rows)

        appln_nr, name_1, name_2, line_1, line_2, city, p_code, state, blank, country, country_name, \
        customer_number = line
        try:
            appln_nr = int(appln_nr)
        except ValueError:
            print(appln_nr)
            continue

        cur.execute("""INSERT INTO ip5_uspto_pat_agent_raw """ 
                    """(appln_nr, name_1, name_2, add_1, add_2, city, postcode, region, country) """
                    """VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) """,
                    [appln_nr, name_1, name_2, line_1, line_2, city, p_code, state, country])
    db.commit()
    # Update the Patstat application IDs from the PATSTAT ids
    cur.execute("""UPDATE ip5_uspto_pat_agent_raw a JOIN ip5_uspto_pat_agent_2017 b USING(appln_nr) """
                """SET a.appln_id = b.appln_id WHERE b.appln_id IS NOT NULL """)
    db.commit()

    # Drop the patent agents that weren't used
    cur.execute("""DROP FROM ip5_uspto_pat_agent_raw WHERE appln_id IS NULL """)
    db.commit()

    # Drop applications with multiple, different agents
    cur.execute("""DROP FROM ip5_uspto_pat_agent_raw WHERE appln_nr = 10181097""")
    cur.execute("""DROP FROM ip5_uspto_pat_agent_raw WHERE appln_nr = 9526921""")
    cur.execute("""DROP FROM ip5_uspto_pat_agent_raw WHERE appln_nr = 12311234""")
    db.commit()


if __name__ == '__main__':
    import csv
    import mysql_tools as mt
    main()
