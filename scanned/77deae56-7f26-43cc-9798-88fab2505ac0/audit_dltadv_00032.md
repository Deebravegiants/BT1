# [H] Chain halt panic in github.com/cometbft/cometbft

## Summary
Severity: High
Advisory: GO-2024-2471
Aliases: GHSA-qr8r-m495-7hc4
Package: github.com/cometbft/cometbft
Published: 2024-01-23
Source: https://osv.dev/vulnerability/GO-2024-2471
Type: chain-advisory

## Affected
- Go: `github.com/cometbft/cometbft` — affected >=0.38.0 <0.38.3

## Details
A vulnerability in CometBFT’s validation logic for VoteExtensionsEnableHeight can result in a chain halt when triggered through a governance parameter change proposal on an ABCI2 Application Chain. If a parameter change proposal including a VoteExtensionsEnableHeight modification is passed, nodes running the affected versions may panic, halting the network.

## References
- https://github.com/cometbft/cometbft/security/advisories/GHSA-qr8r-m495-7hc4
- https://github.com/cometbft/cometbft/commit/5fbc97378b94b0945febe9549399e7c9c5df13ed
