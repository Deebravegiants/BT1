# [?] fix(sync/pending): circumvent race condition between fetching pre-latest and pre-confirmed

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-05-24
Source: https://github.com/software-mansion/pathfinder/commit/39eb9d11933c941eb974838d1b046f169fa0b5b2
Type: security-commit

## Details
fix(sync/pending): circumvent race condition between fetching pre-latest and pre-confirmed

## Patch
### crates/pathfinder/src/state/sync/pending.rs
```diff
@@ -159,18 +159,9 @@ pub(super) async fn poll_pre_confirmed<S: GatewayApi + Clone + Send + 'static>(
             continue;
         }
 
-        // Fetch pre-latest and pre-confirmed.
-        let pre_latest_data = match fetch_pre_latest(&sequencer, latest_number, latest_hash).await {
-            Ok(r) => r.map(Box::new),
-            Err(e) => {
-                tracing::debug!(%e, "Failed to fetch pre-latest block");
-                if wait_for_next_poll(t_fetch + poll_interval, &cache).await {
-                    last_active = Instant::now();
-                }
-                continue;
-            }
-        };
-
+        // Pre-confirmed comes first; its height anchors pre-latest below.
+        // The chain can advance between the two HTTP calls, so pre-latest is
+        // only kept if it chains to the pre-confirmed we just received.
         let response = match sequencer
             .preconfirmed_block(
                 BlockId::Latest,
@@ -224,6 +215,30 @@ pub(super) async fn poll_pre_confirmed<S: GatewayApi + Clone + Send + 'static>(
             }
         }
 
+        // Pre-latest. Kept only when it chains to the pre-confirmed above —
+        // a mismatch means the chain advanced between the two fetches, in
+        // which case publishing pre-confirmed alone is the safe move.
+        let pre_latest_data = match fetch_pre_latest(&sequencer, latest_number, latest_hash).await {
+            Ok(Some(pre_latest)) => {
+                let pre_latest_number = pre_latest.0;
+                if pre_latest_number + 1 == state.block_number {
+                    Some(Box::new(pre_latest))
+                } else {
+                    tracing::debug!(
+                        pre_latest = %pre_latest_number,
+                        pre_confirmed = %state.block_number,
+                        "Pre-latest doesn't chain to pre-confirmed; dropping (chain raced)"
+                    );
+                    None
+                }
+            }
+            Ok(None) => None,
+            Err(e) => {
+                tracing::debug!(%e, "Failed to fetch pre-latest block");
+                None
+            }
+        };
+
         // Publish. Each branch is responsible for signalling cache freshness:
         //   - changed: the emitted event leads to a `cache.store(...)` call, which
         //     bumps freshness as a side effect.
```
