# [?] add double spend checking for orphan tx

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2023-10-23
Source: https://github.com/nervosnetwork/ckb/commit/c5efc75804da6b6ed331bdab163785fa43de166c
Type: security-commit

## Details
add double spend checking for orphan tx

## Patch
### test/src/main.rs
```diff
@@ -429,6 +429,7 @@ fn all_specs() -> Vec<Box<dyn Spec>> {
         Box::new(TxPoolOrphanNormal),
         Box::new(TxPoolOrphanReverse),
         Box::new(TxPoolOrphanUnordered),
+        Box::new(TxPoolOrphanDoubleSpend),
         Box::new(OrphanTxRejected),
         Box::new(GetRawTxPool),
         Box::new(PoolReconcile),
```

### test/src/specs/tx_pool/orphan_tx.rs
```diff
@@ -205,23 +205,23 @@ impl Spec for TxPoolOrphanNormal {
         );
         assert!(
             run_replay_tx(&net, node0, tx1, 0, 2),
-            "tx1 is send expect nothing in orphan pool"
+            "tx1 is sent expect nothing in orphan pool"
         );
         assert!(
             run_replay_tx(&net, node0, tx11, 0, 3),
-            "tx11 is send expect nothing in orphan pool"
+            "tx11 is sent expect nothing in orphan pool"
         );
         assert!(
             run_replay_tx(&net, node0, tx12, 0, 4),
-            "tx12 is send expect nothing in orphan pool"
+            "tx12 is sent expect nothing in orphan pool"
         );
         assert!(
             run_replay_tx(&net, node0, tx13, 0, 5),
-            "tx13 is send expect nothing in orphan pool"
+            "tx13 is sent expect nothing in orphan pool"
         );
         assert!(
             run_replay_tx(&net, node0, final_tx, 0, 6),
-            "final_tx is send expect nothing in orphan pool"
+            "final_tx is sent expect nothing in orphan pool"
         );
     }
 }
@@ -293,12 +293,58 @@ impl Spec for TxPoolOrphanUnordered {
         );
         assert!(
             run_replay_tx(&net, node0, tx1, 1, 4),
-            "tx1 is send, orphan pool only contains final_tx"
+            "tx1 is sent, orphan pool only contains final_tx"
         );
 
         assert!(
             run_replay_tx(&net, node0, tx13, 0, 6),
-            "tx13 is send, orphan pool is empty"
+            "tx13 is sent, orphan pool is empty"
+        );
+    }
+}
+
+pub struct TxPoolOrphanDoubleSpend;
+impl Spec for TxPoolOrphanDoubleSpend {
+    fn run(&self, nodes: &mut Vec<Node>) {
+        let node0 = &nodes[0];
+        node0.mine_until_out_bootstrap_period();
+        let parent = node0.new_transaction_with_capacity(capacity_bytes!(800));
+
+        let script = node0.always_success_script();
+        let new_output1 = CellOutputBuilder::default()
+            .capacity(capacity_bytes!(200).pack())
+            .lock(script.clone())
+            .build();
+        let new_output2 = new_output1.clone();
+        let new_output3 = new_output1.clone();
+
+        let tx1 = parent
+            .as_advanced_builder()
+            .set_inputs(vec![CellInput::new(OutPoint::new(parent.hash(), 0), 0)])
+            .set_outputs(vec![new_output1, new_output2, new_output3])
+            .set_outputs_data(vec![Default::default(); 3])
+            .build();
+
+        let tx11 =
+            node0.new_transaction_with_capacity_and_index(tx1.hash(), capacity_bytes!(100), 0, 0);
+        let tx12 =
+            node0.new_transaction_with_capacity_and_index(tx1.hash(), capacity_bytes!(120), 0, 0);
+
+        let mut net = Net::new(
+            "orphan_tx_test",
+            node0.consensus(),
+            vec![SupportProtocols::RelayV3],
+        );
+        net.connect(node0);
+
+        assert!(
+            run_replay_tx(&net, node0, tx11, 1, 0),
+            "tx11 in orphan pool"
+        );
+
+        assert!(
+            run_replay_tx(&net, node0, tx12, 1, 0),
+            "tx12 is not in orphan pool"
         );
     }
 }
```

