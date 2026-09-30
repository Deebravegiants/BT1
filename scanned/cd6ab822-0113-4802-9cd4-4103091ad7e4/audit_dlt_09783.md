# [?] Update to simplify FeeDistributor logic and also avoid potential underflow when wntForReferralRewards is greater than maxKeeperAndReferralCostsGlp

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2025-07-10
Source: https://github.com/gmx-io/gmx-synthetics/commit/f96a01ba0178ae69c95d54b272b23b410eb8b54c
Type: security-commit

## Details
Update to simplify FeeDistributor logic and also avoid potential underflow when wntForReferralRewards is greater than maxKeeperAndReferralCostsGlp

## Patch
### contracts/fee/FeeDistributor.sol
```diff
@@ -548,12 +548,13 @@ contract FeeDistributor is ReentrancyGuard, RoleModule, OracleModule {
             wntForChainlink -
             wntForTreasury;
 
+        uint256 keeperAndReferralCostsGlp = keeperCostsGlp + wntForReferralRewards;
         uint256 maxKeeperAndReferralCostsGlp = Precision.applyFactor(
             glpWntBeforeV1KeeperAndReferralCosts,
             getUint(Keys.FEE_DISTRIBUTOR_MAX_GLP_KEEPER_REFERRAL_COSTS_FACTOR)
         );
-        if ((keeperCostsGlp + wntForReferralRewards) > maxKeeperAndReferralCostsGlp) {
-            uint256 additionalWntForGlp = (keeperCostsGlp + wntForReferralRewards) - maxKeeperAndReferralCostsGlp;
+        if (keeperAndReferralCostsGlp > maxKeeperAndReferralCostsGlp) {
+            uint256 additionalWntForGlp = keeperAndReferralCostsGlp - maxKeeperAndReferralCostsGlp;
             if (additionalWntForGlp > wntForTreasury) {
                 uint256 maxWntFromTreasury = getUint(Keys.FEE_DISTRIBUTOR_MAX_WNT_AMOUNT_FROM_TREASURY);
                 uint256 additionalWntFromTreasury = additionalWntForGlp - wntForTreasury;
@@ -569,9 +570,9 @@ contract FeeDistributor is ReentrancyGuard, RoleModule, OracleModule {
             } else {
                 wntForTreasury -= additionalWntForGlp;
             }
-            keeperCostsGlp = maxKeeperAndReferralCostsGlp - wntForReferralRewards;
+            keeperAndReferralCostsGlp = maxKeeperAndReferralCostsGlp;
         }
-        uint256 wntForGlp = glpWntBeforeV1KeeperAndReferralCosts - keeperCostsGlp - wntForReferralRewards;
+        uint256 wntForGlp = glpWntBeforeV1KeeperAndReferralCosts - keeperAndReferralCostsGlp;
 
         return (wntForTreasury, wntForGlp);
     }
```

### contracts/mock/MockFeeDistributor.sol
```diff
@@ -553,12 +553,13 @@ contract MockFeeDistributor is ReentrancyGuard, RoleModule, OracleModule {
             wntForChainlink -
             wntForTreasury;
 
+        uint256 keeperAndReferralCostsGlp = keeperCostsGlp + wntForReferralRewards;
         uint256 maxKeeperAndReferralCostsGlp = Precision.applyFactor(
             glpWntBeforeV1KeeperAndReferralCosts,
             getUint(Keys.FEE_DISTRIBUTOR_MAX_GLP_KEEPER_REFERRAL_COSTS_FACTOR)
         );
-        if ((keeperCostsGlp + wntForReferralRewards) > maxKeeperAndReferralCostsGlp) {
-            uint256 additionalWntForGlp = (keeperCostsGlp + wntForReferralRewards) - maxKeeperAndReferralCostsGlp;
+        if (keeperAndReferralCostsGlp > maxKeeperAndReferralCostsGlp) {
+            uint256 additionalWntForGlp = keeperAndReferralCostsGlp - maxKeeperAndReferralCostsGlp;
             if (additionalWntForGlp > wntForTreasury) {
                 uint256 maxWntFromTreasury = getUint(Keys.FEE_DISTRIBUTOR_MAX_WNT_AMOUNT_FROM_TREASURY);
                 uint256 additionalWntFromTreasury = additionalWntForGlp - wntForTreasury;
@@ -574,9 +575,9 @@ contract MockFeeDistributor is ReentrancyGuard, RoleModule, OracleModule {
             } else {
                 wntForTreasury -= additionalWntForGlp;
             }
-            keeperCostsGlp = maxKeeperAndReferralCostsGlp - wntForReferralRewards;
+            keeperAndReferralCostsGlp = maxKeeperAndReferralCostsGlp;
         }
-        uint256 wntForGlp = glpWntBeforeV1KeeperAndReferralCosts - keeperCostsGlp - wntForReferralRewards;
+        uint256 wntForGlp = glpWntBeforeV1KeeperAndReferralCosts - keeperAndReferralCostsGlp;
 
         return (wntForTreasury, wntForGlp);
     }
```
