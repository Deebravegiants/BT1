# [?] [kimiko] cl/sentinel: fix peerstore data race in concurrent peer connections (#19603)  (#19616)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-10
Source: https://github.com/erigontech/erigon/commit/2d94e91a23edfdad4b76aa393c0cdca3eb255762
Type: security-commit

## Details
[kimiko] cl/sentinel: fix peerstore data race in concurrent peer connections (#19603)  (#19616)

closes #19603 
## Summary
- Fix data race between Host.Connect() and Peerstore().RemovePeer() in
libp2p's memoryAddrBook caused by concurrent addAddrsUnlocked() and
background gc() goroutine
- Move the per-connection semaphore from a local variable in
listenForPeers() to a shared connectSem field on the Sentinel struct, so
all connection paths (listenForPeers, findPeersForSubnets,
connectWithAllPeers) serialize through the same semaphore
- Add unit tests for semaphore initialization, concurrency bounds,
release/reacquire cycle, and context cancellation
## Problem
Issue #19603: concurrent Host.Connect() calls trigger a data race in
libp2p v0.37.2's in-memory address book. The race occurs between
addAddrsUnlocked() (called during connect) and the background gc()
goroutine
that cleans expired addresses.
## Fix
Previously, only listenForPeers() used a local semaphore —
findPeersForSubnets() and connectWithAllPeers() had no concurrency
control at all. This PR:
1. Adds connectSem *semaphore.Weighted to the Sentinel struct,
initialized with goRoutinesOpeningPeerConnections (4) capacity
2. All three connection paths now acquire from the shared semaphore
before calling ConnectWithPeer
3. This serializes peerstore writes enough to avoid the race without
reducing throughput (4 concurrent connections is the existing limit)

---------

Co-authored-by: JkLondon <me@ilyamikheev.com>
Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
Co-authored-by: info@weblogix.biz <admin@10gbps.weblogix.it>
