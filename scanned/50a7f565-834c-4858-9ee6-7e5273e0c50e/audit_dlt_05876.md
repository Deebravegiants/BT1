# [?] fix(merkle_tree): don't panic in `BlockOutputWithProofs::verify_proofs` (#1717)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-04-18
Source: https://github.com/matter-labs/zksync-era/commit/a44fac97e0b121c93fde2d3fe15f494128cb3b16
Type: security-commit

## Details
fix(merkle_tree): don't panic in `BlockOutputWithProofs::verify_proofs` (#1717)

## What ❔

don't panic in `BlockOutputWithProofs::verify_proofs` and rather return
a `Result`

## Why ❔

So `BlockOutputWithProofs::verify_proofs` can be used by other
components.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.
- [ ] Spellcheck has been run via `zk spellcheck`.
- [ ] Linkcheck has been run via `zk linkcheck`.

Signed-off-by: Harald Hoyer <harald@matterlabs.dev>

## Patch
### Cargo.lock
```diff
@@ -8741,6 +8741,7 @@ dependencies = [
 name = "zksync_merkle_tree"
 version = "0.1.0"
 dependencies = [
+ "anyhow",
  "assert_matches",
  "clap 4.4.6",
  "insta",
```

### core/lib/merkle_tree/Cargo.toml
```diff
@@ -17,6 +17,7 @@ zksync_storage.workspace = true
 zksync_prover_interface.workspace = true
 zksync_utils.workspace = true
 
+anyhow.workspace = true
 leb128.workspace = true
 once_cell.workspace = true
 rayon.workspace = true
```

### core/lib/merkle_tree/src/hasher/proofs.rs
```diff
@@ -2,6 +2,8 @@
 
 use std::mem;
 
+use anyhow::ensure;
+
 use crate::{
     hasher::{HashTree, HasherWithStats},
     types::{
@@ -15,25 +17,30 @@ impl BlockOutputWithProofs {
     /// Verifies this output against the trusted old root hash of the tree and
     /// the applied instructions.
     ///
-    /// # Panics
+    /// # Errors
     ///
-    /// Panics if the proof doesn't verify.
+    /// As the errors are not actionable, a string error with the failing condition is returned.
     pub fn verify_proofs(
         &self,
         hasher: &dyn HashTree,
         old_root_hash: ValueHash,
         instructions: &[TreeInstruction],
-    ) {
-        assert_eq!(instructions.len(), self.logs.len());
+    ) -> anyhow::Result<()> {
+        ensure!(instructions.len() == self.logs.len());
 
         let mut root_hash = old_root_hash;
         for (op, &instruction) in self.logs.iter().zip(instructions) {
-            assert!(op.merkle_path.len() <= TREE_DEPTH);
+            ensure!(op.merkle_path.len() <= TREE_DEPTH);
             if matches!(instruction, TreeInstruction::Read(_)) {
-                assert_eq!(op.root_hash, root_hash);
-                assert!(op.base.is_read());
+                ensure!(
+                    op.root_hash == root_hash,
+                    "Condition failed: `op.root_hash == root_hash` ({:?} vs {:?})",
+                    op.root_hash,
+                    root_hash
+                );
+                ensure!(op.base.is_read());
             } else {
-                assert!(!op.base.is_read());
+                ensure!(!op.base.is_read());
             }
 
             let prev_entry = match op.base {
@@ -50,13 +57,24 @@ impl BlockOutputWithProofs {
             };
 
             let prev_hash = hasher.fold_merkle_path(&op.merkle_path, prev_entry);
-            assert_eq!(prev_hash, root_hash);
+            ensure!(
+                prev_hash == root_hash,
+                "Condition failed: `prev_hash == root_hash` ({:?} vs {:?})",
+                prev_hash,
+                root_hash
+            );
             if let TreeInstruction::Write(new_entry) = instruction {
                 let next_hash = hasher.fold_merkle_path(&op.merkle_path, new_entry);
-                assert_eq!(next_hash, op.root_hash);
+                ensure!(
+                    next_hash == op.root_hash,
+                    "Condition failed: `next_hash == op.root_hash` ({:?} vs {:?})",
+                    next_hash,
+                    op.root_hash
+                );
             }
             root_hash = op.root_hash;
         }
+        Ok(())
     }
 }
 
```