### tx-pool/src/component/orphan.rs
```diff
@@ -69,6 +69,7 @@ impl OrphanPool {
 
     pub fn remove_orphan_tx(&mut self, id: &ProposalShortId) -> Option<Entry> {
         self.entries.remove(id).map(|entry| {
+            debug!("remove orphan tx {}", entry.tx.hash());
             for out_point in entry.tx.input_pts_iter() {
                 self.by_out_point.remove(&out_point);
             }
@@ -83,7 +84,7 @@ impl OrphanPool {
         self.shrink_to_fit();
     }
 
-    pub fn limit_size(&mut self) -> usize {
+    fn limit_size(&mut self) -> usize {
         let now = ckb_systemtime::unix_time().as_secs();
         let expires: Vec<_> = self
             .entries
@@ -122,6 +123,15 @@ impl OrphanPool {
         if self.entries.contains_key(&tx.proposal_short_id()) {
             return;
         }
+
+        // double spend checking
+        if tx
+            .input_pts_iter()
+            .any(|out_point| self.by_out_point.contains_key(&out_point))
+        {
+            return;
+        }
+
         debug!("add_orphan_tx {}", tx.hash());
 
         self.entries.insert(
```

### tx-pool/src/pool.rs
```diff
@@ -203,6 +203,7 @@ impl TxPool {
     ) {
         for tx in txs {
             let tx_hash = tx.hash();
+            debug!("try remove_committed_tx {}", tx_hash);
             self.remove_committed_tx(tx, callbacks);
 
             self.committed_txs_hash_cache
```

### tx-pool/src/process.rs
```diff
@@ -473,16 +473,20 @@ impl TxPoolService {
 
     pub(crate) async fn find_orphan_by_previous(&self, tx: &TransactionView) -> Vec<OrphanEntry> {
         let orphan = self.orphan.read().await;
-        let ids = orphan.find_by_previous(tx);
-        ids.iter()
-            .map(|id| orphan.get(id).cloned().unwrap())
+        orphan
+            .find_by_previous(tx)
+            .iter()
+            .filter_map(|id| orphan.get(id).cloned())
             .collect::<Vec<_>>()
     }
 
     pub(crate) async fn remove_orphan_tx(&self, id: &ProposalShortId) {
         self.orphan.write().await.remove_orphan_tx(id);
     }
 
+    /// Remove all orphans which are resolved by the given transaction
+    /// the process is like a breath first search, if there is a cycle in `orphan_queue`,
+    /// `_process_tx` will return `Reject` since we have checked duplicated tx
     pub(crate) async fn process_orphan_tx(&self, tx: &TransactionView) {
         let mut orphan_queue: VecDeque<TransactionView> = VecDeque::new();
         orphan_queue.push_back(tx.clone());
@@ -917,24 +921,19 @@ impl TxPoolService {
             }
         }
 
-        self.remove_orphan_txs_by_attach(attached.iter()).await;
+        self.remove_orphan_txs_by_attach(&attached).await;
         {
             let mut chunk = self.chunk.write().await;
             chunk.remove_chunk_txs(attached.iter().map(|tx| tx.proposal_short_id()));
         }
     }
 
-    async fn remove_orphan_txs_by_attach<'a>(
-        &self,
-        txs: impl Iterator<Item = &'a TransactionView>,
-    ) {
-        let mut ids = vec![];
-        for tx in txs {
-            ids.push(tx.proposal_short_id());
+    async fn remove_orphan_txs_by_attach<'a>(&self, txs: &LinkedHashSet<TransactionView>) {
+        for tx in txs.iter() {
             self.process_orphan_tx(tx).await;
         }
         let mut orphan = self.orphan.write().await;
-        orphan.remove_orphan_txs(ids.into_iter());
+        orphan.remove_orphan_txs(txs.iter().map(|tx| tx.proposal_short_id()));
     }
 
     fn readd_detached_tx(
```
