# [?] fix(share/discovery): deadlock in limitedSet (#2190)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-05-13
Source: https://github.com/celestiaorg/celestia-node/commit/9baade4bd0300dabcd160c185e145a824c128e30
Type: security-commit

## Details
fix(share/discovery): deadlock in limitedSet (#2190)

The deadlock eventually blocks the disconnect event processing in Discovery, causing libp2p connection processing to stall. It was discovered via libp2p metrics
