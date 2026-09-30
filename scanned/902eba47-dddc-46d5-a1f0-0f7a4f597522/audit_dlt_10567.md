# [?] release(cp): chore: Upgrade `fast-xml-parser` to `5.3.4` (GHSA-37qj-frw5-hhjh) (#39683)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-01-30
Source: https://github.com/MetaMask/metamask-extension/commit/ce1d80fecf7312fc1b8b5a2b677b4e76dc7a3930
Type: security-commit

## Details
release(cp): chore: Upgrade `fast-xml-parser` to `5.3.4` (GHSA-37qj-frw5-hhjh) (#39683)

## Patch
### lavamoat/browserify/beta/policy.json
```diff
@@ -4274,15 +4274,6 @@
         "setTimeout": true
       }
     },
-    "@metamask/snaps-utils>fast-xml-parser": {
-      "globals": {
-        "entityName": true,
-        "val": true
-      },
-      "packages": {
-        "@metamask/snaps-utils>fast-xml-parser>strnum": true
-      }
-    },
     "@metamask/notification-services-controller>firebase": {
       "packages": {
         "@metamask/notification-services-controller>firebase>@firebase/app": true,
```

### lavamoat/browserify/experimental/policy.json
```diff
@@ -4274,15 +4274,6 @@
         "setTimeout": true
       }
     },
-    "@metamask/snaps-utils>fast-xml-parser": {
-      "globals": {
-        "entityName": true,
-        "val": true
-      },
-      "packages": {
-        "@metamask/snaps-utils>fast-xml-parser>strnum": true
-      }
-    },
     "@metamask/notification-services-controller>firebase": {
       "packages": {
         "@metamask/notification-services-controller>firebase>@firebase/app": true,
```

### lavamoat/browserify/flask/policy.json
```diff
@@ -4274,15 +4274,6 @@
         "setTimeout": true
       }
     },
-    "@metamask/snaps-utils>fast-xml-parser": {
-      "globals": {
-        "entityName": true,
-        "val": true
-      },
-      "packages": {
-        "@metamask/snaps-utils>fast-xml-parser>strnum": true
-      }
-    },
     "@metamask/notification-services-controller>firebase": {
       "packages": {
         "@metamask/notification-services-controller>firebase>@firebase/app": true,
```

### lavamoat/browserify/main/policy.json
```diff
@@ -4274,15 +4274,6 @@
         "setTimeout": true
       }
     },
-    "@metamask/snaps-utils>fast-xml-parser": {
-      "globals": {
-        "entityName": true,
-        "val": true
-      },
-      "packages": {
-        "@metamask/snaps-utils>fast-xml-parser>strnum": true
-      }
-    },
     "@metamask/notification-services-controller>firebase": {
       "packages": {
         "@metamask/notification-services-controller>firebase>@firebase/app": true,
```

### lavamoat/webpack/mv2/beta/policy.json
```diff
@@ -4337,8 +4337,7 @@
     },
     "@metamask/snaps-utils>fast-xml-parser": {
       "globals": {
-        "entityName": true,
-        "val": true
+        "exports.isExist": true
       },
       "packages": {
         "@metamask/snaps-utils>fast-xml-parser>strnum": true
```

### lavamoat/webpack/mv2/experimental/policy.json
```diff
@@ -4337,8 +4337,7 @@
     },
     "@metamask/snaps-utils>fast-xml-parser": {
       "globals": {
-        "entityName": true,
-        "val": true
+        "exports.isExist": true
       },
       "packages": {
         "@metamask/snaps-utils>fast-xml-parser>strnum": true
```

### lavamoat/webpack/mv2/flask/policy.json
```diff
@@ -4337,8 +4337,7 @@
     },
     "@metamask/snaps-utils>fast-xml-parser": {
       "globals": {
-        "entityName": true,
-        "val": true
+        "exports.isExist": true
       },
       "packages": {
         "@metamask/snaps-utils>fast-xml-parser>strnum": true
```

### lavamoat/webpack/mv2/main/policy.json
```diff
@@ -4337,8 +4337,7 @@
     },
     "@metamask/snaps-utils>fast-xml-parser": {
       "globals": {
-        "entityName": true,
-        "val": true
+        "exports.isExist": true
       },
       "packages": {
         "@metamask/snaps-utils>fast-xml-parser>strnum": true
```

### package.json
```diff
@@ -269,7 +269,8 @@
     "which@npm:^1.2.14": "^4.0.0",
     "which@npm:^1.3.1": "^4.0.0",
     "qs@npm:6.13.0": "^6.14.1",
-    "@metamask/bridge-status-controller": "64.3.0"
+    "@metamask/bridge-status-controller": "64.3.0",
+    "fast-xml-parser": "^5.3.4"
   },
   "dependencies": {
     "@babel/runtime": "patch:@babel/runtime@npm%3A7.26.10#~/.yarn/patches/@babel-runtime-npm-7.26.10-fe8c62510a.patch",
```

### yarn.lock
```diff
@@ -26326,14 +26326,14 @@ __metadata:
   languageName: node
   linkType: hard
 
-"fast-xml-parser@npm:^4.4.1":
-  version: 4.4.1
-  resolution: "fast-xml-parser@npm:4.4.1"
+"fast-xml-parser@npm:^5.3.4":
+  version: 5.3.4
+  resolution: "fast-xml-parser@npm:5.3.4"
   dependencies:
-    strnum: "npm:^1.0.5"
+    strnum: "npm:^2.1.0"
   bin:
     fxparser: src/cli/cli.js
-  checksum: 10/0c05ab8703630d8c857fafadbd78d0020d3a8e54310c3842179cd4a0d9d97e96d209ce885e91241f4aa9dd8dfc2fd924a682741a423d65153cad34da2032ec44
+  checksum: 10/0d7e6872fed7c3065641400d43cdf24c03177f05c343bfb31df53b79f0900b085c103f647852d0b00693125aa3f0e9d8b8cfc4273b168d4da0308f857dafe830
   languageName: node
   linkType: hard
 
@@ -42122,10 +42122,10 @@ __metadata:
   languageName: node
   linkType: hard
 
-"strnum@npm:^1.0.5":
-  version: 1.0.5
-  resolution: "strnum@npm:1.0.5"
-  checksum: 10/d3117975db8372d4d7b2c07601ed2f65bf21cc48d741f37a8617b76370d228f2ec26336e53791ebc3638264d23ca54e6c241f57f8c69bd4941c63c79440525ca
+"strnum@npm:^2.1.0":
+  version: 2.1.2
+  resolution: "strnum@npm:2.1.2"
+  checksum: 10/7d894dff385e3a5c5b29c012cf0a7ea7962a92c6a299383c3d6db945ad2b6f3e770511356a9774dbd54444c56af1dc7c435dad6466c47293c48173274dd6c631
   languageName: node
   linkType: hard
 
```
