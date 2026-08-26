# [?] rpcserver: fix race condition in graph cache eviction

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-07-09
Source: https://github.com/lightningnetwork/lnd/commit/ef181adbc8bd4c41952a6a564e64bc842543ef90
Type: security-commit

## Details
rpcserver: fix race condition in graph cache eviction

The previous implementation of the graph cache evictor used
time.AfterFunc, which introduced a race condition. The closure
passed to AfterFunc could execute before the call returned and
assigned the timer to the r.graphCacheEvictor field.

This created a scenario where the closure would attempt to call
Reset() on a nil r.graphCacheEvictor, causing a panic.

This commit fixes the race by replacing time.AfterFunc with a
more robust pattern using time.NewTimer and a dedicated goroutine.
The new timer is created and assigned immediately, ensuring that
r.graphCacheEvictor is never nil when accessed.

The dedicated goroutine now safely manages the timer's lifecycle,
resetting it upon firing and stopping it gracefully upon server
shutdown, which also prevents goroutine leaks.
