#!/usr/bin/python3
"""
.. module:: 2020_uspto_attorney_harmonisation
.. moduleauthor:: T'Mir D. Julius <tjulius@unimelb.edu.au>

:Contact: T'Mir D. Julius <tdj@tdjulius.com>
:Updated: 23/12/2020
"""


def clean_name(name):
    if name is None:
        return 0, ''

    name = ' ' + re.sub('[%s]' % re.escape(punct), '', name).upper() + ' '
    name = name.replace('-', ' ')

    new_name = name

    new_name = new_name.replace('/', ' ')

    for law_word in law_words:

        new_name = re.sub(law_word, "", new_name)
    if new_name != name:
        return 1, ' '.join(new_name.split()).strip()
    elif any([x.isdigit() for x in new_name]):
        return 1, ' '.join(new_name.split()).strip()
    else:
        return 0, ' '.join(new_name.split()).strip()


def main():

    """
    :Description: A script to clean the data imported from
    https://bulkdata.uspto.gov/data/patent/pair/economics/2014/csv.zip
    And move the cleaned data to a new table.
    """

    select_statement = """SELECT upper(name_1), upper(name_2), appln_id, add_1, add_2, city, postcode, region, country FROM """ \
                       """ip5_uspto_pat_agent_raw WHERE appln_id not in """ \
                       """(SELECT appln_id FROM ip5_uspto_pat_agent_clean) limit 10000 """

    db = mt.get_db1()
    cur = db.cursor()

    cur.execute(select_statement)

    results = cur.fetchall()

    i = 0

    while len(results):
        i += 1
        print(i)

        for result in results:
            name, name_2, appln_id, add_1, add_2, city, postcode, region, country = result
            is_ent, new_name = clean_name(name)

            if is_ent == 0:
                line_1 = name_2
                lis_ent, lnew_name = clean_name(line_1)
                # print(lis_ent, lnew_name)
                if lis_ent == 1:
                    is_ent = lis_ent
                    new_name = lnew_name
            #Any duplicates are the same, so just ignore the integrity error
            try:
                cur.execute("""INSERT INTO ip5_uspto_pat_agent_clean (appln_id, recovered_firm, is_firm) """ 
                            """values(%s, %s, %s) """,
                            [appln_id, new_name, is_ent])
            except pymysql.err.IntegrityError:
                print('yeah!')
                continue

        db.commit()
        cur.execute(select_statement)
        results = cur.fetchall()

if __name__ == '__main__':

    import mysql_tools as mt
    import string
    import re
    import pymysql

    #Sorted list of words identifying law offices
    law_words = ["(?<=[\.|,|\|\s|\(|\)])" + x + "(?=[\.|,|\|\s|\(|\)])" for x in sorted(
                        ['LLP',
                         '&',
                         'ASSOCIATES',
                         'LLP',
                         'PLLC',
                         'LLC',
                         'PC',
                         'PLC',
                         'INC',
                         'INCORPORATED',
                         'CORPORATION',
                         'CORP',
                         'IP',
                         'FIRM',
                         'OFFICE',
                         'OFFICES',
                         'GROUP',
                         'INTELLECTUAL PROPERTY',
                         'COMPANY',
                         'CO',
                         '&',
                         'ET AL',
                         'LLB',
                         'LLO',
                         'PA',
                         'AS'],
                        key=len)]

    punct = ''.join([x for x in string.punctuation if x not in ['&', '/', '-']])

    main()

