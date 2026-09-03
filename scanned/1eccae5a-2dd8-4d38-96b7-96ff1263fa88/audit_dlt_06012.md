# [?] fix: deadlock when shutting down gateway (#8990)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-11
Source: https://github.com/fedimint/fedimint/commit/5242f22969886f0e64162ea82ccefef2be260a76
Type: security-commit

## Details
fix: deadlock when shutting down gateway (#8990)

There is a deadlock that can happen in the gateway when the `/stop`
endpoint is called to safely shutdown the gateway. It is supposed to
allow current payments to finish, but this deadlock prevents that and
stalls the gateway indefinitely.

Fix is to make the `ShuttingDown` state terminal, so that the lightning
re-connect thread cannot change it back to running and also release the
write lock when shutting down, which allows for concurrent payments to
finish.

A test has been added to cover this scenario.
