#!/usr/bin/python3
# -*- coding: utf_8 -*-

"""
.. module:: uspto_match_close
.. moduleauthor:: T'Mir D. Julius <tdjulius@unimelb.edu.au>

:Copyright: T'Mir D. Julius for The Melbourne Institute of Applied Economics and Social Research, The University of
 Melbourne, 2020
:Contact: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Updated: 17/07/2020

"""

import json
import mysql_tools as mt
from multiprocessing import Pool
import time

def tolerance():
    """
    Return the tolerance for the cosine distance to be considered a match

    :return:
        A double of the tolerance
    """
    return 0.9


def tabletol():
    """
    Use the tolerance to get the name of the IPA ID table

    :return:
        A string of the table name
    """
    return 'ip5_uspto_pat_agent_clean_'+str(tolerance()).split('.')[1]


def alpha_split(biglist):

    """
    Split up the list of names by first letter.

    :param biglist:
        A list of unique applicant names in alphabetical order
    :return:
        A list of names that all start with the same letter
        A second list of the rest of the list
    """
    # If there's a word in the list find the first letter
    if len(biglist[0][0]):
        first_alpha = biglist[0][0][0]
    else:
        return biglist[:1], biglist[1:]

    # Move names from one list to the other list while the names begin with the same letter.
    # When they don't, return both lists
    for j, entry in enumerate(biglist):
        if entry[0][0] != first_alpha:
            return biglist[:j], biglist[j:]


def get_names_list(names, max_len = 100):

    names_list = list(set([' '.join(x.split()[:2]) for x in names]))
    return (names_list, 2)


def compare(name_list, comparee, current_ipa_id, result_dicts):

    """
    A routine to compare a name to each other member of a list. Finds all items that belong to an IPA ID

    :param name_list: The list of names
    :param comparee: The name being compared
    :param current_ipa_id: The IPA ID of the comparee
    :return:
    """

    matches = list()
    ipadict = dict()

    # Start by adding the current name and IPA ID to the dictionary
    ipadict[comparee] = current_ipa_id
    adds, names = result_dicts[comparee]
    tidy_names, name_lens = get_names_list(names)
    index = 0

    while index < len(name_list):
        entry = name_list[index]
        c_adds, c_names = result_dicts[entry]
        comparer_names, c_name_len = get_names_list(c_names, name_lens)
        found = False
        for name in tidy_names:
            if name in comparer_names:
                for add in adds:
                    if add in c_adds:
                        # print()
                        # print(tidy_names, names)
                        # print(comparer_names, c_names)
                        # print()
                        matches.append(entry)
                        print(name, comparer_names)
                        if not found:
                            del name_list[index]
                            found = True


        # Otherwise, move on to the next list item

        index += 1

    # For each match found in the previous loop, recursively test these against the remaining list items. In this way
    # we chain the matches - eg. The groups are not order specific. If a is within the tolerance of b, and b is within
    # the tolerance of c, but c is not with a, they will still all be picked up.
    # print()
    # print("Matches for %s", current_ipa_id)
    # print(matches)
    # print()
    for match in matches:

        name_list, return_dict = compare(name_list, match, current_ipa_id, result_dicts)
        # print(return_dict)
        for key, val in return_dict.items():
            ipadict[key] = current_ipa_id
    return name_list, ipadict


# Define the matchdict here so as to make it within the scope of the callback function
matchdict = dict()
def get_matchdict():
    return matchdict


def update_match_dict(to_commit):
    """
    A callback function to add the result of each thread to the global result

    :param to_commit: The dict that is to be commited to the global dictionary
    """
    for key, val in to_commit.items():
        matchdict[key] = val
        # print(matchdict)


def match_close_alpha(to_match, result_dicts):

    """
    The routine to run a thread. Takes the first entry of the list and sends it to be compared to the rest of the list.
    Continues taking the first item and comparing it to the rest of the list until the list is empty
    :param to_match: The list of names to be tested
    :return: A dictionary of names and their assigned IPA ID's
    """
    # print(to_match, result_dicts[to_match[0]])
    charalpha = str(to_match[0][0][0])

    print(time.asctime(time.localtime(time.time())) + ' hello! ' + charalpha)
    result_dict = dict()

    num = 0
    # The letter of the alphabet that this list is working on
    charalpha = str(to_match[0][0][0])

    # While there are still items in the list, pull them off and send them to be compared
    while len(to_match):
        id_ipa = to_match[0]
        len_1 = len(to_match)
        to_match, return_dict = compare(to_match[1:], to_match[0], id_ipa, result_dicts)
        for key, val in return_dict.items():
            result_dict[key] = val
        # print(len_1, len(to_match), return_dict, len(result_dict), id_ipa)

    print(time.asctime(time.localtime(time.time())) + ' {} is done!'.format(charalpha))
    return result_dict


