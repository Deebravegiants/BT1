# [?] prevent overflow

## Summary
Severity: Unknown
Chain: Morph
Component: morph-l2/morph
Published: 2024-11-12
Source: https://github.com/morph-l2/morph/commit/177ec308fd526f953791d520c5b3f6366ddf2367
Type: security-commit

## Details
prevent overflow

## Patch
### contracts/contracts/l1/staking/L1Staking.sol
```diff
@@ -222,6 +222,9 @@ contract L1Staking is IL1Staking, Staking, OwnableUpgradeable, ReentrancyGuardUp
 
         uint256 valueSum;
         for (uint256 i = 0; i < sequencers.length; i++) {
+            if (sequencers[i] == address(0)) {
+                continue;
+            }
             if (withdrawals[sequencers[i]] > 0) {
                 delete withdrawals[sequencers[i]];
                 valueSum += stakingValue;
```
