# [?] [TS SDK] Update axios to 1.7.4 due to issue on https://github.com/advisories/GHSA-8hc4-vh64-cxmj (#14381)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-08-22
Source: https://github.com/aptos-labs/aptos-core/commit/7b01b28b889b2508980663a6dab872d6ddbf815d
Type: security-commit

## Details
[TS SDK] Update axios to 1.7.4 due to issue on https://github.com/advisories/GHSA-8hc4-vh64-cxmj (#14381)

Co-authored-by: Sunjin Lee <sunjin@supervlabs.io>
Co-authored-by: Maayan <maayan@aptoslabs.com>

## Patch
### ecosystem/typescript/aptos-client/package.json
```diff
@@ -53,7 +53,7 @@
     "Aptos SDK"
   ],
   "dependencies": {
-    "axios": "1.6.2",
+    "axios": "1.7.4",
     "got": "^11.8.6"
   },
   "devDependencies": {
```
