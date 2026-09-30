# [?] move double spend checking and fix tests

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2023-06-01
Source: https://github.com/nervosnetwork/ckb/commit/d1f56a110a8a906a3d90369f71fa345f8b6d6a1d
Type: security-commit

## Details
move double spend checking and fix tests

## Patch
### Cargo.lock
```diff
@@ -1423,9 +1423,9 @@ dependencies = [
  "ckb-types",
  "ckb-util",
  "ckb-verification",
+ "ckb_multi_index_map",
  "hyper",
  "lru",
- "multi_index_map",
  "rand 0.8.5",
  "rustc-hash",
  "sentry",
@@ -1553,6 +1553,21 @@ dependencies = [
  "paste",
 ]
 
+[[package]]
+name = "ckb_multi_index_map"
+version = "0.0.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "2adba00c3dcb84fc4634c948cf3d24c05ce3193810bfa568effe13ad814f662a"
+dependencies = [
+ "convert_case 0.6.0",
+ "proc-macro-error",
+ "proc-macro2",
+ "quote",
+ "rustc-hash",
+ "slab",
+ "syn",
+]
+
 [[package]]
 name = "clang-sys"
 version = "1.3.1"
@@ -3128,21 +3143,6 @@ dependencies = [
  "faster-hex",
 ]
 
-[[package]]
-name = "multi_index_map"
-version = "0.5.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "7a58eea8dbf91e7420e0e843535f585491046d6017e669d36cb8342cfa4861e2"
-dependencies = [
- "convert_case 0.6.0",
- "proc-macro-error",
- "proc-macro2",
- "quote",
- "rustc-hash",
- "slab",
- "syn",
-]
-
 [[package]]
 name = "native-tls"
 version = "0.2.11"
```

### chain/src/chain.rs
```diff
@@ -560,7 +560,6 @@ impl ChainService {
             self.proposal_table
                 .insert(blk.header().number(), blk.union_proposal_ids());
         }
-
         self.reload_proposal_table(fork);
     }
 
```

### chain/src/tests/dep_cell.rs
```diff
@@ -436,7 +436,6 @@ fn test_package_txs_with_deps2() {
             .internal_process_block(Arc::new(block), Switch::DISABLE_ALL)
             .unwrap();
     }
-
     // skip gap
     {
         while Into::<u64>::into(block_template.number) != 2 {
@@ -461,7 +460,7 @@ fn test_package_txs_with_deps2() {
 
     let mut tx_pool_info = tx_pool.get_tx_pool_info().unwrap();
     while tx_pool_info.proposed_size != txs.len() {
-        tx_pool_info = tx_pool.get_tx_pool_info().unwrap()
+        tx_pool_info = tx_pool.get_tx_pool_info().unwrap();
     }
 
     // get block template with txs
@@ -534,11 +533,11 @@ fn test_package_txs_with_deps_priority() {
         Capacity::shannons(10000),
     );
 
-    let txs = vec![tx2.clone(), tx1];
-    for tx in &txs {
-        let ret = tx_pool.submit_local_tx(tx.clone()).unwrap();
-        assert!(ret.is_ok(), "submit {} {:?}", tx.proposal_short_id(), ret);
-    }
+    let ret = tx_pool.submit_local_tx(tx2.clone()).unwrap();
+    assert!(ret.is_ok(), "submit {} {:?}", tx2.proposal_short_id(), ret);
+
+    let ret = tx_pool.submit_local_tx(tx1.clone()).unwrap();
+    assert!(ret.is_err(), "submit {} {:?}", tx1.proposal_short_id(), ret);
 
     let mut block_template = shared
         .get_block_template(None, None, None)
@@ -548,7 +547,7 @@ fn test_package_txs_with_deps_priority() {
     // proposal txs
     {
         while !(Into::<u64>::into(block_template.number) == 1
-            && block_template.proposals.len() == 2)
+            && block_template.proposals.len() == 1)
         {
             block_template = shared
                 .get_block_template(None, None, None)
```

### rpc/src/tests/module/pool.rs
```diff
@@ -172,7 +172,7 @@ fn test_send_transaction_exceeded_maximum_ancestors_count() {
         parent_tx_hash = tx.hash();
     }
 
-    suite.wait_block_template_array_ge("proposals", 130);
+    suite.wait_block_template_array_ge("proposals", 125);
 
     // 130 txs will be added to proposal list
     while store.get_tip_header().unwrap().number() != (tip.number() + 2) {
```

