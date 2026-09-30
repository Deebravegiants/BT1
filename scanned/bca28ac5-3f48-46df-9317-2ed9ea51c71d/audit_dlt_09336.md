# [?] Merge branch 'v-next' into fix-node-crash

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2025-07-14
Source: https://github.com/NomicFoundation/hardhat/commit/9f162eca0b449786174ac1145aa832007e899e19
Type: security-commit

## Details
Merge branch 'v-next' into fix-node-crash

## Patch
### .changeset/chilly-moose-know.md
```diff
@@ -0,0 +1,5 @@
+---
+"@nomicfoundation/hardhat-verify": patch
+---
+
+Use input fqn in etherscan verification
```

### .changeset/e4584a9c-37b1-4fe2-b8d2-d0522f7393d0.md
```diff
@@ -0,0 +1,3 @@
+---
+"@nomicfoundation/hardhat-toolbox-viem": patch
+---
```

### .changeset/fluffy-glasses-beam.md
```diff
@@ -1,5 +1,4 @@
 ---
-"@nomicfoundation/config": patch
 "hardhat": patch
 ---
 
```

### .changeset/green-hornets-joke.md
```diff
@@ -0,0 +1,6 @@
+---
+"@nomicfoundation/hardhat-errors": patch
+"hardhat": patch
+---
+
+Added support for short option names
```

### .changeset/long-bats-nail.md
```diff
@@ -0,0 +1,6 @@
+---
+"hardhat": patch
+"@nomicfoundation/hardhat-typechain": patch
+---
+
+Added FLAG and LEVEL arguments types
```

### .changeset/pre.json
```diff
@@ -62,12 +62,14 @@
     "calm-clouds-work",
     "cebfba78-9948-4d0d-9d22-ec79652903e2",
     "chatty-rocks-reply",
+    "chilly-moose-know",
     "chilly-nails-return",
     "clean-spies-fail",
     "cool-waves-wonder",
     "curvy-chairs-protect",
     "dull-frogs-wait",
     "e342b7f0-45cb-473d-8637-02b8d1374b4a",
+    "e4584a9c-37b1-4fe2-b8d2-d0522f7393d0",
     "early-dancers-type",
     "early-wolves-move",
     "eight-buckets-know",
@@ -77,7 +79,9 @@
     "eleven-lies-sin",
     "fair-penguins-collect",
     "famous-cooks-leave",
+    "fluffy-glasses-beam",
     "forty-ghosts-breathe",
+    "forty-rings-smile",
     "friendly-beers-happen",
     "friendly-moons-jump",
     "funny-singers-collect",
@@ -95,6 +99,7 @@
     "kind-bags-yawn",
     "lemon-meals-kick",
     "long-toes-deny",
+    "lovely-lizards-decide",
     "lucky-roses-act",
     "many-wombats-grin",
     "mean-avocados-matter",
@@ -113,6 +118,8 @@
     "pretty-lizards-roll",
     "pretty-suits-swim",
     "proud-walls-pump",
+    "quiet-lemons-move",
+    "rare-hotels-carry",
     "real-frogs-buy",
     "release-3.0.0-next.2",
     "release-3.0.0-next.3",
```

