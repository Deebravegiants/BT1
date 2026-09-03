# [?] Fix Deadlock with StartValidating (#1719)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-10-15
Source: https://github.com/celo-org/celo-blockchain/commit/6453534583e45cf0e082973bb68814d23a6d7b27
Type: security-commit

## Details
Fix Deadlock with StartValidating (#1719)

* Add more e2e tests to the celo-blockchain repo

* replicastate: Hold mu on NewChainHead

* Remove coreMu read lock around rs.NewChainHead

This fixes a deadlock introduced when the lock was added. This does not
introduce a unsynchronized access because coreIsStarted is an atomic.
