# [?] [Smoke Test] Small race condition fixes.

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-07
Source: https://github.com/aptos-labs/aptos-core/commit/544323b5a75b3e3a33c24a63948f70544ba67ee8
Type: security-commit

## Details
[Smoke Test] Small race condition fixes.

## Patch
### testsuite/smoke-test/src/state_sync_utils.rs
```diff
@@ -202,6 +202,9 @@ fn verify_first_ledger_info(node: &mut LocalNode) {
     let aptos_db = AptosDB::new_for_test_with_sharding(db_path_buf.as_path(), 1 << 13);
     aptos_db.get_epoch_ending_ledger_info(0).unwrap();
 
+    // Drop the DB handle before restarting the node to release the rocks DB lock file
+    drop(aptos_db);
+
     // Restart the node
     node.start().unwrap();
 }
```

### testsuite/smoke-test/src/utils.rs
```diff
@@ -119,14 +119,12 @@ pub async fn execute_transactions(
     }
 
     // Always ensure that at least one reconfiguration transaction is executed
-    if !execute_epoch_changes {
-        aptos_forge::reconfig(
-            client,
-            &transaction_factory,
-            swarm.chain_info().root_account,
-        )
-        .await;
-    }
+    aptos_forge::reconfig(
+        client,
+        &transaction_factory,
+        swarm.chain_info().root_account,
+    )
+    .await;
 }
 
 /// Executes transactions and waits for all nodes to catch up
```
