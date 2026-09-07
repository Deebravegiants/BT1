# [?] [sc-rpc-server] Fix panic while dropping the RPC runtime on start_ser… (#12847)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-08-12
Source: https://github.com/paritytech/polkadot-sdk/commit/f209831c0e48bf1a3462199e65f17ff6aa68ec13
Type: security-commit

## Details
[sc-rpc-server] Fix panic while dropping the RPC runtime on start_ser… (#12847)

# Description

`start_server` panicked instead of returning its error on both of its
failure
paths, masking the underlying cause. An operator who pins
`--rpc-endpoint` to a
port that is already in use saw a tokio runtime panic rather than
"Address already in use".

The dedicated RPC `tokio::runtime::Runtime` is now held in a guard for
the
duration of `start_server`, so every exit path shuts it down with
`shutdown_background()` and the original error reaches the caller.

Closes #12785

## Integration

No public API change — `RuntimeGuard` is private and `start_server`'s
signature
is unchanged, so downstream code needs no modification. `sc-rpc-server`
takes a
`patch` bump.

There is one behavioural change worth knowing about. Previously, a
non-optional
endpoint that failed to bind (or all endpoints failing) aborted the
process with
a tokio panic. Now the error propagates normally, so
`sc_service::start_rpc_servers` returns `Err` and the node fails to
start with a
readable message instead of a panic. Anything that was (accidentally)
relying on
the process dying at that point will now see a `Result` it must handle —
in
practice this only affects the error message operators see.

_Trimmed to 38 lines — full report: https://github.com/paritytech/polkadot-sdk/commit/f209831c0e48bf1a3462199e65f17ff6aa68ec13_
