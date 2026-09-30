# [?] Merge pull request #6708 from mempool/rodribp/fix-overflow-wblockhash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-08-24
Source: https://github.com/mempool/mempool/commit/e20c6dc6041a74c7087e52e5c3fc0c27e602f42f
Type: security-commit

## Details
Merge pull request #6708 from mempool/rodribp/fix-overflow-wblockhash

fix: winning block link overflows in stale block view

## Patch
### frontend/src/app/components/block/block.component.scss
```diff
@@ -13,6 +13,10 @@
   .alert-mempool {
     flex-direction: row;
     flex-wrap: wrap;
+
+    app-truncate {
+      min-width: 0;
+    }
   }
 
   .container-button {
```
