# [H] Collateral cannot be claimed because there

## Summary
Severity: High
Contest weight: 0.6288
Dataset id: 19813
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Collateral given back to a user due to capped price impacts cannot be claimed because there is no mechanism for the config keeper to set the claimable factor.
The code that claims the collateral for the user only gives back a percentage of the collateral based on a "factor", but there is no function to change the factor from the default of zero.
The user will never be able to claim any of this collateral back, which is a principal loss.
Needing to let users claim their collateral is mainly for when large liquidations cause there to be large impact amounts. While this is not an everyday occurrence, large price gaps and liquidations are a relatively common occurrence in crypto, happening every couple of months, so needing this functionality will be required in the near future. Fixing the issue would require winding down all open positions and requiring LPs to withdraw their collateral, and re-deploying with new code.
```solidity
// File: gmx-synthetics/contracts/market/MarketUtils.sol :
MarketUtils.claimCollateral()
#1
uint256 claimableAmount = dataStore.getUint(Keys.claimableCollateralAmountKey(market, token, timeKey, account));
uint256 claimableFactor = dataStore.getUint(Keys.claimableCollateralFactorKey(market, token, timeKey, account));
uint256 claimedAmount = dataStore.getUint(Keys.claimedCollateralAmountKey(market, token, timeKey, account));
uint256 adjustedClaimableAmount = Precision.applyFactor(claimableAmount, claimableFactor);
if (adjustedClaimableAmount >= claimedAmount) {
    revert CollateralAlreadyClaimed(adjustedClaimableAmount, claimedAmount);
}
cts/market/MarketUtils.sol#L622-L644
```

## Recommendation
```diff
diff --git a/gmx-synthetics/contracts/config/Config.sol b/gmx-synthetics/contracts/config/Config.sol
index 9bb382c..7696eb6 100644
--- a/gmx-synthetics/contracts/config/Config.sol
+++ b/gmx-synthetics/contracts/config/Config.sol
@@ -232,6 +232,8 @@ contract Config is ReentrancyGuard, RoleModule, BasicMulticall {
 allowedBaseKeys[Keys.MIN_COLLATERAL_FACTOR_FOR_OPEN_INTEREST_MULTIPLIER] = true;
 allowedBaseKeys[Keys.MIN_COLLATERAL_USD] = true;
+ allowedBaseKeys[Keys.CLAIMABLE_COLLATERAL_FACTOR] = true;
+ allowedBaseKeys[Keys.VIRTUAL_TOKEN_ID] = true;
 allowedBaseKeys[Keys.VIRTUAL_MARKET_ID] = true;
 allowedBaseKeys[Keys.VIRTUAL_INVENTORY_FOR_SWAPS] = true;
```
