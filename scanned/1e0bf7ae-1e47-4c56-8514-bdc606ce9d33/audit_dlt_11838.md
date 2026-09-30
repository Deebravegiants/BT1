# [?] solana: prevent crash on empty rpc upstream batches

## Summary
Severity: Unknown
Chain: Indexer
Component: subsquid/squid-sdk
Published: 2026-05-07
Source: https://github.com/subsquid/squid-sdk/commit/061b6c26d3fa9ab8cbad77d7abc32aef0b7a08cd
Type: security-commit

## Details
solana: prevent crash on empty rpc upstream batches

## Patch
### common/changes/@subsquid/solana-rpc/master_2026-05-07-13-42.json
```diff
@@ -0,0 +1,10 @@
+{
+  "changes": [
+    {
+      "packageName": "@subsquid/solana-rpc",
+      "comment": "Handle empty batches while applying the upper boundary limit",
+      "type": "patch"
+    }
+  ],
+  "packageName": "@subsquid/solana-rpc"
+}
```

### solana/solana-rpc/src/data-source/chain-fixer.test.ts
```diff
@@ -137,29 +137,12 @@ describe('limitUpperBoundary', () => {
         expect(out).toHaveLength(0)
     })
 
-    // FIXME: TEST NEEDS TO BE FIXED — documents a crash on upstream edge input.
-    //
-    // What's wrong: `limitUpperBoundary` starts its per-batch check with
-    //     if (last(batch.blocks).slot >= to) { ... }
-    // and `last()` from `@subsquid/util-internal` asserts `array.length > 0`.
-    // An upstream batch that happens to arrive empty (skipped-slot windows
-    // from certain fetcher configurations, a filter chain above
-    // limitUpperBoundary that could produce an empty IngestBatch, a faulty
-    // RPC response) will crash the consumer with a generic AssertionError,
-    // not "here's an empty batch, nothing to do".
-    //
-    // Fix direction: guard the call — e.g.
-    //     if (batch.blocks.length === 0) { yield batch; continue }
-    // or drop the batch silently. Either is safer than throwing.
-    //
-    // Wrapped in `it.fails` until the guard lands; vitest reports an
-    // unexpected pass the day it's fixed.
-    it.fails('passes through an empty upstream batch instead of crashing', async () => {
+    it('passes through an empty upstream batch instead of crashing', async () => {
         const batches: IngestBatch[] = [{blocks: []}]
 
         const out = await drain(limitUpperBoundary(10, yieldBatches(...batches)))
 
-        expect(out).toEqual([{blocks: []}]) // desired: yield the empty batch through
+        expect(out).toEqual([{blocks: []}])
     })
 })
 
```

### solana/solana-rpc/src/data-source/chain-fixer.ts
```diff
@@ -28,6 +28,11 @@ export async function* limitUpperBoundary(
     upstream: AsyncIterable<IngestBatch>,
 ): AsyncIterable<IngestBatch> {
     for await (let batch of upstream) {
+        if (batch.blocks.length === 0) {
+            yield batch
+            continue
+        }
+
         if (last(batch.blocks).slot >= to) {
             batch.blocks = batch.blocks.filter((b) => b.slot <= to)
             if (batch.blocks.length > 0) {
```
