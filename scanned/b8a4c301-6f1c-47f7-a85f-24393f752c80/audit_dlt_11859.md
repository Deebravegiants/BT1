# [?] Fix race condition in MockIndexer getItemsOrThrow resolution (#1171)

## Summary
Severity: Unknown
Chain: Indexer
Component: enviodev/hyperindex
Published: 2026-05-01
Source: https://github.com/enviodev/hyperindex/commit/0990eb22ad7b971efd90ab74a9fb829afebc53a5
Type: security-commit

## Details
Fix race condition in MockIndexer getItemsOrThrow resolution (#1171)

* Settle dispatch queue in MockIndexer.getBatchWritePromise

After processedBatches increments, the indexer still needs to dispatch
follow-up actions (e.g. NextQuery, which schedules the next
source.getItemsOrThrow call) before the test's next resolve call has a
pending entry to match.

Without an extra microtask yield, concurrent initialEnterReorgThreshold
helpers and chained resolve->batch sequences race the dispatch and
observe an empty getItemsOrThrowCalls array, manifesting as flaky
failures in the multichain rollback tests.

Mirror the existing settle pattern from getRollbackReadyPromise.

https://claude.ai/code/session_018x4gnkTt9gMeDPFXSbeusn

* Add second microtask yield in getBatchWritePromise

A single yield was insufficient: the multichain rollback tests still
flake at ~25% locally and failed in CI (run 25179347427) at the
"Multi-chain reorg/rollback/reorg loop" assertion observing 0/0 events
processed.

Concurrent initialEnterReorgThreshold helpers leave a follow-up batch
increment (from the second chain's empty resolve) in flight; with one
yield the next getBatchWritePromise() can latch onto that stale
increment instead of waiting for the test's actual events to be
processed. A second yield drains that boundary.

20/20 local runs of Rollback_test.res.mjs now pass.

https://claude.ai/code/session_018x4gnkTt9gMeDPFXSbeusn

---------

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### scenarios/test_codegen/test/helpers/MockIndexer.res
```diff
@@ -366,6 +366,13 @@ module Indexer = {
           while before >= (gsManager->GlobalStateManager.getState).processedBatches {
             await Utils.delay(1)
           }
+          // Skip extra microtasks for indexer to fire follow-up actions
+          // (e.g. the NextQuery dispatch that schedules the next
+          // getItemsOrThrow call). Without this, callers that immediately
+          // call resolveGetItemsOrThrow can race the dispatch and observe
+          // an empty calls array.
+          await Utils.delay(0)
+          await Utils.delay(0)
           resolve()
         })
       },
```
