# [?] eth/protocols/snap: fix data race on testPeer counters (#34802)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-04-24
Source: https://github.com/ethereum/go-ethereum/commit/8091994e7b5954827ad68ccca463647b220b1621
Type: security-commit

## Details
eth/protocols/snap: fix data race on testPeer counters (#34802)

The testPeer request counters (nAccountRequests, nStorageRequests,
nBytecodeRequests, nTrienodeRequests) were plain int fields incremented
with ++. These increments happen in Request* methods that are invoked
concurrently by the Syncer from multiple goroutines
(assignBytecodeTasks, assignStorageTasks, etc.), causing a data race
reliably detected by go test -race.

Change the counters to atomic.Int64 so increments and reads are
synchronized without introducing a mutex.

Fixes races detected in TestMultiSyncManyUseless,
TestMultiSyncManyUselessWithLowTimeout,
TestMultiSyncManyUnresponsive, TestSyncWithStorageAndOneCappedPeer,
TestSyncWithStorageAndCorruptPeer, and
TestSyncWithStorageAndNonProvingPeer.