### pnpm-lock.yaml
```diff
@@ -54,46 +54,46 @@ importers:
   v-next/example-project:
     devDependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-ethers':
-        specifier: workspace:^4.0.0-next.20
+        specifier: workspace:^4.0.0-next.21
         version: link:../hardhat-ethers
       '@nomicfoundation/hardhat-ethers-chai-matchers':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ethers-chai-matchers
       '@nomicfoundation/hardhat-ignition':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition
       '@nomicfoundation/hardhat-ignition-viem':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-viem
       '@nomicfoundation/hardhat-keystore':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-keystore
       '@nomicfoundation/hardhat-mocha':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-mocha
       '@nomicfoundation/hardhat-network-helpers':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-network-helpers
       '@nomicfoundation/hardhat-node-test-runner':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-runner
       '@nomicfoundation/hardhat-typechain':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-typechain
       '@nomicfoundation/hardhat-verify':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-verify
       '@nomicfoundation/hardhat-viem':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-viem
       '@nomicfoundation/hardhat-viem-assertions':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-viem-assertions
       '@nomicfoundation/ignition-core':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-core
       '@openzeppelin/contracts':
         specifier: 5.1.0
@@ -120,7 +120,7 @@ importers:
         specifier: foundry-rs/forge-std#v1.9.4
         version: https://codeload.github.com/foundry-rs/forge-std/tar.gz/1eea5bae12ae557d589f9f0f0edae2faa47cb262
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       mocha:
         specifier: ^11.0.0
@@ -147,13 +147,13 @@ importers:
         specifier: 0.13.0-alpha.6
         version: 0.13.0-alpha.6
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/hardhat-zod-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-zod-utils
       '@nomicfoundation/solidity-analyzer':
         specifier: ^0.1.1
@@ -199,7 +199,7 @@ importers:
         version: 3.24.1
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -241,11 +241,11 @@ importers:
   v-next/hardhat-errors:
     dependencies:
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@types/node':
         specifier: ^20.14.9
@@ -275,10 +275,10 @@ importers:
   v-next/hardhat-ethers:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       debug:
         specifier: ^4.3.2
@@ -290,11 +290,11 @@ importers:
         specifier: ^6.14.0
         version: 6.14.1
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -330,13 +330,13 @@ importers:
   v-next/hardhat-ethers-chai-matchers:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-ethers':
-        specifier: workspace:^4.0.0-next.20
+        specifier: workspace:^4.0.0-next.21
         version: link:../hardhat-ethers
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@types/chai-as-promised':
         specifier: ^8.0.1
@@ -354,14 +354,14 @@ importers:
         specifier: ^6.14.0
         version: 6.14.1
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
     devDependencies:
       '@nomicfoundation/hardhat-mocha':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-mocha
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -409,16 +409,16 @@ importers:
   v-next/hardhat-ignition:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/ignition-core':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-core
       '@nomicfoundation/ignition-ui':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-ui
       chalk:
         specifier: ^5.3.0
@@ -437,7 +437,7 @@ importers:
         specifier: 1.0.2
         version: 1.0.2(nyc@15.1.0)
       '@nomicfoundation/hardhat-network-helpers':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-network-helpers
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -476,7 +476,7 @@ importers:
         specifier: 9.25.1
         version: 9.25.1
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       mocha:
         specifier: ^11.0.0
@@ -509,10 +509,10 @@ importers:
         specifier: 5.6.1
         version: 5.6.1
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/solidity-analyzer':
         specifier: ^0.1.1
@@ -600,26 +600,26 @@ importers:
   v-next/hardhat-ignition-ethers:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
     devDependencies:
       '@istanbuljs/nyc-config-typescript':
         specifier: 1.0.2
         version: 1.0.2(nyc@15.1.0)
       '@nomicfoundation/hardhat-ethers':
-        specifier: workspace:^4.0.0-next.20
+        specifier: workspace:^4.0.0-next.21
         version: link:../hardhat-ethers
       '@nomicfoundation/hardhat-ignition':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
         version: link:../hardhat-test-utils
       '@nomicfoundation/ignition-core':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-core
       '@types/node':
         specifier: ^20.14.9
@@ -637,7 +637,7 @@ importers:
         specifier: ^6.14.0
         version: 6.14.1
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       nyc:
         specifier: 15.1.0
@@ -664,7 +664,7 @@ importers:
         specifier: ^5.0.8
         version: 5.1.1
       '@nomicfoundation/ignition-core':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-core
       '@types/chai':
         specifier: ^4.2.0
@@ -742,26 +742,26 @@ importers:
   v-next/hardhat-ignition-viem:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
     devDependencies:
       '@istanbuljs/nyc-config-typescript':
         specifier: 1.0.2
         version: 1.0.2(nyc@15.1.0)
       '@nomicfoundation/hardhat-ignition':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
         version: link:../hardhat-test-utils
       '@nomicfoundation/hardhat-viem':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-viem
       '@nomicfoundation/ignition-core':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-core
       '@types/node':
         specifier: ^20.14.9
@@ -776,7 +776,7 @@ importers:
         specifier: 9.25.1
         version: 9.25.1
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       nyc:
         specifier: 15.1.0
@@ -809,13 +809,13 @@ importers:
         specifier: 1.7.1
         version: 1.7.1
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/hardhat-zod-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-zod-utils
       chalk:
         specifier: ^5.3.0
@@ -824,14 +824,14 @@ importers:
         specifier: ^4.3.2
         version: 4.4.0(supports-color@5.5.0)
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       zod:
         specifier: ^3.23.8
         version: 3.24.1
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -867,16 +867,16 @@ importers:
   v-next/hardhat-mocha:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/hardhat-zod-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-zod-utils
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       mocha:
         specifier: ^11.0.0
@@ -889,7 +889,7 @@ importers:
         version: 3.24.1
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -922,17 +922,17 @@ importers:
   v-next/hardhat-network-helpers:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -1005,19 +1005,19 @@ importers:
   v-next/hardhat-node-test-runner:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/hardhat-zod-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-zod-utils
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       tsx:
         specifier: ^4.19.3
@@ -1054,14 +1054,14 @@ importers:
   v-next/hardhat-test-utils:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@types/node':
         specifier: ^20.14.9
@@ -1091,47 +1091,47 @@ importers:
   v-next/hardhat-toolbox-mocha-ethers:
     dependencies:
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
     devDependencies:
       '@nomicfoundation/hardhat-ethers':
-        specifier: workspace:^4.0.0-next.20
+        specifier: workspace:^4.0.0-next.21
         version: link:../hardhat-ethers
       '@nomicfoundation/hardhat-ethers-chai-matchers':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ethers-chai-matchers
       '@nomicfoundation/hardhat-ignition':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition
       '@nomicfoundation/hardhat-ignition-ethers':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-ethers
       '@nomicfoundation/hardhat-keystore':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-keystore
       '@nomicfoundation/hardhat-mocha':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-mocha
       '@nomicfoundation/hardhat-network-helpers':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-network-helpers
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
         version: link:../hardhat-test-utils
       '@nomicfoundation/hardhat-typechain':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-typechain
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/hardhat-verify':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-verify
       '@nomicfoundation/ignition-core':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-core
       '@types/chai':
         specifier: ^4.2.0
@@ -1170,41 +1170,41 @@ importers:
   v-next/hardhat-toolbox-viem:
     dependencies:
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
     devDependencies:
       '@nomicfoundation/hardhat-ignition':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition
       '@nomicfoundation/hardhat-ignition-viem':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-viem
       '@nomicfoundation/hardhat-keystore':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-keystore
       '@nomicfoundation/hardhat-network-helpers':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-network-helpers
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-node-test-runner':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-runner
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
         version: link:../hardhat-test-utils
       '@nomicfoundation/hardhat-verify':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-verify
       '@nomicfoundation/hardhat-viem':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-viem
       '@nomicfoundation/hardhat-viem-assertions':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-viem-assertions
       '@nomicfoundation/ignition-core':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-ignition-core
       '@types/node':
         specifier: ^20.14.9
@@ -1237,16 +1237,16 @@ importers:
   v-next/hardhat-typechain:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-ethers':
-        specifier: workspace:^4.0.0-next.20
+        specifier: workspace:^4.0.0-next.21
         version: link:../hardhat-ethers
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/hardhat-zod-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-zod-utils
       '@typechain/ethers-v6':
         specifier: ^0.5.0
@@ -1258,7 +1258,7 @@ importers:
         specifier: ^6.14.0
         version: 6.14.1
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       typechain:
         specifier: ^8.3.1
@@ -1268,7 +1268,7 @@ importers:
         version: 3.24.1
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -1329,7 +1329,7 @@ importers:
         version: 6.21.1
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@types/bn.js':
         specifier: ^5.1.5
@@ -1368,13 +1368,13 @@ importers:
         specifier: ^5.8.0
         version: 5.8.0
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       '@nomicfoundation/hardhat-zod-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-zod-utils
       cbor2:
         specifier: ^1.9.0
@@ -1383,7 +1383,7 @@ importers:
         specifier: ^4.3.2
         version: 4.4.0(supports-color@5.5.0)
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
       semver:
         specifier: ^7.6.3
@@ -1393,7 +1393,7 @@ importers:
         version: 3.24.1
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -1432,17 +1432,17 @@ importers:
   v-next/hardhat-viem:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -1478,23 +1478,23 @@ importers:
   v-next/hardhat-viem-assertions:
     dependencies:
       '@nomicfoundation/hardhat-errors':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-errors
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
         version: link:../hardhat-test-utils
       '@nomicfoundation/hardhat-viem':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-viem
       '@types/node':
         specifier: ^20.14.9
@@ -1527,11 +1527,11 @@ importers:
   v-next/hardhat-zod-utils:
     dependencies:
       '@nomicfoundation/hardhat-utils':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-utils
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
@@ -1567,10 +1567,10 @@ importers:
   v-next/hardhat/templates/01-node-test-runner-viem:
     devDependencies:
       '@nomicfoundation/hardhat-ignition':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../../../hardhat-ignition
       '@nomicfoundation/hardhat-toolbox-viem':
-        specifier: workspace:^5.0.0-next.20
+        specifier: workspace:^5.0.0-next.21
         version: link:../../../hardhat-toolbox-viem
       '@types/node':
         specifier: ^22.8.5
@@ -1579,7 +1579,7 @@ importers:
         specifier: foundry-rs/forge-std#v1.9.4
         version: https://codeload.github.com/foundry-rs/forge-std/tar.gz/1eea5bae12ae557d589f9f0f0edae2faa47cb262
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../..
       typescript:
         specifier: ~5.8.0
@@ -1591,13 +1591,13 @@ importers:
   v-next/hardhat/templates/02-mocha-ethers:
     devDependencies:
       '@nomicfoundation/hardhat-ethers':
-        specifier: workspace:^4.0.0-next.20
+        specifier: workspace:^4.0.0-next.21
         version: link:../../../hardhat-ethers
       '@nomicfoundation/hardhat-ignition':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../../../hardhat-ignition
       '@nomicfoundation/hardhat-toolbox-mocha-ethers':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../../../hardhat-toolbox-mocha-ethers
       '@types/chai':
         specifier: ^4.2.0
@@ -1621,7 +1621,7 @@ importers:
         specifier: foundry-rs/forge-std#v1.9.4
         version: https://codeload.github.com/foundry-rs/forge-std/tar.gz/1eea5bae12ae557d589f9f0f0edae2faa47cb262
       hardhat:
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../..
       mocha:
         specifier: ^11.0.0
@@ -1633,7 +1633,7 @@ importers:
   v-next/template-package:
     devDependencies:
       '@nomicfoundation/hardhat-node-test-reporter':
-        specifier: workspace:^3.0.0-next.20
+        specifier: workspace:^3.0.0-next.21
         version: link:../hardhat-node-test-reporter
       '@nomicfoundation/hardhat-test-utils':
         specifier: workspace:^
```

