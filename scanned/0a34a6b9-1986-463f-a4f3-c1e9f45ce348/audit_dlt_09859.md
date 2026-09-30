# [?] fix(apps): Fix GHSA-2w69-qvjg-hvjx (#9752)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-01-13
Source: https://github.com/iotaledger/iota/commit/8a0100de43603f268183473552b1e4f9bc95c7e7
Type: security-commit

## Details
fix(apps): Fix GHSA-2w69-qvjg-hvjx (#9752)

Fixes
https://github.com/iotaledger/iota/actions/runs/20935041135/job/60155392142
https://github.com/advisories/GHSA-2w69-qvjg-hvjx

## Patch
### apps/explorer/package.json
```diff
@@ -57,7 +57,7 @@
         "react-error-boundary": "^4.0.10",
         "react-hook-form": "^7.45.2",
         "react-resizable-panels": "^0.0.39",
-        "react-router-dom": "^6.24.1",
+        "react-router-dom": "^6.30.3",
         "throttle-debounce": "^5.0.0",
         "zod": "^3.21.4"
     },
```

### apps/wallet/package.json
```diff
@@ -140,7 +140,7 @@
         "react-hook-form": "^7.45.2",
         "react-number-format": "^5.2.2",
         "react-redux": "^8.1.1",
-        "react-router-dom": "^6.24.1",
+        "react-router-dom": "^6.30.3",
         "rxjs": "^7.8.1",
         "semver": "^7.5.4",
         "stream-browserify": "^3.0.0",
```

### dapps/kiosk/package.json
```diff
@@ -25,7 +25,7 @@
         "react": "^18.3.1",
         "react-dom": "^18.3.1",
         "react-hot-toast": "^2.4.1",
-        "react-router-dom": "^6.24.1"
+        "react-router-dom": "^6.30.3"
     },
     "devDependencies": {
         "@headlessui/tailwindcss": "^0.1.3",
```

### dapps/multisig-toolkit/package.json
```diff
@@ -36,7 +36,7 @@
         "react-dom": "^18.3.1",
         "react-hook-form": "^7.45.2",
         "react-hot-toast": "^2.4.1",
-        "react-router-dom": "^6.24.1",
+        "react-router-dom": "^6.30.3",
         "tailwind-merge": "^2.4.0",
         "zod": "^3.21.4"
     },
```

### examples/trading/frontend/package.json
```diff
@@ -26,7 +26,7 @@
     "react": "^18.3.1",
     "react-dom": "^18.3.1",
     "react-hot-toast": "^2.4.1",
-    "react-router-dom": "^6.24.1"
+    "react-router-dom": "^6.30.3"
   },
   "devDependencies": {
     "@types/react": "^18.3.3",
```

### pnpm-lock.yaml
```diff
@@ -561,8 +561,8 @@ importers:
         specifier: ^0.0.39
         version: 0.0.39(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
       react-router-dom:
-        specifier: ^6.24.1
-        version: 6.26.2(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
+        specifier: ^6.30.3
+        version: 6.30.3(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
       throttle-debounce:
         specifier: ^5.0.0
         version: 5.0.2
@@ -917,8 +917,8 @@ importers:
         specifier: ^8.1.1
         version: 8.1.3(@types/react-dom@18.3.0)(@types/react@18.3.9)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(redux@4.2.1)
       react-router-dom:
-        specifier: ^6.24.1
-        version: 6.26.2(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
+        specifier: ^6.30.3
+        version: 6.30.3(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
       rxjs:
         specifier: ^7.8.1
         version: 7.8.1
@@ -1219,8 +1219,8 @@ importers:
         specifier: ^2.4.1
         version: 2.4.1(csstype@3.1.3)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
       react-router-dom:
-        specifier: ^6.24.1
-        version: 6.26.2(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
+        specifier: ^6.30.3
+        version: 6.30.3(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
     devDependencies:
       '@headlessui/tailwindcss':
         specifier: ^0.1.3
@@ -1325,8 +1325,8 @@ importers:
         specifier: ^2.4.1
         version: 2.4.1(csstype@3.1.3)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
       react-router-dom:
-        specifier: ^6.24.1
-        version: 6.26.2(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
+        specifier: ^6.30.3
+        version: 6.30.3(react-dom@18.3.1(react@18.3.1))(react@18.3.1)
       tailwind-merge:
         specifier: ^2.4.0
         version: 2.5.2
@@ -7335,8 +7335,8 @@ packages:
       react-redux:
         optional: true
 
-  '@remix-run/router@1.19.2':
-    resolution: {integrity: sha512-baiMx18+IMuD1yyvOGaHM9QrVUPGGG0jC+z+IPHnRJWUAUvaKuWKyE8gjDj2rzv3sz9zOGoRSPgeBVHRhZnBlA==}
+  '@remix-run/router@1.23.2':
+    resolution: {integrity: sha512-Ic6m2U/rMjTkhERIa/0ZtXJP17QUi2CbWE7cqx4J58M8aA3QTfW+2UlQ4psvTX9IO1RfNVhK3pcpdjej7L+t2w==}
     engines: {node: '>=14.0.0'}
 
   '@reown/appkit-common@1.7.8':
@@ -16801,8 +16801,8 @@ packages:
     peerDependencies:
       react: '>=15'
 
-  react-router-dom@6.26.2:
-    resolution: {integrity: sha512-z7YkaEW0Dy35T3/QKPYB1LjMK2R1fxnHO8kWpUMTBdfVzZrWOiY9a7CtN8HqdWtDUWd5FY6Dl8HFsqVwH4uOtQ==}
+  react-router-dom@6.30.3:
+    resolution: {integrity: sha512-pxPcv1AczD4vso7G4Z3TKcvlxK7g7TNt3/FNGMhfqyntocvYKj+GCatfigGDjbLozC4baguJ0ReCigoDJXb0ag==}
     engines: {node: '>=14.0.0'}
     peerDependencies:
       react: '>=16.8'
@@ -16813,8 +16813,8 @@ packages:
     peerDependencies:
       react: '>=15'
 
-  react-router@6.26.2:
-    resolution: {integrity: sha512-tvN1iuT03kHgOFnLPfLJ8V95eijteveqdOSk+srqfePtQvqCExB8eHOYnlilbOcyJyKnYkr1vJvf7YqotAJu1A==}
+  react-router@6.30.3:
+    resolution: {integrity: sha512-XRnlbKMTmktBkjCLE8/XcZFlnHvr2Ltdr1eJX4idL55/9BbORzyZEaIkBFDhFGCEWBBItsVrDxwx3gnisMitdw==}
     engines: {node: '>=14.0.0'}
     peerDependencies:
       react: '>=16.8'
@@ -27639,7 +27639,7 @@ snapshots:
       react: 18.3.1
       react-redux: 8.1.3(@types/react-dom@18.3.0)(@types/react@18.3.9)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(redux@4.2.1)
 
-  '@remix-run/router@1.19.2': {}
+  '@remix-run/router@1.23.2': {}
 
   '@reown/appkit-common@1.7.8(bufferutil@4.0.9)(typescript@5.8.3)(utf-8-validate@5.0.10)(zod@3.22.4)':
     dependencies:
@@ -40706,12 +40706,12 @@ snapshots:
       tiny-invariant: 1.3.3
       tiny-warning: 1.0.3
 
-  react-router-dom@6.26.2(react-dom@18.3.1(react@18.3.1))(react@18.3.1):
+  react-router-dom@6.30.3(react-dom@18.3.1(react@18.3.1))(react@18.3.1):
     dependencies:
-      '@remix-run/router': 1.19.2
+      '@remix-run/router': 1.23.2
       react: 18.3.1
       react-dom: 18.3.1(react@18.3.1)
-      react-router: 6.26.2(react@18.3.1)
+      react-router: 6.30.3(react@18.3.1)
 
   react-router@5.3.4(react@18.3.1):
     dependencies:
@@ -40726,9 +40726,9 @@ snapshots:
       tiny-invariant: 1.3.3
       tiny-warning: 1.0.3
 
-  react-router@6.26.2(react@18.3.1):
+  react-router@6.30.3(react@18.3.1):
     dependencies:
-      '@remix-run/router': 1.19.2
+      '@remix-run/router': 1.23.2
       react: 18.3.1
 
   react-style-singleton@2.2.1(@types/react@18.3.9)(react@18.3.1):
```
