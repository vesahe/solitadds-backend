import sys, math, pdb
from datetime import timedelta
import pandas as pd
import logging

def summarize_users(odf, udf):
    """ Create a summary of the applications as a table. Presumes events are in datetime order
          * Count number of comments for different roles
    """


    summary = None

    udf = udf.sort_values(['userId', 'datetime'])
    user_ids = udf['userId'].unique()

    n = 0
    total_count = len(user_ids)
    for user_id in user_ids:
        user = parse_user_summary(user_id, udf[udf['userId'] == user_id])

        if summary is None:
            summary = pd.DataFrame(user, index = [0])
        else:
            summary.loc[len(summary)] = user

        n = n + 1
        if n % 100 == 0 or n == total_count:
            print("Processing... {}%".format( int( float(n) / total_count * 100)))

    return summary

def parse_user_summary(user_id, user_events):
    user = {    "userId": user_id, 
                "applicantRoles": len(user_events[user_events['role'] == 'applicant']['applicationId'].unique()),
                "authorityRoles": len(user_events[user_events['role'] == 'authority']['applicationId'].unique())
            }

    return user
