# [?] fix(gateway): contain panics on the iroh api path

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/4fd2d7a5c49582fae0ec8b01701a66ba530fe1cb
Type: security-commit

## Details
fix(gateway): contain panics on the iroh api path

There was no `catch_unwind` anywhere in the gateway. Iroh requests are
spawned with `spawn_cancellable_silent` on the gateway's root task group,
so a panicking handler drops `TaskPanicGuard` with `completed == false`,
which shuts the task group down, returns from `Gateway::run` and exits
the process. Deployments run the gateway under `restart: unless-stopped`,
so a request that panics deterministically is a boot loop rather than a
single crash.

The exposure is public: the docker compose file binds the iroh listener
to `0.0.0.0:8177` and publishes the port, and the gateway's node id is
announced to every federation it serves, so it is discoverable.

The HTTP path needs no equivalent change: `axum::serve` spawns its
connection tasks outside any task group, so a handler panic there only
drops that one connection.

Wrap the iroh handler invocation in `catch_unwind` and answer a 500,
mirroring what `fedimint-server`'s iroh path does.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9
