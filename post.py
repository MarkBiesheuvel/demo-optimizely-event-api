from json import loads as json_decode, dumps as json_encode
from requests import post
from uuid import uuid4
from time import time
from random import random

URL = 'https://logx.optimizely.com/v1/events'

DESIRED_CONVERSION_RATES = [0.2, 0.3, 0.2, 0.4, 0.3]


def get_data_file():
    # Retrieve datafile from local filesystem
    with open('datafile.json', 'r') as file:
        return file.read()


def get_decisions(campaign_id, experiment_id, variation_id):
    # Add decision result
    decisions = [
        {
            'campaign_id': campaign_id,
            'experiment_id': experiment_id,
            'variation_id': variation_id,
            'is_campaign_holdback': False
        }
    ]

    return decisions


def get_events(campaign_id, event_id, event_key, timestamp, conversion_rate):
    # Add decision event
    events = [
        {
            'entity_id': campaign_id,
            'type': 'campaign_activated',
            'timestamp': timestamp,
            'uuid': str(uuid4())
        }
    ]

    # Only add conversion event by random chance
    # TODO: retrieve actual events for user
    if random() < conversion_rate:
        events.append({
            'entity_id': event_id,
            'key': event_key,
            'timestamp': timestamp,
            'uuid': str(uuid4())
        })

    return events


def main():
    datafile = json_decode(get_data_file())

    # TODO: retrieve actual timestamps from database
    timestamp = int(time() * 1000)

    account_id = datafile['accountId']
    event = datafile['events'][0] # TODO: pick correct event, not just the first
    event_id = event['id']
    event_key = event['key']
    experiment = datafile['experiments'][0] # TODO: pick correct experiment, not just the first
    experiment_id = experiment['id']
    campaign_id = experiment['layerId']
    variation_ids = [variation['id'] for variation in experiment['variations']]
    number_of_variations = len(variation_ids)

    payload = {
        'account_id': account_id,
        'visitors': [
            {
                'visitor_id': str(visitor_id),
                'snapshots': [
                    {
                        'decisions': get_decisions(
                            campaign_id,
                            experiment_id,
                            variation_ids[visitor_id % number_of_variations] # TODO: retrieve variation which was shown to user
                        ),
                        'events': get_events(
                            campaign_id,
                            event_id,
                            event_key,
                            timestamp,
                            DESIRED_CONVERSION_RATES[visitor_id % number_of_variations]
                        )
                    }
                ]
            }
            # TODO: retrieve actual visitors from database
            for visitor_id in range(4000, 5000)
        ],
        'enrich_decisions': True,
        'anonymize_ip': True,
        'client_name': 'Optimizely/demo-optimizely-event-api',
        'client_version': '0.0.1'
    }

    # print(payload)
    response = post(URL, json=payload)
    print(response.status_code)


if __name__ == '__main__':
    main()
