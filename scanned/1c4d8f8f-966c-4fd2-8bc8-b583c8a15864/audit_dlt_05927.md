# [?] fix(autonatv2): don't panic in GetReachability after Close

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2026-07-22
Source: https://github.com/libp2p/go-libp2p/commit/f23601bf34bc8f440fe27ec61b41dee81f5cf1eb
Type: security-commit

## Details
fix(autonatv2): don't panic in GetReachability after Close

Close set an.peers = nil without holding an.mx while GetReachability
reads it under the lock: an unsynchronized write, and a nil pointer
panic in peersMap.Shuffled for callers racing with Close. The host
closes autonat before the address manager, so the reachability
tracker's probe workers can issue checks in exactly that window,
crashing the process during shutdown.

Guard the write with the mutex and return ErrNoPeers once closed;
the reachability tracker treats ErrNoPeers as persistent and backs
off its workers.

Assisted-By: Claude Fable 5
