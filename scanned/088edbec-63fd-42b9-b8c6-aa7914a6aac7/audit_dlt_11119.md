# [?] Merge branch 'stanislav-breadless-ZKS-232-forcedexit-automation' into stanislav-breadless-ZKS-494-fe-automation-dos-prevention

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2021-02-26
Source: https://github.com/matter-labs/zksync/commit/e7e357912578c6d4be7eec8a36a871bb81b82993
Type: security-commit

## Details
Merge branch 'stanislav-breadless-ZKS-232-forcedexit-automation' into stanislav-breadless-ZKS-494-fe-automation-dos-prevention

## Patch
### .github/workflows/ci.yml
```diff
@@ -161,6 +161,7 @@ jobs:
         run: |
           echo ZKSYNC_HOME=$(pwd) >> $GITHUB_ENV
           echo $(pwd)/bin >> $GITHUB_PATH
+          echo PLUGIN_CONFIG=fast >> $GITHUB_ENV # use fast mode for geth image (instant tx commit)
 
       - name: start-services
         run: |
```

### changelog/core.md
```diff
@@ -8,6 +8,22 @@ All notable changes to the core components will be documented in this file.
 
 ### Changed
 
+- (`loadtest`): `zksync_fee` has been moved to `[main_wallet]` section from the `[network]` section.
+
+### Added
+
+- (`loadtest`): Added `zksync_fee` option into the `[scenario]` section to set fee for each scenario individually, added
+  `fee_token` option into the `[main_wallet]` section to set token that is used to pay fees for the main wallet
+  operations.
+
+### Fixed
+
+## Release 2021-02-19
+
+### Removed
+
+### Changed
+
 - The token name is now set for each scenario separately instead of the network section of the loadtest configuration.
 - Rejected transactions are now stored in the database for 2 weeks only.
 
@@ -17,9 +33,12 @@ All notable changes to the core components will be documented in this file.
 - Added a `--sloppy` mode to the `dev-fee-ticker-server` to simulate bad networks with the random delays and fails.
 - Added `forced_exit_requests` functionality, which allows users to pay for ForcedExits from L1. Note that a few env
   variables were added that control the behaviour of the tool.
+- Possibility to use CREATE2 ChangePubKey and Transfer in a single batch.
 
 ### Fixed
 
+- Bug with the assignment of new account ids in the state.
+
 ## Release 2021-02-02
 
 ### Removed
```

### changelog/infrastructure.md
```diff
@@ -11,7 +11,17 @@ components, the logs will have the following format:
 
 ### Removed
 
-- (`ci/Dockerfile`): `dockerci/Dockerfile` file with folder was removed , because it is outdated.
+### Changed
+
+### Added
+
+### Fixed
+
+## Release 2021-02-19
+
+### Removed
+
+- (`ci/Dockerfile`): `docker/ci` folder was removed, because it is outdated.
 
 ### Changed
 
```

### core/bin/zksync_api/src/api_server/rest/v1/test_utils.rs
```diff
@@ -28,6 +28,7 @@ use zksync_types::{
     helpers::{apply_updates, closest_packable_fee_amount, closest_packable_token_amount},
     operations::{ChangePubKeyOp, TransferToNewOp},
     prover::ProverJobType,
+    tx::ChangePubKeyType,
     AccountId, AccountMap, Address, BlockNumber, Deposit, DepositOp, ExecutedOperations,
     ExecutedPriorityOp, ExecutedTx, FullExit, FullExitOp, Nonce, PriorityOp, Token, TokenId,
     Transfer, TransferOp, ZkSyncOp, ZkSyncTx, H256,
@@ -124,7 +125,7 @@ impl TestServerConfig {
                 false,
                 TokenId(0),
                 fee.into(),
-                false,
+                ChangePubKeyType::ECDSA,
                 Default::default(),
             );
 
```

