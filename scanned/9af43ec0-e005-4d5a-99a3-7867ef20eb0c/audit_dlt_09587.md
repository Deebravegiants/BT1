# [?] Fix possible panic if mining starts before PoW catches up with PoS.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-09-08
Source: https://github.com/Conflux-Chain/conflux-rust/commit/0c64d3a534128d7c1e80406953fabfe2d1fe8d8c
Type: security-commit

## Details
Fix possible panic if mining starts before PoW catches up with PoS.

## Patch
### core/src/consensus/mod.rs
```diff
@@ -380,6 +380,23 @@ impl ConsensusGraph {
     )
     {
         let correct_parent_hash = {
+            if let Some(pos_ref) = &pos_reference {
+                loop {
+                    let inner = self.inner.read();
+                    let pivot_decision = inner
+                        .pos_verifier
+                        .get_pivot_decision(pos_ref)
+                        .expect("pos ref committed");
+                    if inner.pivot_block_processed(&pivot_decision) {
+                        // If this pos ref is processed in catching-up, its
+                        // pivot decision may have not been processed
+                        break;
+                    } else {
+                        warn!("Wait for PoW to catch up with PoS");
+                        sleep(Duration::from_secs(1));
+                    }
+                }
+            }
             // recompute `blame_info` needs locking `self.inner`, so we limit
             // the lock scope here.
             let mut inner = self.inner.write();
```
