# [H] Lenders can drain the Vault when withdrawing

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-27
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/65
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L1007-L1010


# Vulnerability details

## Impact

`V3Vault` can be drained through the `withdraw()` function due to improper asset conversion.

## Vulnerability

[PR-14](https://github.com/revert-finance/lend/pull/14/files) introduced a couple of updates to the `V3Vault` contract in response [to the following finding](https://github.com/code-423n4/2024-03-revert-lend-findings/issues/222) in order to prevent liquidations from getting DOSed.

A changes has also been introduced to `_withdraw()` so that instead of reverting when a lender tries to withdraw more shares than he owns, the amount is automatically reduced to the max withdrawable shares for that lender. This is how the change looks:

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L1007-L1010
```solidity

 function _withdraw(address receiver, address owner, uint256 amount, bool isShare)
        internal
        returns (uint256 assets, uint256 shares)
    {
        ....

        if (isShare) {
            shares = amount;
            assets = _convertToAssets(amount, newLendExchangeRateX96, Math.Rounding.Down);
        } else {
            assets = amount;
            shares = _convertToShares(amount, newLendExchangeRateX96, Math.Rounding.Up);
        }

+        uint256 ownerBalance = balanceOf(owner);
+        if (shares > ownerBalance) {
+            shares = ownerBalance;
+            assets = _convertToAssets(amount, newLendExchangeRateX96, Math.Rounding.Down);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/65_
