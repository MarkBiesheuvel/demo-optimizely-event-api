from enum import Enum
from os import getenv
from time import sleep, perf_counter_ns
from optimizely import optimizely, event_dispatcher
from optimizely.decision.optimizely_decide_option import OptimizelyDecideOption
from optimizely.event import event_processor


def get_data_file():
    with open('datafile.json', 'r') as file:
        return file.read()


class EventConfig(Enum):
    NONE = 0
    BATCHED = 1
    SYNC = 2


class Client():

    def __init__(self, datafile, event_config):
        kwargs = {
            'datafile': datafile
        }

        if (event_config == EventConfig.NONE):
            kwargs['default_decide_options'] = [
                OptimizelyDecideOption.DISABLE_DECISION_EVENT
            ]

        elif (event_config == EventConfig.SYNC):
            kwargs['event_dispatcher'] = event_dispatcher.EventDispatcher

        elif (event_config == EventConfig.BATCHED):
            kwargs['event_processor'] = event_processor.BatchEventProcessor(
                event_dispatcher.EventDispatcher,
                batch_size=20,
                flush_interval=0.1,
                start_on_init=True,
            )


        self.optimizely = optimizely.Optimizely(**kwargs)

    def decide(self, user_id):
        user = self.optimizely.create_user_context(user_id, {})
        decision = user.decide('sorting_algorithm')


def main():
    datafile = get_data_file()

    for event_config in EventConfig:
        client = Client(datafile, event_config)

        number_of_users = 10 if event_config == EventConfig.SYNC else 10000

        start = perf_counter_ns()

        for i in range(0, number_of_users):
            client.decide(str(i))

        stop = perf_counter_ns()
        elapsed_time = (stop - start) / 1000000

        print(event_config)
        print('Time per user: {:.2f} ms'.format(elapsed_time / number_of_users))
        print('')


if __name__ == '__main__':
    main()

'''Example output:
EventConfig.NONE
Time per user: 0.04 ms

EventConfig.BATCHED
Time per user: 0.10 ms

EventConfig.SYNC
Time per user: 355.00 ms
'''
