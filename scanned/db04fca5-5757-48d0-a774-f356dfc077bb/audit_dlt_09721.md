# [?] fix permission vulnerability

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2025-08-19
Source: https://github.com/etherfi-protocol/smart-contracts/commit/02eeb0432f3e4f51c20d973aa4b587280f09aea5
Type: security-commit

## Details
fix permission vulnerability

## Patch
### src/EtherFiNodesManager.sol
```diff
@@ -73,7 +73,7 @@ contract EtherFiNodesManager is
         _unpause();
     }
 
-    function __initRateLimiter() internal {
+    function __initRateLimiter() external onlyAdmin() {
         exitRequestsLimit = BucketLimiter.create(uint64(100), uint64(1));
     }
 
```
