# [?] fix: typescript/optics-tests/package.json & typescript/optics-tests/package-lock.json to reduce vulnerabilities (#805)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2021-09-20
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/3213b53abedf2403ca65f4603ec024ef502c5f75
Type: security-commit

## Details
fix: typescript/optics-tests/package.json & typescript/optics-tests/package-lock.json to reduce vulnerabilities (#805)

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-JS-ETHERS-1586048

## Patch
### typescript/optics-tests/package-lock.json
```diff
@@ -13,8 +13,7 @@
         "@optics-xyz/multi-provider": "^0.0.4",
         "@optics-xyz/ts-interface": "^1.0.9",
         "@types/node": "^15.14.7",
-        "dotenv": "^10.0.0",
-        "ethers": "^5.4.1"
+        "dotenv": "^10.0.0"
       },
       "devDependencies": {
         "@nomiclabs/hardhat-ethers": "^2.0.2",
@@ -24,7 +23,7 @@
         "@types/mocha": "^8.2.2",
         "chai": "^4.3.4",
         "ethereum-waffle": "^3.3.0",
-        "ethers": "^5.4.4",
+        "ethers": "^5.4.7",
         "hardhat": "^2.3.0",
         "mkdirp": "^1.0.4",
         "prettier": "2.3.0",
@@ -670,9 +669,9 @@
       }
     },
     "node_modules/@ethersproject/bignumber": {
-      "version": "5.4.1",
-      "resolved": "https://registry.npmjs.org/@ethersproject/bignumber/-/bignumber-5.4.1.tgz",
-      "integrity": "sha512-fJhdxqoQNuDOk6epfM7yD6J8Pol4NUCy1vkaGAkuujZm0+lNow//MKu1hLhRiYV4BsOHyBv5/lsTjF+7hWwhJg==",
+      "version": "5.4.2",
+      "resolved": "https://registry.npmjs.org/@ethersproject/bignumber/-/bignumber-5.4.2.tgz",
+      "integrity": "sha512-oIBDhsKy5bs7j36JlaTzFgNPaZjiNDOXsdSgSpXRucUl+UA6L/1YLlFeI3cPAoodcenzF4nxNPV13pcy7XbWjA==",
       "funding": [
         {
           "type": "individual",
@@ -2921,9 +2920,9 @@
       "dev": true
     },
     "node_modules/ethers": {
-      "version": "5.4.6",
-      "resolved": "https://registry.npmjs.org/ethers/-/ethers-5.4.6.tgz",
-      "integrity": "sha512-F7LXARyB/Px3AQC6/QKedWZ8eqCkgOLORqL4B/F0Mag/K+qJSFGqsR36EaOZ6fKg3ZonI+pdbhb4A8Knt/43jQ==",
+      "version": "5.4.7",
+      "resolved": "https://registry.npmjs.org/ethers/-/ethers-5.4.7.tgz",
+      "integrity": "sha512-iZc5p2nqfWK1sj8RabwsPM28cr37Bpq7ehTQ5rWExBr2Y09Sn1lDKZOED26n+TsZMye7Y6mIgQ/1cwpSD8XZew==",
       "funding": [
         {
           "type": "individual",
@@ -2941,7 +2940,7 @@
         "@ethersproject/address": "5.4.0",
         "@ethersproject/base64": "5.4.0",
         "@ethersproject/basex": "5.4.0",
-        "@ethersproject/bignumber": "5.4.1",
+        "@ethersproject/bignumber": "5.4.2",
         "@ethersproject/bytes": "5.4.0",
         "@ethersproject/constants": "5.4.0",
         "@ethersproject/contracts": "5.4.1",
@@ -16549,9 +16548,9 @@
       }
     },
     "@ethersproject/bignumber": {
-      "version": "5.4.1",
-      "resolved": "https://registry.npmjs.org/@ethersproject/bignumber/-/bignumber-5.4.1.tgz",
-      "integrity": "sha512-fJhdxqoQNuDOk6epfM7yD6J8Pol4NUCy1vkaGAkuujZm0+lNow//MKu1hLhRiYV4BsOHyBv5/lsTjF+7hWwhJg==",
+      "version": "5.4.2",
+      "resolved": "https://registry.npmjs.org/@ethersproject/bignumber/-/bignumber-5.4.2.tgz",
+      "integrity": "sha512-oIBDhsKy5bs7j36JlaTzFgNPaZjiNDOXsdSgSpXRucUl+UA6L/1YLlFeI3cPAoodcenzF4nxNPV13pcy7XbWjA==",
       "requires": {
         "@ethersproject/bytes": "^5.4.0",
         "@ethersproject/logger": "^5.4.0",
@@ -18294,17 +18293,17 @@
       }
     },
     "ethers": {
-      "version": "5.4.6",
-      "resolved": "https://registry.npmjs.org/ethers/-/ethers-5.4.6.tgz",
-      "integrity": "sha512-F7LXARyB/Px3AQC6/QKedWZ8eqCkgOLORqL4B/F0Mag/K+qJSFGqsR36EaOZ6fKg3ZonI+pdbhb4A8Knt/43jQ==",
+      "version": "5.4.7",
+      "resolved": "https://registry.npmjs.org/ethers/-/ethers-5.4.7.tgz",
+      "integrity": "sha512-iZc5p2nqfWK1sj8RabwsPM28cr37Bpq7ehTQ5rWExBr2Y09Sn1lDKZOED26n+TsZMye7Y6mIgQ/1cwpSD8XZew==",
       "requires": {
         "@ethersproject/abi": "5.4.1",
         "@ethersproject/abstract-provider": "5.4.1",
         "@ethersproject/abstract-signer": "5.4.1",
         "@ethersproject/address": "5.4.0",
         "@ethersproject/base64": "5.4.0",
         "@ethersproject/basex": "5.4.0",
-        "@ethersproject/bignumber": "5.4.1",
+        "@ethersproject/bignumber": "5.4.2",
         "@ethersproject/bytes": "5.4.0",
         "@ethersproject/constants": "5.4.0",
         "@ethersproject/contracts": "5.4.1",
```

### typescript/optics-tests/package.json
```diff
@@ -7,7 +7,7 @@
     "@types/mocha": "^8.2.2",
     "chai": "^4.3.4",
     "ethereum-waffle": "^3.3.0",
-    "ethers": "^5.4.4",
+    "ethers": "^5.4.7",
     "hardhat": "^2.3.0",
     "mkdirp": "^1.0.4",
     "prettier": "2.3.0",
@@ -21,7 +21,7 @@
     "@optics-xyz/ts-interface": "^1.0.9",
     "@types/node": "^15.14.7",
     "dotenv": "^10.0.0",
-    "ethers": "^5.4.1"
+    "ethers": "^5.4.7"
   },
   "name": "@optics-xyz/optics-test",
   "version": "1.0.0",
```
