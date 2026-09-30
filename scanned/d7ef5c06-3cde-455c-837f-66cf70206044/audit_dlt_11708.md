# [?] Prevent horizontal page overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-07-25
Source: https://github.com/mempool/mempool/commit/bd88584857efdffa1bc21a587af21d141598675b
Type: security-commit

## Details
Prevent horizontal page overflow

## Patch
### frontend/src/styles.scss
```diff
@@ -1601,7 +1601,7 @@ a.badge:hover, a.badge:focus {
   }
 }
 
-.row {
+.container-fluid, .row {
   --bs-gutter-x: 30px;
 }
 
```
