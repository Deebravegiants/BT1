# [?] fix(iota): bump @iota/iota-sdk to ^1.11.0 to resolve CVE-2025-66020 (#3564)

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2026-03-18
Source: https://github.com/pyth-network/pyth-crosschain/commit/104dfd7730d7cce1b98bb0b306bbfe11fb7898d9
Type: security-commit

## Details
fix(iota): bump @iota/iota-sdk to ^1.11.0 to resolve CVE-2025-66020 (#3564)

Upgrades @iota/iota-sdk from ^0.5.0 to ^1.11.0 in pyth-iota-js,
pyth-iota-cli, and contract-manager. The old 0.5.0 version pulled in
valibot@0.36.0 which is vulnerable to ReDoS (CVE-2025-66020, high
severity); 1.11.0 bumps valibot to ^1.2.0 which is the fixed version.

Also fixes the renamed getDynamicFieldObject param (parentId ->
parentObjectId) introduced in the 1.x SDK, and bumps the pyth-iota-js
package version to 2.3.0.

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

## Patch
### contract_manager/package.json
```diff
@@ -6,7 +6,7 @@
     "@cosmjs/cosmwasm-stargate": "^0.32.3",
     "@cosmjs/stargate": "^0.32.3",
     "@injectivelabs/networks": "^1.14.6",
-    "@iota/iota-sdk": "^0.5.0",
+    "@iota/iota-sdk": "^1.11.0",
     "@mysten/move-bytecode-template": "^0.3.0",
     "@mysten/sui": "^1.3.0",
     "@pythnetwork/client": "catalog:",
```

### contract_manager/src/core/contracts/iota.ts
```diff
@@ -331,7 +331,7 @@ export class IotaPriceFeedContract extends PriceFeedContract {
   async getDataSources(): Promise<DataSource[]> {
     const provider = this.getProvider();
     const result = await provider.getDynamicFieldObject({
-      parentId: this.stateId,
+      parentObjectId: this.stateId,
       name: {
         type: "vector<u8>",
         value: "data_sources",
```

### pnpm-lock.yaml
```diff
@@ -453,7 +453,7 @@ importers:
         version: 2.2.0(react@19.2.1)
       '@next/third-parties':
         specifier: 'catalog:'
-        version: 16.1.1(next@16.1.1(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(babel-plugin-react-compiler@19.1.0-rc.1)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(react@19.2.1)
+        version: 16.1.1(next@16.1.1(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(react@19.2.1)
       '@pythnetwork/client':
         specifier: 'catalog:'
         version: 2.22.1(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
@@ -1341,7 +1341,7 @@ importers:
         version: 2.2.0(react@19.2.1)
       '@next/third-parties':
         specifier: 'catalog:'
-        version: 16.1.1(next@16.1.1(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(babel-plugin-react-compiler@19.1.0-rc.1)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(react@19.2.1)
+        version: 16.1.1(next@16.1.1(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(react@19.2.1)
       '@pythnetwork/hermes-client':
         specifier: workspace:*
         version: link:../hermes/client/js
@@ -1359,13 +1359,13 @@ importers:
         version: 0.9.24(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-react':
         specifier: 'catalog:'
-        version: 0.15.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
+        version: 0.15.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
       '@solana/wallet-adapter-react-ui':
         specifier: 'catalog:'
-        version: 0.9.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
+        version: 0.9.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
       '@solana/wallet-adapter-wallets':
         specifier: 'catalog:'
-        version: 0.19.33(@babel/runtime@7.28.6)(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))(zod@3.24.4)
+        version: 0.19.33(@babel/runtime@7.28.6)(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))(zod@3.24.4)
       '@solana/web3.js':
         specifier: 'catalog:'
         version: 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
@@ -1485,8 +1485,8 @@ importers:
         specifier: ^1.14.6
         version: 1.14.47
       '@iota/iota-sdk':
-        specifier: ^0.5.0
-        version: 0.5.0(typescript@5.9.3)
+        specifier: ^1.11.0
+        version: 1.11.0(typescript@5.9.3)
       '@mysten/move-bytecode-template':
         specifier: ^0.3.0
         version: 0.3.0
@@ -1901,10 +1901,10 @@ importers:
         version: 0.15.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
       '@solana/wallet-adapter-react-ui':
         specifier: 'catalog:'
-        version: 0.9.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
+        version: 0.9.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
       '@solana/wallet-adapter-wallets':
         specifier: 'catalog:'
-        version: 0.19.33(@babel/runtime@7.28.6)(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))(zod@3.24.2)
+        version: 0.19.33(@babel/runtime@7.28.6)(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))(zod@3.24.2)
       '@solana/web3.js':
         specifier: ^1.73.0
         version: 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
@@ -2035,7 +2035,7 @@ importers:
         version: 3.10.1
       '@next/third-parties':
         specifier: 'catalog:'
-        version: 16.1.1(next@16.1.1(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(babel-plugin-react-compiler@19.1.0-rc.1)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(react@19.2.1)
+        version: 16.1.1(next@16.1.1(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(react@19.2.1)
       '@pythnetwork/react-hooks':
         specifier: 'workspace:'
         version: link:../react-hooks
@@ -2238,7 +2238,7 @@ importers:
         version: 0.2.39(@swc/core@1.15.0)
       jest:
         specifier: ^29
-        version: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+        version: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       jest-ts-webcompat-resolver:
         specifier: ^1.0.1
         version: 1.0.1(jest-resolve@29.7.0)
@@ -2254,7 +2254,7 @@ importers:
         version: 1.3.2(typescript@5.9.3)
       '@cprussin/jest-config':
         specifier: 'catalog:'
-        version: 2.0.2(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(bufferutil@4.0.9)(eslint@9.23.0(jiti@2.6.1))(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))(next@15.5.9(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(prettier@3.5.3)(typescript@5.9.3)(utf-8-validate@6.0.3)
+        version: 2.0.2(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(bufferutil@4.0.9)(eslint@9.23.0(jiti@2.6.1))(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))(next@15.5.9(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(prettier@3.5.3)(typescript@5.9.3)(utf-8-validate@6.0.3)
       '@cprussin/tsconfig':
         specifier: 'catalog:'
         version: 4.0.2(typescript@5.9.3)
@@ -2968,8 +2968,8 @@ importers:
         specifier: ^0.9.12
         version: 0.9.24(bufferutil@4.0.9)(encoding@0.1.13)(google-protobuf@3.21.4)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(typescript@5.9.3)(utf-8-validate@5.0.10)
       '@iota/iota-sdk':
-        specifier: ^0.5.0
-        version: 0.5.0(typescript@5.9.3)
+        specifier: ^1.11.0
+        version: 1.11.0(typescript@5.9.3)
       '@pythnetwork/contract-manager':
         specifier: workspace:*
         version: link:../../../contract_manager
@@ -3039,8 +3039,8 @@ importers:
   target_chains/sui/sdk/js-iota:
     dependencies:
       '@iota/iota-sdk':
-        specifier: ^0.5.0
-        version: 0.5.0(typescript@5.9.3)
+        specifier: ^1.11.0
+        version: 1.11.0(typescript@5.9.3)
       '@pythnetwork/price-service-client':
         specifier: workspace:*
         version: link:../../../../price_service/client/js
@@ -6640,12 +6640,12 @@ packages:
   '@ioredis/commands@1.3.0':
     resolution: {integrity: sha512-M/T6Zewn7sDaBQEqIZ8Rb+i9y8qfGmq+5SDFSf9sA2lUZTmdDLVdOiQaeDp+Q4wElZ9HG1GAX5KhDaidp6LQsQ==}
 
-  '@iota/bcs@0.2.1':
-    resolution: {integrity: sha512-T+iv5gZhUZP7BiDY7+Ir4MA2rYmyGNZA2b+nxjv219Fp8klFt+l38OWA+1RgJXrCmzuZ+M4hbMAeHhHziURX6Q==}
+  '@iota/bcs@1.5.0':
+    resolution: {integrity: sha512-/hv395YtUcRNLY00v7Cl2O+KvVUaUajg4OucZENgSE4Xu1ygUGsLD3dU5FixOUVOn7Abo+n7+KYr9PE/1dsvWg==}
 
-  '@iota/iota-sdk@0.5.0':
-    resolution: {integrity: sha512-ZFg4C5EuHV55fHITKOO6Mg1dLqgojZqJsDsR3SRt8W9Ofzbjt8shlM2uLNRwDpiM7GzTb4UUFcKXpOt//5gEmQ==}
-    engines: {node: '>=20'}
+  '@iota/iota-sdk@1.11.0':
+    resolution: {integrity: sha512-Fveg/4euheaBUzU1ybPyFGe7sSfLFUjLNHhPjNFUmSBOMR+l9q3LU1QdN2sLElcmgJZ+BLxAEmL8TZ0eX3Khpw==}
+    engines: {node: '>=24'}
 
   '@ipld/dag-pb@2.1.18':
     resolution: {integrity: sha512-ZBnf2fuX9y3KccADURG5vb9FaOeMjFkCrNysB0PtftME/4iCTjxfaLoNq/IAh5fTqUOMXvryN6Jyka4ZGuMLIg==}
@@ -23297,15 +23297,9 @@ snapshots:
     optionalDependencies:
       graphql: 16.13.1
 
-  '@0no-co/graphqlsp@1.12.16(graphql@16.10.0)(typescript@5.9.3)':
-    dependencies:
-      '@gql.tada/internal': 1.0.8(graphql@16.10.0)(typescript@5.9.3)
-      graphql: 16.10.0
-      typescript: 5.9.3
-
   '@0no-co/graphqlsp@1.12.16(graphql@16.13.1)(typescript@5.9.3)':
     dependencies:
-      '@gql.tada/internal': 1.0.8(graphql@16.13.1)(typescript@5.9.3)
+      '@gql.tada/internal': 1.0.8(graphql@16.10.0)(typescript@5.9.3)
       graphql: 16.13.1
       typescript: 5.9.3
 
@@ -26876,15 +26870,15 @@ snapshots:
     transitivePeerDependencies:
       - debug
 
-  '@cprussin/jest-config@2.0.2(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(bufferutil@4.0.9)(eslint@9.23.0(jiti@2.6.1))(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))(next@15.5.9(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(prettier@3.5.3)(typescript@5.9.3)(utf-8-validate@6.0.3)':
+  '@cprussin/jest-config@2.0.2(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(bufferutil@4.0.9)(eslint@9.23.0(jiti@2.6.1))(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))(next@15.5.9(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(prettier@3.5.3)(typescript@5.9.3)(utf-8-validate@6.0.3)':
     dependencies:
-      '@cprussin/jest-runner-eslint': 0.0.1(eslint@9.23.0(jiti@2.6.1))(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))
-      '@cprussin/jest-runner-prettier': 1.0.0(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))(prettier@3.5.3)
+      '@cprussin/jest-runner-eslint': 0.0.1(eslint@9.23.0(jiti@2.6.1))(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))
+      '@cprussin/jest-runner-prettier': 1.0.0(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))(prettier@3.5.3)
       '@testing-library/jest-dom': 6.6.3
-      jest: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       jest-environment-jsdom: 29.7.0(bufferutil@4.0.9)(utf-8-validate@6.0.3)
       prettier: 3.5.3
-      ts-jest: 29.3.1(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))(typescript@5.9.3)
+      ts-jest: 29.3.1(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))(typescript@5.9.3)
       typescript: 5.9.3
     optionalDependencies:
       next: 15.5.9(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1)
@@ -26902,23 +26896,23 @@ snapshots:
       - supports-color
       - utf-8-validate
 
-  '@cprussin/jest-runner-eslint@0.0.1(eslint@9.23.0(jiti@2.6.1))(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))':
+  '@cprussin/jest-runner-eslint@0.0.1(eslint@9.23.0(jiti@2.6.1))(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))':
     dependencies:
       chalk: 4.1.2
       cosmiconfig: 7.1.0
       create-jest-runner: 0.11.2
       dot-prop: 6.0.1
       eslint: 9.23.0(jiti@2.6.1)
-      jest: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
     transitivePeerDependencies:
       - '@jest/test-result'
       - jest-runner
 
-  '@cprussin/jest-runner-prettier@1.0.0(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))(prettier@3.5.3)':
+  '@cprussin/jest-runner-prettier@1.0.0(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))(prettier@3.5.3)':
     dependencies:
-      create-lite-jest-runner: 1.1.2(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))
+      create-lite-jest-runner: 1.1.2(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))
       emphasize: 5.0.0
-      jest: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       jest-diff: 29.7.0
       prettier: 3.5.3
 
@@ -28680,12 +28674,12 @@ snapshots:
 
   '@gql.tada/cli-utils@1.6.3(@0no-co/graphqlsp@1.12.16(graphql@16.10.0)(typescript@5.9.3))(graphql@16.10.0)(typescript@5.9.3)':
     dependencies:
-      '@0no-co/graphqlsp': 1.12.16(graphql@16.10.0)(typescript@5.9.3)
+      '@0no-co/graphqlsp': 1.12.16(graphql@16.13.1)(typescript@5.9.3)
       '@gql.tada/internal': 1.0.8(graphql@16.10.0)(typescript@5.9.3)
       graphql: 16.10.0
       typescript: 5.9.3
 
-  '@gql.tada/cli-utils@1.7.2(@0no-co/graphqlsp@1.12.16(graphql@16.13.1)(typescript@5.9.3))(graphql@16.13.1)(typescript@5.9.3)':
+  '@gql.tada/cli-utils@1.7.2(@0no-co/graphqlsp@1.12.16(graphql@16.10.0)(typescript@5.9.3))(graphql@16.13.1)(typescript@5.9.3)':
     dependencies:
       '@0no-co/graphqlsp': 1.12.16(graphql@16.13.1)(typescript@5.9.3)
       '@gql.tada/internal': 1.0.8(graphql@16.13.1)(typescript@5.9.3)
@@ -28700,7 +28694,7 @@ snapshots:
 
   '@gql.tada/internal@1.0.8(graphql@16.13.1)(typescript@5.9.3)':
     dependencies:
-      '@0no-co/graphql.web': 1.1.2(graphql@16.13.1)
+      '@0no-co/graphql.web': 1.1.2(graphql@16.10.0)
       graphql: 16.13.1
       typescript: 5.9.3
 
@@ -29424,24 +29418,23 @@ snapshots:
 
   '@ioredis/commands@1.3.0': {}
 
-  '@iota/bcs@0.2.1':
+  '@iota/bcs@1.5.0':
     dependencies:
-      bs58: 6.0.0
+      '@scure/base': 1.2.6
 
-  '@iota/iota-sdk@0.5.0(typescript@5.9.3)':
+  '@iota/iota-sdk@1.11.0(typescript@5.9.3)':
     dependencies:
-      '@graphql-typed-document-node/core': 3.2.0(graphql@16.10.0)
-      '@iota/bcs': 0.2.1
-      '@noble/curves': 1.8.1
-      '@noble/hashes': 1.7.1
-      '@scure/bip32': 1.6.2
-      '@scure/bip39': 1.5.4
-      '@suchipi/femver': 1.0.0
-      bech32: 2.0.0
-      gql.tada: 1.8.10(graphql@16.10.0)(typescript@5.9.3)
-      graphql: 16.10.0
-      tweetnacl: 1.0.3
-      valibot: 0.36.0
+      '@graphql-typed-document-node/core': 3.2.0(graphql@16.13.1)
+      '@iota/bcs': 1.5.0
+      '@noble/curves': 1.9.6
+      '@noble/hashes': 1.8.0
+      '@scure/base': 1.2.6
+      '@scure/bip32': 1.7.0
+      '@scure/bip39': 1.6.0
+      bignumber.js: 9.1.2
+      gql.tada: 1.9.0(graphql@16.13.1)(typescript@5.9.3)
+      graphql: 16.13.1
+      valibot: 1.2.0(typescript@5.9.3)
     transitivePeerDependencies:
       - '@gql.tada/svelte-support'
       - '@gql.tada/vue-support'
@@ -29491,7 +29484,7 @@ snapshots:
       jest-util: 29.7.0
       slash: 3.0.0
 
-  '@jest/core@29.7.0(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))':
+  '@jest/core@29.7.0(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))':
     dependencies:
       '@jest/console': 29.7.0
       '@jest/reporters': 29.7.0
@@ -29505,7 +29498,7 @@ snapshots:
       exit: 0.1.2
       graceful-fs: 4.2.11
       jest-changed-files: 29.7.0
-      jest-config: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest-config: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       jest-haste-map: 29.7.0
       jest-message-util: 29.7.0
       jest-regex-util: 29.6.3
@@ -30892,6 +30885,12 @@ snapshots:
       react: 19.2.1
       third-party-capital: 1.0.20
 
+  '@next/third-parties@16.1.1(next@16.1.1(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(react@19.2.1)':
+    dependencies:
+      next: 16.1.1(@babel/core@7.28.6)(@opentelemetry/api@1.9.0)(babel-plugin-react-compiler@19.1.0-rc.1)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1)
+      react: 19.2.1
+      third-party-capital: 1.0.20
+
   '@next/third-parties@16.1.1(next@16.1.1(@opentelemetry/api@1.9.0)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1))(react@19.2.1)':
     dependencies:
       next: 16.1.1(@opentelemetry/api@1.9.0)(babel-plugin-react-compiler@19.1.0-rc.1)(react-dom@19.2.1(react@19.2.1))(react@19.2.1)(sass@1.86.1)
@@ -31732,11 +31731,11 @@ snapshots:
       crypto-js: 4.2.0
       uuidv4: 6.2.13
 
-  '@particle-network/solana-wallet@1.3.2(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)':
+  '@particle-network/solana-wallet@1.3.2(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)':
     dependencies:
       '@particle-network/auth': 1.3.1
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
-      bs58: 5.0.0
+      bs58: 6.0.0
 
   '@paulmillr/qr@0.2.1': {}
 
@@ -35474,16 +35473,7 @@ snapshots:
       '@solana/wallet-adapter-base': 0.9.24(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
 
-  '@solana/wallet-adapter-base-ui@0.1.3(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)':
-    dependencies:
-      '@solana/wallet-adapter-react': 0.15.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
-      '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
-      react: 19.2.1
-    transitivePeerDependencies:
-      - bs58
-      - react-native
-
-  '@solana/wallet-adapter-base-ui@0.1.3(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)':
+  '@solana/wallet-adapter-base-ui@0.1.3(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)':
     dependencies:
       '@solana/wallet-adapter-react': 0.15.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
@@ -35601,9 +35591,9 @@ snapshots:
       '@solana/wallet-adapter-base': 0.9.24(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
 
-  '@solana/wallet-adapter-particle@0.1.13(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)':
+  '@solana/wallet-adapter-particle@0.1.13(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)':
     dependencies:
-      '@particle-network/solana-wallet': 1.3.2(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)
+      '@particle-network/solana-wallet': 1.3.2(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)
       '@solana/wallet-adapter-base': 0.9.24(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
     transitivePeerDependencies:
@@ -35614,22 +35604,10 @@ snapshots:
       '@solana/wallet-adapter-base': 0.9.24(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
 
-  '@solana/wallet-adapter-react-ui@0.9.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)':
-    dependencies:
-      '@solana/wallet-adapter-base': 0.9.24(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
-      '@solana/wallet-adapter-base-ui': 0.1.3(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
-      '@solana/wallet-adapter-react': 0.15.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
-      '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
-      react: 19.2.1
-      react-dom: 19.2.1(react@19.2.1)
-    transitivePeerDependencies:
-      - bs58
-      - react-native
-
-  '@solana/wallet-adapter-react-ui@0.9.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)':
+  '@solana/wallet-adapter-react-ui@0.9.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)':
     dependencies:
       '@solana/wallet-adapter-base': 0.9.24(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
-      '@solana/wallet-adapter-base-ui': 0.1.3(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
+      '@solana/wallet-adapter-base-ui': 0.1.3(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
       '@solana/wallet-adapter-react': 0.15.36(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
       react: 19.2.1
@@ -35818,7 +35796,7 @@ snapshots:
       - utf-8-validate
       - zod
 
-  '@solana/wallet-adapter-wallets@0.19.33(@babel/runtime@7.28.6)(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))(zod@3.24.4)':
+  '@solana/wallet-adapter-wallets@0.19.33(@babel/runtime@7.28.6)(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))(zod@3.24.2)':
     dependencies:
       '@solana/wallet-adapter-alpha': 0.1.11(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-avana': 0.1.14(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
@@ -35839,7 +35817,7 @@ snapshots:
       '@solana/wallet-adapter-nightly': 0.1.17(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-nufi': 0.1.18(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-onto': 0.1.8(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
-      '@solana/wallet-adapter-particle': 0.1.13(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)
+      '@solana/wallet-adapter-particle': 0.1.13(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)
       '@solana/wallet-adapter-phantom': 0.9.25(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-safepal': 0.5.19(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-saifu': 0.1.16(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
@@ -35854,7 +35832,7 @@ snapshots:
       '@solana/wallet-adapter-trezor': 0.1.3(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-trust': 0.1.14(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-unsafe-burner': 0.1.8(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
-      '@solana/wallet-adapter-walletconnect': 0.1.17(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(typescript@5.9.3)(utf-8-validate@5.0.10)(zod@3.24.4)
+      '@solana/wallet-adapter-walletconnect': 0.1.17(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(typescript@5.9.3)(utf-8-validate@5.0.10)(zod@3.24.2)
       '@solana/wallet-adapter-xdefi': 0.1.8(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
     transitivePeerDependencies:
@@ -35895,7 +35873,7 @@ snapshots:
       - ws
       - zod
 
-  '@solana/wallet-adapter-wallets@0.19.33(@babel/runtime@7.28.6)(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))(zod@3.24.2)':
+  '@solana/wallet-adapter-wallets@0.19.33(@babel/runtime@7.28.6)(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-dom@19.2.1(react@19.2.1))(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(react@19.2.1)(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))(zod@3.24.4)':
     dependencies:
       '@solana/wallet-adapter-alpha': 0.1.11(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-avana': 0.1.14(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
@@ -35916,7 +35894,7 @@ snapshots:
       '@solana/wallet-adapter-nightly': 0.1.17(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-nufi': 0.1.18(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-onto': 0.1.8(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
-      '@solana/wallet-adapter-particle': 0.1.13(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@5.0.0)
+      '@solana/wallet-adapter-particle': 0.1.13(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bs58@6.0.0)
       '@solana/wallet-adapter-phantom': 0.9.25(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-safepal': 0.5.19(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-saifu': 0.1.16(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
@@ -35931,7 +35909,7 @@ snapshots:
       '@solana/wallet-adapter-trezor': 0.1.3(@solana/sysvars@2.1.0(fastestsmallesttextencoderdecoder@1.0.22)(typescript@5.9.3))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(encoding@0.1.13)(fastestsmallesttextencoderdecoder@1.0.22)(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10))(tslib@2.8.1)(typescript@5.9.3)(utf-8-validate@5.0.10)(ws@8.19.0(bufferutil@4.0.9)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-trust': 0.1.14(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/wallet-adapter-unsafe-burner': 0.1.8(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
-      '@solana/wallet-adapter-walletconnect': 0.1.17(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(typescript@5.9.3)(utf-8-validate@5.0.10)(zod@3.24.2)
+      '@solana/wallet-adapter-walletconnect': 0.1.17(@react-native-async-storage/async-storage@1.24.0(react-native@0.78.2(@babel/core@7.28.6)(@babel/preset-env@7.29.0(@babel/core@7.28.6))(@types/react@19.2.7)(bufferutil@4.0.9)(react@19.2.1)(utf-8-validate@5.0.10)))(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))(bufferutil@4.0.9)(typescript@5.9.3)(utf-8-validate@5.0.10)(zod@3.24.4)
       '@solana/wallet-adapter-xdefi': 0.1.8(@solana/web3.js@1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10))
       '@solana/web3.js': 1.98.0(bufferutil@4.0.9)(encoding@0.1.13)(utf-8-validate@5.0.10)
     transitivePeerDependencies:
@@ -39269,13 +39247,17 @@ snapshots:
     dependencies:
       acorn: 8.15.0
 
+  acorn-import-attributes@1.9.5(acorn@8.16.0):
+    dependencies:
+      acorn: 8.16.0
+
   acorn-jsx@5.3.2(acorn@8.14.1):
     dependencies:
       acorn: 8.14.1
 
-  acorn-jsx@5.3.2(acorn@8.15.0):
+  acorn-jsx@5.3.2(acorn@8.16.0):
     dependencies:
-      acorn: 8.15.0
+      acorn: 8.16.0
 
   acorn-walk@8.3.4:
     dependencies:
@@ -41161,13 +41143,13 @@ snapshots:
       - supports-color
       - ts-node
 
-  create-jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3)):
+  create-jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)):
     dependencies:
       '@jest/types': 29.6.3
       chalk: 4.1.2
       exit: 0.1.2
       graceful-fs: 4.2.11
-      jest-config: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
+      jest-config: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       jest-util: 29.7.0
       prompts: 2.4.2
     transitivePeerDependencies:
@@ -41176,13 +41158,13 @@ snapshots:
       - supports-color
       - ts-node
 
-  create-jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)):
+  create-jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3)):
     dependencies:
       '@jest/types': 29.6.3
       chalk: 4.1.2
       exit: 0.1.2
       graceful-fs: 4.2.11
-      jest-config: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest-config: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
       jest-util: 29.7.0
       prompts: 2.4.2
     transitivePeerDependencies:
@@ -41206,9 +41188,9 @@ snapshots:
       - supports-color
       - ts-node
 
-  create-lite-jest-runner@1.1.2(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))):
+  create-lite-jest-runner@1.1.2(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))):
     dependencies:
-      jest: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       p-limit: 6.2.0
 
   create-require@1.1.1: {}
@@ -42330,8 +42312,8 @@ snapshots:
 
   espree@10.3.0:
     dependencies:
-      acorn: 8.15.0
-      acorn-jsx: 5.3.2(acorn@8.15.0)
+      acorn: 8.16.0
+      acorn-jsx: 5.3.2(acorn@8.16.0)
       eslint-visitor-keys: 4.2.0
 
   esprima@4.0.1: {}
@@ -44030,7 +44012,7 @@ snapshots:
   gql.tada@1.8.10(graphql@16.10.0)(typescript@5.9.3):
     dependencies:
       '@0no-co/graphql.web': 1.1.2(graphql@16.10.0)
-      '@0no-co/graphqlsp': 1.12.16(graphql@16.10.0)(typescript@5.9.3)
+      '@0no-co/graphqlsp': 1.12.16(graphql@16.13.1)(typescript@5.9.3)
       '@gql.tada/cli-utils': 1.6.3(@0no-co/graphqlsp@1.12.16(graphql@16.10.0)(typescript@5.9.3))(graphql@16.10.0)(typescript@5.9.3)
       '@gql.tada/internal': 1.0.8(graphql@16.10.0)(typescript@5.9.3)
       typescript: 5.9.3
@@ -44043,7 +44025,7 @@ snapshots:
     dependencies:
       '@0no-co/graphql.web': 1.1.2(graphql@16.13.1)
       '@0no-co/graphqlsp': 1.12.16(graphql@16.13.1)(typescript@5.9.3)
-      '@gql.tada/cli-utils': 1.7.2(@0no-co/graphqlsp@1.12.16(graphql@16.13.1)(typescript@5.9.3))(graphql@16.13.1)(typescript@5.9.3)
+      '@gql.tada/cli-utils': 1.7.2(@0no-co/graphqlsp@1.12.16(graphql@16.10.0)(typescript@5.9.3))(graphql@16.13.1)(typescript@5.9.3)
       '@gql.tada/internal': 1.0.8(graphql@16.13.1)(typescript@5.9.3)
       typescript: 5.9.3
     transitivePeerDependencies:
@@ -44616,8 +44598,8 @@ snapshots:
 
   import-in-the-middle@1.13.1:
     dependencies:
-      acorn: 8.15.0
-      acorn-import-attributes: 1.9.5(acorn@8.15.0)
+      acorn: 8.16.0
+      acorn-import-attributes: 1.9.5(acorn@8.16.0)
       cjs-module-lexer: 1.4.3
       module-details-from-path: 1.0.3
 
@@ -45160,16 +45142,16 @@ snapshots:
       - supports-color
       - ts-node
 
-  jest-cli@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3)):
+  jest-cli@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)):
     dependencies:
-      '@jest/core': 29.7.0(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
+      '@jest/core': 29.7.0(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       '@jest/test-result': 29.7.0
       '@jest/types': 29.6.3
       chalk: 4.1.2
-      create-jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
+      create-jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       exit: 0.1.2
       import-local: 3.2.0
-      jest-config: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
+      jest-config: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       jest-util: 29.7.0
       jest-validate: 29.7.0
       yargs: 17.7.2
@@ -45179,16 +45161,16 @@ snapshots:
       - supports-color
       - ts-node
 
-  jest-cli@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)):
+  jest-cli@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3)):
     dependencies:
-      '@jest/core': 29.7.0(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      '@jest/core': 29.7.0(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
       '@jest/test-result': 29.7.0
       '@jest/types': 29.6.3
       chalk: 4.1.2
-      create-jest: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      create-jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
       exit: 0.1.2
       import-local: 3.2.0
-      jest-config: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest-config: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
       jest-util: 29.7.0
       jest-validate: 29.7.0
       yargs: 17.7.2
@@ -45279,7 +45261,7 @@ snapshots:
       - babel-plugin-macros
       - supports-color
 
-  jest-config@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)):
+  jest-config@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)):
     dependencies:
       '@babel/core': 7.28.6
       '@jest/test-sequencer': 29.7.0
@@ -45305,7 +45287,7 @@ snapshots:
       strip-json-comments: 3.1.1
     optionalDependencies:
       '@types/node': 20.17.30
-      ts-node: 10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)
+      ts-node: 10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)
     transitivePeerDependencies:
       - babel-plugin-macros
       - supports-color
@@ -45434,37 +45416,6 @@ snapshots:
       - babel-plugin-macros
       - supports-color
 
-  jest-config@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)):
-    dependencies:
-      '@babel/core': 7.28.6
-      '@jest/test-sequencer': 29.7.0
-      '@jest/types': 29.6.3
-      babel-jest: 29.7.0(@babel/core@7.28.6)
-      chalk: 4.1.2
-      ci-info: 3.9.0
-      deepmerge: 4.3.1
-      glob: 7.2.3
-      graceful-fs: 4.2.11
-      jest-circus: 29.7.0
-      jest-environment-node: 29.7.0
-      jest-get-type: 29.6.3
-      jest-regex-util: 29.6.3
-      jest-resolve: 29.7.0
-      jest-runner: 29.7.0
-      jest-util: 29.7.0
-      jest-validate: 29.7.0
-      micromatch: 4.0.8
-      parse-json: 5.2.0
-      pretty-format: 29.7.0
-      slash: 3.0.0
-      strip-json-comments: 3.1.1
-    optionalDependencies:
-      '@types/node': 22.14.0
-      ts-node: 10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)
-    transitivePeerDependencies:
-      - babel-plugin-macros
-      - supports-color
-
   jest-config@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@22.14.0)(typescript@5.9.3)):
     dependencies:
       '@babel/core': 7.28.6
@@ -45784,24 +45735,24 @@ snapshots:
       - supports-color
       - ts-node
 
-  jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3)):
+  jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)):
     dependencies:
-      '@jest/core': 29.7.0(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
+      '@jest/core': 29.7.0(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       '@jest/types': 29.6.3
       import-local: 3.2.0
-      jest-cli: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
+      jest-cli: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
     transitivePeerDependencies:
       - '@types/node'
       - babel-plugin-macros
       - supports-color
       - ts-node
 
-  jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)):
+  jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3)):
     dependencies:
-      '@jest/core': 29.7.0(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      '@jest/core': 29.7.0(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
       '@jest/types': 29.6.3
       import-local: 3.2.0
-      jest-cli: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest-cli: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
     transitivePeerDependencies:
       - '@types/node'
       - babel-plugin-macros
@@ -51607,12 +51558,12 @@ snapshots:
       '@jest/types': 29.6.3
       babel-jest: 29.7.0(@babel/core@7.28.6)
 
-  ts-jest@29.3.1(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3)))(typescript@5.9.3):
+  ts-jest@29.3.1(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3)))(typescript@5.9.3):
     dependencies:
       bs-logger: 0.2.6
       ejs: 3.1.10
       fast-json-stable-stringify: 2.1.0
-      jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
+      jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3))
       jest-util: 29.7.0
       json5: 2.2.3
       lodash.memoize: 4.1.2
@@ -51627,12 +51578,12 @@ snapshots:
       '@jest/types': 29.6.3
       babel-jest: 29.7.0(@babel/core@7.28.6)
 
-  ts-jest@29.3.1(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(jest@29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3)))(typescript@5.9.3):
+  ts-jest@29.3.1(@babel/core@7.28.6)(@jest/transform@29.7.0)(@jest/types@29.6.3)(babel-jest@29.7.0(@babel/core@7.28.6))(jest@29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3)))(typescript@5.9.3):
     dependencies:
       bs-logger: 0.2.6
       ejs: 3.1.10
       fast-json-stable-stringify: 2.1.0
-      jest: 29.7.0(@types/node@22.14.0)(ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3))
+      jest: 29.7.0(@types/node@20.17.30)(ts-node@10.9.2(@swc/core@1.15.10)(@types/node@20.17.30)(typescript@5.9.3))
       jest-util: 29.7.0
       json5: 2.2.3
       lodash.memoize: 4.1.2
@@ -51718,14 +51669,14 @@ snapshots:
     optionalDependencies:
       '@swc/core': 1.15.10
 
-  ts-node@10.9.2(@swc/core@1.15.0)(@types/node@22.14.0)(typescript@5.9.3):
+  ts-node@10.9.2(@swc/core@1.15.0)(@types/node@20.17.30)(typescript@5.9.3):
     dependencies:
       '@cspotcode/source-map-support': 0.8.1
       '@tsconfig/node10': 1.0.11
       '@tsconfig/node12': 1.0.11
       '@tsconfig/node14': 1.0.3
       '@tsconfig/node16': 1.0.4
-      '@types/node': 22.14.0
+      '@types/node': 20.17.30
       acorn: 8.14.1
       acorn-walk: 8.3.4
       arg: 4.1.3
```

### target_chains/sui/cli-iota/package.json
```diff
@@ -1,7 +1,7 @@
 {
   "dependencies": {
     "@certusone/wormhole-sdk": "^0.9.12",
-    "@iota/iota-sdk": "^0.5.0",
+    "@iota/iota-sdk": "^1.11.0",
     "@pythnetwork/contract-manager": "workspace:*",
     "@pythnetwork/price-service-client": "^1.4.0",
     "@pythnetwork/price-service-sdk": "^1.2.0",
```

### target_chains/sui/cli-iota/tsconfig.build.json
```diff
@@ -1,15 +1,10 @@
 {
-  "extends": "./tsconfig.json",
   "compilerOptions": {
-    "noEmit": false,
-    "incremental": false,
     "declaration": true,
-    "isolatedModules": false
+    "incremental": false,
+    "isolatedModules": false,
+    "noEmit": false
   },
-  "exclude": [
-    "node_modules",
-    "dist",
-    "examples/",
-    "**/__tests__/*"
-  ]
-}
\ No newline at end of file
+  "exclude": ["node_modules", "dist", "examples/", "**/__tests__/*"],
+  "extends": "./tsconfig.json"
+}
```

### target_chains/sui/sdk/js-iota/package.json
```diff
@@ -3,7 +3,7 @@
     "name": "Pyth Data Association"
   },
   "dependencies": {
-    "@iota/iota-sdk": "^0.5.0",
+    "@iota/iota-sdk": "^1.11.0",
     "@pythnetwork/price-service-client": "workspace:*",
     "buffer": "^6.0.3"
   },
@@ -86,5 +86,5 @@
   },
   "type": "module",
   "types": "./dist/cjs/index.d.ts",
-  "version": "2.2.0"
+  "version": "2.3.0"
 }
```

### target_chains/sui/sdk/js-iota/src/client.ts
```diff
@@ -239,7 +239,7 @@ export class IotaPythClient {
     if (!this.priceFeedObjectIdCache.has(normalizedFeedId)) {
       const { id: tableId, fieldType } = await this.getPriceTableInfo();
       const result = await this.provider.getDynamicFieldObject({
-        parentId: tableId,
+        parentObjectId: tableId,
         name: {
           type: `${fieldType}::price_identifier::PriceIdentifier`,
           value: {
@@ -271,7 +271,7 @@ export class IotaPythClient {
   async getPriceTableInfo(): Promise<{ id: ObjectId; fieldType: ObjectId }> {
     if (this.priceTableInfo === undefined) {
       const result = await this.provider.getDynamicFieldObject({
-        parentId: this.pythStateId,
+        parentObjectId: this.pythStateId,
         name: {
           type: "vector<u8>",
           value: "price_info",
```
