# [?] fix(ymax-planner): Log warnings/errors rather than crashing

## Summary
Severity: Unknown
Chain: Agoric
Component: Agoric/agoric-sdk
Published: 2025-09-09
Source: https://github.com/Agoric/agoric-sdk/commit/592dbaa2081c3b35fd19aebabf48fd52ee4a51ed
Type: security-commit

## Details
fix(ymax-planner): Log warnings/errors rather than crashing

Align with https://github.com/Agoric/agoric-sdk/wiki/Logging and follow
the precedent set by Fast USDC.

## Patch
### packages/portfolio-contract/test/published-tx-shape.test.ts
```diff
@@ -0,0 +1,136 @@
+import test from 'ava';
+
+import { matches } from '@endo/patterns';
+
+import { boardSlottingMarshaller } from '@agoric/client-utils';
+import type { AccountId } from '@agoric/orchestration';
+
+import { TxType, type TxStatus } from '../src/resolver/constants.js';
+import {
+  PublishedTxShape,
+  type PublishedTx,
+  type TxId,
+} from '../src/resolver/types.ts';
+
+const marshaller = boardSlottingMarshaller();
+
+type PendingTx = { txId: TxId } & PublishedTx;
+const parsePendingTx = (txId: `tx${number}`, data): PendingTx | null => {
+  if (!matches(data, PublishedTxShape)) return null;
+  return { txId, ...data } as PendingTx;
+};
+
+export const createMockPendingTxData = ({
+  type = TxType.CCTP_TO_EVM,
+  status = 'pending',
+  amount = 100_000n,
+  destinationAddress = 'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
+}: {
+  type?: TxType;
+  status?: TxStatus;
+  amount?: bigint;
+  destinationAddress?: AccountId;
+} = {}) =>
+  harden({
+    type,
+    status,
+    amount,
+    destinationAddress,
+  });
+
+test('parsePendingTx creates valid PendingTx from data', t => {
+  const txId = 'tx1' as `tx${number}`;
+  const txData = createMockPendingTxData({ type: TxType.CCTP_TO_EVM });
+  const capData = marshaller.toCapData(txData);
+
+  const result = parsePendingTx(txId, marshaller.fromCapData(capData));
+
+  t.deepEqual(result, {
+    txId,
+    type: TxType.CCTP_TO_EVM,
+    status: 'pending',
+    amount: 1000_00n,
+    destinationAddress:
+      'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
+  });
+});
+
+test('parsePendingTx returns null for invalid data shape', t => {
+  const txId = 'tx3' as `tx${number}`;
+  const invalidTxData = harden({
+    someOtherField: 'value',
+  });
+
+  const result = parsePendingTx(txId, invalidTxData);
+
+  t.is(result, null);
+});
+
+test('parsePendingTx returns null when CCTP transaction is missing amount field', t => {
+  const txId = 'tx4' as `tx${number}`;
+  const cctpWithoutAmount = harden({
+    type: TxType.CCTP_TO_EVM,
+    status: 'pending',
+    destinationAddress:
+      'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
+  });
+
+  const result = parsePendingTx(txId, cctpWithoutAmount);
+
+  t.is(result, null);
+});
+
+test('parsePendingTx accepts GMP transaction without amount field', t => {
+  const txId = 'tx5' as `tx${number}`;
+  const gmpWithoutAmount = harden({
+    type: TxType.GMP,
+    status: 'pending',
+    destinationAddress:
+      'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
+  });
+
+  const result = parsePendingTx(txId, gmpWithoutAmount);
+
+  t.deepEqual(result, {
+    txId,
+    type: TxType.GMP,
+    status: 'pending',
+    destinationAddress:
+      'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
+  });
+});
+
+test('parsePendingTx validates Noble withdraw transactions require amount', t => {
+  const txId = 'tx1' as `tx${number}`;
+  const nobleWithdrawData = harden({
+    type: TxType.CCTP_TO_NOBLE,
+    status: 'pending',
+    destinationAddress: 'cosmos:noble:noble1abc123456789',
+  });
+  const capData = marshaller.toCapData(nobleWithdrawData);
+  const unmarshalledData = marshaller.fromCapData(capData);
+
+  const result = parsePendingTx(txId, unmarshalledData);
+
+  t.is(result, null);
+});
+
+test('parsePendingTx creates valid Noble withdraw PendingTx from data', t => {
+  const txId = 'tx1' as `tx${number}`;
+  const nobleWithdrawData = createMockPendingTxData({
+    type: TxType.CCTP_TO_NOBLE,
+    amount: 500_000n,
+    destinationAddress: 'cosmos:noble:noble1abc123456789',
+  });
+  const capData = marshaller.toCapData(nobleWithdrawData);
+
+  const result = parsePendingTx(txId, marshaller.fromCapData(capData));
+
+  t.deepEqual(result, {
+    txId,
+    type: TxType.CCTP_TO_NOBLE,
+    status: 'pending',
+    amount: 500_000n,
+    destinationAddress: 'cosmos:noble:noble1abc123456789',
+  });
+});
```

