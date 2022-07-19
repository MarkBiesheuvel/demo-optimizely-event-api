from enum import Enum
from os import environ as environment
from time import sleep, perf_counter_ns
from optimizely import optimizely, event_dispatcher
from optimizely.decision.optimizely_decide_option import OptimizelyDecideOption
from optimizely.event import event_processor


# Three different configurations for sending events
class EventConfig(Enum):
    NONE = 0
    BATCHED = 1
    SYNC = 2


# Wrapper class for Optimizely client
class Client():

    def __init__(self, event_config):
        # Load datafile with SDK key
        kwargs = {
            'sdk_key': environment.get('OPTIMIZELY_SDK_KEY')
        }

        # Prevent all decisions events from being send to Optimizely
        if (event_config == EventConfig.NONE):
            kwargs['default_decide_options'] = [
                OptimizelyDecideOption.DISABLE_DECISION_EVENT
            ]

        # Send each decision event as soon as it happens (synchronously)
        elif (event_config == EventConfig.SYNC):
            kwargs['event_dispatcher'] = event_dispatcher.EventDispatcher

        # Batch mutliple events together before sending
        elif (event_config == EventConfig.BATCHED):
            kwargs['event_processor'] = event_processor.BatchEventProcessor(
                event_dispatcher.EventDispatcher,
                batch_size=20,
                flush_interval=0.1,
                start_on_init=True,
            )

        # Initialize client with dynamic arguments
        self.optimizely = optimizely.Optimizely(**kwargs)

    def decide(self, user_id):
        # Create user context for user id and call decide method
        user = self.optimizely.create_user_context(user_id, {})
        return user.decide('header_text')


def main():
    # Iterate over the three different configuration types
    for event_config in EventConfig:
        client = Client(event_config)

        # Synchronous events are slow, so use smaller sample size
        number_of_users = 10 if event_config == EventConfig.SYNC else 10000

        # Start timer
        start = perf_counter_ns()

        # Perform a large number of operations to determine average time per call
        for i in range(0, number_of_users):
            client.decide(str(i))

        # Stop timer
        stop = perf_counter_ns()
        elapsed_time = (stop - start) / 1000000

        # Print results
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
