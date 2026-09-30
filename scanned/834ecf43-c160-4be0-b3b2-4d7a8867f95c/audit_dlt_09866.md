# [?] fix: Patch vitest `GHSA-9crc-q9x8-hgqq` (#5186)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-02-04
Source: https://github.com/iotaledger/iota/commit/3458f56884868834c2b7d6de509c1c210f8045a8
Type: security-commit

## Details
fix: Patch vitest `GHSA-9crc-q9x8-hgqq` (#5186)

## Patch
### apps/core/package.json
```diff
@@ -55,6 +55,6 @@
         "tailwindcss": "^3.3.3",
         "typescript": "^5.5.3",
         "vite": "^5.3.3",
-        "vitest": "^2.0.1"
+        "vitest": "^2.1.9"
     }
 }
```

### apps/explorer/package.json
```diff
@@ -95,7 +95,7 @@
         "typescript": "^5.5.3",
         "vite": "^5.3.3",
         "vite-plugin-svgr": "^3.2.0",
-        "vitest": "^2.0.1"
+        "vitest": "^2.1.9"
     },
     "browserslist": {
         "production": [
```

### apps/wallet/package.json
```diff
@@ -80,7 +80,7 @@
         "typescript": "^5.5.3",
         "vite": "^5.3.3",
         "vite-tsconfig-paths": "^4.2.0",
-        "vitest": "^2.0.1",
+        "vitest": "^2.1.9",
         "web-ext": "^8.3.0",
         "webpack": "^5.79.0",
         "webpack-cli": "^5.0.1",
```

### pnpm-lock.yaml
```diff
@@ -312,8 +312,8 @@ importers:
         specifier: ^5.3.3
         version: 5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0)
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
 
   apps/explorer:
     dependencies:
@@ -509,7 +509,7 @@ importers:
         version: 4.3.1(vite@5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0))
       '@vitest/ui':
         specifier: ^0.33.0
-        version: 0.33.0(vitest@2.1.1)
+        version: 0.33.0(vitest@2.1.9)
       autoprefixer:
         specifier: ^10.4.19
         version: 10.4.20(postcss@8.4.47)
@@ -541,8 +541,8 @@ importers:
         specifier: ^3.2.0
         version: 3.3.0(rollup@4.30.1)(typescript@5.6.2)(vite@5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0))
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
 
   apps/ui-icons:
     devDependencies:
@@ -996,8 +996,8 @@ importers:
         specifier: ^4.2.0
         version: 4.3.2(typescript@5.6.2)(vite@5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0))
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
       web-ext:
         specifier: ^8.3.0
         version: 8.3.0(body-parser@1.20.3)
@@ -1533,8 +1533,8 @@ importers:
         specifier: ^5.5.3
         version: 5.6.2
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
 
   sdk/build-scripts:
     dependencies:
@@ -1674,8 +1674,8 @@ importers:
         specifier: ^5.3.3
         version: 5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0)
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
 
   sdk/graphql-transport:
     dependencies:
@@ -1729,8 +1729,8 @@ importers:
         specifier: ^5.5.3
         version: 5.6.2
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
       wait-on:
         specifier: ^7.2.0
         version: 7.2.0
@@ -1763,8 +1763,8 @@ importers:
         specifier: ^5.3.3
         version: 5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0)
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
       wait-on:
         specifier: ^7.2.0
         version: 7.2.0
@@ -1803,8 +1803,8 @@ importers:
         specifier: ^5.5.3
         version: 5.6.2
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
 
   sdk/move-bytecode-template:
     devDependencies:
@@ -1818,8 +1818,8 @@ importers:
         specifier: ^5.5.3
         version: 5.6.2
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
       wasm-pack:
         specifier: ^0.13.0
         version: 0.13.0
@@ -1921,8 +1921,8 @@ importers:
         specifier: ^5.3.3
         version: 5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0)
       vitest:
-        specifier: ^2.0.1
-        version: 2.1.1(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+        specifier: ^2.1.9
+        version: 2.1.9(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
       wait-on:
         specifier: ^7.2.0
         version: 7.2.0
@@ -7621,13 +7621,13 @@ packages:
   '@vitest/expect@2.0.5':
     resolution: {integrity: sha512-yHZtwuP7JZivj65Gxoi8upUN2OzHTi3zVfjwdpu2WrvCZPLwsJ2Ey5ILIPccoW23dd/zQBlJ4/dhi7DWNyXCpA==}
 
-  '@vitest/expect@2.1.1':
-    resolution: {integrity: sha512-YeueunS0HiHiQxk+KEOnq/QMzlUuOzbU1Go+PgAsHvvv3tUkJPm9xWt+6ITNTlzsMXUjmgm5T+U7KBPK2qQV6w==}
+  '@vitest/expect@2.1.9':
+    resolution: {integrity: sha512-UJCIkTBenHeKT1TTlKMJWy1laZewsRIzYighyYiJKZreqtdxSos/S1t+ktRMQWu2CKqaarrkeszJx1cgC5tGZw==}
 
-  '@vitest/mocker@2.1.1':
-    resolution: {integrity: sha512-LNN5VwOEdJqCmJ/2XJBywB11DLlkbY0ooDJW3uRX5cZyYCrc4PI/ePX0iQhE3BiEGiQmK4GE7Q/PqCkkaiPnrA==}
+  '@vitest/mocker@2.1.9':
+    resolution: {integrity: sha512-tVL6uJgoUdi6icpxmdrn5YNo3g3Dxv+IHJBr0GXHaEdTcw3F+cPKnsXFhli6nO+f/6SDKPHEK1UN+k+TQv0Ehg==}
     peerDependencies:
-      msw: ^2.3.5
+      msw: ^2.4.9
       vite: ^5.0.0
     peerDependenciesMeta:
       msw:
@@ -7641,17 +7641,20 @@ packages:
   '@vitest/pretty-format@2.1.1':
     resolution: {integrity: sha512-SjxPFOtuINDUW8/UkElJYQSFtnWX7tMksSGW0vfjxMneFqxVr8YJ979QpMbDW7g+BIiq88RAGDjf7en6rvLPPQ==}
 
-  '@vitest/runner@2.1.1':
-    resolution: {integrity: sha512-uTPuY6PWOYitIkLPidaY5L3t0JJITdGTSwBtwMjKzo5O6RCOEncz9PUN+0pDidX8kTHYjO0EwUIvhlGpnGpxmA==}
+  '@vitest/pretty-format@2.1.9':
+    resolution: {integrity: sha512-KhRIdGV2U9HOUzxfiHmY8IFHTdqtOhIzCpd8WRdJiE7D/HUcZVD0EgQCVjm+Q9gkUXWgBvMmTtZgIG48wq7sOQ==}
 
-  '@vitest/snapshot@2.1.1':
-    resolution: {integrity: sha512-BnSku1WFy7r4mm96ha2FzN99AZJgpZOWrAhtQfoxjUU5YMRpq1zmHRq7a5K9/NjqonebO7iVDla+VvZS8BOWMw==}
+  '@vitest/runner@2.1.9':
+    resolution: {integrity: sha512-ZXSSqTFIrzduD63btIfEyOmNcBmQvgOVsPNPe0jYtESiXkhd8u2erDLnMxmGrDCwHCCHE7hxwRDCT3pt0esT4g==}
+
+  '@vitest/snapshot@2.1.9':
+    resolution: {integrity: sha512-oBO82rEjsxLNJincVhLhaxxZdEtV0EFHMK5Kmx5sJ6H9L183dHECjiefOAdnqpIgT5eZwT04PoggUnW88vOBNQ==}
 
   '@vitest/spy@2.0.5':
     resolution: {integrity: sha512-c/jdthAhvJdpfVuaexSrnawxZz6pywlTPe84LUB2m/4t3rl2fTo9NFGBG4oWgaD+FTgDDV8hJ/nibT7IfH3JfA==}
 
-  '@vitest/spy@2.1.1':
-    resolution: {integrity: sha512-ZM39BnZ9t/xZ/nF4UwRH5il0Sw93QnZXd9NAZGRpIgj0yvVwPpLd702s/Cx955rGaMlyBQkZJ2Ir7qyY48VZ+g==}
+  '@vitest/spy@2.1.9':
+    resolution: {integrity: sha512-E1B35FwzXXTs9FHNK6bDszs7mtydNi5MIfUWpceJ8Xbfb1gBMscAnwLbEu+B44ed6W3XjL9/ehLPHR1fkf1KLQ==}
 
   '@vitest/ui@0.33.0':
     resolution: {integrity: sha512-7gbAjLqt30R4bodkJAutdpy4ncv+u5IKTHYTow1c2q+FOxZUC9cKOSqMUxjwaaTwLN+EnDnmXYPtg3CoahaUzQ==}
@@ -7667,6 +7670,9 @@ packages:
   '@vitest/utils@2.1.1':
     resolution: {integrity: sha512-Y6Q9TsI+qJ2CC0ZKj6VBb+T8UPz593N113nnUykqwANqhgf3QkZeHFlusgKLTqrnVHbj/XDKZcDHol+dxVT+rQ==}
 
+  '@vitest/utils@2.1.9':
+    resolution: {integrity: sha512-v0psaMSkNJ3A2NMrUEHFRzJtDPFn+/VWZ5WxImB21T9fjucJRmS7xCS3ppEnARb9y11OAzaD+P2Ps+b+BGX5iQ==}
+
   '@volar/language-core@2.4.11':
     resolution: {integrity: sha512-lN2C1+ByfW9/JRPpqScuZt/4OrUUse57GLI6TbLgTIqBVemdl1wNcZ1qYGEo2+Gw8coYLgCy7SuKqn6IrQcQgg==}
 
@@ -8496,6 +8502,10 @@ packages:
     resolution: {integrity: sha512-pT1ZgP8rPNqUgieVaEY+ryQr6Q4HXNg8Ei9UnLUrjN4IA7dvQC5JB+/kxVcPNDHyBcc/26CXPkbNzq3qwrOEKA==}
     engines: {node: '>=12'}
 
+  chai@5.1.2:
+    resolution: {integrity: sha512-aGtmf24DW6MLHHG5gCx4zaI3uBq3KRtxeVs0DjFH6Z0rDNbsvTxFASFvdj79pxjxZ8/5u3PIiN3IwEIQkiiuPw==}
+    engines: {node: '>=12'}
+
   chalk@2.4.2:
     resolution: {integrity: sha512-Mti+f9lpJNcwF4tWV8/OrTTtF1gZi+f8FqlyAdouralcFWFQWF2+NgCHShjkCb+IFBLq9buZwE1xckQU4peSuQ==}
     engines: {node: '>=4'}
@@ -10111,6 +10121,10 @@ packages:
     resolution: {integrity: sha512-Zk/eNKV2zbjpKzrsQ+n1G6poVbErQxJ0LBOJXaKZ1EViLzH+hrLu9cdXI4zw9dBQJslwBEpbQ2P1oS7nDxs6jQ==}
     engines: {node: '>= 0.8.0'}
 
+  expect-type@1.1.0:
+    resolution: {integrity: sha512-bFi65yM+xZgk+u/KRIpekdSYkTB5W1pEf0Lt8Q8Msh7b+eQ7LXVtIB1Bkm4fvclDEL1b2CZkMhv2mOeF8tMdkA==}
+    engines: {node: '>=12.0.0'}
+
   expect@29.7.0:
     resolution: {integrity: sha512-2Zks0hf1VLFYI1kbh0I5jP3KHHyCHpkfyHBzsSXRFgl/Bg9mWYfMW8oD+PdMPlEwy5HNsR9JutYy6pMeOh61nw==}
     engines: {node: ^14.15.0 || ^16.10.0 || >=18.0.0}
@@ -12057,6 +12071,9 @@ packages:
   loupe@3.1.1:
     resolution: {integrity: sha512-edNu/8D5MKVfGVFRhFf8aAxiTM6Wumfz5XsaatSxlD3w4R1d/WEKUTydCdPGbl9K7QG/Ca3GnDV2sIKIpXRQcw==}
 
+  loupe@3.1.3:
+    resolution: {integrity: sha512-kkIp7XSkP78ZxJEsSxW3712C6teJVoeHHwgo9zJ380de7IYyJ2ISlxojcH2pC5OFLewESmnRi/+XCDIEEVyoug==}
+
   lower-case-first@2.0.2:
     resolution: {integrity: sha512-EVm/rR94FJTZi3zefZ82fLWab+GX14LJN4HrWBcuo6Evmsl9hEfnqxgcHCKb9q+mNf6EVdsjx/qucYFIIB84pg==}
 
@@ -12109,6 +12126,9 @@ packages:
   magic-string@0.30.11:
     resolution: {integrity: sha512-+Wri9p0QHMy+545hKww7YAu5NyzF8iomPL/RQazugQ9+Ez4Ic3mERMd8ZTX5rfK944j+560ZJi8iAwgak1Ac7A==}
 
+  magic-string@0.30.17:
+    resolution: {integrity: sha512-sNPKHvyjVf7gyjwS4xGTaW/mCnF8wnjtifKBEhxfZ7E/S8tQ0rssrwGNn6q8JH/ohItJfSQp9mBtQYuTlH5QnA==}
+
   magic-string@0.30.8:
     resolution: {integrity: sha512-ISQTe55T2ao7XtlAStud6qwYPZjE4GK1S/BeVPus4jrq6JuOnQ00YKQC581RWhR122W7msZV263KzVeLoqidyQ==}
     engines: {node: '>=12'}
@@ -15011,6 +15031,9 @@ packages:
   std-env@3.7.0:
     resolution: {integrity: sha512-JPbdCEQLj1w5GilpiHAx3qJvFndqybBysA3qUOnznweH4QbNYUsW/ea8QzSrnh0vNsezMMw5bcVool8lM0gwzg==}
 
+  std-env@3.8.0:
+    resolution: {integrity: sha512-Bc3YwwCB+OzldMxOXJIIvC6cPRWr/LxOp48CdQTOkPyk/t4JWWJbrilwBd7RJzKV8QW7tJkcgAmeuLLJugl5/w==}
+
   stop-iteration-iterator@1.0.0:
     resolution: {integrity: sha512-iCGQj+0l0HOdZ2AEeBADlsRC+vsnDsZsbdSiH1yNSjcfKM7fdpCMfqAL/dwF5BLiw/XhRft/Wax6zQbhq2BcjQ==}
     engines: {node: '>= 0.4'}
@@ -15391,9 +15414,6 @@ packages:
   tinybench@2.9.0:
     resolution: {integrity: sha512-0+DUvqWMValLmha6lr4kD8iAMK1HzV0/aKnCtWb9v9641TnP/MFb7Pc2bxoxQjTXAErryXVgUOfv2YqNllqGeg==}
 
-  tinyexec@0.3.0:
-    resolution: {integrity: sha512-tVGE0mVJPGb0chKhqmsoosjsS+qUnJVGJpZgsHYQcGoPlG3B51R3PouqTgEGH2Dc9jjFyOqOpix6ZHNMXp1FZg==}
-
   tinyexec@0.3.2:
     resolution: {integrity: sha512-KQQR9yN7R5+OSwaK0XQoj22pwHoTlgYqmUscPYoknOoWCWfj/5/ABTMRi69FrKU5ffPVh5QcFikpWJI/P1ocHA==}
 
@@ -16116,8 +16136,8 @@ packages:
     engines: {node: ^18.0.0 || >=20.0.0}
     hasBin: true
 
-  vite-node@2.1.1:
-    resolution: {integrity: sha512-N/mGckI1suG/5wQI35XeR9rsMsPqKXzq1CdUndzVstBj/HvyxxGctwnK6WX43NGt5L3Z5tcRf83g4TITKJhPrA==}
+  vite-node@2.1.9:
+    resolution: {integrity: sha512-AM9aQ/IPrW/6ENLQg3AGY4K1N2TGZdR5e4gu/MmmR2xR3Ll1+dib+nook92g4TV3PXVyeyxdWwtaCAiUL0hMxA==}
     engines: {node: ^18.0.0 || >=20.0.0}
     hasBin: true
 
@@ -16175,15 +16195,15 @@ packages:
       terser:
         optional: true
 
-  vitest@2.1.1:
-    resolution: {integrity: sha512-97We7/VC0e9X5zBVkvt7SGQMGrRtn3KtySFQG5fpaMlS+l62eeXRQO633AYhSTC3z7IMebnPPNjGXVGNRFlxBA==}
+  vitest@2.1.9:
+    resolution: {integrity: sha512-MSmPM9REYqDGBI8439mA4mWhV5sKmDlBKWIYbA3lRb2PTHACE0mgKwA8yQ2xq9vxDTuk4iPrECBAEW2aoFXY0Q==}
     engines: {node: ^18.0.0 || >=20.0.0}
     hasBin: true
     peerDependencies:
       '@edge-runtime/vm': '*'
       '@types/node': ^18.0.0 || >=20.0.0
-      '@vitest/browser': 2.1.1
-      '@vitest/ui': 2.1.1
+      '@vitest/browser': 2.1.9
+      '@vitest/ui': 2.1.9
       happy-dom: '*'
       jsdom: '*'
     peerDependenciesMeta:
@@ -24527,27 +24547,27 @@ snapshots:
       chai: 5.1.1
       tinyrainbow: 1.2.0
 
-  '@vitest/expect@2.1.1':
+  '@vitest/expect@2.1.9':
     dependencies:
-      '@vitest/spy': 2.1.1
-      '@vitest/utils': 2.1.1
-      chai: 5.1.1
+      '@vitest/spy': 2.1.9
+      '@vitest/utils': 2.1.9
+      chai: 5.1.2
       tinyrainbow: 1.2.0
 
-  '@vitest/mocker@2.1.1(msw@2.4.9(typescript@5.6.2))(vite@5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0))':
+  '@vitest/mocker@2.1.9(msw@2.4.9(typescript@5.6.2))(vite@5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0))':
     dependencies:
-      '@vitest/spy': 2.1.1
+      '@vitest/spy': 2.1.9
       estree-walker: 3.0.3
-      magic-string: 0.30.11
+      magic-string: 0.30.17
     optionalDependencies:
       msw: 2.4.9(typescript@5.6.2)
       vite: 5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0)
 
-  '@vitest/mocker@2.1.1(msw@2.4.9(typescript@5.6.2))(vite@5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0))':
+  '@vitest/mocker@2.1.9(msw@2.4.9(typescript@5.6.2))(vite@5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0))':
     dependencies:
-      '@vitest/spy': 2.1.1
+      '@vitest/spy': 2.1.9
       estree-walker: 3.0.3
-      magic-string: 0.30.11
+      magic-string: 0.30.17
     optionalDependencies:
       msw: 2.4.9(typescript@5.6.2)
       vite: 5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0)
@@ -24560,26 +24580,30 @@ snapshots:
     dependencies:
       tinyrainbow: 1.2.0
 
-  '@vitest/runner@2.1.1':
+  '@vitest/pretty-format@2.1.9':
     dependencies:
-      '@vitest/utils': 2.1.1
+      tinyrainbow: 1.2.0
+
+  '@vitest/runner@2.1.9':
+    dependencies:
+      '@vitest/utils': 2.1.9
       pathe: 1.1.2
 
-  '@vitest/snapshot@2.1.1':
+  '@vitest/snapshot@2.1.9':
     dependencies:
-      '@vitest/pretty-format': 2.1.1
-      magic-string: 0.30.11
+      '@vitest/pretty-format': 2.1.9
+      magic-string: 0.30.17
       pathe: 1.1.2
 
   '@vitest/spy@2.0.5':
     dependencies:
       tinyspy: 3.0.2
 
-  '@vitest/spy@2.1.1':
+  '@vitest/spy@2.1.9':
     dependencies:
       tinyspy: 3.0.2
 
-  '@vitest/ui@0.33.0(vitest@2.1.1)':
+  '@vitest/ui@0.33.0(vitest@2.1.9)':
     dependencies:
       '@vitest/utils': 0.33.0
       fast-glob: 3.3.2
@@ -24588,7 +24612,7 @@ snapshots:
       pathe: 1.1.2
       picocolors: 1.1.0
       sirv: 2.0.4
-      vitest: 2.1.1(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
+      vitest: 2.1.9(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0)
 
   '@vitest/utils@0.33.0':
     dependencies:
@@ -24609,6 +24633,12 @@ snapshots:
       loupe: 3.1.1
       tinyrainbow: 1.2.0
 
+  '@vitest/utils@2.1.9':
+    dependencies:
+      '@vitest/pretty-format': 2.1.9
+      loupe: 3.1.3
+      tinyrainbow: 1.2.0
+
   '@volar/language-core@2.4.11':
     dependencies:
       '@volar/source-map': 2.4.11
@@ -25634,6 +25664,14 @@ snapshots:
       loupe: 3.1.1
       pathval: 2.0.0
 
+  chai@5.1.2:
+    dependencies:
+      assertion-error: 2.0.1
+      check-error: 2.1.1
+      deep-eql: 5.0.2
+      loupe: 3.1.1
+      pathval: 2.0.0
+
   chalk@2.4.2:
     dependencies:
       ansi-styles: 3.2.1
@@ -27619,6 +27657,8 @@ snapshots:
 
   exit@0.1.2: {}
 
+  expect-type@1.1.0: {}
+
   expect@29.7.0:
     dependencies:
       '@jest/expect-utils': 29.7.0
@@ -30032,6 +30072,8 @@ snapshots:
     dependencies:
       get-func-name: 2.0.2
 
+  loupe@3.1.3: {}
+
   lower-case-first@2.0.2:
     dependencies:
       tslib: 2.7.0
@@ -30081,6 +30123,10 @@ snapshots:
     dependencies:
       '@jridgewell/sourcemap-codec': 1.5.0
 
+  magic-string@0.30.17:
+    dependencies:
+      '@jridgewell/sourcemap-codec': 1.5.0
+
   magic-string@0.30.8:
     dependencies:
       '@jridgewell/sourcemap-codec': 1.5.0
@@ -33644,6 +33690,8 @@ snapshots:
 
   std-env@3.7.0: {}
 
+  std-env@3.8.0: {}
+
   stop-iteration-iterator@1.0.0:
     dependencies:
       internal-slot: 1.0.7
@@ -34150,8 +34198,6 @@ snapshots:
 
   tinybench@2.9.0: {}
 
-  tinyexec@0.3.0: {}
-
   tinyexec@0.3.2: {}
 
   tinyglobby@0.2.10:
@@ -34948,10 +34994,11 @@ snapshots:
       - supports-color
       - terser
 
-  vite-node@2.1.1(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0):
+  vite-node@2.1.9(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0):
     dependencies:
       cac: 6.7.14
       debug: 4.3.7(supports-color@8.1.1)
+      es-module-lexer: 1.5.4
       pathe: 1.1.2
       vite: 5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0)
     transitivePeerDependencies:
@@ -34965,10 +35012,11 @@ snapshots:
       - supports-color
       - terser
 
-  vite-node@2.1.1(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0):
+  vite-node@2.1.9(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0):
     dependencies:
       cac: 6.7.14
       debug: 4.3.7(supports-color@8.1.1)
+      es-module-lexer: 1.5.4
       pathe: 1.1.2
       vite: 5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0)
     transitivePeerDependencies:
@@ -35056,30 +35104,31 @@ snapshots:
       sass: 1.79.3
       terser: 5.34.0
 
-  vitest@2.1.1(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0):
+  vitest@2.1.9(@types/node@20.16.9)(@vitest/ui@0.33.0)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0):
     dependencies:
-      '@vitest/expect': 2.1.1
-      '@vitest/mocker': 2.1.1(msw@2.4.9(typescript@5.6.2))(vite@5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0))
-      '@vitest/pretty-format': 2.1.1
-      '@vitest/runner': 2.1.1
-      '@vitest/snapshot': 2.1.1
-      '@vitest/spy': 2.1.1
-      '@vitest/utils': 2.1.1
-      chai: 5.1.1
+      '@vitest/expect': 2.1.9
+      '@vitest/mocker': 2.1.9(msw@2.4.9(typescript@5.6.2))(vite@5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0))
+      '@vitest/pretty-format': 2.1.9
+      '@vitest/runner': 2.1.9
+      '@vitest/snapshot': 2.1.9
+      '@vitest/spy': 2.1.9
+      '@vitest/utils': 2.1.9
+      chai: 5.1.2
       debug: 4.3.7(supports-color@8.1.1)
-      magic-string: 0.30.11
+      expect-type: 1.1.0
+      magic-string: 0.30.17
       pathe: 1.1.2
-      std-env: 3.7.0
+      std-env: 3.8.0
       tinybench: 2.9.0
-      tinyexec: 0.3.0
+      tinyexec: 0.3.2
       tinypool: 1.0.1
       tinyrainbow: 1.2.0
       vite: 5.4.8(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0)
-      vite-node: 2.1.1(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0)
+      vite-node: 2.1.9(@types/node@20.16.9)(sass@1.79.3)(terser@5.34.0)
       why-is-node-running: 2.3.0
     optionalDependencies:
       '@types/node': 20.16.9
-      '@vitest/ui': 0.33.0(vitest@2.1.1)
+      '@vitest/ui': 0.33.0(vitest@2.1.9)
       happy-dom: 15.11.7
       jsdom: 24.1.3
     transitivePeerDependencies:
@@ -35093,26 +35142,27 @@ snapshots:
       - supports-color
       - terser
 
-  vitest@2.1.1(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0):
+  vitest@2.1.9(@types/node@22.7.3)(happy-dom@15.11.7)(jsdom@24.1.3)(msw@2.4.9(typescript@5.6.2))(sass@1.79.3)(terser@5.34.0):
     dependencies:
-      '@vitest/expect': 2.1.1
-      '@vitest/mocker': 2.1.1(msw@2.4.9(typescript@5.6.2))(vite@5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0))
-      '@vitest/pretty-format': 2.1.1
-      '@vitest/runner': 2.1.1
-      '@vitest/snapshot': 2.1.1
-      '@vitest/spy': 2.1.1
-      '@vitest/utils': 2.1.1
-      chai: 5.1.1
+      '@vitest/expect': 2.1.9
+      '@vitest/mocker': 2.1.9(msw@2.4.9(typescript@5.6.2))(vite@5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0))
+      '@vitest/pretty-format': 2.1.9
+      '@vitest/runner': 2.1.9
+      '@vitest/snapshot': 2.1.9
+      '@vitest/spy': 2.1.9
+      '@vitest/utils': 2.1.9
+      chai: 5.1.2
       debug: 4.3.7(supports-color@8.1.1)
-      magic-string: 0.30.11
+      expect-type: 1.1.0
+      magic-string: 0.30.17
       pathe: 1.1.2
-      std-env: 3.7.0
+      std-env: 3.8.0
       tinybench: 2.9.0
-      tinyexec: 0.3.0
+      tinyexec: 0.3.2
       tinypool: 1.0.1
       tinyrainbow: 1.2.0
       vite: 5.4.8(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0)
-      vite-node: 2.1.1(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0)
+      vite-node: 2.1.9(@types/node@22.7.3)(sass@1.79.3)(terser@5.34.0)
       why-is-node-running: 2.3.0
     optionalDependencies:
       '@types/node': 22.7.3
```

### sdk/bcs/package.json
```diff
@@ -65,7 +65,7 @@
         "@size-limit/preset-small-lib": "^11.1.4",
         "size-limit": "^11.1.4",
         "typescript": "^5.5.3",
-        "vitest": "^2.0.1"
+        "vitest": "^2.1.9"
     },
     "dependencies": {
         "bs58": "^6.0.0"
```

### sdk/dapp-kit/package.json
```diff
@@ -72,7 +72,7 @@
         "size-limit": "^11.1.4",
         "typescript": "^5.5.3",
         "vite": "^5.3.3",
-        "vitest": "^2.0.1"
+        "vitest": "^2.1.9"
     },
     "dependencies": {
         "@iota/iota-sdk": "workspace:*",
```

### sdk/graphql-transport/package.json
```diff
@@ -55,7 +55,7 @@
         "dotenv": "^16.4.5",
         "graphql-config": "^5.0.3",
         "typescript": "^5.5.3",
-        "vitest": "^2.0.1",
+        "vitest": "^2.1.9",
         "wait-on": "^7.2.0"
     },
     "dependencies": {
```

### sdk/kiosk/package.json
```diff
@@ -48,7 +48,7 @@
         "ts-retry-promise": "^0.8.1",
         "typescript": "^5.5.3",
         "vite": "^5.3.3",
-        "vitest": "^2.0.1",
+        "vitest": "^2.1.9",
         "wait-on": "^7.2.0"
     }
 }
```

### sdk/ledgerjs-hw-app-iota/package.json
```diff
@@ -72,6 +72,6 @@
         "axios": "^1.7.4",
         "size-limit": "^11.1.4",
         "typescript": "^5.5.3",
-        "vitest": "^2.0.1"
+        "vitest": "^2.1.9"
     }
 }
```

### sdk/move-bytecode-template/package.json
```diff
@@ -16,7 +16,7 @@
         "@iota/bcs": "workspace:*",
         "@iota/build-scripts": "workspace:*",
         "typescript": "^5.5.3",
-        "vitest": "^2.0.1",
+        "vitest": "^2.1.9",
         "wasm-pack": "^0.13.0"
     }
 }
```

### sdk/typescript/package.json
```diff
@@ -130,7 +130,7 @@
         "ts-retry-promise": "^0.8.1",
         "typescript": "^5.5.3",
         "vite": "^5.3.3",
-        "vitest": "^2.0.1",
+        "vitest": "^2.1.9",
         "wait-on": "^7.2.0",
         "ws": "^8.18.0"
     },
```
