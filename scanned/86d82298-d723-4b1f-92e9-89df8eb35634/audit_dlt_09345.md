# [?] fix: add hono and @hono/node-server overrides for audit vulnerabilities

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-03-04
Source: https://github.com/wevm/viem/commit/6fbd6d424bea78a282e1bbffc87b2867c2d11d05
Type: security-commit

## Details
fix: add hono and @hono/node-server overrides for audit vulnerabilities

Amp-Thread-ID: https://ampcode.com/threads/T-019cb6d7-c794-742b-ac88-6bc216b24bbc
Co-authored-by: Amp <amp@ampcode.com>

## Patch
### package.json
```diff
@@ -302,7 +302,9 @@
       "rollup@>=4.0.0 <4.59.0": "4.59.0",
       "basic-ftp@<5.2.0": "5.2.0",
       "minimatch@>=10.0.0 <10.2.3": "10.2.3",
-      "serialize-javascript@<=7.0.2": "7.0.3"
+      "serialize-javascript@<=7.0.2": "7.0.3",
+      "hono@<4.12.4": "4.12.4",
+      "@hono/node-server@<1.19.10": "1.19.10"
     },
     "onlyBuiltDependencies": [
       "bun",
```

### pnpm-lock.yaml
```diff
@@ -84,6 +84,8 @@ overrides:
   basic-ftp@<5.2.0: 5.2.0
   minimatch@>=10.0.0 <10.2.3: 10.2.3
   serialize-javascript@<=7.0.2: 7.0.3
+  hono@<4.12.4: 4.12.4
+  '@hono/node-server@<1.19.10': 1.19.10
 
 importers:
 
@@ -1435,17 +1437,11 @@ packages:
     engines: {node: '>=6'}
     hasBin: true
 
-  '@hono/node-server@1.19.5':
-    resolution: {integrity: sha512-iBuhh+uaaggeAuf+TftcjZyWh2GEgZcVGXkNtskLVoWaXhnJtC5HLHrU8W1KHDoucqO1MswwglmkWLFyiDn4WQ==}
+  '@hono/node-server@1.19.10':
+    resolution: {integrity: sha512-hZ7nOssGqRgyV3FVVQdfi+U4q02uB23bpnYpdvNXkYTRRyWx84b7yf1ans+dnJ/7h41sGL3CeQTfO+ZGxuO+Iw==}
     engines: {node: '>=18.14.1'}
     peerDependencies:
-      hono: 4.11.10
-
-  '@hono/node-server@1.19.9':
-    resolution: {integrity: sha512-vHL6w3ecZsky+8P5MD+eFfaGTyCeOHUIFYMGpQGbrBTSmNNoxv0if69rEZ5giu36weC5saFuznL411gRX7bJDw==}
-    engines: {node: '>=18.14.1'}
-    peerDependencies:
-      hono: 4.11.10
+      hono: 4.12.4
 
   '@iconify-json/lucide@1.2.86':
     resolution: {integrity: sha512-W/Jz7/gGOkI9u43r+UHmQtZtcyw2YLvMwiHa01WV6V4DYltrPNXiD+bCa+djV8LZB1uwF8CiympOMIbgiQ74nA==}
@@ -4148,8 +4144,8 @@ packages:
   highlight.js@10.7.3:
     resolution: {integrity: sha512-tzcUFauisWKNHaRkN4Wjl/ZA07gENAjFl3J/c480dprkGTg5EQstgaNFqBfUqCq54kZRIEcreTsAgF/m2quD7A==}
 
-  hono@4.11.10:
-    resolution: {integrity: sha512-kyWP5PAiMooEvGrA9jcD3IXF7ATu8+o7B3KCbPXid5se52NPqnOpM/r9qeW2heMnOekF4kqR1fXJqCYeCLKrZg==}
+  hono@4.12.4:
+    resolution: {integrity: sha512-ooiZW1Xy8rQ4oELQ++otI2T9DsKpV0M6c6cO6JGx4RTfav9poFFLlet9UMXHZnoM1yG0HWGlQLswBGX3RZmHtg==}
     engines: {node: '>=16.9.0'}
 
   html-escaper@2.0.2:
@@ -7497,13 +7493,9 @@ snapshots:
       protobufjs: 7.4.0
       yargs: 17.7.2
 
-  '@hono/node-server@1.19.5(hono@4.11.10)':
-    dependencies:
-      hono: 4.11.10
-
-  '@hono/node-server@1.19.9(hono@4.11.10)':
+  '@hono/node-server@1.19.10(hono@4.12.4)':
     dependencies:
-      hono: 4.11.10
+      hono: 4.12.4
 
   '@iconify-json/lucide@1.2.86':
     dependencies:
@@ -7767,7 +7759,7 @@ snapshots:
 
   '@modelcontextprotocol/sdk@1.26.0':
     dependencies:
-      '@hono/node-server': 1.19.9(hono@4.11.10)
+      '@hono/node-server': 1.19.10(hono@4.12.4)
       ajv: 8.18.0
       ajv-formats: 3.0.1
       content-type: 1.0.5
@@ -7777,7 +7769,7 @@ snapshots:
       eventsource-parser: 3.0.6
       express: 5.2.1
       express-rate-limit: 8.2.1(express@5.2.1)
-      hono: 4.11.10
+      hono: 4.12.4
       jose: 6.1.3
       json-schema-typed: 8.0.2
       pkce-challenge: 5.0.1
@@ -10440,7 +10432,7 @@ snapshots:
 
   highlight.js@10.7.3: {}
 
-  hono@4.11.10: {}
+  hono@4.12.4: {}
 
   html-escaper@2.0.2: {}
 
@@ -13249,7 +13241,7 @@ snapshots:
       estree-util-visit: 2.0.0
       extend: 3.0.2
       github-slugger: 2.0.0
-      hono: 4.11.10
+      hono: 4.12.4
       image-size: 2.0.2
       mdast-util-from-markdown: 2.0.2
       mdast-util-gfm: 3.1.0
@@ -13314,11 +13306,11 @@ snapshots:
 
   waku@1.0.0-alpha.2(@types/node@24.5.2)(jiti@2.6.0)(lightningcss@1.30.2)(react-dom@19.2.3(react@19.2.3))(react-server-dom-webpack@19.2.4(react-dom@19.2.3(react@19.2.3))(react@19.2.3)(webpack@5.104.1))(react@19.2.3)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.2):
     dependencies:
-      '@hono/node-server': 1.19.5(hono@4.11.10)
+      '@hono/node-server': 1.19.10(hono@4.12.4)
       '@vitejs/plugin-react': 5.1.2(vite@7.3.1(@types/node@24.5.2)(jiti@2.6.0)(lightningcss@1.30.2)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.2))
       '@vitejs/plugin-rsc': 0.5.16(react-dom@19.2.3(react@19.2.3))(react-server-dom-webpack@19.2.4(react-dom@19.2.3(react@19.2.3))(react@19.2.3)(webpack@5.104.1))(react@19.2.3)(vite@7.3.1(@types/node@24.5.2)(jiti@2.6.0)(lightningcss@1.30.2)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.2))
       dotenv: 17.2.3
-      hono: 4.11.10
+      hono: 4.12.4
       magic-string: 0.30.21
       picocolors: 1.1.1
       react: 19.2.3
```
