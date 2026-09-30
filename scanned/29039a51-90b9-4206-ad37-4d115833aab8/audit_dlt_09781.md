# [?] jit audit fixes: Lacking Reentrancy Checks

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2025-09-01
Source: https://github.com/gmx-io/gmx-synthetics/commit/b3412b6c44a3ed8de266dbb8c77459dc8592eddb
Type: security-commit

## Details
jit audit fixes: Lacking Reentrancy Checks

## Patch
### contracts/exchange/OrderHandler.sol
```diff
@@ -265,6 +265,7 @@ contract OrderHandler is IOrderHandler, BaseOrderHandler {
 
     // @dev used by other handlers to avoid duplicating the same code on their side
     // this method is similar to `executeOrder` but skips execution gas validation
+    // the caller function should be protected by a reentrancy guard
     function executeOrderFromController(
         bytes32 key,
         Order.Props memory order,
```
