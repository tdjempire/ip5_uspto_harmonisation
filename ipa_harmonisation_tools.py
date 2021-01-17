"""
.. module:: ipa_harmonisation_tools
.. moduleauthor:: T'Mir D. Julius <tdjulius@unimelb.edu.au>

:Description: Some tools for harmonisation
:Copyright: T'Mir D. Julius for The Melbourne Institute of Applied Economics and Social Research, The University of
 Melbourne, 2014
:Contact: T'Mir D. Julius <tdjulius@unimelb.edu.au>
:Updated: 08/03/2017
"""

import math

def get_cosine(vec1, vec2):
    """
    Find the cosine difference between two words

    :param vec1: A dictionary of bigrams and their values for word one
    :param vec2: A dicitonary of bigrams and their values for word two
    :return: A double of the cosine difference (0.0 < cosine_difference < 1.0)
    """
    intersection = set(vec1.keys()) & set(vec2.keys())

    if not intersection:
        return 0.0

    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])

    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0

    else:
        return float(numerator) / denominator


def get_vector(string_vector):

    """
    Turn a string in to a list of bigrams

    :param some_string: A string
    :return: The list of the bigram decompostion of the string
    """

    list_vector = string_vector.strip().split(',')
    vector = {}

    for entry in list_vector:
        if entry != '':
            key, value = entry.split(':')
            vector[key] = float(value)

    return vector


def get_vector_add(string_vector):

    """
    Turn a string in to a list of bigrams

    :param some_string: A string
    :return: The list of the bigram decompostion of the string
    """

    list_vector = convert_vector(string_vector.strip())
    vector = {}

    for entry in list_vector:
        if entry != '':
            key, value = entry.split(':')
            vector[key] = float(value)

    return vector


def convert_vector(string_vector):

    """
    Turn a string in to a dict of vectors and their weights for a name
    :param string_vector: A string of form bigram_1: weight_1, bigram_2, weight_2, ...
    :return: A dict of form {bigram1: weight_1, bigram_2, weight_2...}
    """
    string_vector = str(string_vector)
    list_vector = string_vector.strip().split(',')
    vector = dict()

    for entry in list_vector:
        if entry != '':
            try:
                key, value = entry.split(':')
                vector[key] = float(value)
            except Exception:
                a = 1
                # print list_vector
                # print e

    return vector
# def compare(list, comparee, ipa_id):
#
#     matches = []
#     matchdict = {}
#     matchdict[comparee[0]] = ipa_id
#     vector = get_vector(comparee[1])
#
#     index = 0
#     first_letter = True
#     while index < len(list) and first_letter:
#         entry = list[index]
#         # print comparee[0]
#         # print '\n'
#         if len(comparee[0]) and entry[0][0] != comparee[0][0]:
#             first_letter = False
#             break
#
#         if get_cosine(vector, get_vector(entry[1])) > tolerance():
#             #cursor.execute("INSERT INTO "+tabletol()+""" (ipa_applt_id, ipa_id, han_id) VALUES(%s, %s, %s)""",
#                            #(entry[2], ipa_id, entry[3]))
#             #matchdict[entry[0]] = ipa_id
#             matches.append(entry)
#             del list[index]
#
#         else:
#             index += 1
#
#     for match in matches:
#         list, return_dict = compare(list, match, ipa_id)
#         for key, val in return_dict.items():
#             matchdict[key] = ipa_id
#     return list, matchdict


def businesstest(name):

    """
    Test for the presence of some common business words to help distinguish individuals from entities. Specifically it
    looks for words that would be used in entity names with commas

    :param name: The name to be tested
    :return: A bool. True if one of the words is present - indicating an entity, or False if it would appear to be an individual
    """
    businesslist = ['UNIVERSITY', 'TECHNICAL', 'SERVICE', 'GESELLSCHAFT', 'BUSINESS', 'SYSTEM', 'ASSOCIATES',
                    'ASSOCIATE', 'RESEARCH', 'DEVELOPMENT', 'AUSTRALIA', 'AUSTRALIAN']

    name = name.split(' ')

    for term in businesslist:
        if term in name:
            return(True)

    return(False)
