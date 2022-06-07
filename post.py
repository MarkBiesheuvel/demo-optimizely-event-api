from json import loads as json_decode, dumps as json_encode
from requests import post
from uuid import uuid4
from time import time

URL = 'https://logx.optimizely.com/v1/events'


def get_data_file():
    with open('datafile.json', 'r') as file:
        return file.read()


def main():
    datafile = json_decode(get_data_file())

    timestamp = int(time() * 1000)

    account_id = datafile['accountId']
    experiment = datafile['experiments'][0] # Only one experiment
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
                        'decisions': [
                            {
                                'campaign_id': campaign_id,
                                'experiment_id': experiment_id,
                                'variation_id': variation_ids[visitor_id % number_of_variations],
                                'is_campaign_holdback': False
                            }
                        ],
                        'events': [
                            {
                                'entity_id': campaign_id,
                                'type': 'campaign_activated',
                                'timestamp': timestamp,
                                'uuid': str(uuid4()),
                            }
                        ]
                    }
                ]
            }
            # Note if this number gets too big, the request might exceed the 10MB limit
            for visitor_id in range(1500, 2000)
        ],
        'enrich_decisions': True,
        'anonymize_ip': True,
        'client_name': 'Optimizely/event-api-test',
        'client_version': '0.0.1'
    }

    response = post(URL, json=payload)
    print(response.status_code)


if __name__ == '__main__':
    main()
