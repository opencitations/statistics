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
