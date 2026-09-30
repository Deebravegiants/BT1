# [?] Fix create block template panic

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-04-19
Source: https://github.com/starcoinorg/starcoin/commit/0ca40b94d86bf4916ed0e60eef5bd484e7e081de
Type: security-commit

## Details
Fix create block template panic

## Patch
### Cargo.lock
```diff
@@ -1662,7 +1662,7 @@ dependencies = [
  "anyhow",
  "bytecode-verifier",
  "datatest-stable",
- "language-e2e-tests",
+ "language-e2e-tests 0.1.0 (git+https://github.com/starcoinorg/libra?rev=a65fce0cd5bd321c2a6ecf8e2a29ff78afca67a9)",
  "libra-config",
  "libra-crypto",
  "libra-state-view",
@@ -2684,6 +2684,41 @@ dependencies = [
  "vm-genesis",
 ]
 
+[[package]]
+name = "language-e2e-tests"
+version = "0.1.0"
+dependencies = [
+ "anyhow",
+ "bytecode-verifier",
+ "compiler",
+ "language-e2e-tests 0.1.0 (git+https://github.com/starcoinorg/libra?rev=a65fce0cd5bd321c2a6ecf8e2a29ff78afca67a9)",
+ "libra-canonical-serialization",
+ "libra-config",
+ "libra-crypto",
+ "libra-logger",
+ "libra-proptest-helpers",
+ "libra-state-view",
+ "libra-types",
+ "libra-vm",
+ "move-core-types",
+ "move-vm-cache",
+ "move-vm-runtime",
+ "move-vm-state",
+ "move-vm-types",
+ "once_cell",
+ "parity-multiaddr 0.7.3",
+ "proptest",
+ "proptest-derive",
+ "rand 0.6.5",
+ "starcoin-config",
+ "starcoin-types",
+ "starcoin-vm-runtime",
+ "stdlib 0.1.0 (git+https://github.com/starcoinorg/libra?rev=a65fce0cd5bd321c2a6ecf8e2a29ff78afca67a9)",
+ "transaction-builder",
+ "vm",
+ "vm-genesis",
+]
+
 [[package]]
 name = "language-tags"
 version = "0.2.2"
@@ -6156,6 +6191,33 @@ dependencies = [
  "tokio-executor 0.2.0-alpha.6",
 ]
 
+[[package]]
+name = "starcoin-functional-tests"
+version = "0.1.0"
+dependencies = [
+ "aho-corasick",
+ "anyhow",
+ "bytecode-verifier",
+ "datatest-stable",
+ "functional-tests",
+ "language-e2e-tests 0.1.0",
+ "libra-config",
+ "libra-crypto",
+ "libra-state-view",
+ "libra-types",
+ "mirai-annotations",
+ "move-core-types",
+ "move-lang",
+ "once_cell",
+ "regex",
+ "starcoin-types",
+ "stdlib 0.1.0",
+ "tempfile",
+ "termcolor",
+ "thiserror",
+ "vm",
+]
+
 [[package]]
 name = "starcoin-genesis"
 version = "0.1.0"
@@ -6753,21 +6815,6 @@ dependencies = [
  "vm",
 ]
 
-[[package]]
-name = "starcoin-vm-tests"
-version = "0.1.0"
-dependencies = [
- "anyhow",
- "bytecode-verifier",
- "datatest-stable",
- "functional-tests",
- "libra-types",
- "move-lang",
- "stdlib 0.1.0",
- "tempfile",
- "vm",
-]
-
 [[package]]
 name = "starcoin-wallet-api"
 version = "0.1.0"
```

### chain/src/chain.rs
```diff
@@ -205,11 +205,10 @@ where
             block_info.num_leaves,
             block_info.num_nodes,
             self.storage.clone(),
-        )
-        .unwrap();
+        )?;
+
         let (accumulator_root, state_root) =
-            BlockExecutor::block_execute(&self.config.vm, &chain_state, &accumulator, txns, true)
-                .unwrap();
+            BlockExecutor::block_execute(&self.config.vm, &chain_state, &accumulator, txns, true)?;
 
         Ok(BlockTemplate::new(
             previous_header.id(),
@@ -375,7 +374,7 @@ where
             None => self.current_header().id(),
         };
         assert!(self.exist_block(block_id));
-        let previous_header = self.get_header(block_id).unwrap().unwrap();
+        let previous_header = self.get_header(block_id)?.unwrap();
         self.create_block_template_inner(author, auth_key_prefix, previous_header, user_txns)
     }
 
```

### miner/src/lib.rs
```diff
@@ -26,6 +26,7 @@ use traits::{Consensus, ConsensusHeader};
 use types::transaction::TxStatus;
 
 pub use miner_client::miner::{Miner as MinerClient, MinerClientActor};
+
 mod headblock_pacemaker;
 mod miner;
 mod miner_client;
@@ -175,7 +176,11 @@ where
                 let block_chain =
                     BlockChain::<C, S, P>::new(config.clone(), head, storage, txpool, collection)
                         .unwrap();
-                let _ = mint::<H, C>(stratum, miner, config, miner_account, txns, &block_chain);
+                if let Err(e) =
+                    mint::<H, C>(stratum, miner, config, miner_account, txns, &block_chain)
+                {
+                    error!("Setting mint job failed: {:?}", e);
+                }
             });
         }
         .into_actor(self);
```
