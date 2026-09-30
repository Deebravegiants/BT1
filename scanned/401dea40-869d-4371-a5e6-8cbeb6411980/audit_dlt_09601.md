# [?] Fix panic in get_logs. (#1484)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-05-25
Source: https://github.com/Conflux-Chain/conflux-rust/commit/7b9897067895388ca9da64b0e23350439d137db9
Type: security-commit

## Details
Fix panic in get_logs. (#1484)

If `to_epoch` is too large, `get_pivot_block_arena_index` will panic.

## Patch
### core/src/consensus/mod.rs
```diff
@@ -749,6 +749,13 @@ impl ConsensusGraph {
                 });
             }
 
+            if to_epoch > inner.best_epoch_number() {
+                return Err(FilterError::OutOfBoundEpochNumber {
+                    to_epoch,
+                    max_epoch: inner.best_epoch_number(),
+                });
+            }
+
             let blooms = filter.bloom_possibilities();
             let mut blocks = vec![];
             for epoch_number in from_epoch..(to_epoch + 1) {
```

### primitives/src/filter.rs
```diff
@@ -28,13 +28,26 @@ use std::{error, fmt};
 /// Errors concerning log filtering.
 pub enum FilterError {
     /// Filter has wrong epoch numbers set.
-    InvalidEpochNumber { from_epoch: u64, to_epoch: u64 },
+    InvalidEpochNumber {
+        from_epoch: u64,
+        to_epoch: u64,
+    },
+
+    OutOfBoundEpochNumber {
+        to_epoch: u64,
+        max_epoch: u64,
+    },
 
     /// Roots for verifying the requested epochs are unavailable.
-    UnableToVerify { epoch: u64, latest_verifiable: u64 },
+    UnableToVerify {
+        epoch: u64,
+        latest_verifiable: u64,
+    },
 
     /// The block requested does not exist
-    UnknownBlock { hash: H256 },
+    UnknownBlock {
+        hash: H256,
+    },
 
     /// Filter error with custom error message (e.g. timeout)
     Custom(String),
@@ -51,6 +64,13 @@ impl fmt::Display for FilterError {
                 "Filter has wrong epoch numbers set (from: {}, to: {})",
                 from_epoch, to_epoch
             },
+            OutOfBoundEpochNumber {
+                to_epoch,
+                max_epoch,
+            } => format! {
+                "Filter to_epoch is larger than the current best_epoch (to: {}, max: {})",
+                to_epoch, max_epoch,
+            },
             UnableToVerify {
                 epoch,
                 latest_verifiable,
```
