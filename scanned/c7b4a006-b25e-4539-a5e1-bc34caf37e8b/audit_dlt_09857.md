# [?] fix(turbo): Fix `GHSA-22cc-p3c6-wpvm` and `GHSA-677m-j7p3-52f9` (#10781)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-03-19
Source: https://github.com/iotaledger/iota/commit/bfb3ee8b534abbc9c67994422024826d73770f25
Type: security-commit

## Details
fix(turbo): Fix `GHSA-22cc-p3c6-wpvm` and `GHSA-677m-j7p3-52f9` (#10781)

Fixes
https://github.com/iotaledger/iota/actions/runs/23267472951/job/67651877123#step:6:39

## Patch
### package.json
```diff
@@ -45,12 +45,13 @@
 			"glob@>=10.2.0 <10.5.0": "10.5.0",
 			"qs@<6.14.1": "6.14.1",
 			"preact@>=10.28.0 <10.28.2": "10.28.2",
-			"h3@<=1.15.4": "1.15.5",
+			"h3@<1.15.6": "1.15.8",
 			"minimatch@>=3.0.0": "^3.1.5",
 			"minimatch@>=5.0.0": "^5.1.9",
 			"minimatch@>=9.0.0": "^9.0.9",
 			"hono@<4.12.4": ">=4.12.4",
-			"axios@<0.30.3": "^0.30.3"
+			"axios@<0.30.3": "^0.30.3",
+			"socket.io-parser@<4.2.6": "4.2.6"
 		}
 	},
 	"engines": {
```

### pnpm-lock.yaml
```diff
@@ -20,12 +20,13 @@ overrides:
   glob@>=10.2.0 <10.5.0: 10.5.0
   qs@<6.14.1: 6.14.1
   preact@>=10.28.0 <10.28.2: 10.28.2
-  h3@<=1.15.4: 1.15.5
+  h3@<1.15.6: 1.15.8
   minimatch@>=3.0.0: ^3.1.5
   minimatch@>=5.0.0: ^5.1.9
   minimatch@>=9.0.0: ^9.0.9
   hono@<4.12.4: '>=4.12.4'
   axios@<0.30.3: ^0.30.3
+  socket.io-parser@<4.2.6: 4.2.6
 
 importers:
 
@@ -14544,8 +14545,8 @@ packages:
     resolution: {integrity: sha512-ax7ZYomf6jqPTQ4+XCpUGyXKHk5WweS+e05MBO4/y3WJ5RkmPXNKvX+bx1behVILVwr6JSQvZAku021CHPXG3Q==}
     engines: {node: '>=10'}
 
-  h3@1.15.5:
-    resolution: {integrity: sha512-xEyq3rSl+dhGX2Lm0+eFQIAzlDN6Fs0EcC4f7BNUmzaRX/PTzeuM+Tr2lHB8FoXggsQIeXLj8EDVgs5ywxyxmg==}
+  h3@1.15.8:
+    resolution: {integrity: sha512-iOH6Vl8mGd9nNfu9C0IZ+GuOAfJHcyf3VriQxWaSWIB76Fg4BnFuk4cxBxjmQSSxJS664+pgjP6e7VBnUzFfcg==}
 
   hachure-fill@0.5.2:
     resolution: {integrity: sha512-3GKBOn+m2LX9iq+JC1064cSFprJY4jL1jCXTcpnfER5HYE2l/4EfWSGzkPa/ZDBmYI0ZOEj5VHV/eKnPGkHuOg==}
@@ -19789,8 +19790,8 @@ packages:
     resolution: {integrity: sha512-hJVXfu3E28NmzGk8o1sHhN3om52tRvwYeidbj7xKy2eIIse5IoKX3USlS6Tqt3BHAtflLIkCQBkzVrEEfWUyYQ==}
     engines: {node: '>=10.0.0'}
 
-  socket.io-parser@4.2.4:
-    resolution: {integrity: sha512-/GbIKmo8ioc+NIWIhwdecY0ge+qVBSMdgxGygevmdHj24bsfgtCmcUUcQ5ZzcylGFHsN3k4HB4Cgkl96KVnuew==}
+  socket.io-parser@4.2.6:
+    resolution: {integrity: sha512-asJqbVBDsBCJx0pTqw3WfesSY0iRX+2xzWEWzrpcH7L6fLzrhyF8WPI8UaeM4YCuDfpwA/cgsdugMsmtz8EJeg==}
     engines: {node: '>=10.0.0'}
 
   sockjs@0.3.24:
@@ -39404,7 +39405,7 @@ snapshots:
     dependencies:
       duplexer: 0.1.2
 
-  h3@1.15.5:
+  h3@1.15.8:
     dependencies:
       cookie-es: 1.2.2
       crossws: 0.3.5
@@ -46069,16 +46070,16 @@ snapshots:
       '@socket.io/component-emitter': 3.1.2
       debug: 4.3.7
       engine.io-client: 6.6.3(bufferutil@4.0.9)(utf-8-validate@5.0.10)
-      socket.io-parser: 4.2.4
+      socket.io-parser: 4.2.6
     transitivePeerDependencies:
       - bufferutil
       - supports-color
       - utf-8-validate
 
-  socket.io-parser@4.2.4:
+  socket.io-parser@4.2.6:
     dependencies:
       '@socket.io/component-emitter': 3.1.2
-      debug: 4.3.7
+      debug: 4.4.3(supports-color@8.1.1)
     transitivePeerDependencies:
       - supports-color
 
@@ -47477,7 +47478,7 @@ snapshots:
       anymatch: 3.1.3
       chokidar: 4.0.3
       destr: 2.0.5
-      h3: 1.15.5
+      h3: 1.15.8
       lru-cache: 10.4.3
       node-fetch-native: 1.6.6
       ofetch: 1.4.1
@@ -48712,10 +48713,10 @@ snapshots:
       '@webassemblyjs/wasm-parser': 1.12.1
       acorn: 8.15.0
       acorn-import-attributes: 1.9.5(acorn@8.15.0)
-      browserslist: 4.28.1
+      browserslist: 4.24.0
       chrome-trace-event: 1.0.4
       enhanced-resolve: 5.17.1
-      es-module-lexer: 1.7.0
+      es-module-lexer: 1.5.4
       eslint-scope: 5.1.1
       events: 3.3.0
       glob-to-regexp: 0.4.1
@@ -48727,7 +48728,7 @@ snapshots:
       schema-utils: 3.3.0
       tapable: 2.2.1
       terser-webpack-plugin: 5.3.10(@swc/core@1.15.11(@swc/helpers@0.5.18))(webpack@5.95.0(@swc/core@1.15.11(@swc/helpers@0.5.18)))
-      watchpack: 2.5.1
+      watchpack: 2.4.2
       webpack-sources: 3.2.3
     transitivePeerDependencies:
       - '@swc/core'
```
