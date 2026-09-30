# [?] chore: fix audit vulnerabilities (lodash, hono, @hono/node-server, basic-ftp)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-04-09
Source: https://github.com/wevm/viem/commit/863f9c6c9c09d2575b80dcefc48c1beb4d5db9c9
Type: security-commit

## Details
chore: fix audit vulnerabilities (lodash, hono, @hono/node-server, basic-ftp)

Amp-Thread-ID: https://ampcode.com/threads/T-019d708b-bcfc-778d-b091-05e975beefc9

## Patch
### package.json
```diff
@@ -246,11 +246,11 @@
       "permissionless>viem": "workspace:*",
       "@babel/helpers@<7.26.10": "7.26.10",
       "@babel/runtime@<7.26.10": "7.26.10",
-      "@hono/node-server@<1.19.10": "1.19.10",
+      "@hono/node-server@<1.19.13": "1.19.13",
       "@isaacs/brace-expansion@<=5.0.0": "5.0.1",
       "@modelcontextprotocol/sdk@>=1.10.0 <=1.25.3": "1.26.0",
       "ajv@<8.18.0": "8.18.0",
-      "basic-ftp@<5.2.0": "5.2.0",
+      "basic-ftp@=5.2.0": "5.2.1",
       "brace-expansion@>=2.0.0 <=2.0.1": "2.0.2",
       "cookie@<0.7.0": "^0.7.0",
       "cross-spawn@<6.0.6": ">=6.0.6",
@@ -260,8 +260,8 @@
       "fastify": ">=5.8.3",
       "find-my-way@>=5.5.0 <8.2.2": "^8.2.2",
       "glob@>=10.3.7 <=11.0.3": ">=11.1.0",
-      "hono": ">=4.12.7",
-      "lodash@>=4.0.0 <=4.17.22": "4.17.23",
+      "hono": ">=4.12.12",
+      "lodash@>=4.0.0 <=4.17.23": "4.18.1",
       "lodash-es@>=4.0.0 <=4.17.22": "4.17.23",
       "mdast-util-to-hast@>=13.0.0 <13.2.1": "13.2.1",
       "micromatch@<4.0.8": "^4.0.8",
```

