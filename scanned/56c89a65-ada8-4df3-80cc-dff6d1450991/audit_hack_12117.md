# [M] Diamond.sol locks up Ether it receives.

## Summary
Severity: Medium
Reporter: Viktor_Cortess
Source: https://github.com/sherlock-audit/2023-06-symmetrical/blob/main/symmio-core/contracts/Diamond.sol#L13
Type: audit-issue

## Details
# Diamond.sol locks up Ether it receives.

## Summary

The Diamond contract can receive ETH. But there’s no way of ever retrieving that ETH from the contract. The funds will be locked up.


## Vulnerability Detail

## Impact

## Code Snippet
https://github.com/sherlock-audit/2023-06-symmetrical/blob/main/symmio-core/contracts/Diamond.sol#L13
## Tool used

Manual Review

## Recommendation

Add the necessary logic to release the ETH it gets.