### services/ymax-planner/src/engine.ts
```diff
@@ -1,15 +1,13 @@
 /// <reference types="ses" />
 /* eslint-env node */
 
-import { log } from 'node:console';
 import { inspect } from 'node:util';
 
 import type { Coin } from '@cosmjs/stargate';
 
-import { Fail, q, X } from '@endo/errors';
+import { Fail, q } from '@endo/errors';
 import { Nat } from '@endo/nat';
 import { isPrimitive } from '@endo/pass-style';
-import { matches } from '@endo/patterns';
 import { makePromiseKit, type PromiseKit } from '@endo/promise-kit';
 
 import type { SigningSmartWalletKit, VStorage } from '@agoric/client-utils';
@@ -43,6 +41,7 @@ import {
 } from './vstorage-utils.ts';
 
 const { isInteger } = Number;
+const { entries } = Object;
 
 const sink = () => {};
 
@@ -70,12 +69,15 @@ const PathSeparator = '.';
  * cf. golang/cosmos/x/vstorage/types/path_keys.go
  */
 const encodedKeyToPath = (key: string) => {
-  const split = key.split(EncodedKeySeparator);
-  split.length > 1 || Fail`invalid encoded key ${q(key)}`;
-  const encodedPath = split.slice(1).join(EncodedKeySeparator);
-  const path = encodedPath.replaceAll(EncodedKeySeparator, PathSeparator);
+  const encodedParts = key.split(EncodedKeySeparator);
+  encodedParts.length > 1 || Fail`invalid encoded key ${q(key)}`;
+  const path = encodedParts.slice(1).join(PathSeparator);
   return path;
 };
+const pathToEncodedKey = (path: string) => {
+  const segments = path.split(PathSeparator);
+  return `${segments.length}${EncodedKeySeparator}${segments.join(EncodedKeySeparator)}`;
+};
 
 /**
  * Determine whether a dot-separated path starts with a sequence of path
@@ -275,6 +277,28 @@ const makeWorkPool = <T, U = T, M extends 'all' | 'allSettled' = 'all'>(
   return harden(results as typeof results & { done: Promise<boolean> });
 };
 
+export const makeVstorageEvent = (
+  blockHeight: bigint,
+  path: string,
+  value: any,
+  marshaller: SigningSmartWalletKit['marshaller'],
+): CosmosEvent => {
+  const streamCellJson = JSON.stringify({
+    blockHeight: String(blockHeight),
+    values: [JSON.stringify(marshaller.toCapData(value))],
+  });
+  const eventAttrs = {
+    store: 'vstorage',
+    key: pathToEncodedKey(path),
+    value: streamCellJson,
+  };
+  const event: CosmosEvent = {
+    type: 'state_change',
+    attributes: entries(eventAttrs).map(([k, v]) => ({ key: k, value: v })),
+  };
+  return event;
+};
+
 type Powers = {
   evmCtx: Omit<EvmContext, 'signingSmartWalletKit' | 'fetch' | 'cosmosRest'>;
   rpc: CosmosRPCClient;
@@ -347,53 +371,35 @@ const processPortfolioEvents = async (
   }
 };
 
-export const parsePendingTx = (txId: `tx${number}`, data): PendingTx | null => {
-  if (!matches(data, PublishedTxShape)) {
-    const err = assert.error(
-      X`expected data ${data} to match ${q(PublishedTxShape)}`,
-    );
-    console.error(err);
-    return null;
-  }
-
-  return { txId, ...data } as PendingTx;
-};
-
 export const processPendingTxEvents = async (
-  evmCtx: EvmContext,
   events: Array<{ path: string; value: string }>,
-  marshaller: SigningSmartWalletKit['marshaller'],
-  handlePendingTxFn = handlePendingTx,
-  logFn = log,
+  handlePendingTxFn,
+  powers: EvmContext & {
+    marshaller: SigningSmartWalletKit['marshaller'];
+    log?: typeof console.log;
+    error?: typeof console.error;
+  },
 ) => {
+  const { marshaller, error = () => {}, ...txPowers } = powers;
+  const { log = () => {} } = powers;
   for (const { path, value: cellJson } of events) {
-    const streamCell = parseStreamCell(cellJson, path);
-
-    // Extract txId from path (e.g., "published.ymax0.pendingTxs.tx1")
-    const txId = stripPrefix(`${PENDING_TX_PATH_PREFIX}.`, path);
-    console.warn('Processing pendingTx event', txId, path);
-
-    for (let i = 0; i < streamCell.values.length; i += 1) {
-      const value = parseStreamCellValue(streamCell, i, path);
-      const tx = parsePendingTx(
-        txId as `tx${number}`,
-        marshaller.fromCapData(value),
-      );
-      if (!tx) continue;
-
-      console.warn('Handling pending tx:', {
-        txId,
-        type: tx.type,
-        status: tx.status,
-      });
-
-      const errorHandler = error => {
-        console.error(`⚠️ Failed to process pendingTx: ${txId}`, error);
-      };
-
-      void handlePendingTxFn({ ...evmCtx }, tx, {
-        log: logFn,
-      }).catch(errorHandler);
+    const errLabel = `🚨 Failed to process pending tx ${path}`;
+    let data;
+    try {
+      // Extract txId from path (e.g., "published.ymax0.pendingTxs.tx1")
+      const txId = stripPrefix(`${PENDING_TX_PATH_PREFIX}.`, path);
+      log('Processing pendingTx event', path);
+
+      const streamCell = parseStreamCell(cellJson, path);
+      const value = parseStreamCellValue(streamCell, -1, path);
+      data = marshaller.fromCapData(value);
+      mustMatch(data, PublishedTxShape, `${path} index -1`);
+      const tx = { txId, ...data } as PendingTx;
+      log('New pending tx', tx);
+      // Tx resolution is non-blocking.
+      void handlePendingTxFn(tx, txPowers).catch(err => error(errLabel, err));
+    } catch (err) {
+      error(errLabel, data, err);
     }
   }
 };
@@ -477,7 +483,7 @@ export const startEngine = async (
         return BigInt((respData.TxResult as any).height);
       default: {
         console.error(
-          `Attempting to read block height from unexpected response type ${respType}`,
+          `🚨 Attempting to read block height from unexpected response type ${respType}`,
           respData,
         );
         const obj = Object.values(respData)[0];
@@ -502,63 +508,74 @@ export const startEngine = async (
   // console.log('subscribed to events', subscriptionFilters);
 
   // TODO: Verify consumption of paginated data.
+  const [pendingTxKeys, portfolioKeys] = await Promise.all(
+    [PENDING_TX_PATH_PREFIX, PORTFOLIOS_PATH_PREFIX].map(vstoragePath =>
+      query.vstorage.keys(vstoragePath),
+    ),
+  );
+
   // TODO: Retry when data is associated with a block height lower than that of
   //       the first result from `responses`.
-  const portfolioKeys = await query.vstorage.keys(PORTFOLIOS_PATH_PREFIX);
   const portfolioKeyForDepositAddr = new Map() as Map<Bech32Address, string>;
   await makeWorkPool(portfolioKeys, undefined, async portfolioKey => {
-    const status = await query.readPublished(
-      `${stripPrefix('published.', PORTFOLIOS_PATH_PREFIX)}.${portfolioKey}`,
-    );
-    mustMatch(status, PortfolioStatusShapeExt, portfolioKey);
-    const { depositAddress } = status;
-    if (!depositAddress) return;
-    portfolioKeyForDepositAddr.set(depositAddress, portfolioKey);
-    // TODO: Use the block height associated with portfolioKey.
-    // https://github.com/Agoric/agoric-sdk/pull/11630
-    deferrals.push({
-      blockHeight: 0n,
-      type: 'transfer' as const,
-      address: depositAddress,
-    });
+    const path = `${PORTFOLIOS_PATH_PREFIX}.${portfolioKey}`;
+    await null;
+    let status;
+    try {
+      status = await query.readPublished(stripPrefix('published.', path));
+      mustMatch(status, PortfolioStatusShapeExt, path);
+      const { depositAddress } = status;
+      if (!depositAddress) return;
+      portfolioKeyForDepositAddr.set(depositAddress, portfolioKey);
+      // TODO: Use the block height associated with portfolioKey.
+      // https://github.com/Agoric/agoric-sdk/pull/11630
+      deferrals.push({
+        blockHeight: 0n,
+        type: 'transfer' as const,
+        address: depositAddress,
+      });
+    } catch (err) {
+      const msg = `⚠️  Could not read ${portfolioKey} status; deferring`;
+      console.error(msg, status, err);
+      const blockHeight = 0n;
+      const event = makeVstorageEvent(
+        blockHeight,
+        PORTFOLIOS_PATH_PREFIX,
+        { addPortfolio: portfolioKey } as StatusFor['portfolios'],
+        marshaller,
+      );
+      deferrals.push({ blockHeight, type: 'kvstore', event });
+    }
   }).done;
 
-  const pendingTxKeys = await query.vstorage.keys(PENDING_TX_PATH_PREFIX);
-  console.warn(
-    `Found ${pendingTxKeys.length} existing pendingTxKeys to monitor`,
-  );
-
+  const txPowers = {
+    ...evmCtx,
+    signingSmartWalletKit,
+    fetch,
+    cosmosRest,
+    marshaller,
+    log: console.warn.bind(console),
+    error: console.error.bind(console),
+  };
+  console.warn(`Found ${pendingTxKeys.length} pending transactions`);
   await makeWorkPool(pendingTxKeys, undefined, async txId => {
-    const logIgnoredError = err => {
-      const msg = `⚠️ Failed to process existing pendingTx: ${txId}`;
-      console.error(msg, err);
-    };
+    const path = `${PENDING_TX_PATH_PREFIX}.${txId}`;
+    const errLabel = `🚨 Failed to process old pending tx ${path}`;
 
+    await null;
     let data;
     try {
-      // eslint-disable-next-line @jessie.js/safe-await-separator
-      data = await query.readPublished(
-        stripPrefix('published.', `${PENDING_TX_PATH_PREFIX}.${txId}`),
+      data = await query.readPublished(stripPrefix('published.', path));
+      mustMatch(data, PublishedTxShape, path);
+      const tx = { txId, ...data } as PendingTx;
+      console.warn('Old pending tx', tx);
+      // Tx resolution is non-blocking.
+      void handlePendingTx(tx, txPowers).catch(err =>
+        console.error(errLabel, err),
       );
     } catch (err) {
-      logIgnoredError(err);
-      return;
+      console.error(errLabel, data, err);
     }
-
-    const tx = parsePendingTx(txId as `tx${number}`, data);
-    if (!tx) return;
-
-    console.warn(`Found existing tx: ${txId}`, {
-      type: tx.type,
-      status: tx.status,
-    });
-
-    // Process existing pending transactions on startup
-    void handlePendingTx(
-      { ...evmCtx, signingSmartWalletKit, fetch, cosmosRest },
-      tx,
-      { log },
-    ).catch(logIgnoredError);
   }).done;
 
   // console.warn('consuming events');
@@ -641,11 +658,7 @@ export const startEngine = async (
       portfolioKeyForDepositAddr,
     });
 
-    await processPendingTxEvents(
-      { ...evmCtx, cosmosRest, signingSmartWalletKit, fetch },
-      pendingTxEvents,
-      marshaller,
-    );
+    await processPendingTxEvents(pendingTxEvents, handlePendingTx, txPowers);
 
     // Detect activity against portfolio deposit addresses.
     const oldAddrActivity = deferrals.splice(0).filter(deferral => {
```

