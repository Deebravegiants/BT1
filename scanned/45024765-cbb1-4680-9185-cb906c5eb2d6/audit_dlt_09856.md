# [?] fix(apps): Patch axios `GHSA-3p68-rc4w-qgx5` and `GHSA-q4gf-8mx6-v5v3` (#11217)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-04-13
Source: https://github.com/iotaledger/iota/commit/cdc2c4c4260a2dfa25fa28a06ff9fffcd355b1d4
Type: security-commit

## Details
fix(apps): Patch axios `GHSA-3p68-rc4w-qgx5` and `GHSA-q4gf-8mx6-v5v3` (#11217)

Fixes
https://github.com/iotaledger/iota/actions/runs/24213971808/job/70689796179#step:6:23

## Patch
### apps/wallet-dashboard/package.json
```diff
@@ -34,7 +34,7 @@
         "bignumber.js": "^9.1.1",
         "clsx": "^2.1.1",
         "formik": "^2.4.2",
-        "next": "^15.5.11",
+        "next": "^15.5.15",
         "react": "^18.3.1",
         "react-error-boundary": "^4.0.10",
         "zustand": "^4.4.1"
```

### apps/wallet/package.json
```diff
@@ -116,7 +116,7 @@
         "@sentry/browser": "^7.120.3",
         "@tanstack/react-query": "^5.50.1",
         "@tanstack/react-query-persist-client": "^5.40.1",
-        "axios": "^1.13.5",
+        "axios": "^1.15.0",
         "bignumber.js": "^9.1.1",
         "buffer": "^6.0.3",
         "class-variance-authority": "^0.7.0",
```

### docs/site/package.json
```diff
@@ -45,7 +45,7 @@
     "@saucelabs/theme-github-codeblock": "^0.3.0",
     "@tanstack/react-query": "^5.50.1",
     "autoprefixer": "^10.4.19",
-    "axios": "^1.13.5",
+    "axios": "^1.15.0",
     "clsx": "^2.1.1",
     "docusaurus-plugin-openapi-docs": "^4.3.7",
     "docusaurus-plugin-sass": "^0.2.3",
```

### package.json
```diff
@@ -53,7 +53,7 @@
 			"minimatch@>=5.0.0": "^5.1.9",
 			"minimatch@>=9.0.0": "^9.0.9",
 			"hono@<4.12.4": ">=4.12.4",
-			"axios@<0.30.3": "^0.30.3",
+			"axios@<1.15.0": "^1.15.0",
 			"socket.io-parser@<4.2.6": "4.2.6",
 			"picomatch@<2.3.2": "^2.3.2",
 			"picomatch@>=4.0.0 <4.0.4": "^4.0.4",
```

### pnpm-lock.yaml
```diff
@@ -26,7 +26,7 @@ overrides:
   minimatch@>=5.0.0: ^5.1.9
   minimatch@>=9.0.0: ^9.0.9
   hono@<4.12.4: '>=4.12.4'
-  axios@<0.30.3: ^0.30.3
+  axios@<1.15.0: ^1.15.0
   socket.io-parser@<4.2.6: 4.2.6
   picomatch@<2.3.2: ^2.3.2
   picomatch@>=4.0.0 <4.0.4: ^4.0.4
@@ -894,8 +894,8 @@ importers:
         specifier: ^5.40.1
         version: 5.56.2(@tanstack/react-query@5.56.2(react@18.3.1))(react@18.3.1)
       axios:
-        specifier: ^1.13.5
-        version: 1.13.5(debug@4.3.7)
+        specifier: ^1.15.0
+        version: 1.15.0(debug@4.3.7)
       bignumber.js:
         specifier: ^9.1.1
         version: 9.1.2
@@ -1124,7 +1124,7 @@ importers:
         version: link:../../sdk/wallet-standard
       '@sentry/nextjs':
         specifier: ^10.40.0
-        version: 10.40.0(@opentelemetry/context-async-hooks@2.5.1(@opentelemetry/api@1.9.0))(@opentelemetry/core@2.5.1(@opentelemetry/api@1.9.0))(@opentelemetry/sdk-trace-base@2.5.1(@opentelemetry/api@1.9.0))(next@15.5.11(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0))(react@18.3.1)(webpack@5.95.0(@swc/core@1.15.11(@swc/helpers@0.5.18)))
+        version: 10.40.0(@opentelemetry/context-async-hooks@2.5.1(@opentelemetry/api@1.9.0))(@opentelemetry/core@2.5.1(@opentelemetry/api@1.9.0))(@opentelemetry/sdk-trace-base@2.5.1(@opentelemetry/api@1.9.0))(next@15.5.15(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0))(react@18.3.1)(webpack@5.95.0(@swc/core@1.15.11(@swc/helpers@0.5.18)))
       '@tanstack/react-query':
         specifier: ^5.50.1
         version: 5.56.2(react@18.3.1)
@@ -1138,8 +1138,8 @@ importers:
         specifier: ^2.4.2
         version: 2.4.6(react@18.3.1)
       next:
-        specifier: ^15.5.11
-        version: 15.5.11(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0)
+        specifier: ^15.5.15
+        version: 15.5.15(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0)
       react:
         specifier: ^18.3.1
         version: 18.3.1
@@ -1478,8 +1478,8 @@ importers:
         specifier: ^10.4.19
         version: 10.4.20(postcss@8.4.47)
       axios:
-        specifier: ^1.13.5
-        version: 1.13.5(debug@4.3.7)
+        specifier: ^1.15.0
+        version: 1.15.0(debug@4.3.7)
       clsx:
         specifier: ^2.1.1
         version: 2.1.1
@@ -1938,8 +1938,8 @@ importers:
         specifier: ^24.0.0
         version: 24.10.12
       axios:
-        specifier: ^1.13.5
-        version: 1.13.5(debug@4.3.7)
+        specifier: ^1.15.0
+        version: 1.15.0(debug@4.3.7)
       size-limit:
         specifier: ^11.1.4
         version: 11.1.5
@@ -6713,60 +6713,60 @@ packages:
       '@nestjs/platform-express':
         optional: true
 
-  '@next/env@15.5.11':
-    resolution: {integrity: sha512-g9s5SS9gC7GJCEOR3OV3zqs7C5VddqxP9X+/6BpMbdXRkqsWfFf2CJPBZNvNEtAkKTNuRgRXAgNxSAXzfLdaTg==}
+  '@next/env@15.5.15':
+    resolution: {integrity: sha512-vcmyu5/MyFzN7CdqRHO3uHO44p/QPCZkuTUXroeUmhNP8bL5PHFEhik22JUazt+CDDoD6EpBYRCaS2pISL+/hg==}
 
   '@next/eslint-plugin-next@14.2.3':
     resolution: {integrity: sha512-L3oDricIIjgj1AVnRdRor21gI7mShlSwU/1ZGHmqM3LzHhXXhdkrfeNY5zif25Bi5Dd7fiJHsbhoZCHfXYvlAw==}
 
-  '@next/swc-darwin-arm64@15.5.7':
-    resolution: {integrity: sha512-IZwtxCEpI91HVU/rAUOOobWSZv4P2DeTtNaCdHqLcTJU4wdNXgAySvKa/qJCgR5m6KI8UsKDXtO2B31jcaw1Yw==}
+  '@next/swc-darwin-arm64@15.5.15':
+    resolution: {integrity: sha512-6PvFO2Tzt10GFK2Ro9tAVEtacMqRmTarYMFKAnV2vYMdwWc73xzmDQyAV7SwEdMhzmiRoo7+m88DuiXlJlGeaw==}
     engines: {node: '>= 10'}
     cpu: [arm64]
     os: [darwin]
 
-  '@next/swc-darwin-x64@15.5.7':
-    resolution: {integrity: sha512-UP6CaDBcqaCBuiq/gfCEJw7sPEoX1aIjZHnBWN9v9qYHQdMKvCKcAVs4OX1vIjeE+tC5EIuwDTVIoXpUes29lg==}
+  '@next/swc-darwin-x64@15.5.15':
+    resolution: {integrity: sha512-G+YNV+z6FDZTp/+IdGyIMFqalBTaQSnvAA+X/hrt+eaTRFSznRMz9K7rTmzvM6tDmKegNtyzgufZW0HwVzEqaQ==}
     engines: {node: '>= 10'}
     cpu: [x64]
     os: [darwin]
 
-  '@next/swc-linux-arm64-gnu@15.5.7':
-    resolution: {integrity: sha512-NCslw3GrNIw7OgmRBxHtdWFQYhexoUCq+0oS2ccjyYLtcn1SzGzeM54jpTFonIMUjNbHmpKpziXnpxhSWLcmBA==}
+  '@next/swc-linux-arm64-gnu@15.5.15':
+    resolution: {integrity: sha512-eVkrMcVIBqGfXB+QUC7jjZ94Z6uX/dNStbQFabewAnk13Uy18Igd1YZ/GtPRzdhtm7QwC0e6o7zOQecul4iC1w==}
     engines: {node: '>= 10'}
     cpu: [arm64]
     os: [linux]
     libc: [glibc]
 
-  '@next/swc-linux-arm64-musl@15.5.7':
-    resolution: {integrity: sha512-nfymt+SE5cvtTrG9u1wdoxBr9bVB7mtKTcj0ltRn6gkP/2Nu1zM5ei8rwP9qKQP0Y//umK+TtkKgNtfboBxRrw==}
+  '@next/swc-linux-arm64-musl@15.5.15':
+    resolution: {integrity: sha512-RwSHKMQ7InLy5GfkY2/n5PcFycKA08qI1VST78n09nN36nUPqCvGSMiLXlfUmzmpQpF6XeBYP2KRWHi0UW3uNg==}
     engines: {node: '>= 10'}
     cpu: [arm64]
     os: [linux]
     libc: [musl]
 
-  '@next/swc-linux-x64-gnu@15.5.7':
-    resolution: {integrity: sha512-hvXcZvCaaEbCZcVzcY7E1uXN9xWZfFvkNHwbe/n4OkRhFWrs1J1QV+4U1BN06tXLdaS4DazEGXwgqnu/VMcmqw==}
+  '@next/swc-linux-x64-gnu@15.5.15':
+    resolution: {integrity: sha512-nplqvY86LakS+eeiuWsNWvfmK8pFcOEW7ZtVRt4QH70lL+0x6LG/m1OpJ/tvrbwjmR8HH9/fH2jzW1GlL03TIg==}
     engines: {node: '>= 10'}
     cpu: [x64]
     os: [linux]
     libc: [glibc]
 
-  '@next/swc-linux-x64-musl@15.5.7':
-    resolution: {integrity: sha512-4IUO539b8FmF0odY6/SqANJdgwn1xs1GkPO5doZugwZ3ETF6JUdckk7RGmsfSf7ws8Qb2YB5It33mvNL/0acqA==}
+  '@next/swc-linux-x64-musl@15.5.15':
+    resolution: {integrity: sha512-eAgl9NKQ84/sww0v81DQINl/vL2IBxD7sMybd0cWRw6wqgouVI53brVRBrggqBRP/NWeIAE1dm5cbKYoiMlqDQ==}
     engines: {node: '>= 10'}
     cpu: [x64]
     os: [linux]
     libc: [musl]
 
-  '@next/swc-win32-arm64-msvc@15.5.7':
-    resolution: {integrity: sha512-CpJVTkYI3ZajQkC5vajM7/ApKJUOlm6uP4BknM3XKvJ7VXAvCqSjSLmM0LKdYzn6nBJVSjdclx8nYJSa3xlTgQ==}
+  '@next/swc-win32-arm64-msvc@15.5.15':
+    resolution: {integrity: sha512-GJVZC86lzSquh0MtvZT+L7G8+jMnJcldloOjA8Kf3wXvBrvb6OGe2MzPuALxFshSm/IpwUtD2mIoof39ymf52A==}
     engines: {node: '>= 10'}
     cpu: [arm64]
     os: [win32]
 
-  '@next/swc-win32-x64-msvc@15.5.7':
-    resolution: {integrity: sha512-gMzgBX164I6DN+9/PGA+9dQiwmTkE4TloBNx8Kv9UiGARsr9Nba7IpcBRA1iTV9vwlYnrE3Uy6I7Aj6qLjQuqw==}
+  '@next/swc-win32-x64-msvc@15.5.15':
+    resolution: {integrity: sha512-nFucjVdwlFqxh/JG3hWSJ4p8+YJV7Ii8aPDuBQULB6DzUF4UNZETXLfEUk+oI2zEznWWULPt7MeuTE6xtK1HSA==}
     engines: {node: '>= 10'}
     cpu: [x64]
     os: [win32]
@@ -11494,16 +11494,10 @@ packages:
   axios-retry@4.5.0:
     resolution: {integrity: sha512-aR99oXhpEDGo0UuAlYcn2iGRds30k366Zfa05XWScR9QaQD4JYiP3/1Qt1u7YlefUOK+cn0CcwoL1oefavQUlQ==}
     peerDependencies:
-      axios: ^0.30.3
+      axios: ^1.15.0
 
-  axios@0.30.3:
-    resolution: {integrity: sha512-5/tmEb6TmE/ax3mdXBc/Mi6YdPGxQsv+0p5YlciXWt3PHIn0VamqCXhRMtScnwY3lbgSXLneOuXAKUhgmSRpwg==}
-
-  axios@1.11.0:
-    resolution: {integrity: sha512-1Lx3WLFQWm3ooKDYZD1eXmoGO9fxYQjrycfHFC8P0sCfQVXyROp0p9PFWBehewBOdCwHc+f/b8I0fMto5eSfwA==}
-
-  axios@1.13.5:
-    resolution: {integrity: sha512-cz4ur7Vb0xS4/KUN0tPWe44eqxrIu31me+fbang3ijiNscE129POzipJJA6zniq2C/Z6sJCjMimjS8Lc/GAs8Q==}
+  axios@1.15.0:
+    resolution: {integrity: sha512-wWyJDlAatxk30ZJer+GeCWS209sA42X+N5jU2jy6oHTp7ufw8uzUTVFBX9+wTfAlhiJXGS0Bq7X6efruWjuK9Q==}
 
   axobject-query@4.1.0:
     resolution: {integrity: sha512-qIj0G9wZbMGNLjLmg1PT6v2mE9AH2zlnADJD/2tC6E00hgmhUOfEB6greHPAfLRSufHqROIUTkw6E+M3lH0PTQ==}
@@ -14144,15 +14138,6 @@ packages:
       debug:
         optional: true
 
-  follow-redirects@1.15.9:
-    resolution: {integrity: sha512-gew4GsXizNgdoRyqmyfMHyAmXsZDk6mHkSxZFCzW9gwlbtOW44CDtYavM+y+72qD/Vq2l550kMF52DT8fOLJqQ==}
-    engines: {node: '>=4.0'}
-    peerDependencies:
-      debug: '*'
-    peerDependenciesMeta:
-      debug:
-        optional: true
-
   for-each@0.3.5:
     resolution: {integrity: sha512-dKx12eRCVIzqCxFGplyFKJMPvLEWgmNtUrpTiJIR5u97zEhRG8ySrtboPHZXx7daLxQVrl643cTzbab2tkQjxg==}
     engines: {node: '>= 0.4'}
@@ -16969,8 +16954,8 @@ packages:
     resolution: {integrity: sha512-HZpdkco+JeXq0G+WWpMJ4NsX3pqb5O7eR9uGz3FfoFt+LYzU8iRWp49nJtud6hsDoywM8tIrDo3gjgmOqJA8LA==}
     engines: {node: '>= 10'}
 
-  next@15.5.11:
-    resolution: {integrity: sha512-L2KPiKmqTDpRdeVDdPjhf43g2/VPe0NCNndq7OKDCgOLWtxe1kbr/zXGIZtYY7kZEAjRf7Bj/mwUFSr+tYC2Yg==}
+  next@15.5.15:
+    resolution: {integrity: sha512-VSqCrJwtLVGwAVE0Sb/yikrQfkwkZW9p+lL/J4+xe+G3ZA+QnWPqgcfH1tDUEuk9y+pthzzVFp4L/U8JerMfMQ==}
     engines: {node: ^18.18.0 || ^19.8.0 || >= 20.0.0}
     hasBin: true
     peerDependencies:
@@ -18605,6 +18590,10 @@ packages:
   proxy-from-env@1.1.0:
     resolution: {integrity: sha512-D+zkORCbA9f1tdWRK0RaCR3GPv50cMxcrz4X8k5LTSUD1Dkw47mKJEZQNunItRTkWwgtaUSo1RVFRIG9ZXiFYg==}
 
+  proxy-from-env@2.1.0:
+    resolution: {integrity: sha512-cJ+oHTW1VAEa8cJslgmUZrc+sjRKgAKl3Zyse6+PV38hZe/V6Z14TbCuXcan9F9ghlz4QrFr2c92TNF82UkYHA==}
+    engines: {node: '>=10'}
+
   ps-tree@1.2.0:
     resolution: {integrity: sha512-0VnamPPYHl4uaU/nSFeZZpR21QAWRz+sRv4iW9+v/GS/J5U5iZB5BNN6J0RMoOvdx2gWM2+ZFMIm58q24e4UYA==}
     engines: {node: '>= 0.10'}
@@ -24483,8 +24472,8 @@ snapshots:
       '@solana/kit': 5.4.0(bufferutil@4.0.9)(typescript@5.8.3)(utf-8-validate@5.0.10)
       '@solana/web3.js': 1.98.4(bufferutil@4.0.9)(typescript@5.8.3)(utf-8-validate@5.0.10)
       abitype: 1.0.6(typescript@5.8.3)(zod@3.25.76)
-      axios: 1.13.5(debug@4.3.7)
-      axios-retry: 4.5.0(axios@1.13.5)
+      axios: 1.15.0(debug@4.3.7)
+      axios-retry: 4.5.0(axios@1.15.0)
       jose: 6.1.3
       md5: 2.3.0
       uncrypto: 0.1.3
@@ -28022,7 +28011,7 @@ snapshots:
       '@ledgerhq/errors': 6.26.0
       '@ledgerhq/hw-transport': 6.31.12
       '@ledgerhq/logs': 6.13.0
-      axios: 1.11.0
+      axios: 1.15.0(debug@4.3.7)
       rxjs: 7.8.1
     transitivePeerDependencies:
       - debug
@@ -28691,34 +28680,34 @@ snapshots:
     optionalDependencies:
       '@nestjs/platform-express': 11.1.12(@nestjs/common@11.1.12(class-validator@0.14.3)(reflect-metadata@0.2.2)(rxjs@7.8.1))(@nestjs/core@11.1.12)
 
-  '@next/env@15.5.11': {}
+  '@next/env@15.5.15': {}
 
   '@next/eslint-plugin-next@14.2.3':
     dependencies:
       glob: 10.5.0
 
-  '@next/swc-darwin-arm64@15.5.7':
+  '@next/swc-darwin-arm64@15.5.15':
     optional: true
 
-  '@next/swc-darwin-x64@15.5.7':
+  '@next/swc-darwin-x64@15.5.15':
     optional: true
 
-  '@next/swc-linux-arm64-gnu@15.5.7':
+  '@next/swc-linux-arm64-gnu@15.5.15':
     optional: true
 
-  '@next/swc-linux-arm64-musl@15.5.7':
+  '@next/swc-linux-arm64-musl@15.5.15':
     optional: true
 
-  '@next/swc-linux-x64-gnu@15.5.7':
+  '@next/swc-linux-x64-gnu@15.5.15':
     optional: true
 
-  '@next/swc-linux-x64-musl@15.5.7':
+  '@next/swc-linux-x64-musl@15.5.15':
     optional: true
 
-  '@next/swc-win32-arm64-msvc@15.5.7':
+  '@next/swc-win32-arm64-msvc@15.5.15':
     optional: true
 
-  '@next/swc-win32-x64-msvc@15.5.7':
+  '@next/swc-win32-x64-msvc@15.5.15':
     optional: true
 
   '@ngraveio/bc-ur@1.1.13':
@@ -31208,7 +31197,7 @@ snapshots:
       '@sentry/types': 6.19.7
       tslib: 1.14.1
 
-  '@sentry/nextjs@10.40.0(@opentelemetry/context-async-hooks@2.5.1(@opentelemetry/api@1.9.0))(@opentelemetry/core@2.5.1(@opentelemetry/api@1.9.0))(@opentelemetry/sdk-trace-base@2.5.1(@opentelemetry/api@1.9.0))(next@15.5.11(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0))(react@18.3.1)(webpack@5.95.0(@swc/core@1.15.11(@swc/helpers@0.5.18)))':
+  '@sentry/nextjs@10.40.0(@opentelemetry/context-async-hooks@2.5.1(@opentelemetry/api@1.9.0))(@opentelemetry/core@2.5.1(@opentelemetry/api@1.9.0))(@opentelemetry/sdk-trace-base@2.5.1(@opentelemetry/api@1.9.0))(next@15.5.15(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0))(react@18.3.1)(webpack@5.95.0(@swc/core@1.15.11(@swc/helpers@0.5.18)))':
     dependencies:
       '@opentelemetry/api': 1.9.0
       '@opentelemetry/semantic-conventions': 1.40.0
@@ -31221,7 +31210,7 @@ snapshots:
       '@sentry/react': 10.40.0(react@18.3.1)
       '@sentry/vercel-edge': 10.40.0
       '@sentry/webpack-plugin': 5.1.1(webpack@5.95.0(@swc/core@1.15.11(@swc/helpers@0.5.18)))
-      next: 15.5.11(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0)
+      next: 15.5.15(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0)
       rollup: 4.59.0
       stacktrace-parser: 0.1.10
     transitivePeerDependencies:
@@ -33308,7 +33297,7 @@ snapshots:
   '@types/node-fetch@2.6.11':
     dependencies:
       '@types/node': 24.10.12
-      form-data: 4.0.4
+      form-data: 4.0.5
 
   '@types/node-forge@1.3.14':
     dependencies:
@@ -33447,7 +33436,7 @@ snapshots:
       '@types/cookiejar': 2.1.5
       '@types/methods': 1.1.4
       '@types/node': 24.10.12
-      form-data: 4.0.4
+      form-data: 4.0.5
 
   '@types/supertest@6.0.2':
     dependencies:
@@ -35416,32 +35405,16 @@ snapshots:
 
   axe-core@4.10.0: {}
 
-  axios-retry@4.5.0(axios@1.13.5):
+  axios-retry@4.5.0(axios@1.15.0):
     dependencies:
-      axios: 1.13.5(debug@4.3.7)
+      axios: 1.15.0(debug@4.3.7)
       is-retry-allowed: 2.2.0
 
-  axios@0.30.3:
+  axios@1.15.0(debug@4.3.7):
     dependencies:
       follow-redirects: 1.15.11(debug@4.3.7)
       form-data: 4.0.5
-      proxy-from-env: 1.1.0
-    transitivePeerDependencies:
-      - debug
-
-  axios@1.11.0:
-    dependencies:
-      follow-redirects: 1.15.9
-      form-data: 4.0.4
-      proxy-from-env: 1.1.0
-    transitivePeerDependencies:
-      - debug
-
-  axios@1.13.5(debug@4.3.7):
-    dependencies:
-      follow-redirects: 1.15.11(debug@4.3.7)
-      form-data: 4.0.5
-      proxy-from-env: 1.1.0
+      proxy-from-env: 2.1.0
     transitivePeerDependencies:
       - debug
 
@@ -35648,7 +35621,7 @@ snapshots:
 
   binary-install@1.1.0:
     dependencies:
-      axios: 0.30.3
+      axios: 1.15.0(debug@4.3.7)
       rimraf: 3.0.2
       tar: 6.2.1
     transitivePeerDependencies:
@@ -38854,8 +38827,6 @@ snapshots:
     optionalDependencies:
       debug: 4.3.7
 
-  follow-redirects@1.15.9: {}
-
   for-each@0.3.5:
     dependencies:
       is-callable: 1.2.7
@@ -42626,24 +42597,24 @@ snapshots:
 
   neotraverse@0.6.15: {}
 
-  next@15.5.11(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0):
+  next@15.5.15(@babel/core@7.26.10)(@opentelemetry/api@1.9.0)(@playwright/test@1.56.1)(babel-plugin-macros@3.1.0)(react-dom@18.3.1(react@18.3.1))(react@18.3.1)(sass@1.86.0):
     dependencies:
-      '@next/env': 15.5.11
+      '@next/env': 15.5.15
       '@swc/helpers': 0.5.15
-      caniuse-lite: 1.0.30001707
+      caniuse-lite: 1.0.30001770
       postcss: 8.4.31
       react: 18.3.1
       react-dom: 18.3.1(react@18.3.1)
       styled-jsx: 5.1.6(@babel/core@7.26.10)(babel-plugin-macros@3.1.0)(react@18.3.1)
     optionalDependencies:
-      '@next/swc-darwin-arm64': 15.5.7
-      '@next/swc-darwin-x64': 15.5.7
-      '@next/swc-linux-arm64-gnu': 15.5.7
-      '@next/swc-linux-arm64-musl': 15.5.7
-      '@next/swc-linux-x64-gnu': 15.5.7
-      '@next/swc-linux-x64-musl': 15.5.7
-      '@next/swc-win32-arm64-msvc': 15.5.7
-      '@next/swc-win32-x64-msvc': 15.5.7
+      '@next/swc-darwin-arm64': 15.5.15
+      '@next/swc-darwin-x64': 15.5.15
+      '@next/swc-linux-arm64-gnu': 15.5.15
+      '@next/swc-linux-arm64-musl': 15.5.15
+      '@next/swc-linux-x64-gnu': 15.5.15
+      '@next/swc-linux-x64-musl': 15.5.15
+      '@next/swc-win32-arm64-msvc': 15.5.15
+      '@next/swc-win32-x64-msvc': 15.5.15
       '@opentelemetry/api': 1.9.0
       '@playwright/test': 1.56.1
       sass: 1.86.0
@@ -44312,7 +44283,7 @@ snapshots:
 
   postcss@8.4.31:
     dependencies:
-      nanoid: 3.3.8
+      nanoid: 3.3.11
       picocolors: 1.1.1
       source-map-js: 1.2.1
 
@@ -44466,6 +44437,8 @@ snapshots:
 
   proxy-from-env@1.1.0: {}
 
+  proxy-from-env@2.1.0: {}
+
   ps-tree@1.2.0:
     dependencies:
       event-stream: 3.3.4
@@ -46424,7 +46397,7 @@ snapshots:
       cookiejar: 2.1.4
       debug: 4.4.1(supports-color@8.1.1)
       fast-safe-stringify: 2.1.1
-      form-data: 4.0.4
+      form-data: 4.0.5
       formidable: 2.1.2
       methods: 1.1.2
       mime: 2.6.0
@@ -48089,7 +48062,7 @@ snapshots:
 
   wait-on@8.0.1(debug@4.3.7):
     dependencies:
-      axios: 1.13.5(debug@4.3.7)
+      axios: 1.15.0(debug@4.3.7)
       joi: 17.13.3
       lodash: 4.18.1
       minimist: 1.2.8
```

### pnpm-workspace.yaml
```diff
@@ -32,4 +32,3 @@ packages:
   - "!sdk/examples/src/**/build"
 minimumReleaseAge: 2880
 blockExoticSubdeps: true
-trustPolicy: no-downgrade
```

### sdk/ledgerjs-hw-app-iota/package.json
```diff
@@ -65,7 +65,7 @@
         "@ledgerhq/hw-transport-node-speculos-http": "^6.30.2",
         "@size-limit/preset-small-lib": "^11.1.4",
         "@types/node": "^24.0.0",
-        "axios": "^1.13.5",
+        "axios": "^1.15.0",
         "size-limit": "^11.1.4",
         "typescript": "^5.5.3",
         "vitest": "^3.2.4"
```
