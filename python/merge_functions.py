import re
from collections import namedtuple, defaultdict
from itertools import combinations
import inflect
from fuzzywuzzy import fuzz  # pylint: disable=import-error


E = inflect.engine()
E.defnoun('The', 'All')
P = E.plural

FuzzyRatioScore = namedtuple('FuzzyRatioScore', 'score value')
FuzzySetScore = namedtuple('FuzzySetScore', 'score value tokens')
ExactScore = namedtuple('ExactScore', 'value count')


# removes punctuation, whitespaces, Yud and Vav from a string
def clean_ans(a):
    return re.sub(r'[\-\'\"\s.?!`()#%*&יהו]', '', str(a))


# return True IFF the given object is empty or has length 0
def ignore_on_empty(a):
    if not a or len(a) == 0:
        return True
    return False


# returns true IFF every field in every merge level of the answer is blank (as defined by the field's "ignore" function)
def ignore_on_all_merge_properties_empty(a, f):
    if not a or len(a) == 0:
        return True
    ignore = True
    for merge_level in f['cmp']:
        for prop in merge_level:
            if not prop['ignore']((prop['string'](a))):
                ignore = False
    return ignore


# return True only if the provided string is empty
def empty_str(s):
    return len(s) == 0


# returns True only if the cleaned version of the provided string is empty
def empty_str_clean(s):
    return len(clean_ans(s)) == 0


# return True IFF the provided strings are identical
def exact_str_compare(a, b):
    return a == b


# returns True IFF the cleaned versions of the provided strings are identical
def clean_str_compare(a, b):
    return clean_ans(a) == clean_ans(b)


# given a, b, and a field object containing a nested array of properties p[][], this function does the following:
# for every merge-level p[i][]:
#       if for every j a[p[i][j]] is empty or b[p[i][j]] is empty, check the next merge level (p[i + 1][])
#               note: "emptiness" is defined for each property prop separately, through the prop['ignore'] function
#       otherwise, compare the non empty properties, and return True IFF they are all identical
def ans_compare(a, b, f):
    found_common_merge_field = False
    for merge_level in f['cmp']:
        check_next_level = True
        for prop in merge_level:
            if not prop['ignore'](prop['string'](a)) and not prop['ignore'](prop['string'](b)):
                check_next_level = False
                # extract params for comparison function
                params = {}
                if 'cmp_args' in prop:
                    params = prop['cmp_args']
                if not prop['cmp'](prop['string'](a), prop['string'](b), **params):
                    return False
                else:
                    found_common_merge_field = True
        if not check_next_level:
            return True
    return found_common_merge_field


def field_compare_exact(a, b):
    return a == b


def field_compare_clean(a, b):
    return clean_ans(a) == clean_ans(b)


# returns True IFF the cleaned versions of the provided strings are identical
def field_compare_clean_first_char(a, b):
    clean_a = clean_ans(a)
    clean_b = clean_ans(b)
    return clean_a[0] == clean_b[0]


# given a list of answer clusters, removes the clusters that have less answers than the maximum answers per-cluster
# i.e. if all clusters have 1 answer, all clusters will be returned. if one cluster has 2 answers and another has only 1
# only the first cluster will be returned
def cluster_filter_most_common(clusters):
    max_cluster_length = 0
    for c in clusters:
        max_cluster_length = max(max_cluster_length, len(c))
    common_cluster_indices = []
    for i in range(len(clusters)):
        if max_cluster_length == len(clusters[i]):
            common_cluster_indices.append(i)
    return common_cluster_indices


# returns True IFF the strings have a token set ration higher than the threshold
def field_compare_fuzzy(a, b, fuzzy_threshold=0.8):
    return top_token_set_ratio(a, b) > fuzzy_threshold


# given a set of answers that were determined to be similar enough to warrant a merge, return a synthesized answer made
# out of the longest answer per property/field
def merge_select_longest_per_property(c, q):
    merged = {}
    for f in q['fields']:
        ans = ""
        for a in c:
            if len(str(a[f])) > len(str(ans)):
                ans = str(a[f])
        merged[f] = ans
    return merged


def return_most_common(arr):
    instance_count = {}
    for a in arr:
        if a not in instance_count:
            instance_count[a] = 0
        instance_count[a] += 1
    max_instances = max(instance_count.values())
    result = []
    for a in arr:
        if instance_count[a] == max_instances:
            result.append(a)
    return result


# given a set of answers that were determined to be similar enough to warrant a merge, return a synthesized answer made
# out of the most common answer per property field, and the longest answer per property/field as a tie breaker
def merge_select_most_common_per_property(c, q):
    merged = {}
    for f in q['fields']:
        property_suggestions = [x[f].strip() for x in c]
        property_suggestions = return_most_common(property_suggestions)
        ans = ""
        for a in property_suggestions:
            if len(str(a)) > len(str(ans)):
                ans = str(a)
        merged[f] = ans
    return merged


def top_partial_ratio(group, user_weights):
    """Return the best partial ratio match from fuzzywuzzy module."""
    scores = []
    group = group.reset_index(level=0, drop=True)
    for combo in combinations(zip(group, group.index), 2):
        # combo format is ((value1, username1),(value2, username2))
        score = fuzz.partial_ratio(combo[0][0], combo[1][0])
        if len(combo[0][0]) >= len(combo[1][0]):
            value, user_name = combo[0][0], combo[0][1]
        else:
            value, user_name = combo[1][0], combo[1][1]
        score = score + user_weights.get(user_name.lower(), 0)  # add weight
        score = min(max(score, 0), 100)  # enforce a ceiling and floor
        scores.append(FuzzyRatioScore(score, value))

    scores = sorted(
        scores, reverse=True, key=lambda s: (s.score, len(s.value)))
    return scores[0]


def top_token_set_ratio(a, b):
    """Return the best token set ratio match from fuzzywuzzy module."""
    score = fuzz.token_set_ratio(a, b)
    tokens_0 = len(a.split())
    tokens_1 = len(b.split())
    if tokens_0 > tokens_1:
        value = a
        tokens = tokens_0
    elif tokens_0 < tokens_1:
        value = b
        tokens = tokens_1
    else:
        tokens = tokens_0
        value = b
        if len(a) <= len(b):
            value = a
    set_score = FuzzySetScore(score, value, tokens)
    return set_score.score
