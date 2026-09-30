# [?] fix(net): avoid itertools Format panic in tracing log (#23331)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-04-01
Source: https://github.com/paradigmxyz/reth/commit/357188f91817691d123d777a101df87820443623
Type: security-commit

## Details
fix(net): avoid itertools Format panic in tracing log (#23331)

## Patch
### crates/net/network/src/transactions/mod.rs
```diff
@@ -1,7 +1,6 @@
 //! Transactions management for the p2p network.
 
 use alloy_consensus::transaction::TxHashRef;
-use itertools::Itertools;
 use rayon::iter::{IntoParallelIterator, ParallelIterator};
 
 /// Aggregation on configurable parameters for [`TransactionsManager`].
@@ -785,7 +784,7 @@ impl<Pool: TransactionPool, N: NetworkPrimitives> TransactionsManager<Pool, N> {
         trace!(target: "net::tx::propagation",
             peer_id=format!("{peer_id:#}"),
             hashes_len=valid_announcement_data.len(),
-            hashes=%valid_announcement_data.keys().format(", "),
+            hashes=?valid_announcement_data.keys(),
             msg_version=%valid_announcement_data.msg_version(),
             client_version=%client,
             "received previously unseen and pending hashes in announcement from peer"
```