### pnpm-lock.yaml
```diff
@@ -27,11 +27,11 @@ overrides:
   permissionless>viem: workspace:*
   '@babel/helpers@<7.26.10': 7.26.10
   '@babel/runtime@<7.26.10': 7.26.10
-  '@hono/node-server@<1.19.10': 1.19.10
+  '@hono/node-server@<1.19.13': 1.19.13
   '@isaacs/brace-expansion@<=5.0.0': 5.0.1
   '@modelcontextprotocol/sdk@>=1.10.0 <=1.25.3': 1.26.0
   ajv@<8.18.0: 8.18.0
-  basic-ftp@<5.2.0: 5.2.0
+  basic-ftp@=5.2.0: 5.2.1
   brace-expansion@>=2.0.0 <=2.0.1: 2.0.2
   cookie@<0.7.0: ^0.7.0
   cross-spawn@<6.0.6: '>=6.0.6'
@@ -41,8 +41,8 @@ overrides:
   fastify: '>=5.8.3'
   find-my-way@>=5.5.0 <8.2.2: ^8.2.2
   glob@>=10.3.7 <=11.0.3: '>=11.1.0'
-  hono: '>=4.12.7'
-  lodash@>=4.0.0 <=4.17.22: 4.17.23
+  hono: '>=4.12.12'
+  lodash@>=4.0.0 <=4.17.23: 4.18.1
   lodash-es@>=4.0.0 <=4.17.22: 4.17.23
   mdast-util-to-hast@>=13.0.0 <13.2.1: 13.2.1
   micromatch@<4.0.8: ^4.0.8
@@ -1428,11 +1428,11 @@ packages:
     engines: {node: '>=6'}
     hasBin: true
 
-  '@hono/node-server@1.19.10':
-    resolution: {integrity: sha512-hZ7nOssGqRgyV3FVVQdfi+U4q02uB23bpnYpdvNXkYTRRyWx84b7yf1ans+dnJ/7h41sGL3CeQTfO+ZGxuO+Iw==}
+  '@hono/node-server@1.19.13':
+    resolution: {integrity: sha512-TsQLe4i2gvoTtrHje625ngThGBySOgSK3Xo2XRYOdqGN1teR8+I7vchQC46uLJi8OF62YTYA3AhSpumtkhsaKQ==}
     engines: {node: '>=18.14.1'}
     peerDependencies:
-      hono: '>=4.12.7'
+      hono: '>=4.12.12'
 
   '@iconify-json/lucide@1.2.86':
     resolution: {integrity: sha512-W/Jz7/gGOkI9u43r+UHmQtZtcyw2YLvMwiHa01WV6V4DYltrPNXiD+bCa+djV8LZB1uwF8CiympOMIbgiQ74nA==}
@@ -3202,8 +3202,8 @@ packages:
     resolution: {integrity: sha512-e23vBV1ZLfjb9apvfPk4rHVu2ry6RIr2Wfs+O324okSidrX7pTAnEJPCh/O5BtRlr7QtZI7ktOP3vsqr7Z5XoA==}
     hasBin: true
 
-  basic-ftp@5.2.0:
-    resolution: {integrity: sha512-VoMINM2rqJwJgfdHq6RiUudKt2BV+FY5ZFezP/ypmwayk68+NzzAQy4XXLlqsGD4MCzq3DrmNFD/uUmBJuGoXw==}
+  basic-ftp@5.2.1:
+    resolution: {integrity: sha512-0yaL8JdxTknKDILitVpfYfV2Ob6yb3udX/hK97M7I3jOeznBNxQPtVvTUtnhUkyHlxFWyr5Lvknmgzoc7jf+1Q==}
     engines: {node: '>=10.0.0'}
 
   bcrypt-pbkdf@1.0.2:
@@ -4134,8 +4134,8 @@ packages:
   highlight.js@10.7.3:
     resolution: {integrity: sha512-tzcUFauisWKNHaRkN4Wjl/ZA07gENAjFl3J/c480dprkGTg5EQstgaNFqBfUqCq54kZRIEcreTsAgF/m2quD7A==}
 
-  hono@4.12.7:
-    resolution: {integrity: sha512-jq9l1DM0zVIvsm3lv9Nw9nlJnMNPOcAtsbsgiUhWcFzPE99Gvo6yRTlszSLLYacMeQ6quHD6hMfId8crVHvexw==}
+  hono@4.12.12:
+    resolution: {integrity: sha512-p1JfQMKaceuCbpJKAPKVqyqviZdS0eUxH9v82oWo1kb9xjQ5wA6iP3FNVAPDFlz5/p7d45lO+BpSk1tuSZMF4Q==}
     engines: {node: '>=16.9.0'}
 
   html-escaper@2.0.2:
@@ -4538,8 +4538,8 @@ packages:
   lodash.startcase@4.4.0:
     resolution: {integrity: sha512-+WKqsK294HMSc2jEbNgpHpd0JfIBhp7rEV4aqXWqFr6AlXov+SlcgB1Fv01y2kGe3Gc8nMW7VA0SrGuSkRfIEg==}
 
-  lodash@4.17.23:
-    resolution: {integrity: sha512-LgVTMpQtIopCi79SJeDiP0TfWi5CNEc/L/aRdTh3yIvmZXTnheWpKjSZhnvMl8iXbC1tFg9gdHHDMLoV7CnG+w==}
+  lodash@4.18.1:
+    resolution: {integrity: sha512-dMInicTPVE8d1e5otfwmmjlxkZoUpiVLwyeTdUsi/Caj/gfzzblBcCE5sRHV/AsjuCmxWrte2TNGSYuCeCq+0Q==}
 
   long@5.2.3:
     resolution: {integrity: sha512-lcHwpNoggQTObv5apGNCTdJrO69eHOZMi4BNC+rTLER8iHAqGrUVeLh/irVIM7zTw2bOXA8T6uNPeujwOLg/2Q==}
@@ -7433,9 +7433,9 @@ snapshots:
       protobufjs: 7.4.0
       yargs: 17.7.2
 
-  '@hono/node-server@1.19.10(hono@4.12.7)':
+  '@hono/node-server@1.19.13(hono@4.12.12)':
     dependencies:
-      hono: 4.12.7
+      hono: 4.12.12
 
   '@iconify-json/lucide@1.2.86':
     dependencies:
@@ -7699,7 +7699,7 @@ snapshots:
 
   '@modelcontextprotocol/sdk@1.26.0':
     dependencies:
-      '@hono/node-server': 1.19.10(hono@4.12.7)
+      '@hono/node-server': 1.19.13(hono@4.12.12)
       ajv: 8.18.0
       ajv-formats: 3.0.1
       content-type: 1.0.5
@@ -7709,7 +7709,7 @@ snapshots:
       eventsource-parser: 3.0.6
       express: 5.2.1
       express-rate-limit: 8.3.0(express@5.2.1)
-      hono: 4.12.7
+      hono: 4.12.12
       jose: 6.1.3
       json-schema-typed: 8.0.2
       pkce-challenge: 5.0.1
@@ -9158,7 +9158,7 @@ snapshots:
       graceful-fs: 4.2.11
       is-stream: 2.0.1
       lazystream: 1.0.1
-      lodash: 4.17.23
+      lodash: 4.18.1
       normalize-path: 3.0.0
       readable-stream: 4.5.2
 
@@ -9264,7 +9264,7 @@ snapshots:
 
   baseline-browser-mapping@2.9.18: {}
 
-  basic-ftp@5.2.0: {}
+  basic-ftp@5.2.1: {}
 
   bcrypt-pbkdf@1.0.2:
     dependencies:
@@ -9343,7 +9343,7 @@ snapshots:
       cron-parser: 4.9.0
       get-port: 5.1.1
       ioredis: 5.6.0
-      lodash: 4.17.23
+      lodash: 4.18.1
       msgpackr: 1.11.2
       semver: 7.7.2
       uuid: 8.3.2
@@ -10215,7 +10215,7 @@ snapshots:
 
   get-uri@6.0.3:
     dependencies:
-      basic-ftp: 5.2.0
+      basic-ftp: 5.2.1
       data-uri-to-buffer: 6.0.2
       debug: 4.4.3
       fs-extra: 11.3.0
@@ -10345,7 +10345,7 @@ snapshots:
 
   highlight.js@10.7.3: {}
 
-  hono@4.12.7: {}
+  hono@4.12.12: {}
 
   html-escaper@2.0.2: {}
 
@@ -10709,7 +10709,7 @@ snapshots:
 
   lodash.startcase@4.4.0: {}
 
-  lodash@4.17.23: {}
+  lodash@4.18.1: {}
 
   long@5.2.3: {}
 
@@ -13129,7 +13129,7 @@ snapshots:
       estree-util-visit: 2.0.0
       extend: 3.0.2
       github-slugger: 2.0.0
-      hono: 4.12.7
+      hono: 4.12.12
       image-size: 2.0.2
       mdast-util-from-markdown: 2.0.2
       mdast-util-gfm: 3.1.0
@@ -13194,11 +13194,11 @@ snapshots:
 
   waku@1.0.0-alpha.2(@types/node@24.5.2)(jiti@2.6.0)(lightningcss@1.30.2)(react-dom@19.2.3(react@19.2.3))(react-server-dom-webpack@19.2.4(react-dom@19.2.3(react@19.2.3))(react@19.2.3)(webpack@5.104.1))(react@19.2.3)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3):
     dependencies:
-      '@hono/node-server': 1.19.10(hono@4.12.7)
+      '@hono/node-server': 1.19.13(hono@4.12.12)
       '@vitejs/plugin-react': 5.1.2(vite@7.3.2(@types/node@24.5.2)(jiti@2.6.0)(lightningcss@1.30.2)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3))
       '@vitejs/plugin-rsc': 0.5.16(react-dom@19.2.3(react@19.2.3))(react-server-dom-webpack@19.2.4(react-dom@19.2.3(react@19.2.3))(react@19.2.3)(webpack@5.104.1))(react@19.2.3)(vite@7.3.2(@types/node@24.5.2)(jiti@2.6.0)(lightningcss@1.30.2)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3))
       dotenv: 17.2.3
-      hono: 4.12.7
+      hono: 4.12.12
       magic-string: 0.30.21
       picocolors: 1.1.1
       react: 19.2.3
```

### pnpm-workspace.yaml
```diff
@@ -39,4 +39,5 @@ minimumReleaseAgeExclude:
   - vitest
   - vocs
   - webpack
+  - basic-ftp
 
```
