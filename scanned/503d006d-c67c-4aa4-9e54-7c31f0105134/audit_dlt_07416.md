# [?] fix: race condition in fast tx collection (#21496)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-03-18
Source: https://github.com/AztecProtocol/aztec-packages/commit/4a893dcfb51204f648dde95f29750a89282f0d14
Type: security-commit

## Details
fix: race condition in fast tx collection (#21496)

Ref: A-513

- Replaces MissingTxsTracker with RequestTracker that unifies missing tx
tracking, deadline management, and cancellation signaling into a single
object
- Ensures cancellation propagates from the deepest stack level upward:
inner workers and node loops settle before collectFast returns (no
orphaned promises)
- Makes node loop inter-retry sleep interruptible by racing against
cancellationToken

## Patch
### yarn-project/p2p/src/client/test/p2p_client.integration_batch_txs.test.ts
```diff
@@ -22,7 +22,7 @@ import { BatchTxRequester } from '../../services/reqresp/batch-tx-requester/batc
 import type { BatchTxRequesterLibP2PService } from '../../services/reqresp/batch-tx-requester/interface.js';
 import type { IBatchRequestTxValidator } from '../../services/reqresp/batch-tx-requester/tx_validator.js';
 import type { ConnectionSampler } from '../../services/reqresp/connection-sampler/connection_sampler.js';
-import { MissingTxsTracker } from '../../services/tx_collection/missing_txs_tracker.js';
+import { RequestTracker } from '../../services/tx_collection/request_tracker.js';
 import { generatePeerIdPrivateKeys } from '../../test-helpers/generate-peer-id-private-keys.js';
 import { getPorts } from '../../test-helpers/get-ports.js';
 import { makeEnrs } from '../../test-helpers/make-enrs.js';
@@ -231,10 +231,9 @@ describe('p2p client integration batch txs', () => {
     mockP2PService.reqResp = (client0 as any).p2pService.reqresp;
 
     const requester = new BatchTxRequester(
-      MissingTxsTracker.fromArray(missingTxHashes),
+      RequestTracker.create(missingTxHashes, new Date(Date.now() + 5_000)),
       blockProposal,
       undefined, // no pinned peer
-      5_000,
       mockP2PService,
       logger,
       undefined,
```

### yarn-project/p2p/src/client/test/tx_proposal_collector/proposal_tx_collector_worker.ts
```diff
@@ -19,7 +19,7 @@ import type { P2PConfig } from '../../../config.js';
 import { BatchTxRequesterCollector, SendBatchRequestCollector } from '../../../services/index.js';
 import type { IBatchRequestTxValidator } from '../../../services/reqresp/batch-tx-requester/tx_validator.js';
 import { RateLimitStatus } from '../../../services/reqresp/rate-limiter/rate_limiter.js';
-import { MissingTxsTracker } from '../../../services/tx_collection/missing_txs_tracker.js';
+import { RequestTracker } from '../../../services/tx_collection/request_tracker.js';
 import {
   AlwaysTrueCircuitVerifier,
   BENCHMARK_CONSTANTS,
@@ -213,10 +213,9 @@ async function runCollector(cmd: Extract<WorkerCommand, { type: 'RUN_COLLECTOR'
       const fetched = await executeTimeout(
         (_signal: AbortSignal) =>
           collector.collectTxs(
-            MissingTxsTracker.fromArray(parsedTxHashes),
+            RequestTracker.create(parsedTxHashes, new Date(Date.now() + internalTimeoutMs)),
             parsedProposal,
             pinnedPeer,
-            internalTimeoutMs,
           ),
         timeoutMs,
         () => new Error(`Collector timed out after ${timeoutMs}ms`),
@@ -231,10 +230,9 @@ async function runCollector(cmd: Extract<WorkerCommand, { type: 'RUN_COLLECTOR'
       const fetched = await executeTimeout(
         (_signal: AbortSignal) =>
           collector.collectTxs(
-            MissingTxsTracker.fromArray(parsedTxHashes),
+            RequestTracker.create(parsedTxHashes, new Date(Date.now() + internalTimeoutMs)),
             parsedProposal,
             pinnedPeer,
-            internalTimeoutMs,
           ),
         timeoutMs,
         () => new Error(`Collector timed out after ${timeoutMs}ms`),
```

### yarn-project/p2p/src/services/reqresp/batch-tx-requester/README.md
```diff
@@ -170,6 +170,37 @@ class BlockTxsResponse {
 
 The `BitVector` is a compact representation where each bit corresponds to a transaction index in the block proposal. This allows efficient capability advertisement without repeating full hashes.
 
+## Cancellation
+
+All cancellation is managed by a single `RequestTracker` instance, shared across the entire collection
+flow. The `RequestTracker` owns the deadline, tracks which txs are still missing, and exposes a
+`cancellationToken` promise that resolves when the request should stop (deadline hit, all txs fetched,
+or external `cancel()` call).
+
+Cancellation propagates from the deepest stack level upward:
+
+```
+RequestTracker.finish()
+  ├── resolves cancellationToken promise
+  │
+  ├── BatchTxRequester workers (deepest)
+  │     ├── shouldStop() checks requestTracker.cancelled → exit loop
+  │     ├── sleepClampedToDeadline races sleep vs cancellationToken → wakes
+  │     └── semaphore.acquire races vs cancellationToken → wakes
+  │           │
+  │           ▼ workers settle → txQueue.end() → generator returns
+  │
+  ├── Node collection loops
+  │     ├── notFinished() checks requestTracker.cancelled → exit loop
+  │     └── inter-retry sleep races vs cancellationToken → wakes
+  │           │
+  │           ▼ all node loops settle
+  │
+  └── collectFast (outermost)
+        awaits Promise.allSettled([reqresp, nodes]) → settles after inner tasks
+        finally: requestTracker.cancel() (idempotent), cleanup
+```
+
 ## Key Files
 
 | File | Description |
@@ -179,15 +210,16 @@ The `BitVector` is a compact representation where each bit corresponds to a tran
 | `peer_collection.ts` | Manages peer classification (dumb/smart/bad) and rate limiting |
 | `interface.ts` | Type definitions for dependencies |
 | `../protocols/block_txs/` | Wire protocol definitions (`BlockTxsRequest`, `BlockTxsResponse`, `BitVector`) |
+| `../../tx_collection/request_tracker.ts` | Centralized deadline, missing tx tracking, and cancellation signal |
 
 ## Stopping Conditions
 
-The `BatchTxRequester` stops when any of these conditions are met:
+The `BatchTxRequester` stops when any of these conditions are met, all managed by the `RequestTracker`:
 
-1. **All transactions fetched** - Success!
-2. **Deadline exceeded** - Timeout configured by caller
-3. **Abort signal** - External cancellation
-4. **No transactions to fetch** - Nothing was missing
+1. **All transactions fetched** - `markFetched()` removes the last missing tx, triggering `finish()`
+2. **Deadline exceeded** - `setTimeout` in `RequestTracker` fires, triggering `finish()`
+3. **External cancellation** - `RequestTracker.cancel()` called (e.g., from `stop()`, `stopCollectingForBlocksUpTo`)
+4. **No transactions to fetch** - Empty hash set at construction, `RequestTracker` finishes immediately
 
 ## Configuration
 
@@ -228,11 +260,15 @@ Request to peer fails
 ## Usage Example
 
 ```typescript
+const requestTracker = RequestTracker.create(
+  missingTxHashes,                          // TxHash[] - what we need
+  new Date(Date.now() + 5_000),             // deadline
+);
+
 const requester = new BatchTxRequester(
-  missingTxHashes,      // TxHash[] - what we need
+  requestTracker,       // IRequestTracker - tracks missing txs, deadline, and cancellation
   blockTxsSource,       // BlockTxsSource - the proposal or block we need txs for
   pinnedPeer,           // PeerId | undefined - peer expected to have the txs
-  timeoutMs,            // number - how long to try
   p2pService,           // BatchTxRequesterLibP2PService
 );
 
@@ -273,6 +309,8 @@ const txs = await BatchTxRequester.collectAllTxs(requester.run());
 │  1. Try RPC nodes first (fast)    │   │  Periodic polling of RPC nodes      │
 │  2. Fall back to BatchTxRequester │   │  and peers for missing txs          │
 │                                   │   │                                     │
+│  Creates RequestTracker per       │   │                                     │
+│  request with deadline            │   │                                     │
 └───────────────────┬───────────────┘   └─────────────────────────────────────┘
                     │
                     │ For 'proposal' and 'block' requests
@@ -281,6 +319,7 @@ const txs = await BatchTxRequester.collectAllTxs(requester.run());
 │                           BatchTxRequester                                  │
 │                                                                             │
 │  Aggressive parallel fetching from multiple peers                           │
+│  Shares RequestTracker with FastTxCollection for unified cancellation       │
 │  Uses BLOCK_TXS sub-protocol for efficient batching                         │
 └───────────────────┬─────────────────────────────────────────────────────────┘
                     │
```

### yarn-project/p2p/src/services/reqresp/batch-tx-requester/batch_tx_requester.test.ts
```diff
@@ -17,7 +17,7 @@ import type { PeerId } from '@libp2p/interface';
 import { type MockProxy, mock } from 'jest-mock-extended';
 
 import { createSecp256k1PeerId } from '../../../index.js';
-import { MissingTxsTracker } from '../../tx_collection/missing_txs_tracker.js';
+import { RequestTracker } from '../../tx_collection/request_tracker.js';
 import type { ConnectionSampler } from '../connection-sampler/connection_sampler.js';
 import type { ReqRespInterface } from '../interface.js';
 import { BitVector, BlockTxsRequest, BlockTxsResponse } from '../protocols/index.js';
@@ -110,25 +110,17 @@ describe('BatchTxRequester', () => {
 
       const clock = new TestClock();
 
-      const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
-        blockProposal,
-        undefined,
-        deadline,
-        mockP2PService,
-        logger,
-        clock,
-        {
-          smartParallelWorkerCount: 0,
-          dumbParallelWorkerCount: 1,
-          txValidator,
-        },
-      );
+      const tracker = RequestTracker.create(missing, new Date(Date.now() + deadline));
+      const requester = new BatchTxRequester(tracker, blockProposal, undefined, mockP2PService, logger, clock, {
+        smartParallelWorkerCount: 0,
+        dumbParallelWorkerCount: 1,
+        txValidator,
+      });
 
       const runPromise = BatchTxRequester.collectAllTxs(requester.run());
 
       await retryUntil(() => (requestCount() === rounds ? true : undefined), 'waitFor', 10, 0.01);
-      clock.advanceTo(deadline + 1);
+      tracker.cancel();
 
       await runPromise;
 
@@ -165,25 +157,17 @@ describe('BatchTxRequester', () => {
 
       const clock = new TestClock();
 
-      const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
-        blockProposal,
-        undefined,
-        deadline,
-        mockP2PService,
-        logger,
-        clock,
-        {
-          smartParallelWorkerCount: 0,
-          dumbParallelWorkerCount: 3,
-          txValidator,
-        },
-      );
+      const tracker = RequestTracker.create(missing, new Date(Date.now() + deadline));
+      const requester = new BatchTxRequester(tracker, blockProposal, undefined, mockP2PService, logger, clock, {
+        smartParallelWorkerCount: 0,
+        dumbParallelWorkerCount: 3,
+        txValidator,
+      });
 
       const runPromise = BatchTxRequester.collectAllTxs(requester.run());
 
       await retryUntil(() => (requestCount() == numberOfRounds * peers.length ? true : undefined), 'waitFor', 10, 0.01);
-      clock.advanceTo(deadline + 1);
+      tracker.cancel();
 
       await runPromise;
 
@@ -294,10 +278,9 @@ describe('BatchTxRequester', () => {
       });
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         undefined,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -348,10 +331,9 @@ describe('BatchTxRequester', () => {
       const semaphore = new TestSemaphore(new Semaphore(0));
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         undefined,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -400,10 +382,9 @@ describe('BatchTxRequester', () => {
 
       const semaphore = new TestSemaphore(new Semaphore(0));
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         dateProvider,
@@ -473,10 +454,9 @@ describe('BatchTxRequester', () => {
 
       const semaphore = new TestSemaphore(new Semaphore(0));
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         dateProvider,
@@ -529,10 +509,9 @@ describe('BatchTxRequester', () => {
 
       const semaphore = new TestSemaphore(new Semaphore(0));
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         dateProvider,
@@ -585,10 +564,9 @@ describe('BatchTxRequester', () => {
       );
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         dateProvider,
@@ -662,10 +640,9 @@ describe('BatchTxRequester', () => {
       });
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         dateProvider,
@@ -776,10 +753,9 @@ describe('BatchTxRequester', () => {
       });
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         dateProvider,
@@ -916,10 +892,9 @@ describe('BatchTxRequester', () => {
       });
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         clock,
@@ -990,26 +965,18 @@ describe('BatchTxRequester', () => {
 
       const clock = new TestClock();
 
-      const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
-        blockProposal,
-        undefined,
-        shortDeadline,
-        mockP2PService,
-        logger,
-        clock,
-        {
-          smartParallelWorkerCount: 1,
-          dumbParallelWorkerCount: 1,
-          txValidator,
-        },
-      );
+      const tracker = RequestTracker.create(missing, new Date(Date.now() + shortDeadline));
+      const requester = new BatchTxRequester(tracker, blockProposal, undefined, mockP2PService, logger, clock, {
+        smartParallelWorkerCount: 1,
+        dumbParallelWorkerCount: 1,
+        txValidator,
+      });
 
       const runPromise = BatchTxRequester.collectAllTxs(requester.run());
 
-      // Wait for first request, then advance clock past deadline
+      // Wait for first request, then cancel the tracker
       await onFirstRequest;
-      clock.advanceTo(shortDeadline + 1);
+      tracker.cancel();
 
       await runPromise;
 
@@ -1033,33 +1000,31 @@ describe('BatchTxRequester', () => {
       const peers = await Promise.all([createSecp256k1PeerId(), createSecp256k1PeerId()]);
       connectionSampler.getPeerListSortedByConnectionCountAsc.mockReturnValue(peers);
 
-      // Create abort controller and immediately abort
-      const abortController = new AbortController();
-      abortController.abort();
+      // Create tracker and immediately cancel
+      const tracker = RequestTracker.create(missing, new Date(Date.now() + deadline));
+      tracker.cancel();
 
       let requestsMade = 0;
       // eslint-disable-next-line require-await
       reqResp.sendRequestToPeer.mockImplementation(async () => {
         requestsMade++;
-        // This should never be called since we abort immediately
+        // This should never be called since we cancel immediately
         return {
           status: ReqRespStatus.SUCCESS,
           data: Buffer.alloc(0),
         };
       });
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        tracker,
         blockProposal,
         undefined,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
         {
           smartParallelWorkerCount: 2,
           dumbParallelWorkerCount: 2,
-          abortSignal: abortController.signal,
           txValidator,
         },
       );
@@ -1090,12 +1055,12 @@ describe('BatchTxRequester', () => {
         [peers[2].toString(), Array.from({ length: 10 }, (_, i) => i + 20)],
       ]);
 
-      const abortController = new AbortController();
+      const tracker = RequestTracker.create(missing, new Date(Date.now() + deadline));
       let requestCount = 0;
 
       reqResp.sendRequestToPeer.mockImplementation(async (peerId: any) => {
         if (requestCount === 1) {
-          abortController.abort();
+          tracker.cancel();
         }
 
         // Return successful response with transactions
@@ -1112,7 +1077,7 @@ describe('BatchTxRequester', () => {
 
         requestCount++;
 
-        // Allow event loop to process abort signal
+        // Allow event loop to process cancellation
         await sleep(50);
         return {
           status: ReqRespStatus.SUCCESS,
@@ -1121,25 +1086,23 @@ describe('BatchTxRequester', () => {
       });
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        tracker,
         blockProposal,
         undefined,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
         {
           smartParallelWorkerCount: 0,
           dumbParallelWorkerCount: 2,
-          abortSignal: abortController.signal,
           txValidator,
         },
       );
 
       const result = await BatchTxRequester.collectAllTxs(requester.run());
 
-      // Verify abort was actually triggered
-      expect(abortController.signal.aborted).toBe(true);
+      // Verify cancellation was actually triggered
+      expect(tracker.checkCancelled()).toBe(true);
 
       expect(result).toBeDefined();
       expect(result!.length).toBeGreaterThan(0);
@@ -1169,36 +1132,26 @@ describe('BatchTxRequester', () => {
       const { mockImplementation } = createRequestLogger(blockProposal, new Set(), peerTransactions, 100);
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
 
-      const abortController = new AbortController();
+      const tracker = RequestTracker.create(missing, new Date(Date.now() + deadline));
 
       // Create semaphore that starts with 0 permits to block smart workers
       const semaphore = new TestSemaphore(new Semaphore(0));
-      const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
-        blockProposal,
-        undefined,
-        deadline,
-        mockP2PService,
-        logger,
-        clock,
-        {
-          semaphore,
-          smartParallelWorkerCount: 2,
-          dumbParallelWorkerCount: 2,
-          peerCollection,
-          abortSignal: abortController.signal,
-          txValidator,
-        },
-      );
+      const requester = new BatchTxRequester(tracker, blockProposal, undefined, mockP2PService, logger, clock, {
+        semaphore,
+        smartParallelWorkerCount: 2,
+        dumbParallelWorkerCount: 2,
+        peerCollection,
+        txValidator,
+      });
 
       const runPromise = BatchTxRequester.collectAllTxs(requester.run());
 
       await sleep(1000); // Allow some time for smart workers to start and block on semaphore
-      abortController.abort(); // Trigger abort while smart workers are blocked
+      tracker.cancel(); // Trigger cancellation while smart workers are blocked
       const result = await runPromise;
 
-      // Verify abort was triggered
-      expect(abortController.signal.aborted).toBe(true);
+      // Verify cancellation was triggered
+      expect(tracker.checkCancelled()).toBe(true);
 
       // Verify peer was promoted to smart
       expect(peerCollection.smartPeersMarked).toContain(peers[0].toString());
@@ -1250,10 +1203,9 @@ describe('BatchTxRequester', () => {
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         undefined,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -1331,10 +1283,9 @@ describe('BatchTxRequester', () => {
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         undefined,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -1402,10 +1353,9 @@ describe('BatchTxRequester', () => {
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         undefined,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -1450,7 +1400,7 @@ describe('BatchTxRequester', () => {
       const peer = await createSecp256k1PeerId();
       connectionSampler.getPeerListSortedByConnectionCountAsc.mockReturnValue([peer]);
 
-      const tracker = MissingTxsTracker.fromArray(missing);
+      const tracker = RequestTracker.create(missing, new Date(Date.now() + deadline));
 
       // Peer has only first half of transactions
       const peerTransactions = new Map([[peer.toString(), Array.from({ length: TX_BATCH_SIZE }, (_, i) => i)]]);
@@ -1462,7 +1412,6 @@ describe('BatchTxRequester', () => {
         tracker,
         blockProposal,
         undefined,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -1519,10 +1468,9 @@ describe('BatchTxRequester', () => {
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -1571,10 +1519,9 @@ describe('BatchTxRequester', () => {
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -1653,10 +1600,9 @@ describe('BatchTxRequester', () => {
       });
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         clock,
@@ -1709,10 +1655,9 @@ describe('BatchTxRequester', () => {
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
@@ -1765,10 +1710,9 @@ describe('BatchTxRequester', () => {
       reqResp.sendRequestToPeer.mockImplementation(mockImplementation);
 
       const requester = new BatchTxRequester(
-        MissingTxsTracker.fromArray(missing),
+        RequestTracker.create(missing, new Date(Date.now() + deadline)),
         blockProposal,
         pinnedPeer,
-        deadline,
         mockP2PService,
         logger,
         new DateProvider(),
```

### yarn-project/p2p/src/services/reqresp/batch-tx-requester/batch_tx_requester.ts
```diff
@@ -1,15 +1,14 @@
 import { chunkWrapAround } from '@aztec/foundation/collection';
-import { TimeoutError } from '@aztec/foundation/error';
 import { type Logger, createLogger } from '@aztec/foundation/log';
 import { FifoMemoryQueue, type ISemaphore, Semaphore } from '@aztec/foundation/queue';
 import { sleep } from '@aztec/foundation/sleep';
-import { DateProvider, executeTimeout } from '@aztec/foundation/timer';
+import { DateProvider } from '@aztec/foundation/timer';
 import { PeerErrorSeverity } from '@aztec/stdlib/p2p';
 import { Tx, TxArray, TxHash } from '@aztec/stdlib/tx';
 
 import type { PeerId } from '@libp2p/interface';
 
-import type { IMissingTxsTracker } from '../../tx_collection/missing_txs_tracker.js';
+import type { IRequestTracker } from '../../tx_collection/request_tracker.js';
 import { ReqRespSubProtocol } from '.././interface.js';
 import { BlockTxsRequest, BlockTxsResponse, type BlockTxsSource } from '.././protocols/index.js';
 import { ReqRespStatus } from '.././status.js';
@@ -42,16 +41,14 @@ import { BatchRequestTxValidator, type IBatchRequestTxValidator } from './tx_val
  *    - Is the peer which was unable to send us successful response N times in a row
  * */
 export class BatchTxRequester {
+  private readonly requestTracker: IRequestTracker;
   private readonly blockTxsSource: BlockTxsSource;
   private readonly pinnedPeer: PeerId | undefined;
-  private readonly timeoutMs: number;
   private readonly p2pService: BatchTxRequesterLibP2PService;
   private readonly logger: Logger;
-  private readonly dateProvider: DateProvider;
   private readonly opts: BatchTxRequesterOptions;
   private readonly peers: IPeerCollection;
   private readonly txsMetadata: ITxMetadataCollection;
-  private readonly deadline: number;
   private readonly smartRequesterSemaphore: ISemaphore;
   private readonly txQueue: FifoMemoryQueue<Tx>;
   private readonly txValidator: IBatchRequestTxValidator;
@@ -60,29 +57,26 @@ export class BatchTxRequester {
   private readonly txBatchSize: number;
 
   constructor(
-    missingTxsTracker: IMissingTxsTracker,
+    requestTracker: IRequestTracker,
     blockTxsSource: BlockTxsSource,
     pinnedPeer: PeerId | undefined,
-    timeoutMs: number,
     p2pService: BatchTxRequesterLibP2PService,
     logger?: Logger,
     dateProvider?: DateProvider,
     opts?: BatchTxRequesterOptions,
   ) {
+    this.requestTracker = requestTracker;
     this.blockTxsSource = blockTxsSource;
     this.pinnedPeer = pinnedPeer;
-    this.timeoutMs = timeoutMs;
     this.p2pService = p2pService;
     this.logger = logger ?? createLogger('p2p:reqresp_batch');
-    this.dateProvider = dateProvider ?? new DateProvider();
     this.opts = opts ?? {};
 
     this.smartParallelWorkerCount =
       this.opts.smartParallelWorkerCount ?? DEFAULT_BATCH_TX_REQUESTER_SMART_PARALLEL_WORKER_COUNT;
     this.dumbParallelWorkerCount =
       this.opts.dumbParallelWorkerCount ?? DEFAULT_BATCH_TX_REQUESTER_DUMB_PARALLEL_WORKER_COUNT;
     this.txBatchSize = this.opts.txBatchSize ?? DEFAULT_BATCH_TX_REQUESTER_TX_BATCH_SIZE;
-    this.deadline = this.dateProvider.now() + this.timeoutMs;
     this.txQueue = new FifoMemoryQueue(this.logger);
     this.txValidator = this.opts.txValidator ?? new BatchRequestTxValidator(this.p2pService.txValidatorConfig);
 
@@ -93,53 +87,43 @@ export class BatchTxRequester {
       this.peers = new PeerCollection(
         this.p2pService.connectionSampler,
         this.pinnedPeer,
-        this.dateProvider,
+        dateProvider ?? new DateProvider(),
         badPeerThreshold,
         this.p2pService.peerScoring,
       );
     }
-    this.txsMetadata = new MissingTxMetadataCollection(missingTxsTracker, this.txBatchSize);
+    this.txsMetadata = new MissingTxMetadataCollection(requestTracker, this.txBatchSize);
     this.smartRequesterSemaphore = this.opts.semaphore ?? new Semaphore(0);
   }
 
   /*
    * Fetches all missing transactions and yields them  one by one
    * */
   public async *run(): AsyncGenerator<Tx, Tx | undefined, unknown> {
-    // Our timeout is represented in milliseconds but queue expects seconds
-    // We also want to make sure we wait at least 1 second in case of very low timeouts
-    const timeoutQueueAfter = Math.max(Math.ceil(this.timeoutMs / 1_000), 1);
     try {
       if (this.txsMetadata.getMissingTxHashes().size === 0) {
         return undefined;
       }
 
-      // Start workers in background
-      const workersPromise = executeTimeout(
-        () => Promise.allSettled([this.smartRequester(), this.dumbRequester(), this.pinnedPeerRequester()]),
-        this.timeoutMs,
-      ).finally(() => {
+      // Start workers in background. Workers stop themselves via requestTracker.checkCancelled().
+      const workersPromise = Promise.allSettled([
+        this.smartRequester(),
+        this.dumbRequester(),
+        this.pinnedPeerRequester(),
+      ]).finally(() => {
         this.txQueue.end();
       });
 
+      // Yield txs as workers put them on the queue. The queue's end() drains remaining items
+      // before returning null, so we don't lose any txs.
       while (true) {
-        const tx = await this.txQueue.get(timeoutQueueAfter);
+        const tx = await this.txQueue.get();
 
-        // null indicates that the queue has ended
         if (tx === null) {
           break;
         }
 
         yield tx;
-
-        if (this.shouldStop()) {
-          // Drain queue before ending
-          let remaining;
-          while ((remaining = this.txQueue.getImmediate()) !== undefined) {
-            yield remaining;
-          }
-          break;
-        }
       }
 
       this.unlockSmartRequesterSemaphores();
@@ -360,7 +344,10 @@ export class BatchTxRequester {
   ) {
     try {
       this.logger.trace(`Smart worker ${workerIndex} started`);
-      await executeTimeout((_: AbortSignal) => this.smartRequesterSemaphore.acquire(), this.timeoutMs);
+      await Promise.race([this.smartRequesterSemaphore.acquire(), this.requestTracker.cancellationToken]);
+      if (this.requestTracker.checkCancelled()) {
+        return;
+      }
       this.logger.trace(`Smart worker ${workerIndex} acquired semaphore`);
 
       while (!this.shouldStop()) {
@@ -384,7 +371,10 @@ export class BatchTxRequester {
           //
           // When a dumb peer responds with valid txIndices, it gets
           // promoted to smart and releases the semaphore, waking this worker.
-          await executeTimeout((_: AbortSignal) => this.smartRequesterSemaphore.acquire(), this.timeoutMs);
+          await Promise.race([this.smartRequesterSemaphore.acquire(), this.requestTracker.cancellationToken]);
+          if (this.requestTracker.checkCancelled()) {
+            break;
+          }
           this.logger.debug(`Worker loop smart: acquired next smart peer`);
           continue;
         }
@@ -411,11 +401,7 @@ export class BatchTxRequester {
         });
       }
     } catch (err: any) {
-      if (err instanceof TimeoutError) {
-        this.logger.debug(`Smart worker ${workerIndex} timed out waiting for semaphore`);
-      } else {
-        this.logger.error(`Smart worker ${workerIndex} encountered an error: ${err}`);
-      }
+      this.logger.error(`Smart worker ${workerIndex} encountered an error: ${err}`);
     } finally {
       this.logger.debug(`Smart worker ${workerIndex} finished`);
     }
@@ -651,27 +637,14 @@ export class BatchTxRequester {
   }
 
   /*
-   * @returns true if all missing txs have been fetched */
-  private fetchedAllTxs() {
-    return this.txsMetadata.getMissingTxHashes().size == 0;
-  }
-
-  /*
-   * Checks if the BatchTxRequester should stop fetching missing txs
-   * Conditions for stopping are:
-   * - There have been no missing transactions to start with
-   * - All transactions have been fetched
-   * - The deadline has been hit (no more time to fetch)
-   * - This process has been cancelled via abortSignal
-   *
-   * @returns true if BatchTxRequester should stop, otherwise false*/
+   * Checks if the BatchTxRequester should stop fetching missing txs.
+   * Delegates to requestTracker which covers: deadline hit, all txs fetched, or external cancellation. */
   private shouldStop() {
-    const aborted = this.opts.abortSignal?.aborted ?? false;
-    if (aborted) {
+    if (this.requestTracker.checkCancelled()) {
       this.unlockSmartRequesterSemaphores();
     }
 
-    return aborted || this.fetchedAllTxs() || this.dateProvider.now() > this.deadline;
+    return this.requestTracker.checkCancelled();
   }
 
   /*
@@ -689,10 +662,9 @@ export class BatchTxRequester {
    * This ensures we don't sleep past the deadline.
    * */
   private async sleepClampedToDeadline(durationMs: number) {
-    const remaining = this.deadline - this.dateProvider.now();
-    const thereIsTimeRemaining = remaining > 0;
-    if (thereIsTimeRemaining) {
-      await sleep(Math.min(durationMs, remaining));
+    if (this.requestTracker.checkCancelled()) {
+      return;
     }
+    await Promise.race([sleep(durationMs), this.requestTracker.cancellationToken]);
   }
 }
```

### yarn-project/p2p/src/services/reqresp/batch-tx-requester/interface.ts
```diff
@@ -49,7 +49,6 @@ export interface BatchTxRequesterOptions {
   //Injectable for testing purposes
   semaphore?: ISemaphore;
   peerCollection?: IPeerCollection;
-  abortSignal?: AbortSignal;
   /** Optional tx validator for testing - if not provided, one is created from p2pService.txValidatorConfig */
   txValidator?: IBatchRequestTxValidator;
 }
```

### yarn-project/p2p/src/services/reqresp/batch-tx-requester/missing_txs.ts
```diff
@@ -2,7 +2,7 @@ import { type Tx, TxHash } from '@aztec/stdlib/tx';
 
 import type { PeerId } from '@libp2p/interface';
 
-import type { IMissingTxsTracker } from '../../tx_collection/missing_txs_tracker.js';
+import type { IRequestTracker } from '../../tx_collection/request_tracker.js';
 import { DEFAULT_BATCH_TX_REQUESTER_TX_BATCH_SIZE } from './config.js';
 import type { ITxMetadataCollection } from './interface.js';
 
@@ -41,10 +41,10 @@ export class MissingTxMetadataCollection implements ITxMetadataCollection {
   private txMetadata = new Map<string, MissingTxMetadata>();
 
   constructor(
-    private missingTxsTracker: IMissingTxsTracker,
+    private requestTracker: IRequestTracker,
     private readonly txBatchSize: number = DEFAULT_BATCH_TX_REQUESTER_TX_BATCH_SIZE,
   ) {
-    missingTxsTracker.missingTxHashes.forEach(hash => this.txMetadata.set(hash, new MissingTxMetadata(hash)));
+    requestTracker.missingTxHashes.forEach(hash => this.txMetadata.set(hash, new MissingTxMetadata(hash)));
   }
 
   public getPrioritizingNotInFlightAndLowerRequestCount(txs: string[]): MissingTxMetadata[] {
@@ -65,7 +65,7 @@ export class MissingTxMetadataCollection implements ITxMetadataCollection {
   }
 
   public getMissingTxHashes(): Set<string> {
-    return this.missingTxsTracker.missingTxHashes;
+    return this.requestTracker.missingTxHashes;
   }
 
   public getTxsPeerHas(peer: PeerId): Set<string> {
@@ -128,7 +128,7 @@ export class MissingTxMetadataCollection implements ITxMetadataCollection {
   }
 
   public alreadyFetched(txHash: TxHash): boolean {
-    return !this.missingTxsTracker.isMissing(txHash.toString());
+    return !this.requestTracker.isMissing(txHash.toString());
   }
 
   public markFetched(peerId: PeerId, tx: Tx): boolean {
@@ -144,7 +144,7 @@ export class MissingTxMetadataCollection implements ITxMetadataCollection {
     }
 
     txMeta.peers.add(peerId.toString());
-    return this.missingTxsTracker.markFetched(tx);
+    return this.requestTracker.markFetched(tx);
   }
 
   public markPeerHas(peerId: PeerId, txHash: TxHash[]) {
```

### yarn-project/p2p/src/services/tx_collection/fast_tx_collection.ts
```diff
@@ -1,25 +1,22 @@
 import { BlockNumber } from '@aztec/foundation/branded-types';
 import { times } from '@aztec/foundation/collection';
-import { AbortError, TimeoutError } from '@aztec/foundation/error';
 import { type Logger, createLogger } from '@aztec/foundation/log';
-import { promiseWithResolvers } from '@aztec/foundation/promise';
 import { sleep } from '@aztec/foundation/sleep';
 import { DateProvider, elapsed } from '@aztec/foundation/timer';
 import type { L2BlockInfo } from '@aztec/stdlib/block';
-import type { BlockProposal } from '@aztec/stdlib/p2p';
 import { type Tx, TxHash } from '@aztec/stdlib/tx';
 
 import type { PeerId } from '@libp2p/interface';
 
 import type { BatchTxRequesterConfig } from '../reqresp/batch-tx-requester/config.js';
 import type { BatchTxRequesterLibP2PService } from '../reqresp/batch-tx-requester/interface.js';
 import type { TxCollectionConfig } from './config.js';
-import { MissingTxsTracker } from './missing_txs_tracker.js';
 import {
   BatchTxRequesterCollector,
   type MissingTxsCollector,
   SendBatchRequestCollector,
 } from './proposal_tx_collector.js';
+import { RequestTracker } from './request_tracker.js';
 import type { FastCollectionRequest, FastCollectionRequestInput } from './tx_collection.js';
 import type { TxAddContext, TxCollectionSink } from './tx_collection_sink.js';
 import type { TxSource } from './tx_source.js';
@@ -48,7 +45,9 @@ export class FastTxCollection {
   }
 
   public async stop() {
-    this.requests.forEach(request => request.promise.reject(new AbortError(`Stopped collection service`)));
+    this.requests.forEach(request => {
+      request.requestTracker.cancel();
+    });
     await Promise.resolve();
   }
 
@@ -75,81 +74,65 @@ export class FastTxCollection {
         ? { ...input.blockProposal.toBlockInfo(), blockNumber: input.blockNumber }
         : { ...input.block.toBlockInfo() };
 
-    // This promise is used to await for the collection to finish during the main collectFast method.
-    // It gets resolved in `foundTxs` when all txs have been collected, or rejected if the request is aborted or hits the deadline.
-    const promise = promiseWithResolvers<void>();
-    const timeoutTimer = setTimeout(() => promise.reject(new TimeoutError(`Timed out while collecting txs`)), timeout);
-
     const request: FastCollectionRequest = {
       ...input,
       blockInfo,
-      promise,
-      missingTxTracker: MissingTxsTracker.fromArray(txHashes),
-      deadline: opts.deadline,
+      requestTracker: RequestTracker.create(txHashes, opts.deadline, this.dateProvider),
     };
 
     const [duration] = await elapsed(() => this.collectFast(request, { ...opts }));
-    clearTimeout(timeoutTimer);
 
     this.log.verbose(
-      `Collected ${request.missingTxTracker.collectedTxs.length} txs out of ${txHashes.length} for ${input.type} at slot ${blockInfo.slotNumber}`,
+      `Collected ${request.requestTracker.collectedTxs.length} txs out of ${txHashes.length} for ${input.type} at slot ${blockInfo.slotNumber}`,
       {
         ...blockInfo,
         duration,
         requestType: input.type,
-        missingTxs: [...request.missingTxTracker.missingTxHashes],
+        missingTxs: [...request.requestTracker.missingTxHashes],
       },
     );
-    return request.missingTxTracker.collectedTxs;
+    return request.requestTracker.collectedTxs;
   }
 
-  protected async collectFast(
-    request: FastCollectionRequest,
-    opts: { proposal?: BlockProposal; deadline: Date; pinnedPeer?: PeerId },
-  ) {
+  protected async collectFast(request: FastCollectionRequest, opts: { pinnedPeer?: PeerId }) {
     this.requests.add(request);
     const { blockInfo } = request;
 
     this.log.debug(
-      `Starting fast collection of ${request.missingTxTracker.numberOfMissingTxs} txs for ${request.type} at slot ${blockInfo.slotNumber}`,
-      { ...blockInfo, requestType: request.type, deadline: opts.deadline },
+      `Starting fast collection of ${request.requestTracker.numberOfMissingTxs} txs for ${request.type} at slot ${blockInfo.slotNumber}`,
+      { ...blockInfo, requestType: request.type, deadline: request.requestTracker.deadline },
     );
 
     try {
       // Start blasting all nodes for the txs. We give them a little time to respond before we start reqresp.
-      // And keep an eye on the request promise to ensure we don't wait longer than the deadline or return as soon
-      // as we have collected all txs, whatever the source.
-      const nodeCollectionPromise = this.collectFastFromNodes(request, opts);
+      // We race against the cancellation token to exit as soon as all txs are collected, the deadline expires,
+      // or the request is externally cancelled.
+      const nodeCollectionPromise = this.collectFastFromNodes(request);
       const waitBeforeReqResp = sleep(this.config.txCollectionFastNodesTimeoutBeforeReqRespMs);
-      await Promise.race([request.promise.promise, waitBeforeReqResp]);
+      await Promise.race([request.requestTracker.cancellationToken, waitBeforeReqResp]);
 
-      // If we have collected all txs, we can stop here
-      if (request.missingTxTracker.allFetched()) {
-        this.log.debug(`All txs collected for slot ${blockInfo.slotNumber} without reqresp`, blockInfo);
+      // If we have collected all txs or the request was cancelled, we can stop here.
+      // Wait for node collection to settle so inner tasks finish before we return.
+      if (request.requestTracker.checkCancelled()) {
+        if (request.requestTracker.allFetched()) {
+          this.log.debug(`All txs collected for slot ${blockInfo.slotNumber} without reqresp`, blockInfo);
+        }
+        await nodeCollectionPromise;
         return;
       }
 
       // Start blasting reqresp for the remaining txs. Note that node collection keeps running in parallel.
       // We stop when we have collected all txs, timed out, or both node collection and reqresp have given up.
-      const collectionPromise = Promise.allSettled([this.collectFastViaReqResp(request, opts), nodeCollectionPromise]);
-      await Promise.race([collectionPromise, request.promise.promise]);
+      // Inner tasks observe requestTracker.checkCancelled() and stop themselves, so this settles shortly after cancellation.
+      await Promise.allSettled([this.collectFastViaReqResp(request, opts), nodeCollectionPromise]);
     } catch (err) {
-      // Log and swallow all errors
-      const logCtx = {
+      this.log.error(`Error collecting txs for ${request.type} for slot ${blockInfo.slotNumber}`, err, {
         ...blockInfo,
-        errorMessage: err instanceof Error ? err.message : undefined,
-        missingTxs: request.missingTxTracker.missingTxHashes.values().map(txHash => txHash.toString()),
-      };
-      if (err instanceof Error && err.name === 'TimeoutError') {
-        this.log.warn(`Timed out collecting txs for ${request.type} at slot ${blockInfo.slotNumber}`, logCtx);
-      } else if (err instanceof Error && err.name === 'AbortError') {
-        this.log.warn(`Aborted collecting txs for ${request.type} at slot ${blockInfo.slotNumber}`, logCtx);
-      } else {
-        this.log.error(`Error collecting txs for ${request.type} for slot ${blockInfo.slotNumber}`, err, logCtx);
-      }
+        missingTxs: request.requestTracker.missingTxHashes.values().map(txHash => txHash.toString()),
+      });
     } finally {
       // Ensure no unresolved promises and remove the request from the set
-      request.promise.resolve();
+      request.requestTracker.cancel();
       this.requests.delete(request);
     }
   }
@@ -160,30 +143,28 @@ export class FastTxCollection {
    * the txs that have been requested less often whenever we need to send a new batch of requests. We ensure that no
    * tx is requested more than once at the same time to the same node.
    */
-  private async collectFastFromNodes(request: FastCollectionRequest, opts: { deadline: Date }): Promise<void> {
+  private async collectFastFromNodes(request: FastCollectionRequest): Promise<void> {
     if (this.nodes.length === 0) {
       return;
     }
 
     // Keep a shared priority queue of all txs pending to be requested, sorted by the number of attempts made to collect them.
-    const attemptsPerTx = [...request.missingTxTracker.missingTxHashes].map(txHash => ({
+    const attemptsPerTx = [...request.requestTracker.missingTxHashes].map(txHash => ({
       txHash,
       attempts: 0,
       found: false,
     }));
 
     // Returns once we have finished all node loops. Each loop finishes when the deadline is hit, or all txs have been collected.
-    await Promise.allSettled(this.nodes.map(node => this.collectFastFromNode(request, node, attemptsPerTx, opts)));
+    await Promise.allSettled(this.nodes.map(node => this.collectFastFromNode(request, node, attemptsPerTx)));
   }
 
   private async collectFastFromNode(
     request: FastCollectionRequest,
     node: TxSource,
     attemptsPerTx: { txHash: string; attempts: number; found: boolean }[],
-    opts: { deadline: Date },
   ) {
-    const notFinished = () =>
-      this.dateProvider.now() <= +opts.deadline && !request.missingTxTracker.allFetched() && this.requests.has(request);
+    const notFinished = () => !request.requestTracker.checkCancelled();
 
     const maxParallelRequests = this.config.txCollectionFastMaxParallelRequestsPerNode;
     const maxBatchSize = this.config.txCollectionNodeRpcMaxBatchSize;
@@ -200,7 +181,7 @@ export class FastTxCollection {
           if (!txToRequest) {
             // No more txs to process
             break;
-          } else if (!request.missingTxTracker.isMissing(txToRequest.txHash)) {
+          } else if (!request.requestTracker.isMissing(txToRequest.txHash)) {
             // Mark as found if it was found somewhere else, we'll then remove it from the array.
             // We don't delete it now since 'array.splice' is pretty expensive, so we do it after sorting.
             txToRequest.found = true;
@@ -235,7 +216,7 @@ export class FastTxCollection {
           async () => {
             const result = await node.getTxsByHash(txHashes.map(TxHash.fromString));
             for (const tx of result.validTxs) {
-              request.missingTxTracker.markFetched(tx);
+              request.requestTracker.markFetched(tx);
             }
             return result;
           },
@@ -254,9 +235,12 @@ export class FastTxCollection {
           activeRequestsToThisNode.delete(requestedTx.txHash);
         }
 
-        // Sleep a bit until hitting the node again (or not, depending on config)
+        // Sleep a bit until hitting the node again, but wake up immediately on cancellation
         if (notFinished()) {
-          await sleep(this.config.txCollectionFastNodeIntervalMs);
+          await Promise.race([
+            sleep(this.config.txCollectionFastNodeIntervalMs),
+            request.requestTracker.cancellationToken,
+          ]);
         }
       }
     };
@@ -266,21 +250,20 @@ export class FastTxCollection {
   }
 
   private async collectFastViaReqResp(request: FastCollectionRequest, opts: { pinnedPeer?: PeerId }) {
-    const timeoutMs = +request.deadline - this.dateProvider.now();
     const pinnedPeer = opts.pinnedPeer;
     const blockInfo = request.blockInfo;
     const slotNumber = blockInfo.slotNumber;
-    if (timeoutMs < 100) {
+    if (request.requestTracker.timeoutMs < 100) {
       this.log.warn(
         `Not initiating fast reqresp for txs for ${request.type} at slot ${blockInfo.slotNumber} due to timeout`,
-        { timeoutMs, ...blockInfo },
+        { timeoutMs: request.requestTracker.timeoutMs, ...blockInfo },
       );
       return;
     }
 
     this.log.debug(
-      `Starting fast reqresp for ${request.missingTxTracker.numberOfMissingTxs} txs for ${request.type} at slot ${blockInfo.slotNumber}`,
-      { ...blockInfo, timeoutMs, pinnedPeer },
+      `Starting fast reqresp for ${request.requestTracker.numberOfMissingTxs} txs for ${request.type} at slot ${blockInfo.slotNumber}`,
+      { ...blockInfo, timeoutMs: request.requestTracker.timeoutMs, pinnedPeer },
     );
 
     try {
@@ -289,34 +272,28 @@ export class FastTxCollection {
           let result: Tx[];
           if (request.type === 'proposal') {
             result = await this.missingTxsCollector.collectTxs(
-              request.missingTxTracker,
+              request.requestTracker,
               request.blockProposal,
               pinnedPeer,
-              timeoutMs,
             );
           } else if (request.type === 'block') {
             const blockTxsSource = {
               txHashes: request.block.body.txEffects.map(e => e.txHash),
               archive: request.block.archive.root,
             };
-            result = await this.missingTxsCollector.collectTxs(
-              request.missingTxTracker,
-              blockTxsSource,
-              pinnedPeer,
-              timeoutMs,
-            );
+            result = await this.missingTxsCollector.collectTxs(request.requestTracker, blockTxsSource, pinnedPeer);
           } else {
             throw new Error(`Unknown request type: ${(request as any).type}`);
           }
           return { validTxs: result, invalidTxHashes: [] };
         },
-        Array.from(request.missingTxTracker.missingTxHashes),
+        Array.from(request.requestTracker.missingTxHashes),
         { description: `reqresp for slot ${slotNumber}`, method: 'fast-req-resp', ...opts, ...request.blockInfo },
         this.getAddContext(request),
       );
     } catch (err) {
       this.log.error(`Error sending fast reqresp request for txs`, err, {
-        txs: [...request.missingTxTracker.missingTxHashes],
+        txs: [...request.requestTracker.missingTxHashes],
         ...blockInfo,
       });
     }
@@ -340,20 +317,19 @@ export class FastTxCollection {
       for (const tx of txs) {
         const txHash = tx.txHash.toString();
         // Remove the tx hash from the missing set, and add it to the found set.
-        if (request.missingTxTracker.markFetched(tx)) {
+        if (request.requestTracker.markFetched(tx)) {
           this.log.trace(`Found tx ${txHash} for fast collection request`, {
             ...request.blockInfo,
             txHash: tx.txHash.toString(),
             type: request.type,
           });
-        }
-        // If we found all txs for this request, we resolve the promise
-        if (request.missingTxTracker.allFetched()) {
-          this.log.trace(`All txs found for fast collection request`, {
-            ...request.blockInfo,
-            type: request.type,
-          });
-          request.promise.resolve();
+          if (request.requestTracker.allFetched()) {
+            this.log.trace(`All txs found for fast collection request`, {
+              ...request.blockInfo,
+              type: request.type,
+            });
+            break;
+          }
         }
       }
     }
@@ -366,8 +342,7 @@ export class FastTxCollection {
   public stopCollectingForBlocksUpTo(blockNumber: BlockNumber): void {
     for (const request of this.requests) {
       if (request.blockInfo.blockNumber <= blockNumber) {
-        request.promise.reject(new AbortError(`Stopped collecting txs up to block ${blockNumber}`));
-        this.requests.delete(request);
+        request.requestTracker.cancel();
       }
     }
   }
@@ -379,8 +354,7 @@ export class FastTxCollection {
   public stopCollectingForBlocksAfter(blockNumber: BlockNumber): void {
     for (const request of this.requests) {
       if (request.blockInfo.blockNumber > blockNumber) {
-        request.promise.reject(new AbortError(`Stopped collecting txs after block ${blockNumber}`));
-        this.requests.delete(request);
+        request.requestTracker.cancel();
       }
     }
   }
```

### yarn-project/p2p/src/services/tx_collection/missing_txs_tracker.ts
```diff
@@ -1,52 +0,0 @@
-import { TxHash } from '@aztec/stdlib/tx';
-import type { Tx } from '@aztec/stdlib/tx';
-
-/**
- * Tracks which transactions are still missing and need to be fetched.
- * Allows external code to mark transactions as fetched, enabling coordination
- * between multiple fetching mechanisms (e.g., BatchTxRequester and Rpc Node requests).
- */
-export interface IMissingTxsTracker {
-  /** Returns the set of transaction hashes that are still missing. */
-  get missingTxHashes(): Set<string>;
-  /** Size of this.missingTxHashes */
-  get numberOfMissingTxs(): number;
-  /** Are all requested txs are fetched */
-  allFetched(): boolean;
-  /** Checks that transaction is still missing */
-  isMissing(txHash: string): boolean;
-  /** Marks a transaction as fetched. Returns true if it was previously missing. */
-  markFetched(tx: Tx): boolean;
-  /** Get list of collected txs */
-  get collectedTxs(): Tx[];
-}
-
-export class MissingTxsTracker implements IMissingTxsTracker {
-  public readonly collectedTxs: Tx[] = [];
-
-  private constructor(public readonly missingTxHashes: Set<string>) {}
-
-  public static fromArray(hashes: TxHash[] | string[]) {
-    return new MissingTxsTracker(new Set(hashes.map(hash => hash.toString())));
-  }
-
-  markFetched(tx: Tx): boolean {
-    if (this.missingTxHashes.delete(tx.txHash.toString())) {
-      this.collectedTxs.push(tx);
-      return true;
-    }
-    return false;
-  }
-
-  get numberOfMissingTxs(): number {
-    return this.missingTxHashes.size;
-  }
-
-  allFetched(): boolean {
-    return this.numberOfMissingTxs === 0;
-  }
-
-  isMissing(txHash: string): boolean {
-    return this.missingTxHashes.has(txHash.toString());
-  }
-}
```

### yarn-project/p2p/src/services/tx_collection/proposal_tx_collector.ts
```diff
@@ -9,7 +9,7 @@ import type { BatchTxRequesterConfig } from '../reqresp/batch-tx-requester/confi
 import type { BatchTxRequesterLibP2PService } from '../reqresp/batch-tx-requester/interface.js';
 import type { IBatchRequestTxValidator } from '../reqresp/batch-tx-requester/tx_validator.js';
 import { type BlockTxsSource, ReqRespSubProtocol, chunkTxHashesRequest } from '../reqresp/index.js';
-import type { IMissingTxsTracker } from './missing_txs_tracker.js';
+import type { IRequestTracker } from './request_tracker.js';
 
 /**
  * Strategy interface for collecting missing transactions for a block or proposal.
@@ -18,17 +18,15 @@ import type { IMissingTxsTracker } from './missing_txs_tracker.js';
 export interface MissingTxsCollector {
   /**
    * Collect missing transactions for a block or proposal.
-   * @param missingTxsTracker - The missing transactions tracker
+   * @param requestTracker - The missing transactions tracker
    * @param blockTxsSource - The block or proposal containing the transactions
    * @param pinnedPeer - Optional peer expected to have the transactions
-   * @param timeoutMs - Timeout in milliseconds
    * @returns The collected transactions
    */
   collectTxs(
-    missingTxsTracker: IMissingTxsTracker,
+    requestTracker: IRequestTracker,
     blockTxsSource: BlockTxsSource,
     pinnedPeer: PeerId | undefined,
-    timeoutMs: number,
   ): Promise<Tx[]>;
 }
 
@@ -46,10 +44,9 @@ export class BatchTxRequesterCollector implements MissingTxsCollector {
   ) {}
 
   async collectTxs(
-    missingTxsTracker: IMissingTxsTracker,
+    requestTracker: IRequestTracker,
     blockTxsSource: BlockTxsSource,
     pinnedPeer: PeerId | undefined,
-    timeoutMs: number,
   ): Promise<Tx[]> {
     const {
       batchTxRequesterSmartParallelWorkerCount: smartParallelWorkerCount,
@@ -59,10 +56,9 @@ export class BatchTxRequesterCollector implements MissingTxsCollector {
     } = this.batchTxRequesterConfig ?? {};
 
     const batchRequester = new BatchTxRequester(
-      missingTxsTracker,
+      requestTracker,
       blockTxsSource,
       pinnedPeer,
-      timeoutMs,
       this.p2pService,
       this.log,
       this.dateProvider,
@@ -94,16 +90,15 @@ export class SendBatchRequestCollector implements MissingTxsCollector {
   ) {}
 
   async collectTxs(
-    missingTxsTracker: IMissingTxsTracker,
+    requestTracker: IRequestTracker,
     _blockTxsSource: BlockTxsSource,
     pinnedPeer: PeerId | undefined,
-    timeoutMs: number,
   ): Promise<Tx[]> {
     const txs = await this.p2pService.reqResp.sendBatchRequest<ReqRespSubProtocol.TX>(
       ReqRespSubProtocol.TX,
-      chunkTxHashesRequest(Array.from(missingTxsTracker.missingTxHashes).map(TxHash.fromString)),
+      chunkTxHashesRequest(Array.from(requestTracker.missingTxHashes).map(TxHash.fromString)),
       pinnedPeer,
-      timeoutMs,
+      requestTracker.timeoutMs,
       this.maxPeers,
       this.maxRetryAttempts,
     );
```

### yarn-project/p2p/src/services/tx_collection/request_tracker.ts
```diff
@@ -0,0 +1,127 @@
+import { type PromiseWithResolvers, promiseWithResolvers } from '@aztec/foundation/promise';
+import type { DateProvider } from '@aztec/foundation/timer';
+import { TxHash } from '@aztec/stdlib/tx';
+import type { Tx } from '@aztec/stdlib/tx';
+
+/**
+ * Tracks which transactions are still missing and need to be fetched.
+ * Manages the request deadline and serves as the sole source of cancellation signal.
+ * The request is cancelled when all txs are fetched or the deadline expires.
+ */
+export interface IRequestTracker {
+  /** Returns the set of transaction hashes that are still missing. */
+  get missingTxHashes(): Set<string>;
+  /** Size of this.missingTxHashes */
+  get numberOfMissingTxs(): number;
+  /** Are all requested txs fetched */
+  allFetched(): boolean;
+  /** Checks that transaction is still missing */
+  isMissing(txHash: string): boolean;
+  /** Marks a transaction as fetched. Returns true if it was previously missing. */
+  markFetched(tx: Tx): boolean;
+  /** Get list of collected txs */
+  get collectedTxs(): Tx[];
+  /** The deadline for this request. */
+  get deadline(): Date;
+  /** Remaining time in milliseconds until deadline. Returns 0 if already past. */
+  get timeoutMs(): number;
+  /** Checks whether the request is cancelled (deadline expired or all fetched). May trigger cancellation if deadline has passed. */
+  checkCancelled(): boolean;
+  /** Resolves when deadline expires or all txs are fetched. */
+  get cancellationToken(): Promise<void>;
+  /** Externally cancel the request. */
+  cancel(): void;
+}
+
+export class RequestTracker implements IRequestTracker {
+  public readonly collectedTxs: Tx[] = [];
+  private done = false;
+  private readonly cancellationTokenPromise: PromiseWithResolvers<void>;
+  private readonly deadlineTimer: ReturnType<typeof setTimeout> | undefined;
+
+  private constructor(
+    public readonly missingTxHashes: Set<string>,
+    public readonly deadline: Date,
+    private readonly dateProvider?: DateProvider,
+  ) {
+    this.cancellationTokenPromise = promiseWithResolvers<void>();
+
+    if (missingTxHashes.size === 0) {
+      this.finish();
+      return;
+    }
+
+    const now = this.dateProvider?.now() ?? Date.now();
+    const remaining = deadline.getTime() - now;
+    if (remaining <= 0) {
+      this.finish();
+    } else {
+      this.deadlineTimer = setTimeout(() => this.finish(), remaining);
+    }
+  }
+
+  public static create(hashes: TxHash[] | string[], deadline: Date, dateProvider?: DateProvider) {
+    return new RequestTracker(new Set(hashes.map(hash => hash.toString())), deadline, dateProvider);
+  }
+
+  markFetched(tx: Tx): boolean {
+    if (this.missingTxHashes.delete(tx.txHash.toString())) {
+      this.collectedTxs.push(tx);
+      if (this.allFetched()) {
+        this.finish();
+      }
+      return true;
+    }
+    return false;
+  }
+
+  get numberOfMissingTxs(): number {
+    return this.missingTxHashes.size;
+  }
+
+  allFetched(): boolean {
+    return this.numberOfMissingTxs === 0;
+  }
+
+  isMissing(txHash: string): boolean {
+    return this.missingTxHashes.has(txHash.toString());
+  }
+
+  get timeoutMs(): number {
+    const now = this.dateProvider?.now() ?? Date.now();
+    return Math.max(0, this.deadline.getTime() - now);
+  }
+
+  checkCancelled(): boolean {
+    if (this.done) {
+      return true;
+    }
+    // Synchronous fallback: check deadline even if setTimeout hasn't fired yet.
+    // This prevents macrotask starvation in tight async loops from blocking cancellation.
+    const now = this.dateProvider?.now() ?? Date.now();
+    if (now >= this.deadline.getTime()) {
+      this.finish();
+      return true;
+    }
+    return false;
+  }
+
+  get cancellationToken(): Promise<void> {
+    return this.cancellationTokenPromise.promise;
+  }
+
+  cancel(): void {
+    this.finish();
+  }
+
+  private finish() {
+    if (this.done) {
+      return;
+    }
+    this.done = true;
+    if (this.deadlineTimer) {
+      clearTimeout(this.deadlineTimer);
+    }
+    this.cancellationTokenPromise.resolve();
+  }
+}
```

### yarn-project/p2p/src/services/tx_collection/slow_tx_collection.ts
```diff
@@ -196,7 +196,7 @@ export class SlowTxCollection {
     // from mined unproven blocks it has seen in the past.
     const fastRequests = this.fastCollection.getFastCollectionRequests();
     const fastCollectionTxs: Set<string> = new Set(
-      fastRequests.values().flatMap(r => Array.from(r.missingTxTracker.missingTxHashes)),
+      fastRequests.values().flatMap(r => Array.from(r.requestTracker.missingTxHashes)),
     );
 
     // Return all missing txs that are not in fastCollectionTxs and are ready for reqresp if requested
```
