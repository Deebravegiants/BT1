# [?] fix(pnpm): Fix GHSA-mp2g-9vg9-f4cg, patch h3 to 1.15.5 (#9828)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-01-20
Source: https://github.com/iotaledger/iota/commit/f399d6409e72b2b12cce5383209625cc1e380fe4
Type: security-commit

## Details
fix(pnpm): Fix GHSA-mp2g-9vg9-f4cg, patch h3 to 1.15.5 (#9828)

Fixes
https://github.com/iotaledger/iota/actions/runs/21118615942/job/60727917282

Co-authored-by: JCNoguera <88061365+VmMad@users.noreply.github.com>

## Patch
### package.json
```diff
@@ -44,7 +44,8 @@
 			"node-forge@1.3.1": "^1.3.3",
 			"glob@>=10.2.0 <10.5.0": "10.5.0",
 			"qs@<6.14.1": "6.14.1",
-			"preact@>=10.28.0 <10.28.2": "10.28.2"
+			"preact@>=10.28.0 <10.28.2": "10.28.2",
+			"h3@<=1.15.4": "1.15.5"
 		}
 	},
 	"engines": {
```

### pnpm-lock.yaml
```diff
@@ -14,6 +14,7 @@ overrides:
   glob@>=10.2.0 <10.5.0: 10.5.0
   qs@<6.14.1: 6.14.1
   preact@>=10.28.0 <10.28.2: 10.28.2
+  h3@<=1.15.4: 1.15.5
 
 importers:
 
@@ -12690,8 +12691,8 @@ packages:
     resolution: {integrity: sha512-ax7ZYomf6jqPTQ4+XCpUGyXKHk5WweS+e05MBO4/y3WJ5RkmPXNKvX+bx1behVILVwr6JSQvZAku021CHPXG3Q==}
     engines: {node: '>=10'}
 
-  h3@1.15.3:
-    resolution: {integrity: sha512-z6GknHqyX0h9aQaTx22VZDf6QyZn+0Nh+Ym8O/u0SGSkyF5cuTJYKlc8MkzW3Nzf9LE1ivcpmYC3FUGpywhuUQ==}
+  h3@1.15.5:
+    resolution: {integrity: sha512-xEyq3rSl+dhGX2Lm0+eFQIAzlDN6Fs0EcC4f7BNUmzaRX/PTzeuM+Tr2lHB8FoXggsQIeXLj8EDVgs5ywxyxmg==}
 
   handle-thing@2.0.1:
     resolution: {integrity: sha512-9Qn4yBxelxoh2Ow62nP+Ka/kMnOXRi8BXnRaUwezLNhqelnN49xKz4F/dPP8OYLxLxq6JDtZb2i9XznUQbNPTg==}
@@ -15008,8 +15009,8 @@ packages:
   node-int64@0.4.0:
     resolution: {integrity: sha512-O5lz91xSOeoXP6DulyHfllpq+Eg00MWitZIbtPfoSEvqIHdl5gfcY6hYzDWnj0qD5tz52PI08u9qUvSVeUBeHw==}
 
-  node-mock-http@1.0.0:
-    resolution: {integrity: sha512-0uGYQ1WQL1M5kKvGRXWQ3uZCHtLTO8hln3oBjIusM75WoesZ909uQJs/Hb946i2SS+Gsrhkaa6iAO17jRIv6DQ==}
+  node-mock-http@1.0.4:
+    resolution: {integrity: sha512-8DY+kFsDkNXy1sJglUfuODx1/opAGJGyrTuFqEoN90oRc2Vk0ZbD4K2qmKXBBEhZQzdKHIVfEJpDU8Ak2NJEvQ==}
 
   node-notifier@10.0.1:
     resolution: {integrity: sha512-YX7TSyDukOZ0g+gmzjB6abKu+hTGvO8+8+gIFDsRCU2t8fLV/P2unmt+LGFaIa4y64aX98Qksa97rgz4vMNeLQ==}
@@ -18656,6 +18657,9 @@ packages:
   ufo@1.6.1:
     resolution: {integrity: sha512-9a4/uxlTWJ4+a5i0ooc1rU7C7YOw3wT+UGqdeNNHWnOF9qcMBgLRS+4IYUqbczewFx4mLEig6gawh7X6mFlEkA==}
 
+  ufo@1.6.3:
+    resolution: {integrity: sha512-yDJTmhydvl5lJzBmy/hyOAA0d+aqCBuwl818haVdYCRrWV84o7YyeVm4QlVHStqNrrJSTb6jKuFAVqAFsr+K3Q==}
+
   uglify-js@3.19.3:
     resolution: {integrity: sha512-v3Xu+yuwBXisp6QYTcH4UbH+xYJXqnq2m/LtQVWKWzYc1iehYnLixoQDN9FH6/j9/oybfd6W9Ghwkl8+UMKTKQ==}
     engines: {node: '>=0.8.0'}
@@ -35515,16 +35519,16 @@ snapshots:
     dependencies:
       duplexer: 0.1.2
 
-  h3@1.15.3:
+  h3@1.15.5:
     dependencies:
       cookie-es: 1.2.2
       crossws: 0.3.5
       defu: 6.1.4
       destr: 2.0.5
       iron-webcrypto: 1.2.1
-      node-mock-http: 1.0.0
+      node-mock-http: 1.0.4
       radix3: 1.1.2
-      ufo: 1.6.1
+      ufo: 1.6.3
       uncrypto: 0.1.3
 
   handle-thing@2.0.1: {}
@@ -38729,7 +38733,7 @@ snapshots:
 
   node-int64@0.4.0: {}
 
-  node-mock-http@1.0.0: {}
+  node-mock-http@1.0.4: {}
 
   node-notifier@10.0.1:
     dependencies:
@@ -43047,6 +43051,8 @@ snapshots:
 
   ufo@1.6.1: {}
 
+  ufo@1.6.3: {}
+
   uglify-js@3.19.3:
     optional: true
 
@@ -43228,7 +43234,7 @@ snapshots:
       anymatch: 3.1.3
       chokidar: 4.0.3
       destr: 2.0.5
-      h3: 1.15.3
+      h3: 1.15.5
       lru-cache: 10.4.3
       node-fetch-native: 1.6.6
       ofetch: 1.4.1
```
