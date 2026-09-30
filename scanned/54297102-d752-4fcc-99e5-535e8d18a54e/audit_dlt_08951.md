# [?] fix: warp read crashing when warpRouteId is provided (#7139)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2025-10-02
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/571901a6d3196ae32cfcf4e753a2659f947326ce
Type: security-commit

## Details
fix: warp read crashing when warpRouteId is provided (#7139)

## Patch
### .changeset/sharp-wombats-vanish.md
```diff
@@ -0,0 +1,5 @@
+---
+"@hyperlane-xyz/cli": minor
+---
+
+Fix warp read crashing when providing the `--warpRouteId` flag
```

### typescript/cli/src/commands/warp.ts
```diff
@@ -225,6 +225,8 @@ export const read: CommandModuleWithContext<
     address,
     config: configFilePath,
     symbol,
+    warp,
+    warpRouteId,
   }) => {
     logCommandHeader('Hyperlane Warp Reader');
 
@@ -233,6 +235,8 @@ export const read: CommandModuleWithContext<
       chain,
       address,
       symbol,
+      warpCoreConfigPath: warp,
+      warpRouteId,
     });
 
     if (configFilePath) {
```

### typescript/cli/src/read/warp.ts
```diff
@@ -17,7 +17,12 @@ import {
   TokenStandard,
   WarpCoreConfig,
 } from '@hyperlane-xyz/sdk';
-import { ProtocolType, objMap, promiseObjAll } from '@hyperlane-xyz/utils';
+import {
+  Address,
+  ProtocolType,
+  objMap,
+  promiseObjAll,
+} from '@hyperlane-xyz/utils';
 
 import { CommandContext } from '../context/types.js';
 import { logGray, logRed, logTable, warnYellow } from '../logger.js';
@@ -28,37 +33,39 @@ export async function runWarpRouteRead({
   chain,
   address,
   symbol,
+  warpRouteId,
+  warpCoreConfigPath,
 }: {
   context: CommandContext;
   chain?: ChainName;
   address?: string;
   symbol?: string;
+  warpRouteId?: string;
+  warpCoreConfigPath?: string;
 }): Promise<ChainMap<HypTokenRouterConfig>> {
-  const hasTokenSymbol = Boolean(symbol);
-  const hasChainAddress = Boolean(chain && address);
-
-  if (!hasTokenSymbol && !hasChainAddress) {
-    logRed(
-      'Invalid input parameters. Please provide either a token symbol or both chain name and token address',
+  let addresses: ChainMap<Address>;
+  let warpCoreConfig: WarpCoreConfig | undefined;
+  if (symbol || warpCoreConfigPath || warpRouteId) {
+    warpCoreConfig = await getWarpCoreConfigOrExit({
+      context,
+      symbol,
+      warp: warpCoreConfigPath,
+      warpRouteId,
+    });
+
+    addresses = Object.fromEntries(
+      warpCoreConfig.tokens.map((t) => [t.chainName, t.addressOrDenom!]),
+    );
+  } else if (chain && address) {
+    addresses = {
+      [chain]: address,
+    };
+  } else {
+    throw new Error(
+      'Invalid input parameters. Please provide either a token symbol, a warp route id or both chain name and token address',
     );
-    process.exit(1);
   }
 
-  const warpCoreConfig = hasTokenSymbol
-    ? await getWarpCoreConfigOrExit({
-        context,
-        symbol,
-      })
-    : undefined;
-
-  const addresses = warpCoreConfig
-    ? Object.fromEntries(
-        warpCoreConfig.tokens.map((t) => [t.chainName, t.addressOrDenom!]),
-      )
-    : {
-        [chain!]: address!,
-      };
-
   return deriveWarpRouteConfigs(context, addresses, warpCoreConfig);
 }
 
```

### typescript/cli/src/tests/commands/warp.ts
```diff
@@ -11,6 +11,8 @@ import { readYamlOrJson } from '../../utils/files.js';
 
 import { localTestRunCmdPrefix } from './helpers.js';
 
+$.verbose = true;
+
 export class HyperlaneE2EWarpTestCommands {
   protected cmdPrefix: string[];
 
@@ -67,17 +69,20 @@ export class HyperlaneE2EWarpTestCommands {
     warpAddress,
     symbol,
     outputPath,
+    warpRouteId,
   }: {
     chain?: string;
     symbol?: string;
     warpAddress?: string;
+    warpRouteId?: string;
     outputPath?: string;
   }): ProcessPromise {
     return $`${localTestRunCmdPrefix()} hyperlane warp read \
             --registry ${this.registryPath} \
             ${warpAddress ? ['--address', warpAddress] : []} \
             ${chain ? ['--chain', chain] : []} \
             ${symbol ? ['--symbol', symbol] : []} \
+            ${warpRouteId ? ['--warpRouteId', warpRouteId] : []} \
             --verbosity debug \
             ${outputPath || this.outputPath ? ['--config', outputPath || this.outputPath] : []}`;
   }
```

### typescript/cli/src/tests/ethereum/warp/warp-read.e2e-test.ts
```diff
@@ -90,7 +90,7 @@ describe('hyperlane warp read e2e tests', async function () {
 
       expect(output.exitCode).to.equal(1);
       expect(output.text()).to.include(
-        'Invalid input parameters. Please provide either a token symbol or both chain name and token address',
+        'Invalid input parameters. Please provide either a token symbol, a warp route id or both chain name and token address',
       );
     });
   });
@@ -166,6 +166,64 @@ describe('hyperlane warp read e2e tests', async function () {
     });
   });
 
+  describe('hyperlane warp read --warpRouteId ...', () => {
+    it('should throw an error if no warp route with the provided id exists', async () => {
+      const readOutputPath = `${TEMP_PATH}/warp-read-all-chain-with-symbol.yaml`;
+
+      await hyperlaneWarp.deploy(WARP_DEPLOY_OUTPUT_PATH, ANVIL_KEY);
+
+      const warpRouteId = 'ETH/does-not-exist';
+      const finalOutput = await hyperlaneWarp
+        .readRaw({
+          warpRouteId,
+          outputPath: readOutputPath,
+        })
+        .nothrow();
+
+      expect(finalOutput.exitCode).to.equal(1);
+      expect(finalOutput.text()).includes(
+        `No warp route found with the provided id "${warpRouteId}"`,
+      );
+    });
+
+    it('should successfully read the complete warp route config from all the chains', async () => {
+      const readOutputPath = `${TEMP_PATH}/warp-read-all-chain-with-symbol.yaml`;
+
+      const warpConfig: WarpRouteDeployConfig = {
+        [CHAIN_NAME_2]: {
+          type: TokenType.synthetic,
+          mailbox: chain2Addresses.mailbox,
+          owner: ownerAddress,
+        },
+        [CHAIN_NAME_3]: {
+          type: TokenType.native,
+          mailbox: chain3Addresses.mailbox,
+          owner: ownerAddress,
+        },
+      };
+
+      writeYamlOrJson(WARP_DEPLOY_OUTPUT_PATH, warpConfig);
+      await hyperlaneWarp.deploy(WARP_DEPLOY_OUTPUT_PATH, ANVIL_KEY);
+
+      const finalOutput = await hyperlaneWarp
+        .readRaw({
+          warpRouteId: 'ETH/warp-route-deployment',
+          outputPath: readOutputPath,
+        })
+        .nothrow();
+
+      expect(finalOutput.exitCode).to.equal(0);
+
+      const warpReadResult: WarpRouteDeployConfig =
+        readYamlOrJson(readOutputPath);
+      expect(warpReadResult[CHAIN_NAME_2]).not.to.be.undefined;
+      expect(warpReadResult[CHAIN_NAME_2].type).to.equal(TokenType.synthetic);
+
+      expect(warpReadResult[CHAIN_NAME_3]).not.to.be.undefined;
+      expect(warpReadResult[CHAIN_NAME_3].type).to.equal(TokenType.native);
+    });
+  });
+
   describe('hyperlane warp read --chain ... --config ...', () => {
     it('should be able to read a warp route', async function () {
       await hyperlaneWarp.deploy(
```

### typescript/cli/src/utils/warp.ts
```diff
@@ -31,19 +31,31 @@ export async function getWarpCoreConfigOrExit({
   context,
   symbol,
   warp,
+  warpRouteId,
 }: {
   context: CommandContext;
   symbol?: string;
   warp?: string;
+  warpRouteId?: string;
 }): Promise<WarpCoreConfig> {
   let warpCoreConfig: WarpCoreConfig;
   if (symbol) {
     warpCoreConfig = await selectRegistryWarpRoute(context.registry, symbol);
   } else if (warp) {
     warpCoreConfig = await readWarpCoreConfig({ filePath: warp });
+  } else if (warpRouteId) {
+    const maybeWarpRoute = await context.registry.getWarpRoute(warpRouteId);
+    assert(
+      maybeWarpRoute,
+      `No warp route found with the provided id "${warpRouteId}"`,
+    );
+
+    warpCoreConfig = maybeWarpRoute;
   } else {
-    logRed(`Please specify either a symbol or warp config`);
-    process.exit(0);
+    logRed(
+      `Invalid input parameters. Please provide either a token symbol, a warp route id or both chain name and token address`,
+    );
+    process.exit(1);
   }
 
   return warpCoreConfig;
```
