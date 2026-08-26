# [?] node/pkg/p2p: Prevent potential nil pointer dereference when processing heartbeats

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2023-11-14
Source: https://github.com/wormhole-foundation/wormhole/commit/dfbdc9afb4342e1de0998bd1270a3e951958238f
Type: security-commit

## Details
node/pkg/p2p: Prevent potential nil pointer dereference when processing heartbeats

Resolves the problem occurring when dereferencing a nil `gk *ecdsa.PublicKey`
during heartbeat processing. This issue arises when non-guardian processes
utilizing the p2p package set the key to `nil`.
