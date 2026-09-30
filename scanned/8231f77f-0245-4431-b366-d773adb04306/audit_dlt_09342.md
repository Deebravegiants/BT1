# [?] chore: bump fast-uri to fix audit vulnerabilities

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-05-11
Source: https://github.com/wevm/viem/commit/87c43b3fea78999f667d458ede7bd824a729f476
Type: security-commit

## Details
chore: bump fast-uri to fix audit vulnerabilities

Amp-Thread-ID: https://ampcode.com/threads/T-019e15fc-8215-72c8-a742-13bfe06456d4

## Patch
### package.json
```diff
@@ -304,7 +304,8 @@
       "@vitejs/plugin-rsc@<=0.5.22": "0.5.23",
       "next@>=16.0.0-beta.0 <16.2.3": "16.2.3",
       "react-server-dom-webpack@>=19.2.0 <19.2.5": "19.2.5",
-      "basic-ftp@<=5.3.0": "5.3.1"
+      "basic-ftp@<=5.3.0": "5.3.1",
+      "fast-uri@<=3.1.1": "3.1.2"
     },
     "onlyBuiltDependencies": [
       "bun",
```

### pnpm-lock.yaml
```diff
@@ -83,6 +83,7 @@ overrides:
   next@>=16.0.0-beta.0 <16.2.3: 16.2.3
   react-server-dom-webpack@>=19.2.0 <19.2.5: 19.2.5
   basic-ftp@<=5.3.0: 5.3.1
+  fast-uri@<=3.1.1: 3.1.2
 
 importers:
 
@@ -3856,8 +3857,8 @@ packages:
   fast-safe-stringify@2.1.1:
     resolution: {integrity: sha512-W+KJc2dmILlPplD/H4K9l9LcAHAfPtP6BY84uVLXQ6Evcz9Lcg33Y2z1IVblT6xdY54PXYVHEv+0Wpq8Io6zkA==}
 
-  fast-uri@3.0.3:
-    resolution: {integrity: sha512-aLrHthzCjH5He4Z2H9YZ+v6Ujb9ocRuW6ZzkJQOrTxleEijANq4v1TsaPaVG1PZcuurEzrLcWRyYBYXD5cEiaw==}
+  fast-uri@3.1.2:
+    resolution: {integrity: sha512-rVjf7ArG3LTk+FS6Yw81V1DLuZl1bRbNrev6Tmd/9RaroeeRRJhAt7jg/6YFxbvAQXUCavSoZhPPj6oOx+5KjQ==}
 
   fastify-plugin@4.5.1:
     resolution: {integrity: sha512-stRHYGeuqpEZTL1Ef0Ovr2ltazUT9g844X5z/zEBFLG8RYlpDiOCIG+ATvYEp+/zmc7sN29mcIMp8gvYplYPIQ==}
@@ -6152,6 +6153,14 @@ packages:
   vfile@6.0.3:
     resolution: {integrity: sha512-KzIbH/9tXat2u30jf+smMwFCsno4wHVdNmzFyL+T/L3UGqqk6JKfVqOFOZEpZSHADH1k40ab6NUIXZq422ov3Q==}
 
+  viem@2.48.11:
+    resolution: {integrity: sha512-+WZ5E0dBS6GtKb+1wEk5DeYRRRW42+pFnXCo67Ydodf42sBwO+hu3wnQy66lc4MKmHz+llPVdbyehYr9oTE2iw==}
+    peerDependencies:
+      typescript: ^5.9.3
+    peerDependenciesMeta:
+      typescript:
+        optional: true
+
   viem@2.48.8:
     resolution: {integrity: sha512-Xj3Nrt66SKtn06kczU91ELn9Difr84ZM5A62BTlaisT5lpgt058i2mBkfMZCXHGb1ocOLjzC2ztPhD0Lvky7uQ==}
     peerDependencies:
@@ -7188,7 +7197,7 @@ snapshots:
     dependencies:
       ajv: 8.18.0
       ajv-formats: 3.0.1
-      fast-uri: 3.0.3
+      fast-uri: 3.1.2
 
   '@fastify/error@4.2.0': {}
 
@@ -7998,7 +8007,7 @@ snapshots:
       pino-pretty: 10.3.1
       prom-client: 14.2.0
       type-fest: 4.39.0
-      viem: 2.48.8(typescript@5.9.3)(zod@3.25.76)
+      viem: 2.48.11(typescript@5.9.3)(zod@3.25.76)
       yargs: 17.7.2
       zod: 3.25.76
       zod-validation-error: 1.5.0(zod@3.25.76)
@@ -8965,7 +8974,7 @@ snapshots:
   ajv@8.18.0:
     dependencies:
       fast-deep-equal: 3.1.3
-      fast-uri: 3.0.3
+      fast-uri: 3.1.2
       json-schema-traverse: 1.0.0
       require-from-string: 2.0.2
 
@@ -9862,7 +9871,7 @@ snapshots:
       '@fastify/merge-json-schemas': 0.2.1
       ajv: 8.18.0
       ajv-formats: 3.0.1
-      fast-uri: 3.0.3
+      fast-uri: 3.1.2
       json-schema-ref-resolver: 3.0.0
       rfdc: 1.4.1
 
@@ -9874,7 +9883,7 @@ snapshots:
 
   fast-safe-stringify@2.1.1: {}
 
-  fast-uri@3.0.3: {}
+  fast-uri@3.1.2: {}
 
   fastify-plugin@4.5.1: {}
 
@@ -12698,7 +12707,7 @@ snapshots:
       '@types/unist': 3.0.3
       vfile-message: 4.0.2
 
-  viem@2.48.8(typescript@5.9.3)(zod@3.25.76):
+  viem@2.48.11(typescript@5.9.3)(zod@3.25.76):
     dependencies:
       '@noble/curves': 1.9.1
       '@noble/hashes': 1.8.0
```
