# [?] chore: fix tar audit vulnerability

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/wagmi
Published: 2026-01-21
Source: https://github.com/wevm/wagmi/commit/184426165170737c0587d94696b50b6c433d2014
Type: security-commit

## Details
chore: fix tar audit vulnerability

## Patch
### pnpm-lock.yaml
```diff
@@ -92,8 +92,7 @@ overrides:
   node-forge@<1.3.2: '>=1.3.2'
   semver@<5.7.2: '>=5.7.2'
   serialize-javascript@>=6.0.0 <6.0.2: 6.0.2
-  tar@<=7.5.2: 7.5.3
-  tar@=7.5.1: 7.5.2
+  tar@<=7.5.3: 7.5.4
   tmp@<=0.2.3: 0.2.4
   undici@<6.23.0: 6.23.0
   undici@>=7.0.0 <7.18.2: 7.18.2
@@ -9325,8 +9324,8 @@ packages:
   tar-stream@3.1.7:
     resolution: {integrity: sha512-qJj60CXt7IU1Ffyc3NJMjh6EkuCFej46zUqJ4J7pqYlThyd9bO0XBTmcOIhSzZJVWfsLks0+nle/j538YAW9RQ==}
 
-  tar@7.5.3:
-    resolution: {integrity: sha512-ENg5JUHUm2rDD7IvKNFGzyElLXNjachNLp6RaGf4+JOgxXHkqA+gq81ZAMCUmtMtqBsoU62lcp6S27g1LCYGGQ==}
+  tar@7.5.4:
+    resolution: {integrity: sha512-AN04xbWGrSTDmVwlI4/GTlIIwMFk/XEv7uL8aa57zuvRy6s4hdBed+lVq2fAZ89XDa7Us3ANXcE3Tvqvja1kTA==}
     engines: {node: '>=18'}
 
   temp-dir@1.0.0:
@@ -12010,7 +12009,7 @@ snapshots:
       node-fetch: 2.7.0
       nopt: 8.1.0
       semver: 7.7.3
-      tar: 7.5.3
+      tar: 7.5.4
     transitivePeerDependencies:
       - encoding
       - supports-color
@@ -20209,7 +20208,7 @@ snapshots:
       execa: 9.6.0
       get-port: 7.1.0
       http-proxy: 1.18.1
-      tar: 7.5.3
+      tar: 7.5.4
     optionalDependencies:
       testcontainers: 11.11.0
     transitivePeerDependencies:
@@ -21012,7 +21011,7 @@ snapshots:
     transitivePeerDependencies:
       - bare-abort-controller
 
-  tar@7.5.3:
+  tar@7.5.4:
     dependencies:
       '@isaacs/fs-minipass': 4.0.1
       chownr: 3.0.0
```

### pnpm-workspace.yaml
```diff
@@ -66,8 +66,7 @@ overrides:
   node-forge@<1.3.2: '>=1.3.2'
   semver@<5.7.2: '>=5.7.2'
   serialize-javascript@>=6.0.0 <6.0.2: 6.0.2
-  tar@<=7.5.2: '7.5.3'
-  tar@=7.5.1: '7.5.2'
+  tar@<=7.5.3: 7.5.4
   tmp@<=0.2.3: 0.2.4
   undici@<6.23.0: 6.23.0
   undici@>=7.0.0 <7.18.2: 7.18.2
```
