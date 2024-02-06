The project uses Linux Chorme driver and we only use 1 CPU to avoid unnecessary errors.

# Target site
[United States Power Outage Tracker](https://data.usatoday.com/national-power-outage-map-tracker/)

# Run the code
```
pip install -r requirements.txt
python main.py --state-abbr [str] --start-time [str] --end-time [str] --output-format [str]
# state-abbr: Abbrivation of state, default='CA'
# start-time: format '%Y%m%d%H', default: '2024012118'
# end-time: format '%Y%m%d%H', default: '' (means now)
# output-format: default: 'csv', support 'parquet'
# e.g.
# $ python main.py --start-time 2024020300
# Initializing driver...
# Scraping CA: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 58/58 [02:33<00:00,  2.64s/it]
# Saved results to outputs/CA_2024020300_2024020609.csv
```

# Output
Check outputs [here](outputs)

# Preview
| fdate                | number of customers without power | county         | state | fips  |
|----------------------|-----------------------------------|----------------|-------|-------|
| 2024-02-03 00:00:00  | 11                                | Alameda County | CA    | 06001 |
| 2024-02-03 01:00:00  | 11                                | Alameda County | CA    | 06001 |
| 2024-02-03 02:00:00  | 11                                | Alameda County | CA    | 06001 |
| 2024-02-03 03:00:00  | 11                                | Alameda County | CA    | 06001 |
| 2024-02-03 04:00:00  | 0                                 | Alameda County | CA    | 06001 |
