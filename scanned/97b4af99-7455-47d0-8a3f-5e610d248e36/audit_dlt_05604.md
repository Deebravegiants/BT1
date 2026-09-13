# [?] core/filtermaps: fix deadlock in filtermap callback (#31708)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-04-25
Source: https://github.com/ethereum/go-ethereum/commit/b6bdd698a0584a8e62a34b6aa6871e8bf8b6e6fb
Type: security-commit

## Details
core/filtermaps: fix deadlock in filtermap callback (#31708)

This PR fixes a deadlock situation is deleteTailEpoch that might arise
when
range delete is running in iterator based fallback mode (either using
leveldb
database or the hashdb state storage scheme). 

In this case a stopCb callback is called periodically that does check
events,
including matcher sync requests, in which case it tries to acquire
indexLock
for read access, while deleteTailEpoch already held it for write access.

This pull request removes the indexLock acquiring in
`FilterMapsMatcherBackend.synced`
as this function is only called in the indexLoop.

Fixes https://github.com/ethereum/go-ethereum/issues/31700
