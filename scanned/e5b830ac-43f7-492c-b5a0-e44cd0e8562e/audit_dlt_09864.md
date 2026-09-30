# [?] chore: Updates NextJS to fix CVE-2025-29927 (#6057)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-03-24
Source: https://github.com/iotaledger/iota/commit/24138efe90dad847b4cedd79ac36afb8bd7b7987
Type: security-commit

## Details
chore: Updates NextJS to fix CVE-2025-29927 (#6057)

## Patch
### apps/wallet-dashboard/package.json
```diff
@@ -32,7 +32,7 @@
         "@tanstack/react-virtual": "^3.5.0",
         "clsx": "^2.1.1",
         "formik": "^2.4.2",
-        "next": "14.2.23",
+        "next": "14.2.25",
         "react": "^18.3.1",
         "zustand": "^4.4.1"
     },
```

### pnpm-lock.yaml
```diff
@@ -1033,7 +1033,7 @@ importers:
         version: link:../../sdk/wallet-standard
       '@sentry/nextjs':
         specifier: ^7.120.3
-        version: 7.120.3(next@14.2.23(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3))(react@18.3.1)(webpack@5.95.0)
+        version: 7.120.3(next@14.2.25(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3))(react@18.3.1)(webpack@5.95.0)
       '@tanstack/react-query':
         specifier: ^5.50.1
         version: 5.56.2(react@18.3.1)
@@ -1047,8 +1047,8 @@ importers:
         specifier: ^2.4.2
         version: 2.4.6(react@18.3.1)
       next:
-        specifier: 14.2.23
-        version: 14.2.23(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3)
+        specifier: 14.2.25
+        version: 14.2.25(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3)
       react:
         specifier: ^18.3.1
         version: 18.3.1
@@ -4877,62 +4877,62 @@ packages:
       '@nestjs/platform-express':
         optional: true
 
-  '@next/env@14.2.23':
-    resolution: {integrity: sha512-CysUC9IO+2Bh0omJ3qrb47S8DtsTKbFidGm6ow4gXIG6reZybqxbkH2nhdEm1tC8SmgzDdpq3BIML0PWsmyUYA==}
+  '@next/env@14.2.25':
+    resolution: {integrity: sha512-JnzQ2cExDeG7FxJwqAksZ3aqVJrHjFwZQAEJ9gQZSoEhIow7SNoKZzju/AwQ+PLIR4NY8V0rhcVozx/2izDO0w==}
 
   '@next/eslint-plugin-next@14.2.3':
     resolution: {integrity: sha512-L3oDricIIjgj1AVnRdRor21gI7mShlSwU/1ZGHmqM3LzHhXXhdkrfeNY5zif25Bi5Dd7fiJHsbhoZCHfXYvlAw==}
 
-  '@next/swc-darwin-arm64@14.2.23':
-    resolution: {integrity: sha512-WhtEntt6NcbABA8ypEoFd3uzq5iAnrl9AnZt9dXdO+PZLACE32z3a3qA5OoV20JrbJfSJ6Sd6EqGZTrlRnGxQQ==}
+  '@next/swc-darwin-arm64@14.2.25':
+    resolution: {integrity: sha512-09clWInF1YRd6le00vt750s3m7SEYNehz9C4PUcSu3bAdCTpjIV4aTYQZ25Ehrr83VR1rZeqtKUPWSI7GfuKZQ==}
     engines: {node: '>= 10'}
     cpu: [arm64]
     os: [darwin]
 
-  '@next/swc-darwin-x64@14.2.23':
-    resolution: {integrity: sha512-vwLw0HN2gVclT/ikO6EcE+LcIN+0mddJ53yG4eZd0rXkuEr/RnOaMH8wg/sYl5iz5AYYRo/l6XX7FIo6kwbw1Q==}
+  '@next/swc-darwin-x64@14.2.25':
+    resolution: {integrity: sha512-V+iYM/QR+aYeJl3/FWWU/7Ix4b07ovsQ5IbkwgUK29pTHmq+5UxeDr7/dphvtXEq5pLB/PucfcBNh9KZ8vWbug==}
     engines: {node: '>= 10'}
     cpu: [x64]
     os: [darwin]
 
-  '@next/swc-linux-arm64-gnu@14.2.23':
-    resolution: {integrity: sha512-uuAYwD3At2fu5CH1wD7FpP87mnjAv4+DNvLaR9kiIi8DLStWSW304kF09p1EQfhcbUI1Py2vZlBO2VaVqMRtpg==}
+  '@next/swc-linux-arm64-gnu@14.2.25':
+    resolution: {integrity: sha512-LFnV2899PJZAIEHQ4IMmZIgL0FBieh5keMnriMY1cK7ompR+JUd24xeTtKkcaw8QmxmEdhoE5Mu9dPSuDBgtTg==}
     engines: {node: '>= 10'}
     cpu: [arm64]
     os: [linux]
 
-  '@next/swc-linux-arm64-musl@14.2.23':
-    resolution: {integrity: sha512-Mm5KHd7nGgeJ4EETvVgFuqKOyDh+UMXHXxye6wRRFDr4FdVRI6YTxajoV2aHE8jqC14xeAMVZvLqYqS7isHL+g==}
+  '@next/swc-linux-arm64-musl@14.2.25':
+    resolution: {integrity: sha512-QC5y5PPTmtqFExcKWKYgUNkHeHE/z3lUsu83di488nyP0ZzQ3Yse2G6TCxz6nNsQwgAx1BehAJTZez+UQxzLfw==}
     engines: {node: '>= 10'}
     cpu: [arm64]
     os: [linux]
 
-  '@next/swc-linux-x64-gnu@14.2.23':
-    resolution: {integrity: sha512-Ybfqlyzm4sMSEQO6lDksggAIxnvWSG2cDWnG2jgd+MLbHYn2pvFA8DQ4pT2Vjk3Cwrv+HIg7vXJ8lCiLz79qoQ==}
+  '@next/swc-linux-x64-gnu@14.2.25':
+    resolution: {integrity: sha512-y6/ML4b9eQ2D/56wqatTJN5/JR8/xdObU2Fb1RBidnrr450HLCKr6IJZbPqbv7NXmje61UyxjF5kvSajvjye5w==}
     engines: {node: '>= 10'}
     cpu: [x64]
     os: [linux]
 
-  '@next/swc-linux-x64-musl@14.2.23':
-    resolution: {integrity: sha512-OSQX94sxd1gOUz3jhhdocnKsy4/peG8zV1HVaW6DLEbEmRRtUCUQZcKxUD9atLYa3RZA+YJx+WZdOnTkDuNDNA==}
+  '@next/swc-linux-x64-musl@14.2.25':
+    resolution: {integrity: sha512-sPX0TSXHGUOZFvv96GoBXpB3w4emMqKeMgemrSxI7A6l55VBJp/RKYLwZIB9JxSqYPApqiREaIIap+wWq0RU8w==}
     engines: {node: '>= 10'}
     cpu: [x64]
     os: [linux]
 
-  '@next/swc-win32-arm64-msvc@14.2.23':
-    resolution: {integrity: sha512-ezmbgZy++XpIMTcTNd0L4k7+cNI4ET5vMv/oqNfTuSXkZtSA9BURElPFyarjjGtRgZ9/zuKDHoMdZwDZIY3ehQ==}
+  '@next/swc-win32-arm64-msvc@14.2.25':
+    resolution: {integrity: sha512-ReO9S5hkA1DU2cFCsGoOEp7WJkhFzNbU/3VUF6XxNGUCQChyug6hZdYL/istQgfT/GWE6PNIg9cm784OI4ddxQ==}
     engines: {node: '>= 10'}
     cpu: [arm64]
     os: [win32]
 
-  '@next/swc-win32-ia32-msvc@14.2.23':
-    resolution: {integrity: sha512-zfHZOGguFCqAJ7zldTKg4tJHPJyJCOFhpoJcVxKL9BSUHScVDnMdDuOU1zPPGdOzr/GWxbhYTjyiEgLEpAoFPA==}
+  '@next/swc-win32-ia32-msvc@14.2.25':
+    resolution: {integrity: sha512-DZ/gc0o9neuCDyD5IumyTGHVun2dCox5TfPQI/BJTYwpSNYM3CZDI4i6TOdjeq1JMo+Ug4kPSMuZdwsycwFbAw==}
     engines: {node: '>= 10'}
     cpu: [ia32]
     os: [win32]
 
-  '@next/swc-win32-x64-msvc@14.2.23':
-    resolution: {integrity: sha512-xCtq5BD553SzOgSZ7UH5LH+OATQihydObTrCTvVzOro8QiWYKdBVwcB2Mn2MLMo6DGW9yH1LSPw7jS7HhgJgjw==}
+  '@next/swc-win32-x64-msvc@14.2.25':
+    resolution: {integrity: sha512-KSznmS6eFjQ9RJ1nEc66kJvtGIL1iZMYmGEXsZPh2YtnLtqrgdVvKXJY2ScjjoFnG6nGLyPFR0UiEvDwVah4Tw==}
     engines: {node: '>= 10'}
     cpu: [x64]
     os: [win32]
@@ -12776,8 +12776,8 @@ packages:
   neo-async@2.6.2:
     resolution: {integrity: sha512-Yd3UES5mWCSqR+qNT93S3UoYUkqAZ9lLg8a7g9rimsWmYGK8cVToA4/sF3RrshdyV3sAGMXVUmpMYOw+dLpOuw==}
 
-  next@14.2.23:
-    resolution: {integrity: sha512-mjN3fE6u/tynneLiEg56XnthzuYw+kD7mCujgVqioxyPqbmiotUCGJpIZGS/VaPg3ZDT1tvWxiVyRzeqJFm/kw==}
+  next@14.2.25:
+    resolution: {integrity: sha512-N5M7xMc4wSb4IkPvEV5X2BRRXUmhVHNyaXwEM86+voXthSZz8ZiRyQW4p9mwAoAPIm6OzuVZtn7idgEJeAJN3Q==}
     engines: {node: '>=18.17.0'}
     hasBin: true
     peerDependencies:
@@ -20087,7 +20087,7 @@ snapshots:
       '@types/ws': 8.5.12
       graphql: 16.9.0
       isomorphic-ws: 5.0.0(ws@8.18.0)
-      tslib: 2.7.0
+      tslib: 2.8.1
       ws: 8.18.0
     transitivePeerDependencies:
       - bufferutil
@@ -20301,7 +20301,7 @@ snapshots:
       cross-inspect: 1.0.1
       dset: 3.1.4
       graphql: 16.9.0
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   '@graphql-tools/wrap@10.0.29(graphql@16.9.0)':
     dependencies:
@@ -21063,37 +21063,37 @@ snapshots:
     optionalDependencies:
       '@nestjs/platform-express': 10.4.4(@nestjs/common@10.4.4(class-validator@0.14.1)(reflect-metadata@0.2.2)(rxjs@7.8.1))(@nestjs/core@10.4.4)
 
-  '@next/env@14.2.23': {}
+  '@next/env@14.2.25': {}
 
   '@next/eslint-plugin-next@14.2.3':
     dependencies:
       glob: 10.3.10
 
-  '@next/swc-darwin-arm64@14.2.23':
+  '@next/swc-darwin-arm64@14.2.25':
     optional: true
 
-  '@next/swc-darwin-x64@14.2.23':
+  '@next/swc-darwin-x64@14.2.25':
     optional: true
 
-  '@next/swc-linux-arm64-gnu@14.2.23':
+  '@next/swc-linux-arm64-gnu@14.2.25':
     optional: true
 
-  '@next/swc-linux-arm64-musl@14.2.23':
+  '@next/swc-linux-arm64-musl@14.2.25':
     optional: true
 
-  '@next/swc-linux-x64-gnu@14.2.23':
+  '@next/swc-linux-x64-gnu@14.2.25':
     optional: true
 
-  '@next/swc-linux-x64-musl@14.2.23':
+  '@next/swc-linux-x64-musl@14.2.25':
     optional: true
 
-  '@next/swc-win32-arm64-msvc@14.2.23':
+  '@next/swc-win32-arm64-msvc@14.2.25':
     optional: true
 
-  '@next/swc-win32-ia32-msvc@14.2.23':
+  '@next/swc-win32-ia32-msvc@14.2.25':
     optional: true
 
-  '@next/swc-win32-x64-msvc@14.2.23':
+  '@next/swc-win32-x64-msvc@14.2.25':
     optional: true
 
   '@noble/curves@1.4.2':
@@ -21354,11 +21354,11 @@ snapshots:
     dependencies:
       asn1js: 3.0.5
       pvtsutils: 1.3.5
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   '@peculiar/json-schema@1.1.12':
     dependencies:
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   '@peculiar/webcrypto@1.5.0':
     dependencies:
@@ -22507,7 +22507,7 @@ snapshots:
       '@sentry/types': 6.19.7
       tslib: 1.14.1
 
-  '@sentry/nextjs@7.120.3(next@14.2.23(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3))(react@18.3.1)(webpack@5.95.0)':
+  '@sentry/nextjs@7.120.3(next@14.2.25(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3))(react@18.3.1)(webpack@5.95.0)':
     dependencies:
       '@rollup/plugin-commonjs': 24.0.0(rollup@2.79.2)
       '@sentry/core': 7.120.3
@@ -22519,7 +22519,7 @@ snapshots:
       '@sentry/vercel-edge': 7.120.3
       '@sentry/webpack-plugin': 1.21.0
       chalk: 3.0.0
-      next: 14.2.23(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3)
+      next: 14.2.25(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3)
       react: 18.3.1
       resolve: 1.22.8
       rollup: 2.79.2
@@ -23564,7 +23564,7 @@ snapshots:
   '@swc/helpers@0.5.5':
     dependencies:
       '@swc/counter': 0.1.3
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   '@swc/types@0.1.12':
     dependencies:
@@ -24924,13 +24924,13 @@ snapshots:
       '@kamilkisiela/fast-url-parser': 1.1.4
       busboy: 1.6.0
       fast-querystring: 1.1.2
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   '@whatwg-node/node-fetch@0.7.8':
     dependencies:
       '@whatwg-node/disposablestack': 0.0.5
       busboy: 1.6.0
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   '@xtuc/ieee754@1.2.0': {}
 
@@ -24939,7 +24939,7 @@ snapshots:
   '@yarnpkg/esbuild-plugin-pnp@3.0.0-rc.15(esbuild@0.18.20)':
     dependencies:
       esbuild: 0.18.20
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   '@yarnpkg/fslib@2.10.3':
     dependencies:
@@ -25302,7 +25302,7 @@ snapshots:
     dependencies:
       pvtsutils: 1.3.5
       pvutils: 1.1.3
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   assert@2.1.0:
     dependencies:
@@ -25318,7 +25318,7 @@ snapshots:
 
   ast-types@0.16.1:
     dependencies:
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   astral-regex@2.0.0: {}
 
@@ -25758,7 +25758,7 @@ snapshots:
   capital-case@1.0.4:
     dependencies:
       no-case: 3.0.4
-      tslib: 2.7.0
+      tslib: 2.8.1
       upper-case-first: 2.0.2
 
   cardinal@2.1.1:
@@ -26202,7 +26202,7 @@ snapshots:
   constant-case@3.0.4:
     dependencies:
       no-case: 3.0.4
-      tslib: 2.7.0
+      tslib: 2.8.1
       upper-case: 2.0.2
 
   content-disposition@0.5.2: {}
@@ -27021,7 +27021,7 @@ snapshots:
   dot-case@3.0.4:
     dependencies:
       no-case: 3.0.4
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   dot-prop@5.3.0:
     dependencies:
@@ -28775,7 +28775,7 @@ snapshots:
   header-case@2.0.4:
     dependencies:
       capital-case: 1.0.4
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   headers-polyfill@4.0.3: {}
 
@@ -31241,9 +31241,9 @@ snapshots:
 
   neo-async@2.6.2: {}
 
-  next@14.2.23(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3):
+  next@14.2.25(@babel/core@7.25.2)(@playwright/test@1.47.2)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.79.3):
     dependencies:
-      '@next/env': 14.2.23
+      '@next/env': 14.2.25
       '@swc/helpers': 0.5.5
       busboy: 1.6.0
       caniuse-lite: 1.0.30001664
@@ -31253,15 +31253,15 @@ snapshots:
       react-dom: 18.3.1(react@18.3.1)
       styled-jsx: 5.1.1(@babel/core@7.25.2)(babel-plugin-macros@3.1.0)(react@18.3.1)
     optionalDependencies:
-      '@next/swc-darwin-arm64': 14.2.23
-      '@next/swc-darwin-x64': 14.2.23
-      '@next/swc-linux-arm64-gnu': 14.2.23
-      '@next/swc-linux-arm64-musl': 14.2.23
-      '@next/swc-linux-x64-gnu': 14.2.23
-      '@next/swc-linux-x64-musl': 14.2.23
-      '@next/swc-win32-arm64-msvc': 14.2.23
-      '@next/swc-win32-ia32-msvc': 14.2.23
-      '@next/swc-win32-x64-msvc': 14.2.23
+      '@next/swc-darwin-arm64': 14.2.25
+      '@next/swc-darwin-x64': 14.2.25
+      '@next/swc-linux-arm64-gnu': 14.2.25
+      '@next/swc-linux-arm64-musl': 14.2.25
+      '@next/swc-linux-x64-gnu': 14.2.25
+      '@next/swc-linux-x64-musl': 14.2.25
+      '@next/swc-win32-arm64-msvc': 14.2.25
+      '@next/swc-win32-ia32-msvc': 14.2.25
+      '@next/swc-win32-x64-msvc': 14.2.25
       '@playwright/test': 1.47.2
       sass: 1.79.3
     transitivePeerDependencies:
@@ -31271,7 +31271,7 @@ snapshots:
   no-case@3.0.4:
     dependencies:
       lower-case: 2.0.2
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   node-abort-controller@3.1.1: {}
 
@@ -31676,7 +31676,7 @@ snapshots:
   pascal-case@3.1.2:
     dependencies:
       no-case: 3.0.4
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   password-prompt@1.1.3:
     dependencies:
@@ -31688,7 +31688,7 @@ snapshots:
   path-case@3.0.4:
     dependencies:
       dot-case: 3.0.4
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   path-equal@1.2.5: {}
 
@@ -32538,7 +32538,7 @@ snapshots:
 
   pvtsutils@1.3.5:
     dependencies:
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   pvutils@1.1.3: {}
 
@@ -32964,7 +32964,7 @@ snapshots:
       esprima: 4.0.1
       source-map: 0.6.1
       tiny-invariant: 1.3.3
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   rechoir@0.6.2:
     dependencies:
@@ -33516,7 +33516,7 @@ snapshots:
   sentence-case@3.0.4:
     dependencies:
       no-case: 3.0.4
-      tslib: 2.7.0
+      tslib: 2.8.1
       upper-case-first: 2.0.2
 
   serialize-javascript@6.0.2:
@@ -35661,7 +35661,7 @@ snapshots:
       '@peculiar/json-schema': 1.1.12
       asn1js: 3.0.5
       pvtsutils: 1.3.5
-      tslib: 2.7.0
+      tslib: 2.8.1
 
   webextension-polyfill-ts@0.25.0:
     dependencies:
```
