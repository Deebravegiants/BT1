# [?] fix: solidity/optics-xapps/package.json & solidity/optics-xapps/package-lock.json to reduce vulnerabilities (#664)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2021-08-30
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/c6ed8da42591cf9de988093131a28c7d2e8b5515
Type: security-commit

## Details
fix: solidity/optics-xapps/package.json & solidity/optics-xapps/package-lock.json to reduce vulnerabilities (#664)

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-JS-OPENZEPPELINCONTRACTS-1570170
- https://snyk.io/vuln/SNYK-JS-OPENZEPPELINCONTRACTSUPGRADEABLE-1570169

## Patch
### solidity/optics-xapps/package-lock.json
```diff
@@ -10,8 +10,8 @@
       "license": "MIT OR Apache-2.0",
       "dependencies": {
         "@celo-org/optics-sol": "file:../optics-core",
-        "@openzeppelin/contracts": "~3.4.0",
-        "@openzeppelin/contracts-upgradeable": "~3.4.0",
+        "@openzeppelin/contracts": "^3.4.2",
+        "@openzeppelin/contracts-upgradeable": "^3.4.2",
         "@summa-tx/memview-sol": "^2.0.0"
       },
       "devDependencies": {
@@ -1625,14 +1625,14 @@
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
@@ -24132,7 +24132,9 @@
           "resolved": "https://registry.npmjs.org/@typechain/ethers-v5/-/ethers-v5-2.0.0.tgz",
           "integrity": "sha512-0xdCkyGOzdqh4h5JSf+zoWx85IusEjDcPIwNEHP8mrWSnCae4rvrqB+/gtpdNfX7zjlFlZiMeePn2r63EI3Lrw==",
           "dev": true,
-          "requires": {}
+          "requires": {
+            "ethers": "^5.0.2"
+          }
         },
         "js-sha3": {
           "version": "0.8.0",
@@ -24788,14 +24790,14 @@
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

### solidity/optics-xapps/package.json
```diff
@@ -40,8 +40,8 @@
   "license": "MIT OR Apache-2.0",
   "dependencies": {
     "@celo-org/optics-sol": "file:../optics-core",
-    "@openzeppelin/contracts": "~3.4.0",
-    "@openzeppelin/contracts-upgradeable": "~3.4.0",
+    "@openzeppelin/contracts": "~3.4.2",
+    "@openzeppelin/contracts-upgradeable": "~3.4.2",
     "@summa-tx/memview-sol": "^2.0.0"
   }
 }
```