### core/bin/zksync_api/src/api_server/rest/v1/transactions.rs
```diff
@@ -641,8 +641,11 @@ mod tests {
             .map(|(tx, token)| (tx.clone(), token, tx.account()))
             .collect::<Vec<_>>();
         let batch_signature = {
+            let eth_private_key = acc
+                .try_get_eth_private_key()
+                .expect("Should have ETH private key");
             let batch_message = EthBatchSignData::get_batch_sign_message(txs);
-            let eth_sig = PackedEthSignature::sign(&acc.eth_private_key, &batch_message).unwrap();
+            let eth_sig = PackedEthSignature::sign(eth_private_key, &batch_message).unwrap();
             let single_signature = TxEthSignature::EthereumSignature(eth_sig);
 
             EthBatchSignatures::Single(single_signature)
@@ -690,7 +693,7 @@ mod tests {
         assert!(client
             .submit_tx(
                 transfer_bad_token.clone(),
-                Some(TxEthSignature::EthereumSignature(eth_sig)),
+                eth_sig.map(TxEthSignature::EthereumSignature),
                 None
             )
             .await
@@ -708,7 +711,10 @@ mod tests {
             .collect::<Vec<_>>();
         let batch_signature = {
             let batch_message = EthBatchSignData::get_batch_sign_message(txs);
-            let eth_sig = PackedEthSignature::sign(&from.eth_private_key, &batch_message).unwrap();
+            let eth_private_key = from
+                .try_get_eth_private_key()
+                .expect("should have eth private key");
+            let eth_sig = PackedEthSignature::sign(eth_private_key, &batch_message).unwrap();
             let single_signature = TxEthSignature::EthereumSignature(eth_sig);
 
             EthBatchSignatures::Single(single_signature)
@@ -757,7 +763,10 @@ mod tests {
             .collect::<Vec<_>>();
         let batch_signature = {
             let batch_message = EthBatchSignData::get_batch_sign_message(txs);
-            let eth_sig = PackedEthSignature::sign(&from.eth_private_key, &batch_message).unwrap();
+            let eth_private_key = from
+                .try_get_eth_private_key()
+                .expect("should have eth private key");
+            let eth_sig = PackedEthSignature::sign(eth_private_key, &batch_message).unwrap();
             let single_signature = TxEthSignature::EthereumSignature(eth_sig);
 
             EthBatchSignatures::Single(single_signature)
@@ -803,7 +812,7 @@ mod tests {
         client
             .submit_tx(
                 ZkSyncTx::Transfer(Box::new(tx.clone())),
-                Some(TxEthSignature::EthereumSignature(eth_sig.clone())),
+                eth_sig.clone().map(TxEthSignature::EthereumSignature),
                 Some(true),
             )
             .await
@@ -812,15 +821,15 @@ mod tests {
         client
             .submit_tx(
                 ZkSyncTx::Transfer(Box::new(tx.clone())),
-                Some(TxEthSignature::EthereumSignature(eth_sig.clone())),
+                eth_sig.clone().map(TxEthSignature::EthereumSignature),
                 Some(false),
             )
             .await?;
         // Submit without fast-processing flag.
         client
             .submit_tx(
                 ZkSyncTx::Transfer(Box::new(tx)),
-                Some(TxEthSignature::EthereumSignature(eth_sig)),
+                eth_sig.clone().map(TxEthSignature::EthereumSignature),
                 None,
             )
             .await?;
@@ -839,23 +848,23 @@ mod tests {
         client
             .submit_tx(
                 ZkSyncTx::Withdraw(Box::new(tx.clone())),
-                Some(TxEthSignature::EthereumSignature(eth_sig.clone())),
+                eth_sig.clone().map(TxEthSignature::EthereumSignature),
                 Some(true),
             )
             .await?;
         // Submit with the disabled fast-processing.
         client
             .submit_tx(
                 ZkSyncTx::Withdraw(Box::new(tx.clone())),
-                Some(TxEthSignature::EthereumSignature(eth_sig.clone())),
+                eth_sig.clone().map(TxEthSignature::EthereumSignature),
                 Some(false),
             )
             .await?;
         // Submit without fast-processing flag.
         client
             .submit_tx(
                 ZkSyncTx::Withdraw(Box::new(tx)),
-                Some(TxEthSignature::EthereumSignature(eth_sig.clone())),
+                eth_sig.clone().map(TxEthSignature::EthereumSignature),
                 None,
             )
             .await?;
```

