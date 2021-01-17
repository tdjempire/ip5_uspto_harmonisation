#!/usr/bin/python3
# -*- coding: utf_8 -*-

"""
.. module:: vectorisemysql
.. moduleauthor:: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Contact: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Updated: 23/12/2020
"""


def main():

    """
    :Description: A script that takes the clean_names from the ipa_applt_clean table, and uses the weighted bigram dict\
    to create a vector. The vector is then stored as a blob in the ipa_applt_clean table

    """
    db = mt.get_db1()
    cur = db.cursor()

    cur.execute('SELECT a.appln_id, a.recovered_firm FROM ip5_uspto_pat_agent_clean a '
                'WHERE a.is_firm = 1')

    results = cur.fetchall()

    print(len(results))

    weights = json.load(open('data/bigramdictionaryattorneys.txt'))

    i = 0.0
    while len(results):
        print(i)
        for result in results:
            i += 1
            applt_id, clean_name = result

            vector = {}

            lletter = '|'

            try:
                for letter in clean_name:
                    vector[lletter+letter] = vector.get(lletter+letter, 0) + weights.get(lletter+letter, 0.05)
                    lletter = letter
            except Exception:
                # print e
                print(clean_name)
                print(applt_id)
                exit()

            vector[lletter+'|'] = weights[lletter+'|']

            string = ''

            for key, value in vector.items():
                string =  string + str(key).strip()+':'+str(value).strip()+','

            cur.execute("""UPDATE ip5_uspto_pat_agent_clean SET vector = %s WHERE appln_id = %s""", (string, applt_id))

            if i % 1000 == 0:
                print('applt_id = {0}, i = {1}, name = {2} and vector = {3}'.format(applt_id, i, clean_name, vector))
                db.commit()

        db.commit()


if __name__ == "__main__":
    import json
    import mysql_tools as mt
    main()
