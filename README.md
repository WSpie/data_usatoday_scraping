# Target site
[United States Power Outage Tracker](https://data.usatoday.com/national-power-outage-map-tracker/)

# Run the code
```
pip install -r requirements.txt
python main.py --state-abbr CA --start-time 2024020300 --end-time 2024020510
# state-abbr: Abbrivation of state
# start-time/ end-time: format '%Y%m%d%H'
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
