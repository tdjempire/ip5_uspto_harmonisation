#!/usr/bin/python3
# -*- coding: utf_8 -*-

"""
.. module:: makedictmysql
.. moduleauthor:: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Contact: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Updated: 23/12/2020

"""


def createdict(text):
    """
    Turns a long string of small | separated strings in to a series of bigrams and turns them in to a counter

    :param text: A string of | separated words that will create the dictionary
    :return: A counter of bigrams that occur in the given file
    """
    bigrams = []

    lletter = '|'

    for letter in text:
        bigrams.append(lletter+letter)
        lletter = letter

    letter = '|'
    bigrams.append(lletter+letter)

    return collections.Counter(bigrams)


def calculatedict(occurences):
    """
    Takes a counter and uses it to calculate the weights of given bigrams with $w_b = frac{1}{log(n_{occurences(b)})+1}
    As per:
    Raffo, J., & Lhuillery, S. (2009).
    How to play the "Names Game": Patent retrieval comparing different heuristics.
    Research Policy, 38(10), 1617-1627.

    :param occurences: A counter object
    :return: A dict of {(bigram:weights)}
    """
    weights = {}
    for bigram in occurences:
        weights[bigram] = 1.0/(math.log(occurences[bigram])+1.0)
    return weights


def main():
    """
    :Description: A script that takes the clean_names from the ipa_applt_clean table, and uses them to create a \
    weighted bigram dictionary as per:

    Raffo, Julio, and Stéphane Lhuillery. \
    "How to play the “Names Game”: Patent retrieval comparing different heuristics." \
    Research Policy 38.10 (2009): 1617-1627.

    """

    dictout = open('data/bigramdictionaryattorneys.txt', 'w')

    db = mt.get_db1()
    cur = db.cursor()

    cur.execute("""SELECT min(appln_id), max(appln_id) FROM ip5_uspto_pat_agent_clean""")
    results = cur.fetchall()
    batchsize = 10000000
    maxid = results[0][1]
    minid = results[0][0]
    print(minid)
    print(maxid)

    occurences = collections.Counter()
    num = 0.0
    for i in range(int(minid/batchsize), int(maxid/batchsize)+2):
        print(i*batchsize)
        cur.execute("""SELECT a.recovered_firm FROM ip5_uspto_pat_agent_clean a  """
                    """WHERE a.is_firm = 1 """
                    """AND a.appln_id >= %s AND a.appln_id <= %s """,
                    [i*batchsize, (i+1)*batchsize])
        results = cur.fetchall()
        print(len(results))

        names = ""

        print('This is one')
        print(len(results))

        for result in results:
            num += 1
            names = names + result[0] + "|"
            if num % 10000 == 0:
                print(num, int(maxid/batchsize)+2)

        print('This is two')
        occurences = occurences + createdict(names)

    print('This is three')
    weights = calculatedict(occurences)
    print('This is four')
    frequencies = occurences.most_common(50)

    counts = [x[1] for x in frequencies]
    words = [x[0] for x in frequencies]

    pos = np.arange(len(words))
    width = 1.0     # gives histogram aspect to the bar diagram

    matplotlib.rc('xtick', labelsize=8)

    ax = plt.axes()
    ax.set_xticks(pos + (width / 2))
    ax.set_xticklabels(words, rotation='vertical')
    ax.set_xlabel('Bigram')
    ax.set_ylabel('Number of Occurences', rotation='vertical')

    plt.bar(pos, counts, width, color='r')
    plt.subplots_adjust(bottom=0.3)

    pylab.savefig('data/bigramattorneys.pdf')
    json.dump(weights, dictout)

    dictout.close()


if __name__ == '__main__':
    import collections
    import numpy as np
    import pylab
    import matplotlib.pyplot as plt
    import matplotlib
    import math
    import json
    import mysql_tools as mt
    main()
