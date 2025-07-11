#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Giuseppe Grieco <g.grieco1997@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

__author__ = 'giuseppegrieco'

'''
This script is run monthly and takes as input the monthly activity in terms
of access to the different endpoints. The output is a prometheus-like file
containing different statistics on the accesses of the month.

Syntax: python stats.py <logfile.txt> <output_path>*

* the output path is not mandatory, the default output path is the script's
directory.
'''
import argparse
import re
import json
import collections
import csv
from os.path import isdir, isfile, sep

from prometheus_client import Counter, CollectorRegistry, write_to_textfile, Gauge, Info

# Input file in order to check whether the indicated file exists or not,
# and is a json file
def input_file_json(string):
    if isfile(string):
        if '.json' in string:
            return string
        raise ValueError(string)
    raise FileNotFoundError(string)

# Input file in order to check whether the indicated file exists or not,
# and is a txt file
def input_file(string):
    if isfile(string):
        if '.txt' in string:
            return string
        raise ValueError(string)
    raise FileNotFoundError(string)

# Directory type in order to check whether the indicated path exists or not
def directory(string):
    if not string.endswith(sep):
        string = string + sep
    if isdir(string):
        return string
    raise NotADirectoryError(string)

parser = argparse.ArgumentParser(
    description='It extracts the statistics starting from a file containing the monthly accesses'
)

parser.add_argument(
    'logfile',
    help='input file (.txt) containing monthly accesses to oc',
    type=input_file
)
parser.add_argument(
    "externalIndicators",
    help='input file (.json) containing additional indicators',
    type=input_file_json
)
parser.add_argument(
    '--output-dir',
    help='the path in which to save the output file',
    type=directory,
    default='.' + sep
)

args = parser.parse_args()

# Directory in which to save the output file
output_path = args.output_dir

# File containg log activity for a given month: each line is an access
# to a specific endpoint,  all the informations contained in a line
# are separated by the character '#'
log_file = args.logfile

# File containing additional statistics
external_indicators_file = args.externalIndicators

ends_withs = {
    # SPARQL endpoints:
    '/sparql': 'sparql',
    '/index/sparql': 'sparql',
    '/meta/sparql': 'sparql',
    '/ccc/sparql': 'sparql',
}

contains = {
    # REST API di OpenCitation
    '/index/api/v1/': 'oc_api',
    '/index/api/v2/': 'oc_api',
    '/index/coci/api/v1/': 'oc_api',
    '/index/croci/api/v1/': 'oc_api',
    '/meta/api/v1/': 'oc_api',
    '/meta/api/v2/': 'oc_api',
    '/ccc/api/v1/': 'oc_api',
    '/api/v1/': 'oc_api',
    '/api/v2/': 'oc_api',

    # Dataset resources:
    '/corpus/': 'dataset',
    '/index/': 'dataset',
    '/index/ci/': 'dataset',
    '/index/coci/ci/': 'dataset',
    '/index/croci/ci/': 'dataset',
    '/ccc/': 'dataset',
    '/meta/': 'dataset',

    # Additional services:
    '/oci': 'additional_services',
    '/intrepid': 'additional_services'
}

contains_keys = [
    '/index/api/v1/',
    '/index/api/v2/',
    '/index/coci/api/v1/',
    '/index/croci/api/v1/',
    '/meta/api/v1/',
    '/meta/api/v2/',
    '/ccc/api/v1/',
    '/api/v1/',
    '/api/v2/',

    # Dataset resources:
    '/corpus/',
    '/index/',
    '/index/ci/',
    '/index/coci/ci/',
    '/index/croci/ci/',
    '/ccc/',
    '/meta/',

    # Additional services:
    '/oci',
    '/intrepid'
]

contains_values = [
    'oc_api',
    'oc_api',
    'oc_api',
    'oc_api',
    'oc_api',
    'oc_api',
    'oc_api',
    'oc_api',
    'oc_api',

    # Dataset resources:
    'dataset',
    'dataset',
    'dataset',
    'dataset',
    'dataset',
    'dataset',
    'dataset',

    # Additional services:
    'additional_services',
    'additional_services'
]

registry = CollectorRegistry()

