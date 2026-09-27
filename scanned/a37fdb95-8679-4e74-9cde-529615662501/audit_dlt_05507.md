# [?] Reject lamport underflow in event parent deserialization (#981)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2026-05-20
Source: https://github.com/0xsoniclabs/sonic/commit/33877f981af65949675d01773d4b89dcb189e34b
Type: security-commit

## Details
Reject lamport underflow in event parent deserialization (#981)

A peer-controlled lamportDiff exceeding the event's own lamport causes a silent uint32 underflow,
producing a garbage parent ID that stalls in the DAG buffer indefinitely without triggering a peer ban.
Reject such events with ErrMalformedEncoding instead.
