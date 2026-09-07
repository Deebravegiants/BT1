# [M] Loss of precision in the YieldVault causes DoS when depositing from the Vault

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-24
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/79
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L1176-L1184


# Vulnerability details

# Title
Loss of precision in the YieldVault causes DoS when depositing from the Vault

## Original Issue
[M-22 - Loss of precision leads to undercollateralized](https://github.com/code-423n4/2023-07-pooltogether-findings/issues/143)

## Details
The original demonstrates how the Vault could fall into undercollateralization mode if the YieldVault rounds down the deposits causing a loss of precision.
- The problem was caused because the number of minted shares (_totalSupplyAmount) would be greater than the number of deposited assets in the YieldVault (_withdrawableAssets) because of the loss of precision when rounding down the amount of deposited assets in the YieldVault.

## Mitigation
The mitigation was to refactor the way the Vault determines if it's collateralized or not, as part of this change, the `_currentExchangeRate()` function was removed, and instead new logic was implemented to make that the shares are fully backed 1:1 to assets in the YieldVault.
Now, with the new logic, when depositing in the Vault, there is a check that validates if the deposited assets in the YieldVault were the exact amount of deposited assets.



### Conclusion of the Mitigation and Proof of Concept of the New Bug
The implemented mitigation prevents the Vault from falling into under-collateralization but now introduces a new bug where the deposits could fall into DoS because of the loss of precision in the YieldVault because most vaults will do rounds-down shares calculations.
For example: depositing `1000000000`, but it can only withdraw `999999999`.
- Using the above example with the new implementation:
  - 1. The vault will deposit into the YieldVault `1000000000`
  - 2. The YieldVault will cause the loss of precision, thus, the totalWithdrawableAssets in the YieldVault was increased by `999999999` instead of `1000000000`.
  - 3. The Vault will validate if the withdrawableAssetsAfter the deposit is greater than the previousWithdrawableAssets + the depositedAmount
  - 4. The check will fail because the withdrawableAssetsAfter is less than (previousWithdrawableAssets + the depositedAmount)
    - The reason is because **withdrawableAssetsAfter is actually (previousWithdrawableAssets + `999999999`)** (Because of the loss of precision)
    - **_expectedWithdrawableAssets == (previousWithdrawableAssets + `1000000000`)**

    - So **the check is actually comparing ==> (previousWithdrawableAssets + `999999999`) < (previousWithdrawableAssets + `1000000000`)**, thus, the tx will be reverted!

```solidity
function _deposit(
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/79_
