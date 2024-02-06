from bs4 import BeautifulSoup
import os
import pandas as pd
import json
import re
from tqdm import tqdm
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from argparse import ArgumentParser

import warnings
warnings.filterwarnings('ignore')

main_url = 'https://data.usatoday.com/national-power-outage-map-tracker/area/'

def init_driver(headless=True):
    print('Initializing driver...')
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def clean_json_string(input_str):
    # Initial clean-up steps as before
    input_str = re.sub(r"//.*?\n|/\*.*?\*/", "", input_str, flags=re.DOTALL)  # Remove comments
    input_str = re.sub(r"(?<!\\)'", '"', input_str)  # Replace single quotes with double quotes

    # New step: Try to isolate the JSON object by cutting off extra data
    # This step is highly specific to the format of your data and may need adjustment
    end_of_json_match = re.search(r"}\s*;", input_str)  # Look for the end of the JSON object followed by a semicolon
    if end_of_json_match:
        input_str = input_str[:end_of_json_match.end()-1]  # Exclude everything after the end of the JSON object

    return input_str

def formatting(json_str):
    cleaned_json_str = clean_json_string(json_str)
    try:
        data = json.loads(cleaned_json_str)
        fdate = data['fdate']
        dataset_data = data['datasets'][0]['data']
        label = data['datasets'][0]['label']
        df = pd.DataFrame({'fdate': fdate, label: dataset_data})
        return df
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return None
    
def scrape_county(dic, driver):
    url = main_url + dic['suffix']
    driver.get(url)

    # Wait for the necessary JavaScript to execute and load data
    # Example: time.sleep(5) or more sophisticated waiting
    # For better results, use explicit waits here to wait for a specific element or condition

    html_content = driver.page_source

    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script', type='text/javascript')

    for script in scripts:
        if 'var barChartData =' in script.text:
            pattern = re.compile(r"var barChartData = ({.*?})\s*function", re.DOTALL)
            match = pattern.search(script.text)
            if match:
                json_str = match.group(1)
                df = formatting(json_str)
                if df is not None:
                    df['county'] = dic['name']
                    df['state'] = dic['state']
                    df['fips'] = dic['fips']
                    return df, driver
                else:
                    print("Could not format data")

    return None, driver

def filter_by_date(df, start_time, end_time):
    # Ensure 'fdate' is in datetime format for filtering
    df['fdate'] = pd.to_datetime(df['fdate'], format='%Y%m%d%H')

    start_dt = datetime.strptime(start_time, '%Y%m%d%H')
    if end_time:
        end_dt = datetime.strptime(end_time, '%Y%m%d%H')
    else:
        end_dt = datetime.now()

    filtered_df = df[(df['fdate'] >= start_dt) & (df['fdate'] <= end_dt)]

    # Get min and max times from 'fdate' in the specified format
    min_time = filtered_df['fdate'].min().strftime('%Y%m%d%H')
    max_time = filtered_df['fdate'].max().strftime('%Y%m%d%H')

    return filtered_df, min_time, max_time

def output_formatting(df, path, format):
    if format == 'csv':
        df.to_csv(path + '.csv', index=False)
    elif format == 'parquet':
        df.to_parquet(path + '.parquet', index=False)
    else:
        df.to_csv(path + '.' + format, index=False)
    print(f'Saved results to {path}.{format}')

def main(state_abbr, start_time, end_time, output_format):
    driver = init_driver()
    os.makedirs('outputs', exist_ok=True)

    FIPS_df = pd.read_csv('state_and_county_fips_master.csv')
    target_df = FIPS_df[FIPS_df['state'] == state_abbr].copy()
    target_df['fips'] = target_df['fips'].apply(lambda x: '0'+str(x) if len(str(x)) < 5 else str(x))
    target_df['suffix'] = target_df['name'].str.replace(' ', '-') + '-' + target_df['state'] + '/' + target_df['fips'] + '/'
    target_df['suffix'] = target_df['suffix'].str.lower()

    results = []

    for record in tqdm(target_df.to_dict('records'), desc=f"Scraping {state_abbr}"):
        result, driver = scrape_county(record, driver)
        if result is not None:
            results.append(result)

    if results:  # Check if the list is not empty
        combined_df = pd.concat(results, ignore_index=True)
        filtered_df, start, end = filter_by_date(combined_df, start_time, end_time)
        filtered_df_path = f'outputs/{state_abbr}_{start}_{end}'
        output_formatting(filtered_df, filtered_df_path, output_format)
    else:
        print("No data was scraped.")
    driver.close()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--state-abbr', default='CA')
    parser.add_argument('--start-time', default='2024012118', help='YYYYMMDDHH')
    parser.add_argument('--end-time', default='', help='YYYYMMDDHH')
    parser.add_argument('--output-format', default='csv')
    opt = parser.parse_args()

    main(opt.state_abbr, opt.start_time, opt.end_time, opt.output_format)