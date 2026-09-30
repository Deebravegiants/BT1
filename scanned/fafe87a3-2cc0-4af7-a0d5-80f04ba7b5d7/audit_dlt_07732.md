# [?] fix(rpc): prevent panic in log subscription on broadcast lag (#23561)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-04-15
Source: https://github.com/paradigmxyz/reth/commit/6e4009eed404816b3d33c2869e2022189af17df7
Type: security-commit

## Details
fix(rpc): prevent panic in log subscription on broadcast lag (#23561)

## Patch
### crates/rpc/rpc/src/eth/pubsub.rs
```diff
@@ -447,10 +447,10 @@ where
 
     /// Returns a stream that yields all logs that match the given filter.
     fn log_stream(&self, filter: Filter) -> impl Stream<Item = Log> {
-        BroadcastStream::new(self.eth_api.provider().subscribe_to_canonical_state())
-            .map(move |canon_state| {
-                canon_state.expect("new block subscription never ends").block_receipts()
-            })
+        self.eth_api
+            .provider()
+            .canonical_state_stream()
+            .map(move |canon_state| canon_state.block_receipts())
             .flat_map(futures::stream::iter)
             .flat_map(move |(block_receipts, removed)| {
                 let all_logs = logs_utils::matching_block_logs_with_tx_hashes(
```
