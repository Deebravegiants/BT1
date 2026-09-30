# [?] fix: winning block link overflows in stale block view

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-08-22
Source: https://github.com/mempool/mempool/commit/8e36be06c0fd5566d064ebad4648db4fda7cb23d
Type: security-commit

## Details
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