def main():

    """
    :Description: A script to harmonise names based on a cosine distance of a given tolerance. Names that are within a\
     given cosine distance are assigned the same IPA ID. The IPA ID/IPA Applt ID are written to the ipa_id table

    """
    # Get the database
    # --------------
    db = mt.get_db1()
    cur = db.cursor()

    # Select the clean names for all entities
    cur.execute("""SELECT us_att_id FROM ip5_uspto_pat_agent_clean_9 """
                """GROUP BY us_att_id""")

    results = list(cur.fetchall())
    usid_add_names = dict()
    usids = [x[0] for x in results]

    for usid in usids:
        print(usid)
        cur.execute("""SELECT a.recovered_firm, c.add_1, c.add_2, c.city, c.region FROM ip5_uspto_pat_agent_clean a """
                    """join ip5_uspto_pat_agent_clean_9 b using(appln_id) """
                    """join ip5_uspto_pat_agent_raw c using(appln_id) """
                    """where b.us_att_id = %s """, [usid])
        results_us = cur.fetchall()
        # print(results_us)

        names = list(set([x[0] for x in results_us]))
        adds = list()
        for result in results_us:
            adds.append(';'.join([x.upper() for x in result[1:] if x is not None and x != '']))
        usid_add_names[usid] = [adds, list(set(names))]
    results_alpha = list()
    results = list(usid_add_names.keys())
    results.sort()

    print(len(results))

    # While there are still entries in the list, keep breaking it up by first letter. Put the alpha lists in a list of
    # lists
    while len(results):
        try:
            alpha, remainder = alpha_split(results)
            # print(len(results))
        except Exception:
            # print e
            alpha = results
            remainder = []
        results = remainder
        results_alpha.append(alpha)

    print(len(results_alpha))

    # Sort the list of lists in order of list length so that the long lists can be sent to the pool first
    results_alpha = sorted(results_alpha, key=lambda k: len(k))
    start_time = time.time()


    # Investigations found that the number of concurrent processes should be the number of processors available. My
    # desktop has 12.
    pool = Pool(processes=10)

    # Send each list to the matching routines. Once each clean name in the list is assigned an IPA ID, the name:id pairs
    # are inserted in to a global dict
    for alpha in reversed(results_alpha):
        pool.apply_async(match_close_alpha, [alpha, usid_add_names], callback=update_match_dict)

    # Close the pool
    pool.close()
    # Wait for the jobs to finish
    pool.join()

    print("--- %s seconds ---" % str(time.time() - start_time))
    matchdict = get_matchdict()

    # Dump the dict to a file in case something happens in the next step. By this point the code has been running for
    # ~10 hours, so it is good to back up
    json.dump(matchdict, open('../data/test.json', 'w'))

    #------------------------

    matchdict = json.load(open('../data/test.json'))
    print(len(matchdict))
    # exit()
    # Refresh the database connection because it was probably lost over the last 10 hours
    # db = imt.get_ipa_db()
    db = mt.get_db1()
    cur = db.cursor()
    # exit()

    i = 0

    # For each clean name, find all matching appln ID's
    for clean_name, ipa_id in matchdict.items():
        cur.execute("""SELECT appln_id FROM ip5_uspto_pat_agent_clean_9 WHERE us_att_id = %s""", [clean_name])

        results = cur.fetchall()

        # For each found ID, pair it with the IPA ID, and store these in the table
        for result in results:
            ipa_applt = result[0]
            cur.execute("INSERT INTO "+tabletol()+"""_exp (appln_id, us_att_id) VALUES(%s, %s)""",
                        [ipa_applt, ipa_id])
        i += 1

        # Commit and print every 100 entries
        if i % 100 == 0:
            print(i)
            db.commit()
    db.commit()

if __name__ == '__main__':

    main()