# Counter of accesses to different endpoints oc
http_requests = Counter(
    'opencitations_http_requests',
    'Counter for HTTP requests to opencitations endpoints',
    ['endpoint'],
    registry=registry
)

# Aggregate counter of accesses to the different categories of endpoints oc
agg_counter = Counter(
    'opencitations_agg_counter',
    'Aggregate HTTP requests counter to opencitations endpoints',
    ['category'],
    registry=registry
)

# Initialization of aggregate counters
agg_counter.labels('additional_services_requests')
agg_counter.labels('dataset_requests')
agg_counter.labels('oc_api_requests')
agg_counter.labels('sparql_requests')
agg_counter.labels('others_requests')

# Initialization of accessess counters
for suffix in ends_withs:
    http_requests.labels(suffix)
for substr in contains:
    http_requests.labels(substr)

# goes through every line of the log file
#rgx = re.compile('(.*)#(.*):(.*)#(.*):(.*)#(.*):(.*)#(.*):(.*)#(.*):(.*)')

rgx = re.compile('(.*)#( REMOTE_ADDR):(.*)#( HTTP_USER_AGENT):(.*)#( HTTP_REFERER):(.*)#( HTTP_HOST):(.*)#( REQUEST_URI):(.*)#( HTTP_AUTHORIZATION):(.*)')

file = open(log_file, 'r')
aut_tokens = dict()
for line in file.readlines():
    line = line.strip()
    match_1 = rgx.match(line)
    if match_1:
        groups = rgx.search(line).groups()

        # split and parse the differents attributes of the current line
        request_uri = groups[10].strip()

        # calc unique users
        http_authorization = groups[12].strip().lower()
        rgtoken = re.compile('.*-.*-.*-.*')
        if rgtoken.match(http_authorization):
            if http_authorization not in aut_tokens:
                aut_tokens[http_authorization] = 0
            aut_tokens[http_authorization] += 1

        # It checks if the request made is of a specific type,
        # if it's so it increases the counter of that request,
        # otherwise the aggregate counter `agg_others_requests`
        # increases. In the case the counter of any request type
        # is updated even the aggregated counter corresponding
        # to its category is updated.
        found = False

        for suffix in ends_withs:
            if(request_uri.startswith(suffix)):
                http_requests.labels(suffix).inc()
                agg_counter.labels(ends_withs[suffix] + '_requests').inc()
                found = True
                break
        if not found:
            for i in range(0, len(contains_keys)):
                if contains_keys[i] in request_uri:
                    http_requests.labels(contains_keys[i]).inc()
                    agg_counter.labels(contains_values[i] + '_requests').inc()
                    found = True
                    break
            if not found:
                agg_counter.labels('others_requests').inc()

# Additional statistics
file = open(external_indicators_file, 'r')
external_indicators = json.load(file)
indexed_records = Gauge(
    'opencitations_indexed_records',
    'Indexed records',
    registry=registry
)
indexed_records.set(
    external_indicators["indexed_records"]
)
harvested_data_sources = Gauge(
    'opencitations_harvested_data_sources',
    'Harvested data sources',
    registry=registry
)
harvested_data_sources.set(
    external_indicators["harvested_data_sources"]
)
file.close()


# Add the date as info
i = Info(
    'opencitations_date',
    'Date to which the statistics refers to',
    registry=registry
)
date_split = log_file.split(sep)[-1].replace('.txt', '').replace("oc-", "")
date_split = date_split.split("-")
i.info({'month': date_split[1], 'year': date_split[0]})

# Add the date as info
tokens = Info(
    'opencitations_auth_tokens',
    'Number of unique API users (authorization token)',
    registry=registry
)
tokens.info({ 'count_calls_unique_users': str(sum(aut_tokens.values())) , 'count_unique_users': str(len(aut_tokens.keys())) })

# dump tokens to csv
output_file = log_file.split(sep)[-1].replace('.txt', '')+"-users.csv"
with open(output_path + output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for key, value in aut_tokens.items():
        writer.writerow([key, value])

# Write the obtained statistics in a file
output_file = log_file.split(sep)[-1].replace('.txt', '.prom')
write_to_textfile( output_path + output_file, registry)
