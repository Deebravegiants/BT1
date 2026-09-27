# [M] V3Vault::maxWithdrawal incorrectly converts balance to assets

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-27
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/63
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L345


# Vulnerability details

## Vulnerability details

The `maxWithdrawal()` function of `V3Vault` calculates the maximum amount of underlying tokens an account can withdraw based on the shares it owns.

The initial problem with `maxWithdrawal()` and `V3Vault` overall was that they were not implemented according to the specs of ERC-4626 standard [as outlined in the original issue](https://github.com/code-423n4/2024-03-revert-lend-findings/issues/249). In the case of `maxWithdrawal()` it did not consider the following [part of the spec](https://eips.ethereum.org/EIPS/eip-4626):

> MUST factor in both global and user-specific limits, like if withdrawals are entirely disabled (even temporarily) it MUST return 0.

In order to remediate the issue and make the `V3Vault` ERC-4626 compliant, protocol devs [prepared the following PR](https://github.com/revert-finance/lend/pull/15/files), where `maxWithdrawal()` was refactored so that it includes the actual daily limit that is applied when withdrawing assets:

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L335-L347
```solidity
 function maxWithdraw(address owner) external view override returns (uint256) {
-        (, uint256 lendExchangeRateX96) = _calculateGlobalInterest();
-        return _convertToAssets(balanceOf(owner), lendExchangeRateX96, Math.Rounding.Down);

+        (uint256 debtExchangeRateX96, uint256 lendExchangeRateX96) = _calculateGlobalInterest();

+        uint256 ownerShareBalance = balanceOf(owner);
+        uint256 ownerAssetBalance = _convertToAssets(ownerShareBalance, lendExchangeRateX96, Math.Rounding.Down);

+        (uint256 balance, ) = _getBalanceAndReserves(debtExchangeRateX96, lendExchangeRateX96);
+        if (balance > ownerAssetBalance) {
+            return ownerAssetBalance;
+        } else {
+            return _convertToAssets(balance, lendExchangeRateX96, Math.Rounding.Down);
+        }
    }
```

The problem with the new code is this part:

```solidity
   // @audit balance is already converted to assets
   (uint256 balance, ) = _getBalanceAndReserves(debtExchangeRateX96, lendExchangeRateX96);

    // @audit - converts to assets a second time
    } else {
        return _convertToAssets(balance, lendExchangeRateX96, Math.Rounding.Down);
    }
```

If we take a look at `_getBalanceAndReserves()` we can see that the returned `balance` is already converted to `assets`:

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L1107-L1116
```solidity
function _getBalanceAndReserves(uint256 debtExchangeRateX96, uint256 lendExchangeRateX96)
        internal
        view
        returns (uint256 balance, uint256 reserves)
    {
 --->       balance = totalAssets();
        uint256 debt = _convertToAssets(debtSharesTotal, debtExchangeRateX96, Math.Rounding.Up);
        uint256 lent = _convertToAssets(totalSupply(), lendExchangeRateX96, Math.Rounding.Up);
        reserves = balance + debt > lent ? balance + debt - lent : 0;
    }
```
This means that `maxWithdraw()` improperly converts `balance` a second time and will overinflate the result, especially when `debtExchangeRateX96` is high. 

## Impact

`V3Vault::maxWithdraw()` inflates the actual amount that can be withdrawn, which can impact badly protocols and contracts integrating with the vault. The possibility is quite real considering that `maxWithdraw()` is part of the official ERC-4626 which is very widely adopted.

## Recommended mitigation steps

Refactor `V3Vault::maxWithdraw()` so that it does not convert `balance` to assets a second time:

```solidity
  function maxWithdraw(address owner) external view override returns (uint256) {
        ....
        if (balance > ownerAssetBalance) {
            return ownerAssetBalance;
        } else {
-            return _convertToAssets(balance, lendExchangeRateX96, Math.Rounding.Down);
+            return balance
        }
    }

```


## Assessed type

Math
