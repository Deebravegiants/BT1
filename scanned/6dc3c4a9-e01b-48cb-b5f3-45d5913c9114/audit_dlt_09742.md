# [?] fix(lightning-server): fix rare panic in LN transaction submission

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-08-21
Source: https://github.com/fedimint/fedimint/commit/e644a049d9ac7e133936a06db1bb7118ec692746
Type: security-commit

## Details
fix(lightning-server): fix rare panic in LN transaction submission

## Patch
### modules/fedimint-ln-server/src/lib.rs
```diff
@@ -725,8 +725,17 @@ impl ServerModule for Lightning {
                 .await;
 
                 // TODO: sanity-check encrypted preimage size
-                dbtx.insert_new_entry(&OfferKey(offer.hash), &(*offer).clone())
-                    .await;
+                if dbtx
+                    .insert_entry(&OfferKey(offer.hash), &(*offer).clone())
+                    .await
+                    .is_some()
+                {
+                    // Technically the error isn't due to a duplicate encrypted preimage but due to
+                    // a duplicate payment hash, practically it's the same problem though: re-using
+                    // the invoice key. Since we can't eaily extend the error enum we just re-use
+                    // this variant.
+                    return Err(LightningOutputError::DuplicateEncryptedPreimage);
+                }
 
                 dbtx.on_commit(|| {
                     LN_INCOMING_OFFER.inc();
```

### modules/fedimint-ln-tests/tests/tests.rs
```diff
@@ -3,11 +3,15 @@ use std::sync::Arc;
 
 use anyhow::bail;
 use assert_matches::assert_matches;
+use bitcoin_hashes::{Hash, sha256};
+use fedimint_client::transaction::{
+    ClientOutput, ClientOutputBundle, TransactionBuilder, TxSubmissionStates, TxSubmissionStatesSM,
+};
 use fedimint_client::{Client, ClientHandleArc};
 use fedimint_client_module::oplog::OperationLogEntry;
-use fedimint_core::core::OperationId;
+use fedimint_core::core::{IntoDynInstance, OperationId};
 use fedimint_core::module::CommonModuleInit as _;
-use fedimint_core::util::NextOrPending;
+use fedimint_core::util::{BoxStream, NextOrPending};
 use fedimint_core::{Amount, sats, secp256k1};
 use fedimint_dummy_client::{DummyClientInit, DummyClientModule};
 use fedimint_dummy_common::config::DummyGenParams;
@@ -16,13 +20,16 @@ use fedimint_ln_client::{
     InternalPayState, LightningClientInit, LightningClientModule, LightningOperationMeta,
     LnPayState, LnReceiveState, MockGatewayConnection, OutgoingLightningPayment, PayType,
 };
-use fedimint_ln_common::LightningCommonInit;
 use fedimint_ln_common::config::LightningGenParams;
+use fedimint_ln_common::contracts::incoming::IncomingContractOffer;
+use fedimint_ln_common::contracts::{EncryptedPreimage, PreimageKey};
+use fedimint_ln_common::{LightningCommonInit, LightningOutput};
 use fedimint_ln_server::LightningInit;
 use fedimint_testing::federation::FederationTest;
 use fedimint_testing::fixtures::Fixtures;
 use fedimint_testing::ln::FakeLightningTest;
 use fedimint_testing::{Gateway, LightningModuleMode};
+use futures::StreamExt;
 use lightning_invoice::{Bolt11Invoice, Bolt11InvoiceDescription, Description};
 use rand::rngs::OsRng;
 use secp256k1::Keypair;
@@ -621,6 +628,97 @@ async fn rejects_wrong_network_invoice() -> anyhow::Result<()> {
     Ok(())
 }
 
+#[tokio::test(flavor = "multi_thread")]
+async fn server_rejects_duplicate_offer() -> anyhow::Result<()> {
+    let fixtures = fixtures();
+    let fed = fixtures.new_fed_degraded().await;
+    let client1 = fed.new_client().await;
+    let ln_module = client1.get_first_module::<LightningClientModule>()?;
+
+    let threshold_pub_key = ln_module.cfg.threshold_pub_key;
+
+    let encrypted_preimage_1 = EncryptedPreimage::new(&PreimageKey([0x42; 33]), &threshold_pub_key);
+    let offer_output_1 = LightningOutput::new_v0_offer(IncomingContractOffer {
+        amount: sats(1000),
+        hash: sha256::Hash::hash(&[]),
+        encrypted_preimage: encrypted_preimage_1.clone(),
+        expiry_time: None,
+    });
+    let transaction_builder_1 = TransactionBuilder::new().with_outputs(
+        ClientOutputBundle::new_no_sm(vec![ClientOutput {
+            output: offer_output_1,
+            amount: Amount::ZERO,
+        }])
+        .into_dyn(ln_module.id),
+    );
+    let operation_id_1 = OperationId::new_random();
+
+    let encrypted_preimage_2 = EncryptedPreimage::new(&PreimageKey([0x43; 33]), &threshold_pub_key);
+    let offer_output_2 = LightningOutput::new_v0_offer(IncomingContractOffer {
+        amount: sats(1000),
+        hash: sha256::Hash::hash(&[]),
+        encrypted_preimage: encrypted_preimage_2.clone(),
+        expiry_time: None,
+    });
+    let transaction_builder_2 = TransactionBuilder::new().with_outputs(
+        ClientOutputBundle::new_no_sm(vec![ClientOutput {
+            output: offer_output_2,
+            amount: Amount::ZERO,
+        }])
+        .into_dyn(ln_module.id),
+    );
+    let operation_id_2 = OperationId::new_random();
+
+    assert_ne!(
+        encrypted_preimage_1, encrypted_preimage_2,
+        "The two should have different encrypted preimages"
+    );
+
+    async fn await_tx_accepted(
+        tx_updates: BoxStream<'static, TxSubmissionStatesSM>,
+    ) -> Result<(), String> {
+        tx_updates
+            .filter_map(|tx_update| {
+                std::future::ready(match tx_update.state {
+                    TxSubmissionStates::Accepted(_) => Some(Ok(())),
+                    TxSubmissionStates::Rejected(_, submit_error) => Some(Err(submit_error)),
+                    _ => None,
+                })
+            })
+            .next()
+            .await
+            .expect("Tx either accepted or rejected")
+    }
+
+    client1
+        .finalize_and_submit_transaction(operation_id_1, "", |_| (), transaction_builder_1)
+        .await
+        .expect("Tx finalization failed");
+    await_tx_accepted(
+        client1
+            .transaction_updates(operation_id_1)
+            .await
+            .update_stream,
+    )
+    .await
+    .expect("First offer should be accepted");
+
+    client1
+        .finalize_and_submit_transaction(operation_id_2, "", |_| (), transaction_builder_2)
+        .await
+        .expect("Tx finalization failed");
+    await_tx_accepted(
+        client1
+            .transaction_updates(operation_id_2)
+            .await
+            .update_stream,
+    )
+    .await
+    .expect_err("Second offer should be rejected");
+
+    Ok(())
+}
+
 #[cfg(test)]
 mod fedimint_migration_tests {
     use std::str::FromStr;
```
