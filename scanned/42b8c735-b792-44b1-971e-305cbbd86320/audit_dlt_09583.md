# [?] Fix panic when writing staking events before pos starts.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-11-17
Source: https://github.com/Conflux-Chain/conflux-rust/commit/5c93f3ccb643224992757c15d3157e55f3951dc7
Type: security-commit

## Details
Fix panic when writing staking events before pos starts.

## Patch
### core/src/consensus/consensus_inner/consensus_executor.rs
```diff
@@ -1357,11 +1357,13 @@ impl ConsensusExecutionHandler {
                             block_traces.push(executed.trace.into());
                         }
 
-                        for log in &transaction_logs {
-                            if let Some(staking_event) =
-                                decode_register_info(log)
-                            {
-                                epoch_staking_events.push(staking_event);
+                        if self.pos_verifier.pos_option().is_some() {
+                            for log in &transaction_logs {
+                                if let Some(staking_event) =
+                                    decode_register_info(log)
+                                {
+                                    epoch_staking_events.push(staking_event);
+                                }
                             }
                         }
                     }
@@ -1419,18 +1421,20 @@ impl ConsensusExecutionHandler {
 
             epoch_receipts.push(block_receipts);
         }
-        self.pos_verifier
-            .consensus_db()
-            .put_staking_events(
-                pivot_block.block_header.height(),
-                pivot_block.hash(),
-                epoch_staking_events,
-            )
-            .map_err(|e| {
-                cfx_statedb::Error::from(DbErrorKind::PosDatabaseError(
-                    format!("{:?}", e),
-                ))
-            })?;
+        if self.pos_verifier.pos_option().is_some() {
+            self.pos_verifier
+                .consensus_db()
+                .put_staking_events(
+                    pivot_block.block_header.height(),
+                    pivot_block.hash(),
+                    epoch_staking_events,
+                )
+                .map_err(|e| {
+                    cfx_statedb::Error::from(DbErrorKind::PosDatabaseError(
+                        format!("{:?}", e),
+                    ))
+                })?;
+        }
 
         if on_local_pivot {
             self.tx_pool.recycle_transactions(to_pending);
```

### core/src/pos/pow_handler.rs
```diff
@@ -204,7 +204,14 @@ impl PowInterface for PowHandler {
                     block_hash: me_decision,
                 },
             )
-            .map_err(|e| e.into())
+            .or_else(|e| {
+                debug!("get_staking_events from pow: err={:?}", e);
+                Self::get_staking_events_impl(
+                    pow_consensus,
+                    parent_decision,
+                    me_decision,
+                )
+            })
     }
 
     async fn wait_for_initialization(&self, last_decision: H256) {
```
