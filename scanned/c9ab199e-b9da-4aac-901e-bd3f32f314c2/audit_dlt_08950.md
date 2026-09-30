# [?] fix(sdk): `EV5GnosisSafeTxSubmitter` crashing when creating safe transactions (#7508)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2025-12-02
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/156a37d6eb75cc49998b2c60164a5872dd081110
Type: security-commit

## Details
fix(sdk): `EV5GnosisSafeTxSubmitter` crashing when creating safe transactions (#7508)

## Patch
### .changeset/heavy-mails-care.md
```diff
@@ -0,0 +1,5 @@
+---
+"@hyperlane-xyz/sdk": minor
+---
+
+Fixed the `EV5GnosisSafeTxSubmitter` which failed to create the SAFE transactions due to incorrect typing of the SAFE sdk classes not surfacing incorrect function params when calling `Safe.createTransaction`
```

### solidity/contracts/mock/MockSafe.sol
```diff
@@ -0,0 +1,20 @@
+// SPDX-License-Identifier: Apache-2.0
+pragma solidity >=0.8.0;
+
+contract MockSafe {
+    address[] private owners;
+    uint256 private threshold;
+
+    constructor(address[] memory _owners, uint256 _threshold) {
+        owners = _owners;
+        threshold = _threshold;
+    }
+
+    function getOwners() external view returns (address[] memory) {
+        return owners;
+    }
+
+    function getThreshold() external view returns (uint256) {
+        return threshold;
+    }
+}
```

### typescript/cli/src/deploy/warp.ts
```diff
@@ -53,6 +53,7 @@ import {
   objMap,
   promiseObjAll,
   retryAsync,
+  rootLogger,
 } from '@hyperlane-xyz/utils';
 
 import { TypedAnnotatedTransaction } from '../../../sdk/dist/providers/ProviderType.js';
@@ -972,6 +973,7 @@ async function submitWarpApplyTransactions(
         100, // baseRetryMs
       );
     } catch (e) {
+      rootLogger.debug('Error in submitWarpApplyTransactions', e);
       logBlue(`Error in submitWarpApplyTransactions`, e);
       console.dir(transactions);
     }
```

### typescript/cli/src/tests/ethereum/commands/helpers.ts
```diff
@@ -1,4 +1,5 @@
 import { ethers } from 'ethers';
+import http from 'http';
 import path from 'path';
 import { $ } from 'zx';
 
@@ -18,6 +19,7 @@ import {
   XERC20VSTest,
   XERC20VSTest__factory,
 } from '@hyperlane-xyz/core';
+import { TestChainMetadata } from '@hyperlane-xyz/provider-sdk/chain';
 import {
   WarpCoreConfig,
   WarpCoreConfigSchema,
@@ -425,3 +427,74 @@ export async function hyperlaneSubmit({
         ${strategyPath ? ['--strategy', strategyPath] : []} \
         --yes`;
 }
