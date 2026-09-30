# [?] Fix node panics from malformed P2P and contract inputs

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-24
Source: https://github.com/Conflux-Chain/conflux-rust/commit/9607fd0bcf7544b79195e10b05043b1b70010980
Type: security-commit

## Details
Fix node panics from malformed P2P and contract inputs

## Patch
### crates/cfxcore/core/src/sync/message/get_block_txn.rs
```diff
@@ -75,24 +75,24 @@ impl Handleable for GetBlockTxn {
         match ctx.manager.graph.block_by_hash(&self.block_hash) {
             Some(block) => {
                 debug!("Process get_blocktxn hash={:?}", block.hash());
-                let mut tx_resp = Vec::with_capacity(self.index_skips.len());
-                let mut last = 0;
-                for index_skip in self.index_skips.iter() {
-                    last += *index_skip;
-                    if last >= block.transactions.len() {
+                let mut transactions = block.transactions.iter();
+                let tx_resp = self
+                    .index_skips
+                    .iter()
+                    .map(|index_skip| {
+                        transactions
+                            .nth(*index_skip)
+                            .map(|tx| tx.transaction.clone())
+                    })
+                    .collect::<Option<Vec<_>>>()
+                    .ok_or_else(|| {
                         warn!(
                             "Request tx index out of bound, peer={}, hash={}",
                             ctx.node_id,
                             block.hash()
                         );
-                        return Err(Error::InvalidGetBlockTxn(
-                            "index out-of-bound".into(),
-                        )
-                        .into());
-                    }
-                    tx_resp.push(block.transactions[last].transaction.clone());
-                    last += 1;
-                }
+                        Error::InvalidGetBlockTxn("index out-of-bound".into())
+                    })?;
                 let response = GetBlockTxnResponse {
                     request_id: self.request_id,
                     block_hash: self.block_hash,
```

### crates/cfxcore/core/src/sync/message/get_block_txn_response.rs
```diff
@@ -53,25 +53,23 @@ impl Handleable for GetBlockTxnResponse {
             ctx.manager.graph.block_header_by_hash(&resp_hash)
         {
             debug!("Process blocktxn hash={:?}", resp_hash);
+
             let signed_txns = ctx
                 .manager
                 .graph
                 .data_man
                 .recover_unsigned_tx_with_order(&self.block_txn)?;
             match ctx.manager.graph.data_man.compact_block_by_hash(&resp_hash) {
                 Some(cmpct) => {
-                    let mut trans =
-                        Vec::with_capacity(cmpct.reconstructed_txns.len());
-                    let mut index = 0;
-                    for tx in cmpct.reconstructed_txns {
-                        match tx {
-                            Some(tx) => trans.push(tx),
-                            None => {
-                                trans.push(signed_txns[index].clone());
-                                index += 1;
-                            }
-                        }
-                    }
+                    // FIXME: Invalid blocktxn responses after match_request
+                    // must still clean up block inflight
+                    // state and resend the request. Otherwise the
+                    // corresponding request will never be satisfied.
+                    let trans = fill_missing_slots(
+                        cmpct.reconstructed_txns,
+                        &signed_txns,
+                    )
+                    .ok_or(Error::UnexpectedResponse)?;
                     // FIXME Should check if hash matches
                     let block = Block::new(header, trans);
                     debug!(
@@ -145,3 +143,50 @@ impl Handleable for GetBlockTxnResponse {
         Ok(())
     }
 }
+
+/// Fill missing slots with candidates in order.
+///
+/// `items` contains already-known values as `Some` and holes as `None`.
+/// `candidates` must match those holes exactly: too few candidates would leave
+/// missing values unresolved, while too many candidates means the response does
+/// not match the requested layout. Returns `None` for either mismatch.
+fn fill_missing_slots<'a, T: Clone>(
+    items: Vec<Option<T>>, candidates: &[T],
+) -> Option<Vec<T>> {
+    let mut candidates_iter = candidates.iter();
+    let result: Vec<T> = items
+        .into_iter()
+        .map(|slot| slot.or_else(|| candidates_iter.next().cloned()))
+        // Any single None that can't be filled fails the entire reconstruction.
+        .collect::<Option<Vec<T>>>()?;
+
+    // Extra candidates means the response doesn't match the compact layout.
+    if candidates_iter.next().is_some() {
+        return None;
+    }
+
+    Some(result)
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[test]
+    fn reject_too_few_candidates() {
+        assert!(fill_missing_slots(vec![None::<u8>], &[]).is_none());
+    }
+
+    #[test]
+    fn reject_too_many_candidates() {
+        assert!(fill_missing_slots(vec![Some(1u8)], &[2]).is_none());
+    }
+
+    #[test]
+    fn fill_missing_slots_in_order() {
+        assert_eq!(
+            fill_missing_slots(vec![Some(1u8), None, Some(3)], &[2]).unwrap(),
+            vec![1, 2, 3],
+        );
+    }
+}
```

### crates/cfxcore/core/src/sync/message/transactions.rs
```diff
@@ -622,7 +622,7 @@ impl Handleable for GetTransactionsResponse {
                         self.tx_hashes,
                         req.window_index,
                         &req.tx_hashes_indices,
-                    );
+                    )?;
             }
             Ok(())
         } else {
```

