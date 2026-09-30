# [?] Address CVE-2021-44906 (#13376)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-03-23
Source: https://github.com/digital-asset/daml/commit/9fef07a02ac67c286b3ec6c80e2a12a0fe9d8db5
Type: security-commit

## Details
Address CVE-2021-44906 (#13376)

changelog_begin
changelog_end

## Patch
### navigator/frontend/package.json
```diff
@@ -100,6 +100,7 @@
     "**/set-value": "^4.0.1",
     "**/strip-ansi": "^6.0.0",
     "**/shelljs": "^0.8.5",
+    "**/minimist": "^1.2.6",
     "modernizr/**/markdown-it": "^12.3.2"
   }
 }
```

### navigator/frontend/yarn.lock
```diff
@@ -4907,10 +4907,10 @@ minimatch@~3.0.2:
   dependencies:
     brace-expansion "^1.1.7"
 
-minimist@^1.2.0, minimist@^1.2.5:
-  version "1.2.5"
-  resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.5.tgz#67d66014b66a6a8aaa0c083c5fd58df4e4e97602"
-  integrity sha512-FM9nNUYrRBAELZQT3xeZQ7fmMOBg6nWNmJKTcgsJeaLstP/UODVpGsr5OhXhhXg6f+qtJ8uiZ+PUxkDWcgIXLw==
+minimist@^1.2.0, minimist@^1.2.5, minimist@^1.2.6:
+  version "1.2.6"
+  resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.6.tgz#8637a5b759ea0d6e98702cfb3a9283323c93af44"
+  integrity sha512-Jsjnk4bw3YJqYzbdyBiNsPWHPfO++UGG749Cxs6peCu5Xg4nrena6OVxOYxrQTqww0Jmwt+Ref8rggumkTLz9Q==
 
 minipass@^3.1.1:
   version "3.1.3"
```

### package.json
```diff
@@ -9,7 +9,8 @@
     "**/bl": "^4.0.3",
     "**/ws": "^7.4.6",
     "**/chalk": "^2.4.1",
-    "**/glob-parent": "^5.1.2"
+    "**/glob-parent": "^5.1.2",
+    "**/minimist": "^1.2.6"
   },
   "dependencies": {
     "@mixer/parallel-prettier": "^2.0.1",
```

### yarn.lock
```diff
@@ -2123,10 +2123,10 @@ minimalistic-crypto-utils@^1.0.1:
   dependencies:
     brace-expansion "^1.1.7"
 
-minimist@^1.1.0, minimist@^1.1.1:
-  version "1.2.5"
-  resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.5.tgz#67d66014b66a6a8aaa0c083c5fd58df4e4e97602"
-  integrity sha512-FM9nNUYrRBAELZQT3xeZQ7fmMOBg6nWNmJKTcgsJeaLstP/UODVpGsr5OhXhhXg6f+qtJ8uiZ+PUxkDWcgIXLw==
+minimist@^1.1.0, minimist@^1.1.1, minimist@^1.2.6:
+  version "1.2.6"
+  resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.6.tgz#8637a5b759ea0d6e98702cfb3a9283323c93af44"
+  integrity sha512-Jsjnk4bw3YJqYzbdyBiNsPWHPfO++UGG749Cxs6peCu5Xg4nrena6OVxOYxrQTqww0Jmwt+Ref8rggumkTLz9Q==
 
 mkdirp-classic@^0.5.2:
   version "0.5.3"
```