### test/src/main.rs
```diff
@@ -388,12 +388,6 @@ fn canonicalize_path<P: AsRef<Path>>(path: P) -> PathBuf {
         .unwrap_or_else(|_| path.as_ref().to_path_buf())
 }
 
-fn _all_specs() -> Vec<Box<dyn Spec>> {
-    // This case is not stable right now
-    //vec![Box::new(PoolResolveConflictAfterReorg)]
-    vec![Box::new(RemoveConflictFromPending)]
-}
-
 fn all_specs() -> Vec<Box<dyn Spec>> {
     let mut specs: Vec<Box<dyn Spec>> = vec![
         Box::new(BlockSyncFromOne),
@@ -436,8 +430,6 @@ fn all_specs() -> Vec<Box<dyn Spec>> {
         Box::new(GetRawTxPool),
         Box::new(PoolReconcile),
         Box::new(PoolResurrect),
-        //TODO: (yukang)
-        //Box::new(PoolResolveConflictAfterReorg),
         Box::new(InvalidHeaderDep),
         #[cfg(not(target_os = "windows"))]
         Box::new(PoolPersisted),
```

### test/src/node.rs
```diff
@@ -5,6 +5,7 @@ use crate::{SYSTEM_CELL_ALWAYS_FAILURE_INDEX, SYSTEM_CELL_ALWAYS_SUCCESS_INDEX};
 use ckb_app_config::CKBAppConfig;
 use ckb_chain_spec::consensus::Consensus;
 use ckb_chain_spec::ChainSpec;
+use ckb_error::AnyError;
 use ckb_jsonrpc_types::TxStatus;
 use ckb_jsonrpc_types::{BlockFilter, BlockTemplate, TxPoolInfo};
 use ckb_logger::{debug, error};
@@ -357,6 +358,17 @@ impl Node {
             .send_transaction(transaction.data().into())
     }
 
+    pub fn submit_transaction_with_result(
+        &self,
+        transaction: &TransactionView,
+    ) -> Result<Byte32, AnyError> {
+        let res = self
+            .rpc_client()
+            .send_transaction_result(transaction.data().into())?
+            .pack();
+        Ok(res)
+    }
+
     pub fn get_transaction(&self, tx_hash: Byte32) -> TxStatus {
         self.rpc_client().get_transaction(tx_hash).tx_status
     }
```

### test/src/specs/relay/transaction_relay.rs
```diff
@@ -5,7 +5,6 @@ use crate::util::transaction::{always_success_transaction, always_success_transa
 use crate::utils::{build_relay_tx_hashes, build_relay_txs, sleep, wait_until};
 use crate::{Net, Node, Spec};
 use ckb_constant::sync::RETRY_ASK_TX_TIMEOUT_INCREASE;
-use ckb_jsonrpc_types::Status;
 use ckb_logger::info;
 use ckb_network::SupportProtocols;
 use ckb_types::{
@@ -234,10 +233,15 @@ impl Spec for TransactionRelayConflict {
             .build();
         node0.rpc_client().send_transaction(tx1.data().into());
         sleep(6);
-        node0.rpc_client().send_transaction(tx2.data().into());
+
+        let res = node0
+            .rpc_client()
+            .send_transaction_result(tx2.data().into());
+        assert!(res.is_err());
+        eprintln!("res: {:?}", res);
 
         let relayed = wait_until(20, || {
-            [tx1.hash(), tx2.hash()].iter().all(|hash| {
+            [tx1.hash()].iter().all(|hash| {
                 node1
                     .rpc_client()
                     .get_transaction(hash.clone())
@@ -247,13 +251,14 @@ impl Spec for TransactionRelayConflict {
         });
         assert!(relayed, "all transactions should be relayed");
 
-        let proposed = node1.mine_with_blocking(|template| template.proposals.len() != 3);
+        let proposed = node1.mine_with_blocking(|template| template.proposals.len() != 2);
         node1.mine_with_blocking(|template| template.number.value() != (proposed + 1));
 
         waiting_for_sync(nodes);
         node0.wait_for_tx_pool();
         node1.wait_for_tx_pool();
 
+        /*
         let ret = node1
             .rpc_client()
             .get_transaction_with_verbosity(tx2.hash(), 1);
@@ -289,5 +294,6 @@ impl Spec for TransactionRelayConflict {
                 .is_some()
         });
         assert!(relayed, "Transaction should be relayed to node1");
+        */
     }
 }
```

