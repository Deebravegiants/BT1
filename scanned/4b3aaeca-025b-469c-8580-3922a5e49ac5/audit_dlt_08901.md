# [?] fix: panic in consensus task when process terminated

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-02-06
Source: https://github.com/software-mansion/pathfinder/commit/8cef4d3c3b1443154e5f6fac8d4e7da58dbcd6b2
Type: security-commit

## Details
fix: panic in consensus task when process terminated

## Patch
### crates/pathfinder/src/consensus/inner/p2p_task.rs
```diff
@@ -164,7 +164,13 @@ pub fn spawn(
                     }
                 }
                 from_consensus = rx_from_consensus.recv() => {
-                    from_consensus.expect("Receiver not to be dropped")
+                    match from_consensus {
+                        Some(command) => command,
+                        None => {
+                            tracing::warn!("Consensus command receiver was dropped, exiting P2P task");
+                            anyhow::bail!("Consensus command receiver was dropped, exiting P2P task");
+                        }
+                    }
                 }
                 from_sync = rx_from_sync.recv() => match from_sync {
                     Some(request) => P2PTaskEvent::SyncRequest(request),
```
