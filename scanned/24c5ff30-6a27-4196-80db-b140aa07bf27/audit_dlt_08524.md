# [?] Fix PrismJS DOM Clobbering Vulnerability (#6938)

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2025-03-11
Source: https://github.com/IntersectMBO/plutus/commit/a9a678965d56a10899afbffc4402d81c55f3b64a
Type: security-commit

## Details
Fix PrismJS DOM Clobbering Vulnerability (#6938)

## Patch
### doc/docusaurus/package.json
```diff
@@ -35,7 +35,8 @@
     "nanoid": "3.3.8",
     "path-to-regexp": "3.3.0",
     "katex": "0.16.21",
-    "dompurify": "3.2.4"
+    "dompurify": "3.2.4",
+    "prismjs": "1.30.0"
   },
   "browserslist": {
     "production": [
```

### doc/docusaurus/yarn.lock
```diff
@@ -7632,10 +7632,10 @@ prism-react-renderer@^2.3.0:
     "@types/prismjs" "^1.26.0"
     clsx "^2.0.0"
 
-prismjs@^1.29.0:
-  version "1.29.0"
-  resolved "https://registry.yarnpkg.com/prismjs/-/prismjs-1.29.0.tgz#f113555a8fa9b57c35e637bba27509dcf802dd12"
-  integrity sha512-Kx/1w86q/epKcmte75LNrEoT+lX8pBpavuAbvJWRXar7Hz8jrtF+e3vY751p0R8H9HdArwaCTNDDzHg/ScJK1Q==
+prismjs@1.30.0, prismjs@^1.29.0:
+  version "1.30.0"
+  resolved "https://registry.yarnpkg.com/prismjs/-/prismjs-1.30.0.tgz#d9709969d9d4e16403f6f348c63553b19f0975a9"
+  integrity sha512-DEvV2ZF2r2/63V+tK8hQvrR2ZGn10srHbXviTlcv7Kpzw8jWiNTqbVgjO3IY8RxrrOUF8VPMQQFysYYYv0YZxw==
 
 process-nextick-args@~2.0.0:
   version "2.0.1"
```
