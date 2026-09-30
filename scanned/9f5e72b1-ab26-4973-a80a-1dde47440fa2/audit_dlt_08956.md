# [?] fix: solidity/optics-core/package.json & solidity/optics-core/package-lock.json to reduce vulnerabilities (#666)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2021-08-30
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/9206b2605796c2e569b23e6e7e8c85bd2795ffb5
Type: security-commit

## Details
fix: solidity/optics-core/package.json & solidity/optics-core/package-lock.json to reduce vulnerabilities (#666)

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-JS-OPENZEPPELINCONTRACTS-1570170
- https://snyk.io/vuln/SNYK-JS-OPENZEPPELINCONTRACTSUPGRADEABLE-1570169

## Patch
### solidity/optics-core/package-lock.json
```diff
@@ -9,8 +9,8 @@
       "version": "0.0.0",
       "license": "MIT OR Apache-2.0",
       "dependencies": {
-        "@openzeppelin/contracts": "^3.4.0",
-        "@openzeppelin/contracts-upgradeable": "~3.4.0",
+        "@openzeppelin/contracts": "^3.4.2",
+        "@openzeppelin/contracts-upgradeable": "^3.4.2",
         "@summa-tx/memview-sol": "^2.0.0",
         "dotenv": "^10.0.0",
         "ts-generator": "^0.1.1"
@@ -1276,14 +1276,14 @@
       }
     },
     "node_modules/@openzeppelin/contracts": {
-      "version": "3.4.1",
-      "resolved": "https://registry.npmjs.org/@openzeppelin/contracts/-/contracts-3.4.1.tgz",
-      "integrity": "sha512-cUriqMauq1ylzP2TxePNdPqkwI7Le3Annh4K9rrpvKfSBB/bdW+Iu1ihBaTIABTAAJ85LmKL5SSPPL9ry8d1gQ=="
+      "version": "3.4.2",
+      "resolved": "https://registry.npmjs.org/@openzeppelin/contracts/-/contracts-3.4.2.tgz",
+      "integrity": "sha512-z0zMCjyhhp4y7XKAcDAi3Vgms4T2PstwBdahiO0+9NaGICQKjynK3wduSRplTgk4LXmoO1yfDGO5RbjKYxtuxA=="
     },
     "node_modules/@openzeppelin/contracts-upgradeable": {
-      "version": "3.4.1",
-      "resolved": "https://registry.npmjs.org/@openzeppelin/contracts-upgradeable/-/contracts-upgradeable-3.4.1.tgz",
-      "integrity": "sha512-wBGlUzEkOxcj/ghtcF2yKc8ZYh+PTUtm1mK38zoENulJ6aplij7eH8quo3lMugfzPJy+V6V5qI8QhdQmCn7hkQ=="
+      "version": "3.4.2",
+      "resolved": "https://registry.npmjs.org/@openzeppelin/contracts-upgradeable/-/contracts-upgradeable-3.4.2.tgz",
+      "integrity": "sha512-mDlBS17ymb2wpaLcrqRYdnBAmP1EwqhOXMvqWk2c5Q1N1pm5TkiCtXM9Xzznh4bYsQBq0aIWEkFFE2+iLSN1Tw=="
     },
     "node_modules/@resolver-engine/core": {
       "version": "0.3.3",
@@ -23431,14 +23431,14 @@
       }
     },
     "@openzeppelin/contracts": {
-      "version": "3.4.1",
-      "resolved": "https://registry.npmjs.org/@openzeppelin/contracts/-/contracts-3.4.1.tgz",
-      "integrity": "sha512-cUriqMauq1ylzP2TxePNdPqkwI7Le3Annh4K9rrpvKfSBB/bdW+Iu1ihBaTIABTAAJ85LmKL5SSPPL9ry8d1gQ=="
+      "version": "3.4.2",
+      "resolved": "https://registry.npmjs.org/@openzeppelin/contracts/-/contracts-3.4.2.tgz",
+      "integrity": "sha512-z0zMCjyhhp4y7XKAcDAi3Vgms4T2PstwBdahiO0+9NaGICQKjynK3wduSRplTgk4LXmoO1yfDGO5RbjKYxtuxA=="
     },
     "@openzeppelin/contracts-upgradeable": {
-      "version": "3.4.1",
-      "resolved": "https://registry.npmjs.org/@openzeppelin/contracts-upgradeable/-/contracts-upgradeable-3.4.1.tgz",
-      "integrity": "sha512-wBGlUzEkOxcj/ghtcF2yKc8ZYh+PTUtm1mK38zoENulJ6aplij7eH8quo3lMugfzPJy+V6V5qI8QhdQmCn7hkQ=="
+      "version": "3.4.2",
+      "resolved": "https://registry.npmjs.org/@openzeppelin/contracts-upgradeable/-/contracts-upgradeable-3.4.2.tgz",
+      "integrity": "sha512-mDlBS17ymb2wpaLcrqRYdnBAmP1EwqhOXMvqWk2c5Q1N1pm5TkiCtXM9Xzznh4bYsQBq0aIWEkFFE2+iLSN1Tw=="
     },
     "@resolver-engine/core": {
       "version": "0.3.3",
```

### solidity/optics-core/package.json
```diff
@@ -40,8 +40,8 @@
   "author": "James Prestwich",
   "license": "MIT OR Apache-2.0",
   "dependencies": {
-    "@openzeppelin/contracts": "^3.4.0",
-    "@openzeppelin/contracts-upgradeable": "~3.4.0",
+    "@openzeppelin/contracts": "^3.4.2",
+    "@openzeppelin/contracts-upgradeable": "~3.4.2",
     "@summa-tx/memview-sol": "^2.0.0",
     "dotenv": "^10.0.0",
     "ts-generator": "^0.1.1"
```
