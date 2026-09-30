# [?] chore: bump vitest to fix audit vulnerability (#4715)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-06-04
Source: https://github.com/wevm/viem/commit/a74b05d6e6a4c74ce74990469804858a77af612e
Type: security-commit

## Details
chore: bump vitest to fix audit vulnerability (#4715)

chore: bump vitest to ^4.1.8 to fix audit vulnerability

Resolves the critical advisory GHSA-5xrq-8626-4rwp (vitest <4.1.0), which
was failing the CI `pnpm audit` check.

Amp-Thread-ID: https://ampcode.com/threads/T-019e8cab-fd02-709f-9185-a2766192718b

## Patch
### package.json
```diff
@@ -58,7 +58,7 @@
     "@size-limit/preset-big-lib": "^11.2.0",
     "@types/bun": "^1.2.22",
     "@types/node": "^24.5.2",
-    "@vitest/coverage-v8": "^4.0.15",
+    "@vitest/coverage-v8": "^4.1.8",
     "bun": "^1.2.22",
     "ethers": "^6.15.0",
     "knip": "^5.64.0",
@@ -72,7 +72,7 @@
     "size-limit": "^11.2.0",
     "testcontainers": "^11.10.0",
     "typescript": "catalog:",
-    "vitest": "^4.0.15"
+    "vitest": "^4.1.8"
   },
   "packageManager": "pnpm@10.33.2",
   "engines": {
```

### pnpm-lock.yaml
```diff
@@ -130,8 +130,8 @@ importers:
         specifier: ^24.5.2
         version: 24.5.2
       '@vitest/coverage-v8':
-        specifier: ^4.0.15
-        version: 4.0.15(vitest@4.0.15(@opentelemetry/api@1.7.0)(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3))
+        specifier: ^4.1.8
+        version: 4.1.8(vitest@4.1.8)
       bun:
         specifier: ^1.2.22
         version: 1.2.22
@@ -172,8 +172,8 @@ importers:
         specifier: ^5.9.3
         version: 5.9.3
       vitest:
-        specifier: ^4.0.15
-        version: 4.0.15(@opentelemetry/api@1.7.0)(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3)
+        specifier: ^4.1.8
+        version: 4.1.8(@opentelemetry/api@1.7.0)(@types/node@24.5.2)(@vitest/coverage-v8@4.1.8)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3)
 
   environments/bun:
     dependencies:
@@ -753,10 +753,18 @@ packages:
     resolution: {integrity: sha512-qMlSxKbpRlAridDExk92nSobyDdpPijUq2DW6oDnUqd0iOGxmQjyqhMIihI9+zv4LPyZdRje2cavWPbCbWm3eA==}
     engines: {node: '>=6.9.0'}
 
+  '@babel/helper-string-parser@7.29.7':
+    resolution: {integrity: sha512-Pb5ijPrZ89GDH8223L4UP8i6QApWxs04RbPQJTeWDV0/keR2E36MeKnyr6LYmUUvqRRI+Iv87SuF1W6ErINzYw==}
+    engines: {node: '>=6.9.0'}
+
   '@babel/helper-validator-identifier@7.28.5':
     resolution: {integrity: sha512-qSs4ifwzKJSV39ucNjsvc6WVHs6b7S03sOh2OcHF9UHfVPqWWALUsNUVzhSBiItjRZoLHx7nIarVjqKVusUZ1Q==}
     engines: {node: '>=6.9.0'}
 
+  '@babel/helper-validator-identifier@7.29.7':
+    resolution: {integrity: sha512-qehxGkRj55h/ff8EMaJ+cYhyaKlHIxqYDn682wQD7RNp9UujOQsHog2uS0r2vzr4pW+sXf90NeeayjcNaX3fFg==}
+    engines: {node: '>=6.9.0'}
+
   '@babel/helper-validator-option@7.27.1':
     resolution: {integrity: sha512-YvjJow9FxbhFFKDSuFnVCe2WxXk1zWc22fFePVNEaWJEu8IrZVlda6N0uHwzZrUM1il7NC9Mlp4MaJYbYd9JSg==}
     engines: {node: '>=6.9.0'}
@@ -770,6 +778,11 @@ packages:
     engines: {node: '>=6.0.0'}
     hasBin: true
 
+  '@babel/parser@7.29.7':
+    resolution: {integrity: sha512-hnORnjP/1P/zFEndoeX+n+t1RwWRJiJpM/jO7FW32Kn9r5+sJB2JWOdYo4L6k78j15eCwY3Gm/7364B1EMwtNg==}
+    engines: {node: '>=6.0.0'}
+    hasBin: true
+
   '@babel/runtime@7.26.10':
     resolution: {integrity: sha512-2WJMeRQPHKSPemqk/awGrAiuFfzBmOIPXKizAsVhWH9YJqLZ0H+HS4c8loHGgW6utJ3E/ejXQUsiGaQy2NZ9Fw==}
     engines: {node: '>=6.9.0'}
@@ -790,6 +803,10 @@ packages:
     resolution: {integrity: sha512-qQ5m48eI/MFLQ5PxQj4PFaprjyCTLI37ElWMmNs0K8Lk3dVeOdNpB3ks8jc7yM5CDmVC73eMVk/trk3fgmrUpA==}
     engines: {node: '>=6.9.0'}
 
+  '@babel/types@7.29.7':
+    resolution: {integrity: sha512-4zBIxpPzowiZpusoFkyGVwakdRJUyuH5PxQ/PrqghfdFWWasvnCdPfQXHrenDai+gyLARulZjZowCOj6fjT4pA==}
+    engines: {node: '>=6.9.0'}
+
   '@balena/dockerignore@1.0.2':
     resolution: {integrity: sha512-wMue2Sy4GAVTk6Ic4tJVcnfdau+gx2EnG7S+uAEe+TWJFqE4YoWN4/H8MSLj4eYJKxGg26lZwboEniNiNwZQ6Q==}
 
@@ -2675,6 +2692,9 @@ packages:
   '@standard-schema/spec@1.0.0':
     resolution: {integrity: sha512-m2bOd0f2RT9k8QJx1JN85cZYyH1RqFBdlwtkSlf4tBDYLCiiZnv1fIIwacK6cqwXavOydf0NPToMQgpKq+dVlA==}
 
+  '@standard-schema/spec@1.1.0':
+    resolution: {integrity: sha512-l2aFy5jALhniG5HgqrD6jXLi/rUWrKvqN/qJx6yoJsgKhblVd+iqqU4RCXavm/jPityDo5TCvKMnpjKnOriy0w==}
+
   '@stitches/core@1.2.8':
     resolution: {integrity: sha512-Gfkvwk9o9kE9r9XNBmJRfV8zONvXThnm1tcuojL04Uy5uRyqg93DC83lDebl0rocZCfKSjUv+fWYtMQmEDJldg==}
 
@@ -3054,20 +3074,20 @@ packages:
       react-server-dom-webpack:
         optional: true
 
-  '@vitest/coverage-v8@4.0.15':
-    resolution: {integrity: sha512-FUJ+1RkpTFW7rQITdgTi93qOCWJobWhBirEPCeXh2SW2wsTlFxy51apDz5gzG+ZEYt/THvWeNmhdAoS9DTwpCw==}
+  '@vitest/coverage-v8@4.1.8':
+    resolution: {integrity: sha512-lt3kovsyHwYe00wq4D1ti0Z974fWj4NLp6siqiyEufUpyFwK9Yhi7rBhac9JL5aA0zoMrJqc4vYPZRUnI7l7nw==}
     peerDependencies:
-      '@vitest/browser': 4.0.15
-      vitest: 4.0.15
+      '@vitest/browser': 4.1.8
+      vitest: 4.1.8
     peerDependenciesMeta:
       '@vitest/browser':
         optional: true
 
-  '@vitest/expect@4.0.15':
-    resolution: {integrity: sha512-Gfyva9/GxPAWXIWjyGDli9O+waHDC0Q0jaLdFP1qPAUUfo1FEXPXUfUkp3eZA0sSq340vPycSyOlYUeM15Ft1w==}
+  '@vitest/expect@4.1.8':
+    resolution: {integrity: sha512-h3nDO677RDLEGlBxyQ5CW8RlMThSKSRLUePLOx09gNIWRL40edgA1GCZSZgf1W55MFAG6/Sw14KeaAnqv0NKdQ==}
 
-  '@vitest/mocker@4.0.15':
-    resolution: {integrity: sha512-CZ28GLfOEIFkvCFngN8Sfx5h+Se0zN+h4B7yOsPVCcgtiO7t5jt9xQh2E1UkFep+eb9fjyMfuC5gBypwb07fvQ==}
+  '@vitest/mocker@4.1.8':
+    resolution: {integrity: sha512-LEiN/xe4OSIbKe9HQIp5OC24agGD9J5CnmMgsLohVVoOPWL9a2sBoR6VBx43jQZb7Kr1l4RCuyCJzcAa0+dojw==}
     peerDependencies:
       msw: ^2.4.9
       vite: 6.4.2
@@ -3077,20 +3097,20 @@ packages:
       vite:
         optional: true
 
-  '@vitest/pretty-format@4.0.15':
-    resolution: {integrity: sha512-SWdqR8vEv83WtZcrfLNqlqeQXlQLh2iilO1Wk1gv4eiHKjEzvgHb2OVc3mIPyhZE6F+CtfYjNlDJwP5MN6Km7A==}
+  '@vitest/pretty-format@4.1.8':
+    resolution: {integrity: sha512-9GasEBxpZ1VYIpqHf/0+YGg121uSNwCKOJqIrTwWP/TB7DmFCiaBpNl3aPZzoLWfWkuqhbH8vJIVobZkvdo2cA==}
 
-  '@vitest/runner@4.0.15':
-    resolution: {integrity: sha512-+A+yMY8dGixUhHmNdPUxOh0la6uVzun86vAbuMT3hIDxMrAOmn5ILBHm8ajrqHE0t8R9T1dGnde1A5DTnmi3qw==}
+  '@vitest/runner@4.1.8':
+    resolution: {integrity: sha512-EmVxeBAfMJvycdjd6Hm+RbFBbA9fKvo0Kx37hNpBYoYeavH3RNsBXWDooR1mgD52dCrxIIuP7UotpfiwOikvcg==}
 
-  '@vitest/snapshot@4.0.15':
-    resolution: {integrity: sha512-A7Ob8EdFZJIBjLjeO0DZF4lqR6U7Ydi5/5LIZ0xcI+23lYlsYJAfGn8PrIWTYdZQRNnSRlzhg0zyGu37mVdy5g==}
+  '@vitest/snapshot@4.1.8':
+    resolution: {integrity: sha512-acfZboRmAIf05DEKcBQy33VXojFJjtUdLyo7oOmV9kebb2xdU01UknNiPuPZoJZQyO7DF0gZdTGTpeAzET9QPQ==}
 
-  '@vitest/spy@4.0.15':
-    resolution: {integrity: sha512-+EIjOJmnY6mIfdXtE/bnozKEvTC4Uczg19yeZ2vtCz5Yyb0QQ31QWVQ8hswJ3Ysx/K2EqaNsVanjr//2+P3FHw==}
+  '@vitest/spy@4.1.8':
+    resolution: {integrity: sha512-6EevtBp6OZOPF7bmz36HrGMeP3txgVSrgebWxHOafDXGkhIzfXK14f8KF6MuFfgXXUeHxmpD3BQxkV00/3s5mA==}
 
-  '@vitest/utils@4.0.15':
-    resolution: {integrity: sha512-HXjPW2w5dxhTD0dLwtYHDnelK3j8sR8cWIaLxr22evTyY6q8pRCjZSmhRWVjBaOVXChQd6AwMzi9pucorXCPZA==}
+  '@vitest/utils@4.1.8':
+    resolution: {integrity: sha512-uOJamYALNhfJ6iolExyQM40yIQwDqYnkKtQ5VCiSe17E33H0aQ/u+1GlRuz4LZBk6Mm3sg90G9hEbmEt37C1Zg==}
 
   '@webassemblyjs/ast@1.14.1':
     resolution: {integrity: sha512-nuBEDgQfm1ccRp/8bCQrx1frohyufl4JlbMMZ4P1wpeOfDhF6FQkxZJ1b/e+PLwr6X1Nhw6OLme5usuBWYBvuQ==}
@@ -3312,8 +3332,8 @@ packages:
     resolution: {integrity: sha512-x1FCFnFifvYDDzTaLII71vG5uvDwgtmDTEVWAxrgeiR8VjMONcCXJx7E+USjDtHlwFmt9MysbqgF9b9Vjr6w+w==}
     engines: {node: '>=4'}
 
-  ast-v8-to-istanbul@0.3.8:
-    resolution: {integrity: sha512-szgSZqUxI5T8mLKvS7WTjF9is+MVbOeLADU73IseOcrqhxr/VAvy6wfoVE39KnKzA7JRhjF5eUagNlHwvZPlKQ==}
+  ast-v8-to-istanbul@1.0.3:
+    resolution: {integrity: sha512-jCMQ6ZylLPudp0CDfBmQBZUsrh1/8psbmu9ibeVWKuHWD0YrH9YABwlKu5kVEFoT0GCQQW9Z/SxfuEbbkGQCRg==}
 
   astring@1.9.0:
     resolution: {integrity: sha512-LElXdjswlqjWrPpJFg1Fx4wpkOCxj1TDHlSV4PlaRxHGWko024xICaa97ZkMfs6DRKlCguiAI+rbXv5GWwXIkg==}
@@ -3493,8 +3513,8 @@ packages:
   ccount@2.0.1:
     resolution: {integrity: sha512-eyrF0jiFpY+3drT6383f1qhkbGsLSifNAjA61IUjZjmLCWjItY6LB9ft9YhoDgwfmclB2zhu51Lc7+95b8NRAg==}
 
-  chai@6.2.1:
-    resolution: {integrity: sha512-p4Z49OGG5W/WBCPSS/dH3jQ73kD6tiMmUM+bckNK6Jr5JHMG3k9bg/BvKR8lKmtVBKmOiuVaV2ws8s9oSbwysg==}
+  chai@6.2.2:
+    resolution: {integrity: sha512-NUPRluOfOiTKBKvWPtSD4PhFvWCqOi0BGStNWs57X9js7XGTprSmFoz5F0tWhR4WPjNeR9jXqdC7/UpSJTnlRg==}
     engines: {node: '>=18'}
 
   chalk@4.1.2:
@@ -3856,9 +3876,6 @@ packages:
     resolution: {integrity: sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw==}
     engines: {node: '>= 0.4'}
 
-  es-module-lexer@1.7.0:
-    resolution: {integrity: sha512-jEQoCwk8hyb2AZziIOLhDqpm5+2ww5uIE6lkO/6jcOCusfk6LhMHpXXfBLXTZ7Ydyt0j4VoUQv6uGNYbdW+kBA==}
-
   es-module-lexer@2.0.0:
     resolution: {integrity: sha512-5POEcUuZybH7IdmGsD8wlf0AI55wMecM9rVBTI/qEAy2c1kTOm3DjFYjrBdI2K3BaJjJYfYFeRtM0t9ssnRuxw==}
 
@@ -4026,8 +4043,8 @@ packages:
     resolution: {integrity: sha512-Zk/eNKV2zbjpKzrsQ+n1G6poVbErQxJ0LBOJXaKZ1EViLzH+hrLu9cdXI4zw9dBQJslwBEpbQ2P1oS7nDxs6jQ==}
     engines: {node: '>= 0.8.0'}
 
-  expect-type@1.2.2:
-    resolution: {integrity: sha512-JhFGDVJ7tmDJItKhYgJCGLOWjuK9vPxiXoUFLwLDc99NlmklilbiQJwoctZtt13+xMw91MCk/REan6MWHqDjyA==}
+  expect-type@1.3.0:
+    resolution: {integrity: sha512-knvyeauYhqjOYvQ66MznSMs83wmHrCycNEN6Ao+2AeYEfxUIkuiVxdEa1qlGEPK+We3n0THiDciYSsCcgW/DoA==}
     engines: {node: '>=12.0.0'}
 
   express-rate-limit@8.3.0:
@@ -4498,10 +4515,6 @@ packages:
     resolution: {integrity: sha512-GCfE1mtsHGOELCU8e/Z7YWzpmybrx/+dSTfLrvY8qRmaY6zXTKWn6WQIjaAFw069icm6GVMNkgu0NzI4iPZUNw==}
     engines: {node: '>=10'}
 
-  istanbul-lib-source-maps@5.0.6:
-    resolution: {integrity: sha512-yg2d+Em4KizZC5niWhQaIomgf5WlL4vOOjZ5xGCmF8SnPE/mDWWXgvRExdcpCgh9lLRRa1/fSYp2ymmbJ1pI+A==}
-    engines: {node: '>=10'}
-
   istanbul-reports@3.2.0:
     resolution: {integrity: sha512-HGYWWS/ehqTV3xN10i23tkPkpH46MLCIMFNCaaKNavAXTF1RkqxawEPtnjnGZ6XKSInBKkiOA5BKS+aZiY3AvA==}
     engines: {node: '>=8'}
@@ -4529,6 +4542,9 @@ packages:
     resolution: {integrity: sha512-34wB/Y7MW7bzjKRjUKTa46I2Z7eV62Rkhva+KkopW7Qvv/OSWBqvkSY7vusOPrNuZcUG3tApvdVgNB8POj3SPw==}
     engines: {node: '>=10'}
 
+  js-tokens@10.0.0:
+    resolution: {integrity: sha512-lM/UBzQmfJRo9ABXbPWemivdCW8V2G8FHaHdypQaIy523snUjog0W71ayWXTjiR+ixeMyVHN2XcpnTd/liPg/Q==}
+
   js-tokens@4.0.0:
     resolution: {integrity: sha512-RdJUflcE3cUzKiMqQgsCu06FPu9UdIJO0beYbPhHN4k6apgJtifcoCtT9bcxOpYBtpD2kCM6Sbzg4CausW/PKQ==}
 
@@ -4747,8 +4763,8 @@ packages:
   magic-string@0.30.21:
     resolution: {integrity: sha512-vd2F4YUyEXKGcLHoq+TEyCjxueSeHnFxyyjNp80yg0XV4vUhnDer/lvvlqM/arB5bXQN5K2/3oinyCRyx8T2CQ==}
 
-  magicast@0.5.1:
-    resolution: {integrity: sha512-xrHS24IxaLrvuo613F719wvOIv9xPHFWQHuvGUBmPnCA/3MQxKI3b+r7n1jAoDHmsbC5bRhTZYR77invLAxVnw==}
+  magicast@0.5.3:
+    resolution: {integrity: sha512-pVKE4UdSQ7DvHzivsCIFx2BJn1mHG6KsyrFcaxFx6tONdneEuThrDx0Cj3AMg58KyN4pzYT+LHOotxDQDjNvkw==}
 
   make-dir@4.0.0:
     resolution: {integrity: sha512-hXdUTZYIVOt1Ex//jAQi+wTZZpUpwBj/0QsOzqegb3rGMMeJiSEu5xLHnYfBrRV4RH2+OCSOO95Is/7x1WJ4bw==}
@@ -6027,8 +6043,8 @@ packages:
     resolution: {integrity: sha512-DvEy55V3DB7uknRo+4iOGT5fP1slR8wQohVdknigZPMpMstaKJQWhwiYBACJE3Ul2pTnATihhBYnRhZQHGBiRw==}
     engines: {node: '>= 0.8'}
 
-  std-env@3.10.0:
-    resolution: {integrity: sha512-5GS12FdOZNliM5mAOxFRg7Ir0pWz8MdpYm6AY6VPkGpbA7ZzmbzNcBJQ0GPvvyWgcY7QAhCgf9Uy89I03faLkg==}
+  std-env@4.1.0:
+    resolution: {integrity: sha512-Rq7ybcX2RuC55r9oaPVEW7/xu3tj8u4GeBYHBWCychFtzMIr86A7e3PPEBPT37sHStKX3+TiX/Fr/ACmJLVlLQ==}
 
   stream-shift@1.0.3:
     resolution: {integrity: sha512-76ORR0DO1o1hlKwTbi/DM3EXWGf3ZJYO8cXX5RJwnul2DEg2oyoZyjLNoQM8WsvZiFKCRfC1O0J7iCvie3RZmQ==}
@@ -6234,8 +6250,8 @@ packages:
     resolution: {integrity: sha512-pn99VhoACYR8nFHhxqix+uvsbXineAasWm5ojXoN8xEwK5Kd3/TrhNn1wByuD52UxWRLy8pu+kRMniEi6Eq9Zg==}
     engines: {node: '>=12.0.0'}
 
-  tinyrainbow@3.0.3:
-    resolution: {integrity: sha512-PSkbLUoxOFRzJYjjxHJt9xro7D+iilgMX/C9lawzVuYiIdcihh9DXmVibBe8lmcFrRi/VzlPjBxbN7rH24q8/Q==}
+  tinyrainbow@3.1.0:
+    resolution: {integrity: sha512-Bf+ILmBgretUrdJxzXM0SgXLZ3XfiaUuOj/IKQHuTXip+05Xn+uyEYdVg0kYDipTBcLrCVyUzAPz7QmArb0mmw==}
     engines: {node: '>=14.0.0'}
 
   tmp@0.2.6:
@@ -6563,18 +6579,20 @@ packages:
       vite:
         optional: true
 
-  vitest@4.0.15:
-    resolution: {integrity: sha512-n1RxDp8UJm6N0IbJLQo+yzLZ2sQCDyl1o0LeugbPWf8+8Fttp29GghsQBjYJVmWq3gBFfe9Hs1spR44vovn2wA==}
+  vitest@4.1.8:
+    resolution: {integrity: sha512-flY6ScbCIt9HThs+C5HS7jvGOB560DJtk/Z15IQROTA6zEy49Nh8T/dofWTQL+n3vswqn87sbJNiuqw1SDp5Ig==}
     engines: {node: ^20.0.0 || ^22.0.0 || >=24.0.0}
     hasBin: true
     peerDependencies:
       '@edge-runtime/vm': '*'
       '@opentelemetry/api': ~1.7.0
       '@types/node': ^20.0.0 || ^22.0.0 || >=24.0.0
-      '@vitest/browser-playwright': 4.0.15
-      '@vitest/browser-preview': 4.0.15
-      '@vitest/browser-webdriverio': 4.0.15
-      '@vitest/ui': 4.0.15
+      '@vitest/browser-playwright': 4.1.8
+      '@vitest/browser-preview': 4.1.8
+      '@vitest/browser-webdriverio': 4.1.8
+      '@vitest/coverage-istanbul': 4.1.8
+      '@vitest/coverage-v8': 4.1.8
+      '@vitest/ui': 4.1.8
       happy-dom: '*'
       jsdom: '*'
     peerDependenciesMeta:
@@ -6590,6 +6608,10 @@ packages:
         optional: true
       '@vitest/browser-webdriverio':
         optional: true
+      '@vitest/coverage-istanbul':
+        optional: true
+      '@vitest/coverage-v8':
+        optional: true
       '@vitest/ui':
         optional: true
       happy-dom:
@@ -6913,8 +6935,12 @@ snapshots:
 
   '@babel/helper-string-parser@7.27.1': {}
 
+  '@babel/helper-string-parser@7.29.7': {}
+
   '@babel/helper-validator-identifier@7.28.5': {}
 
+  '@babel/helper-validator-identifier@7.29.7': {}
+
   '@babel/helper-validator-option@7.27.1': {}
 
   '@babel/helpers@7.28.4':
@@ -6926,6 +6952,10 @@ snapshots:
     dependencies:
       '@babel/types': 7.28.5
 
+  '@babel/parser@7.29.7':
+    dependencies:
+      '@babel/types': 7.29.7
+
   '@babel/runtime@7.26.10':
     dependencies:
       regenerator-runtime: 0.14.1
@@ -6955,6 +6985,11 @@ snapshots:
       '@babel/helper-string-parser': 7.27.1
       '@babel/helper-validator-identifier': 7.28.5
 
+  '@babel/types@7.29.7':
+    dependencies:
+      '@babel/helper-string-parser': 7.29.7
+      '@babel/helper-validator-identifier': 7.29.7
+
   '@balena/dockerignore@1.0.2': {}
 
   '@base-ui/react@1.1.0(@types/react@19.0.8)(react-dom@19.2.6(react@19.2.6))(react@19.2.6)':
@@ -8844,6 +8879,8 @@ snapshots:
 
   '@standard-schema/spec@1.0.0': {}
 
+  '@standard-schema/spec@1.1.0': {}
+
   '@stitches/core@1.2.8': {}
 
   '@svgr/babel-plugin-add-jsx-attribute@8.0.0(@babel/core@7.28.5)':
@@ -9205,61 +9242,60 @@ snapshots:
     optionalDependencies:
       react-server-dom-webpack: 19.2.6(react-dom@19.2.6(react@19.2.6))(react@19.2.6)(webpack@5.104.1(esbuild@0.27.2))
 
-  '@vitest/coverage-v8@4.0.15(vitest@4.0.15(@opentelemetry/api@1.7.0)(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3))':
+  '@vitest/coverage-v8@4.1.8(vitest@4.1.8)':
     dependencies:
       '@bcoe/v8-coverage': 1.0.2
-      '@vitest/utils': 4.0.15
-      ast-v8-to-istanbul: 0.3.8
+      '@vitest/utils': 4.1.8
+      ast-v8-to-istanbul: 1.0.3
       istanbul-lib-coverage: 3.2.2
       istanbul-lib-report: 3.0.1
-      istanbul-lib-source-maps: 5.0.6
       istanbul-reports: 3.2.0
-      magicast: 0.5.1
+      magicast: 0.5.3
       obug: 2.1.1
-      std-env: 3.10.0
-      tinyrainbow: 3.0.3
-      vitest: 4.0.15(@opentelemetry/api@1.7.0)(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3)
-    transitivePeerDependencies:
-      - supports-color
+      std-env: 4.1.0
+      tinyrainbow: 3.1.0
+      vitest: 4.1.8(@opentelemetry/api@1.7.0)(@types/node@24.5.2)(@vitest/coverage-v8@4.1.8)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3)
 
-  '@vitest/expect@4.0.15':
+  '@vitest/expect@4.1.8':
     dependencies:
-      '@standard-schema/spec': 1.0.0
+      '@standard-schema/spec': 1.1.0
       '@types/chai': 5.2.2
-      '@vitest/spy': 4.0.15
-      '@vitest/utils': 4.0.15
-      chai: 6.2.1
-      tinyrainbow: 3.0.3
+      '@vitest/spy': 4.1.8
+      '@vitest/utils': 4.1.8
+      chai: 6.2.2
+      tinyrainbow: 3.1.0
 
-  '@vitest/mocker@4.0.15(vite@6.4.2(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3))':
+  '@vitest/mocker@4.1.8(vite@6.4.2(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3))':
     dependencies:
-      '@vitest/spy': 4.0.15
+      '@vitest/spy': 4.1.8
       estree-walker: 3.0.3
       magic-string: 0.30.21
     optionalDependencies:
       vite: 6.4.2(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3)
 
-  '@vitest/pretty-format@4.0.15':
+  '@vitest/pretty-format@4.1.8':
     dependencies:
-      tinyrainbow: 3.0.3
+      tinyrainbow: 3.1.0
 
-  '@vitest/runner@4.0.15':
+  '@vitest/runner@4.1.8':
     dependencies:
-      '@vitest/utils': 4.0.15
+      '@vitest/utils': 4.1.8
       pathe: 2.0.3
 
-  '@vitest/snapshot@4.0.15':
+  '@vitest/snapshot@4.1.8':
     dependencies:
-      '@vitest/pretty-format': 4.0.15
+      '@vitest/pretty-format': 4.1.8
+      '@vitest/utils': 4.1.8
       magic-string: 0.30.21
       pathe: 2.0.3
 
-  '@vitest/spy@4.0.15': {}
+  '@vitest/spy@4.1.8': {}
 
-  '@vitest/utils@4.0.15':
+  '@vitest/utils@4.1.8':
     dependencies:
-      '@vitest/pretty-format': 4.0.15
-      tinyrainbow: 3.0.3
+      '@vitest/pretty-format': 4.1.8
+      convert-source-map: 2.0.0
+      tinyrainbow: 3.1.0
 
   '@webassemblyjs/ast@1.14.1':
     dependencies:
@@ -9506,11 +9542,11 @@ snapshots:
     dependencies:
       tslib: 2.8.1
 
-  ast-v8-to-istanbul@0.3.8:
+  ast-v8-to-istanbul@1.0.3:
     dependencies:
       '@jridgewell/trace-mapping': 0.3.31
       estree-walker: 3.0.3
-      js-tokens: 9.0.1
+      js-tokens: 10.0.0
 
   astring@1.9.0: {}
 
@@ -9694,7 +9730,7 @@ snapshots:
 
   ccount@2.0.1: {}
 
-  chai@6.2.1: {}
+  chai@6.2.2: {}
 
   chalk@4.1.2:
     dependencies:
@@ -10009,8 +10045,6 @@ snapshots:
 
   es-errors@1.3.0: {}
 
-  es-module-lexer@1.7.0: {}
-
   es-module-lexer@2.0.0: {}
 
   es-module-lexer@2.1.0: {}
@@ -10261,7 +10295,7 @@ snapshots:
 
   exit@0.1.2: {}
 
-  expect-type@1.2.2: {}
+  expect-type@1.3.0: {}
 
   express-rate-limit@8.3.0(express@5.2.1):
     dependencies:
@@ -10830,14 +10864,6 @@ snapshots:
       make-dir: 4.0.0
       supports-color: 7.2.0
 
-  istanbul-lib-source-maps@5.0.6:
-    dependencies:
-      '@jridgewell/trace-mapping': 0.3.31
-      debug: 4.4.3
-      istanbul-lib-coverage: 3.2.2
-    transitivePeerDependencies:
-      - supports-color
-
   istanbul-reports@3.2.0:
     dependencies:
       html-escaper: 2.0.2
@@ -10861,6 +10887,8 @@ snapshots:
 
   joycon@3.1.1: {}
 
+  js-tokens@10.0.0: {}
+
   js-tokens@4.0.0: {}
 
   js-tokens@9.0.1: {}
@@ -11049,10 +11077,10 @@ snapshots:
     dependencies:
       '@jridgewell/sourcemap-codec': 1.5.5
 
-  magicast@0.5.1:
+  magicast@0.5.3:
     dependencies:
-      '@babel/parser': 7.28.5
-      '@babel/types': 7.28.5
+      '@babel/parser': 7.29.7
+      '@babel/types': 7.29.7
       source-map-js: 1.2.1
 
   make-dir@4.0.0:
@@ -12886,7 +12914,7 @@ snapshots:
 
   statuses@2.0.2: {}
 
-  std-env@3.10.0: {}
+  std-env@4.1.0: {}
 
   stream-shift@1.0.3: {}
 
@@ -13134,7 +13162,7 @@ snapshots:
       fdir: 6.5.0(picomatch@4.0.4)
       picomatch: 4.0.4
 
-  tinyrainbow@3.0.3: {}
+  tinyrainbow@3.1.0: {}
 
   tmp@0.2.6: {}
 
@@ -13415,31 +13443,32 @@ snapshots:
     optionalDependencies:
       vite: 8.0.14(@types/node@24.5.2)(esbuild@0.27.2)(jiti@2.7.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3)
 
-  vitest@4.0.15(@opentelemetry/api@1.7.0)(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3):
-    dependencies:
-      '@vitest/expect': 4.0.15
-      '@vitest/mocker': 4.0.15(vite@6.4.2(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3))
-      '@vitest/pretty-format': 4.0.15
-      '@vitest/runner': 4.0.15
-      '@vitest/snapshot': 4.0.15
-      '@vitest/spy': 4.0.15
-      '@vitest/utils': 4.0.15
-      es-module-lexer: 1.7.0
-      expect-type: 1.2.2
+  vitest@4.1.8(@opentelemetry/api@1.7.0)(@types/node@24.5.2)(@vitest/coverage-v8@4.1.8)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3):
+    dependencies:
+      '@vitest/expect': 4.1.8
+      '@vitest/mocker': 4.1.8(vite@6.4.2(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3))
+      '@vitest/pretty-format': 4.1.8
+      '@vitest/runner': 4.1.8
+      '@vitest/snapshot': 4.1.8
+      '@vitest/spy': 4.1.8
+      '@vitest/utils': 4.1.8
+      es-module-lexer: 2.1.0
+      expect-type: 1.3.0
       magic-string: 0.30.21
       obug: 2.1.1
       pathe: 2.0.3
       picomatch: 4.0.4
-      std-env: 3.10.0
+      std-env: 4.1.0
       tinybench: 2.9.0
       tinyexec: 1.0.2
-      tinyglobby: 0.2.15
-      tinyrainbow: 3.0.3
+      tinyglobby: 0.2.16
+      tinyrainbow: 3.1.0
       vite: 6.4.2(@types/node@24.5.2)(jiti@2.7.0)(lightningcss@1.32.0)(terser@5.36.0)(tsx@4.21.0)(yaml@2.8.3)
       why-is-node-running: 2.3.0
     optionalDependencies:
       '@opentelemetry/api': 1.7.0
       '@types/node': 24.5.2
+      '@vitest/coverage-v8': 4.1.8(vitest@4.1.8)
     transitivePeerDependencies:
       - jiti
       - less
```