### v-next/example-project/package.json
```diff
@@ -23,21 +23,21 @@
     "test": "hardhat test nodejs && hardhat test mocha"
   },
   "devDependencies": {
-    "hardhat": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-ethers-chai-matchers": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-errors": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-ethers": "workspace:^4.0.0-next.20",
-    "@nomicfoundation/hardhat-ignition": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/ignition-core": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-ignition-viem": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-keystore": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-mocha": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-network-helpers": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-node-test-runner": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-typechain": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-verify": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-viem": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-viem-assertions": "workspace:^3.0.0-next.20",
+    "hardhat": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-ethers-chai-matchers": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-errors": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-ethers": "workspace:^4.0.0-next.21",
+    "@nomicfoundation/hardhat-ignition": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/ignition-core": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-ignition-viem": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-keystore": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-mocha": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-network-helpers": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-node-test-runner": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-typechain": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-verify": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-viem": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-viem-assertions": "workspace:^3.0.0-next.21",
     "@openzeppelin/contracts": "5.1.0",
     "@types/chai": "^4.2.0",
     "@types/mocha": ">=10.0.10",
```

### v-next/hardhat-errors/package.json
```diff
@@ -1,6 +1,6 @@
 {
   "name": "@nomicfoundation/hardhat-errors",
-  "version": "3.0.0-next.20",
+  "version": "3.0.0-next.21",
   "description": "The different errors that Hardhat can throw",
   "homepage": "https://github.com/nomicfoundation/hardhat/tree/v-next/v-next/hardhat-errors",
   "repository": {
@@ -42,7 +42,7 @@
     "README.md"
   ],
   "devDependencies": {
-    "@nomicfoundation/hardhat-node-test-reporter": "workspace:^3.0.0-next.20",
+    "@nomicfoundation/hardhat-node-test-reporter": "workspace:^3.0.0-next.21",
     "@types/node": "^20.14.9",
     "c8": "^9.1.0",
     "eslint": "9.25.1",
@@ -53,6 +53,6 @@
     "typescript": "~5.8.0"
   },
   "dependencies": {
-    "@nomicfoundation/hardhat-utils": "workspace:^3.0.0-next.20"
+    "@nomicfoundation/hardhat-utils": "workspace:^3.0.0-next.21"
   }
 }
```

