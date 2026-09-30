# [M] Denial of service when syncing with a malicious peer in github.com/cometbft/cometbft

## Summary
Severity: Medium
Advisory: GO-2024-2951
Aliases: GHSA-hg58-rf2h-6rr7
Package: github.com/cometbft/cometbft
Published: 2024-07-02
Source: https://osv.dev/vulnerability/GO-2024-2951
Type: chain-advisory

## Affected
- Go: `github.com/cometbft/cometbft` — affected >=0.38.0 <0.38.8

## Details
A malicious peer can cause a syncing node to panic during blocksync. The syncing node may enter into a catastrophic invalid syncing state or get stuck in blocksync mode, never switching to consensus. Nodes that are vulnerable to this state may experience a Denial of Service condition in which syncing will not work as expected when joining a network as a client.

## References
- https://github.com/cometbft/cometbft/security/advisories/GHSA-hg58-rf2h-6rr7
- https://github.com/cometbft/cometbft/commit/07866e11139127e415bd0339ac377b6e6a845533
- https://github.com/cometbft/cometbft/commit/8ba2e4f52d5e626e019501ba6420cc86d5de7857
