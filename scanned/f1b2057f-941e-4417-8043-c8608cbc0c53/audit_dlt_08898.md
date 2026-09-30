# [?] fix(p2p_task): panic on decided block missing

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-02-25
Source: https://github.com/software-mansion/pathfinder/commit/161dee4ff8dd7453f2472616044253b42ce2576e
Type: security-commit

## Details
fix(p2p_task): panic on decided block missing

## Patch
### crates/pathfinder/src/consensus/inner/p2p_task.rs
```diff
@@ -510,11 +510,17 @@ pub fn spawn(
                         );
                         let stopwatch = std::time::Instant::now();
 
-                        let block = finalized_blocks
-                            .remove(&height_and_round)
-                            .expect("This block is not removed from the map anywhere else");
-                        decided_blocks
-                            .insert(height_and_round.height(), (height_and_round.round(), block));
+                        // `None` is possible here if the node has been respawned when precommit for
+                        // this height has already been agreed by the quorum. We loose the finalized
+                        // block for the height, but the consensus engine should still be able to
+                        // decide on the block (thanks to WAL) and move on to the next height. The
+                        // actual missing block will be fetched by the sync task from the FGw.
+                        if let Some(block) = finalized_blocks.remove(&height_and_round) {
+                            decided_blocks.insert(
+                                height_and_round.height(),
+                                (height_and_round.round(), block),
+                            );
+                        }
 
                         tracing::info!(
                             "🖧  💾 {validator_address} Finalized and prepared block for \
```
