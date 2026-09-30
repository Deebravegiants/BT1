# [?] Fix panic after restarting the server

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2021-02-01
Source: https://github.com/matter-labs/zksync/commit/7e7a43c7f998f91764b9b6ba6926a9e31201ac9c
Type: security-commit

## Details
Fix panic after restarting the server

## Patch
### core/bin/data_restore/src/database_storage_interactor.rs
```diff
@@ -261,6 +261,7 @@ impl StorageInteractor for DatabaseStorageInteractor<'_> {
             .await
             .expect("Can't get the last verified block");
 
+        // Use new schema to get `last_committed`, `last_verified_block` and `last_executed_block` (ZKS-427).
         self.storage
             .data_restore_schema()
             .initialize_eth_stats(
```

### core/bin/zksync_core/src/mempool/mod.rs
```diff
@@ -352,7 +352,7 @@ impl MempoolBlocksHandler {
     }
 
     async fn run(mut self) {
-        log::info!("Block mempool handler is  running");
+        log::info!("Block mempool handler is running");
         while let Some(request) = self.requests.next().await {
             match request {
                 MempoolBlocksRequest::GetBlock(block) => {
@@ -564,7 +564,7 @@ impl MempoolTransactionsHandler {
     }
 
     async fn run(mut self) {
-        log::info!("Transaction mempool handler is  running");
+        log::info!("Transaction mempool handler is running");
         while let Some(request) = self.requests.next().await {
             match request {
                 MempoolTransactionRequest::NewTx(tx, resp) => {
```

### core/bin/zksync_core/src/state_keeper/mod.rs
```diff
@@ -329,21 +329,13 @@ impl ZkSyncStateInitParams {
         storage: &mut zksync_storage::StorageProcessor<'_>,
         block_number: BlockNumber,
     ) -> Result<u64, anyhow::Error> {
-        let is_operation_exists = storage
+        let block = storage
             .chain()
-            .operations_schema()
-            .get_stored_aggregated_operation(block_number, AggregatedActionType::CommitBlocks)
-            .await
-            .is_some();
-
-        if is_operation_exists {
-            let block = storage
-                .chain()
-                .block_schema()
-                .get_block(block_number)
-                .await?
-                .expect("Block should exist");
+            .block_schema()
+            .get_block(block_number)
+            .await?;
 
+        if let Some(block) = block {
             Ok(block.processed_priority_ops.1)
         } else {
             Ok(0)
```

### core/bin/zksync_eth_sender/src/database.rs
```diff
@@ -23,10 +23,10 @@ pub(super) trait DatabaseInterface {
     /// Loads the unconfirmed and unprocessed operations from the database.
     /// Unconfirmed operations are Ethereum operations that were started, but not confirmed yet.
     /// Unprocessed operations are zkSync operations that were not started at all.
-    async fn restore_state(
+    async fn load_unconfirmed_operations(
         &self,
         connection: &mut StorageProcessor<'_>,
-    ) -> anyhow::Result<(VecDeque<ETHOperation>, Vec<(i64, AggregatedOperation)>)>;
+    ) -> anyhow::Result<VecDeque<ETHOperation>>;
 
     /// Loads the unprocessed operations from the database.
     /// Unprocessed operations are zkSync operations that were not started at all.
@@ -124,19 +124,16 @@ impl DatabaseInterface for Database {
         Ok(connection)
     }
 
-    async fn restore_state(
+    async fn load_unconfirmed_operations(
         &self,
         connection: &mut StorageProcessor<'_>,
-    ) -> anyhow::Result<(VecDeque<ETHOperation>, Vec<(i64, AggregatedOperation)>)> {
+    ) -> anyhow::Result<VecDeque<ETHOperation>> {
         let unconfirmed_ops = connection
             .ethereum_schema()
             .load_unconfirmed_operations()
             .await?;
-        let unprocessed_ops = connection
-            .ethereum_schema()
-            .load_unprocessed_operations()
-            .await?;
-        Ok((unconfirmed_ops, unprocessed_ops))
+
+        Ok(unconfirmed_ops)
     }
 
     async fn load_new_operations(
```

