# [?] Merge bitcoindevkit/bdk#1731: fix(core): Fix checkpoint Drop stack overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2024-11-21
Source: https://github.com/bitcoindevkit/bdk/commit/d8c8afe10f3eedf39ee7fa76217acff8c14519fe
Type: security-commit

## Details
Merge bitcoindevkit/bdk#1731: fix(core): Fix checkpoint Drop stack overflow

2df5861c5e1bf308f1b215b19e00d882aee07e87 test(core): test `Drop` implementation of `CPInner` (valued mammal)
67e1dc37bff195d91f2959f3f4bf5d5d10da597c fix(core): Fix checkpoint Drop stack overflow (LLFourn)

Pull request description:

  Fixes #1634

  This needs a test that demonstrates the issue is fixed. I was hoping @ValuedMammal could do that for me.

ACKs for top commit:
  ValuedMammal:
    self-ACK 2df5861c5e1bf308f1b215b19e00d882aee07e87
  notmandatory:
    ACK 2df5861c5e1bf308f1b215b19e00d882aee07e87

Tree-SHA512: a431cb93505cbde2a9287de09d5faac003b8dfa01342cd22c6ca197d70a73948f94f55dfa365cc06b5be36f78458ed34d4ef5fa8c9e5e2989a21c7ce5b55d9ca

## Patch
### crates/core/src/checkpoint.rs
```diff
@@ -21,6 +21,34 @@ struct CPInner {
     prev: Option<Arc<CPInner>>,
 }
 
+/// When a `CPInner` is dropped we need to go back down the chain and manually remove any
+/// no-longer referenced checkpoints. Letting the default rust dropping mechanism handle this
+/// leads to recursive logic and stack overflows
+///
+/// https://github.com/bitcoindevkit/bdk/issues/1634
+impl Drop for CPInner {
+    fn drop(&mut self) {
+        // Take out `prev` so its `drop` won't be called when this drop is finished
+        let mut current = self.prev.take();
+        while let Some(arc_node) = current {
+            // Get rid of the Arc around `prev` if we're the only one holding a ref
+            // So the `drop` on it won't be called when the `Arc` is dropped.
+            //
+            // FIXME: When MSRV > 1.70.0 this should use Arc::into_inner which actually guarantees
+            // that no recursive drop calls can happen even with multiple threads.
+            match Arc::try_unwrap(arc_node).ok() {
+                Some(mut node) => {
+                    // Keep going backwards
+                    current = node.prev.take();
+                    // Don't call `drop` on `CPInner` since that risks it becoming recursive.
+                    core::mem::forget(node);
+                }
+                None => break,
+            }
+        }
+    }
+}
+
 impl PartialEq for CheckPoint {
     fn eq(&self, other: &Self) -> bool {
         let self_cps = self.iter().map(|cp| cp.block_id());
```

### crates/core/tests/test_checkpoint.rs
```diff
@@ -1,5 +1,5 @@
-use bdk_core::CheckPoint;
-use bdk_testenv::block_id;
+use bdk_core::{BlockId, CheckPoint};
+use bdk_testenv::{block_id, hash};
 
 /// Inserting a block that already exists in the checkpoint chain must always succeed.
 #[test]
@@ -32,3 +32,22 @@ fn checkpoint_insert_existing() {
         }
     }
 }
+
+#[test]
+fn checkpoint_destruction_is_sound() {
+    // Prior to the fix in https://github.com/bitcoindevkit/bdk/pull/1731
+    // this could have caused a stack overflow due to drop recursion in Arc.
+    // We test that a long linked list can clean itself up without blowing
+    // out the stack.
+    let mut cp = CheckPoint::new(BlockId {
+        height: 0,
+        hash: hash!("g"),
+    });
+    let end = 10_000;
+    for height in 1u32..end {
+        let hash = bitcoin::hashes::Hash::hash(height.to_be_bytes().as_slice());
+        let block = BlockId { height, hash };
+        cp = cp.push(block).unwrap();
+    }
+    assert_eq!(cp.iter().count() as u32, end);
+}
```
