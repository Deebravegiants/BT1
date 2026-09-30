# [?] fix: audit vulnerabilities (yauzl, undici)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-03-14
Source: https://github.com/wevm/viem/commit/3d122e9002b10a462247e050687905252442857b
Type: security-commit

## Details
fix: audit vulnerabilities (yauzl, undici)

Amp-Thread-ID: https://ampcode.com/threads/T-019cea30-c276-748b-b5f1-a3f030f23ee2
Co-authored-by: Amp <amp@ampcode.com>

## Patch
### package.json
```diff
@@ -280,11 +280,12 @@
       "smol-toml@<=1.3.0": "1.3.1",
       "tar": ">=7.5.10",
       "tar-fs@>=3.0.0 <3.1.1": ">=3.1.1",
-      "undici@>=7.0.0 <7.18.2": "7.18.2",
+      "undici@>=7.0.0 <7.24.0": "7.24.0",
       "vite@>=6.0.0 <=6.4.0": "6.4.1",
       "webpack@>=5.49.0 <=5.104.0": "5.104.1",
       "ws@>=7.0.0 <7.5.10": "^7.5.10",
-      "ws@>=8.0.0 <8.17.1": "^8.17.1"
+      "ws@>=8.0.0 <8.17.1": "^8.17.1",
+      "yauzl@<3.2.1": "3.2.1"
     },
     "onlyBuiltDependencies": [
       "bun",
```

### pnpm-lock.yaml
```diff
@@ -66,6 +66,9 @@ overrides:
   webpack@>=5.49.0 <=5.104.0: 5.104.1
   ws@>=7.0.0 <7.5.10: ^7.5.10
   ws@>=8.0.0 <8.17.1: ^8.17.1
+  yauzl@<3.2.1: '>=3.2.1'
+  undici@>=7.0.0 <7.24.0: '>=7.24.0'
+  undici@>=7.17.0 <7.24.0: '>=7.24.0'
 
 importers:
 
@@ -3911,9 +3914,6 @@ packages:
   fd-package-json@2.0.0:
     resolution: {integrity: sha512-jKmm9YtsNXN789RS/0mSzOC1NUq9mkVd65vbSSVsKdjGvYXBuE4oWe2QOEoFeRmJg+lPuZxpmrfFclNhoRMneQ==}
 
-  fd-slicer@1.1.0:
-    resolution: {integrity: sha512-cE1qsB/VwyQozZ+q1dGxR8LBYNZeofhEdUNGSMbQD3Gw2lAzX9Zb3uIU6Ebc/Fmyjo9AWWfnn0AUCHqtevs/8g==}
-
   fdir@6.5.0:
     resolution: {integrity: sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==}
     engines: {node: '>=12.0.0'}
@@ -6112,8 +6112,8 @@ packages:
   undici-types@7.12.0:
     resolution: {integrity: sha512-goOacqME2GYyOZZfb5Lgtu+1IDmAlAEu5xnD3+xTzS10hT0vzpf0SPjkXwAw9Jm+4n/mQGDP3LO8CPbYROeBfQ==}
 
-  undici@7.18.2:
-    resolution: {integrity: sha512-y+8YjDFzWdQlSE9N5nzKMT3g4a5UBX1HKowfdXh0uvAnTaqqwqB92Jt4UXBAeKekDs5IaDKyJFR4X1gYVCgXcw==}
+  undici@7.24.0:
+    resolution: {integrity: sha512-jxytwMHhsbdpBXxLAcuu0fzlQeXCNnWdDyRHpvWsUl8vd98UwYdl9YTyn8/HcpcJPC3pwUveefsa3zTxyD/ERg==}
     engines: {node: '>=20.18.1'}
 
   unicode-emoji-modifier-base@1.0.0:
@@ -6559,8 +6559,9 @@ packages:
     resolution: {integrity: sha512-7dSzzRQ++CKnNI/krKnYRV7JKKPUXMEh61soaHKg9mrWEhzFWhFnxPxGl+69cD1Ou63C13NUPCnmIcrvqCuM6w==}
     engines: {node: '>=12'}
 
-  yauzl@2.10.0:
-    resolution: {integrity: sha512-p4a9I6X6nu6IhoGmBqAcbJy1mlC4j27vEPZX9F4L4/vZT3Lyq1VkFHw/V/PUcB9Buo+DG3iHkT0x3Qya58zc3g==}
+  yauzl@3.2.1:
+    resolution: {integrity: sha512-k1isifdbpNSFEHFJ1ZY4YDewv0IH9FR61lDetaRMD3j2ae3bIXGV+7c+LHCqtQGofSd8PIyV4X6+dHMAnSr60A==}
+    engines: {node: '>=12'}
 
   yocto-queue@0.1.0:
     resolution: {integrity: sha512-rVksvsnNCdJ/ohGc6xgPwyN8eheCxsiLM8mxuE/t/mOVqJewPuO1miLpTHQiRgTKCLexL4MeAFVagts7HmNZ2Q==}
@@ -10078,7 +10079,7 @@ snapshots:
     dependencies:
       debug: 4.4.3
       get-stream: 5.2.0
-      yauzl: 2.10.0
+      yauzl: 3.2.1
     optionalDependencies:
       '@types/yauzl': 2.10.3
     transitivePeerDependencies:
@@ -10151,10 +10152,6 @@ snapshots:
     dependencies:
       walk-up-path: 4.0.0
 
-  fd-slicer@1.1.0:
-    dependencies:
-      pend: 1.2.0
-
   fdir@6.5.0(picomatch@4.0.3):
     optionalDependencies:
       picomatch: 4.0.3
@@ -12798,7 +12795,7 @@ snapshots:
       ssh-remote-port-forward: 1.0.4
       tar-fs: 3.1.1
       tmp: 0.2.5
-      undici: 7.18.2
+      undici: 7.24.0
     transitivePeerDependencies:
       - bare-buffer
       - supports-color
@@ -12914,7 +12911,7 @@ snapshots:
 
   undici-types@7.12.0: {}
 
-  undici@7.18.2: {}
+  undici@7.24.0: {}
 
   unicode-emoji-modifier-base@1.0.0: {}
 
@@ -13438,10 +13435,10 @@ snapshots:
       y18n: 5.0.8
       yargs-parser: 21.1.1
 
-  yauzl@2.10.0:
+  yauzl@3.2.1:
     dependencies:
       buffer-crc32: 0.2.13
-      fd-slicer: 1.1.0
+      pend: 1.2.0
 
   yocto-queue@0.1.0: {}
 
```
