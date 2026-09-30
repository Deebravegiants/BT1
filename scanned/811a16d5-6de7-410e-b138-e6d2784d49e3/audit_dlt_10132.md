# [?] fix a potential panic, `indexer.tip` may fail.

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2024-01-04
Source: https://github.com/nervosnetwork/ckb/commit/497a632beb7e3993af19d40aeb9164227048c584
Type: security-commit

## Details
fix a potential panic, `indexer.tip` may fail.

## Patch
### util/indexer-sync/src/lib.rs
```diff
@@ -95,38 +95,42 @@ impl IndexerSyncService {
             error!("secondary_db try_catch_up_with_primary error {}", e);
         }
         loop {
-            if let Some((tip_number, tip_hash)) = indexer.tip().expect("get tip should be OK") {
-                match self.get_block_by_number(tip_number + 1) {
-                    Some(block) => {
-                        if block.parent_hash() == tip_hash {
-                            info!(
-                                "{} append {}, {}",
-                                indexer.get_identity(),
-                                block.number(),
-                                block.hash()
-                            );
-                            indexer.append(&block).expect("append block should be OK");
-                        } else {
-                            info!(
-                                "{} rollback {}, {}",
-                                indexer.get_identity(),
-                                tip_number,
-                                tip_hash
-                            );
-                            indexer.rollback().expect("rollback block should be OK");
+            match indexer.tip() {
+                Ok(Some((tip_number, tip_hash))) => {
+                    match self.get_block_by_number(tip_number + 1) {
+                        Some(block) => {
+                            if block.parent_hash() == tip_hash {
+                                info!(
+                                    "{} append {}, {}",
+                                    indexer.get_identity(),
+                                    block.number(),
+                                    block.hash()
+                                );
+                                indexer.append(&block).expect("append block should be OK");
+                            } else {
+                                info!(
+                                    "{} rollback {}, {}",
+                                    indexer.get_identity(),
+                                    tip_number,
+                                    tip_hash
+                                );
+                                indexer.rollback().expect("rollback block should be OK");
+                            }
+                        }
+                        None => {
+                            break;
                         }
-                    }
-                    None => {
-                        break;
                     }
                 }
-            } else {
-                match self.get_block_by_number(0) {
+                Ok(None) => match self.get_block_by_number(0) {
                     Some(block) => indexer.append(&block).expect("append block should be OK"),
                     None => {
-                        error!("ckb node returns an empty genesis block");
+                        error!("CKB node returns an empty genesis block");
                         break;
                     }
+                },
+                Err(e) => {
+                    error!("Failed to get tip: {}", e);
                 }
             }
         }
```

### util/rich-indexer/src/indexer_handle/async_indexer_handle.rs
```diff
@@ -579,11 +579,9 @@ async fn build_sql_by_filter(
                     query_builder
                         .and_where_eq("lock_script.code_hash", format!("${}", param_index));
                     param_index += 1;
-
                     query_builder
                         .and_where_eq("lock_script.hash_type", format!("${}", param_index));
                     param_index += 1;
-
                     query_builder.and_where(format!("lock_script.args LIKE ${}", param_index));
                     param_index += 1;
                 }
```
