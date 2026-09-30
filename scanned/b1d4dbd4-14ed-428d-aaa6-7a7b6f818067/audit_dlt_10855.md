# [?] chain: Fix assert panic (#940)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-07-23
Source: https://github.com/starcoinorg/starcoin/commit/58625b6c8eda8246e45eaa85ae1c5173ee8536ee
Type: security-commit

## Details
chain: Fix assert panic (#940)

## Patch
### chain/src/chain.rs
```diff
@@ -336,7 +336,8 @@ where
             Some(hash) => hash,
             None => self.current_header().id(),
         };
-        assert!(self.exist_block(block_id));
+        ensure!(self.exist_block(block_id), "Block id not exist");
+
         let previous_header = self
             .get_header(block_id)?
             .ok_or_else(|| format_err!("Can find block header by {:?}", block_id))?;
@@ -425,9 +426,8 @@ where
     ) -> Result<ConnectBlockResult> {
         let pre_hash = header.parent_hash();
         if verify_head_id {
-            assert_eq!(
-                self.head_block().id(),
-                pre_hash,
+            ensure!(
+                self.head_block().id() == pre_hash,
                 "Invalid block: Parent id mismatch."
             );
         }
@@ -504,13 +504,11 @@ where
             executor::block_execute(&self.chain_state, txns.clone(), block.header().gas_limit())?;
         let state_root = executed_data.state_root;
         let vec_transaction_info = &executed_data.txn_infos;
-        assert_eq!(
-            block.header().state_root(),
-            state_root,
-            "verify block:{:?} state_root fail.",
-            block.header().id()
+        ensure!(
+            state_root == block.header().state_root(),
+            "verify block:{:?} state_root fail",
+            block.header().id(),
         );
-
         let block_gas_used = vec_transaction_info
             .iter()
             .fold(0u64, |acc, i| acc + i.gas_used());
```

### chain/src/chain_service.rs
```diff
@@ -3,7 +3,7 @@
 
 use crate::{chain::BlockChain, chain_metrics::CHAIN_METRICS};
 use actix::Addr;
-use anyhow::{format_err, Error, Result};
+use anyhow::{ensure, format_err, Error, Result};
 use bus::{Broadcast, BusActor};
 use config::NodeConfig;
 use crypto::hash::PlainCryptoHash;
@@ -184,7 +184,7 @@ where
             number -= 1;
         }
 
-        assert!(
+        ensure!(
             ancestor.is_some(),
             "Can not find ancestors from block accumulator."
         );
```
