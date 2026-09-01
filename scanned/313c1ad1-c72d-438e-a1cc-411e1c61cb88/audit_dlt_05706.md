# [?] graphdb: fix potential sql tx exhaustion

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-12-07
Source: https://github.com/lightningnetwork/lnd/commit/2d25bce1bf69e9ad4bdcfef5b4114f24b90ee63c
Type: security-commit

## Details
graphdb: fix potential sql tx exhaustion

We should avoid taking the lock of a mutex inside transaction.
Currently we also take this lock in other places and there is a
chance that in case the application lock aquires the lock but
all transactions are already blocked waiting for the mutex to
unlock, we end up in a deadlock.
