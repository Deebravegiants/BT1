# [?] fix: prevent subtraction underflow in `NeighborStats::get_bandwidth`

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-07-01
Source: https://github.com/stacks-network/stacks-core/commit/b2b586f83148f800cd519aa4e04a423dc090aed8
Type: security-commit

## Details
fix: prevent subtraction underflow in `NeighborStats::get_bandwidth`

My mock-miner crashed overnight because the subtraction in the `else`
branch underflowed. While this won't crash a release build (and is
unlikely on a true 24/7 node, which won't go into energy saving like
apparently my laptop did), we should still handle it.
