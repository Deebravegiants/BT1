# [?] Fix server panic

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2021-02-11
Source: https://github.com/matter-labs/zksync/commit/25bd3682f184e64e8791e1c1f25bf008103d1b4a
Type: security-commit

## Details
Fix server panic

## Patch
### core/lib/storage/sqlx-data.json
```diff
@@ -2201,68 +2201,6 @@
       ]
     }
   },
-  "83064cc95efff2cea2b6ff1b3ae13e07a247afb40c2a287968988110404cd175": {
-    "query": "SELECT eth_operations.* FROM aggregate_operations\n                  LEFT JOIN eth_aggregated_ops_binding ON eth_aggregated_ops_binding.op_id = aggregate_operations.id\n                  LEFT JOIN eth_operations ON eth_aggregated_ops_binding.eth_op_id = eth_operations.id\n            WHERE\n                  eth_operations.confirmed = true AND aggregate_operations.id = $1\n            LIMIT 1",
-    "describe": {
-      "columns": [
-        {
-          "ordinal": 0,
-          "name": "id",
-          "type_info": "Int8"
-        },
-        {
-          "ordinal": 1,
-          "name": "nonce",
-          "type_info": "Int8"
-        },
-        {
-          "ordinal": 2,
-          "name": "confirmed",
-          "type_info": "Bool"
-        },
-        {
-          "ordinal": 3,
-          "name": "raw_tx",
-          "type_info": "Bytea"
-        },
-        {
-          "ordinal": 4,
-          "name": "op_type",
-          "type_info": "Text"
-        },
-        {
-          "ordinal": 5,
-          "name": "final_hash",
-          "type_info": "Bytea"
-        },
-        {
-          "ordinal": 6,
-          "name": "last_deadline_block",
-          "type_info": "Int8"
-        },
-        {
-          "ordinal": 7,
-          "name": "last_used_gas_price",
-          "type_info": "Numeric"
-        }
-      ],
-      "parameters": {
-        "Left": [
-          "Int8"
-        ]
-      },
-      "nullable": [
-        false,
-        false,
-        false,
-        false,
-        false,
-        true,
-        false,
-        false
-      ]
-    }
-  },
   "83cc9ff843c9dd1c974b651f5ed1e0c6bea94454db1d6f01b8fdf556cdd77d81": {
     "query": "DELETE FROM mempool_txs\n            WHERE tx_hash = $1",
     "describe": {
@@ -3114,6 +3052,69 @@
       ]
     }
   },
+  "bec05747dcfbf729bfd6e5d6aedf8da39f6d0d4ab5f0eae8dfed6c07adac1ba8": {
+    "query": "SELECT eth_operations.* FROM aggregate_operations\n                LEFT JOIN eth_aggregated_ops_binding ON eth_aggregated_ops_binding.op_id = aggregate_operations.id\n                LEFT JOIN eth_operations ON eth_aggregated_ops_binding.eth_op_id = eth_operations.id\n            WHERE\n                ($1 BETWEEN from_block AND to_block) AND action_type = $2 AND eth_operations.confirmed = true \n            LIMIT 1",
+    "describe": {
+      "columns": [
+        {
+          "ordinal": 0,
+          "name": "id",
+          "type_info": "Int8"
+        },
+        {
+          "ordinal": 1,
+          "name": "nonce",
+          "type_info": "Int8"
+        },
+        {
+          "ordinal": 2,
+          "name": "confirmed",
+          "type_info": "Bool"
+        },
+        {
+          "ordinal": 3,
+          "name": "raw_tx",
+          "type_info": "Bytea"
+        },
+        {
+          "ordinal": 4,
+          "name": "op_type",
+          "type_info": "Text"
+        },
+        {
+          "ordinal": 5,
+          "name": "final_hash",
+          "type_info": "Bytea"
+        },
+        {
+          "ordinal": 6,
+          "name": "last_deadline_block",
+          "type_info": "Int8"
+        },
+        {
+          "ordinal": 7,
+          "name": "last_used_gas_price",
+          "type_info": "Numeric"
+        }
+      ],
+      "parameters": {
+        "Left": [
+          "Int8",
+          "Text"
+        ]
+      },
+      "nullable": [
+        false,
+        false,
+        false,
+        false,
+        false,
+        true,
+        false,
+        false
+      ]
+    }
+  },
   "bf002ea8011c653cebce62d2c49f4a5e7415e45fb7db5f7f68ae86c43b60b393": {
     "query": "SELECT * FROM eth_parameters WHERE id = true",
     "describe": {
```

### core/lib/storage/src/chain/operations/mod.rs
```diff
@@ -353,21 +353,15 @@ impl<'a, 'c> OperationsSchema<'a, 'c> {
             return Ok(None);
         };
 
-        let execute_block_operation = self
-            .get_aggregated_op_that_affects_block(AggregatedActionType::ExecuteBlocks, block_number)
+        let withdrawal_hash = EthereumSchema(self.0)
+            .aggregated_op_final_hash(block_number)
             .await?;
 
-        let res = if let Some((op_id, _)) = execute_block_operation {
-            EthereumSchema(self.0).aggregated_op_final_hash(op_id).await
-        } else {
-            Ok(None)
-        };
-
         metrics::histogram!(
             "sql.chain.operations.eth_withdraw_tx_for_execute_block",
             start.elapsed()
         );
-        res
+        Ok(withdrawal_hash)
     }
 
     /// Returns the hash of the Ethereum transaction in which the
```

### core/lib/storage/src/ethereum/mod.rs
```diff
@@ -8,6 +8,7 @@ use zksync_basic_types::{H256, U256};
 // Workspace imports
 use zksync_types::aggregated_operations::{AggregatedActionType, AggregatedOperation};
 use zksync_types::ethereum::{ETHOperation, InsertedOperationResponse};
+use zksync_types::BlockNumber;
 // Local imports
 use self::records::{ETHParams, ETHStats, ETHTxHash, StorageETHOperation};
 use crate::{chain::operations::records::StoredAggregatedOperation, QueryResult, StorageProcessor};
@@ -591,16 +592,20 @@ impl<'a, 'c> EthereumSchema<'a, 'c> {
         Ok(())
     }
 
-    pub async fn aggregated_op_final_hash(&mut self, op_id: i64) -> QueryResult<Option<H256>> {
+    pub async fn aggregated_op_final_hash(
+        &mut self,
+        block_number: BlockNumber,
+    ) -> QueryResult<Option<H256>> {
         let eth_operation = sqlx::query_as!(
             StorageETHOperation,
             "SELECT eth_operations.* FROM aggregate_operations
-                  LEFT JOIN eth_aggregated_ops_binding ON eth_aggregated_ops_binding.op_id = aggregate_operations.id
-                  LEFT JOIN eth_operations ON eth_aggregated_ops_binding.eth_op_id = eth_operations.id
+                LEFT JOIN eth_aggregated_ops_binding ON eth_aggregated_ops_binding.op_id = aggregate_operations.id
+                LEFT JOIN eth_operations ON eth_aggregated_ops_binding.eth_op_id = eth_operations.id
             WHERE
-                  eth_operations.confirmed = true AND aggregate_operations.id = $1
+                ($1 BETWEEN from_block AND to_block) AND action_type = $2 AND eth_operations.confirmed = true 
             LIMIT 1",
-            op_id
+            i64::from(*block_number),
+            AggregatedActionType::ExecuteBlocks.to_string(),
         )
         .fetch_optional(self.0.conn())
         .await?;
```