### services/ymax-planner/src/pending-tx-manager.ts
```diff
@@ -199,13 +199,13 @@ type HandlePendingTxOptions = {
 };
 
 export const handlePendingTx = async (
-  ctx: EvmContext,
   tx: PendingTx,
   {
     log = () => {},
     registry = createMonitorRegistry(),
     timeoutMs = 300000, // 5 min
-  }: HandlePendingTxOptions,
+    ...evmCtx
+  }: EvmContext & HandlePendingTxOptions,
 ) => {
   await null;
   const logPrefix = `[${tx.txId}]`;
@@ -214,5 +214,5 @@ export const handlePendingTx = async (
   const monitor = registry[tx.type] as PendingTxMonitor<PendingTx, EvmContext>;
   monitor || Fail`${logPrefix} No monitor registered for tx type: ${tx.type}`;
 
-  await monitor.watch(ctx, tx, log, timeoutMs);
+  await monitor.watch(evmCtx, tx, log, timeoutMs);
 };
```

### services/ymax-planner/test/cctp-watcher.test.ts
```diff
@@ -62,7 +62,8 @@ test('handlePendingTx processes CCTP transaction successfully', async t => {
   }, 50);
 
   await t.notThrowsAsync(async () => {
-    await handlePendingTx(mockEvmCtx, cctpTx, {
+    await handlePendingTx(cctpTx, {
+      ...mockEvmCtx,
       log: logger,
       timeoutMs: 3000,
     });
@@ -124,7 +125,8 @@ test('handlePendingTx keeps tx pending on amount mismatch until timeout', async
   }, 50);
 
   await t.notThrowsAsync(async () => {
-    await handlePendingTx(mockEvmCtx, cctpTx, {
+    await handlePendingTx(cctpTx, {
+      ...mockEvmCtx,
       log: logger,
       timeoutMs: 3000,
     });
```

