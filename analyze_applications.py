import sys, math, pdb
from datetime import timedelta
import pandas as pd
import logging

SESSION_THRESHOLD_IN_MINUTES = 15

def summarize(odf, udf):
    """ Create a summary of the applications as a table. Presumes app_events are in datetime order
          * Count number of comments for different roles
    """

    summary = None

    udf = udf.sort_values(['applicationId', 'datetime'])

    print("Analyzing {} usage events  ({} unique actions)".format(len(udf), len(udf["action"].unique())))

    application_ids = udf['applicationId'].unique()

    n = 0
    total_count = len(application_ids)

    for application_id in application_ids:
        app = odf[odf['applicationId'] == application_id]

        if app.empty:
            print("Skipping application with no operative data: " + application_id)
            continue

        app_info = parse_application_summary(application_id, app.iloc[0].to_dict(), udf[udf['applicationId'] == application_id])

        if summary is None:
            summary = pd.DataFrame(app_info, index = [0])
        else:
            summary.loc[len(summary)] = app_info

        n = n + 1
        if n % 1000 == 0 or n == total_count:
            print("Processed {}%".format( int( float(n) / total_count * 100)))


    summary = pd.merge(odf, summary, on = 'applicationId')

    return summary

def parse_application_summary(application_id, app, app_events):
    result = {  "applicationId": application_id, 
                "nEvents": len(app_events),
                "nUpdateDocs": len(find_app_events_by_action(app_events, 'update-doc')),
                "nApplicationComments": len(find_app_events_by_action_and_target(app_events, 'add-comment', 'application')),
                "nApplicationCommentsApplicant": len(find_app_events_by_action_and_role_and_target(app_events, 'add-comment', 'applicant', 'application')),
                "nApplicationCommentsAuthority": len(find_app_events_by_action_and_role_and_target(app_events, 'add-comment', 'authority', 'application')),
                "sessionLength": count_session_length(app_events, SESSION_THRESHOLD_IN_MINUTES),
                "sessionLengthApplicant": count_session_length_by_role(app_events, 'applicant', SESSION_THRESHOLD_IN_MINUTES),
                "sessionLengthAuthority": count_session_length_by_role(app_events, 'authority', SESSION_THRESHOLD_IN_MINUTES),
                "leadTime": count_days(app, 'createdDate', 'verdictGivenDate')
            }
    return result

def find_unique_users_by_application(app_events):
	return app_events.userId.nunique()

def find_unique_users_by_application_and_role(app_events, role):
    result = app_events[app_events['role'] == role]
    return result.userId.nunique()

def find_app_events_by_action(app_events, action):
    return app_events[app_events['action'] == action]

def find_app_events_by_action_and_target(app_events, action, target):
    result = app_events[app_events['action'] == action]
    result = app_events[app_events['target'] == target]
    return result

def find_app_events_by_action_and_role(app_events, action, role):
    # TODO: one liner would be better, but & is not supported
    result = app_events[app_events['action'] == action]
    result = result[result['role'] == role]
    return result

def find_app_events_by_action_and_role_and_target(app_events, action, role, target):
    # TODO: one liner would be better, but & is not supported
    result = find_app_events_by_action_and_role(app_events, action, role)
    result = result[result['role'] == role]
    result = result[result['target'] == target]
    return result

def count_session_length(app_events, thresholdMinutes):
    delta = timedelta(minutes = thresholdMinutes)

    timestamps = app_events['datetime']

    if(len(timestamps) == 0):
        return 0

    prev = timestamps.iloc[0]
    i = 1
    totalSession = 0
    while i < len(timestamps):
        diff = timestamps.iloc[i] - prev
        prev = timestamps.iloc[i]
        if(diff < delta):
            totalSession = totalSession + diff.total_seconds()

        i = i + 1
        
    return round(totalSession / 60, 0)

def count_session_length_by_role(app_events, role, thresholdMinutes):
    return count_session_length(app_events[app_events['role'] == role], thresholdMinutes)

def count_days_between_app_events(app_events, fromEvent, tillEvent):
    e1 = find_app_events_by_action(app_events, fromEvent)
    e2 = find_app_events_by_action(app_events, tillEvent)

    if(len(e1) > 0 and len(e2) > 0):
        firstSubmission = e1.iloc(0)
        verdictGiven = e2.iloc(0)        
        timeBetween = e2['datetime'].iloc[0] - e1['datetime'].iloc[0]
        return timeBetween.days + 1
    else:
        return None

def count_days(app, fromDate, tillDate):
    delta = app[tillDate] - app[fromDate]

    if pd.isnull(delta):
        return None
    else:
        return int(delta.days + 1)

def count_flow_efficiency(app, app_events, fromDate, tillDate):
    days = count_days(app, fromDate, tillDate)
    if days is None or days <= 0:
        return None

    activeDates = app_events['datetime'].dt.normalize()
    activeDates = activeDates[activeDates >= app[fromDate].normalize()]
    activeDates = activeDates[activeDates <= app[tillDate].normalize()]

    nOfProcessedDays = len(activeDates.unique())
    flowEfficiency = int(round(float(nOfProcessedDays) / days, 2) * 100)

    return flowEfficiency
