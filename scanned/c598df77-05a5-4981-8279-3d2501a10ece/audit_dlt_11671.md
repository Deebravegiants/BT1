# [?] fix(core): Fix checkpoint Drop stack overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2024-11-18
Source: https://github.com/bitcoindevkit/bdk/commit/67e1dc37bff195d91f2959f3f4bf5d5d10da597c
Type: security-commit

## Details
fix(core): Fix checkpoint Drop stack overflow

Fixes #1634

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
+                    // Keep goign backwards
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
