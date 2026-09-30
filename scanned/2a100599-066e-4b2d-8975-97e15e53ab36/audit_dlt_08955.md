# [?] fix: typescript/optics-deploy/package.json & typescript/optics-deploy/package-lock.json to reduce vulnerabilities (#725)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2021-09-06
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/15c7750b391f6461da17b57ea7a90c23d8ef7c15
Type: security-commit

## Details
fix: typescript/optics-deploy/package.json & typescript/optics-deploy/package-lock.json to reduce vulnerabilities (#725)

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-JS-AXIOS-1579269

## Patch
### typescript/optics-deploy/package-lock.json
```diff
@@ -11,7 +11,7 @@
       "dependencies": {
         "@ethersproject/experimental": "^5.3.0",
         "@types/node": "^16.6.1",
-        "axios": "^0.21.1",
+        "axios": "^0.21.3",
         "dotenv": "^10.0.0"
       },
       "devDependencies": {
@@ -769,11 +769,11 @@
       }
     },
     "node_modules/axios": {
-      "version": "0.21.1",
-      "resolved": "https://registry.npmjs.org/axios/-/axios-0.21.1.tgz",
-      "integrity": "sha512-dKQiRHxGD9PPRIUNIWvZhPTPpl1rf/OxTYKsqKUDjBwYylTvV7SjSHJb9ratfyzM6wCdLCOYLzs73qpg5c4iGA==",
+      "version": "0.21.3",
+      "resolved": "https://registry.npmjs.org/axios/-/axios-0.21.3.tgz",
+      "integrity": "sha512-JtoZ3Ndke/+Iwt5n+BgSli/3idTvpt5OjKyoCmz4LX5+lPiY5l7C1colYezhlxThjNa/NhngCUWZSZFypIFuaA==",
       "dependencies": {
-        "follow-redirects": "^1.10.0"
+        "follow-redirects": "^1.14.0"
       }
     },
     "node_modules/balanced-match": {
@@ -1780,11 +1780,11 @@
       }
     },
     "axios": {
-      "version": "0.21.1",
-      "resolved": "https://registry.npmjs.org/axios/-/axios-0.21.1.tgz",
-      "integrity": "sha512-dKQiRHxGD9PPRIUNIWvZhPTPpl1rf/OxTYKsqKUDjBwYylTvV7SjSHJb9ratfyzM6wCdLCOYLzs73qpg5c4iGA==",
+      "version": "0.21.3",
+      "resolved": "https://registry.npmjs.org/axios/-/axios-0.21.3.tgz",
+      "integrity": "sha512-JtoZ3Ndke/+Iwt5n+BgSli/3idTvpt5OjKyoCmz4LX5+lPiY5l7C1colYezhlxThjNa/NhngCUWZSZFypIFuaA==",
       "requires": {
-        "follow-redirects": "^1.10.0"
+        "follow-redirects": "^1.14.0"
       }
     },
     "balanced-match": {
```

### typescript/optics-deploy/package.json
```diff
@@ -21,7 +21,7 @@
   "dependencies": {
     "@ethersproject/experimental": "^5.3.0",
     "@types/node": "^16.6.1",
-    "axios": "^0.21.1",
+    "axios": "^0.21.3",
     "dotenv": "^10.0.0"
   }
 }
```
