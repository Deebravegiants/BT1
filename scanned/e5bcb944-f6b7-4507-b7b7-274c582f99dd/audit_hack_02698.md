# [M] Manipulations of withdrawalFee64x64/performanceFee64x64

## Summary
Severity: Medium
Reporter: cccz
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L155-L190
Type: audit-issue

## Details
# Manipulations of withdrawalFee64x64/performanceFee64x64

## Summary
Manipulations of withdrawalFee64x64/performanceFee64x64

## Vulnerability Detail

The owner can set the performanceFee64x64/withdrawalFee64x64 to a number close to ONE_64x64 in the setPerformanceFee64x64/setWithdrawalFee64x64 functions of the VaultAdmin contract, which may cause the             feeInCollateral in the _collectPerformanceFee function and feeInCollateral/feesInShortContracts in _collectWithdrawalFee function to be too large.

## Impact
This causes the user to receive too few tokens.
## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L155-L190
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L367-L389
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L515-L526
## Tool used

Manual Review

## Recommendation

Consider limiting performanceFee64x64/withdrawalFee64x64 in setPerformanceFee64x64/setWithdrawalFee64x64 function
