# [?] fix: prevent potential IRM underflow

## Summary
Severity: Unknown
Chain: Euler
Component: euler-xyz/euler-vault-kit
Published: 2024-07-08
Source: https://github.com/euler-xyz/euler-vault-kit/commit/fbb91df449266c2293ea3654b91cdcf2d5e4efb4
Type: security-commit

## Details
fix: prevent potential IRM underflow

## Patch
### src/InterestRateModels/IRMLinearKink.sol
```diff
@@ -19,7 +19,7 @@ contract IRMLinearKink is IIRM {
     /// @notice Utilization at which the slope of the interest rate function changes. In type(uint32).max scale.
     uint256 public immutable kink;
 
-    constructor(uint256 baseRate_, uint256 slope1_, uint256 slope2_, uint256 kink_) {
+    constructor(uint256 baseRate_, uint256 slope1_, uint256 slope2_, uint32 kink_) {
         baseRate = baseRate_;
         slope1 = slope1_;
         slope2 = slope2_;
```
