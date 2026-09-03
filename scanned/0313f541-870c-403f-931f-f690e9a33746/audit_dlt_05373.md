# [?] fix(connectionmanager): don't panic on wakeup send during shutdown (#989) (#1029)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2026-06-15
Source: https://github.com/kaspanet/rusty-kaspa/commit/1fe3697b4ebf5d5ceac33fbe3b73b8d3348b3325
Type: security-commit

## Details
fix(connectionmanager): don't panic on wakeup send during shutdown (#989) (#1029)

`force_next_iteration.send(()).unwrap()` panics when the event-loop receiver has
already been dropped (e.g. on shutdown). `add_connection_request` is reachable
from the `AddPeer` RPC handler, so an `AddPeer` racing with daemon shutdown can
panic the gRPC/wRPC handler task.

The wakeup is fire-and-forget: if the loop is gone the wakeup is moot (the loop
is exiting anyway, and a 30s ticker drives it otherwise), so ignore the send
error instead of unwrapping. Applies to both the constructor wakeup (lib.rs:74)
and the per-request wakeup (lib.rs:109).