### crates/cfxcore/core/src/sync/request_manager/mod.rs
```diff
@@ -458,11 +458,15 @@ impl RequestManager {
         &self, io: &dyn NetworkContext, peer_id: NodeId,
         responded_tx_hashes: Vec<H256>, window_index: usize,
         tx_hashes_indices: &Vec<usize>,
-    ) {
+    ) -> Result<(), Error> {
         let _timer = MeterTimer::time_func(REQUEST_MANAGER_TX_TIMER.as_ref());
 
         if responded_tx_hashes.is_empty() {
-            return;
+            return Ok(());
+        }
+
+        if responded_tx_hashes.len() > tx_hashes_indices.len() {
+            return Err(Error::UnexpectedResponse.into());
         }
 
         let mut tx_from_hashes_inflight_keys = self
@@ -511,7 +515,7 @@ impl RequestManager {
         };
 
         if request.is_empty() {
-            return;
+            return Ok(());
         }
 
         if self
@@ -523,6 +527,8 @@ impl RequestManager {
                 tx_from_hashes_inflight_keys.remove(&Key::Hash(id));
             }
         }
+
+        Ok(())
     }
 
     pub fn request_compact_blocks(
```

### crates/execution/executor/src/executive/tests.rs
```diff
@@ -621,6 +621,24 @@ fn test_deposit_withdraw_lock() {
     );
     assert_eq!(state.total_staking_tokens(), U256::zero());
 
+    // getVotePower with a near-u64::MAX block number used to panic when
+    // adding the quarter/year offsets.
+    params.call_type = CallType::Call;
+    let mut get_vote_power_data = vec![0xc9, 0x0a, 0xba, 0xc8];
+    get_vote_power_data.extend_from_slice(&[0u8; 12]);
+    get_vote_power_data.extend_from_slice(sender.as_bytes());
+    get_vote_power_data.extend_from_slice(&U256::MAX.to_big_endian());
+    params.data = Some(get_vote_power_data);
+    let mut tracer = ();
+    let result = ExecutiveContext::new(&mut state, &env, &machine, &spec)
+        .call_for_test(params.clone(), &mut substate, &mut tracer)
+        .expect("no db error");
+    assert!(result.is_err());
+    assert_eq!(
+        result.unwrap_err(),
+        vm::Error::InternalContract("block number overflow".into())
+    );
+
     // deposit 10^18 - 1, not enough
     params.call_type = CallType::Call;
     params.data = Some("b6b55f250000000000000000000000000000000000000000000000000de0b6b3a763ffff".from_hex().unwrap());
```

### crates/execution/executor/src/internal_contract/components/storage_layout.rs
```diff
@@ -25,10 +25,19 @@ pub fn dynamic_slot(base: U256) -> U256 {
 // General function for solidity storage rule
 pub fn array_slot(base: U256, index: usize, element_size: usize) -> U256 {
     // Solidity will apply an overflowing add here.
-    // However, if this function is used correctly, the overflowing will
-    // happen with a negligible exception, so we let it panic when
-    // overflowing happen.
-    base + index * element_size
+    let (offset, _) =
+        U256::from(index).overflowing_mul(U256::from(element_size));
+    base.overflowing_add(offset).0
 }
 
 pub fn u256_to_array(input: U256) -> [u8; 32] { input.to_big_endian() }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[test]
+    fn array_slot_wraps_like_solidity() {
+        assert_eq!(array_slot(U256::MAX, 1, 1), U256::zero());
+    }
+}
```

### crates/execution/executor/src/internal_contract/impls/staking.rs
```diff
@@ -108,18 +108,28 @@ pub fn get_vote_power(
         block_number = current_block_number;
     }
 
-    let three_months_locked = state.locked_staking_balance_at_block_number(
-        &address,
-        block_number + MINED_BLOCK_COUNT_PER_QUARTER,
-    )?;
-    let six_months_locked = state.locked_staking_balance_at_block_number(
-        &address,
-        block_number + 2 * MINED_BLOCK_COUNT_PER_QUARTER,
-    )?;
-    let one_year_locked = state.locked_staking_balance_at_block_number(
-        &address,
-        block_number + 4 * MINED_BLOCK_COUNT_PER_QUARTER,
-    )?;
+    let three_months_block = block_number
+        .checked_add(MINED_BLOCK_COUNT_PER_QUARTER)
+        .ok_or_else(|| {
+            vm::Error::InternalContract("block number overflow".into())
+        })?;
+    let six_months_block = block_number
+        .checked_add(2 * MINED_BLOCK_COUNT_PER_QUARTER)
+        .ok_or_else(|| {
+            vm::Error::InternalContract("block number overflow".into())
+        })?;
+    let one_year_block = block_number
+        .checked_add(4 * MINED_BLOCK_COUNT_PER_QUARTER)
+        .ok_or_else(|| {
+            vm::Error::InternalContract("block number overflow".into())
+        })?;
+
+    let three_months_locked = state
+        .locked_staking_balance_at_block_number(&address, three_months_block)?;
+    let six_months_locked = state
+        .locked_staking_balance_at_block_number(&address, six_months_block)?;
+    let one_year_locked = state
+        .locked_staking_balance_at_block_number(&address, one_year_block)?;
 
     // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━
     //              Remaining Committed Staking Time             ┃  Voting Power
```
