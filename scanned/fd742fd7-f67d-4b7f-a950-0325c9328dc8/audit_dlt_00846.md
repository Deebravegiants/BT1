# [?] Merge branch 'grarco/fix-masp-height-overflow' (#4725)

## Summary
Severity: Unknown
Chain: Namada
Component: anoma/namada
Published: 2025-07-16
Source: https://github.com/namada-net/namada/commit/783786578bdcc98630932420b93e1dd2ca83a4f6
Type: security-commit

## Details
Merge branch 'grarco/fix-masp-height-overflow' (#4725)

* origin/grarco/fix-masp-height-overflow:
  Error out on missing block
  Fixes broken migration test
  Adjusts block height in dry-run
  Fixes broken tests
  Changelog #4725
  Improves masp expiration tests
  Fixes possible expiration overflow in masp tx construction

## Patch
### .changelog/unreleased/bug-fixes/4725-fix-masp-height-overflow.md
```diff
@@ -0,0 +1,2 @@
+- Fixed a possible overflow of the masp expiration height in the SDK.
+  ([\#4725](https://github.com/anoma/namada/pull/4725))
\ No newline at end of file
```

### crates/node/src/dry_run_tx.rs
```diff
@@ -33,7 +33,7 @@ where
     tx.validate_tx().into_storage_result()?;
 
     let gas_scale = parameters::get_gas_scale(&state)?;
-    let height = state.in_mem().get_last_block_height();
+    let height = state.in_mem().get_block_height().0;
 
     // Wrapper dry run to allow estimating the entire gas cost of a transaction
     let (wrapper_hash, tx_result, tx_gas_meter) = match tx.header().tx_type {
```

### crates/node/src/shell/testing/node.rs
```diff
@@ -371,6 +371,15 @@ impl MockNode {
             .unwrap_or_default()
     }
 
+    pub fn last_block_height(&self) -> BlockHeight {
+        self.shell
+            .lock()
+            .unwrap()
+            .state
+            .in_mem()
+            .get_last_block_height()
+    }
+
     pub fn current_epoch(&self) -> Epoch {
         self.shell.lock().unwrap().state.in_mem().last_epoch
     }
@@ -484,9 +493,8 @@ impl MockNode {
     pub fn finalize_and_commit(&self, header_time: Option<DateTimeUtc>) {
         let (proposer_address, votes) = self.prepare_request();
 
+        let height = self.last_block_height().next_height();
         let mut locked = self.shell.lock().unwrap();
-        let height =
-            locked.state.in_mem().get_last_block_height().next_height();
 
         // check if we have protocol txs to be included
         // in the finalize block request
@@ -614,9 +622,8 @@ impl MockNode {
             }),
             ..Default::default()
         };
+        let height = self.last_block_height().next_height();
         let mut locked = self.shell.lock().unwrap();
-        let height =
-            locked.state.in_mem().get_last_block_height().next_height();
         let (result, tx_results) = locked.process_proposal(req);
 
         let mut errors: Vec<_> = tx_results
```

### crates/node/src/utils.rs
```diff
@@ -189,7 +189,7 @@ pub fn dry_run_proposal(
 
     let gas_scale = parameters::get_gas_scale(&state)
         .expect("Failed to get gas scale from parameters");
-    let height = state.in_mem().get_last_block_height();
+    let height = state.in_mem().get_block_height().0;
 
     let mut tx = Tx::from_type(TxType::Raw);
     tx.header.chain_id = chain_id.clone();
```

### crates/shielded_token/src/masp/shielded_wallet.rs
```diff
@@ -1277,10 +1277,17 @@ pub trait ShieldedApi<U: ShieldedUtils + MaybeSend + MaybeSync>:
             Some(expiration) => {
                 // Try to match a DateTime expiration with a plausible
                 // corresponding block height
-                let last_block_height = Self::query_block(context.client())
-                    .await
-                    .map_err(|e| TransferErr::General(e.to_string()))?
-                    .unwrap_or(1);
+                let last_block_height = u32::try_from(
+                    Self::query_block(context.client())
+                        .await
+                        .map_err(|e| TransferErr::General(e.to_string()))?
+                        .ok_or_else(|| {
+                            TransferErr::General(
+                                "No blocks have been produced yet".to_string(),
+                            )
+                        })?,
+                )
+                .map_err(|e| TransferErr::General(e.to_string()))?;
                 let max_block_time =
                     Self::query_max_block_time_estimate(context.client())
                         .await
@@ -1296,14 +1303,20 @@ pub trait ShieldedApi<U: ShieldedUtils + MaybeSend + MaybeSync>:
                         / i64::try_from(max_block_time.0).unwrap(),
                 )
                 .map_err(|e| TransferErr::General(e.to_string()))?;
-                u32::try_from(last_block_height)
-                    .map_err(|e| TransferErr::General(e.to_string()))?
-                    + delta_blocks
+                match checked!(last_block_height + delta_blocks) {
+                    Ok(height) if height <= u32::MAX - 20 => height,
+                    _ => {
+                        return Err(TransferErr::General(
+                            "The provided expiration exceeds the maximum \
+                             allowed"
+                                .to_string(),
+                        ));
+                    }
+                }
             }
             None => {
-                // NOTE: The masp library doesn't support optional
-                // expiration so we set the max to mimic
-                // a never-expiring tx. We also need to
+                // NOTE: The masp library doesn't support optional expiration so
+                // we set the max to mimic a never-expiring tx. We also need to
                 // remove 20 which is going to be added back by the builder
                 u32::MAX - 20
             }
```

### crates/state/src/in_memory.rs
```diff
@@ -216,12 +216,23 @@ where
         )
     }
 
-    /// Get the block height
+    /// Get the block height. The height is that of the block to which the
+    /// current transaction is being applied if we are in between the
+    /// `FinalizeBlock` and the `Commit` phases. For all the other phases we
+    /// return the block height of next block that the consensus process
+    /// will decide upon (i.e. the block height of the last committed block
+    /// + 1)
     pub fn get_block_height(&self) -> (BlockHeight, Gas) {
+        let height = match self.header {
+            Some(_) => self.block.height,
+            // When not finalizing a decided block, increase the block height to
+            // match that of the next block that will be proposed
+            None => self.block.height.next_height(),
+        };
         // Adding consts that cannot overflow
         #[allow(clippy::arithmetic_side_effects)]
         (
-            self.block.height,
+            height,
             (BLOCK_HEIGHT_LENGTH as u64 * MEMORY_ACCESS_GAS_PER_BYTE).into(),
         )
     }
```

### crates/state/src/wl_state.rs
```diff
@@ -1198,10 +1198,10 @@ where
         Ok(tree)
     }
 
-    /// Get the timestamp of the last committed block, or the current timestamp
-    /// if no blocks have been produced yet
+    /// Get the timestamp of the last committed block, or the current local
+    /// timestamp if no blocks have been produced yet
     pub fn get_last_block_timestamp(&self) -> Result<DateTimeUtc> {
-        let last_block_height = self.in_mem.get_block_height().0;
+        let last_block_height = self.in_mem.get_last_block_height();
 
         Ok(self.db.read_block_header(last_block_height)?.map_or_else(
             #[allow(clippy::disallowed_methods)]
```

### crates/storage/src/lib.rs
```diff
@@ -89,7 +89,11 @@ pub trait StorageRead {
     fn get_chain_id(&self) -> Result<ChainId>;
 
     /// Getting the block height. The height is that of the block to which the
-    /// current transaction is being applied.
+    /// current transaction is being applied if we are in between the
+    /// `FinalizeBlock` and the `Commit` phases. For all the other phases we
+    /// return the block height of next block that the consensus process
+    /// will decide upon (i.e. the block height of the last committed block
+    /// + 1)
     fn get_block_height(&self) -> Result<BlockHeight>;
 
     /// Getting the block header.
```

### crates/tests/src/integration/ledger_tests.rs
```diff
@@ -2325,7 +2325,7 @@ fn scheduled_migration() -> Result<()> {
         locked.scheduled_migration = Some(scheduled_migration);
     }
 
-    while node.block_height().0 != 4 {
+    while node.last_block_height().0 != 4 {
         node.finalize_and_commit(None)
     }
     // check that the key doesn't exist before the scheduled block
```

### crates/tests/src/integration/masp.rs
```diff
@@ -15,6 +15,7 @@ use namada_apps_lib::wallet::defaults::{
 use namada_core::address::Address;
 use namada_core::dec::Dec;
 use namada_core::masp::{MaspTxId, Precision, TokenMap, encode_asset_type};
+use namada_node::shell::ResultCode;
 use namada_node::shell::testing::client::run;
 use namada_node::shell::testing::node::NodeResults;
 use namada_node::shell::testing::utils::{Bin, CapturedOutput};
@@ -4598,9 +4599,11 @@ fn multiple_unfetched_txs_same_block() -> Result<()> {
     Ok(())
 }
 
-/// Tests that an expired masp tx is rejected by the vp
+/// Tests that an expired masp tx is rejected by the vp. The transaction is
+/// applied at the first invalid height, i.e. block_height = expiration_height +
+/// 1
 #[test]
-fn expired_masp_tx() -> Result<()> {
+fn masp_tx_expiration_first_invalid_block_height() -> Result<()> {
     // This address doesn't matter for tests. But an argument is required.
     let validator_one_rpc = "http://127.0.0.1:26567";
     // Download the shielded pool parameters before starting node
@@ -4704,6 +4707,18 @@ fn expired_masp_tx() -> Result<()> {
         .native_token
         .clone();
     let mut tx = Tx::try_from_json_bytes(&tx_bytes).unwrap();
+    let masp_expiry_height = tx
+        .sections
+        .iter()
+        .find_map(|section| {
+            if let Section::MaspTx(transaction) = section {
+                Some(transaction)
+            } else {
+                None
+            }
+        })
+        .unwrap()
+        .expiry_height();
     // Remove the expiration field to avoid a failure because of it, we only
     // want to check the expiration in the masp vp
     tx.header.expiration = None;
@@ -4719,9 +4734,8 @@ fn expired_masp_tx() -> Result<()> {
     let wrapper_hash = tx.wrapper_hash();
     let inner_cmt = tx.first_commitments().unwrap();
 
-    // Skip at least 20 blocks to ensure expiration (this is because of the
-    // default masp expiration)
-    for _ in 0..=20 {
+    // Skip blocks to ensure expiration
+    while u64::from(node.block_height()) < u64::from(masp_expiry_height) {
         node.finalize_and_commit(None);
     }
     node.clear_results();
@@ -4768,6 +4782,349 @@ fn expired_masp_tx() -> Result<()> {
     Ok(())
 }
 
+// Tests that an expired masp tx doing masp fee payment is rejected by the vp in
+// process proposal. The transaction is set to be applied at the first invalid
+// height, i.e. block_height = expiration_height + 1
+#[test]
+fn masp_tx_expiration_first_invalid_block_height_with_fee_payment() -> Result<()>
+{
+    // This address doesn't matter for tests. But an argument is required.
+    let validator_one_rpc = "http://127.0.0.1:26567";
+    // Download the shielded pool parameters before starting node
+    let _ = FsShieldedUtils::new(PathBuf::new());
+    let (mut node, _services) = setup::setup()?;
+    _ = node.next_epoch();
+
+    // Initialize account we can access the secret keys of. The account must
+    // have no balance to be used as a disposable gas payer
+    let (cooper_alias, cooper_key) =
+        make_temp_account(&node, validator_one_rpc, "Cooper", NAM, 0)?;
+
+    // 1. Shield tokens
+    _ = node.next_epoch();
+    run(
+        &node,
+        Bin::Client,
+        apply_use_device(vec![
+            "shield",
+            "--source",
+            ALBERT_KEY,
+            "--target",
+            AA_PAYMENT_ADDRESS,
+            "--token",
+            NAM,
+            "--amount",
+            "100",
+            "--ledger-address",
+            validator_one_rpc,
+        ]),
+    )?;
+    // sync shielded context
+    run(
+        &node,
+        Bin::Client,
+        vec!["shielded-sync", "--node", validator_one_rpc],
+    )?;
+
+    // 2. Shielded operation to avoid the need of a signature on the inner tx.
+    //    Dump the tx to then reload and submit
+    let tempdir = tempfile::tempdir().unwrap();
+
+    _ = node.next_epoch();
+    let captured = CapturedOutput::of(|| {
+        run(
+            &node,
+            Bin::Client,
+            apply_use_device(vec![
+                "transfer",
+                "--source",
+                A_SPENDING_KEY,
+                "--target",
+                AC_PAYMENT_ADDRESS,
+                "--token",
+                NAM,
+                "--amount",
+                "50",
+                // This gas payer has no funds so we are going to use it as a
+                // disposable gas payer via the MASP
+                "--gas-payer",
+                cooper_alias.as_ref(),
+                // We want to create an expired masp tx. Doing so will also set
+                // the expiration field of the header which can
+                // be a problem because this would lead to the
+                // transaction being rejected by the
+                // protocol check while we want to test expiration in the masp
+                // vp. However, this is not a real issue: to
+                // avoid the failure in protocol we are going
+                // to overwrite the header with one having no
+                // expiration
+                "--expiration",
+                #[allow(clippy::disallowed_methods)]
+                &DateTimeUtc::now().to_string(),
+                "--output-folder-path",
+                tempdir.path().to_str().unwrap(),
+                "--dump-tx",
+                "--ledger-address",
+                validator_one_rpc,
+            ]),
+        )
+    });
+    assert!(captured.result.is_ok());
+
+    let file_path = tempdir
+        .path()
+        .read_dir()
+        .unwrap()
+        .next()
+        .unwrap()
+        .unwrap()
+        .path();
+    let tx_bytes = std::fs::read(&file_path).unwrap();
+    std::fs::remove_file(&file_path).unwrap();
+
+    let sk = cooper_key;
+    let pk = sk.to_public();
+
+    let native_token = node
+        .shell
+        .lock()
+        .unwrap()
+        .state
+        .in_mem()
+        .native_token
+        .clone();
+    let mut tx = Tx::try_from_json_bytes(&tx_bytes).unwrap();
+    let masp_expiry_height = tx
+        .sections
+        .iter()
+        .find_map(|section| {
+            if let Section::MaspTx(transaction) = section {
+                Some(transaction)
+            } else {
+                None
+            }
+        })
+        .unwrap()
+        .expiry_height();
+    // Remove the expiration field to avoid a failure because of it, we only
+    // want to check the expiration in the masp vp
+    tx.header.expiration = None;
+    tx.add_wrapper(
+        namada_sdk::tx::data::wrapper::Fee {
+            amount_per_gas_unit: DenominatedAmount::native(100.into()),
+            token: native_token.clone(),
+        },
+        pk.clone(),
+        DEFAULT_GAS_LIMIT.into(),
+    );
+    tx.sign_wrapper(sk.clone());
+
+    // Skip blocks to ensure expiration
+    while u64::from(node.block_height()) < u64::from(masp_expiry_height) {
+        node.finalize_and_commit(None);
+    }
+    node.clear_results();
+    node.submit_txs(vec![tx.to_bytes()]);
+    {
+        // Assert that the block was rejected in process proposal
+        let codes = node.tx_result_codes.lock().unwrap();
+        assert!(!codes.is_empty());
+
+        for code in codes.iter() {
+            match code {
+                NodeResults::Rejected(tx_result) => {
+                    assert_eq!(tx_result.code, ResultCode::FeeError.to_u32());
+                    assert!(
+                        tx_result.info.contains("MASP transaction is expired")
+                    );
+                }
+                _ => panic!("Test failed"),
+            }
+        }
+
+        let results = node.tx_results.lock().unwrap();
+        // We never made it to finalize block
+        assert!(results.is_empty());
+    }
+
+    Ok(())
+}
+
+// Tests that a masp tx applied at the last valid block before expiration
+// (block_height = expiration_height) is accepted by the vp
+#[test]
+fn masp_tx_expiration_last_valid_block_height() -> Result<()> {
+    // This address doesn't matter for tests. But an argument is required.
+    let validator_one_rpc = "http://127.0.0.1:26567";
+    // Download the shielded pool parameters before starting node
+    let _ = FsShieldedUtils::new(PathBuf::new());
+    let (mut node, _services) = setup::setup()?;
+    _ = node.next_epoch();
+
+    // Initialize accounts we can access the secret keys of
+    let (cooper_alias, cooper_key) =
+        make_temp_account(&node, validator_one_rpc, "Cooper", NAM, 500_000)?;
+
+    // 1. Shield tokens
+    _ = node.next_epoch();
+    run(
+        &node,
+        Bin::Client,
+        apply_use_device(vec![
+            "shield",
+            "--source",
+            ALBERT_KEY,
+            "--target",
+            AA_PAYMENT_ADDRESS,
+            "--token",
+            NAM,
+            "--amount",
+            "100",
+            "--ledger-address",
+            validator_one_rpc,
+        ]),
+    )?;
+    // sync shielded context
+    run(
+        &node,
+        Bin::Client,
+        vec!["shielded-sync", "--node", validator_one_rpc],
+    )?;
+
+    // 2. Shielded operation to avoid the need of a signature on the inner tx.
+    //    Dump the tx to then reload and submit
+    let tempdir = tempfile::tempdir().unwrap();
+
+    _ = node.next_epoch();
+    let captured = CapturedOutput::of(|| {
+        run(
+            &node,
+            Bin::Client,
+            apply_use_device(vec![
+                "transfer",
+                "--source",
+                A_SPENDING_KEY,
+                "--target",
+                AC_PAYMENT_ADDRESS,
+                "--token",
+                NAM,
+                "--amount",
+                "50",
+                "--gas-payer",
+                cooper_alias.as_ref(),
+                // We want to create an expired masp tx. Doing so will also set
+                // the expiration field of the header which can
+                // be a problem because this would lead to the
+                // transaction being rejected by the
+                // protocol check while we want to test expiration in the masp
+                // vp. However, this is not a real issue: to
+                // avoid the failure in protocol we are going
+                // to overwrite the header with one having no
+                // expiration
+                "--expiration",
+                #[allow(clippy::disallowed_methods)]
+                &DateTimeUtc::now().to_string(),
+                "--output-folder-path",
+                tempdir.path().to_str().unwrap(),
+                "--dump-tx",
+                "--ledger-address",
+                validator_one_rpc,
+            ]),
+        )
+    });
+    assert!(captured.result.is_ok());
+
+    let file_path = tempdir
+        .path()
+        .read_dir()
+        .unwrap()
+        .next()
+        .unwrap()
+        .unwrap()
+        .path();
+    let tx_bytes = std::fs::read(&file_path).unwrap();
+    std::fs::remove_file(&file_path).unwrap();
+
+    let sk = cooper_key;
+    let pk = sk.to_public();
+
+    let native_token = node
+        .shell
+        .lock()
+        .unwrap()
+        .state
+        .in_mem()
+        .native_token
+        .clone();
+    let mut tx = Tx::try_from_json_bytes(&tx_bytes).unwrap();
+    let masp_expiry_height = tx
+        .sections
+        .iter()
+        .find_map(|section| {
+            if let Section::MaspTx(transaction) = section {
+                Some(transaction)
+            } else {
+                None
+            }
+        })
+        .unwrap()
+        .expiry_height();
+    // Remove the expiration field to avoid a failure because of it, we only
+    // want to check the expiration in the masp vp
+    tx.header.expiration = None;
+    tx.add_wrapper(
+        namada_sdk::tx::data::wrapper::Fee {
+            amount_per_gas_unit: DenominatedAmount::native(100.into()),
+            token: native_token.clone(),
+        },
+        pk.clone(),
+        DEFAULT_GAS_LIMIT.into(),
+    );
+    tx.sign_wrapper(sk.clone());
+    let wrapper_hash = tx.wrapper_hash();
+    let inner_cmt = tx.first_commitments().unwrap();
+
+    // Skip enough blocks to get to the expiry height. Remove one from the
+    // expiry height cause that will be added back in the process of producing
+    // the block with the masp tx
+    while u64::from(node.block_height()) < (u64::from(masp_expiry_height) - 1) {
+        node.finalize_and_commit(None);
+    }
+
+    node.clear_results();
+    node.submit_txs(vec![tx.to_bytes()]);
+    {
+        let codes = node.tx_result_codes.lock().unwrap();
+        // If empty then failed in process proposal
+        assert!(!codes.is_empty());
+
+        for code in codes.iter() {
+            assert!(matches!(code, NodeResults::Ok));
+        }
+
+        let results = node.tx_results.lock().unwrap();
+        // We submitted a single batch
+        assert_eq!(results.len(), 1);
+
+        for result in results.iter() {
+            // The batch should contain a single inner tx
+            assert_eq!(result.len(), 1);
+
+            let inner_tx_result = result
+                .get_inner_tx_result(
+                    wrapper_hash.as_ref(),
+                    itertools::Either::Right(inner_cmt),
+                )
+                .expect("Missing expected tx result")
+                .as_ref()
+                .expect("Result is supposed to be Ok");
+            assert!(inner_tx_result.is_accepted());
+        }
+    }
+
+    Ok(())
+}
+
 // Test that a masp unshield transaction can be succesfully executed even across
 // an epoch boundary.
 #[test]
```

### crates/vm/src/host_env.rs
```diff
@@ -1582,7 +1582,10 @@ where
 
 /// Getting the block height function exposed to the wasm VM Tx
 /// environment. The height is that of the block to which the current
-/// transaction is being applied.
+/// transaction is being applied if we are in between the `FinalizeBlock`
+/// and the `Commit` phases. For all the other phases we return the block height
+/// of next block that the consensus process will decide upon (i.e. the block
+/// height of the last committed block + 1)
 pub fn tx_get_block_height<MEM, D, H, CA>(
     env: &mut TxVmEnv<MEM, D, H, CA>,
 ) -> TxResult<u64>
@@ -1769,7 +1772,10 @@ where
 
 /// Getting the block height function exposed to the wasm VM VP
 /// environment. The height is that of the block to which the current
-/// transaction is being applied.
+/// transaction is being applied if we are in between the `FinalizeBlock`
+/// and the `Commit` phases. For all the other phases we return the block height
+/// of next block that the consensus process will decide upon (i.e. the block
+/// height of the last committed block + 1)
 pub fn vp_get_block_height<MEM, D, H, EVAL, CA>(
     env: &mut VpVmEnv<MEM, D, H, EVAL, CA>,
 ) -> Result<u64>
```

### crates/vp/src/vp_host_fns.rs
```diff
@@ -212,7 +212,10 @@ where
 }
 
 /// Getting the block height. The height is that of the block to which the
-/// current transaction is being applied.
+/// current transaction is being applied if we are in between the
+/// `FinalizeBlock` and the `Commit` phases. For all the other phases we return
+/// the block height of next block that the consensus process will decide upon
+/// (i.e. the block height of the last committed block + 1)
 pub fn get_block_height<S>(
     gas_meter: &RefCell<impl GasMetering>,
     state: &S,
```
