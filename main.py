#!/usr/bin/python

import sys, re, pdb
import logging
import argparse

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib, datetime

import utils, data_helper

import analyze


def parse_args():
    """
    Parse command line args.
    
    Example
    -------
    python main.py --input-file-operative ../data/small/some-applications-operative-pub-20161031.csv --input-file-usage ../data/small/some-lupapiste-usage-pub-20161031.csv --output-file-applications ../target/application-summary.csv --output-file-users ../target/user-summary.csv --output-file-comments ../target/comments-by-application.json
    """
    parser = argparse.ArgumentParser(description='SOLITADDS analysis')
    parser.add_argument('-io', '--input-file-operative', help='Input CSV file for operative data', required=False)
    parser.add_argument('-iu', '--input-file-usage', help='Input CSV file for usage data', required=True)
    parser.add_argument('-oa', '--output-file-applications', help='Output CSV file for applications', required=False, default = None)
    parser.add_argument('-ou', '--output-file-users', help='Output CSV file for users', required=False, default = None)
    parser.add_argument('-oc', '--output-file-comments', help='Output JSON file for comments by applications', required=False, default = None)
    args = vars(parser.parse_args())
    return args

        
if __name__ == "__main__":
    args = parse_args()
    input_file_operative = args['input_file_operative']
    input_file_usage = args['input_file_usage']
    output_file_applications = args['output_file_applications']
    output_file_users = args['output_file_users']
    output_file_comments = args['output_file_comments']

    analysis_start_time = datetime.datetime.now()

    odf = data_helper.import_operative_data(input_file_operative)
    udf = data_helper.import_usage_data(input_file_usage)

    print("Total number of apps: {}".format(len(odf)))
    print("Total number of events: {} with time range from {} to {} ".format(len(udf), udf['datetime'].min(), udf['datetime'].max()))

    application_summary =  analyze.summarize_applications(odf, udf)
    application_summary.to_csv(output_file_applications, sep=';', encoding='utf-8')
    
    user_summary = analyze.summarize_users(odf, udf)
    user_summary.to_csv(output_file_users, sep=';', encoding='utf-8')
    
    comments_by_application = analyze.comments_by_application(application_summary)
    comments_by_application.to_json(output_file_comments, "records")

    print("Analysis took {} seconds".format(datetime.datetime.now() - analysis_start_time))
