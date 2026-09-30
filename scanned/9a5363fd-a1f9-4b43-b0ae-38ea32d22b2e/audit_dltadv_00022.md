# [M] Consensus flaw in github.com/ethereum/go-ethereum

## Summary
Severity: Medium
Advisory: GO-2021-0105
Aliases: CVE-2020-26265, GHSA-xw37-57qp-9mm4
Package: github.com/ethereum/go-ethereum
Published: 2021-07-28
Source: https://osv.dev/vulnerability/GO-2021-0105
Type: chain-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=1.9.4 <1.9.20

## Details
Due to an incorrect state calculation, a specific set of transactions could cause a consensus disagreement, causing users of this package to reject a canonical chain.

## References
- https://github.com/ethereum/go-ethereum/pull/21080
- https://github.com/ethereum/go-ethereum/commit/87c0ba92136a75db0ab2aba1046d4a9860375d6a