### core/lib/merkle_tree/tests/integration/merkle_tree.rs
```diff
@@ -55,7 +55,9 @@ fn output_proofs_are_computed_correctly_on_empty_tree(kv_count: u64) {
 
     assert_eq!(output.root_hash(), Some(expected_hash));
     assert_eq!(output.logs.len(), instructions.len());
-    output.verify_proofs(&Blake2Hasher, empty_tree_hash, &instructions);
+    output
+        .verify_proofs(&Blake2Hasher, empty_tree_hash, &instructions)
+        .unwrap();
     let root_hash = output.root_hash().unwrap();
 
     let reads = instructions
@@ -64,7 +66,9 @@ fn output_proofs_are_computed_correctly_on_empty_tree(kv_count: u64) {
     let mut reads: Vec<_> = reads.collect();
     reads.shuffle(&mut rng);
     let output = tree.extend_with_proofs(reads.clone());
-    output.verify_proofs(&Blake2Hasher, root_hash, &reads);
+    output
+        .verify_proofs(&Blake2Hasher, root_hash, &reads)
+        .unwrap();
     assert_eq!(output.root_hash(), Some(root_hash));
 }
 
@@ -138,7 +142,9 @@ fn proofs_are_computed_correctly_for_mixed_instructions() {
         .iter()
         .any(|op| matches!(op.base, TreeLogEntry::Read { .. })));
 
-    output.verify_proofs(&Blake2Hasher, old_root_hash, &instructions);
+    output
+        .verify_proofs(&Blake2Hasher, old_root_hash, &instructions)
+        .unwrap();
     assert_eq!(output.root_hash(), Some(expected_hash));
 }
 
@@ -163,7 +169,9 @@ fn proofs_are_computed_correctly_for_missing_keys() {
         .filter(|op| matches!(op.base, TreeLogEntry::ReadMissingKey));
     assert_eq!(read_misses.count(), 30);
     let empty_tree_hash = Blake2Hasher.empty_subtree_hash(256);
-    output.verify_proofs(&Blake2Hasher, empty_tree_hash, &instructions);
+    output
+        .verify_proofs(&Blake2Hasher, empty_tree_hash, &instructions)
+        .unwrap();
 }
 
 fn test_intermediate_commits(db: &mut impl Database, chunk_size: usize) {
@@ -196,7 +204,9 @@ fn output_proofs_are_computed_correctly_with_intermediate_commits(chunk_size: us
     for chunk in kvs.chunks(chunk_size) {
         let instructions = convert_to_writes(chunk);
         let output = tree.extend_with_proofs(instructions.clone());
-        output.verify_proofs(&Blake2Hasher, root_hash, &instructions);
+        output
+            .verify_proofs(&Blake2Hasher, root_hash, &instructions)
+            .unwrap();
         root_hash = output.root_hash().unwrap();
     }
     assert_eq!(root_hash, *expected_hash);
@@ -390,12 +400,16 @@ fn proofs_are_computed_correctly_with_key_updates(updated_keys: usize) {
     let mut tree = MerkleTree::new(PatchSet::default());
     let output = tree.extend_with_proofs(old_instructions.clone());
     let empty_tree_hash = Blake2Hasher.empty_subtree_hash(256);
-    output.verify_proofs(&Blake2Hasher, empty_tree_hash, &old_instructions);
+    output
+        .verify_proofs(&Blake2Hasher, empty_tree_hash, &old_instructions)
+        .unwrap();
 
     let root_hash = output.root_hash().unwrap();
     let output = tree.extend_with_proofs(instructions.clone());
     assert_eq!(output.root_hash(), Some(*expected_hash));
-    output.verify_proofs(&Blake2Hasher, root_hash, &instructions);
+    output
+        .verify_proofs(&Blake2Hasher, root_hash, &instructions)
+        .unwrap();
 
     let keys: Vec<_> = kvs.iter().map(|entry| entry.key).collect();
     let proofs = tree.entries_with_proofs(1, &keys).unwrap();
```

### core/lib/merkle_tree/tests/integration/recovery.rs
```diff
@@ -106,7 +106,9 @@ fn test_tree_after_recovery<DB: Database>(
         } else {
             let instructions = convert_to_writes(chunk);
             let output = tree.extend_with_proofs(instructions.clone());
-            output.verify_proofs(&Blake2Hasher, prev_root_hash, &instructions);
+            output
+                .verify_proofs(&Blake2Hasher, prev_root_hash, &instructions)
+                .unwrap();
             output.root_hash().unwrap()
         };
 
```
