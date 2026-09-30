# [?] fix: address race condition in parallel noir_js build (#11028)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-02
Source: https://github.com/noir-lang/noir/commit/d08a41c82a2eca4cfd5facb197c851ac808343a1
Type: security-commit

## Details
fix: address race condition in parallel noir_js build (#11028)

## Patch
### tooling/noir_js/tsconfig.json
```diff
@@ -11,10 +11,5 @@
     "noImplicitAny": false,
   },
   "include": ["src/**/*.ts"],
-  "exclude": ["node_modules"],
-  "references": [
-    {
-      "path": "../noir_js_types"
-    },
-  ]
+  "exclude": ["node_modules"]
 }
```