### core/bin/zksync_eth_sender/src/lib.rs
```diff
@@ -131,14 +131,27 @@ impl<ETH: EthereumInterface, DB: DatabaseInterface> ETHSender<ETH, DB> {
             .acquire_connection()
             .await
             .expect("Unable to connect to DB");
+        let mut transaction = connection
+            .start_transaction()
+            .await
+            .expect("Unable create database transaction");
 
-        let (ongoing_ops, unprocessed_ops) = db
-            .restore_state(&mut connection)
+        let ongoing_ops = db
+            .load_unconfirmed_operations(&mut transaction)
             .await
             .expect("Can't restore state");
 
+        let operations_id = ongoing_ops
+            .iter()
+            .filter_map(|eth_op| eth_op.op.as_ref())
+            .map(|aggregated_op| aggregated_op.0)
+            .collect::<Vec<_>>();
+        db.remove_unprocessed_operations(&mut transaction, operations_id)
+            .await
+            .expect("Failed remove unprocessed operations");
+
         let stats = db
-            .load_stats(&mut connection)
+            .load_stats(&mut transaction)
             .await
             .expect("Failed loading ETH operations stats");
 
@@ -151,31 +164,20 @@ impl<ETH: EthereumInterface, DB: DatabaseInterface> ETHSender<ETH, DB> {
 
         let gas_adjuster = GasAdjuster::new(&db).await;
 
+        transaction
+            .commit()
+            .await
+            .expect("Failed commit database transaction");
         drop(connection);
-        let mut sender = Self {
+
+        Self {
             ethereum,
             ongoing_ops,
             db,
             tx_queue,
             gas_adjuster,
             options,
-        };
-
-        // Add all the unprocessed operations to the queue.
-        for operation in unprocessed_ops {
-            log::info!(
-                "Adding unprocessed ZKSync operation <id -; action: {}; blocks: {}-{}> to queue",
-                // operation.id.expect("ID must be set"),
-                operation.1.get_action_type().to_string(),
-                operation.1.get_block_range().0,
-                operation.1.get_block_range().1,
-            );
-            sender
-                .add_operation_to_queue(operation)
-                .expect("Failed add unprocessed ZKSync operation");
         }
-
-        sender
     }
 
     /// Main routine of `ETHSender`.
@@ -185,10 +187,10 @@ impl<ETH: EthereumInterface, DB: DatabaseInterface> ETHSender<ETH, DB> {
                 self.options.sender.tx_poll_period(),
                 self.load_new_operations(),
             );
-            // Display an error message only if the error is in receiving new operations and not the timeout.
+            // If the time has expired then we do nothing, but if we received an error
+            // when loading an new operation, then panic.
             if let Ok(load_new_operation) = load_new_operation_future.await {
-                load_new_operation
-                    .unwrap_or_else(|e| log::warn!("Failed load new operations : {}", e));
+                load_new_operation.unwrap_or_else(|e| panic!("Failed load new operations: {}", e));
             }
 
             if self.options.sender.is_enabled {
```

### core/bin/zksync_eth_sender/src/tests/mock.rs
```diff
@@ -158,10 +158,10 @@ impl DatabaseInterface for MockDatabase {
         Ok(())
     }
 
-    async fn restore_state(
+    async fn load_unconfirmed_operations(
         &self,
         _connection: &mut StorageProcessor<'_>,
-    ) -> anyhow::Result<(VecDeque<ETHOperation>, Vec<(i64, AggregatedOperation)>)> {
+    ) -> anyhow::Result<VecDeque<ETHOperation>> {
         todo!()
         // Ok((
         //     self.restore_state.clone(),
```

### core/lib/storage/sqlx-data.json
```diff
@@ -186,6 +186,18 @@
       ]
     }
   },
+  "0d6babe453e10d8fd58e15eaac7b77d9d5ad315b84d36c66f7abb414202666d1": {
+    "query": "INSERT INTO eth_unprocessed_aggregated_ops (op_id)\n                VALUES ($1)",
+    "describe": {
+      "columns": [],
+      "parameters": {
+        "Left": [
+          "Int8"
+        ]
+      },
+      "nullable": []
+    }
+  },
   "0e390d0f58d24733d76253da2e4d9c9a0f5c96702d164fe3ad64af8aec43ee49": {
     "query": "\n                SELECT * FROM account_balance_updates\n                WHERE account_id = $1 AND block_number > $2\n            ",
     "describe": {
@@ -4024,18 +4036,6 @@
       ]
     }
   },
-  "faa748174cd959672c7c14247c4dcb66194758e0eeefe4de5935a55e208a2139": {
-    "query": "INSERT INTO eth_unprocessed_aggregated_ops (op_id)\n            VALUES ($1)",
-    "describe": {
-      "columns": [],
-      "parameters": {
-        "Left": [
-          "Int8"
-        ]
-      },
-      "nullable": []
-    }
-  },
   "fd16aadbd04d4a48332d59c77290a588f1a33922418b55a08c656a44ff75b8e8": {
     "query": "SELECT * FROM account_balance_updates WHERE block_number = $1",
     "describe": {
```

### core/lib/storage/src/chain/operations/mod.rs
```diff
@@ -324,13 +324,18 @@ impl<'a, 'c> OperationsSchema<'a, 'c> {
         .await?
         .id;
 
-        sqlx::query!(
-            "INSERT INTO eth_unprocessed_aggregated_ops (op_id)
-            VALUES ($1)",
-            id
-        )
-        .execute(transaction.conn())
-        .await?;
+        if !matches!(
+            operation.get_action_type(),
+            AggregatedActionType::CreateProofBlocks
+        ) {
+            sqlx::query!(
+                "INSERT INTO eth_unprocessed_aggregated_ops (op_id)
+                VALUES ($1)",
+                id
+            )
+            .execute(transaction.conn())
+            .await?;
+        }
 
         transaction.commit().await?;
         Ok(())
```

### core/lib/storage/src/data_restore/mod.rs
```diff
@@ -237,8 +237,7 @@ impl<'a, 'c> DataRestoreSchema<'a, 'c> {
         last_executed_block: BlockNumber,
     ) -> QueryResult<()> {
         let start = Instant::now();
-        // Withdraw ops counter is set equal to the `verify` ops counter
-        // since we assume that we've sent a withdraw for every `verify` op.
+
         sqlx::query!(
             "UPDATE eth_parameters
             SET last_committed_block = $1, last_verified_block = $2, last_executed_block = $3
```
