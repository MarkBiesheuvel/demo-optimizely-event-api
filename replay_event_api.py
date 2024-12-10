from requests import post
import csv
import requests
from more_itertools import chunked
from time import sleep
from uuid import uuid4
from datetime import datetime

# Event API endpoint
URL = 'https://logx.optimizely.com/v1/events'

# Account ID of customer
ACCOUNT_ID = '30331290497'

with open('visitors-off-variation.csv') as file:
    reader = csv.reader(file)

    # Build a lookup map (column name -> index) from the header row
    columns = {
        column_name: index
        for (index, column_name) in enumerate(next(reader))
    }

    # Helper function to retrieve cell by column name
    def get(row, column_name):
        return row[columns[column_name]]

    # Helper function to parse timestamp
    def timestamp(row):
        timestamp = get(row, 'timestamp')
        date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        return int(date.timestamp() * 1000)

    # Transform every row from the CSV file
    visitors = (
        {
            'visitor_id': get(row, 'visitor_id'),
            'snapshots': [
                {
                    'decisions':  [
                        {
                            'campaign_id': get(row, 'campaign_id'),
                            'experiment_id': get(row, 'experiment_id'),
                            'variation_id': '1044265', # Overwriting the variation id
                            'is_campaign_holdback': False
                        }
                    ],
                    'events': [
                        {
                            'entity_id': get(row, 'campaign_id'),
                            'type': 'campaign_activated',
                            'timestamp': timestamp(row),
                            'uuid': str(uuid4())
                        }
                    ]
                }
            ]
        }
        for row in reader
    )

    payloads = (
        {
            'account_id': ACCOUNT_ID,
            'visitors': chunk,
            'enrich_decisions': True,
            'anonymize_ip': True,
            'client_name': 'replay_event_api.py',
            'client_version': '1'
        }
        for chunk in chunked(visitors, 50)
    )

    for payload in payloads:
        response = post(URL, json=payload)
        print(response.status_code)
        sleep(0.1)