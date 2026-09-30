# [?] release(cp): fix: bump `fast-xml-parser` to `5.3.6` to fix DoS vulnerability and ignore `ajv` advisory (#40187)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-18
Source: https://github.com/MetaMask/metamask-extension/commit/41460393135eb1eae072bb13560d8107fcad2ab5
Type: security-commit

## Details
release(cp): fix: bump `fast-xml-parser` to `5.3.6` to fix DoS vulnerability and ignore `ajv` advisory (#40187)

## Patch
### .yarnrc.yml
```diff
@@ -37,6 +37,12 @@ npmAuditIgnoreAdvisories:
   # URL: https://github.com/advisories/GHSA-wqch-xfxh-vrr4
   - 1110857
 
+  # Issue: ajv has ReDoS when using `$data` option
+  # A lot of our linting tooling relies on old versions of ajv, which proves hard to deal with
+  # For now, we are ignoring this to unblock CI
+  # URL: https://github.com/advisories/GHSA-2g4f-4pwh-qvx6
+  - 1113214
+
   ### Package Deprecations:
 
   # React-tippy brings in popper.js and react-tippy has not been updated in
```

### package.json
```diff
@@ -249,7 +249,7 @@
     "qs@npm:6.13.0": "^6.14.1",
     "@metamask/bridge-status-controller": "64.3.0",
     "@ledgerhq/hw-transport-webhid@npm:^6.31.0": "patch:@ledgerhq/hw-transport-webhid@npm%3A6.31.0#~/.yarn/patches/@ledgerhq-hw-transport-webhid-npm-6.31.0-efbecf27ab.patch",
-    "fast-xml-parser": "^5.3.4",
+    "fast-xml-parser": "^5.3.6",
     "@metamask/snaps-controllers": "^18.0.0"
   },
   "dependencies": {
```

### yarn.lock
```diff
@@ -26511,14 +26511,14 @@ __metadata:
   languageName: node
   linkType: hard
 
-"fast-xml-parser@npm:^5.3.4":
-  version: 5.3.4
-  resolution: "fast-xml-parser@npm:5.3.4"
+"fast-xml-parser@npm:^5.3.6":
+  version: 5.3.6
+  resolution: "fast-xml-parser@npm:5.3.6"
   dependencies:
-    strnum: "npm:^2.1.0"
+    strnum: "npm:^2.1.2"
   bin:
     fxparser: src/cli/cli.js
-  checksum: 10/0d7e6872fed7c3065641400d43cdf24c03177f05c343bfb31df53b79f0900b085c103f647852d0b00693125aa3f0e9d8b8cfc4273b168d4da0308f857dafe830
+  checksum: 10/03527ab0bdf49d960fdc8f6088cd0715c052e06b68b39459da87b1a1fbb3439a855b2d83cbf3c400e983b8e668b396296b072a4dd5c63403cf1e618c9326b6df
   languageName: node
   linkType: hard
 
@@ -42263,7 +42263,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"strnum@npm:^2.1.0":
+"strnum@npm:^2.1.2":
   version: 2.1.2
   resolution: "strnum@npm:2.1.2"
   checksum: 10/7d894dff385e3a5c5b29c012cf0a7ea7962a92c6a299383c3d6db945ad2b6f3e770511356a9774dbd54444c56af1dc7c435dad6466c47293c48173274dd6c631
```
