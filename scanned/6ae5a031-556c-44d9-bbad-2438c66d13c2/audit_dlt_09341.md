# [?] fix(deps): patch audit vulnerabilities (#4876)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-07-21
Source: https://github.com/wevm/viem/commit/a8c5ee4c216e82b76ea623a24ce3252d04480f33
Type: security-commit

## Details
fix(deps): patch audit vulnerabilities (#4876)

fix(deps): patched audit vulnerabilities

Co-authored-by: Steven Truong <struong@users.noreply.github.com>

## Patch
### pnpm-lock.yaml
```diff
@@ -27,10 +27,11 @@ overrides:
   '@babel/runtime@<7.26.10': 7.26.10
   '@babel/core': '>=7.29.6 <8'
   '@grpc/grpc-js': '>=1.14.4'
-  '@hono/node-server@<1.19.13': 1.19.13
+  '@hono/node-server@<2.0.5': 2.0.6
   '@isaacs/brace-expansion@<=5.0.0': 5.0.1
   '@modelcontextprotocol/sdk@>=1.10.0 <=1.25.3': 1.26.0
   '@opentelemetry/core': '>=2.8.0'
+  '@opentelemetry/propagator-jaeger@<2.9.0': 2.9.0
   ajv@<8.18.0: 8.18.0
   brace-expansion@>=2.0.0 <=2.0.1: 2.0.2
   cookie@<0.7.0: ^0.7.0
@@ -49,7 +50,7 @@ overrides:
   '@opentelemetry/sdk-node@<0.217.0': 0.217.0
   find-my-way@>=5.5.0 <8.2.2: ^8.2.2
   glob@>=10.3.7 <=11.0.3: '>=11.1.0'
-  hono: '>=4.12.21'
+  hono: '>=4.12.27'
   ip-address@<=10.1.0: 10.1.1
   lodash@>=4.0.0 <=4.17.23: 4.18.1
   lodash-es@>=4.0.0 <=4.17.22: 4.17.23
@@ -96,7 +97,7 @@ overrides:
   next@>=16.0.0-beta.0 <16.2.6: 16.2.6
   react-server-dom-webpack@>=19.2.0 <19.2.6: 19.2.6
   basic-ftp@<=5.3.0: 5.3.1
-  fast-uri@<=3.1.1: 3.1.2
+  fast-uri@<=3.1.2: 3.1.3
 
 importers:
 
@@ -259,7 +260,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -272,7 +273,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -285,7 +286,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -298,7 +299,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -311,7 +312,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -330,7 +331,7 @@ importers:
         version: 19.2.3(react@19.2.3)
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       '@types/react':
         specifier: ^19
@@ -358,7 +359,7 @@ importers:
         version: 19.2.3(react@19.2.3)
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       '@types/react':
         specifier: ^19
@@ -380,7 +381,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -393,7 +394,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -412,7 +413,7 @@ importers:
         version: 19.2.3(react@19.2.3)
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       '@types/react':
         specifier: ^19
@@ -434,7 +435,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -447,7 +448,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -460,7 +461,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -473,7 +474,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -536,7 +537,7 @@ importers:
         version: 19.2.3(react@19.2.3)
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       '@types/react':
         specifier: ^19
@@ -564,7 +565,7 @@ importers:
         version: 19.2.3(react@19.2.3)
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       '@types/react':
         specifier: ^19
@@ -586,7 +587,7 @@ importers:
     dependencies:
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       typescript:
         specifier: ^5.9.3
@@ -605,7 +606,7 @@ importers:
         version: 19.2.3(react@19.2.3)
       viem:
         specifier: latest
-        version: 2.48.8(typescript@5.9.3)(zod@4.4.3)
+        version: 2.55.4(typescript@5.9.3)(zod@4.4.3)
     devDependencies:
       '@types/react':
         specifier: ^19
@@ -1253,17 +1254,11 @@ packages:
     peerDependencies:
       vue: ^3.2.0
 
-  '@hono/node-server@1.19.13':
-    resolution: {integrity: sha512-TsQLe4i2gvoTtrHje625ngThGBySOgSK3Xo2XRYOdqGN1teR8+I7vchQC46uLJi8OF62YTYA3AhSpumtkhsaKQ==}
-    engines: {node: '>=18.14.1'}
-    peerDependencies:
-      hono: '>=4.12.21'
-
   '@hono/node-server@2.0.6':
     resolution: {integrity: sha512-7DeRlKG57JDBNZ5Qj2jwVdgwQy4b0tLubRLl3zCf91/rCf9i7p1V5FtW/yWibm1uUHE493ts9ZXH/7g/LQWl+g==}
     engines: {node: '>=20'}
     peerDependencies:
-      hono: '>=4.12.21'
+      hono: '>=4.12.27'
 
   '@iconify-json/lucide@1.2.114':
     resolution: {integrity: sha512-NbvH3B1BYo6wBtS7joLi7f2UVQOqK2dtZodMFf3kkBs+Tnh9TkRuy8oVHr1RM8UK6bUtvAXxfNlGAah0CuvPCw==}
@@ -1881,8 +1876,8 @@ packages:
     peerDependencies:
       '@opentelemetry/api': ~1.7.0
 
-  '@opentelemetry/propagator-jaeger@2.7.1':
-    resolution: {integrity: sha512-KMjVBHzP4N60bOzxja76M1F1hZZ43lGPga5ix+mkv9+kk1nx9SbkxSvJsMbuVUxdPQmsPTqGShmhN8ulrMOg6Q==}
+  '@opentelemetry/propagator-jaeger@2.9.0':
+    resolution: {integrity: sha512-4mYGty27rYvSM0jtp1ZUOqd3LfVRCYg9H5G9OFzSx5HViYToU21MFhWfco7x1HwXr7ER8yGOiCIHZUwjPksc0Q==}
     engines: {node: ^18.19.0 || >=20.6.0}
     peerDependencies:
       '@opentelemetry/api': ~1.7.0
@@ -3342,6 +3337,7 @@ packages:
 
   acorn-import-assertions@1.9.0:
     resolution: {integrity: sha512-cmMwop9x+8KFhxvKrKfPYmN6/pKTYYHBqLa0DfvVZcKMJWNyWLnaqND7dx/qn66R7ewM1UX5XMaDVP5wlVTaVA==}
+    deprecated: package has been renamed to acorn-import-attributes
     peerDependencies:
       acorn: ^8
 
@@ -3574,11 +3570,6 @@ packages:
     resolution: {integrity: sha512-yQbXgO/OSZVD2IsiLlro+7Hf6Q18EJrKSEsdoMzKePKXct3gvD8oLcOQdIzGupr5Fj+EDe8gO/lxc1BzfMpxvA==}
     engines: {node: '>=8'}
 
-  browserslist@4.28.1:
-    resolution: {integrity: sha512-ZC5Bd0LgJXgwGqUknZY/vkUQ04r8NXnJZ3yYi4vDmSiZmC/pdSN0NbNRPxZpbtO4uAfDUAFffO8IZoM3Gj8IkA==}
-    engines: {node: ^6 || ^7 || ^8 || ^9 || ^10 || ^11 || ^12 || >=13.7}
-    hasBin: true
-
   browserslist@4.28.4:
     resolution: {integrity: sha512-MTc8i/x9jBQd1iMw2CFGS+rwMa07eYjLR0CCTLDACl9xhxy+nIs3KeML/biicXtk9JrZ6dnnTatmc7ErPXIxqw==}
     engines: {node: ^6 || ^7 || ^8 || ^9 || ^10 || ^11 || ^12 || >=13.7}
@@ -3873,9 +3864,6 @@ packages:
     resolution: {integrity: sha512-uV2QOWP2nWzsy2aMp8aRibhi9dlzF5Hgh5SHaB9OiTGEyDTiJJyx0uy51QXdyWbtAHNua4XJzUKca3OzKUd3vA==}
     engines: {node: '>= 8'}
 
-  csstype@3.1.3:
-    resolution: {integrity: sha512-M1uQkMl8rQK/szD0LNhtqxIPLpimGm8sOBwU7lLnCpSbTyY3yeU1Vc7l4KT5zT4s/yOxHH5O7tIuuLOCnLADRw==}
-
   csstype@3.2.3:
     resolution: {integrity: sha512-z1HGKcYy2xA8AGQfwrn0PAy+PB7X/GSj3UVJW9qKyn43xWa+gl5nXmU4qqLMRzWVLFC8KusUX8T/0kCiOYpAIQ==}
 
@@ -4003,9 +3991,6 @@ packages:
   ee-first@1.1.1:
     resolution: {integrity: sha512-WMwm9LhRUo+WUaRN+vRuETqG89IgZphVSNkdFgeb6sS/E4OrDIN7t48CAewSHXc6C8lefD8KKfr5vY61brQlow==}
 
-  electron-to-chromium@1.5.286:
-    resolution: {integrity: sha512-9tfDXhJ4RKFNerfjdCcZfufu49vg620741MNs26a9+bhLThdB+plgMeou98CAaHu/WATj2iHOOHTp1hWtABj2A==}
-
   electron-to-chromium@1.5.380:
     resolution: {integrity: sha512-W6d5AbuEoRayO447cqrg6lKJIlscgRnnxOZl/08kfV71BQDoEBC7Wwis68z87LjyK6f4kWyTaubuDbhHKrZkbA==}
 
@@ -4025,10 +4010,6 @@ packages:
   end-of-stream@1.4.4:
     resolution: {integrity: sha512-+uw1inIHVPQoaVuHzRyXd21icM+cnt4CzD5rW+NC1wjOUSTOs+Te7FOv7AhN7vS9x/oIyhLP5PR1H+phQAHu5Q==}
 
-  enhanced-resolve@5.18.3:
-    resolution: {integrity: sha512-d4lC8xfavMeBjzGr2vECC3fsGXziXZQyJxD868h2M/mBI3PwAuODxAkLkq5HYuvrPYcUtiLzsTo8U3PgX3Ocww==}
-    engines: {node: '>=10.13.0'}
-
   enhanced-resolve@5.21.6:
     resolution: {integrity: sha512-aNnGCvbJ/RIyWo1IuhNdVjnNF+EjH9wpzpNHt+ci/m9He9LJvUN8wrCcXjp9cWsGNAuvSpVFTx/vraAFQ8qGjQ==}
     engines: {node: '>=10.13.0'}
@@ -4286,8 +4267,8 @@ packages:
   fast-safe-stringify@2.1.1:
     resolution: {integrity: sha512-W+KJc2dmILlPplD/H4K9l9LcAHAfPtP6BY84uVLXQ6Evcz9Lcg33Y2z1IVblT6xdY54PXYVHEv+0Wpq8Io6zkA==}
 
-  fast-uri@3.1.2:
-    resolution: {integrity: sha512-rVjf7ArG3LTk+FS6Yw81V1DLuZl1bRbNrev6Tmd/9RaroeeRRJhAt7jg/6YFxbvAQXUCavSoZhPPj6oOx+5KjQ==}
+  fast-uri@3.1.3:
+    resolution: {integrity: sha512-i70LwGWUduXqzicKXWshooq+sWL1K3WUU5rKZNG/0i3a1OSoX3HqhH5WbWwTmqWfor4urUakGPiRQcleRZTwOg==}
 
   fastify-plugin@4.5.1:
     resolution: {integrity: sha512-stRHYGeuqpEZTL1Ef0Ovr2ltazUT9g844X5z/zEBFLG8RYlpDiOCIG+ATvYEp+/zmc7sN29mcIMp8gvYplYPIQ==}
@@ -4476,6 +4457,7 @@ packages:
   glob@8.1.0:
     resolution: {integrity: sha512-r8hpEjiQEYlF2QU0df3dS+nxxSIreXQS1qRhMJM0Q5NDdR386C7jb7Hwwod8Fgiuex+k0GFjgft18yvxm5XoCQ==}
     engines: {node: '>=12'}
+    deprecated: Old versions of glob are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exorbitant rates) by contacting i@izs.me
 
   globby@11.1.0:
     resolution: {integrity: sha512-jhIXaOzy1sb8IyocaruWSn1TjmnBVs8Ayhcy83rmxNJ8q2uWKCAj3CnJY+KpGSXCueAPc0i05kVvVKtP1t9S3g==}
@@ -4573,10 +4555,6 @@ packages:
     resolution: {integrity: sha512-Xwwo44whKBVCYoliBQwaPvtd/2tYFkRQtXDWj1nackaV2JPXx3L0+Jvd8/qCJ2p+ML0/XVkJ2q+Mr+UVdpJK5w==}
     engines: {node: '>=12.0.0'}
 
-  hono@4.12.25:
-    resolution: {integrity: sha512-2NFaIyNVgJmBs/ecmtGzlmluTFs5cHEWGTdu0t1HBwYzoGXOL5nUQBRMXsXWla5i4KkG//QMzVP88m1+I3fdAQ==}
-    engines: {node: '>=16.9.0'}
-
   hono@4.12.27:
     resolution: {integrity: sha512-1yrb/+w6HWQJrUCLkJ2IF5jNIPvvFkblV5RNOYl6bV+OA6p9GLcMpHFFGTosSvHvcAUibuUukRqhlYI4z32C7Q==}
     engines: {node: '>=16.9.0'}
@@ -4675,6 +4653,7 @@ packages:
 
   inflight@1.0.6:
     resolution: {integrity: sha512-k92I/b08q4wvFscXCLvqfsHCrjrF7yiXsQuIVvVE7N82W3+aqpzuUdBbfhWcy/FZR3/4IgflMgKLOsvPDrGCJA==}
+    deprecated: This module is not supported, and leaks memory. Do not use it. Check out lru-cache if you want a good and tested way to coalesce async requests by a key value, which is much more comprehensive and powerful.
 
   inherits@2.0.4:
     resolution: {integrity: sha512-k/vGaX4/Yla3WzyMCvTQOXYeIHvqOKtnqBduzTHpzpQZzAskKMhZ2K+EnBiSM9zGSoIFeMpXKxa4dYeZIQqewQ==}
@@ -4846,10 +4825,6 @@ packages:
     resolution: {integrity: sha512-1td788aAnnZ5qs7V2QIRl1owjtYpbKt749Y3xauqQgwIIGF/xXWz1wMTEBx5O3LK3lXLVuqXPdPxj2BoFHaW9Q==}
     hasBin: true
 
-  js-yaml@5.2.1:
-    resolution: {integrity: sha512-zfLtNfQqxVqq3uaTqSkh4x4hZw3KHobGUA0fJUj4wawW8bsQLTVqpHdXSIzidh7o+4lEW36tANuAGdaFx6Zgnw==}
-    hasBin: true
-
   jsesc@3.1.0:
     resolution: {integrity: sha512-/sM3dO2FOzXjKQhJuo0Q173wf2KOo8t4I8vHy6lF9poUp7bKT0/NHE8fPX23PwfhnykfqnC2xRxOnVw5XuGIaA==}
     engines: {node: '>=6'}
@@ -5366,7 +5341,7 @@ packages:
       '@modelcontextprotocol/sdk': 1.26.0
       elysia: '>=1'
       express: '>=5'
-      hono: '>=4.12.21'
+      hono: '>=4.12.27'
       viem: '>=2.47.5'
     peerDependenciesMeta:
       '@modelcontextprotocol/sdk':
@@ -5484,9 +5459,6 @@ packages:
     resolution: {integrity: sha512-s+w+rBWnpTMwSFbaE0UXsRlg7hU4FjekKU4eyAih5T8nJuNZT1nNsskXpxmeqSK9UzkBl6UgRlnKc8hz8IEqOw==}
     hasBin: true
 
-  node-releases@2.0.27:
-    resolution: {integrity: sha512-nmh3lCkYZ3grZvqcCH+fjmQ7X+H0OeZgP40OierEaAptX4XofMh5kwNbWh7lBduUzCcV/8kZ+NDLCwm2iorIlA==}
-
   node-releases@2.0.50:
     resolution: {integrity: sha512-J6l92tKHX6w8Jy5nO1Vuc01NoIiRGi/d6qBKVxh+IQ8Cr3b6HbVNfKiF8ZpFKufTwpwxMmce2W3iQZ861ZRyTg==}
     engines: {node: '>=18'}
@@ -5581,14 +5553,6 @@ packages:
       typescript:
         optional: true
 
-  ox@0.14.20:
-    resolution: {integrity: sha512-rby38C3nDn8eQkf29Zgw4hkCZJ64Qqi0zRPWL8ENUQ7JVuoITqrVtwWQgM/He19SCMUEc7hS/Sjw0jIOSLJhOw==}
-    peerDependencies:
-      typescript: ^5.9.3
-    peerDependenciesMeta:
-      typescript:
-        optional: true
-
   ox@0.14.24:
     resolution: {integrity: sha512-mviaFeN/cSkj/1B7EJKB3fYzQ4E3y7CDmR7Iqei1QUT0M1Zkuo0kNI/ewBnShf7h5r57gp68/DFltjNu5HJCYQ==}
     peerDependencies:
@@ -6528,10 +6492,6 @@ packages:
   tailwindcss@4.3.1:
     resolution: {integrity: sha512-hk+TB1m+K8CYNrP6rjQaq/Y+4Zylwpa87mLYBKCunwnnQ9p+fHb7kmSfGqyEJoxF/O6CDyABWVFEafNSYKll+Q==}
 
-  tapable@2.3.0:
-    resolution: {integrity: sha512-g9ljZiwki/LfxmQADO3dEY1CbpmXT5Hm2fJ+QaGKwSXUylMybePR7/67YW7jOrrvjEgL1Fmz5kzyAjWVWLlucg==}
-    engines: {node: '>=6'}
-
   tapable@2.3.3:
     resolution: {integrity: sha512-uxc/zpqFg6x7C8vOE7lh6Lbda8eEL9zmVm/PLeTPBRhh1xCgdWaQ+J1CUieGpIfm2HdtsUpRv+HshiasBMcc6A==}
     engines: {node: '>=6'}
@@ -6911,16 +6871,16 @@ packages:
   vfile@6.0.3:
     resolution: {integrity: sha512-KzIbH/9tXat2u30jf+smMwFCsno4wHVdNmzFyL+T/L3UGqqk6JKfVqOFOZEpZSHADH1k40ab6NUIXZq422ov3Q==}
 
-  viem@2.48.8:
-    resolution: {integrity: sha512-Xj3Nrt66SKtn06kczU91ELn9Difr84ZM5A62BTlaisT5lpgt058i2mBkfMZCXHGb1ocOLjzC2ztPhD0Lvky7uQ==}
+  viem@2.54.6:
+    resolution: {integrity: sha512-OfybECKJYVmhiNqz+SHhed+O2h6niQ+0Wjg9J0b4bV+/QrvLgjxhfKO7hZqsuK1YtZ/0BErBKy708Zp+cU5T0Q==}
     peerDependencies:
       typescript: ^5.9.3
     peerDependenciesMeta:
       typescript:
         optional: true
 
-  viem@2.54.6:
-    resolution: {integrity: sha512-OfybECKJYVmhiNqz+SHhed+O2h6niQ+0Wjg9J0b4bV+/QrvLgjxhfKO7hZqsuK1YtZ/0BErBKy708Zp+cU5T0Q==}
+  viem@2.55.4:
+    resolution: {integrity: sha512-iSVcFADHPS0GRcY+YMGubuOH0QXcLN87HVlPNaFLPzJv6OzNOql2cim+QxtTe/QxXUqbXLnzTmpFms4PLGyJ6A==}
     peerDependencies:
       typescript: ^5.9.3
     peerDependenciesMeta:
@@ -7921,7 +7881,7 @@ snapshots:
     dependencies:
       ajv: 8.18.0
       ajv-formats: 3.0.1
-      fast-uri: 3.1.2
+      fast-uri: 3.1.3
 
   '@fastify/error@4.2.0': {}
 
@@ -8014,10 +7974,6 @@ snapshots:
       '@tanstack/vue-virtual': 3.13.30(vue@3.5.39(typescript@5.9.3))
       vue: 3.5.39(typescript@5.9.3)
 
-  '@hono/node-server@1.19.13(hono@4.12.27)':
-    dependencies:
-      hono: 4.12.27
-
   '@hono/node-server@2.0.6(hono@4.12.27)':
     dependencies:
       hono: 4.12.27
@@ -8311,7 +8267,7 @@ snapshots:
 
   '@modelcontextprotocol/sdk@1.26.0(@cfworker/json-schema@4.1.1)':
     dependencies:
-      '@hono/node-server': 1.19.13(hono@4.12.27)
+      '@hono/node-server': 2.0.6(hono@4.12.27)
       ajv: 8.18.0
       ajv-formats: 3.0.1
       content-type: 1.0.5
@@ -8703,7 +8659,7 @@ snapshots:
       '@opentelemetry/api': 1.7.0
       '@opentelemetry/core': 2.8.0(@opentelemetry/api@1.7.0)
 
-  '@opentelemetry/propagator-jaeger@2.7.1(@opentelemetry/api@1.7.0)':
+  '@opentelemetry/propagator-jaeger@2.9.0(@opentelemetry/api@1.7.0)':
     dependencies:
       '@opentelemetry/api': 1.7.0
       '@opentelemetry/core': 2.8.0(@opentelemetry/api@1.7.0)
@@ -8777,7 +8733,7 @@ snapshots:
       '@opentelemetry/instrumentation': 0.217.0(@opentelemetry/api@1.7.0)
       '@opentelemetry/otlp-exporter-base': 0.217.0(@opentelemetry/api@1.7.0)
       '@opentelemetry/propagator-b3': 2.7.1(@opentelemetry/api@1.7.0)
-      '@opentelemetry/propagator-jaeger': 2.7.1(@opentelemetry/api@1.7.0)
+      '@opentelemetry/propagator-jaeger': 2.9.0(@opentelemetry/api@1.7.0)
       '@opentelemetry/resources': 2.7.1(@opentelemetry/api@1.7.0)
       '@opentelemetry/sdk-logs': 0.217.0(@opentelemetry/api@1.7.0)
       '@opentelemetry/sdk-metrics': 2.7.1(@opentelemetry/api@1.7.0)
@@ -9935,7 +9891,7 @@ snapshots:
 
   '@types/react@19.0.8':
     dependencies:
-      csstype: 3.1.3
+      csstype: 3.2.3
 
   '@types/shimmer@1.2.0': {}
 
@@ -10288,10 +10244,10 @@ snapshots:
 
   accounts@0.9.0(@modelcontextprotocol/sdk@1.26.0(@cfworker/json-schema@4.1.1))(@types/react@19.0.8)(express@5.2.1)(react@19.2.6)(typescript@5.9.3)(use-sync-external-store@1.6.0(react@19.2.6))(viem@src):
     dependencies:
-      hono: 4.12.25
+      hono: 4.12.27
       idb-keyval: 6.2.2
       mipd: 0.0.7(typescript@5.9.3)
-      mppx: 0.6.5(@modelcontextprotocol/sdk@1.26.0(@cfworker/json-schema@4.1.1))(express@5.2.1)(hono@4.12.25)(typescript@5.9.3)(viem@src)
+      mppx: 0.6.5(@modelcontextprotocol/sdk@1.26.0(@cfworker/json-schema@4.1.1))(express@5.2.1)(hono@4.12.27)(typescript@5.9.3)(viem@src)
       ox: 0.14.24(typescript@5.9.3)(zod@4.3.6)
       webauthx: 0.1.2(typescript@5.9.3)(zod@4.3.6)
       zod: 4.3.6
@@ -10360,7 +10316,7 @@ snapshots:
   ajv@8.18.0:
     dependencies:
       fast-deep-equal: 3.1.3
-      fast-uri: 3.1.2
+      fast-uri: 3.1.3
       json-schema-traverse: 1.0.0
       require-from-string: 2.0.2
 
@@ -10536,14 +10492,6 @@ snapshots:
     dependencies:
       fill-range: 7.1.1
 
-  browserslist@4.28.1:
-    dependencies:
-      baseline-browser-mapping: 2.10.8
-      caniuse-lite: 1.0.30001769
-      electron-to-chromium: 1.5.286
-      node-releases: 2.0.27
-      update-browserslist-db: 1.2.3(browserslist@4.28.1)
-
   browserslist@4.28.4:
     dependencies:
       baseline-browser-mapping: 2.10.40
@@ -10775,7 +10723,7 @@ snapshots:
   cosmiconfig@8.3.6(typescript@5.9.3):
     dependencies:
       import-fresh: 3.3.1
-      js-yaml: 5.2.1
+      js-yaml: 4.3.0
       parse-json: 5.2.0
       path-type: 4.0.0
     optionalDependencies:
@@ -10806,8 +10754,6 @@ snapshots:
       shebang-command: 2.0.0
       which: 2.0.2
 
-  csstype@3.1.3: {}
-
   csstype@3.2.3: {}
 
   cva@1.0.0-beta.4(typescript@5.9.3):
@@ -10922,8 +10868,6 @@ snapshots:
 
   ee-first@1.1.1: {}
 
-  electron-to-chromium@1.5.286: {}
-
   electron-to-chromium@1.5.380: {}
 
   emoji-regex@8.0.0: {}
@@ -10938,11 +10882,6 @@ snapshots:
     dependencies:
       once: 1.4.0
 
-  enhanced-resolve@5.18.3:
-    dependencies:
-      graceful-fs: 4.2.11
-      tapable: 2.3.0
-
   enhanced-resolve@5.21.6:
     dependencies:
       graceful-fs: 4.2.11
@@ -11272,7 +11211,7 @@ snapshots:
       '@fastify/merge-json-schemas': 0.2.1
       ajv: 8.18.0
       ajv-formats: 3.0.1
-      fast-uri: 3.1.2
+      fast-uri: 3.1.3
       json-schema-ref-resolver: 3.0.0
       rfdc: 1.4.1
 
@@ -11284,7 +11223,7 @@ snapshots:
 
   fast-safe-stringify@2.1.1: {}
 
-  fast-uri@3.1.2: {}
+  fast-uri@3.1.3: {}
 
   fastify-plugin@4.5.1: {}
 
@@ -11701,8 +11640,6 @@ snapshots:
 
   highlight.js@11.11.1: {}
 
-  hono@4.12.25: {}
-
   hono@4.12.27: {}
 
   hookable@6.1.1: {}
@@ -11948,10 +11885,6 @@ snapshots:
     dependencies:
       argparse: 2.0.1
 
-  js-yaml@5.2.1:
-    dependencies:
-      argparse: 2.0.1
-
   jsesc@3.1.0: {}
 
   json-parse-even-better-errors@2.3.1: {}
@@ -12717,7 +12650,7 @@ snapshots:
 
   module-details-from-path@1.0.4: {}
 
-  mppx@0.6.5(@modelcontextprotocol/sdk@1.26.0(@cfworker/json-schema@4.1.1))(express@5.2.1)(hono@4.12.25)(typescript@5.9.3)(viem@src):
+  mppx@0.6.5(@modelcontextprotocol/sdk@1.26.0(@cfworker/json-schema@4.1.1))(express@5.2.1)(hono@4.12.27)(typescript@5.9.3)(viem@src):
     dependencies:
       incur: 0.3.25
       ox: 0.14.15(typescript@5.9.3)(zod@4.3.6)
@@ -12726,7 +12659,7 @@ snapshots:
     optionalDependencies:
       '@modelcontextprotocol/sdk': 1.26.0(@cfworker/json-schema@4.1.1)
       express: 5.2.1
-      hono: 4.12.25
+      hono: 4.12.27
     transitivePeerDependencies:
       - typescript
 
@@ -12857,8 +12790,6 @@ snapshots:
       detect-libc: 2.1.2
     optional: true
 
-  node-releases@2.0.27: {}
-
   node-releases@2.0.50: {}
 
   normalize-path@3.0.0: {}
@@ -12939,52 +12870,52 @@ snapshots:
     transitivePeerDependencies:
       - zod
 
-  ox@0.14.20(typescript@5.9.3)(zod@4.4.3):
+  ox@0.14.24(typescript@5.9.3)(zod@4.3.6):
     dependencies:
       '@adraffy/ens-normalize': 1.11.1
       '@noble/ciphers': 1.3.0
       '@noble/curves': 1.9.1
       '@noble/hashes': 1.8.0
       '@scure/bip32': 1.7.0
       '@scure/bip39': 1.6.0
-      abitype: 1.2.3(typescript@5.9.3)(zod@4.4.3)
+      abitype: 1.2.3(typescript@5.9.3)(zod@4.3.6)
       eventemitter3: 5.0.1
     optionalDependencies:
       typescript: 5.9.3
     transitivePeerDependencies:
       - zod
 
-  ox@0.14.24(typescript@5.9.3)(zod@4.3.6):
+  ox@0.14.30(typescript@5.9.3)(zod@3.25.76):
     dependencies:
       '@adraffy/ens-normalize': 1.11.1
       '@noble/ciphers': 1.3.0
       '@noble/curves': 1.9.1
       '@noble/hashes': 1.8.0
       '@scure/bip32': 1.7.0
       '@scure/bip39': 1.6.0
-      abitype: 1.2.3(typescript@5.9.3)(zod@4.3.6)
+      abitype: 1.2.3(typescript@5.9.3)(zod@3.25.76)
       eventemitter3: 5.0.1
     optionalDependencies:
       typescript: 5.9.3
     transitivePeerDependencies:
       - zod
 
-  ox@0.14.30(typescript@5.9.3)(zod@3.25.76):
+  ox@0.14.30(typescript@5.9.3)(zod@4.4.3):
     dependencies:
       '@adraffy/ens-normalize': 1.11.1
       '@noble/ciphers': 1.3.0
       '@noble/curves': 1.9.1
       '@noble/hashes': 1.8.0
       '@scure/bip32': 1.7.0
       '@scure/bip39': 1.6.0
-      abitype: 1.2.3(typescript@5.9.3)(zod@3.25.76)
+      abitype: 1.2.3(typescript@5.9.3)(zod@4.4.3)
       eventemitter3: 5.0.1
     optionalDependencies:
       typescript: 5.9.3
     transitivePeerDependencies:
       - zod
 
-  ox@0.14.30(typescript@5.9.3)(zod@4.3.6):
+  ox@0.14.31(typescript@5.9.3)(zod@4.3.6):
     dependencies:
       '@adraffy/ens-normalize': 1.11.1
       '@noble/ciphers': 1.3.0
@@ -14188,8 +14119,6 @@ snapshots:
 
   tailwindcss@4.3.1: {}
 
-  tapable@2.3.0: {}
-
   tapable@2.3.3: {}
 
   tar-fs@2.1.4:
@@ -14538,12 +14467,6 @@ snapshots:
       vite: 8.0.16(@types/node@24.13.2)(esbuild@0.28.1)(jiti@2.7.0)(terser@5.36.0)(tsx@4.22.4)(yaml@2.8.3)
       webpack: 5.104.1(esbuild@0.28.1)
 
-  update-browserslist-db@1.2.3(browserslist@4.28.1):
-    dependencies:
-      browserslist: 4.28.1
-      escalade: 3.2.0
-      picocolors: 1.1.1
-
   update-browserslist-db@1.2.3(browserslist@4.28.4):
     dependencies:
       browserslist: 4.28.4
@@ -14581,15 +14504,15 @@ snapshots:
       '@types/unist': 3.0.3
       vfile-message: 4.0.3
 
-  viem@2.48.8(typescript@5.9.3)(zod@4.4.3):
+  viem@2.54.6(typescript@5.9.3)(zod@3.25.76):
     dependencies:
       '@noble/curves': 1.9.1
       '@noble/hashes': 1.8.0
       '@scure/bip32': 1.7.0
       '@scure/bip39': 1.6.0
-      abitype: 1.2.3(typescript@5.9.3)(zod@4.4.3)
+      abitype: 1.2.3(typescript@5.9.3)(zod@3.25.76)
       isows: 1.0.7(ws@8.21.0)
-      ox: 0.14.20(typescript@5.9.3)(zod@4.4.3)
+      ox: 0.14.30(typescript@5.9.3)(zod@3.25.76)
       ws: 8.21.0
     optionalDependencies:
       typescript: 5.9.3
@@ -14598,15 +14521,15 @@ snapshots:
       - utf-8-validate
       - zod
 
-  viem@2.54.6(typescript@5.9.3)(zod@3.25.76):
+  viem@2.55.4(typescript@5.9.3)(zod@4.4.3):
     dependencies:
       '@noble/curves': 1.9.1
       '@noble/hashes': 1.8.0
       '@scure/bip32': 1.7.0
       '@scure/bip39': 1.6.0
-      abitype: 1.2.3(typescript@5.9.3)(zod@3.25.76)
+      abitype: 1.2.3(typescript@5.9.3)(zod@4.4.3)
       isows: 1.0.7(ws@8.21.0)
-      ox: 0.14.30(typescript@5.9.3)(zod@3.25.76)
+      ox: 0.14.30(typescript@5.9.3)(zod@4.4.3)
       ws: 8.21.0
     optionalDependencies:
       typescript: 5.9.3
@@ -14628,7 +14551,7 @@ snapshots:
       picomatch: 4.0.4
       postcss: 8.5.10
       rollup: 4.59.0
-      tinyglobby: 0.2.16
+      tinyglobby: 0.2.17
     optionalDependencies:
       '@types/node': 24.5.2
       fsevents: 2.3.3
@@ -14901,7 +14824,7 @@ snapshots:
 
   webauthx@0.1.2(typescript@5.9.3)(zod@4.3.6):
     dependencies:
-      ox: 0.14.30(typescript@5.9.3)(zod@4.3.6)
+      ox: 0.14.31(typescript@5.9.3)(zod@4.3.6)
     transitivePeerDependencies:
       - typescript
       - zod
@@ -14922,9 +14845,9 @@ snapshots:
       '@webassemblyjs/wasm-parser': 1.14.1
       acorn: 8.17.0
       acorn-import-phases: 1.0.4(acorn@8.17.0)
-      browserslist: 4.28.1
+      browserslist: 4.28.4
       chrome-trace-event: 1.0.4
-      enhanced-resolve: 5.18.3
+      enhanced-resolve: 5.21.6
       es-module-lexer: 2.3.0
       eslint-scope: 5.1.1
       events: 3.3.0
@@ -14935,7 +14858,7 @@ snapshots:
       mime-types: 2.1.35
       neo-async: 2.6.2
       schema-utils: 4.3.3
-      tapable: 2.3.0
+      tapable: 2.3.3
       terser-webpack-plugin: 5.3.16(webpack@5.104.1)
       watchpack: 2.5.1
       webpack-sources: 3.3.3
@@ -14954,9 +14877,9 @@ snapshots:
       '@webassemblyjs/wasm-parser': 1.14.1
       acorn: 8.17.0
       acorn-import-phases: 1.0.4(acorn@8.17.0)
-      browserslist: 4.28.1
+      browserslist: 4.28.4
       chrome-trace-event: 1.0.4
-      enhanced-resolve: 5.18.3
+      enhanced-resolve: 5.21.6
       es-module-lexer: 2.3.0
       eslint-scope: 5.1.1
       events: 3.3.0
@@ -14967,7 +14890,7 @@ snapshots:
       mime-types: 2.1.35
       neo-async: 2.6.2
       schema-utils: 4.3.3
-      tapable: 2.3.0
+      tapable: 2.3.3
       terser-webpack-plugin: 5.3.16(esbuild@0.28.1)(webpack@5.104.1(esbuild@0.28.1))
       watchpack: 2.5.1
       webpack-sources: 3.3.3
```

### pnpm-workspace.yaml
```diff
@@ -45,10 +45,11 @@ overrides:
   '@babel/runtime@<7.26.10': 7.26.10
   '@babel/core': '>=7.29.6 <8'
   '@grpc/grpc-js': '>=1.14.4'
-  '@hono/node-server@<1.19.13': 1.19.13
+  '@hono/node-server@<2.0.5': 2.0.6
   '@isaacs/brace-expansion@<=5.0.0': 5.0.1
   '@modelcontextprotocol/sdk@>=1.10.0 <=1.25.3': 1.26.0
   '@opentelemetry/core': '>=2.8.0'
+  '@opentelemetry/propagator-jaeger@<2.9.0': 2.9.0
   ajv@<8.18.0: 8.18.0
   brace-expansion@>=2.0.0 <=2.0.1: 2.0.2
   cookie@<0.7.0: ^0.7.0
@@ -67,7 +68,7 @@ overrides:
   '@opentelemetry/sdk-node@<0.217.0': 0.217.0
   find-my-way@>=5.5.0 <8.2.2: ^8.2.2
   glob@>=10.3.7 <=11.0.3: '>=11.1.0'
-  hono: '>=4.12.21'
+  hono: '>=4.12.27'
   ip-address@<=10.1.0: 10.1.1
   lodash@>=4.0.0 <=4.17.23: 4.18.1
   lodash-es@>=4.0.0 <=4.17.22: 4.17.23
@@ -114,7 +115,7 @@ overrides:
   next@>=16.0.0-beta.0 <16.2.6: 16.2.6
   react-server-dom-webpack@>=19.2.0 <19.2.6: 19.2.6
   basic-ftp@<=5.3.0: 5.3.1
-  fast-uri@<=3.1.1: 3.1.2
+  fast-uri@<=3.1.2: 3.1.3
 
 allowBuilds:
   bun: true
```
