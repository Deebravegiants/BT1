# [?] fix panic error selector

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2023-01-28
Source: https://github.com/gmx-io/gmx-synthetics/commit/25dfabe6a842c503934b4edd03a183792a047733
Type: security-commit

## Details
fix panic error selector

## Patch
### contracts/utils/RevertUtils.sol
```diff
@@ -16,11 +16,11 @@ library RevertUtils {
             errorSelector := mload(add(result, 0x20))
         }
 
-        // 0x3f0694f5 is the selector for Panic(string)
+        // 0x4e487b71 is the selector for Panic(uint256)
         // 0x08c379a0 is the selector for Error(string)
         // referenced from https://blog.soliditylang.org/2021/04/21/custom-errors/
         if (
-            errorSelector == bytes4(0x3f0694f5) ||
+            errorSelector == bytes4(0x4e487b71) ||
             errorSelector == bytes4(0x08c379a0)
         ) {
             assembly {
```
