# [?] Merge pull request #7415 from benjamin-stacks/fix/neighbor-sort-underflow

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-07-20
Source: https://github.com/stacks-network/stacks-core/commit/37dc20a9f658442cdcac32c7568387884ec4e9ea
Type: security-commit

## Details
Merge pull request #7415 from benjamin-stacks/fix/neighbor-sort-underflow

fix: unchecked integer underflow in p2p neighbor sort

## Patch
### changelog.d/7415-neighbor-compare-underflow.fixed
```diff
@@ -0,0 +1 @@
+Ensure sorting p2p neighbors by uptime behaves predictably in the face of system clock adjustments.
\ No newline at end of file
```

### stackslib/src/net/prune.rs
```diff
@@ -107,8 +107,8 @@ impl PeerNetwork {
     /// Within uptime buckets, sort by health.
     fn compare_neighbor_uptime_health(stats1: &NeighborStats, stats2: &NeighborStats) -> Ordering {
         let now = get_epoch_time_secs();
-        let uptime_1 = (now - stats1.first_contact_time) as f64;
-        let uptime_2 = (now - stats2.first_contact_time) as f64;
+        let uptime_1 = now.saturating_sub(stats1.first_contact_time) as f64;
+        let uptime_2 = now.saturating_sub(stats2.first_contact_time) as f64;
 
         let uptime_bucket_1 = fmax!(0.0, uptime_1.log2().round()) as u64;
         let uptime_bucket_2 = fmax!(0.0, uptime_2.log2().round()) as u64;
```
