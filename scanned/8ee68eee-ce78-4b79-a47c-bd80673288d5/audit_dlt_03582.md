# [M] M-22 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-26
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/96
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L1183-L1184


# Vulnerability details

## Comments
The underlying yield vaults used by the V5 vaults usually round down shares received when depositing. As a result, if the Vault deposits to an underlying yield vault that has already issued shares, it is possible that a deposit could be rounded down to a lower number of shares. As a result user deposits could fail because the vault will be considered not-collateralised due to the 1 wei difference in expected withdrawable assets from the yield vault.

## Mitigation
The updated implementation now compares the withdrawable assets after a deposit with the expected withdrawal amount based on the size of the deposit and reverts if the former is less than the latter. This ensures that the vault isn't inadvertently becoming undercollateralised during a deposit.

## Mitigation not resolved
The new implementation doesn’t necessarily solve the original issue because it just reverts if the updated withdrawable assets from the underlying yield vault is less than the assets we’ve just deposited; yes it prevents the vault from being undercollateralised, but now deposits could revert if there is a loss of precision of 1 wei in the underlying yield vault. If we wanted to protect against a rounding issue we should add in a 1 wei tolerance to the updated deposit computation. Even though the model OZ implementation rounds up for conversion in one direction and then rounds down for for conversion in the other direction, we cannot guarantee that all underlying yield vaults will do this. Thus we should still have a small wei buffer to account for any rounding issues, otherwise we might inadvertently end up bricking deposits for users in certain conditions where the deposit amount paired with the underlying vault balance leads to a rounding discrepancy.

## Suggestion
In order to prevent a user from deliberately depositing assets that will result in a loss of precision in the underlying yield vault (and therefore lead to undercollateralisation with the first deposit) I'd recommend allowing the V5 vault owner to specify a minimum deposit value that is then enforced in the deposit and mint methods. Any further loss of precision should be guarded against as suggested in the original report. Below is a suggested diff:

```
diff --git a/src/Vault.sol b/src/Vault.sol
index 4da1d00..b784477 100644
--- a/src/Vault.sol
+++ b/src/Vault.sol
@@ -1180,7 +1180,7 @@ contract Vault is IERC4626, ERC20Permit, ILiquidationSource, Ownable {
     uint256 _expectedWithdrawableAssets = _withdrawableAssets + _assets;
     uint256 _withdrawableAssetsAfter = _totalAssets();
 
-    if (_withdrawableAssetsAfter < _expectedWithdrawableAssets)
+    if (_withdrawableAssetsAfter + 1 < _expectedWithdrawableAssets)
       revert YVWithdrawableAssetsLTExpected(_withdrawableAssetsAfter, _expectedWithdrawableAssets);
 
     _mint(_receiver, _assets);
```


## Assessed type


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/96_
