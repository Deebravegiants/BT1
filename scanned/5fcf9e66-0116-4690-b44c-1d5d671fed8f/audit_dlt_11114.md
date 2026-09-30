# [?] Do not panic on rejected txs

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2021-11-18
Source: https://github.com/matter-labs/zksync/commit/29bff639418b194077881176188c41bda6acc643
Type: security-commit

## Details
Do not panic on rejected txs

Signed-off-by: deniallugo <deniallugo@gmail.com>

## Patch
### core/bin/zksync_core/src/rejected_tx_cleaner.rs
```diff
@@ -25,12 +25,14 @@ pub fn run_rejected_tx_cleaner(config: &ZkSyncConfig, db_pool: ConnectionPool) -
                 .access_storage()
                 .await
                 .expect("transactions cleaner couldn't access the database");
-            storage
+            if let Err(e) = storage
                 .chain()
                 .operations_schema()
                 .remove_rejected_transactions(max_age)
                 .await
-                .expect("failed to delete rejected transactions from the database");
+            {
+                vlog::error!("Can't delete rejected transactions {:?}", e);
+            }
             timer.tick().await;
         }
     })
```

### core/lib/storage/sqlx-data.json
```diff
@@ -3453,18 +3453,6 @@
       ]
     }
   },
-  "8542fbcf1f669243a111348851c36ec3b01c4c11ac3391d55546d22a9e714e6b": {
-    "query": "DELETE FROM executed_transactions\n            WHERE success = false AND created_at < $1",
-    "describe": {
-      "columns": [],
-      "parameters": {
-        "Left": [
-          "Timestamptz"
-        ]
-      },
-      "nullable": []
-    }
-  },
   "860cebd02464f314a5d2f7f9708beff689cce8891d8727189318732765f60a88": {
     "query": "\n            WITH aggr_comm AS (\n                SELECT \n                    aggregate_operations.created_at, \n                    eth_operations.final_hash, \n                    commit_aggregated_blocks_binding.block_number \n                FROM aggregate_operations\n                    INNER JOIN commit_aggregated_blocks_binding ON aggregate_operations.id = commit_aggregated_blocks_binding.op_id\n                    INNER JOIN eth_aggregated_ops_binding ON aggregate_operations.id = eth_aggregated_ops_binding.op_id\n                    INNER JOIN eth_operations ON eth_operations.id = eth_aggregated_ops_binding.eth_op_id\n                WHERE aggregate_operations.confirmed = true \n            ),\n            aggr_exec as (\n                 SELECT \n                    aggregate_operations.created_at, \n                    eth_operations.final_hash, \n                    execute_aggregated_blocks_binding.block_number \n                FROM aggregate_operations\n                    INNER JOIN execute_aggregated_blocks_binding ON aggregate_operations.id = execute_aggregated_blocks_binding.op_id\n                    INNER JOIN eth_aggregated_ops_binding ON aggregate_operations.id = eth_aggregated_ops_binding.op_id\n                    INNER JOIN eth_operations ON eth_operations.id = eth_aggregated_ops_binding.eth_op_id\n                WHERE aggregate_operations.confirmed = true \n            )\n            SELECT\n                blocks.number AS \"block_number!\",\n                blocks.root_hash AS \"new_state_root!\",\n                blocks.block_size AS \"block_size!\",\n                committed.final_hash AS \"commit_tx_hash?\",\n                verified.final_hash AS \"verify_tx_hash?\",\n                committed.created_at AS \"committed_at!\",\n                verified.created_at AS \"verified_at?\"\n            FROM blocks\n                     INNER JOIN aggr_comm committed ON blocks.number = committed.block_number\n                     LEFT JOIN aggr_exec verified ON blocks.number = verified.block_number\n            WHERE false\n                OR committed.final_hash = $1\n                OR verified.final_hash = $1\n                OR blocks.root_hash = $1\n                OR blocks.number = $2\n            ORDER BY blocks.number DESC\n            LIMIT 1;\n            ",
     "describe": {
@@ -4367,6 +4355,18 @@
       "nullable": []
     }
   },
+  "a545c7251d381afbb2bdcbaef0cc5f1bc322db47ee0db555b83b9e19119bc756": {
+    "query": "DELETE FROM executed_transactions WHERE tx_hash IN (SELECT tx_hash FROM executed_transactions WHERE success = false AND created_at < $1 LIMIT 1000)",
+    "describe": {
+      "columns": [],
+      "parameters": {
+        "Left": [
+          "Timestamptz"
+        ]
+      },
+      "nullable": []
+    }
+  },
   "a77668a3dce7f7cd1f45816f932eea685d429c3d75b40ea8e1a1bb9fc29f11c6": {
     "query": "UPDATE prover_job_queue SET (job_status, updated_at, updated_by) = ($1, now(), 'server_clean_idle')\n            WHERE job_status = $2 and (now() - updated_at) >= interval '120 seconds'",
     "describe": {
```
