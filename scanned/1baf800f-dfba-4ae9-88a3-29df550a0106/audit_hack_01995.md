# [M] 6.5 totalSupply Mapping Not Updated

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The ClaimFee contract has a totalSupply mapping which should track the total supply of claims per
ilk. However, neither the mintClaim nor burnClaim functions update the mapping.

Code corrected:

The totalSupply mapping is now updated accordingly in the mintClaim and burnClaim functions.