### services/ymax-planner/test/gmp-watcher.test.ts
```diff
@@ -46,7 +46,8 @@ test('handlePendingTx processes GMP transaction successfully', async t => {
   }, 50);
 
   await t.notThrowsAsync(async () => {
-    await handlePendingTx(mockEvmCtx, gmpTx, {
+    await handlePendingTx(gmpTx, {
+      ...mockEvmCtx,
       log: logger,
       timeoutMs: 3000,
     });
@@ -83,7 +84,8 @@ test('handlePendingTx times out GMP transaction with no matching event', async t
   // Don't emit any matching events - let it timeout
 
   await t.notThrowsAsync(async () => {
-    await handlePendingTx(mockEvmCtx, gmpTx, {
+    await handlePendingTx(gmpTx, {
+      ...mockEvmCtx,
       log: logger,
       timeoutMs: 3000,
     });
```

### services/ymax-planner/test/pending-tx.test.ts
```diff
@@ -5,7 +5,7 @@ import {
   type EvmContext,
   type PendingTx,
 } from '../src/pending-tx-manager.ts';
-import { processPendingTxEvents, parsePendingTx } from '../src/engine.ts';
+import { processPendingTxEvents } from '../src/engine.ts';
 import {
   createMockEvmContext,
   createMockPendingTxData,
@@ -16,129 +16,31 @@ import { TxType } from '@aglocal/portfolio-contract/src/resolver/constants.js';
 
 const marshaller = boardSlottingMarshaller();
 
-// --- Unit tests for parsePendingTx ---
-test('parsePendingTx creates valid PendingTx from data', t => {
-  const txId = 'tx1' as `tx${number}`;
-  const txData = createMockPendingTxData({ type: TxType.CCTP_TO_EVM });
-  const capData = marshaller.toCapData(txData);
-
-  const result = parsePendingTx(txId, marshaller.fromCapData(capData));
-
-  t.deepEqual(result, {
-    txId,
-    type: TxType.CCTP_TO_EVM,
-    status: 'pending',
-    amount: 1000_00n,
-    destinationAddress:
-      'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
-  });
-});
-
-test('parsePendingTx returns null for invalid data shape', t => {
-  const txId = 'tx3' as `tx${number}`;
-  const invalidTxData = harden({
-    someOtherField: 'value',
-  });
-
-  const result = parsePendingTx(txId, invalidTxData);
-
-  t.is(result, null);
-});
-
-test('parsePendingTx returns null when CCTP transaction is missing amount field', t => {
-  const txId = 'tx4' as `tx${number}`;
-  const cctpWithoutAmount = harden({
-    type: TxType.CCTP_TO_EVM,
-    status: 'pending',
-    destinationAddress:
-      'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
-  });
-
-  const result = parsePendingTx(txId, cctpWithoutAmount);
-
-  t.is(result, null);
-});
-
-test('parsePendingTx accepts GMP transaction without amount field', t => {
-  const txId = 'tx5' as `tx${number}`;
-  const gmpWithoutAmount = harden({
-    type: TxType.GMP,
-    status: 'pending',
-    destinationAddress:
-      'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
-  });
-
-  const result = parsePendingTx(txId, gmpWithoutAmount);
-
-  t.deepEqual(result, {
-    txId,
-    type: TxType.GMP,
-    status: 'pending',
-    destinationAddress:
-      'eip155:42161:0x742d35Cc6635C0532925a3b8D9dEB1C9e5eb2b64',
-  });
-});
-
-test('parsePendingTx validates Noble withdraw transactions require amount', t => {
-  const txId = 'tx1' as `tx${number}`;
-  const nobleWithdrawData = harden({
-    type: TxType.CCTP_TO_NOBLE,
-    status: 'pending',
-    destinationAddress: 'cosmos:noble:noble1abc123456789',
-  });
-  const capData = marshaller.toCapData(nobleWithdrawData);
-  const unmarshalledData = marshaller.fromCapData(capData);
-
-  const result = parsePendingTx(txId, unmarshalledData);
-
-  t.is(result, null);
-});
-
-test('parsePendingTx creates valid Noble withdraw PendingTx from data', t => {
-  const txId = 'tx1' as `tx${number}`;
-  const nobleWithdrawData = createMockPendingTxData({
-    type: TxType.CCTP_TO_NOBLE,
-    amount: 500_000n,
-    destinationAddress: 'cosmos:noble:noble1abc123456789',
-  });
-  const capData = marshaller.toCapData(nobleWithdrawData);
-
-  const result = parsePendingTx(txId, marshaller.fromCapData(capData));
-
-  t.deepEqual(result, {
-    txId,
-    type: TxType.CCTP_TO_NOBLE,
-    status: 'pending',
-    amount: 500_000n,
-    destinationAddress: 'cosmos:noble:noble1abc123456789',
-  });
-});
-
-// --- Unit tests for processPendingTxEvents ---
-test('processPendingTxEvents handles valid single transaction event', async t => {
-  const mockEvmCtx = createMockEvmContext();
+const makeMockHandlePendingTx = () => {
   const handledTxs: PendingTx[] = [];
-
-  // Mock handlePendingTx to track calls
   const mockHandlePendingTx = async (
-    ctx: EvmContext,
     tx: PendingTx,
-    log: any,
+    { log: any, ...evmCtx }: any,
   ) => {
     handledTxs.push(tx);
   };
+  return { mockHandlePendingTx, handledTxs };
+};
+
+// --- Unit tests for processPendingTxEvents ---
+test('processPendingTxEvents handles valid single transaction event', async t => {
+  const { mockHandlePendingTx, handledTxs } = makeMockHandlePendingTx();
+  const mockEvmCtx = createMockEvmContext();
 
   const txData = createMockPendingTxData({ type: TxType.CCTP_TO_EVM });
   const capData = marshaller.toCapData(txData);
   const streamCell = createMockStreamCell([JSON.stringify(capData)]);
   const events = [createMockPendingTxEvent('tx1', JSON.stringify(streamCell))];
 
-  await processPendingTxEvents(
-    mockEvmCtx,
-    events,
+  await processPendingTxEvents(events, mockHandlePendingTx, {
+    ...mockEvmCtx,
     marshaller,
-    mockHandlePendingTx,
-  );
+  });
 
   t.is(handledTxs.length, 1);
   t.like(handledTxs[0], {
@@ -149,16 +51,8 @@ test('processPendingTxEvents handles valid single transaction event', async t =>
 });
 
 test('processPendingTxEvents handles multiple transaction events', async t => {
+  const { mockHandlePendingTx, handledTxs } = makeMockHandlePendingTx();
   const mockEvmCtx = createMockEvmContext();
-  const handledTxs: PendingTx[] = [];
-
-  const mockHandlePendingTx = async (
-    ctx: EvmContext,
-    tx: PendingTx,
-    log: any,
-  ) => {
-    handledTxs.push(tx);
-  };
 
   const originalCctpData = createMockPendingTxData({
     type: TxType.CCTP_TO_EVM,
@@ -179,29 +73,19 @@ test('processPendingTxEvents handles multiple transaction events', async t => {
     ),
   ];
 
-  await processPendingTxEvents(
-    mockEvmCtx,
-    events,
+  await processPendingTxEvents(events, mockHandlePendingTx, {
+    ...mockEvmCtx,
     marshaller,
-    mockHandlePendingTx,
-  );
+  });
 
   t.is(handledTxs.length, 2);
   t.like(handledTxs[0], { txId: 'tx1', type: TxType.CCTP_TO_EVM });
   t.like(handledTxs[1], { txId: 'tx2', type: TxType.GMP });
 });
 
-test('processPendingTxEvents processes valid transactions before throwing on invalid stream cell', async t => {
+test('processPendingTxEvents errors do not disrupt processing valid transactions', async t => {
+  const { mockHandlePendingTx, handledTxs } = makeMockHandlePendingTx();
   const mockEvmCtx = createMockEvmContext();
-  const handledTxs: PendingTx[] = [];
-
-  const mockHandlePendingTx = async (
-    ctx: EvmContext,
-    tx: PendingTx,
-    log: any,
-  ) => {
-    handledTxs.push(tx);
-  };
 
   const validTx1 = createMockPendingTxData({ type: TxType.CCTP_TO_EVM });
   const validTx2 = createMockPendingTxData({ type: TxType.GMP });
@@ -228,37 +112,34 @@ test('processPendingTxEvents processes valid transactions before throwing on inv
       'tx3',
       JSON.stringify({ values: [JSON.stringify(validCapData2)] }),
     ),
+    createMockPendingTxEvent(
+      'tx4',
+      JSON.stringify(createMockStreamCell([JSON.stringify(validCapData2)])),
+    ),
   ];
 
-  await t.throwsAsync(
-    () =>
-      processPendingTxEvents(
-        mockEvmCtx,
-        events,
-        marshaller,
-        mockHandlePendingTx,
-      ),
-    { message: /Must have missing properties.*blockHeight/ },
+  const errorLog = [] as Array<any[]>;
+  await processPendingTxEvents(events, mockHandlePendingTx, {
+    ...mockEvmCtx,
+    marshaller,
+    error: (...args) => errorLog.push(args),
+  });
+  if (errorLog.length !== 2) {
+    t.log(errorLog);
+  }
+  t.is(errorLog.length, 2);
+  t.regex(errorLog[0].at(-1).message, /\btx2\b/);
+  t.regex(
+    errorLog[1].at(-1).message,
+    /\btx3\b.*Must have missing properties.*blockHeight/,
   );
 
-  t.is(
-    handledTxs.length,
-    1,
-    'No transactions should be handled due to invalid tx causing early return',
-  );
+  t.is(handledTxs.length, 2);
 });
 
 test('processPendingTxEvents handles only pending transactions', async t => {
+  const { mockHandlePendingTx, handledTxs } = makeMockHandlePendingTx();
   const mockEvmCtx = createMockEvmContext();
-  const handledTxs: PendingTx[] = [];
-
-  const mockHandlePendingTx = async (
-    ctx: EvmContext,
-    tx: PendingTx,
-    log: any,
-  ) => {
-    handledTxs.push(tx);
-  };
 
   const tx1 = createMockPendingTxData({ type: TxType.CCTP_TO_EVM });
   const tx2 = createMockPendingTxData({ type: TxType.GMP, status: 'success' });
@@ -277,28 +158,18 @@ test('processPendingTxEvents handles only pending transactions', async t => {
     ),
   ];
 
-  await processPendingTxEvents(
-    mockEvmCtx,
-    events,
+  await processPendingTxEvents(events, mockHandlePendingTx, {
+    ...mockEvmCtx,
     marshaller,
-    mockHandlePendingTx,
-  );
+  });
 
   t.is(handledTxs.length, 1);
   t.is(handledTxs[0].status, 'pending');
 });
 
 test('processPendingTxEvents handles Noble withdraw transactions', async t => {
+  const { mockHandlePendingTx, handledTxs } = makeMockHandlePendingTx();
   const mockEvmCtx = createMockEvmContext();
-  const handledTxs: PendingTx[] = [];
-
-  const mockHandlePendingTx = async (
-    ctx: EvmContext,
-    tx: PendingTx,
-    log: any,
-  ) => {
-    handledTxs.push(tx);
-  };
 
   const nobleWithdrawData = createMockPendingTxData({
     type: TxType.CCTP_TO_NOBLE,
@@ -310,12 +181,10 @@ test('processPendingTxEvents handles Noble withdraw transactions', async t => {
   const streamCell = createMockStreamCell([JSON.stringify(capData)]);
   const events = [createMockPendingTxEvent('tx1', JSON.stringify(streamCell))];
 
-  await processPendingTxEvents(
-    mockEvmCtx,
-    events,
+  await processPendingTxEvents(events, mockHandlePendingTx, {
+    ...mockEvmCtx,
     marshaller,
-    mockHandlePendingTx,
-  );
+  });
 
   t.is(handledTxs.length, 1);
   t.like(handledTxs[0], {
@@ -341,7 +210,7 @@ test('handlePendingTx throws error for unsupported transaction type', async t =>
   } as any;
 
   await t.throwsAsync(
-    () => handlePendingTx(mockEvmCtx, unsupportedTx, { log: mockLog }),
+    () => handlePendingTx(unsupportedTx, { ...mockEvmCtx, log: mockLog }),
     { message: /No monitor registered for tx type: "cctpV2"/ },
   );
 });
```
