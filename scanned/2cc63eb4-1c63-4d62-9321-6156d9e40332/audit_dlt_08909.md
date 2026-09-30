# [?] fix `subtract with overflow` bug

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2024-12-13
Source: https://github.com/software-mansion/pathfinder/commit/cbd71d9bcf68d87e2b9e9ed196f50a102d687cd3
Type: security-commit

## Details
fix `subtract with overflow` bug

## Patch
### crates/storage/src/connection/event.rs
```diff
@@ -584,7 +584,7 @@ pub(crate) fn rebuild_running_event_filter(
     )?;
 
     let Some(latest) = latest_stmt
-        .query_row([], |row| row.get::<_, u64>(0))
+        .query_row([], |row| row.get_block_number(0))
         .optional()
         .context("Querying latest block number")?
     else {
@@ -600,12 +600,22 @@ pub(crate) fn rebuild_running_event_filter(
         .context("Querying last stored event filter to_block")?;
 
     let first_running_event_filter_block = match last_to_block {
+        // Last stored block was at the end of the running event filter range, no need
+        // to rebuild.
+        Some(last_to_block) if last_to_block == latest.get() => {
+            let next_block = latest + 1;
+
+            return Ok(RunningEventFilter {
+                filter: AggregateBloom::new(next_block),
+                next_block,
+            });
+        }
         Some(last_to_block) => BlockNumber::new_or_panic(last_to_block + 1),
         // Event filter table is empty, rebuild running filter from the genesis block.
         None => BlockNumber::GENESIS,
     };
 
-    let total_blocks_to_cover = latest - first_running_event_filter_block.get();
+    let total_blocks_to_cover = latest.get() - first_running_event_filter_block.get();
     let mut covered_blocks = 0;
     let mut last_progress_report = Instant::now();
 
```
