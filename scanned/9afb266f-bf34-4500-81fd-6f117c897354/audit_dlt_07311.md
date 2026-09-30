# [?] fix: build_scripts/npm_linux/package.json & build_scripts/npm_linux/package-lock.json to reduce vulnerabilities (#13286)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2022-09-02
Source: https://github.com/Chia-Network/chia-blockchain/commit/d0a51ea0e8c80baca820aa403a825d52f0b2a2e4
Type: security-commit

## Details
fix: build_scripts/npm_linux/package.json & build_scripts/npm_linux/package-lock.json to reduce vulnerabilities (#13286)

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-JS-GOT-2932019

## Patch
### build_scripts/npm_linux/package.json
```diff
@@ -10,7 +10,7 @@
   "author": "",
   "license": "ISC",
   "dependencies": {
-    "electron-builder": "^23.3.3",
+    "electron-builder": "^23.5.0",
     "lerna": "^5.4.0"
   }
 }
```
