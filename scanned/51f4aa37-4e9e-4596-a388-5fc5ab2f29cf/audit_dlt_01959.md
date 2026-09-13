# [?] node/pkg/common: Fix race condition in PostObservationRequest

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2022-08-17
Source: https://github.com/wormhole-foundation/wormhole/commit/4712a6f774c9fec82be9ec4ccd82cb037161b691
Type: security-commit

## Details
node/pkg/common: Fix race condition in PostObservationRequest

Any goroutine can push into a channel so the current implementation has
a race condition where the channel can become full immediately after the
length check, causing the subsequent send on the channel to block.

Fix this by wrapping the send on the channel with a select block.
Control will fall through to the default case only if the actual send
operation blocks, avoiding the potential race with other goroutines.
