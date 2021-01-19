"""This script was written in Python 3.6.6 "out of the box" and should run without any added packages."""
import csv
import json
import sys
import re
import db
import os
import merge_functions
import flag_functions

csv.field_size_limit(sys.maxsize)
test = sys.maxsize


# File location section:
directory = './data'  # modify this to match your directory structure including file names
data_file = directory + os.sep + 'deciphering-the-military-rule-classifications.csv'  # modify as needed

debug = {'doc': '44410798', 'q': 'title'}

classifications = {}
flags = [
    {
        "flag": "retired",
        "tester": flag_functions.flag_retired
    },
    {
        "flag": "suggested_title",
        "q": "is_title?",
        "f": "is_title",
        "ans": "no",
        "tester": flag_functions.flag_on_answer
    },
    {
        "flag": "missing_title",
        "q": "title",
        "tester": flag_functions.flag_on_no_answers
    },
    {
        "flag": "inconclusive_title",
        "q": "title",
        "tester": flag_functions.flag_on_multiple_answers
    },
    {
        "flag": "implicit_date",
        "q": "is_date?",
        "f": "is_date",
        "ans": "infer",
        "tester": flag_functions.flag_on_answer
    },
    {
        "flag": "inconclusive_day",
        "q": "day",
        "tester": flag_functions.flag_on_multiple_answers
    },
    {
        "flag": "inconclusive_month",
        "q": "month",
        "tester": flag_functions.flag_on_multiple_answers
    },
    {
        "flag": "inconclusive_year",
        "q": "year",
        "tester": flag_functions.flag_on_multiple_answers
    },
    {
        "flag": "standout_location",
        "q": "locations_list",
        "tester": flag_functions.flag_on_standout_answers
    },
    {
        "flag": "missing_summary",
        "q": "summary",
        "tester": flag_functions.flag_on_no_answers
    }
]
questions = {
    'is_title?': {
        'cmp': [
            [
                {
                    'string': lambda x: x['is_title'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['is_title'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'title': {
        'cmp': [
            [
                {
                    'string': lambda x: x['title'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ]
        ],
        'fields': ['title'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty,
        'cluster_filter': merge_functions.cluster_filter_most_common
    },
    'is_date?': {
        'cmp': [
            [
                {
                    'string': lambda x: x['is_date'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['is_date'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'day': {
        'cmp': [
            [
                {
                    'string': lambda x: x['day'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['day'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'month': {
        'cmp': [
            [
                {
                    'string': lambda x: x['month'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['month'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'year': {
        'cmp': [
            [
                {
                    'string': lambda x: x['year'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['year'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'doc_type': {
        'cmp': [
            [
                {
                    'string': lambda x: x['doc_type'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['doc_type'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'author_list': {
        'cmp': [
            [
                {
                    'string': lambda x: x['first_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean_first_char
                },
                {
                    'string': lambda x: x['last_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ],
            [
                {
                    'string': lambda x: x['role'] + " " + x['admin'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ]
        ],
        'fields': ['first_name', 'last_name', 'role', 'admin'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'recipient_list': {
        'cmp': [
            [
                {
                    'string': lambda x: x['first_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean_first_char
                },
                {
                    'string': lambda x: x['last_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ],
            [
                {
                    'string': lambda x: x['role'] + " " + x['admin'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ]
        ],
        'fields': ['first_name', 'last_name', 'role', 'admin'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'c_c_list': {
        'cmp': [
            [
                {
                    'string': lambda x: x['first_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean_first_char
                },
                {
                    'string': lambda x: x['last_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ],
            [
                {
                    'string': lambda x: x['role'] + " " + x['admin'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ]
        ],
        'fields': ['first_name', 'last_name', 'role', 'admin'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'participant_list': {
        'cmp': [
            [
                {
                    'string': lambda x: x['first_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean_first_char
                },
                {
                    'string': lambda x: x['last_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ],
            [
                {
                    'string': lambda x: x['role'] + " " + x['admin'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ]
        ],
        'fields': ['first_name', 'last_name', 'role', 'admin'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'author_no_rep_list': {
        'cmp': [
            [
                {
                    'string': lambda x: x['first_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean_first_char
                },
                {
                    'string': lambda x: x['last_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ],
            [
                {
                    'string': lambda x: x['role'] + " " + x['admin'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ]
        ],
        'fields': ['first_name', 'last_name', 'role', 'admin'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'names_list': {
        'cmp': [
            [
                {
                    'string': lambda x: x['first_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean_first_char
                },
                {
                    'string': lambda x: x['last_name'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_fuzzy,
                    'cmp_args': {"fuzzy_threshold": 50}
                }
            ]
        ],
        'fields': ['first_name', 'last_name'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'institution_list': {
        'cmp': [
            [
                {
                    'string': lambda x: x['institution'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['institution'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'locations_list': {
        'cmp': [
            [
                {
                    'string': lambda x: x['location'],
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['location'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
    'summary': {
        'cmp': [
            [
                {
                    'string': lambda x: False,
                    'ignore': merge_functions.empty_str_clean,
                    'cmp': merge_functions.field_compare_clean
                }
            ]
        ],
        'fields': ['summary'],
        'merge': merge_functions.merge_select_longest_per_property,
        'ignore_ans': merge_functions.ignore_on_all_merge_properties_empty
    },
}


# Function definitions needed for any blocks.
def include(class_record):
    if int(class_record['workflow_id']) == 13195:
        pass
    else:
        return False
    # # these alternate conditional tests may be needed in special circumstances
    if float(class_record['workflow_version']) >= 960.81:
        pass  # replace '001.01' with first version of the workflow to include.
    else:
        return False
    # if 50000000 >= int(class_record['subject_ids']) >= 44000000:
    #     pass  # replace upper and lower subject_ids to include only a specified range of subjects - this is
    #     # a very useful slice since subjects are selected together and can still be aggregated.
    # else:
    #     return False
    # if '2100-00-10 00:00:00 UTC' >= class_record['created_at'] >= '2020-04-13 00:00:00 UTC':
    #     pass  # replace earliest and latest created_at date and times to select records commenced in a
    #     #  specific time period
    # else:
    #     return False
    # otherwise :
    return True


# Set up the output file structure with desired fields:
# prepare the output file and write the header
def parse_file():
    fieldnames = ['classification_id',
                  'subject_id',
                  'user_name',
                  'workflow_id',
                  'workflow_version',
                  'created_at',
                  'my_ID',
                  'image1',
                  'pages',
                  'is_title?',
                  'title',
                  'is_date?',
                  'day',
                  'month',
                  'year',
                  'doc_type',
                  '#_authors',
                  'author_list',
                  '#_recipients',
                  'recipient_list',
                  '#_c_copy',
                  'c_c_list',
                  '#_participants',
                  'participant_list',
                  '#_author_no_rep',
                  'author_no_rep_list',
                  '#_names',
                  'names_list',
                  '#_institutions',
                  'institution_list',
                  '#_locations',
                  'locations_list',
                  'summary'
                  ]

    # this area for initializing counters, status lists and loading pick lists into memory:
    i = 0
    j = 0

    #  open the zooniverse data file using dictreader,  and load the more complex json strings as python objects
    with open(data_file, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            # useful for debugging - set the number of record to process at a low number ~1000
            # if i == 500:
            #     break
            i += 1
            # if i % 5000 == 0:
            #     print('.', end='')
            if include(row) is True:
                j += 1
                try:
                    annotations = json.loads(row['annotations'])
                    subject_data = json.loads(row['subject_data'])
                except json.decoder.JSONDecodeError:
                    continue
                subject = row['subject_ids']
                # this is the area the various blocks of code will be inserted to preform additional general
                # tasks, to flatten the annotations field, or test the data for various conditions.

                # pull metadata from the subject data field
                metadata = subject_data[subject]
                try:
                    my_id = metadata['my_ID']
                except KeyError:
                    my_id = ''
                try:
                    image1 = metadata['image1']
                except KeyError:
                    image1 = ''

                pages = 0
                for p in list(metadata)[2:]:
                    if metadata[p] and p.find('image') == 0:
                        pages += 1

                # reset the field variables for each new row
                is_title = ''
                title = ''
                is_date = ''
                day = ''
                month = ''
                year = ''
                doc_type = ''
                authors = ''
                author_list = []
                recipients = ''
                recipient_list = []
                c_copies = ''
                c_c_list = []
                participants = ''
                participant_list = []
                no_reps = ''
                author_no_rep_list = []
                names = ''
                names_list = []
                institutions = 0
                institution_list = []
                locations = 0
                location_list = []
                summary = ''

                # loop over the tasks
                for task in annotations:

                    # is there a title?
                    try:
                        if task['task'] == 'T1':
                            if task['value']:
                                is_title = task['value']
                    except KeyError:
                        print(subject, 'T1 KeyError')

                    # Free Transcription title or suggested title?
                    try:
                        if task['task'] == 'T2' or task['task'] == 'T255':
                            if task['value']:
                                title = task['value']
                    except KeyError:
                        print(subject, 'T2, T255 KeyError')

                    # is there a date?
                    try:
                        if task['task'] == 'T3' or task['task'] == 'T129':
                            if task['value']:
                                is_date = task['value']
                                if len(is_date) > 3:
                                    is_date = 'infer'
                    except KeyError:
                        print(subject, 'T3, T129 KeyError')

                    # Date combo task?
                    if task['task'] == 'T4' or task['task'] == 'T130':
                        for combo_task in task['value']:
                            try:
                                if combo_task['task'] == 'T5' or combo_task['task'] == 'T131':
                                    if combo_task['value'][0]:
                                        day = combo_task['value'][0]['value']
                            except KeyError:
                                day = ''
                            try:
                                if combo_task['task'] == 'T6' or combo_task['task'] == 'T132':
                                    if combo_task['value'][0]:
                                        month = combo_task['value'][0]['value']
                            except KeyError:
                                month = ''
                            try:
                                if combo_task['task'] == 'T7' or combo_task['task'] == 'T133':
                                    if combo_task['value'][0]:
                                        year = combo_task['value'][0]['value']
                            except KeyError:
                                year = ''

                    # document type?
                    try:
                        if task['task'] == 'T8' or task['task'] == 'T134':
                            if task['value']:
                                doc_type = task['value']
                    except KeyError:
                        doc_type = ''

                    # authors - combo transcription with loops
                    if task['task'] in ['T9', 'T135', 'T15', 'T141']:
                        author_dict = {'first_name': '', 'last_name': '', 'role': '', 'admin': ''}
                        try:
                            if task['value'][0]['value']:
                                author_dict['first_name'] = task['value'][0]['value']
                        except KeyError:
                            print(subject, task['task'][1], 'KeyError')
                        try:
                            if task['value'][1]['value']:
                                author_dict['last_name'] = task['value'][1]['value']
                        except KeyError:
                            print(subject, task['task'][2], 'KeyError')
                        try:
                            if task['value'][2]['value']:
                                author_dict['role'] = task['value'][2]['value']
                        except KeyError:
                            print(subject, task['task'][3], 'KeyError')
                        try:
                            if task['value'][3]['value']:
                                author_dict['admin'] = task['value'][3]['value']
                        except KeyError:
                            print(subject, task['task'][0], 'KeyError')
                        if author_dict['first_name'] or author_dict['last_name'] \
                                or author_dict['role'] or author_dict['admin']:
                            author_list.append(author_dict)

                    # recipients - combo transcription with loops
                    if task['task'] in ['T20', 'T146', 'T26', 'T152']:
                        recipients_dict = {'first_name': '', 'last_name': '', 'role': '', 'admin': ''}
                        try:
                            if task['value'][0]['value']:
                                recipients_dict['first_name'] = task['value'][0]['value']
                        except KeyError:
                            print(subject, task['task'][0], 'KeyError')
                        try:
                            if task['value'][1]['value']:
                                recipients_dict['last_name'] = task['value'][1]['value']
                        except KeyError:
                            print(subject, task['task'][1], 'KeyError')
                        try:
                            if task['value'][2]['value']:
                                recipients_dict['role'] = task['value'][2]['value']
                        except KeyError:
                            print(subject, task['task'][2], 'KeyError')
                        try:
                            if task['value'][3]['value']:
                                recipients_dict['admin'] = task['value'][3]['value']
                        except KeyError:
                            print(subject, task['task'][3], 'KeyError')
                        if recipients_dict['first_name'] or recipients_dict['last_name'] \
                                or recipients_dict['role'] or recipients_dict['admin']:
                            recipient_list.append(recipients_dict)

                    # c_c_list - combo transcription with loops
                    if task['task'] in ['T31', 'T158', 'T37', 'T164']:
                        c_c_dict = {'first_name': '', 'last_name': '', 'role': '', 'admin': ''}
                        try:
                            if task['value'][0]['value']:
                                c_c_dict['first_name'] = task['value'][0]['value']
                        except KeyError:
                            print(subject, task['task'][0], 'KeyError')
                        try:
                            if task['value'][1]['value']:
                                c_c_dict['last_name'] = task['value'][1]['value']
                        except KeyError:
                            print(subject, task['task'][1], 'KeyError')
                        try:
                            if task['value'][2]['value']:
                                c_c_dict['role'] = task['value'][2]['value']
                        except KeyError:
                            print(subject, task['task'][2], 'KeyError')
                        try:
                            if task['value'][3]['value']:
                                c_c_dict['admin'] = task['value'][3]['value']
                        except KeyError:
                            print(subject, task['task'][3], 'KeyError')
                        if c_c_dict['first_name'] or c_c_dict['last_name'] \
                                or c_c_dict['role'] or c_c_dict['admin']:
                            c_c_list.append(c_c_dict)

                    # participants - combo transcription with loops
                    if task['task'] in ['T42', 'T169', 'T48', 'T175']:
                        participants_dict = {'first_name': '', 'last_name': '', 'role': '', 'admin': ''}
                        try:
                            if task['value'][0]['value']:
                                participants_dict['first_name'] = task['value'][0]['value']
                        except KeyError:
                            print(subject, task['task'][0], 'KeyError')
                        try:
                            if task['value'][1]['value']:
                                participants_dict['last_name'] = task['value'][1]['value']
                        except KeyError:
                            print(subject, task['task'][1], 'KeyError')
                        try:
                            if task['value'][2]['value']:
                                participants_dict['role'] = task['value'][2]['value']
                        except KeyError:
                            print(subject, task['task'][2], 'KeyError')
                        try:
                            if task['value'][3]['value']:
                                participants_dict['admin'] = task['value'][3]['value']
                        except KeyError:
                            print(subject, task['task'][3], 'KeyError')
                        if participants_dict['first_name'] or participants_dict['last_name'] \
                                or participants_dict['role'] or participants_dict['admin']:
                            participant_list.append(participants_dict)

                    # author_no_rep - combo transcription with loops
                    if task['task'] in ['T53', 'T180', 'T59', 'T186']:
                        author_no_rep_dict = {'first_name': '', 'last_name': '', 'role': '', 'admin': ''}
                        try:
                            if task['value'][0]['value']:
                                author_no_rep_dict['first_name'] = task['value'][0]['value']
                        except KeyError:
                            print(subject, task['task'][0], 'KeyError')
                        try:
                            if task['value'][1]['value']:
                                author_no_rep_dict['last_name'] = task['value'][1]['value']
                        except KeyError:
                            print(subject, task['task'][1], 'KeyError')
                        try:
                            if task['value'][2]['value']:
                                author_no_rep_dict['role'] = task['value'][2]['value']
                        except KeyError:
                            print(subject, task['task'][2], 'KeyError')
                        try:
                            if task['value'][3]['value']:
                                author_no_rep_dict['admin'] = task['value'][3]['value']
                        except KeyError:
                            print(subject, task['task'][3], 'KeyError')
                        if author_no_rep_dict['first_name'] or author_no_rep_dict['last_name'] \
                                or author_no_rep_dict['role'] or author_no_rep_dict['admin']:
                            author_no_rep_list.append(author_no_rep_dict)

                    # names - combo transcription with loops
                    if task['task'] in ['T67', 'T194', 'T77', 'T204']:
                        for index in range(0, 4):
                            names_dict = {'first_name': '', 'last_name': ''}
                            try:
                                if task['value'][index * 2]['value']:
                                    names_dict['first_name'] = task['value'][index * 2]['value']
                            except KeyError:
                                print(subject, task['task'][index * 2], 'KeyError')
                            try:
                                if task['value'][index * 2 + 1]['value']:
                                    names_dict['last_name'] = task['value'][index * 2 + 1]['value']
                            except KeyError:
                                print(subject, task['task'][index * 2 + 1], 'KeyError')
                            if names_dict['first_name'] or names_dict['last_name']:
                                names_list.append(names_dict)

                    # is there names?
                    try:
                        if task['task'] in ['T64', 'T191', 'T65', 'T192', 'T66', 'T193']:
                            if task['value']:
                                names = task['value']
                    except KeyError:
                        names = ''

                    # institutions - combo transcription with loops
                    if task['task'] in ['T87', 'T214', 'T97', 'T224']:
                        for index in range(0, 8):
                            try:
                                if task['value'][index]['value']:
                                    institution_list.append({'institution': task['value'][index]['value']})
                            except KeyError:
                                print(subject, task['task'][index], 'KeyError')

                    # locations - combo transcription with loops
                    if task['task'] in ['T107', 'T234', 'T117', 'T245']:
                        for index in range(0, 8):
                            try:
                                if task['value'][index]['value']:
                                    location_list.append({'location':task['value'][index]['value']})
                            except KeyError:
                                print(subject, task['task'][index], 'KeyError')

                    # summary
                    try:
                        if task['task'] == 'T126' or task['task'] == 'T254':
                            if task['value']:
                                summary = task['value']
                    except KeyError:
                        summary = ''

                if is_date == 'no':
                    # force no date due to data persistence on back-out
                    day = ''
                    month = ''
                    year = ''

                # This set up the writer to match the field names above and the variable names of their values:
                if not row['subject_ids'] in classifications:
                    classifications[row['subject_ids']] = []
                classifications[row['subject_ids']].append({
                    'classification_id': row['classification_id'],
                    'subject_id': row['subject_ids'],
                    'user_name': row['user_name'],
                    'workflow_id': row['workflow_id'],
                    'workflow_version': row['workflow_version'],
                    'created_at': row['created_at'],
                    'my_ID': my_id,
                    'image1': image1,
                    'pages': pages,
                    'is_title?': [{'is_title': is_title}],
                    'title': [{'title': title}],
                    'is_date?': [{'is_date': is_date}],
                    'day': [{'day': str(day)}],
                    'month': [{'month': str(month)}],
                    'year': [{'year': str(year)}],
                    'doc_type': [{'doc_type': doc_type}],
                    'author_list': author_list,
                    'recipient_list': recipient_list,
                    'c_c_list': c_c_list,
                    'participant_list': participant_list,
                    'author_no_rep_list': author_no_rep_list,
                    'names_list': names_list,
                    'institution_list': institution_list,
                    'locations_list': location_list,
                    'summary': [{'summary': summary}]
                })


def should_ignore(a, f):
    if not a or len(a) == 0:
        return True
    for prop in f['merge']:
        if not a[prop] or len(str(a[prop])) == 0:
            return True
    return False


def clean_ans(a):
    return re.sub(r'[\-\'\"\s.?!`יו]', '', str(a))


def compare(a, b, f):
    for prop in f['merge']:
        if not clean_ans(a[prop]) == clean_ans(b[prop]):
            return False
    return True


parse_file()
reconciled_classifications = []
for doc in classifications:
    title = ""
    reconciled = {'annotations': {}, 'users': [], 'id': doc}
    doc_flags = []
    for q in questions:
        if debug["doc"] == doc and debug["q"] == q:
            print("debugging")
        for ans in classifications[doc]:
            if q not in reconciled['annotations']:
                # question and label - strings by which we identify the question
                # answers - contains all the given answers to th question, with each assigned to the user who gave it
                # clusters - contains a list of lists, each inner list contains answers that were determined to be
                # similar, and should be merged
                # merged - contains a list of all the given answers, without duplicates
                # (duplicate answers having been merged)
                reconciled['annotations'][q] = {
                    'question': q, 'label': q,
                    'answers': {},
                    'clusters': [],
                    'reconciled': []
                }
            if ans['user_name'] not in reconciled['users']:
                reconciled['users'].append(ans['user_name'])
            if ans['user_name'] not in reconciled['annotations'][q]['answers']:
                reconciled['annotations'][q]['answers'][ans['user_name']] = {'user': ans['user_name'], 'answers': []}
            for single_ans in ans[q]:
                if questions[q]['ignore_ans'](single_ans, questions[q]):
                    reconciled['annotations'][q]['answers'][ans['user_name']]['answers'].append(
                        {"ans": single_ans, "cluster_index": -1}
                    )
                    continue
                else:
                    duplicate = False
                    # loop over previous answers, and check them against the current answer
                    for c in range(len(reconciled['annotations'][q]['clusters'])):
                        for prev_ans in reconciled['annotations'][q]['clusters'][c]:
                            if merge_functions.ans_compare(prev_ans, single_ans, questions[q]):
                                duplicate = True
                                reconciled['annotations'][q]['clusters'][c].append(single_ans)
                                reconciled['annotations'][q]['answers'][ans['user_name']]['answers'].append(
                                    {"ans": single_ans,
                                     "cluster_index": c}
                                )
                                break
                        if duplicate:
                            break
                    if not duplicate:
                        reconciled['annotations'][q]['clusters'].append([single_ans])
                        reconciled['annotations'][q]['answers'][ans['user_name']]['answers'].append(
                            {"ans": single_ans, "cluster_index": (len(reconciled['annotations'][q]['clusters'])-1)}
                        )
        # drop clusters (for example, the "title" field keeps only the most common cluster
        if "cluster_filter" in questions[q]:
            clusters_to_keep = questions[q]['cluster_filter'](reconciled['annotations'][q]['clusters'])
        # as a default - don't drop any clusters
        else:
            clusters_to_keep = range(len(reconciled['annotations'][q]['clusters']))
        # merge answers here
        for c_i in clusters_to_keep:
            c = reconciled['annotations'][q]['clusters'][c_i]
            cluster_merge = questions[q]['merge'](c, questions[q])
            reconciled['annotations'][q]['reconciled'].append(cluster_merge)
        del reconciled['annotations'][q]['clusters']
    # raise flags
    for f in flags:
        if flag_functions.test_flag(reconciled, f):
            doc_flags.append(f["flag"])
    db.save_flags(doc, doc_flags)
    reconciled['annotations'] = list(reconciled['annotations'].values())
    reconciled_classifications.append(reconciled)
    db.save_docs(doc, json.dumps(reconciled), title)
db.commit()

print("done")

