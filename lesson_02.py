import unicodecsv
from datetime import datetime as dt
from collections import defaultdict
import numpy as np

def parse_date(date):
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')

def parse_maybe_int(i):
    if i == '':
        return None
    else:
        return int(i)

def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days < 7 and time_delta.days >= 0

def read_csv(filename):
    with open(filename, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        return list(reader)

enrollments = read_csv('enrollments.csv')
daily_engagement = read_csv('daily_engagement.csv')
project_submissions = read_csv('project_submissions.csv')

for engagement_record in daily_engagement:
    engagement_record['account_key'] = engagement_record['acct']
    del(engagement_record['acct'])

for enrollment in enrollments:
    enrollment['cancel_date'] = parse_date(enrollment['cancel_date'])
    enrollment['days_to_cancel'] = parse_maybe_int(enrollment['days_to_cancel'])
    enrollment['is_canceled'] = enrollment['is_canceled'] == 'True'
    enrollment['is_udacity'] = enrollment['is_udacity'] == 'True'
    enrollment['join_date'] = parse_date(enrollment['join_date'])

for engagement_record in daily_engagement:
    engagement_record['lessons_completed'] = int(float(engagement_record['lessons_completed']))
    engagement_record['num_courses_visited'] = int(float(engagement_record['num_courses_visited']))
    engagement_record['projects_completed'] = int(float(engagement_record['projects_completed']))
    engagement_record['total_minutes_visited'] = float(engagement_record['total_minutes_visited'])
    engagement_record['utc_date'] = parse_date(engagement_record['utc_date'])

for submission in project_submissions:
    submission['completion_date'] = parse_date(submission['completion_date'])
    submission['creation_date'] = parse_date(submission['creation_date'])

udacity_test_accounts = set()
for enrollment in enrollments:
    if enrollment['is_udacity']:
        udacity_test_accounts.add(enrollment['account_key'])

def remove_udacity_accounts(data):
    non_udacity_data = []
    for data_point in data:
        if data_point['account_key'] not in udacity_test_accounts:
            non_udacity_data.append(data_point)
    return non_udacity_data

def get_unique_students(data):
    unqiue_students = set()
    for data_point in data:
        unqiue_students.add(data_point['account_key'])
    return unqiue_students

non_udacity_enrollments = remove_udacity_accounts(enrollments)
non_udacity_engagements = remove_udacity_accounts(daily_engagement)
non_udacity_submissions = remove_udacity_accounts(project_submissions)

enrollment_unique_students = get_unique_students(enrollments)
engagement_unique_students = get_unique_students(daily_engagement)
submission_unique_students = get_unique_students(project_submissions)

enrollment_num_rows = len(enrollments)
enrollment_num_unique_students = len(enrollment_unique_students)

engagement_num_rows = len(daily_engagement)
engagement_num_unique_students = len(engagement_unique_students)

submission_num_rows = len(project_submissions)
submission_num_unique_students = len(submission_unique_students)

enroll_count = 0
for enrollment in enrollments:
    if enrollment['account_key'] not in engagement_unique_students \
            and enrollment['days_to_cancel'] != 0:
        enroll_count += 1

paid_students = {}
for enrollment in non_udacity_enrollments:
    if not enrollment['is_canceled'] or enrollment['days_to_cancel'] > 7:
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']

        if account_key not in paid_students or \
                enrollment_date > paid_students[account_key]:
            paid_students[account_key] = enrollment_date

def remove_free_trial_cancels(data):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data

paid_enrollments = remove_free_trial_cancels(non_udacity_enrollments)
paid_engagements = remove_free_trial_cancels(non_udacity_engagements)
paid_submissions = remove_free_trial_cancels(non_udacity_submissions)

paid_engagement_in_first_week = []
for engagement_record in paid_engagements:
    account_key = engagement_record['account_key']
    join_date = paid_students[account_key]
    engagement_record_date = engagement_record['utc_date']

    if within_one_week(join_date, engagement_record_date):
        paid_engagement_in_first_week.append(engagement_record)

# Replaced by function
# engagement_by_account = defaultdict(list)
# for engagement_record in paid_engagement_in_first_week:
#     account_key = engagement_record['account_key']
#     engagement_by_account[account_key].append(engagement_record)

# print engagement_by_account.items()[0]

# total_minutes_by_account = {}
# for account_key, engagement_for_student in engagement_by_account.items():
#     total_minutes = 0
#     for engagement_record in engagement_for_student:
#         total_minutes += engagement_record['total_minutes_visited']
#     total_minutes_by_account[account_key] = total_minutes
#
# total_minutes = total_minutes_by_account.values()
#
# total_lessons_by_account = {}
# for account_key, engagement_for_student in engagement_by_account.items():
#     total_lessons = 0
#     for engagement_record in engagement_for_student:
#         total_lessons += engagement_record['lessons_completed']
#     total_lessons_by_account[account_key] = total_lessons
#
# total_lessons = total_lessons_by_account.values()

def group_data(data, key_name):
    grouped_data = defaultdict(list)
    for data_point in data:
        key = data_point[key_name]
        grouped_data[key].append(data_point)
    return grouped_data

def sum_grouped_items(grouped_data, field_name):
    summed_data = {}
    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            total += data_point[field_name]
        summed_data[key] = total
    return summed_data

def describe_data(data):
    print 'Mean: %s' % np.mean(data)
    print 'Standard deviation: %s' % np.std(data)
    print 'Minimum: %s' % np.min(data)
    print 'Maximum: %s' % np.max(data)

engagement_by_account = group_data(paid_engagement_in_first_week, 'account_key')

total_minutes_by_account = sum_grouped_items(engagement_by_account, 'total_minutes_visited')
total_minutes = total_minutes_by_account.values()
describe_data(total_minutes)

total_lessons_by_account = sum_grouped_items(engagement_by_account, 'lessons_completed')
total_lessons = total_lessons_by_account.values()
describe_data(total_lessons)

# Repalced by function
# print 'Mean minutes: %s' % np.mean(total_minutes)
# print 'Standard deviation minutes: %s' % np.std(total_minutes)
# print 'Minimum minutes: %s' % np.min(total_minutes)
# print 'Maximum minutes: %s' % np.max(total_minutes)
#
# print 'Mean lessons: %s' % np.mean(total_lessons)
# print 'Standard deviation lessons: %s' % np.std(total_lessons)
# print 'Minimum lessons: %s' % np.min(total_lessons)
# print 'Maximum lessons: %s' % np.max(total_lessons)

# student_with_max_minutes = None
# max_minutes = 0
# for student, total_minutes in total_minutes_by_account.items():
#     if total_minutes > max_minutes:
#         max_minutes = total_minutes
#         student_with_max_minutes = student

# for engagement_record in paid_engagement_in_first_week:
#     if engagement_record['account_key'] == student_with_max_minutes:
        # print engagement_record
