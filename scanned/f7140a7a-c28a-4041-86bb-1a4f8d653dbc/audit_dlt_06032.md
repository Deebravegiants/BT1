# [?] fix(turbo): Fix `GHSA-37ch-88jc-xwx2` and `GHSA-j3q9-mxjg-w52f (#11006)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-03-30
Source: https://github.com/iotaledger/iota/commit/76e50e62228b1a44223b13f1b12c0e82aa259bb1
Type: security-commit

## Details
fix(turbo): Fix `GHSA-37ch-88jc-xwx2` and `GHSA-j3q9-mxjg-w52f (#11006)

Fixes https://github.com/advisories/GHSA-j3q9-mxjg-w52f and
https://github.com/advisories/GHSA-37ch-88jc-xwx2

Error:
https://github.com/iotaledger/iota/actions/runs/23667847414/job/68954194586#step:6:24

## Patch
### package.json
```diff
@@ -31,7 +31,8 @@
 	},
 	"pnpm": {
 		"overrides": {
-			"path-to-regexp@<0.1.12": "^0.1.12",
+			"path-to-regexp@<0.1.13": "^0.1.13",
+			"path-to-regexp@>=8.0.0 <8.4.0": "8.4.0",
 			"image-size@<1.1.1": "^1.2.1",
 			"multer@<2.1.1": "^2.1.1",
 			"immutable@>=5.0.0 <5.1.5": "5.1.5",
```

### pnpm-lock.yaml
```diff
@@ -5,7 +5,8 @@ settings:
   excludeLinksFromLockfile: false
 
 overrides:
-  path-to-regexp@<0.1.12: ^0.1.12
+  path-to-regexp@<0.1.13: ^0.1.13
+  path-to-regexp@>=8.0.0 <8.4.0: 8.4.0
   image-size@<1.1.1: ^1.2.1
   multer@<2.1.1: ^2.1.1
   immutable@>=5.0.0 <5.1.5: 5.1.5
@@ -17570,8 +17571,8 @@ packages:
     resolution: {integrity: sha512-3O/iVVsJAPsOnpwWIeD+d6z/7PmqApyQePUtCndjatj/9I5LylHvt5qluFaBT3I5h3r1ejfR056c+FCv+NnNXg==}
     engines: {node: 18 || 20 || >=22}
 
-  path-to-regexp@0.1.12:
-    resolution: {integrity: sha512-RA1GjUVMnvYFxuqovrEqZoxxW5NUZqbwKtYz/Tt7nXerk0LbLblQmrsgdeOxV5SFHf0UDggjS/bSeOZwt1pmEQ==}
+  path-to-regexp@0.1.13:
+    resolution: {integrity: sha512-A/AGNMFN3c8bOlvV9RreMdrv7jsmF9XIfDeCd87+I8RNg6s78BhJxMu69NEMHBSJFxKidViTEdruRwEk/WIKqA==}
 
   path-to-regexp@1.9.0:
     resolution: {integrity: sha512-xIp7/apCFJuUHdDLWe8O1HIkb0kQrOMb/0u6FXQjemHn/ii5LrIzU6bdECnsiTF/GjZkMEKg1xdiZwNqDYlZ6g==}
@@ -17582,8 +17583,8 @@ packages:
   path-to-regexp@6.3.0:
     resolution: {integrity: sha512-Yhpw4T9C6hPpgPeA28us07OJeqZ5EzQTkbfwuhsUg0c237RomFoETJgmp2sa3F/41gfLE6G5cqcYwznmeEeOlQ==}
 
-  path-to-regexp@8.3.0:
-    resolution: {integrity: sha512-7jdwVIRtsP8MYpdXSwOS0YdD0Du+qOoF/AEPIt88PcCFrZCzx41oxku1jD88hZBwbNUIEfpqvuhjFaMAqMTWnA==}
+  path-to-regexp@8.4.0:
+    resolution: {integrity: sha512-PuseHIvAnz3bjrM2rGJtSgo1zjgxapTLZ7x2pjhzWwlp4SJQgK3f3iZIQwkpEnBaKz6seKBADpM4B4ySkuYypg==}
 
   path-type@4.0.0:
     resolution: {integrity: sha512-gDKb8aZMDeD/tZWs9P6+q0J9Mwkdl6xMV8TjnGP3qJVJ06bdMgkbBlLU8IdfOsIsFz2BW1rNVT3XuNEl8zPAvw==}
@@ -28654,7 +28655,7 @@ snapshots:
       '@nuxt/opencollective': 0.4.1
       fast-safe-stringify: 2.1.1
       iterare: 1.2.1
-      path-to-regexp: 8.3.0
+      path-to-regexp: 8.4.0
       reflect-metadata: 0.2.2
       rxjs: 7.8.1
       tslib: 2.8.1
@@ -28669,7 +28670,7 @@ snapshots:
       cors: 2.8.5
       express: 5.2.1
       multer: 2.1.1
-      path-to-regexp: 8.3.0
+      path-to-regexp: 8.4.0
       tslib: 2.8.1
     transitivePeerDependencies:
       - supports-color
@@ -38481,7 +38482,7 @@ snapshots:
       methods: 1.1.2
       on-finished: 2.4.1
       parseurl: 1.3.3
-      path-to-regexp: 0.1.12
+      path-to-regexp: 0.1.13
       proxy-addr: 2.0.7
       qs: 6.14.1
       range-parser: 1.2.1
@@ -38517,7 +38518,7 @@ snapshots:
       methods: 1.1.2
       on-finished: 2.4.1
       parseurl: 1.3.3
-      path-to-regexp: 0.1.12
+      path-to-regexp: 0.1.13
       proxy-addr: 2.0.7
       qs: 6.14.1
       range-parser: 1.2.1
@@ -38553,7 +38554,7 @@ snapshots:
       methods: 1.1.2
       on-finished: 2.4.1
       parseurl: 1.3.3
-      path-to-regexp: 0.1.12
+      path-to-regexp: 0.1.13
       proxy-addr: 2.0.7
       qs: 6.14.1
       range-parser: 1.2.1
@@ -43378,7 +43379,7 @@ snapshots:
       lru-cache: 11.2.6
       minipass: 7.1.3
 
-  path-to-regexp@0.1.12: {}
+  path-to-regexp@0.1.13: {}
 
   path-to-regexp@1.9.0:
     dependencies:
@@ -43388,7 +43389,7 @@ snapshots:
 
   path-to-regexp@6.3.0: {}
 
-  path-to-regexp@8.3.0: {}
+  path-to-regexp@8.4.0: {}
 
   path-type@4.0.0: {}
 
@@ -45539,7 +45540,7 @@ snapshots:
       depd: 2.0.0
       is-promise: 4.0.0
       parseurl: 1.3.3
-      path-to-regexp: 8.3.0
+      path-to-regexp: 8.4.0
     transitivePeerDependencies:
       - supports-color
 
```
