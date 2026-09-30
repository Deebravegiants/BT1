# [M] Denial of service in github.com/tendermint/tendermint

## Summary
Severity: Medium
Advisory: GO-2021-0090
Aliases: CVE-2020-15091, GHSA-6jqj-f58p-mrw3
Package: github.com/tendermint/tendermint
Published: 2021-04-14
Source: https://osv.dev/vulnerability/GO-2021-0090
Type: chain-advisory

## Affected
- Go: `github.com/tendermint/tendermint` — affected >=0.33.0 <0.34.0-dev1.0.20200702134149-480b995a3172

## Details
Proposed commits may contain signatures for blocks not contained within the commit. Instead of skipping these signatures, they cause failure during verification. A malicious proposer can use this to force consensus failures.

## References
- https://github.com/tendermint/tendermint/pull/5426
- https://github.com/tendermint/tendermint/commit/480b995a31727593f58b361af979054d17d84340
- https://github.com/tendermint/tendermint/issues/4926
