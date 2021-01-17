#!/usr/bin/python
# -*- coding: utf_8 -*-

"""
.. module:: dump_us.py
.. moduleauthor:: T'Mir D. Julius <tdjulius@unimelb.edu.au>

:Copyright: T'Mir D. Julius, 2020
:Contact: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Updated: 17/12/2020

"""

def main():

    """
    :Description: A script to harmonise names based on a cosine distance of a given tolerance. Names that are within a\
     given cosine distance are assigned the same IPA ID. The IPA ID/IPA Applt ID are written to the ipa_id table

    """

    db = mt.get_db1()
    cur = db.cursor()

    # Select the clean names for all entities
    cur.execute("""SELECT a.appln_id, a.appln_nr, b.us_att_id, a.name_1, a.name_2, c.recovered_firm, """ 
                """a.add_1, a.add_2, a.city, a.region, a.postcode, a.country """
                """FROM ip5_uspto_pat_agent_clean_9_exp b """
                """JOIN ip5_uspto_pat_agent_raw a USING(appln_id)"""
                """JOIN ip5_uspto_pat_agent_clean c USING(appln_id)""")

    results = list(cur.fetchall())

    out_file = open("data/ip5_uspto_tdj_addresses.txt", 'w')
    out_csv = csv.writer(out_file)
    out_csv.writerow(['appln_id', 'appln_nr', 'us_att_id', 'name_1', 'name_2', 'cleaned_name', 'address_1', 'address_2',
                      'city', 'region', 'postcode', 'country'])
    for result in results:
        out_csv.writerow(result)
    out_file.close()


if __name__ == '__main__':
    import csv
    import mysql_tools as mt
    main()
