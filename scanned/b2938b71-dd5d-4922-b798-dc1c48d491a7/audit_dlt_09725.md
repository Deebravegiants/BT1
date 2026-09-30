# [?] fix possible overflow in initVaultCache

## Summary
Severity: Unknown
Chain: Euler
Component: euler-xyz/euler-vault-kit
Published: 2024-05-13
Source: https://github.com/euler-xyz/euler-vault-kit/commit/5aea1e2483f13c17a6178e8170859fa64c50eda7
Type: security-commit

## Details
fix possible overflow in initVaultCache

## Patch
### src/EVault/shared/Cache.sol
```diff
@@ -75,21 +75,26 @@ contract Cache is Storage, Errors {
             uint256 interestRate = vaultStorage.interestRate;
 
             uint256 newInterestAccumulator = vaultCache.interestAccumulator;
+            uint256 newTotalBorrows = vaultCache.totalBorrows.toUint();
 
             unchecked {
+                uint256 intermediate;
                 (uint256 multiplier, bool overflow) = RPow.rpow(interestRate + 1e27, deltaT, 1e27);
 
                 // if exponentiation or accumulator update overflows, keep the old accumulator
                 if (!overflow) {
-                    uint256 intermediate = newInterestAccumulator * multiplier;
+                    intermediate = newInterestAccumulator * multiplier;
                     if (newInterestAccumulator == intermediate / multiplier) {
                         newInterestAccumulator = intermediate / 1e27;
                     }
                 }
+
+                intermediate = newTotalBorrows * newInterestAccumulator;
+                if (newTotalBorrows == intermediate / newInterestAccumulator) {
+                    newTotalBorrows = intermediate / vaultCache.interestAccumulator;
+                }
             }
 
-            uint256 newTotalBorrows =
-                vaultCache.totalBorrows.toUint() * newInterestAccumulator / vaultCache.interestAccumulator;
             uint256 newAccumulatedFees = vaultCache.accumulatedFees.toUint();
             uint256 newTotalShares = vaultCache.totalShares.toUint();
             uint256 feeAssets = (newTotalBorrows - vaultCache.totalBorrows.toUint()) * interestFee.toUint16()
```
