RETIRED_ANS_COUNT = 3


def test_flag(doc, flag):
    if "q" in flag and "ans" in flag and "f" in flag:
        return flag["tester"](doc, flag["q"], flag["ans"], flag["f"])
    elif "q" in flag:
        return flag["tester"](doc, flag["q"])
    return flag["tester"](doc)


def flag_retired(doc):
    return len(doc['users']) >= RETIRED_ANS_COUNT


def flag_on_answer(doc, q, ans, f):
    for a in doc['annotations'][q]['reconciled']:
        if a[f] == ans:
            return True
    return False


def flag_on_multiple_answers(doc, q):
    return len(doc['annotations'][q]['reconciled']) > 1


def flag_on_no_answers(doc, q):
    return len(doc['annotations'][q]['reconciled']) < 1


def flag_on_standout_answers(doc, q):
    cluster_users = {}
    users = []
    for u in doc['annotations'][q]['answers']:
        users.append(u)
        for a in doc['annotations'][q]['answers'][u]['answers']:
            if a['cluster_index'] not in cluster_users:
                cluster_users[a['cluster_index']] = []
            if u not in cluster_users[a['cluster_index']]:
                cluster_users[a['cluster_index']].append(u)
    if len(users) < RETIRED_ANS_COUNT:
        return False
    for u in users:
        answer_only_supplied_by_u = False
        answer_supplied_by_everyone_but_u = False
        for c in cluster_users:
            if len(cluster_users[c]) == 1:
                if u in cluster_users[c]:
                    answer_only_supplied_by_u = True
            if len(cluster_users[c]) == len(users) - 1:
                if u not in cluster_users[c]:
                    answer_supplied_by_everyone_but_u = True
        if answer_only_supplied_by_u and answer_supplied_by_everyone_but_u:
            return True
    return False
