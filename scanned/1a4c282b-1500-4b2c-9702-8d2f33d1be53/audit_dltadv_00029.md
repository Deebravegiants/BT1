# [H] Denial of service via OOM in github.com/cometbft/cometbft

## Summary
Severity: High
Advisory: GO-2023-1883
Aliases: CVE-2023-34451, GHSA-w24w-wp77-qffm
Package: github.com/cometbft/cometbft
Published: 2023-07-13
Source: https://osv.dev/vulnerability/GO-2023-1883
Type: chain-advisory

## Affected
- Go: `github.com/cometbft/cometbft` — affected >=0 <0.37.2

## Details
A bug in the CometBFT middleware causes the mempool's two data structures to fall out of sync. This can lead to duplicate transactions that cannot be removed, even after they are committed in a block. The only way to remove the transaction is to restart the node. This can be exploited by an attacker to bring down a node by repeatedly submitting duplicate transactions.

## References
- https://github.com/cometbft/cometbft/security/advisories/GHSA-w24w-wp77-qffm
- https://github.com/cometbft/cometbft/pull/890
- https://github.com/tendermint/tendermint/pull/2778
