# [?] fix: crash recovery checkpoint inclusivity

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-07-06
Source: https://github.com/ponder-sh/ponder/commit/0b64de16eb3315d7a16b3ce7f4c5cb24aa4e4595
Type: security-commit

## Details
fix: crash recovery checkpoint inclusivity

## Patch
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
