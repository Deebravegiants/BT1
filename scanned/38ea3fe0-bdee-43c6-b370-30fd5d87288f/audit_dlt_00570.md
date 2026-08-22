# [?] Fix IndexOutOfBoundsException race condition in TransactionBroadcaster (#10482)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-05-26
Source: https://github.com/besu-eth/besu/commit/77b4a04b3ea521b754588a9ca9feb8bc20ddbf4c
Type: security-commit

## Details
Fix IndexOutOfBoundsException race condition in TransactionBroadcaster (#10482)

* Fix IndexOutOfBoundsException race condition in TransactionBroadcaster

Signed-off-by: rakshaak29 <rakshaak29@gmail.com>

* test: add regression test for IndexOutOfBoundsException race condition in TransactionBroadcaster

When peerCount() and streamAvailablePeers() are called sequentially, peers can
disconnect between the two calls. This causes numPeersToSendFullTransactions
(calculated from peerCount) to exceed the actual number of peers returned by
streamAvailablePeers(), causing subList() to throw IndexOutOfBoundsException.

The new test reproduces this scenario: peerCount() returns 9 (sqrt = 3 full-tx
peers) but only 2 peers are available when streamAvailablePeers() is called.

Signed-off-by: rakshaak29 <rakshaak29@gmail.com>

* Fix spotless formatting

Signed-off-by: rakshaak29 <rakshaak29@gmail.com>

---------

Signed-off-by: rakshaak29 <rakshaak29@gmail.com>
Co-authored-by: Fabio Di Fabio <fabio.difabio@consensys.net>
