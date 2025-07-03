# log_auth_stats.py
import os
import re
import argparse
import csv
from collections import defaultdict

def main(log_dir, years_to_include):
    # Regex to extract the HTTP_AUTHORIZATION value
    auth_pattern = re.compile(r'HTTP_AUTHORIZATION: ([^\s#]+)')
    # Regex to check if token is a valid UUID
    uuid_pattern = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-'
                              r'[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
                              r'[0-9a-fA-F]{12}$')

    monthly_auth_tokens = defaultdict(set)
    yearly_auth_tokens = defaultdict(set)

    monthly_token_calls = defaultdict(lambda: defaultdict(int))
    yearly_token_calls = defaultdict(lambda: defaultdict(int))

    # Process log files
    for filename in os.listdir(log_dir):
        if filename.startswith('oc-') and filename.endswith('.txt'):
            parts = filename[3:-4].split('-')
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
                            # Skip "None", "bearer", "Basic", "NTLM", etc.
                            if token != 'None' and uuid_pattern.match(token):
                                monthly_auth_tokens[year_month].add(token)
                                yearly_auth_tokens[year].add(token)
                                monthly_token_calls[year_month][token] += 1
                                yearly_token_calls[year][token] += 1
            except Exception as e:
                print(f'Error reading {file_path}: {e}')

    # Print stats
    print('\n📊 Monthly stats:')
    for ym in sorted(monthly_auth_tokens):
        count = len(monthly_auth_tokens[ym])
        print(f'  {ym}: {count} unique valid tokens')
        print('    Calls per token:')
        for token, calls in sorted(monthly_token_calls[ym].items(), key=lambda x: -x[1]):
            print(f'      Token: {token} -> {calls} calls')

    print('\n📊 Yearly stats:')
    for year in sorted(yearly_auth_tokens):
        count = len(yearly_auth_tokens[year])
        print(f'  {year}: {count} unique valid tokens')
        print('    Calls per token:')
        for token, calls in sorted(yearly_token_calls[year].items(), key=lambda x: -x[1]):
            print(f'      Token: {token} -> {calls} calls')

    # Save to CSV
    save_to_csv('monthly_stats.csv', monthly_token_calls)
    save_to_csv('yearly_stats.csv', yearly_token_calls, is_yearly=True)

    print('\n✅ CSV files saved: monthly_stats.csv, yearly_stats.csv')

def save_to_csv(filename, token_calls_dict, is_yearly=False):
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if is_yearly:
            writer.writerow(['year', 'token', 'calls'])
        else:
            writer.writerow(['year_month', 'token', 'calls'])

        for period in sorted(token_calls_dict):
            for token, calls in sorted(token_calls_dict[period].items(), key=lambda x: -x[1]):
                writer.writerow([period, token, calls])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze log files to count valid HTTP_AUTHORIZATION UUID tokens and calls.')
    parser.add_argument('log_dir', help='Directory containing log files (e.g., logs/)')
    parser.add_argument('years', nargs='+', help='Year(s) to include (e.g., 2024 or 2023 2024)')

    args = parser.parse_args()
    main(args.log_dir, args.years)
