# [?] Merge pull request #5464 from WalletConnect/renovate/npm-elliptic-vulnerability

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2024-10-30
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/aba5a4bcdc04f0815c4ab196b22050f19540e84d
Type: security-commit

## Details
Merge pull request #5464 from WalletConnect/renovate/npm-elliptic-vulnerability

fix(deps): update dependency elliptic to v6.6.0 [security]

## Patch
### package-lock.json
```diff
@@ -10975,9 +10975,9 @@
       "peer": true
     },
     "node_modules/elliptic": {
-      "version": "6.5.7",
-      "resolved": "https://registry.npmjs.org/elliptic/-/elliptic-6.5.7.tgz",
-      "integrity": "sha512-ESVCtTwiA+XhY3wyh24QqRGBoP3rEdDUl3EDUUo9tft074fi19IrdpH7hLCMMP3CIj7jb3W96rn8lt/BqIlt5Q==",
+      "version": "6.6.0",
+      "resolved": "https://registry.npmjs.org/elliptic/-/elliptic-6.6.0.tgz",
+      "integrity": "sha512-dpwoQcLc/2WLQvJvLRHKZ+f9FgOdjnq11rurqwekGQygGPsYSK29OMMD2WalatiqQ+XGFDglTNixpPfI+lpaAA==",
       "dependencies": {
         "bn.js": "^4.11.9",
         "brorand": "^1.1.0",
@@ -27631,7 +27631,7 @@
         "@walletconnect/window-getters": "1.0.1",
         "@walletconnect/window-metadata": "1.0.1",
         "detect-browser": "5.3.0",
-        "elliptic": "6.5.7",
+        "elliptic": "6.6.0",
         "query-string": "7.1.3",
         "uint8arrays": "3.1.0"
       },
@@ -34245,7 +34245,7 @@
         "@walletconnect/window-getters": "1.0.1",
         "@walletconnect/window-metadata": "1.0.1",
         "detect-browser": "5.3.0",
-        "elliptic": "6.5.7",
+        "elliptic": "6.6.0",
         "query-string": "7.1.3",
         "uint8arrays": "3.1.0"
       },
@@ -36372,9 +36372,9 @@
       "peer": true
     },
     "elliptic": {
-      "version": "6.5.7",
-      "resolved": "https://registry.npmjs.org/elliptic/-/elliptic-6.5.7.tgz",
-      "integrity": "sha512-ESVCtTwiA+XhY3wyh24QqRGBoP3rEdDUl3EDUUo9tft074fi19IrdpH7hLCMMP3CIj7jb3W96rn8lt/BqIlt5Q==",
+      "version": "6.6.0",
+      "resolved": "https://registry.npmjs.org/elliptic/-/elliptic-6.6.0.tgz",
+      "integrity": "sha512-dpwoQcLc/2WLQvJvLRHKZ+f9FgOdjnq11rurqwekGQygGPsYSK29OMMD2WalatiqQ+XGFDglTNixpPfI+lpaAA==",
       "requires": {
         "bn.js": "^4.11.9",
         "brorand": "^1.1.0",
```

### packages/utils/package.json
```diff
@@ -48,7 +48,7 @@
     "@walletconnect/window-getters": "1.0.1",
     "@walletconnect/window-metadata": "1.0.1",
     "detect-browser": "5.3.0",
-    "elliptic": "6.5.7",
+    "elliptic": "6.6.0",
     "query-string": "7.1.3",
     "uint8arrays": "3.1.0"
   },
```