### test/src/specs/tx_pool/collision.rs
```diff
@@ -1,6 +1,4 @@
-use crate::util::check::{
-    is_transaction_committed, is_transaction_pending, is_transaction_rejected,
-};
+use crate::util::check::{is_transaction_committed, is_transaction_pending};
 use crate::utils::{assert_send_transaction_fail, blank, commit, propose};
 use crate::{Node, Spec};
 use ckb_types::bytes::Bytes;
@@ -67,7 +65,8 @@ impl Spec for ConflictInPending {
 
         let (txa, txb) = conflict_transactions(node);
         node.submit_transaction(&txa);
-        node.submit_transaction(&txb);
+        let res = node.submit_transaction_with_result(&txb);
+        assert!(res.is_err());
 
         node.submit_block(&propose(node, &[&txa]));
         (0..window.closest()).for_each(|_| {
@@ -89,13 +88,15 @@ impl Spec for ConflictInGap {
 
         let (txa, txb) = conflict_transactions(node);
         node.submit_transaction(&txa);
-        node.submit_transaction(&txb);
+        let res = node.submit_transaction_with_result(&txb);
+        assert!(res.is_err());
 
         node.submit_block(&propose(node, &[&txa]));
         (0..window.closest() - 1).for_each(|_| {
             node.submit_block(&blank(node));
         });
-        node.submit_block(&propose(node, &[&txb]));
+
+        //node.submit_block(&propose(node, &[&txb]));
         let block = node.new_block(None, None, None);
         assert_eq!(&[txa], &block.transactions()[1..]);
 
@@ -114,7 +115,8 @@ impl Spec for ConflictInProposed {
 
         let (txa, txb) = conflict_transactions(node);
         node.submit_transaction(&txa);
-        node.submit_transaction(&txb);
+        let res = node.submit_transaction_with_result(&txb);
+        assert!(res.is_err());
 
         node.submit_block(&propose(node, &[&txa, &txb]));
         node.mine(window.farthest());
@@ -153,12 +155,13 @@ impl Spec for RemoveConflictFromPending {
             conflict_transactions_with_capacity(node, Bytes::new(), capacity_bytes!(1000));
         let txc = node.new_transaction_with_since_capacity(txb.hash(), 0, capacity_bytes!(100));
         node.submit_transaction(&txa);
-        node.submit_transaction(&txb);
-        node.submit_transaction(&txc);
+        let res = node.submit_transaction_with_result(&txb);
+        assert!(res.is_err());
+
+        let res = node.submit_transaction_with_result(&txc);
+        assert!(res.is_err());
 
         assert!(is_transaction_pending(node, &txa));
-        assert!(is_transaction_pending(node, &txb));
-        assert!(is_transaction_pending(node, &txc));
 
         node.submit_block(&propose(node, &[&txa]));
         (0..window.closest()).for_each(|_| {
@@ -168,8 +171,6 @@ impl Spec for RemoveConflictFromPending {
         node.wait_for_tx_pool();
 
         assert!(is_transaction_committed(node, &txa));
-        assert!(is_transaction_rejected(node, &txb));
-        assert!(is_transaction_rejected(node, &txc));
     }
 }
 
```

