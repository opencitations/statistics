### opencitations/statistics/script
# Statistics script
This code requires Python 3.5 or later, then you need to install the dependencies in order to run the script:
```
cd statistics/script
pip install -r requirements.txt
```
---
## Usage
### `extractor.py`
For a given log file in input, this script goes through every line, i.e. every access to a specific endpoints and collects statistics.

usage: python `extractor.py` [-h] [--output-dir OUTPUT_DIR] logfile:  
- `logfile`: is a string containing the path to the log file to use as
input for the script, note that this argument is mandatory.
- `--output-dir`: is a string indicated the path in which to save the output file. The output path is not mandatory, the default output path is the script's directory.

#### Output file format
The output file contains the following fields:
- **opencitations_http_requests**: counter of http requests. It is represented by a Counter in prometheus where each label indicates a counter for a specific endpoint, e.g. opencitations_http_requests_total{endpoint="/index/croci/ci/"} is the the counter for the endpoint /index/croci/ci/.
- **opencitations_http_requests_created**: contains the timestamp indicating the creation date of each counter opencitations_http_requests{*}.
- **opencitations_agg_counter_total**: aggregate counter of http requests. It is represented by a Counter in prometheus where each label indicates a counter for a specific aggregation, endpoints are grouped as follows:
  - opencitations_agg_counter_total{category="sparql_requests"}
    - /sparql
    - /index/sparql
    - /ccc/sparql
  - opencitations_agg_counter_total{category="additional_services_requests"}
    - /oci
    - /intrepid
  - opencitations_agg_counter_total{category="dataset_requests"}
    - /corpus/
    - /index/coci/ci/
    - /index/croci/ci/
    - /ccc/
  - opencitations_agg_counter_total{category="oc_api_requests"}
    - /index/api/v1/
    - /index/coci/api/v1/
    - /index/croci/api/v1/
    - /ccc/api/v1/
    - /api/v1/
  - opencitations_agg_counter_created{category="others_requests"}: this counts all requests that do not belong to any of the prec
- **agg_counter_created**: contains the timestamp indicating the creation date of each aggregated counter opencitations_agg_counter_total{*}.
- **opencitations_harvested_data_sources**: 
- **opencitations_indexed_records**:
