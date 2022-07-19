# Demo: Optimizely Event API

These are two scripts to demonstrate the Optimizely Events API.

## Why use the Event API

By default, any time the `decide` method is called in the SDK, automatically a request is send to the Event API. This introduces a bit of latency. The `performance.py` script shows the difference in performance/latency between not sending decision events, sending them in batches and sending them synchronously (default).

If the sending decision events is disabled in the SDK, it is still possible to send them "manully" to the Event API. (See below)

## Posting to Event API

The `post.py` shows how to make a post request to the API. In this example, various fields and IDs are retrieved from the datafile, but it is also possible to hardcode these IDs in the script or to store them in a local database.
