# [?] Address remaining issues about CVE-2021-44906 (#13382)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-03-23
Source: https://github.com/digital-asset/daml/commit/50fd93c250fde730e0efbe98199917e6f9c0e0c6
Type: security-commit

## Details
Address remaining issues about CVE-2021-44906 (#13382)

Addresses https://github.com/digital-asset/daml/security/dependabot/28
Addresses https://github.com/digital-asset/daml/security/dependabot/24

changelog_begin
changelog_end

## Patch
### compiler/daml-extension/package.json
```diff
@@ -155,6 +155,7 @@
     },
     "resolutions": {
         "**/markdown-it": "^12.3.2",
-        "**/simple-get": "^4.0.1"
+        "**/simple-get": "^4.0.1",
+        "**/minimist": "^1.2.6"
     }
 }
```

### compiler/daml-extension/yarn.lock
```diff
@@ -579,10 +579,10 @@ minimatch@^3.0.3, minimatch@^3.0.4:
   dependencies:
     brace-expansion "^1.1.7"
 
-minimist@^1.2.0, minimist@^1.2.3:
-  version "1.2.5"
-  resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.5.tgz#67d66014b66a6a8aaa0c083c5fd58df4e4e97602"
-  integrity sha512-FM9nNUYrRBAELZQT3xeZQ7fmMOBg6nWNmJKTcgsJeaLstP/UODVpGsr5OhXhhXg6f+qtJ8uiZ+PUxkDWcgIXLw==
+minimist@^1.2.0, minimist@^1.2.3, minimist@^1.2.6:
+  version "1.2.6"
+  resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.6.tgz#8637a5b759ea0d6e98702cfb3a9283323c93af44"
+  integrity sha512-Jsjnk4bw3YJqYzbdyBiNsPWHPfO++UGG749Cxs6peCu5Xg4nrena6OVxOYxrQTqww0Jmwt+Ref8rggumkTLz9Q==
 
 mkdirp-classic@^0.5.2, mkdirp-classic@^0.5.3:
   version "0.5.3"
```

### language-support/ts/packages/package.json
```diff
@@ -33,6 +33,7 @@
     "**/hosted-git-info": "^4.0.2",
     "**/string-width": "^4.2.3",
     "**/strip-ansi": "^6.0.1",
-    "**/ansi-regex": "^5.0.1"
+    "**/ansi-regex": "^5.0.1",
+    "**/minimist": "^1.2.6"
   }
 }
```

### language-support/ts/packages/yarn.lock
```diff
@@ -2637,10 +2637,10 @@ minimatch@^3.0.4:
   dependencies:
     brace-expansion "^1.1.7"
 
-minimist@^1.2.5:
-  version "1.2.5"
-  resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.5.tgz#67d66014b66a6a8aaa0c083c5fd58df4e4e97602"
-  integrity sha512-FM9nNUYrRBAELZQT3xeZQ7fmMOBg6nWNmJKTcgsJeaLstP/UODVpGsr5OhXhhXg6f+qtJ8uiZ+PUxkDWcgIXLw==
+minimist@^1.2.5, minimist@^1.2.6:
+  version "1.2.6"
+  resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.6.tgz#8637a5b759ea0d6e98702cfb3a9283323c93af44"
+  integrity sha512-Jsjnk4bw3YJqYzbdyBiNsPWHPfO++UGG749Cxs6peCu5Xg4nrena6OVxOYxrQTqww0Jmwt+Ref8rggumkTLz9Q==
 
 ms@2.1.2:
   version "2.1.2"
```