### v-next/hardhat-errors/src/descriptors.ts
```diff
@@ -738,6 +738,32 @@ Please double check your arguments.`,
           'The global option "--config" cannot be used with the "init" command',
         websiteDescription: `The global option "--config" cannot be used with the "init" command.
 
+Please double check your arguments.`,
+      },
+      CANNOT_GROUP_OPTIONS: {
+        number: 509,
+        messageTemplate:
+          'Invalid option "{option}". Options cannot be grouped together. Try providing the options separately.',
+        websiteTitle: "Options grouping is not supported",
+        websiteDescription: `Options cannot be grouped together.
+
+Please double check your arguments, and try providing the options separately.`,
+      },
+      CANNOT_REPEAT_OPTIONS: {
+        number: 510,
+        messageTemplate:
+          'Invalid option "{option}". Options of type "{type}" cannot be repeated.',
+        websiteTitle: "Options repetition is not supported",
+        websiteDescription: `Some options cannot be repeated.
+
+Please double check your arguments.`,
+      },
+      INVALID_SHORT_NAME: {
+        number: 511,
+        messageTemplate: `Argument short name "{name}" is invalid. It must consist of exactly one letter.`,
+        websiteTitle: "Invalid short argument name",
+        websiteDescription: `One of your Hardhat or task short argument names is invalid.
+
 Please double check your arguments.`,
       },
     },
