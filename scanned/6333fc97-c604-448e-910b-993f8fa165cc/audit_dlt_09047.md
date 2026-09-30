# [?] release(cp): chore(security): Set yarn resolution for `qs` to patch vulnerability (#39015)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-01-05
Source: https://github.com/MetaMask/metamask-extension/commit/a2fb2d58da7db3dae464d6d29940c0cd5a241581
Type: security-commit

## Details
release(cp): chore(security): Set yarn resolution for `qs` to patch vulnerability (#39015)

## Patch
### lavamoat/browserify/beta/policy.json
```diff
@@ -4636,7 +4636,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5591,7 +5591,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/browserify/experimental/policy.json
```diff
@@ -4636,7 +4636,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5591,7 +5591,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/browserify/flask/policy.json
```diff
@@ -4636,7 +4636,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5591,7 +5591,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/browserify/main/policy.json
```diff
@@ -4636,7 +4636,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5591,7 +5591,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/build-system/policy.json
```diff
@@ -5711,7 +5711,7 @@
         "gulp>vinyl-fs>pumpify>pump": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -8218,7 +8218,7 @@
         "gulp-livereload>tiny-lr>debug": true,
         "gulp-livereload>tiny-lr>faye-websocket": true,
         "react>object-assign": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "gulp>vinyl-fs>glob-stream>to-absolute-glob": {
```

### lavamoat/webpack/mv2/policy.json
```diff
@@ -4857,7 +4857,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -5951,7 +5951,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### lavamoat/webpack/mv3/policy.json
```diff
@@ -3284,7 +3284,7 @@
         "react": true
       }
     },
-    "browserify>url>qs": {
+    "mockttp>express>qs": {
       "packages": {
         "string.prototype.matchall>side-channel": true
       }
@@ -4251,7 +4251,7 @@
     "browserify>url": {
       "packages": {
         "browserify>url>punycode": true,
-        "browserify>url>qs": true
+        "mockttp>express>qs": true
       }
     },
     "react-focus-lock>use-callback-ref": {
```

### package.json
```diff
@@ -251,7 +251,8 @@
     "@metamask/bridge-controller@npm:^63.2.0": "patch:@metamask/bridge-controller@npm%3A64.0.0#~/.yarn/patches/@metamask-bridge-controller-npm-64.0.0-956740f7c8.patch",
     "@metamask/assets-controllers@npm:^92.0.0": "patch:@metamask/assets-controllers@patch%3A@metamask/assets-controllers@npm%253A93.0.0%23~/.yarn/patches/@metamask-assets-controllers-npm-93.0.0-ea998cb0bd.patch%3A%3Aversion=93.0.0&hash=224a2c#~/.yarn/patches/@metamask-assets-controllers-patch-0229f60576.patch",
     "@metamask/assets-controllers@npm:^93.0.0": "patch:@metamask/assets-controllers@patch%3A@metamask/assets-controllers@npm%253A93.0.0%23~/.yarn/patches/@metamask-assets-controllers-npm-93.0.0-ea998cb0bd.patch%3A%3Aversion=93.0.0&hash=224a2c#~/.yarn/patches/@metamask-assets-controllers-patch-0229f60576.patch",
-    "@metamask/assets-controllers@npm:^91.0.0": "patch:@metamask/assets-controllers@patch%3A@metamask/assets-controllers@npm%253A93.0.0%23~/.yarn/patches/@metamask-assets-controllers-npm-93.0.0-ea998cb0bd.patch%3A%3Aversion=93.0.0&hash=224a2c#~/.yarn/patches/@metamask-assets-controllers-patch-0229f60576.patch"
+    "@metamask/assets-controllers@npm:^91.0.0": "patch:@metamask/assets-controllers@patch%3A@metamask/assets-controllers@npm%253A93.0.0%23~/.yarn/patches/@metamask-assets-controllers-npm-93.0.0-ea998cb0bd.patch%3A%3Aversion=93.0.0&hash=224a2c#~/.yarn/patches/@metamask-assets-controllers-patch-0229f60576.patch",
+    "qs@npm:6.13.0": "^6.14.1"
   },
   "dependencies": {
     "@babel/runtime": "patch:@babel/runtime@npm%3A7.25.9#~/.yarn/patches/@babel-runtime-npm-7.25.9-fe8c62510a.patch",
```

### yarn.lock
```diff
@@ -37529,21 +37529,12 @@ __metadata:
   languageName: node
   linkType: hard
 
-"qs@npm:6.13.0":
-  version: 6.13.0
-  resolution: "qs@npm:6.13.0"
-  dependencies:
-    side-channel: "npm:^1.0.6"
-  checksum: 10/f548b376e685553d12e461409f0d6e5c59ec7c7d76f308e2a888fd9db3e0c5e89902bedd0754db3a9038eda5f27da2331a6f019c8517dc5e0a16b3c9a6e9cef8
-  languageName: node
-  linkType: hard
-
-"qs@npm:^6.10.0, qs@npm:^6.12.3, qs@npm:^6.4.0":
-  version: 6.14.0
-  resolution: "qs@npm:6.14.0"
+"qs@npm:^6.10.0, qs@npm:^6.12.3, qs@npm:^6.14.1, qs@npm:^6.4.0":
+  version: 6.14.1
+  resolution: "qs@npm:6.14.1"
   dependencies:
     side-channel: "npm:^1.1.0"
-  checksum: 10/a60e49bbd51c935a8a4759e7505677b122e23bf392d6535b8fc31c1e447acba2c901235ecb192764013cd2781723dc1f61978b5fdd93cc31d7043d31cdc01974
+  checksum: 10/34b5ab00a910df432d55180ef39c1d1375e550f098b5ec153b41787f1a6a6d7e5f9495593c3b112b77dbc6709d0ae18e55b82847a4c2bbbb0de1e8ccbb1794c5
   languageName: node
   linkType: hard
 
@@ -40765,7 +40756,7 @@ __metadata:
   languageName: node
   linkType: hard
 
-"side-channel@npm:^1.0.4, side-channel@npm:^1.0.6, side-channel@npm:^1.1.0":
+"side-channel@npm:^1.0.4, side-channel@npm:^1.1.0":
   version: 1.1.0
   resolution: "side-channel@npm:1.1.0"
   dependencies:
```
