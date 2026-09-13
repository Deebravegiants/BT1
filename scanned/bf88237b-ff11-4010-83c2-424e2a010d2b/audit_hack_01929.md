# [M] 5.1 Unexpected Staking of Tokens

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Risk Accepted

Since the spent assets are not validated against the Balancer v2 pool's underlying assets,
lendAndStake() could stake LP tokens from the vault along with the newly generated ones.

Consider the following scenario

```
1.Vault holds 1 Balancer LP
2.Manager triggers lendAndStake where the underlyings of the Balancer LP's pool and Balancer
LP are specified as spent assets.
