# [?] Fix panic in blob cache when scs array is empty or shorter than commitments (#15581)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2025-08-12
Source: https://github.com/OffchainLabs/prysm/commit/eace128ee9ef7b6b7d76b232045f47a173a71216
Type: security-commit

## Details
Fix panic in blob cache when scs array is empty or shorter than commitments (#15581)

* Fix panic in beacon-chain/das/blob_cache.go

* Regression test for empty/short scs array panic

* Changelog fragment
