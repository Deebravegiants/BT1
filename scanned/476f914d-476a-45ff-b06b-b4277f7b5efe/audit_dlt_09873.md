# [?] fix(wallet): stringify json nft metadata to avoid nft details crash (#3675)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2024-11-03
Source: https://github.com/iotaledger/iota/commit/2578ffef14fe7cc5296a0439c7dde26b962b12cd
Type: security-commit

## Details
fix(wallet): stringify json nft metadata to avoid nft details crash (#3675)

## Patch
### apps/wallet/src/ui/app/pages/home/nft-details/index.tsx
```diff
@@ -72,19 +72,26 @@ function NFTDetailsPage() {
         navigate(`/nft-transfer/${nftId}`);
     }
 
-    function formatMetaValue(value: string) {
-        if (value.includes('http')) {
+    function formatMetaValue(value: string | object) {
+        if (typeof value === 'object') {
             return {
-                value: value.startsWith('http')
-                    ? truncateString(value, 20, 8)
-                    : formatAddress(value),
-                valueLink: value,
+                value: JSON.stringify(value),
+                valueLink: undefined,
+            };
+        } else {
+            if (value.includes('http')) {
+                return {
+                    value: value.startsWith('http')
+                        ? truncateString(value, 20, 8)
+                        : formatAddress(value),
+                    valueLink: value,
+                };
+            }
+            return {
+                value: value,
+                valueLink: undefined,
             };
         }
-        return {
-            value: value,
-            valueLink: undefined,
-        };
     }
 
     return (
```
