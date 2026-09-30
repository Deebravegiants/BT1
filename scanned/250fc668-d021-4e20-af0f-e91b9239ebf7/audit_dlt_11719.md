# [?] Fix tx-list highlight overflow on small screens

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2025-09-09
Source: https://github.com/mempool/mempool/commit/1af6fefb7d79997a2a4a10fb321c857b5ff349e0
Type: security-commit

## Details
Fix tx-list highlight overflow on small screens

## Patch
### frontend/src/app/components/transactions-list/transactions-list.component.scss
```diff
@@ -1,12 +1,18 @@
 .col {
 	&:first-child {
 		padding-right: 0;
+		@media (max-width: 992px) {
+			padding-right: 15px;
+		}
 		td:last-child {
 			padding-right: calc(0.3em + 15px);
 		}
 	}
 	&:last-child {
 		padding-left: 0;
+		@media (max-width: 992px) {
+			padding-left: 15px;
+		}
 		td:first-child {
 			padding-left: calc(0.3em + 15px);
 		}
```
