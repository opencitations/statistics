import os
import re
import argparse
from collections import defaultdict

def main(log_dir, years_to_include):
    # Regex to extract HTTP_AUTHORIZATION value
    auth_pattern = re.compile(r'HTTP_AUTHORIZATION: ([^\s#]+)')

    monthly_auth_tokens = defaultdict(set)
    yearly_auth_tokens = defaultdict(set)

    # Process files
    for filename in os.listdir(log_dir):
        if filename.startswith('oc-') and filename.endswith('.txt'):
            parts = filename[3:-4].split('-')  # remove 'oc-' and '.txt'
            if len(parts) != 2:
                continue
            year, month = parts
            if year not in years_to_include:
                continue
            year_month = f'{year}-{month}'

            file_path = os.path.join(log_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        match = auth_pattern.search(line)
                        if match:
                            token = match.group(1)
                            if token != 'None':
                                monthly_auth_tokens[year_month].add(token)
                                yearly_auth_tokens[year].add(token)
            except Exception as e:
                print(f'Error reading {file_path}: {e}')

    # Print stats
    print('\n📊 Monthly stats:')
    for ym in sorted(monthly_auth_tokens):
        count = len(monthly_auth_tokens[ym])
        print(f'  {ym}: {count} unique HTTP_AUTHORIZATION tokens')

    print('\n📊 Yearly stats:')
    for year in sorted(yearly_auth_tokens):
        count = len(yearly_auth_tokens[year])
        print(f'  {year}: {count} unique HTTP_AUTHORIZATION tokens in total')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze web log files to count unique HTTP_AUTHORIZATION tokens.')
    parser.add_argument('log_dir', help='Directory containing log files (e.g., logs/)')
    parser.add_argument('years', nargs='+', help='Year(s) to include (e.g., 2024 or 2023 2024)')

    args = parser.parse_args()
    main(args.log_dir, args.years)