@@ -979,7 +1005,7 @@ Remaining test suites: {suites}`,
 {error}`,
         websiteTitle: "Project file resolution error",
         websiteDescription: `There was an error while resolving the project file.
-        
+
 Please double-check your configuration. If it keeps happening, please report it.`,
       },
       NPM_ROOT_RESOLUTION_ERROR: {
@@ -989,7 +1015,7 @@ Please double-check your configuration. If it keeps happening, please report it.
 {error}`,
         websiteTitle: "Npm file resolution error",
         websiteDescription: `There was an error while resolving an npm module that you are trying to compile and generate artifacts for.
-        
+
 Please double-check your configuration. If it keeps happening, please report it.`,
       },
       IMPORT_RESOLUTION_ERROR: {
```

### v-next/hardhat-ethers-chai-matchers/package.json
```diff
@@ -1,6 +1,6 @@
 {
   "name": "@nomicfoundation/hardhat-ethers-chai-matchers",
-  "version": "3.0.0-next.20",
+  "version": "3.0.0-next.21",
   "description": "Hardhat utils for testing",
   "homepage": "https://github.com/nomicfoundation/hardhat/tree/v-next/v-next/hardhat-ethers-chai-matchers",
   "repository": {
@@ -45,8 +45,8 @@
     "README.md"
   ],
   "devDependencies": {
-    "@nomicfoundation/hardhat-mocha": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-node-test-reporter": "workspace:^3.0.0-next.20",
+    "@nomicfoundation/hardhat-mocha": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-node-test-reporter": "workspace:^3.0.0-next.21",
     "@nomicfoundation/hardhat-test-utils": "workspace:^",
     "@types/chai": "^4.2.0",
     "@types/debug": "^4.1.7",
@@ -63,15 +63,15 @@
     "typescript": "~5.8.0"
   },
   "dependencies": {
-    "@nomicfoundation/hardhat-errors": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-utils": "workspace:^3.0.0-next.20",
+    "@nomicfoundation/hardhat-errors": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-utils": "workspace:^3.0.0-next.21",
     "@types/chai-as-promised": "^8.0.1",
     "chai-as-promised": "^8.0.0",
     "deep-eql": "^5.0.1"
   },
   "peerDependencies": {
-    "hardhat": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-ethers": "workspace:^4.0.0-next.20",
+    "hardhat": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-ethers": "workspace:^4.0.0-next.21",
     "chai": "^5.1.2",
     "ethers": "^6.14.0"
   }
```

### v-next/hardhat-ethers/package.json
```diff
@@ -1,6 +1,6 @@
 {
   "name": "@nomicfoundation/hardhat-ethers",
-  "version": "4.0.0-next.20",
+  "version": "4.0.0-next.21",
   "description": "Hardhat plugin for ethers",
   "homepage": "https://github.com/nomicfoundation/hardhat/tree/v-next/v-next/hardhat-ethers",
   "repository": {
@@ -43,7 +43,7 @@
     "README.md"
   ],
   "devDependencies": {
-    "@nomicfoundation/hardhat-node-test-reporter": "workspace:^3.0.0-next.20",
+    "@nomicfoundation/hardhat-node-test-reporter": "workspace:^3.0.0-next.21",
     "@nomicfoundation/hardhat-test-utils": "workspace:^",
     "@types/debug": "^4.1.7",
     "@types/node": "^20.14.9",
@@ -56,13 +56,13 @@
     "typescript": "~5.8.0"
   },
   "dependencies": {
-    "@nomicfoundation/hardhat-errors": "workspace:^3.0.0-next.20",
-    "@nomicfoundation/hardhat-utils": "workspace:^3.0.0-next.20",
+    "@nomicfoundation/hardhat-errors": "workspace:^3.0.0-next.21",
+    "@nomicfoundation/hardhat-utils": "workspace:^3.0.0-next.21",
     "debug": "^4.3.2",
     "ethereum-cryptography": "^2.2.1",
     "ethers": "^6.14.0"
   },
   "peerDependencies": {
-    "hardhat": "workspace:^3.0.0-next.20"
+    "hardhat": "workspace:^3.0.0-next.21"
   }
 }
```
