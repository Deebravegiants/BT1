# [?] quic: fix integer underflow in ACK handler

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-03-01
Source: https://github.com/firedancer-io/firedancer/commit/0918bc166007bcd02efad0c39406b13af34d8419
Type: security-commit

## Details
quic: fix integer underflow in ACK handler

When a peer ACKs packet number 0 (the first packet in a connection),
the expression `largest_ack-1` wraps to ULONG_MAX. The subsequent
treap lookup idx_le(~0UL) returns the element with the largest key,
causing the skip_ceil computation to iterate from the wrong end of
the data structure. This incorrectly marks unrelated packets as
"lost", triggering spurious retransmissions.