### core/bin/zksync_api/src/api_server/tx_sender.rs
```diff
@@ -1,7 +1,7 @@
 //! Helper module to submit transactions into the zkSync Network.
 
 // Built-in uses
-use std::{fmt::Display, str::FromStr};
+use std::{collections::HashSet, fmt::Display, str::FromStr};
 
 // External uses
 use bigdecimal::BigDecimal;
@@ -20,7 +20,7 @@ use zksync_types::{
     tx::{
         EthBatchSignData, EthBatchSignatures, EthSignData, SignedZkSyncTx, TxEthSignature, TxHash,
     },
-    Address, BatchFee, Fee, Token, TokenId, TokenLike, TxFeeTypes, ZkSyncTx,
+    Address, BatchFee, Fee, Token, TokenId, TokenLike, TxFeeTypes, ZkSyncTx, H160,
 };
 
 // Local uses
@@ -443,9 +443,18 @@ impl TxSender {
             verified_txs.extend(verified_batch.into_iter());
         } else {
             // Otherwise, we process every transaction in turn.
-            for (tx, sender, token, sender_type, msg_to_sign) in
+
+            // This hashset holds addresses that have performed a CREATE2 ChangePubKey
+            // within this batch, so that we don't check ETH signatures on their transactions
+            // from this batch. We save the account type to the db later.
+            let mut create2_senders = HashSet::<H160>::new();
+
+            for (tx, sender, token, mut sender_type, msg_to_sign) in
                 izip!(txs, tx_senders, tokens, tx_sender_types, messages_to_sign)
             {
+                if create2_senders.contains(&sender) {
+                    sender_type = EthAccountType::CREATE2;
+                }
                 let verified_tx = verify_tx_info_message_signature(
                     &tx.tx,
                     sender,
@@ -458,6 +467,14 @@ impl TxSender {
                 .await?
                 .unwrap_tx();
 
+                if let ZkSyncTx::ChangePubKey(tx) = tx.tx {
+                    if let Some(auth_data) = tx.eth_auth_data {
+                        if auth_data.is_create2() {
+                            create2_senders.insert(sender);
+                        }
+                    }
+                }
+
                 verified_txs.push(verified_tx);
             }
         }
```

### core/bin/zksync_api/src/fee_ticker/constants.rs
```diff
@@ -24,6 +24,9 @@ pub(crate) const BASE_OLD_CHANGE_PUBKEY_OFFCHAIN_COST: u64 =
 pub(crate) const BASE_CHANGE_PUBKEY_OFFCHAIN_COST: u64 = CommitCost::CHANGE_PUBKEY_COST_OFFCHAIN
     + VerifyCost::CHANGE_PUBKEY_COST
     + AMORTIZED_COST_PER_CHUNK * (ChangePubKeyOp::CHUNKS as u64);
+pub(crate) const BASE_CHANGE_PUBKEY_CREATE2_COST: u64 = CommitCost::CHANGE_PUBKEY_COST_CREATE2
+    + VerifyCost::CHANGE_PUBKEY_COST
+    + AMORTIZED_COST_PER_CHUNK * (ChangePubKeyOp::CHUNKS as u64);
 pub(crate) const BASE_CHANGE_PUBKEY_ONCHAIN_COST: u64 = CommitCost::CHANGE_PUBKEY_COST_ONCHAIN
     + VerifyCost::CHANGE_PUBKEY_COST
     + AMORTIZED_COST_PER_CHUNK * (ChangePubKeyOp::CHUNKS as u64);
@@ -34,3 +37,4 @@ pub(crate) const SUBSIDY_TRANSFER_COST: u64 = 550;
 pub(crate) const SUBSIDY_TRANSFER_TO_NEW_COST: u64 = 550 * 3;
 pub(crate) const SUBSIDY_WITHDRAW_COST: u64 = 45000;
 pub(crate) const SUBSIDY_CHANGE_PUBKEY_OFFCHAIN_COST: u64 = 10000;
+pub(crate) const SUBSIDY_CHANGE_PUBKEY_CREATE2_COST: u64 = 10000;
```

