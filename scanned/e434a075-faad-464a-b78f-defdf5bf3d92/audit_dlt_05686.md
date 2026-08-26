# [?] Fix deadlock on engine start (#1685)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-24
Source: https://github.com/celo-org/celo-blockchain/commit/00a9a9d191becec1ca922490674efbfeac3101a8
Type: security-commit

## Details
Fix deadlock on engine start (#1685)

* Fix deadlock during StartValidating

StartValidating makes a call to RefreshValPeers while holding
coreMu and RefreshValPeers waits for all validator peers to be deleted
and then reconnects to known validators.

If any of those peers has called IsValidating before RefreshValPeers
tries to delete them, the system gets stuck in a deadlock because
IsValidating also tries to acquire coreMu. The peer will never acquire
coreMu because it is held by StartValidating, and StartValidating will
never return because it is waiting for all peers to disconnect.

This commit makes coreStarted into an atomic variable so that peers can
make threadsafe calls to IsValidating without needing to acquire
coreStarted.

* Fix long wait for nodes to connect

At test startup sometimes nodes were taking in the region of 30s to connect
whilst other times it was happening in μs. The problem was we were
trying to connect all peers to all other peers. That meant that for any
two peers they would both dial each other. Sometimes if this occurred
close enough in time both sides would hang up the connections (I call
this cross dialing). This happens because each side counts their
outgoing connection as connected and then when the incoming connection
arrives they drop it because they see themselves as already connected.
When this happened nodes would retry after some time probably 30s and
then be connected.

The fix was to ensure that for any two nodes only one of them dials the
other.
