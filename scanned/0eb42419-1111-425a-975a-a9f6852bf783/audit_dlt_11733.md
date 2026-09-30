# [?] fix overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-07-08
Source: https://github.com/mempool/mempool/commit/c391a532dea60cde836b4669bf00277cde72931e
Type: security-commit

## Details
fix overflow

## Patch
### frontend/src/app/components/blockchain-blocks/blockchain-blocks.component.scss
```diff
@@ -173,6 +173,7 @@
 }
 .show {
   opacity: 1;
+  white-space: nowrap;
 }
 .hide {
   opacity: 0.4;
```
