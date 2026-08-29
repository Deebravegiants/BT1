# [M] V3Vault::_deposit incorrectly validates the global lending limit and allows borrowing of assets above the limit

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-27
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/64
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L961


# Vulnerability details

## Vulnerability details

`V3Vault` applies a global limit on the total amount of assets that can be deposited for borrowing. This limit is enforced through the `globalLendLimit` state variable, set by the contract owner.

This is how the limit is applied in the `_deposit()` function:

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L961-L962
```solidity
  function _deposit(address receiver, uint256 amount, bool isShare, bytes memory permitData)
        internal
        returns (uint256 assets, uint256 shares)
    {
        ....
        
        // check for global limit
        if (totalSupply() + shares > globalLendLimit) {
            revert GlobalLendLimit();
        }
        
        // check for daily limit
        if (assets > dailyLendIncreaseLimitLeft) {
            revert DailyLendIncreaseLimit();
        }

        ....
    }
```

If you look closely you can see that `globalLendLimit` is compared against the total shares. This is wrong since `globalLendLimit` is measured in terms of assets, not shares. This can be further validated by looking at the `maxDeposit()` & `maxMint()` functions:

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L322

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/64_
