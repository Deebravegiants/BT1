# [?] Fix overflow math issue

## Summary
Severity: Unknown
Chain: Balancer
Component: balancer/balancer-v3-monorepo
Published: 2023-05-30
Source: https://github.com/balancer/balancer-v3-monorepo/commit/e504fb0fd3fd8ae0b9c447c350e2ae9c4dd01de5
Type: security-commit

## Details
Fix overflow math issue

## Patch
### pkg/solidity-utils/contracts/math/FixedPoint.sol
```diff
@@ -92,11 +92,12 @@ library FixedPoint {
             return mulDown(square, square);
         } else {
             uint256 raw = LogExpMath.pow(x, y);
-            unchecked {
-                uint256 maxError = mulUp(raw, MAX_POW_RELATIVE_ERROR) + 1;
-                if (raw < maxError) {
-                    return 0;
-                } else {
+
+            uint256 maxError = mulUp(raw, MAX_POW_RELATIVE_ERROR) + 1;
+            if (raw < maxError) {
+                return 0;
+            } else {
+                unchecked {
                     return raw - maxError;
                 }
             }
@@ -119,11 +120,9 @@ library FixedPoint {
             return mulUp(square, square);
         } else {
             uint256 raw = LogExpMath.pow(x, y);
-            unchecked {
-                uint256 maxError = mulUp(raw, MAX_POW_RELATIVE_ERROR) + 1;
+            uint256 maxError = mulUp(raw, MAX_POW_RELATIVE_ERROR) + 1;
 
-                return raw + maxError;
-            }
+            return raw + maxError;
         }
     }
 
```
