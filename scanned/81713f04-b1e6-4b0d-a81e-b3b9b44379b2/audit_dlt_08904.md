# [?] Merge pull request #3148 from eqlabs/krisztian/fix-block-time-metrics-underflow

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2025-12-17
Source: https://github.com/software-mansion/pathfinder/commit/c20315572eedcdecce8596376ce0d348712a9a47
Type: security-commit

## Details
Merge pull request #3148 from eqlabs/krisztian/fix-block-time-metrics-underflow

fix(pathfinder/sync): prevent underflow in block time metrics

## Patch
### crates/pathfinder/src/state/sync.rs
```diff
@@ -832,8 +832,11 @@ async fn consumer(
                     metrics::histogram!("block_processing_duration_seconds")
                         .record(update_t.as_secs_f64());
                     metrics::gauge!("block_latency").set(latency as f64);
-                    metrics::gauge!("block_time")
-                        .set((block_timestamp.get() - latest_timestamp.get()) as f64);
+                    if let Some(block_time_secs) =
+                        block_timestamp.get().checked_sub(latest_timestamp.get())
+                    {
+                        metrics::gauge!("block_time").set(block_time_secs as f64);
+                    }
                     latest_timestamp = block_timestamp;
                     next_number += 1;
 
```
