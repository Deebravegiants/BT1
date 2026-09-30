# [?] Merge pull request #1872 from ponder-sh/typedarray/fix-crash-recovery-checkpoint

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-07-07
Source: https://github.com/ponder-sh/ponder/commit/b90ad5288d8515c7f9ec83e2b1f6f6d6bd693a1c
Type: security-commit

## Details
Merge pull request #1872 from ponder-sh/typedarray/fix-crash-recovery-checkpoint

## Patch
### .changeset/light-walls-speak.md
```diff
@@ -0,0 +1,5 @@
+---
+"ponder": patch
+---
+
+Fixed a bug that caused duplicate events after crash recovery for apps with high event density.
```

### packages/core/src/sync/index.ts
```diff
@@ -365,19 +365,19 @@ export const createSync = async (params: {
             }
           }
 
+          // Removes events that have a checkpoint earlier than (or equal to)
+          // the crash recovery checkpoint.
           async function* sortCrashRecoveryEvents(
             eventGenerator: AsyncGenerator<{
               events: Event[];
               checkpoint: string;
             }>,
           ) {
             for await (const { events, checkpoint } of eventGenerator) {
-              // Sort out any events before the crash recovery checkpoint
-
               if (
                 crashRecoveryCheckpoint &&
                 events.length > 0 &&
-                events[0]!.checkpoint < crashRecoveryCheckpoint
+                events[0]!.checkpoint <= crashRecoveryCheckpoint
               ) {
                 const [, right] = partition(
                   events,
```
