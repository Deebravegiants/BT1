# [M] Deadlock in github.com/cometbft/cometbft/consensus

## Summary
Severity: Medium
Advisory: GO-2023-1882
Aliases: CVE-2023-34450, GHSA-mvj3-qrqh-cjvr
Package: github.com/cometbft/cometbft
Published: 2023-07-06
Source: https://osv.dev/vulnerability/GO-2023-1882
Type: chain-advisory

## Affected
- Go: `github.com/cometbft/cometbft` — affected >=0.37.1 <0.37.2

## Details
An internal modification to the way PeerState is serialized to JSON introduced a deadlock when the new function MarshalJSON is called.

This function can be called in two ways. The first is via logs, by setting the consensus logging module to "debug" level (which should not happen in production), and setting the log output format to JSON. The second is via RPC dump_consensus_state.

## References
- https://github.com/cometbft/cometbft/security/advisories/GHSA-mvj3-qrqh-cjvr
- https://github.com/cometbft/cometbft/pull/524
- https://github.com/cometbft/cometbft/pull/863
- https://github.com/cometbft/cometbft/pull/865