+
+/**
+ * Creates a mock Safe Transaction Service API server.
+ */
+export async function createMockSafeApi(
+  metadata: TestChainMetadata,
+  safeAddress: Address,
+  safeOwner: Address,
+  nonce: number,
+): Promise<{
+  server: ReturnType<typeof http.createServer>;
+  url: string;
+  close: () => Promise<void>;
+}> {
+  const serviceUrl = metadata.gnosisSafeTransactionServiceUrl;
+  assert(
+    serviceUrl,
+    `Safe service url is required for running mock SAFE service for chain ${metadata.name}`,
+  );
+  const port = new URL(serviceUrl).port;
+
+  const server = http.createServer((req, res) => {
+    const url = req.url || '';
+    console.info('Mock safe API received request', req.method, url);
+
+    if (url.includes('/safes/') && url.includes('multisig-transactions')) {
+      // Mock GET /v2/safes/${address}/multisig-transactions/`
+      res.writeHead(200, { 'Content-Type': 'application/json' });
+
+      res.end(JSON.stringify({ count: 0, results: [] }));
+    } else if (url.includes('/safes/')) {
+      // Mock GET /api/v1/safes/{address}/
+      res.writeHead(200, { 'Content-Type': 'application/json' });
+      res.end(
+        JSON.stringify({
+          address: safeAddress,
+          nonce,
+          threshold: 1,
+          owners: [safeOwner],
+          masterCopy: safeAddress,
+          modules: [],
+          version: '1.3.0',
+        }),
+      );
+    } else if (url.includes('/delegates')) {
+      // Mock GET /api/v2/delegates?safe={address}
+      res.writeHead(200, { 'Content-Type': 'application/json' });
+
+      res.end(JSON.stringify({ count: 1, results: [{ delegate: safeOwner }] }));
+    } else if (
+      req.method === 'POST' &&
+      url.includes('/multisig-transactions')
+    ) {
+      // Mock POST /api/v2/safes/{address}/multisig-transactions/
+      res.writeHead(201, { 'Content-Type': 'application/json' });
+
+      res.end(JSON.stringify({ success: true }));
+    } else {
+      res.statusCode = 404;
+      res.end();
+    }
+  });
+
+  await new Promise<void>((resolve) => server.listen(port, resolve));
+
+  return {
+    server,
+    url: serviceUrl,
+    close: () => new Promise<void>((resolve) => server.close(() => resolve())),
+  };
+}
```

### typescript/cli/src/tests/ethereum/warp/apply/warp-apply-submitters.e2e-test.ts
```diff
@@ -3,12 +3,14 @@ import { Signer, Wallet, ethers } from 'ethers';
 
 import {
   InterchainAccountRouter__factory,
+  MockSafe__factory,
   TimelockController,
   TimelockController__factory,
 } from '@hyperlane-xyz/core';
 import { ChainAddresses } from '@hyperlane-xyz/registry';
 import {
   CallData,
+  ChainSubmissionStrategy,
   ChainSubmissionStrategySchema,
   DerivedCoreConfig,
   SubmissionStrategy,
@@ -38,6 +40,7 @@ import {
   TEST_CHAIN_METADATA_BY_PROTOCOL,
   TEST_CHAIN_NAMES_BY_PROTOCOL,
 } from '../../../constants.js';
+import { createMockSafeApi } from '../../commands/helpers.js';
 import { WarpTestFixture } from '../../fixtures/warp-test-fixture.js';
 
 describe('hyperlane warp apply with submitters', async function () {
@@ -57,11 +60,13 @@ describe('hyperlane warp apply with submitters', async function () {
   let chain2DomainId: Domain;
   let chain3DomainId: Domain;
   let timelockInstance: TimelockController;
+  let safeAddress: Address;
   let chain3IcaAddress: Address;
   const WARP_DEPLOY_CONFIG_PATH: string = DEFAULT_EVM_WARP_DEPLOY_PATH;
   const WARP_CORE_CONFIG_PATH: string = DEFAULT_EVM_WARP_CORE_PATH;
   const WARP_ROUTE_ID: string = DEFAULT_EVM_WARP_ID;
   const FORMATTED_TIMELOCK_SUBMITTER_STRATEGY_PATH = `${TEMP_PATH}/timelock-simple-strategy.yaml`;
+  const SAFE_TX_BUILDER_SUBMITTER_STRATEGY_PATH = `${TEMP_PATH}/gnosis-safe-strategy.yaml`;
 
   const evmChain2Core = new HyperlaneE2ECoreTestCommands(
     ProtocolType.Ethereum,
@@ -182,6 +187,13 @@ describe('hyperlane warp apply with submitters', async function () {
         ethers.constants.AddressZero,
       );
 
+    // Deploy a mock SAFE so that the SDK can check that a contract exists
+    // at the provided address successfully
+    const mockSafe = await new MockSafe__factory()
+      .connect(chain3Signer)
+      .deploy([initialOwnerAddress], 1);
+    safeAddress = mockSafe.address;
+
     // Configure ICA connections by enrolling the ICAs with each other
     const [coreConfigChain2, coreConfigChain3]: DerivedCoreConfig[] =
       await Promise.all([
@@ -371,4 +383,123 @@ describe('hyperlane warp apply with submitters', async function () {
       ).to.equal(expectedChain2Gas);
     });
   });
+
+  describe(`${TxSubmitterType.GNOSIS_TX_BUILDER}/${TxSubmitterType.GNOSIS_SAFE}`, () => {
+    let mockSafeApiServer: Awaited<ReturnType<typeof createMockSafeApi>>;
+
+    before(async function () {
+      mockSafeApiServer = await createMockSafeApi(
+        TEST_CHAIN_METADATA_BY_PROTOCOL.ethereum.CHAIN_NAME_3,
+        safeAddress,
+        initialOwnerAddress,
+        5,
+      );
+    });
+
+    after(async function () {
+      await mockSafeApiServer.close();
+    });
+
+    it('should propose the transaction file to the Safe API', async () => {
+      const warpDeployConfig = fixture.getDeployConfig();
+      warpDeployConfig[
+        TEST_CHAIN_NAMES_BY_PROTOCOL.ethereum.CHAIN_NAME_3
+      ].owner = safeAddress;
+      await deployAndExportWarpRoute();
+
+      const txBuilderStrategy: ChainSubmissionStrategy = {
+        [TEST_CHAIN_NAMES_BY_PROTOCOL.ethereum.CHAIN_NAME_3]: {
+          submitter: {
+            type: TxSubmitterType.GNOSIS_SAFE,
+            chain: TEST_CHAIN_NAMES_BY_PROTOCOL.ethereum.CHAIN_NAME_3,
+            safeAddress: safeAddress,
+          },
+        },
+      };
+
+      writeYamlOrJson(
+        SAFE_TX_BUILDER_SUBMITTER_STRATEGY_PATH,
+        txBuilderStrategy,
+      );
+
+      warpDeployConfig[
+        TEST_CHAIN_NAMES_BY_PROTOCOL.ethereum.CHAIN_NAME_3
+      ].destinationGas = {
+        [chain2DomainId]: '100000',
+      };
+      writeYamlOrJson(WARP_DEPLOY_CONFIG_PATH, warpDeployConfig);
+
+      const output = await evmWarpCommands.applyRaw({
+        warpRouteId: WARP_ROUTE_ID,
+        strategyUrl: SAFE_TX_BUILDER_SUBMITTER_STRATEGY_PATH,
+        hypKey: HYP_KEY_BY_PROTOCOL.ethereum,
+      });
+
+      expect(output.text()).not.to.include(
+        'Error in submitWarpApplyTransactions Error:',
+      );
+    });
+
+    it('should generate the JSON transaction file to be submitted to the Safe Transaction Builder', async () => {
+      const warpDeployConfig = fixture.getDeployConfig();
+      warpDeployConfig[
+        TEST_CHAIN_NAMES_BY_PROTOCOL.ethereum.CHAIN_NAME_3
+      ].owner = safeAddress;
+      await deployAndExportWarpRoute();
+
+      const txBuilderStrategy: ChainSubmissionStrategy = {
+        [TEST_CHAIN_NAMES_BY_PROTOCOL.ethereum.CHAIN_NAME_3]: {
+          submitter: {
+            type: TxSubmitterType.GNOSIS_TX_BUILDER,
+            chain: TEST_CHAIN_NAMES_BY_PROTOCOL.ethereum.CHAIN_NAME_3,
+            safeAddress: safeAddress,
+            version: '1.0',
+          },
+        },
+      };
+
+      writeYamlOrJson(
+        SAFE_TX_BUILDER_SUBMITTER_STRATEGY_PATH,
+        txBuilderStrategy,
+      );
+
+      warpDeployConfig[
+        TEST_CHAIN_NAMES_BY_PROTOCOL.ethereum.CHAIN_NAME_3
+      ].destinationGas = {
+        [chain2DomainId]: '100000',
+      };
+      writeYamlOrJson(WARP_DEPLOY_CONFIG_PATH, warpDeployConfig);
+
+      const result = await evmWarpCommands.applyRaw({
+        warpRouteId: WARP_ROUTE_ID,
+        strategyUrl: SAFE_TX_BUILDER_SUBMITTER_STRATEGY_PATH,
+        hypKey: HYP_KEY_BY_PROTOCOL.ethereum,
+      });
+
+      // Extract the transaction file from the logs
+      const output = result.text();
+      const filePathMatch = output.match(
+        /Transaction receipts.*successfully written to (.*-gnosisSafeTxBuilder-.*\.json)/,
+      );
+      assert(
+        filePathMatch,
+        'Expected transaction receipts file path in output',
+      );
+      const [, filePath] = filePathMatch;
+
+      // Read the exported JSON file
+      const txBuilderJson: {
+        version: string;
+        chainId: string;
+        transactions: { to: string; data: string }[];
+      } = readYamlOrJson(filePath);
+
+      // Verify Safe Transaction Builder JSON format
+      expect(txBuilderJson).to.have.property('version', '1.0');
+      expect(txBuilderJson).to.have.property('chainId');
+      expect(txBuilderJson).to.have.property('transactions');
+      expect(txBuilderJson.transactions).to.be.an('array');
+      expect(txBuilderJson.transactions.length).to.equal(1);
+    });
+  });
 });
```

### typescript/cli/test-configs/test-registry/chains/anvil3/metadata.yaml
```diff
@@ -23,3 +23,4 @@ nativeToken:
   name: Ether
   symbol: ETH
   decimals: 18
+gnosisSafeTransactionServiceUrl: http://127.0.0.1:2496
```

### typescript/provider-sdk/src/chain.ts
```diff
@@ -40,6 +40,7 @@ export interface TestChainMetadata extends ChainMetadataForAltVM {
   rpcPort: number;
   rpcUrl: string;
   restPort: number;
+  gnosisSafeTransactionServiceUrl?: string;
 }
 
 /**
```

### typescript/sdk/src/providers/transactions/submitter/ethersV5/EV5GnosisSafeTxBuilder.ts
```diff
@@ -1,9 +1,9 @@
+import SafeApiKit from '@safe-global/api-kit';
+import Safe from '@safe-global/protocol-kit';
 import { SafeTransactionData } from '@safe-global/safe-core-sdk-types';
 
 import { assert } from '@hyperlane-xyz/utils';
 
-// prettier-ignore
-// @ts-ignore
 import { getSafe, getSafeService } from '../../../../utils/gnosisSafe.js';
 import { MultiProvider } from '../../../MultiProvider.js';
 import { AnnotatedEV5Transaction } from '../../../ProviderType.js';
@@ -30,8 +30,8 @@ export class EV5GnosisSafeTxBuilder extends EV5GnosisSafeTxSubmitter {
   constructor(
     public readonly multiProvider: MultiProvider,
     public readonly props: EV5GnosisSafeTxBuilderProps,
-    safe: any,
-    safeService: any,
+    safe: Safe.default,
+    safeService: SafeApiKit.default,
   ) {
     super(multiProvider, props, safe, safeService);
   }
```

### typescript/sdk/src/providers/transactions/submitter/ethersV5/EV5GnosisSafeTxSubmitter.ts
```diff
@@ -1,14 +1,18 @@
+import SafeApiKit from '@safe-global/api-kit';
+import Safe from '@safe-global/protocol-kit';
 import {
-  OperationType,
+  MetaTransactionData,
   SafeTransaction,
 } from '@safe-global/safe-core-sdk-types';
 import { Logger } from 'pino';
 
 import { Address, assert, rootLogger } from '@hyperlane-xyz/utils';
 
-// prettier-ignore
-// @ts-ignore
-import { canProposeSafeTransactions, getSafe, getSafeService } from '../../../../utils/gnosisSafe.js';
+import {
+  canProposeSafeTransactions,
+  getSafe,
+  getSafeService,
+} from '../../../../utils/gnosisSafe.js';
 import { MultiProvider } from '../../../MultiProvider.js';
 import { AnnotatedEV5Transaction } from '../../../ProviderType.js';
 import { TxSubmitterType } from '../TxSubmitterTypes.js';
@@ -27,8 +31,8 @@ export class EV5GnosisSafeTxSubmitter implements EV5TxSubmitterInterface {
   constructor(
     public readonly multiProvider: MultiProvider,
     public readonly props: EV5GnosisSafeTxSubmitterProps,
-    private safe: any,
-    private safeService: any,
+    private safe: Safe.default,
+    private safeService: SafeApiKit.default,
   ) {}
 
   static async create(
@@ -67,7 +71,11 @@ export class EV5GnosisSafeTxSubmitter implements EV5TxSubmitterInterface {
   }
 
   protected async getNextNonce(): Promise<number> {
-    return await this.safeService.getNextNonce(this.props.safeAddress);
+    const nextNonce = await this.safeService.getNextNonce(
+      this.props.safeAddress,
+    );
+
+    return parseInt(nextNonce);
   }
 
   public async createSafeTransaction(
@@ -77,25 +85,30 @@ export class EV5GnosisSafeTxSubmitter implements EV5TxSubmitterInterface {
     const submitterChainId = this.multiProvider.getChainId(this.props.chain);
 
     const safeTransactionData = transactions.map(
-      ({ to, data, value, chainId }) => {
+      ({ to, data, value, chainId }): MetaTransactionData => {
         assert(chainId, 'Invalid AnnotatedEV5Transaction: chainId is required');
         assert(
           chainId === submitterChainId,
           `Invalid AnnotatedEV5Transaction: Cannot submit tx for chain ID ${chainId} to submitter for chain ID ${submitterChainId}.`,
         );
+        assert(
+          data,
+          `Invalid AnnotatedEV5Transaction: calldata is required for gnosis safe transaction on chain with ID ${submitterChainId}`,
+        );
+        assert(
+          to,
+          `Invalid AnnotatedEV5Transaction: target address is required for gnosis safe transaction on chain with ID ${submitterChainId}`,
+        );
         return { to, data, value: value?.toString() ?? '0' };
       },
     );
 
     const isMultiSend = transactions.length > 1;
     const safeTransaction = await this.safe.createTransaction({
-      safeTransactionData,
+      transactions: safeTransactionData,
       onlyCalls: isMultiSend,
       options: {
         nonce: nextNonce,
-        operation: isMultiSend
-          ? OperationType.DelegateCall
-          : OperationType.Call,
       },
     });
 
```

### typescript/sdk/src/utils/gnosisSafe.ts
```diff
@@ -14,7 +14,10 @@ export function safeApiKeyRequired(txServiceUrl: string): boolean {
   return /safe\.global|5afe\.dev/.test(txServiceUrl);
 }
 
-export function getSafeService(chain: ChainName, multiProvider: MultiProvider) {
+export function getSafeService(
+  chain: ChainName,
+  multiProvider: MultiProvider,
+): SafeApiKit.default {
   const { gnosisSafeTransactionServiceUrl, gnosisSafeApiKey } =
     multiProvider.getChainMetadata(chain);
   let txServiceUrl = gnosisSafeTransactionServiceUrl;
@@ -99,7 +102,7 @@ export async function getSafe(
   multiProvider: MultiProvider,
   safeAddress: Address,
   signer?: SafeProviderConfig['signer'],
-) {
+): Promise<Safe.default> {
   // Get the chain id for the given chain
   const chainId = `${multiProvider.getEvmChainId(chain)}`;
 
@@ -155,7 +158,7 @@ export async function getSafe(
 export async function getSafeDelegates(
   service: SafeApiKit.default,
   safeAddress: Address,
-) {
+): Promise<string[]> {
   const delegateResponse = await service.getSafeDelegates({ safeAddress });
   return delegateResponse.results.map((r) => r.delegate);
 }
@@ -165,7 +168,7 @@ export async function canProposeSafeTransactions(
   chain: ChainName,
   multiProvider: MultiProvider,
   safeAddress: Address,
-) {
+): Promise<boolean> {
   let safeService: SafeApiKit.default;
   try {
     safeService = getSafeService(chain, multiProvider);
```
