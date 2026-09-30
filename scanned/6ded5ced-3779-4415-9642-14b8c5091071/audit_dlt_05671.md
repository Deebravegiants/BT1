# [?] deps: update the `elliptic` to fix a vulnerability  (#8374)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ChainSafe/lodestar
Published: 2025-09-11
Source: https://github.com/ChainSafe/lodestar/commit/8644a83c623c7eda1830d90ec5d67f3aed5aeec3
Type: security-commit

## Details
deps: update the `elliptic` to fix a vulnerability  (#8374)

**Motivation**

Keep the dependencies safe from all vulnerabilities. 

**Description**

- Fix a `critical` level vulnerability. 

https://github.com/advisories/GHSA-fc9h-whq2-v747

It's not critical for our beacon node or validator implementation but
used in `@lodestar/prover` package.

**Steps to test or reproduce**

Run all tests

## Patch
### package.json
```diff
@@ -83,6 +83,7 @@
     "dns-over-http-resolver": "^2.1.1",
     "loupe": "^2.3.6",
     "testcontainers/**/nan": "^2.19.0",
-    "vitest": "3.0.9"
+    "vitest": "3.0.9",
+    "elliptic": ">=6.6.1"
   }
 }
```

### yarn.lock
```diff
@@ -5999,10 +5999,10 @@ electron@^26.2.2:
     "@types/node" "^18.11.18"
     extract-zip "^2.0.1"
 
-elliptic@6.5.4, elliptic@^6.5.3, elliptic@^6.5.4:
-  version "6.5.4"
-  resolved "https://registry.npmjs.org/elliptic/-/elliptic-6.5.4.tgz"
-  integrity sha512-iLhC6ULemrljPZb+QutR5TQGB+pdW6KGD5RSegS+8sorOZT+rdQFbsQFJgvN3eRqNALqJer4oQ16YvJHlU8hzQ==
+elliptic@6.5.4, elliptic@>=6.6.1, elliptic@^6.5.3, elliptic@^6.5.4:
+  version "6.6.1"
+  resolved "https://registry.yarnpkg.com/elliptic/-/elliptic-6.6.1.tgz#3b8ffb02670bf69e382c7f65bf524c97c5405c06"
+  integrity sha512-RaddvvMatK2LJHqFJ+YA4WysVN5Ita9E35botqIYspQ4TkRAlCicdzKOjlyv/1Za5RyTNn7di//eEV0uTAfe3g==
   dependencies:
     bn.js "^4.11.9"
     brorand "^1.1.0"
```
