# [?] fix(indexer): panic when rollback after prune

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2022-10-14
Source: https://github.com/nervosnetwork/ckb/commit/071b23abf6792feef0e36a1d751db2ea08111e9e
Type: security-commit

## Details
fix(indexer): panic when rollback after prune

## Patch
### util/indexer/src/indexer.rs
```diff
@@ -715,8 +715,9 @@ where
     /// Prune useless data
     pub(crate) fn prune(&self) -> Result<(), Error> {
         let (tip_number, _tip_hash) = self.tip()?.expect("stored tip");
-        if tip_number > self.keep_num {
-            let prune_to_block = tip_number - self.keep_num;
+        let prune_number = self.keep_num + 1;
+        if tip_number > prune_number {
+            let prune_to_block = tip_number - prune_number;
             let mut batch = self.store.batch()?;
             // prune ConsumedOutPoint => Cell
             let key_prefix_consumed_out_point = vec![KeyPrefix::ConsumedOutPoint as u8];
@@ -1007,10 +1008,12 @@ mod tests {
         H256,
     };
 
+    const KEEP_NUM: u64 = 10;
+
     fn new_indexer<S: Store>(prefix: &str) -> Indexer<S> {
         let tmp_dir = tempfile::Builder::new().prefix(prefix).tempdir().unwrap();
         let store = S::new(tmp_dir.path().to_str().unwrap());
-        Indexer::new(store, 10, 1, None, CustomFilters::new(None, None))
+        Indexer::new(store, KEEP_NUM, 1, None, CustomFilters::new(None, None))
     }
 
     #[test]
@@ -1553,7 +1556,8 @@ mod tests {
             .unwrap()
             .take_while(|(key, _value)| key.starts_with(&key_prefix))
             .count();
-        assert_eq!(22, stored_consumed_out_points);
+        // 12 blocks
+        assert_eq!(24, stored_consumed_out_points);
 
         let key_prefix = [KeyPrefix::TxHash as u8];
         let stored_tx_hashes = indexer
@@ -1562,8 +1566,73 @@ mod tests {
             .unwrap()
             .take_while(|(key, _value)| key.starts_with(&key_prefix))
             .count();
-        // 11 blocks, 3 txs per block
-        assert_eq!(33, stored_tx_hashes);
+        // 12 blocks, 3 txs per block
+        assert_eq!(36, stored_tx_hashes);
+    }
+
+    // This case is to test whether the prune boundary affects the rollback history block
+    #[test]
+    fn prune_bound() {
+        let indexer = new_indexer::<RocksdbStore>("prune");
+
+        let lock_script1 = ScriptBuilder::default()
+            .code_hash(H256(rand::random()).pack())
+            .hash_type(ScriptHashType::Data.into())
+            .args(Bytes::from(b"lock_script1".to_vec()).pack())
+            .build();
+
+        let cellbase0 = TransactionBuilder::default()
+            .input(CellInput::new_cellbase_input(0))
+            .witness(Script::default().into_witness())
+            .output(
+                CellOutputBuilder::default()
+                    .capacity(capacity_bytes!(1000).pack())
+                    .lock(lock_script1.clone())
+                    .build(),
+            )
+            .output_data(Default::default())
+            .build();
+
+        let block0 = BlockBuilder::default()
+            .transaction(cellbase0)
+            .header(HeaderBuilder::default().number(0.pack()).build())
+            .build();
+
+        indexer.append(&block0).unwrap();
+
+        let mut pre_block = block0;
+
+        for i in 0..20 {
+            let cellbase = TransactionBuilder::default()
+                .input(CellInput::new_cellbase_input(i + 1))
+                .witness(Script::default().into_witness())
+                .output(
+                    CellOutputBuilder::default()
+                        .capacity(capacity_bytes!(1000).pack())
+                        .lock(lock_script1.clone())
+                        .build(),
+                )
+                .output_data(Default::default())
+                .build();
+
+            pre_block = BlockBuilder::default()
+                .transaction(cellbase)
+                .header(
+                    HeaderBuilder::default()
+                        .number((pre_block.number() + 1).pack())
+                        .parent_hash(pre_block.hash())
+                        .build(),
+                )
+                .build();
+
+            indexer.append(&pre_block).unwrap();
+        }
+
+        let (tip_number, _) = indexer.tip().unwrap().unwrap();
+        let longest_fork_number = tip_number.saturating_sub(KEEP_NUM);
+        let rollback_start = indexer.get_block_hash(longest_fork_number);
+        assert!(rollback_start.is_ok());
+        assert!(rollback_start.unwrap().is_some());
     }
 
     #[test]
```