### test/src/specs/tx_pool/different_txs_with_same_input.rs
```diff
@@ -28,10 +28,14 @@ impl Spec for DifferentTxsWithSameInput {
             .as_advanced_builder()
             .set_outputs(vec![output])
             .build();
+
         node0.rpc_client().send_transaction(tx1.data().into());
-        node0.rpc_client().send_transaction(tx2.data().into());
+        let res = node0
+            .rpc_client()
+            .send_transaction_result(tx2.data().into());
+        assert!(res.is_err(), "tx2 should be rejected");
 
-        node0.mine_with_blocking(|template| template.proposals.len() != 3);
+        node0.mine_with_blocking(|template| template.proposals.len() != 2);
         node0.mine_with_blocking(|template| template.number.value() != 14);
         node0.mine_with_blocking(|template| template.transactions.len() != 2);
 
@@ -47,11 +51,11 @@ impl Spec for DifferentTxsWithSameInput {
         assert!(!commit_txs_hash.contains(&tx2.hash()));
 
         // when tx1 was confirmed, tx2 should be rejected
-        let ret = node0.rpc_client().get_transaction(tx2.hash());
-        assert!(
-            matches!(ret.tx_status.status, Status::Rejected),
-            "tx2 should be rejected"
-        );
+        // let ret = node0.rpc_client().get_transaction(tx2.hash());
+        // assert!(
+        //     matches!(ret.tx_status.status, Status::Rejected),
+        //     "tx2 should be rejected"
+        // );
 
         // verbosity = 1
         let ret = node0
@@ -60,11 +64,11 @@ impl Spec for DifferentTxsWithSameInput {
         assert!(ret.transaction.is_none());
         assert!(matches!(ret.tx_status.status, Status::Committed));
 
-        let ret = node0
-            .rpc_client()
-            .get_transaction_with_verbosity(tx2.hash(), 1);
-        assert!(ret.transaction.is_none());
-        assert!(matches!(ret.tx_status.status, Status::Rejected));
+        // let ret = node0
+        //     .rpc_client()
+        //     .get_transaction_with_verbosity(tx2.hash(), 1);
+        // assert!(ret.transaction.is_none());
+        // assert!(matches!(ret.tx_status.status, Status::Rejected));
 
         // verbosity = 2
         let ret = node0
@@ -73,10 +77,10 @@ impl Spec for DifferentTxsWithSameInput {
         assert!(ret.transaction.is_some());
         assert!(matches!(ret.tx_status.status, Status::Committed));
 
-        let ret = node0
-            .rpc_client()
-            .get_transaction_with_verbosity(tx2.hash(), 2);
-        assert!(ret.transaction.is_none());
-        assert!(matches!(ret.tx_status.status, Status::Rejected));
+        // let ret = node0
+        //     .rpc_client()
+        //     .get_transaction_with_verbosity(tx2.hash(), 2);
+        // assert!(ret.transaction.is_none());
+        // assert!(matches!(ret.tx_status.status, Status::Rejected));
     }
 }
```

### test/src/specs/tx_pool/send_tx_chain.rs
```diff
@@ -33,10 +33,15 @@ impl Spec for SendTxChain {
         assert_eq!(txs.len(), MAX_ANCESTORS_COUNT + 1);
         // send tx chain
         info!("submit fresh txs chain to node0");
-        for tx in txs[..=MAX_ANCESTORS_COUNT].iter() {
+        for tx in txs[..=MAX_ANCESTORS_COUNT - 1].iter() {
             let ret = node0.rpc_client().send_transaction_result(tx.data().into());
             assert!(ret.is_ok());
         }
+        // The last one will be rejected
+        let ret = node0
+            .rpc_client()
+            .send_transaction_result(txs[MAX_ANCESTORS_COUNT].data().into());
+        assert!(ret.is_err());
 
         node0.mine(3);
 
@@ -76,6 +81,11 @@ impl Spec for SendTxChain {
             .rpc_client()
             .send_transaction_result(txs.last().unwrap().data().into());
         assert!(ret.is_err());
+        assert!(ret
+            .err()
+            .unwrap()
+            .to_string()
+            .contains("Transaction exceeded maximum ancestors count limit"));
     }
 
     fn modify_app_config(&self, config: &mut ckb_app_config::CKBAppConfig) {
```

### tx-pool/Cargo.toml
```diff
@@ -36,8 +36,7 @@ sentry = { version = "0.26.0", optional = true }
 serde_json = "1.0"
 rand = "0.8.4"
 hyper = { version = "0.14", features = ["http1", "client", "tcp"] }
-#multi_index_map = { git = "https://github.com/wyjin/multi_index_map.git", branch = "master" }
-multi_index_map = "0.5.0"
+ckb_multi_index_map = "0.0.1" # ckb team fork crate
 slab = "0.4"
 rustc-hash = "1.1"
 tokio-util = "0.7.8"
```

### tx-pool/src/component/edges.rs
```diff
@@ -91,6 +91,10 @@ impl Edges {
         self.outputs.get(out_point)
     }
 
+    pub(crate) fn remove_deps(&mut self, out_point: &OutPoint) -> Option<HashSet<ProposalShortId>> {
+        self.deps.remove(out_point)
+    }
+
     pub(crate) fn insert_deps(&mut self, out_point: OutPoint, txid: ProposalShortId) {
         self.deps.entry(out_point).or_default().insert(txid);
     }
```
