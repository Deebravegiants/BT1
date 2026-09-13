# [?] quic: prevent underflow in conn_tx with initial

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-03-01
Source: https://github.com/firedancer-io/firedancer/commit/9956c3f606892a974e33eba537316eb770bbadc0
Type: security-commit

## Details
quic: prevent underflow in conn_tx with initial

This is not actually a reachable bug today, but adds some defense
in depth, to make sure the padding calculation stays intact if
outgoing initial packet size increases.
