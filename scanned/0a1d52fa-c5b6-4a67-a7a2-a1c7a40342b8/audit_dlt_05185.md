# [?] net: bound peer protocol list in HELLO to prevent O(n^2) DoS

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-06-02
Source: https://github.com/Conflux-Chain/conflux-rust/commit/1d388fb676046259381af288ddd9e6138a5fa321
Type: security-commit

## Details
net: bound peer protocol list in HELLO to prevent O(n^2) DoS

A HELLO packet can be up to ~16MB (the 3-byte length prefix in
connection.rs), and `read_hello` decoded the peer-supplied `peer_caps`
list without any length bound, then scanned it for duplicate protocols
with an O(n^2) nested loop. Since `read_hello` runs inline on the single
network event-loop poll thread, one ~16MB packet (~2.8M entries) could
stall all inbound P2P processing for the whole node for minutes to hours.

Bound the advertised protocol count before decoding via
`iter().take(N + 1).count()` (constant-time thanks to the rlp offset
cache), rejecting peers that advertise more than a sane maximum, and
replace the O(n^2) duplicate scan with an O(n) HashSet. Real peers
advertise only a handful of protocols (cfx, clp, hsb).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
