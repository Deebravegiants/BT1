# [?] fix(telemetry): Fix panic when stopping node with telemetry (#11914)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-08-09
Source: https://github.com/near/nearcore/commit/598a101a2c9baa2f07eab389e3129579bc773007
Type: security-commit

## Details
fix(telemetry): Fix panic when stopping node with telemetry (#11914)

We observed that nodes on `2.1.0-rc.2` were printing a panic after
receiving a signal to stop. [zulip
conversation](https://near.zulipchat.com/#narrow/stream/308695-nearone.2Fprivate/topic/2.2E1.2E0-rc2.20panic.20on.20shutdown).

We looked into the problem and found out that it's caused by the
destructor of `awc::Client`.
The logic went like this:

* Node operator enables uploading telemetry in `config.json`
* `neard` is started and `TelemetryActor` is spawned to upload telemetry
data to the specified endpoints
* `TelemetryActor` creates an instance of `awc::Client` to perform HTTP
POST requests with telemetry data.
* `awc::Client` maintains a connection pool with open connections that
can be reused for making requests to the same host
* After making a request, the connection is kept alive and put in this
pool
* At some point the node receives a signal to stop and the runtime is
stopped
* After that `awc::Client` is destroyed and its destructor goes over the
connections in the pool and closes them
* To close a connection, the destructor spawns a future and uses
`tokio::time::timeout`. Calling `tokio::time::timeout` after the runtime
has been closed is illegal and causes a panic.

To fix the issue we can disable keeping the connections alive. We can
force the client to close the connection after performing a request.
Then there are no connections in the pool and the destructor doesn't
enter the panicking code path.

## Patch
### chain/telemetry/src/lib.rs
```diff
@@ -92,6 +92,7 @@ impl Handler<TelemetryEvent> for TelemetryActor {
                 self.client
                     .post(endpoint.clone())
                     .insert_header(("Content-Type", "application/json"))
+                    .force_close() // See https://github.com/near/nearcore/pull/11914
                     .send_json(&msg.content)
                     .map(move |response| {
                         let result = if let Err(error) = response {
```
