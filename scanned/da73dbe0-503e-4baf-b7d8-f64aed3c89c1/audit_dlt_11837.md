# [?] fix crash for events not own by extrinsic (#120)

## Summary
Severity: Unknown
Chain: Indexer
Component: subquery/subql
Published: 2021-01-25
Source: https://github.com/subquery/subql/commit/1a904ba76a3eecfe20e04713bf691e34acfafbc8
Type: security-commit

## Details
fix crash for events not own by extrinsic (#120)

## Patch
### packages/node/src/indexer/indexer.manager.ts
```diff
@@ -156,7 +156,11 @@ export class IndexerManager implements OnApplicationBootstrap {
         wrappedBlock,
         events,
       );
-      const wrappedEvents = SubstrateUtil.wrapEvents(wrappedExtrinsics, events);
+      const wrappedEvents = SubstrateUtil.wrapEvents(
+        wrappedExtrinsics,
+        events,
+        wrappedBlock,
+      );
       this.block$.next({
         block: wrappedBlock,
         extrinsics: wrappedExtrinsics,
```

### packages/node/src/utils/substrate.ts
```diff
@@ -75,10 +75,11 @@ function filterExtrinsicEvents(
 export function wrapEvents(
   extrinsics: SubstrateExtrinsic[],
   events: EventRecord[],
+  block: SubstrateBlock,
 ): SubstrateEvent[] {
   return events.reduce((acc, event, idx) => {
     const { phase } = event;
-    const wrappedEvent: SubstrateEvent = merge(event, { idx });
+    const wrappedEvent: SubstrateEvent = merge(event, { idx, block });
     if (phase.isApplyExtrinsic) {
       wrappedEvent.extrinsic = extrinsics[phase.asApplyExtrinsic.toNumber()];
     }
@@ -136,7 +137,7 @@ export function filterEvents(
 ): SubstrateEvent[] {
   if (!filter) return events;
   return events.filter(
-    ({ event, extrinsic: { block } }) =>
+    ({ block, event }) =>
       (filter.specVersion === undefined ||
         block.specVersion === undefined ||
         checkSpecRange(filter.specVersion, block.specVersion)) &&
```

### packages/types/src/interfaces.ts
```diff
@@ -31,4 +31,5 @@ export interface SubstrateEvent extends EventRecord {
   // index in the block
   idx: number;
   extrinsic?: SubstrateExtrinsic;
+  block: SubstrateBlock;
 }
```
