#!/usr/bin/python3
# -*- coding: utf_8 -*-

"""
.. module:: cosine_distance_fast_multi
.. moduleauthor:: T'Mir D. Julius <tdjulius@unimelb.edu.au>

:Copyright: T'Mir D. Julius for The Melbourne Institute of Applied Economics and Social Research, The University of
 Melbourne, 2014
:Contact: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Updated: 23/12/2020

"""

import json
import mysql_tools as mt
import ipa_harmonisation_tools as iht
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


def compare(name_list, comparee, current_ipa_id):

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
    ipadict[comparee[0]] = current_ipa_id
    vector = iht.convert_vector(comparee[1])

    index = 0

    # While there are still items to be processed
    while index < len(name_list):
        entry = name_list[index]

        # If there is a comparee, and the comparee's first letter is the same as the name to be compared, break the loop
        if len(comparee[0]) and entry[0][0] != comparee[0][0]:
            break

        # If the cosine distance between the comparee and the item are within the tolerance, add the entry to the list
        # of items to be compared and remove the item from the list. Do not increment the list index
        if iht.get_cosine(vector, iht.convert_vector(entry[1])) > tolerance():

            matches.append(entry)
            del name_list[index]

        # Otherwise, move on to the next list item
        else:
            index += 1

    # For each match found in the previous loop, recursively test these against the remaining list items. In this way
    # we chain the matches - eg. The groups are not order specific. If a is within the tolerance of b, and b is within
    # the tolerance of c, but c is not with a, they will still all be picked up.
    for match in matches:
        name_list, return_dict = compare(name_list, match, current_ipa_id)
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


def cosine_distance_alpha(to_match):

    """
    The routine to run a thread. Takes the first entry of the list and sends it to be compared to the rest of the list.
    Continues taking the first item and comparing it to the rest of the list until the list is empty
    :param to_match: The list of names to be tested
    :return: A dictionary of names and their assigned IPA ID's
    """
    charalpha = str(to_match[0][0][0])

    print(time.asctime(time.localtime(time.time())) + ' hello! ' + charalpha)
    result_dict = dict()

    num = 0
    # The letter of the alphabet that this list is working on
    charalpha = str(to_match[0][0][0])

    # While there are still items in the list, pull them off and send them to be compared
    while len(to_match):
        num += 1
        id_ipa = charalpha + str(num).zfill(6)
        to_match, return_dict = compare(to_match[1:], to_match[0], id_ipa)

        for key, val in return_dict.items():
            result_dict[key] = val

    print(time.asctime(time.localtime(time.time())) + ' {} is done!'.format(charalpha))
    return result_dict


def main():

    """
    :Description: A script to harmonise names based on a cosine distance of a given tolerance. Names that are within a\
     given cosine distance are assigned the same IPA ID. The IPA ID/IPA Applt ID are written to the ipa_id table

    """
    # Get the database
    # db = imt.get_ipa_db()
    # --------------
    db = mt.get_db1()
    cur = db.cursor()

    # Select the clean names for all entities
    cur.execute("""SELECT b.recovered_firm, b.vector FROM ip5_uspto_pat_agent_clean b """
                """where b.recovered_firm != '' and b.is_firm = 1 """
                """GROUP BY b.recovered_firm""")

    results = list(cur.fetchall())

    results_alpha = list()

    print(len(results))

    # While there are still entries in the list, keep breaking it up by first letter. Put the alpha lists in a list of
    # lists
    while len(results):
        try:
            alpha, remainder = alpha_split(results)
            print(len(results))
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
    # desktop has 8.
    pool = Pool(processes=10)

    # Send each list to the matching routines. Once each clean name in the list is assigned an IPA ID, the name:id pairs
    # are inserted in to a global dict
    for alpha in reversed(results_alpha):
        pool.apply_async(cosine_distance_alpha, [alpha], callback=update_match_dict)
        # update_match_dict(cosine_distance_alpha(alpha))
    # Close the pool
    pool.close()
    # Wait for the jobs to finish
    pool.join()

    print("--- %s seconds ---" % str(time.time() - start_time))
    matchdict = get_matchdict()
    print(len(matchdict))

    # Dump the dict to a file in case something happens in the next step. By this point the code has been running for
    # ~10 hours, so it is good to back up
    json.dump(matchdict, open('data/test.json', 'w'))

    #------------------------

    matchdict = json.load(open('data/test.json'))
    print(len(matchdict))
    # Refresh the database connection because it was probably lost over the last 10 hours
    # db = imt.get_ipa_db()
    db = mt.get_db1()
    cur = db.cursor()

    i = 0

    # For each clean name, find all matching appln ID's
    for clean_name, ipa_id in matchdict.items():
        cur.execute("""SELECT appln_id FROM ip5_uspto_pat_agent_clean WHERE recovered_firm = %s""", [clean_name])

        results = cur.fetchall()

        # For each found ID, pair it with the IPA ID, and store these in the table
        for result in results:
            ipa_applt = result[0]
            cur.execute("INSERT INTO "+tabletol()+""" (appln_id, us_att_id) VALUES(%s, %s)""",
                        [ipa_applt, ipa_id])
        i += 1

        # Commit and print every 100 entries
        if i % 100 == 0:
            print(i)
            db.commit()
    db.commit()


if __name__ == '__main__':

    main()