### core/bin/zksync_api/src/fee_ticker/mod.rs
```diff
@@ -26,8 +26,8 @@ use tokio::time::Instant;
 use zksync_config::{configs::ticker::TokenPriceSource, ZkSyncConfig};
 use zksync_storage::ConnectionPool;
 use zksync_types::{
-    Address, BatchFee, ChangePubKeyOp, Fee, OutputFeeType, Token, TokenId, TokenLike, TransferOp,
-    TransferToNewOp, TxFeeTypes, WithdrawOp,
+    tokens::ChangePubKeyFeeTypeArg, tx::ChangePubKeyType, Address, BatchFee, ChangePubKeyOp, Fee,
+    OutputFeeType, Token, TokenId, TokenLike, TransferOp, TransferToNewOp, TxFeeTypes, WithdrawOp,
 };
 use zksync_utils::ratio_to_big_decimal;
 
@@ -46,7 +46,6 @@ use crate::fee_ticker::{
     },
 };
 use crate::utils::token_db_cache::TokenDBCache;
-use zksync_types::tokens::{ChangePubKeyFeeType, ChangePubKeyFeeTypeArg};
 
 mod constants;
 mod ticker_api;
@@ -104,21 +103,21 @@ impl GasOperationsCost {
             ),
             (
                 OutputFeeType::ChangePubKey(ChangePubKeyFeeTypeArg::ContractsV4Version(
-                    ChangePubKeyFeeType::Onchain,
+                    ChangePubKeyType::Onchain,
                 )),
                 constants::BASE_CHANGE_PUBKEY_ONCHAIN_COST.into(),
             ),
             (
                 OutputFeeType::ChangePubKey(ChangePubKeyFeeTypeArg::ContractsV4Version(
-                    ChangePubKeyFeeType::ECDSA,
+                    ChangePubKeyType::ECDSA,
                 )),
                 constants::BASE_CHANGE_PUBKEY_OFFCHAIN_COST.into(),
             ),
             (
                 OutputFeeType::ChangePubKey(ChangePubKeyFeeTypeArg::ContractsV4Version(
-                    ChangePubKeyFeeType::CREATE2,
+                    ChangePubKeyType::CREATE2,
                 )),
-                constants::BASE_CHANGE_PUBKEY_OFFCHAIN_COST.into(),
+                constants::BASE_CHANGE_PUBKEY_CREATE2_COST.into(),
             ),
         ]
         .into_iter()
@@ -155,21 +154,21 @@ impl GasOperationsCost {
             ),
             (
                 OutputFeeType::ChangePubKey(ChangePubKeyFeeTypeArg::ContractsV4Version(
-                    ChangePubKeyFeeType::Onchain,
+                    ChangePubKeyType::Onchain,
                 )),
                 constants::BASE_CHANGE_PUBKEY_ONCHAIN_COST.into(),
             ),
             (
                 OutputFeeType::ChangePubKey(ChangePubKeyFeeTypeArg::ContractsV4Version(
-                    ChangePubKeyFeeType::ECDSA,
+                    ChangePubKeyType::ECDSA,
                 )),
                 constants::SUBSIDY_CHANGE_PUBKEY_OFFCHAIN_COST.into(),
             ),
             (
                 OutputFeeType::ChangePubKey(ChangePubKeyFeeTypeArg::ContractsV4Version(
-                    ChangePubKeyFeeType::CREATE2,
+                    ChangePubKeyType::CREATE2,
                 )),
-                constants::SUBSIDY_CHANGE_PUBKEY_OFFCHAIN_COST.into(),
+                constants::SUBSIDY_CHANGE_PUBKEY_CREATE2_COST.into(),
             ),
         ]
         .into_iter()
```

### core/bin/zksync_core/src/eth_watch/client.rs
```diff
@@ -145,5 +145,7 @@ impl EthClient for EthHttpClient {
 }
 
 pub async fn get_web3_block_number(web3: &Web3<http::Http>) -> anyhow::Result<u64> {
-    Ok(web3.eth().block_number().await?.as_u64())
+    let block_number = web3.eth().block_number().await?.as_u64();
+
+    Ok(block_number)
 }
```

### core/bin/zksync_core/src/mempool/mod.rs
```diff
@@ -463,15 +463,9 @@ async fn store_account_type(
     tx: &ChangePubKey,
     storage: &mut StorageProcessor<'_>,
 ) -> Result<(), TxAddError> {
-    let account_type = if tx
-        .eth_auth_data
-        .as_ref()
-        .map(|auth| auth.is_create2())
-        .unwrap_or(false)
-    {
-        EthAccountType::CREATE2
-    } else {
-        EthAccountType::Owned
+    let account_type = match &tx.eth_auth_data {
+        Some(auth) if auth.is_create2() => EthAccountType::CREATE2,
+        _ => EthAccountType::Owned,
     };
     storage
         .chain()
```

### core/bin/zksync_core/src/state_keeper/tests.rs
```diff
@@ -855,7 +855,7 @@ mod execute_proposed_block {
         let bad_withdraw = create_account_and_withdrawal(
             &mut tester,
             TokenId(2),
-            AccountId(2),
+            AccountId(1),
             100u32,
             145u32,
             Default::default(),
@@ -884,7 +884,7 @@ mod execute_proposed_block {
         let good_withdraw = create_account_and_withdrawal(
             &mut tester,
             TokenId(2),
-            AccountId(2),
+            AccountId(1),
             200u32,
             145u32,
             Default::default(),
@@ -914,7 +914,7 @@ mod execute_proposed_block {
         let bad_withdraw = create_account_and_withdrawal(
             &mut tester,
             TokenId(2),
-            AccountId(2),
+            AccountId(1),
             100u32,
             145u32,
             Default::default(),
```

### core/bin/zksync_forced_exit_requests/src/eth_watch.rs
```diff
@@ -344,8 +344,7 @@ pub fn run_forced_exit_contract_watcher(
             connection_pool.clone(),
             config.clone(),
         )
-        .await
-        .unwrap();
+        .await;
 
         // In case there were some transactions which were submitted
         // but were not committed we will try to wait until they are committed
```
