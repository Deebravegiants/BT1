# [?] release(cp): fix: tar audit vulnerability by forcing patched version (#39349)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-01-19
Source: https://github.com/MetaMask/metamask-extension/commit/352bca22883ac7d71c4faf4a3ae3bdad22454daa
Type: security-commit

## Details
release(cp): fix: tar audit vulnerability by forcing patched version (#39349)

## Patch
### .github/scripts/check-template-and-add-labels.ts
```diff
@@ -33,6 +33,7 @@ const knownBots = [
   'sentry-io',
   'devin-ai-integration',
   'runway-github',
+  'copilot',
 ];
 
 main().catch((error: Error): void => {
```

### .github/workflows/cla.yml
```diff
@@ -27,6 +27,6 @@ jobs:
           url-to-cladocument: 'https://metamask.io/cla'
           # This branch can't have protections, commits are made directly to the specified branch.
           branch: 'cla-signatures'
-          allowlist: 'dependabot[bot],metamaskbot,@metamaskbotv2[bot],crowdin-bot,runway-github[bot],cursor'
+          allowlist: 'dependabot[bot],metamaskbot,@metamaskbotv2[bot],crowdin-bot,runway-github[bot],cursor,copilot[bot]'
           allow-organization-members: true
           blockchain-storage-flag: false
```

### package.json
```diff
@@ -190,6 +190,7 @@
     "undeclared-identifiers@^1.1.2": "patch:undeclared-identifiers@npm%3A1.1.2#./.yarn/patches/undeclared-identifiers-npm-1.1.2-13d6792e9e.patch",
     "stylelint@^13.6.1": "patch:stylelint@npm%3A13.6.1#./.yarn/patches/stylelint-npm-13.6.1-47aaddf62b.patch",
     "symbol-observable": "^2.0.3",
+    "tar": "^7.5.3",
     "async-done@~1.3.2": "patch:async-done@npm%3A1.3.2#./.yarn/patches/async-done-npm-1.3.2-1f0a4a8997.patch",
     "async-done@^1.2.0": "patch:async-done@npm%3A1.3.2#./.yarn/patches/async-done-npm-1.3.2-1f0a4a8997.patch",
     "async-done@^1.2.2": "patch:async-done@npm%3A1.3.2#./.yarn/patches/async-done-npm-1.3.2-1f0a4a8997.patch",
```

### yarn.lock
```diff
@@ -21237,13 +21237,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"chownr@npm:^2.0.0":
-  version: 2.0.0
-  resolution: "chownr@npm:2.0.0"
-  checksum: 10/c57cf9dd0791e2f18a5ee9c1a299ae6e801ff58fee96dc8bfd0dcb4738a6ce58dd252a3605b1c93c6418fe4f9d5093b28ffbf4d66648cb2a9c67eaef9679be2f
-  languageName: node
-  linkType: hard
-
 "chownr@npm:^3.0.0":
   version: 3.0.0
   resolution: "chownr@npm:3.0.0"
@@ -27015,15 +27008,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"fs-minipass@npm:^2.0.0":
-  version: 2.1.0
-  resolution: "fs-minipass@npm:2.1.0"
-  dependencies:
-    minipass: "npm:^3.0.0"
-  checksum: 10/03191781e94bc9a54bd376d3146f90fe8e082627c502185dbf7b9b3032f66b0b142c1115f3b2cc5936575fc1b44845ce903dd4c21bec2a8d69f3bd56f9cee9ec
-  languageName: node
-  linkType: hard
-
 "fs-minipass@npm:^3.0.0":
   version: 3.0.2
   resolution: "fs-minipass@npm:3.0.2"
@@ -27554,7 +27538,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"glob@npm:^10.0.0, glob@npm:^10.2.2, glob@npm:^10.3.10, glob@npm:^10.3.7, glob@npm:^10.5.0":
+"glob@npm:^10.0.0, glob@npm:^10.2.2, glob@npm:^10.3.10, glob@npm:^10.5.0":
   version: 10.5.0
   resolution: "glob@npm:10.5.0"
   dependencies:
@@ -34271,7 +34255,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"minizlib@npm:^2.1.1, minizlib@npm:^2.1.2":
+"minizlib@npm:^2.1.2":
   version: 2.1.2
   resolution: "minizlib@npm:2.1.2"
   dependencies:
@@ -34281,13 +34265,12 @@ __metadata:
   languageName: node
   linkType: hard
 
-"minizlib@npm:^3.0.1":
-  version: 3.0.1
-  resolution: "minizlib@npm:3.0.1"
+"minizlib@npm:^3.1.0":
+  version: 3.1.0
+  resolution: "minizlib@npm:3.1.0"
   dependencies:
-    minipass: "npm:^7.0.4"
-    rimraf: "npm:^5.0.5"
-  checksum: 10/622cb85f51e5c206a080a62d20db0d7b4066f308cb6ce82a9644da112367c3416ae7062017e631eb7ac8588191cfa4a9a279b8651c399265202b298e98c4acef
+    minipass: "npm:^7.1.2"
+  checksum: 10/f47365cc2cb7f078cbe7e046eb52655e2e7e97f8c0a9a674f4da60d94fb0624edfcec9b5db32e8ba5a99a5f036f595680ae6fe02a262beaa73026e505cc52f99
   languageName: node
   linkType: hard
 
@@ -34336,7 +34319,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"mkdirp@npm:^1.0.3, mkdirp@npm:^1.0.4":
+"mkdirp@npm:^1.0.4":
   version: 1.0.4
   resolution: "mkdirp@npm:1.0.4"
   bin:
@@ -34345,7 +34328,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"mkdirp@npm:^3.0.0, mkdirp@npm:^3.0.1":
+"mkdirp@npm:^3.0.0":
   version: 3.0.1
   resolution: "mkdirp@npm:3.0.1"
   bin:
@@ -39681,17 +39664,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"rimraf@npm:^5.0.5":
-  version: 5.0.5
-  resolution: "rimraf@npm:5.0.5"
-  dependencies:
-    glob: "npm:^10.3.7"
-  bin:
-    rimraf: dist/esm/bin.mjs
-  checksum: 10/a612c7184f96258b7d1328c486b12ca7b60aa30e04229a08bbfa7e964486deb1e9a1b52d917809311bdc39a808a4055c0f950c0280fba194ba0a09e6f0d404f6
-  languageName: node
-  linkType: hard
-
 "ripemd160@npm:=2.0.1":
   version: 2.0.1
   resolution: "ripemd160@npm:2.0.1"
@@ -42516,31 +42488,16 @@ __metadata:
   languageName: node
   linkType: hard
 
-"tar@npm:^6.1.11, tar@npm:^6.1.13, tar@npm:^6.1.2":
-  version: 6.2.1
-  resolution: "tar@npm:6.2.1"
-  dependencies:
-    chownr: "npm:^2.0.0"
-    fs-minipass: "npm:^2.0.0"
-    minipass: "npm:^5.0.0"
-    minizlib: "npm:^2.1.1"
-    mkdirp: "npm:^1.0.3"
-    yallist: "npm:^4.0.0"
-  checksum: 10/bfbfbb2861888077fc1130b84029cdc2721efb93d1d1fb80f22a7ac3a98ec6f8972f29e564103bbebf5e97be67ebc356d37fa48dbc4960600a1eb7230fbd1ea0
-  languageName: node
-  linkType: hard
-
-"tar@npm:^7.4.3":
-  version: 7.4.3
-  resolution: "tar@npm:7.4.3"
+"tar@npm:^7.5.3":
+  version: 7.5.3
+  resolution: "tar@npm:7.5.3"
   dependencies:
     "@isaacs/fs-minipass": "npm:^4.0.0"
     chownr: "npm:^3.0.0"
     minipass: "npm:^7.1.2"
-    minizlib: "npm:^3.0.1"
-    mkdirp: "npm:^3.0.1"
+    minizlib: "npm:^3.1.0"
     yallist: "npm:^5.0.0"
-  checksum: 10/12a2a4fc6dee23e07cc47f1aeb3a14a1afd3f16397e1350036a8f4cdfee8dcac7ef5978337a4e7b2ac2c27a9a6d46388fc2088ea7c80cb6878c814b1425f8ecf
+  checksum: 10/106b85ef799eb9c2a5d91278b14cdd9486551a5d889a7d88f719513dd7e04b7bd77417df27d3fcb43ef54dda5acc15730e627259164ce245dd968d86fd6ee517
   languageName: node
   linkType: hard
 
```
