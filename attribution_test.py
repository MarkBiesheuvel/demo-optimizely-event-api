from json import loads as json_decode, dumps as json_encode
from requests import post
from uuid import uuid4
from time import time, sleep
from itertools import cycle

# Log API endpoint
url = 'https://logx.optimizely.com/v1/events'

# Marks account
account_id = '21537940595'

# Event `like`
event_id = '22645203584'
event_key = 'like'

# A/B test on `tanka` flag
experiment_id = '9300000149156'
campaign_id = '9300000113985'

# Attribute `view_type`
attribute_id = '22639503163'
attribute_key = 'view_type'

# On variation
variation_id = '109279'


def timestamp():
    return int(time() * 1000)


def get_decision():
    return {
        'campaign_id': campaign_id,
        'experiment_id': experiment_id,
        'variation_id': variation_id,
        'is_campaign_holdback': False
    }


def get_decision_event():
    return {
        'entity_id': campaign_id,
        'type': 'campaign_activated',
        'timestamp': timestamp(),
        'uuid': str(uuid4())
    }


def get_conversion_event():
    return {
        'entity_id': event_id,
        'key': event_key,
        'timestamp': timestamp(),
        'uuid': str(uuid4())
    }


def get_attribute(attribute_value):
    return {
        'type': 'custom',
        'entity_id': attribute_id,
        'key': attribute_key,
        'value': attribute_value,
    }


def get_payload(number, enrich_decisions, attribute_value):
    visitor_id = 'visitor number={} enrich={}'.format(number, 'y' if enrich_decisions else 'n')
    print('Sending event for visitor "{}" and attribute value "{}"'.format(visitor_id, attribute_value))

    return {
        'account_id': account_id,
        'visitors': [
            {
                'visitor_id': 'visitor number={} enrich={}'.format(number, enrich_decisions),
                'attributes': [
                    get_attribute(attribute_value),
                ],
                'snapshots': [
                    {
                        'decisions': [
                            get_decision(),
                        ],
                        'events': [
                            get_decision_event(),
                            get_conversion_event(),
                        ]
                    }
                ]
            }
        ],
        'enrich_decisions': enrich_decisions,
        'anonymize_ip': True,
        'client_name': 'Optimizely/demo-optimizely-event-api',
        'client_version': '0.0.1'
    }


def send_payload(payload):
    # print(payload)
    post(url, json=payload)


def main():

    visitors = list(zip(range(10), cycle([True, False])))

    for (number, enrich_decisions) in visitors:
        payload = get_payload(number, enrich_decisions, 'Webview')
        send_payload(payload)

    sleep(90)

    for (number, enrich_decisions) in visitors:
        payload = get_payload(number, enrich_decisions, 'Native')
        send_payload(payload)

    sleep(90)

    for (number, enrich_decisions) in visitors:
        payload = get_payload(number, enrich_decisions, 'Webview')
        send_payload(payload)

    sleep(90)

    for (number, enrich_decisions) in visitors:
        payload = get_payload(number, enrich_decisions, 'Native')
        send_payload(payload)


if __name__ == '__main__':
    main()
