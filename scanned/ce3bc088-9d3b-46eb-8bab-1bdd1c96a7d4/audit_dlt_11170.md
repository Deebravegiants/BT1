# [?] Validate op batch groups to prevent trace panic (#2782)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-03-11
Source: https://github.com/0xMiden/miden-vm/commit/58dee7a264026dd54e182c317fd64ec86fd2ac24
Type: security-commit

## Details
Validate op batch groups to prevent trace panic (#2782)

* Validate op batch groups to prevent trace panic

* chore: add changelog for op batch validation

## Patch
### CHANGELOG.md
```diff
@@ -25,6 +25,7 @@
 - Introduced `FastProcessor` safe stack method accesses for event handlers ([#2797](https://github.com/0xMiden/miden-vm/pull/2797)).
 - Hardened syscall target validation to avoid panic paths and reject invalid digests at assembly time ([#2804](https://github.com/0xMiden/miden-vm/pull/2804)).
 - Add bounds to attacker-controlled allocation sizes in advice map and keccak256/sha512 precompiles ([#2805](https://github.com/0xMiden/miden-vm/pull/2805)).
+- Prevented a trace-generation panic by validating op batch groups in basic blocks ([#2782](https://github.com/0xMiden/miden-vm/pull/2782)).
 
 ## 0.21.1 (2026-02-24)
 
```

### core/src/mast/node/basic_block_node/mod.rs
```diff
@@ -34,6 +34,7 @@ pub const GROUP_SIZE: usize = 9;
 
 /// Maximum number of groups per batch.
 pub const BATCH_SIZE: usize = 8;
+const _: [(); 1] = [(); ((BATCH_SIZE & (BATCH_SIZE - 1)) == 0) as usize];
 
 // BASIC BLOCK NODE
 // ================================================================================================
@@ -439,7 +440,7 @@ impl BasicBlockNode {
 
 impl BasicBlockNode {
     /// Validates that this BasicBlockNode satisfies the core invariants:
-    /// 1. Power-of-two number of groups in each batch
+    /// 1. Non-final batches must be full (BATCH_SIZE groups), final batch must be power-of-two
     /// 2. No operation group ends with an operation requiring an immediate value
     /// 3. The last operation group in a batch cannot contain operations requiring immediate values
     /// 4. OpBatch structural consistency (num_groups <= BATCH_SIZE, group size <= GROUP_SIZE)
@@ -458,11 +459,22 @@ impl BasicBlockNode {
         Ok(())
     }
 
-    /// Validates that each batch has a power-of-two number of groups.
+    /// Validates that non-final batches are full and the final batch is power-of-two.
+    ///
+    /// This invariant is required by trace generation (see `num_op_groups`) and is expected to
+    /// hold for all serialized forests produced by the assembler; violations indicate corrupted
+    /// or malformed input.
     fn validate_power_of_two_groups(&self) -> Result<(), String> {
         for (batch_idx, batch) in self.op_batches.iter().enumerate() {
             let num_groups = batch.num_groups();
-            if !num_groups.is_power_of_two() {
+            if batch_idx + 1 < self.op_batches.len() {
+                if num_groups != BATCH_SIZE {
+                    return Err(format!(
+                        "Batch {}: {} groups is not full batch size {}",
+                        batch_idx, num_groups, BATCH_SIZE
+                    ));
+                }
+            } else if !num_groups.is_power_of_two() {
                 return Err(format!(
                     "Batch {}: {} groups is not power of two",
                     batch_idx, num_groups
```

### core/src/mast/node/basic_block_node/tests.rs
```diff
@@ -350,6 +350,12 @@ proptest! {
             assert!(batch.num_groups <= BATCH_SIZE);
             assert!(batch.num_groups.is_power_of_two());
         }
+        // All non-final batches must be full.
+        for (idx, batch) in batches.iter().enumerate() {
+            if idx + 1 < batches.len() {
+                assert_eq!(batch.num_groups, BATCH_SIZE);
+            }
+        }
 
         // The total number of operations should be preserved, modulo padding
         let total_ops_from_batches: usize = batches.iter().map(|batch| {
```

### core/src/mast/serialization/tests.rs
```diff
@@ -3,10 +3,11 @@ use std::string::ToString;
 use super::*;
 use crate::{
     Felt, ONE, Word,
+    chiplets::hasher,
     mast::{
         BasicBlockNodeBuilder, CallNodeBuilder, DynNodeBuilder, ExternalNodeBuilder,
         JoinNodeBuilder, LoopNodeBuilder, MastForestContributor, MastForestError, MastNodeExt,
-        SplitNodeBuilder, UntrustedMastForest,
+        OP_BATCH_SIZE, OpBatch, SplitNodeBuilder, UntrustedMastForest,
     },
     operations::{DebugOptions, Decorator, Operation},
     serde::SliceReader,
@@ -1527,6 +1528,83 @@ fn test_untrusted_forest_detects_hash_mismatch() {
     assert_matches!(result, Err(MastForestError::HashMismatch { .. }));
 }
 
+/// Build a packed operation group from op codes.
+fn build_group(ops: &[Operation]) -> Felt {
+    let mut group = 0u64;
+    for (i, op) in ops.iter().enumerate() {
+        group |= (op.op_code() as u64) << (Operation::OP_BITS * i);
+    }
+    Felt::new(group)
+}
+
+fn make_batch(num_groups: usize, op: Operation) -> OpBatch {
+    let ops: Vec<Operation> = (0..num_groups).map(|_| op).collect();
+    let mut indptr = [0usize; OP_BATCH_SIZE + 1];
+
+    for i in 0..num_groups {
+        indptr[i + 1] = i + 1;
+    }
+    for i in (num_groups + 1)..=OP_BATCH_SIZE {
+        indptr[i] = indptr[i - 1];
+    }
+
+    // Only the prefix [0..num_groups] is semantically valid; mark unused entries padded.
+    let mut padding = [false; OP_BATCH_SIZE];
+    for pad in padding.iter_mut().skip(num_groups) {
+        *pad = true;
+    }
+    let mut groups = [Felt::new(0); OP_BATCH_SIZE];
+    for group in groups.iter_mut().take(num_groups) {
+        *group = build_group(&[op]);
+    }
+
+    OpBatch::new_from_parts(ops, indptr, padding, groups, num_groups)
+}
+
+/// Test that UntrustedMastForest::validate rejects a non-full batch before the last batch.
+#[test]
+fn test_untrusted_forest_rejects_non_full_prefix_batch() {
+    let op_batches = vec![make_batch(4, Operation::Add), make_batch(2, Operation::Mul)];
+
+    let op_groups: Vec<Felt> =
+        op_batches.iter().flat_map(|batch| batch.groups()).copied().collect();
+    let digest = hasher::hash_elements(&op_groups);
+
+    let mut forest = MastForest::new();
+    let block_id = BasicBlockNodeBuilder::from_op_batches(op_batches, Vec::new(), digest)
+        .add_to_forest(&mut forest)
+        .unwrap();
+    forest.make_root(block_id);
+
+    let bytes = forest.to_bytes();
+    let untrusted = UntrustedMastForest::read_from_bytes(&bytes).unwrap();
+    let result = untrusted.validate();
+
+    assert_matches!(result, Err(MastForestError::InvalidBatchPadding(_, _)));
+}
+
+/// Test that UntrustedMastForest::validate accepts full prefix batches and a power-of-two last.
+#[test]
+fn test_untrusted_forest_accepts_full_prefix_batch() {
+    let op_batches = vec![make_batch(OP_BATCH_SIZE, Operation::Add), make_batch(4, Operation::Mul)];
+
+    let op_groups: Vec<Felt> =
+        op_batches.iter().flat_map(|batch| batch.groups()).copied().collect();
+    let digest = hasher::hash_elements(&op_groups);
+
+    let mut forest = MastForest::new();
+    let block_id = BasicBlockNodeBuilder::from_op_batches(op_batches, Vec::new(), digest)
+        .add_to_forest(&mut forest)
+        .unwrap();
+    forest.make_root(block_id);
+
+    let bytes = forest.to_bytes();
+    let untrusted = UntrustedMastForest::read_from_bytes(&bytes).unwrap();
+    let result = untrusted.validate();
+
+    assert!(result.is_ok(), "full prefix batches should validate");
+}
+
 /// Test that UntrustedMastForest::validate succeeds for forests with all node types.
 #[test]
 fn test_untrusted_forest_validates_all_node_types() {
```
