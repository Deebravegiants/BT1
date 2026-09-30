# [?] fix: dropped tagging indices no longer cause a pxe crash on sync (#23044)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-05-12
Source: https://github.com/AztecProtocol/aztec-packages/commit/6226e13c668963a96b9deea420e180bc98da7c79
Type: security-commit

## Details
fix: dropped tagging indices no longer cause a pxe crash on sync (#23044)

Fixes #22949.

We keep track of the range of tagging indices used by a tx as
`(lowestIdx, highestIdx)` - we need this so that future transactions
start from `highest + 1` even if a previous tx has not yet been mined,
avoiding tag duplication. The lowest index is required in case of
transaction reverts: we walk all indices from low to high and test which
ones survived onchain, and that way determine the actual highest index
for a tx.

On sync, we validate that our records for a tx match the indices used in
said tx - this helps detect bugs (like the bug being fixed here). This
check started failing because our `(low, high)` record did not consider
the possibility of logs being squashed - if either `low` or `high` got
squashed then the range would change. Note that we don't care about
indices between low and high being squashed , gaps are ok - we only
really care about the edges.

This PR fixes this by inspecting tx effects to adjust the range prior to
storing the indices in the database. It hints at the need for a tagging
service layer, but that was a bigger change that I didn't want to
introduce here. I added tests for both new functions created, plus an
e2e regression test that checks we've fixed the original issue. I
validated that the test fails without this fix.

---------

Co-authored-by: Nicolas Chamo <nicolas@chamo.com.ar>
Co-authored-by: AztecBot <tech@aztecprotocol.com>
Co-authored-by: Maxim Vezenov <mvezenov@gmail.com>

## Patch
### noir-projects/noir-contracts/contracts/test/test_log_contract/src/main.nr
```diff
@@ -7,6 +7,7 @@ pub contract TestLog {
     use aztec::{
         macros::{events::event, functions::external, storage::storage},
         messages::message_delivery::MessageDelivery,
+        note::note_getter_options::NoteGetterOptions,
         oracle::random::random,
         protocol::{address::AztecAddress, traits::{FromField, Serialize}},
         state_vars::{Owned, PrivateSet},
@@ -93,6 +94,24 @@ pub contract TestLog {
         self.emit(ExampleNestedEvent { nested: NestedStruct { a, b, c }, extra_value: extra });
     }
 
+    /// This emits two note messages using unconstrained onchain delivery, consuming two tag indices. The note
+    /// from the first message is nullified in the same transaction, resulting in note, nullifier and logs being
+    /// squashed.
+    ///
+    /// Used to verify that PXE successfully handles scenarios where used tagging indices don't make it their way to the
+    /// tx effects due to squashing.
+    #[external("private")]
+    fn deliver_squashed_and_surviving_notes(other: AztecAddress) {
+        let note_set = self.storage.example_set.at(other);
+
+        // Create the first note and message, then immediately nullify. This squashes all effects.
+        note_set.insert(FieldNote { value: 0 }).deliver(MessageDelivery.ONCHAIN_UNCONSTRAINED);
+        let _ = note_set.pop_notes(NoteGetterOptions::new());
+
+        // Deliver a second note message. Only this one will be included in the logs.
+        note_set.insert(FieldNote { value: 1 }).deliver(MessageDelivery.ONCHAIN_UNCONSTRAINED);
+    }
+
     #[external("private")]
     fn emit_encrypted_events_nested(other: AztecAddress, num_nested_calls: u32) {
         // Safety: We use the following just as an arbitrary test value
```

### yarn-project/end-to-end/src/e2e_event_logs.test.ts
```diff
@@ -262,4 +262,29 @@ describe('Logs', () => {
       expect(allTags.size).toBe(tx1NumLogs + tx2NumLogs);
     });
   });
+
+  describe('tagging cache reconciliation against kernel squashing', () => {
+    // Regression test for https://github.com/AztecProtocol/aztec-packages/issues/22949.
+    //
+    // The PXE's tagging cache reserves an index for every log emission attempted during private execution, but the
+    // kernel may then squash some of those logs (e.g. when a note is created and nullified in the same tx, taking
+    // its delivery log with it). The PXE must reconcile the recorded ranges against the kernel's surviving private
+    // logs before persisting them, otherwise a subsequent tx sharing the same tagging secret hits a
+    // `Conflicting range` error when its tagging sync re-derives the range from on-chain data and notices a mismatch.
+    it('does not throw `Conflicting range` across consecutive squashing txs sharing a tagging secret', async () => {
+      // Each call reserves two indexes for the (sender, sender, contract) tagging secret and squashes the first
+      // delivery's (note, nullifier, log) triple. Pre-fix, the second call's tagging sync would observe that the
+      // first tx had recorded `[N, N+1]` while only `[N+1]` actually landed on chain, and throw.
+      // Using `account1Address` for both sender and recipient mirrors the original repro from #22949
+      // (`transfer_private_to_public(self, self, ...)`) and keeps the note's owner accessible from the wallet for
+      // in-tx nullification.
+      await testLogContract.methods
+        .deliver_squashed_and_surviving_notes(account1Address)
+        .send({ from: account1Address });
+
+      await testLogContract.methods
+        .deliver_squashed_and_surviving_notes(account1Address)
+        .send({ from: account1Address });
+    });
+  });
 });
```

### yarn-project/pxe/src/pxe.ts
```diff
@@ -84,6 +84,7 @@ import { PrivateEventStore } from './storage/private_event_store/private_event_s
 import { RecipientTaggingStore } from './storage/tagging_store/recipient_tagging_store.js';
 import { SenderAddressBookStore } from './storage/tagging_store/sender_address_book_store.js';
 import { SenderTaggingStore } from './storage/tagging_store/sender_tagging_store.js';
+import { persistSenderTaggingIndexRangesForTx } from './tagging/index.js';
 
 export type PackedPrivateEvent = InTx & {
   packedEvent: Fr[];
@@ -842,22 +843,20 @@ export class PXE {
           nodeRPCCalls: contractFunctionSimulator?.getStats().nodeRPCCalls,
         });
 
-        // While not strictly necessary to store tagging cache contents in the DB since we sync tagging indexes from
-        // chain before sending new logs, the sync can only see logs already included in blocks. If we send another
-        // transaction before this one is included in a block from this PXE, and that transaction contains a log with
-        // a tag derived from the same secret, we would reuse the tag and the transactions would be linked. Hence
-        // storing the tags here prevents linkage of txs sent from the same PXE.
-        const taggingIndexRangesUsedInTheTx = privateExecutionResult.entrypoint.taggingIndexRanges;
-        if (taggingIndexRangesUsedInTheTx.length > 0) {
-          const txHash = await txProvingResult.getTxHash();
-
-          await this.senderTaggingStore.storePendingIndexes(taggingIndexRangesUsedInTheTx, txHash, jobId);
-          this.log.debug(`Stored used tagging index ranges as sender for the tx`, {
-            taggingIndexRangesUsedInTheTx,
-          });
-        } else {
-          this.log.debug(`No tagging index ranges used in the tx`);
-        }
+        // We keep track of which tagging indices we've used in this tx so that we don't repeat them in future txs
+        // (which would link them) without having to rely on this tx being mined (and us seeing the indices being used
+        // onchain).
+        // Note that this must happen _after_ proving as it requires the proof's public inputs, from which the kernels
+        // may have removed some logs due to note-nullifier squashing - this may lead to range of tagging indices we've
+        // actually used to being reduced.
+        await persistSenderTaggingIndexRangesForTx(
+          this.senderTaggingStore,
+          privateExecutionResult.entrypoint.taggingIndexRanges,
+          publicInputs,
+          () => txProvingResult.getTxHash(),
+          jobId,
+          this.log,
+        );
 
         return txProvingResult;
       } catch (err: any) {
```

### yarn-project/pxe/src/tagging/index.ts
```diff
@@ -11,6 +11,7 @@
 
 export { syncTaggedPrivateLogs } from './recipient_sync/sync_tagged_private_logs.js';
 export { syncSenderTaggingIndexes } from './sender_sync/sync_sender_tagging_indexes.js';
+export { persistSenderTaggingIndexRangesForTx } from './persist_sender_tagging_index_ranges.js';
 export { UNFINALIZED_TAGGING_INDEXES_WINDOW_LEN } from './constants.js';
 export { getAllPrivateLogsByTags, getAllPublicLogsByTagsFromContract } from './get_all_logs_by_tags.js';
 
```

### yarn-project/pxe/src/tagging/persist_sender_tagging_index_ranges.test.ts
```diff
@@ -0,0 +1,107 @@
+import { type Logger, createLogger } from '@aztec/foundation/log';
+import type { PrivateKernelTailCircuitPublicInputs } from '@aztec/stdlib/kernel';
+import { type ExtendedDirectionalAppTaggingSecret, PrivateLog, SiloedTag } from '@aztec/stdlib/logs';
+import { randomExtendedDirectionalAppTaggingSecret } from '@aztec/stdlib/testing';
+import { TxHash } from '@aztec/stdlib/tx';
+
+import { jest } from '@jest/globals';
+import { type MockProxy, mock } from 'jest-mock-extended';
+
+import type { SenderTaggingStore } from '../storage/tagging_store/sender_tagging_store.js';
+import { persistSenderTaggingIndexRangesForTx } from './persist_sender_tagging_index_ranges.js';
+
+describe('persistSenderTaggingIndexRangesForTx', () => {
+  let secret: ExtendedDirectionalAppTaggingSecret;
+  let store: MockProxy<SenderTaggingStore>;
+  let publicInputs: MockProxy<PrivateKernelTailCircuitPublicInputs>;
+  let log: Logger;
+  let txHash: TxHash;
+  let getTxHash: jest.Mock<() => Promise<TxHash>>;
+
+  beforeAll(async () => {
+    secret = await randomExtendedDirectionalAppTaggingSecret();
+    log = createLogger('test:persist-sender-tagging-index-ranges');
+  });
+
+  beforeEach(() => {
+    store = mock<SenderTaggingStore>();
+    publicInputs = mock<PrivateKernelTailCircuitPublicInputs>();
+    txHash = TxHash.random();
+    getTxHash = jest.fn<() => Promise<TxHash>>().mockResolvedValue(txHash);
+  });
+
+  /** Builds a `PrivateLog` whose first field is the siloed tag for `(secret, index)`. */
+  async function survivingLogForIndex(index: number): Promise<PrivateLog> {
+    const tag = await SiloedTag.compute({ extendedSecret: secret, index });
+    return PrivateLog.fromBlobFields(1, [tag.value]);
+  }
+
+  it('does nothing when no recorded ranges are provided', async () => {
+    publicInputs.getNonEmptyPrivateLogs.mockReturnValue([]);
+
+    await persistSenderTaggingIndexRangesForTx(store, [], publicInputs, getTxHash, 'test', log);
+
+    expect(store.storePendingIndexes).not.toHaveBeenCalled();
+    expect(getTxHash).not.toHaveBeenCalled();
+  });
+
+  it('does nothing when every recorded index was squashed', async () => {
+    publicInputs.getNonEmptyPrivateLogs.mockReturnValue([]);
+
+    await persistSenderTaggingIndexRangesForTx(
+      store,
+      [{ extendedSecret: secret, lowestIndex: 1, highestIndex: 3 }],
+      publicInputs,
+      getTxHash,
+      'test',
+      log,
+    );
+
+    expect(store.storePendingIndexes).not.toHaveBeenCalled();
+    expect(getTxHash).not.toHaveBeenCalled();
+  });
+
+  it('persists recorded ranges unchanged when every index survives', async () => {
+    publicInputs.getNonEmptyPrivateLogs.mockReturnValue([
+      await survivingLogForIndex(1),
+      await survivingLogForIndex(2),
+      await survivingLogForIndex(3),
+    ]);
+
+    await persistSenderTaggingIndexRangesForTx(
+      store,
+      [{ extendedSecret: secret, lowestIndex: 1, highestIndex: 3 }],
+      publicInputs,
+      getTxHash,
+      'test',
+      log,
+    );
+
+    expect(store.storePendingIndexes).toHaveBeenCalledWith(
+      [{ extendedSecret: secret, lowestIndex: 1, highestIndex: 3 }],
+      txHash,
+      'test',
+    );
+    expect(getTxHash).toHaveBeenCalledTimes(1);
+  });
+
+  it('persists shrunk ranges when some indexes were squashed', async () => {
+    // Recorded range [1, 5], but only indexes 2 and 4 survived squashing.
+    publicInputs.getNonEmptyPrivateLogs.mockReturnValue([await survivingLogForIndex(2), await survivingLogForIndex(4)]);
+
+    await persistSenderTaggingIndexRangesForTx(
+      store,
+      [{ extendedSecret: secret, lowestIndex: 1, highestIndex: 5 }],
+      publicInputs,
+      getTxHash,
+      'test',
+      log,
+    );
+
+    expect(store.storePendingIndexes).toHaveBeenCalledWith(
+      [{ extendedSecret: secret, lowestIndex: 2, highestIndex: 4 }],
+      txHash,
+      'test',
+    );
+  });
+});
```

### yarn-project/pxe/src/tagging/persist_sender_tagging_index_ranges.ts
```diff
@@ -0,0 +1,57 @@
+import type { Logger } from '@aztec/foundation/log';
+import type { PrivateKernelTailCircuitPublicInputs } from '@aztec/stdlib/kernel';
+import type { TaggingIndexRange } from '@aztec/stdlib/logs';
+import type { TxHash } from '@aztec/stdlib/tx';
+
+import type { SenderTaggingStore } from '../storage/tagging_store/sender_tagging_store.js';
+import { reconcileTaggingIndexRangesAgainstSurvivingTags } from './reconcile_tagging_index_ranges.js';
+
+/**
+ * Persists the tagging index ranges that a tx used as a sender, after reconciling them against the kernel's surviving
+ * private logs.
+ *
+ * The tagging index cache reserves an index for every log emission attempted during private execution, but the kernel
+ * may then squash some of those logs (e.g. when a note is created and nullified within the same tx). This function
+ * shrinks the recorded ranges to match the actual on-chain footprint before writing them, so that what we persist is
+ * consistent with what the network will see.
+ *
+ * @remarks Storing the recorded ranges in the DB may not be seen as necessary because we sync from chain before sending
+ * new logs, but the sync can only see logs already included in blocks. If we sent another transaction before this one
+ * was included from the same PXE, and that transaction contained a log with a tag derived from the same secret, we
+ * would reuse the tag and the transactions would be linked. Persisting in the DB prevents that linkage.
+ *
+ * @param store - The sender tagging store.
+ * @param recordedRanges - The tagging index ranges as recorded during private execution (pre-squash).
+ * @param publicInputs - The final kernel public inputs, used to determine which private logs survived squashing.
+ * @param getTxHash - Lazy accessor for the tx hash. Called only when there is something to persist, since computing
+ * the tx hash is expensive.
+ * @param jobId - Job context for staged writes to the store. See `JobCoordinator` for more details.
+ * @param log - Logger.
+ */
+export async function persistSenderTaggingIndexRangesForTx(
+  store: SenderTaggingStore,
+  recordedRanges: TaggingIndexRange[],
+  publicInputs: PrivateKernelTailCircuitPublicInputs,
+  getTxHash: () => Promise<TxHash>,
+  jobId: string,
+  log: Logger,
+): Promise<void> {
+  if (recordedRanges.length === 0) {
+    log.debug(`No tagging index ranges used in the tx`);
+    return;
+  }
+
+  const survivingTags = new Set(
+    publicInputs.getNonEmptyPrivateLogs().map(privateLog => privateLog.fields[0].toString()),
+  );
+  const reconciledRanges = await reconcileTaggingIndexRangesAgainstSurvivingTags(recordedRanges, survivingTags);
+
+  if (reconciledRanges.length === 0) {
+    log.debug(`All tagging index ranges used in the tx were squashed by the kernel`, { recordedRanges });
+    return;
+  }
+
+  const txHash = await getTxHash();
+  await store.storePendingIndexes(reconciledRanges, txHash, jobId);
+  log.debug(`Stored used tagging index ranges as sender for the tx`, { recordedRanges, reconciledRanges });
+}
```

### yarn-project/pxe/src/tagging/reconcile_tagging_index_ranges.test.ts
```diff
@@ -0,0 +1,179 @@
+import { type ExtendedDirectionalAppTaggingSecret, SiloedTag } from '@aztec/stdlib/logs';
+import { randomExtendedDirectionalAppTaggingSecret } from '@aztec/stdlib/testing';
+
+import { reconcileTaggingIndexRangesAgainstSurvivingTags } from './reconcile_tagging_index_ranges.js';
+
+describe('reconcileTaggingIndexRangesAgainstSurvivingTags', () => {
+  let secret1: ExtendedDirectionalAppTaggingSecret;
+  let secret2: ExtendedDirectionalAppTaggingSecret;
+
+  beforeAll(async () => {
+    secret1 = await randomExtendedDirectionalAppTaggingSecret();
+    secret2 = await randomExtendedDirectionalAppTaggingSecret();
+  });
+
+  /** Builds a set of surviving siloed tag values from a list of `(secret, index)` pairs. */
+  async function buildSurvivingTags(
+    pairs: Array<{ secret: ExtendedDirectionalAppTaggingSecret; index: number }>,
+  ): Promise<Set<string>> {
+    const tags = await Promise.all(
+      pairs.map(({ secret, index }) => SiloedTag.compute({ extendedSecret: secret, index })),
+    );
+    return new Set(tags.map(t => t.value.toString()));
+  }
+
+  it('returns empty when given no ranges', async () => {
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags([], new Set());
+    expect(reconciled).toEqual([]);
+  });
+
+  it('drops a range when no surviving tags are provided', async () => {
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 3 }],
+      new Set(),
+    );
+    expect(reconciled).toEqual([]);
+  });
+
+  it('leaves the range unchanged when every index survives', async () => {
+    const survivingTags = await buildSurvivingTags([
+      { secret: secret1, index: 1 },
+      { secret: secret1, index: 2 },
+      { secret: secret1, index: 3 },
+    ]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 3 }],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 3 }]);
+  });
+
+  it('lowers `highestIndex` when trailing indexes are squashed', async () => {
+    const survivingTags = await buildSurvivingTags([
+      { secret: secret1, index: 1 },
+      { secret: secret1, index: 2 },
+    ]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 5 }],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 2 }]);
+  });
+
+  it('raises `lowestIndex` when leading indexes are squashed', async () => {
+    const survivingTags = await buildSurvivingTags([
+      { secret: secret1, index: 4 },
+      { secret: secret1, index: 5 },
+    ]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 5 }],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([{ extendedSecret: secret1, lowestIndex: 4, highestIndex: 5 }]);
+  });
+
+  it('shrinks both bounds when leading and trailing indexes are squashed', async () => {
+    const survivingTags = await buildSurvivingTags([
+      { secret: secret1, index: 3 },
+      { secret: secret1, index: 4 },
+    ]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 6 }],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([{ extendedSecret: secret1, lowestIndex: 3, highestIndex: 4 }]);
+  });
+
+  it('keeps the original bounds when only interior indexes are squashed', async () => {
+    const survivingTags = await buildSurvivingTags([
+      { secret: secret1, index: 1 },
+      { secret: secret1, index: 5 },
+    ]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 5 }],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 5 }]);
+  });
+
+  it('collapses to a single-index range when only one interior index survives', async () => {
+    const survivingTags = await buildSurvivingTags([{ secret: secret1, index: 3 }]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 1, highestIndex: 5 }],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([{ extendedSecret: secret1, lowestIndex: 3, highestIndex: 3 }]);
+  });
+
+  it('drops a fully-squashed range while keeping unrelated ranges that survive', async () => {
+    const survivingTags = await buildSurvivingTags([
+      { secret: secret2, index: 1 },
+      { secret: secret2, index: 2 },
+    ]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [
+        { extendedSecret: secret1, lowestIndex: 1, highestIndex: 3 },
+        { extendedSecret: secret2, lowestIndex: 1, highestIndex: 2 },
+      ],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([{ extendedSecret: secret2, lowestIndex: 1, highestIndex: 2 }]);
+  });
+
+  it('reconciles each range independently when multiple secrets are provided', async () => {
+    const survivingTags = await buildSurvivingTags([
+      { secret: secret1, index: 2 },
+      { secret: secret1, index: 3 },
+      { secret: secret2, index: 5 },
+    ]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [
+        { extendedSecret: secret1, lowestIndex: 1, highestIndex: 4 },
+        { extendedSecret: secret2, lowestIndex: 4, highestIndex: 6 },
+      ],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([
+      { extendedSecret: secret1, lowestIndex: 2, highestIndex: 3 },
+      { extendedSecret: secret2, lowestIndex: 5, highestIndex: 5 },
+    ]);
+  });
+
+  it('keeps a single-index range when its index survives', async () => {
+    const survivingTags = await buildSurvivingTags([{ secret: secret1, index: 7 }]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 7, highestIndex: 7 }],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([{ extendedSecret: secret1, lowestIndex: 7, highestIndex: 7 }]);
+  });
+
+  it('drops a single-index range when its index is squashed', async () => {
+    const survivingTags = await buildSurvivingTags([{ secret: secret2, index: 7 }]);
+
+    const reconciled = await reconcileTaggingIndexRangesAgainstSurvivingTags(
+      [{ extendedSecret: secret1, lowestIndex: 7, highestIndex: 7 }],
+      survivingTags,
+    );
+
+    expect(reconciled).toEqual([]);
+  });
+});
```

### yarn-project/pxe/src/tagging/reconcile_tagging_index_ranges.ts
```diff
@@ -0,0 +1,102 @@
+import { type ExtendedDirectionalAppTaggingSecret, SiloedTag, type TaggingIndexRange } from '@aztec/stdlib/logs';
+
+/**
+ * Reconciles tagging index ranges recorded by the PXE during private execution against the set of siloed tags whose
+ * private logs survived to the final kernel output.
+ *
+ * Each input range is the contiguous `[lowestIndex, highestIndex]` set of indexes that the tagging index cache
+ * reserved for a given `(sender, recipient, app)` secret while a tx was being executed. The kernel may then squash
+ * some of those logs (e.g. when a note is created and nullified within the same tx, taking its log with it), so the
+ * actual on-chain footprint can be a strict subset of what was reserved.
+ *
+ * For each input range, this function shrinks `[lowestIndex, highestIndex]` so that both bounds correspond to indexes
+ * that actually survived, trimming any dropped indices at the front or the back. It is possible that some interior
+ * indexes were also dropped, leaving gaps between the lowest and highest indices, but we ignore those and accept the
+ * resulting inefficiency rather than complicate the tagging model with one in which transactions may use interleaved
+ * indices.
+ *
+ * Trimming tailing indices (e.g. `highestIndex`) is highly useful as it lets us reuse those indices in future
+ * transactions. Trimming indices at the front (e.g. `lowestIndex`) is not as impactful since we will not ever use a
+ * tagging index if a larger one exists (same as with gaps), but it does help in both making the consistency check
+ * between database and transaction effects cheaper (as there's fewer logs to test) and making the database more
+ * accurately reflect reality.
+ *
+ * Ranges with no surviving indexes are dropped from the output entirely.
+ *
+ * Example scenario:
+ *   - used indexes 3 to 7, kerel squashed indexes 3, 5, and 7:
+ *      - range: [3, 7]
+ *      - survived: set(3, 5, 7)
+ *      - output: [4, 6]  (trimmed from both ends, gap at 5 is tolerated)
+ *
+ * @param ranges - The tagging index ranges as recorded during private execution (pre-squash).
+ * @param survivingTags - The set of siloed tag values (as strings) of private logs that survived kernel squashing.
+ * @returns The reconciled ranges, with bounds tightened to surviving indexes and fully-squashed ranges removed.
+ */
+export async function reconcileTaggingIndexRangesAgainstSurvivingTags(
+  ranges: TaggingIndexRange[],
+  survivingTags: Set<string>,
+): Promise<TaggingIndexRange[]> {
+  const reconciled: TaggingIndexRange[] = [];
+
+  for (const range of ranges) {
+    const newLowestIndex = await findFirstSurvivingIndex(
+      range.extendedSecret,
+      range.lowestIndex,
+      range.highestIndex,
+      survivingTags,
+    );
+    if (newLowestIndex === undefined) {
+      // No index in this range corresponds to a surviving log: the entire range was squashed.
+      continue;
+    }
+
+    // newLowestIndex is itself a survivor, so the backward scan is guaranteed to find at least that index.
+    const newHighestIndex = await findLastSurvivingIndex(
+      range.extendedSecret,
+      newLowestIndex,
+      range.highestIndex,
+      survivingTags,
+    );
+
+    reconciled.push({
+      extendedSecret: range.extendedSecret,
+      lowestIndex: newLowestIndex,
+      highestIndex: newHighestIndex!,
+    });
+  }
+
+  return reconciled;
+}
+
+/** Scans `[start, end]` ascending and returns the first index whose siloed tag is in `survivingTags`. */
+async function findFirstSurvivingIndex(
+  extendedSecret: ExtendedDirectionalAppTaggingSecret,
+  start: number,
+  end: number,
+  survivingTags: Set<string>,
+): Promise<number | undefined> {
+  for (let index = start; index <= end; index++) {
+    const tag = await SiloedTag.compute({ extendedSecret, index });
+    if (survivingTags.has(tag.value.toString())) {
+      return index;
+    }
+  }
+  return undefined;
+}
+
+/** Scans `[start, end]` descending and returns the first index whose siloed tag is in `survivingTags`. */
+async function findLastSurvivingIndex(
+  extendedSecret: ExtendedDirectionalAppTaggingSecret,
+  start: number,
+  end: number,
+  survivingTags: Set<string>,
+): Promise<number | undefined> {
+  for (let index = end; index >= start; index--) {
+    const tag = await SiloedTag.compute({ extendedSecret, index });
+    if (survivingTags.has(tag.value.toString())) {
+      return index;
+    }
+  }
+  return undefined;
+}
```
