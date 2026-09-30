# [?] fix: panic when claiming an uneconomical contract

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-10
Source: https://github.com/fedimint/fedimint/commit/f675cd3ad02561962eccbf0012955ba819840d13
Type: security-commit

## Details
fix: panic when claiming an uneconomical contract

## Patch
### modules/fedimint-gwv2-client/src/receive_sm.rs
```diff
@@ -11,6 +11,7 @@ use fedimint_core::core::OperationId;
 use fedimint_core::encoding::{Decodable, Encodable};
 use fedimint_core::module::{Amounts, ApiRequestErased};
 use fedimint_core::secp256k1::Keypair;
+use fedimint_core::util::FmtCompactAnyhow;
 use fedimint_core::{NumPeersExt, OutPoint, PeerId};
 use fedimint_lnv2_common::contracts::IncomingContract;
 use fedimint_lnv2_common::endpoint_constants::DECRYPTION_KEY_SHARE_ENDPOINT;
@@ -274,16 +275,49 @@ impl ReceiveStateMachine {
             keys: vec![old_state.common.refund_keypair],
         };
 
-        let outpoints = global_context
+        let outpoints = match global_context
             .claim_inputs(
                 dbtx,
                 // The input of the refund tx is managed by this state machine
                 ClientInputBundle::new_no_sm(vec![client_input]),
             )
             .await
-            .expect("Cannot claim input, additional funding needed")
-            .into_iter()
-            .collect();
+        {
+            Ok(outpoints) => outpoints.into_iter().collect(),
+            // The contract is the refund transaction's only input, so this fails
+            // exactly when the federation's fees exceed the contract, leaving nothing
+            // to refund. The gateway keeps the lightning payment it already received
+            // for it, so the loss is bounded by the contract; a panic here would not
+            // be, because it runs in the executor and would take down every payment
+            // this gateway handles for the federation, on every restart.
+            Err(err) => {
+                warn!(
+                    target: LOG_CLIENT_MODULE_GW,
+                    err = %err.fmt_compact_anyhow(),
+                    amount = %old_state.common.contract.commitment.amount,
+                    "Not refunding incoming contract, its amount does not cover the refund fee"
+                );
+
+                client_ctx
+                    .module
+                    .client_ctx
+                    .log_event(
+                        &mut dbtx.module_tx(),
+                        IncomingPaymentFailed {
+                            payment_image: old_state
+                                .common
+                                .contract
+                                .commitment
+                                .payment_image
+                                .clone(),
+                            error: "Contract does not cover the refund fee".to_string(),
+                        },
+                    )
+                    .await;
+
+                return old_state.update(ReceiveSMState::Failure);
+            }
+        };
 
         client_ctx
             .module
```

### modules/fedimint-lnv2-client/src/lib.rs
```diff
@@ -52,9 +52,9 @@ use fedimint_lnv2_common::gateway_api::{
 };
 use fedimint_lnv2_common::{
     Bolt11InvoiceDescription, GatewayApi, KIND, LightningCommonInit, LightningInvoice,
-    LightningModuleTypes, LightningOutput, LightningOutputV0, MINIMUM_INCOMING_CONTRACT_AMOUNT,
-    lnurl, tweak,
+    LightningModuleTypes, LightningOutput, LightningOutputV0, lnurl, tweak,
 };
+use fedimint_logging::LOG_CLIENT_MODULE_LNV2;
 use futures::StreamExt;
 use lightning_invoice::{Bolt11Invoice, Currency};
 use secp256k1::{Keypair, PublicKey, Scalar, SecretKey, ecdh};
@@ -203,6 +203,10 @@ pub enum ReceiveOperationState {
     Claimed,
     /// Either a programming error has occurred or the federation is malicious.
     Failure,
+    /// The contract is worth less than the federation charges to claim it, so
+    /// it was left unclaimed. Reachable without any payment request of ours:
+    /// anyone can address an incoming contract to a published lnurl key.
+    Uneconomical,
 }
 
 /// The final state of an operation receiving a payment over lightning.
@@ -214,6 +218,9 @@ pub enum FinalReceiveOperationState {
     Claimed,
     /// Either a programming error has occurred or the federation is malicious.
     Failure,
+    /// The contract is worth less than the federation charges to claim it, so
+    /// it was left unclaimed.
+    Uneconomical,
 }
 
 pub type ReceiveResult = Result<(Bolt11Invoice, OperationId), ReceiveError>;
@@ -895,6 +902,23 @@ impl LightningClientModule {
             .await
     }
 
+    /// Whether an incoming contract worth `amount` is worth claiming, i.e.
+    /// whether claiming it would leave the wallet better off than leaving it.
+    ///
+    /// This is the computed counterpart of a fixed dust limit: it prices the
+    /// actual claim - the lightning input fee at this federation's fee
+    /// consensus, the change the primary module has to mint, and the
+    /// sub-denomination remainder that cannot be minted at all - rather than
+    /// assuming a floor. A quote that fails outright is the same verdict: the
+    /// claim spends the contract as the transaction's only input, so a fee
+    /// larger than the contract leaves a transaction that cannot be balanced.
+    async fn is_worth_claiming(&self, amount: Amount) -> bool {
+        match self.receive_fee_quote(amount).await {
+            Ok(quote) => quote.total().get_bitcoin() < amount,
+            Err(_) => false,
+        }
+    }
+
     /// Computes the federation fee a `send` funding an outgoing contract worth
     /// `amount` would incur, without submitting anything.
     ///
@@ -1035,7 +1059,10 @@ impl LightningClientModule {
 
         let contract_amount = routing_info.receive_fee.subtract_from(amount.msats);
 
-        if contract_amount < MINIMUM_INCOMING_CONTRACT_AMOUNT {
+        // Quoting the claim against this federation's fee consensus is exact, where a
+        // fixed floor is either too permissive or too strict depending on how the
+        // federation is configured.
+        if !self.is_worth_claiming(contract_amount).await {
             return Err(ReceiveError::AmountTooSmall);
         }
 
@@ -1168,7 +1195,8 @@ impl LightningClientModule {
                 ReceiveOperationState::Pending | ReceiveOperationState::Claiming => false,
                 ReceiveOperationState::Expired
                 | ReceiveOperationState::Claimed
-                | ReceiveOperationState::Failure => true,
+                | ReceiveOperationState::Failure
+                | ReceiveOperationState::Uneconomical => true,
             }, move || {
             stream! {
                 loop {
@@ -1189,6 +1217,10 @@ impl LightningClientModule {
                                 yield ReceiveOperationState::Expired;
                                 return;
                             }
+                            ReceiveSMState::Uneconomical => {
+                                yield ReceiveOperationState::Uneconomical;
+                                return;
+                            }
                         }
                     }
                 }
@@ -1219,6 +1251,9 @@ impl LightningClientModule {
                 ReceiveOperationState::Failure => {
                     final_state = Some(FinalReceiveOperationState::Failure);
                 }
+                ReceiveOperationState::Uneconomical => {
+                    final_state = Some(FinalReceiveOperationState::Uneconomical);
+                }
                 _ => {}
             }
         }
@@ -1309,6 +1344,28 @@ impl LightningClientModule {
             .await;
 
         for contract in &contracts {
+            // The stream carries every incoming contract the federation funded, and
+            // anyone can address one to a published lnurl key. Check that it is ours
+            // before quoting - recovering the keys is local arithmetic, the quote
+            // reads the wallet - and skip the contracts the claim fee would swallow,
+            // so that unsolicited dust never becomes an operation in the first place.
+            if self
+                .recover_contract_keys(self.lnurl_keypair.secret_key(), contract)
+                .is_none()
+            {
+                continue;
+            }
+
+            if !self.is_worth_claiming(contract.commitment.amount).await {
+                warn!(
+                    target: LOG_CLIENT_MODULE_LNV2,
+                    amount = %contract.commitment.amount,
+                    "Ignoring incoming contract, its amount does not cover the claim fee"
+                );
+
+                continue;
+            }
+
             if let Some(operation_id) = self
                 .receive_incoming_contract(
                     self.lnurl_keypair.secret_key(),
```

### modules/fedimint-lnv2-client/src/receive_sm.rs
```diff
@@ -5,12 +5,13 @@ use fedimint_core::core::OperationId;
 use fedimint_core::encoding::{Decodable, Encodable};
 use fedimint_core::module::Amounts;
 use fedimint_core::secp256k1::Keypair;
+use fedimint_core::util::FmtCompactAnyhow;
 use fedimint_core::{Amount, OutPoint};
 use fedimint_lnv2_common::contracts::{IncomingContract, fee_from_expiration};
 use fedimint_lnv2_common::{LightningInput, LightningInputV0};
 use fedimint_logging::LOG_CLIENT_MODULE_LNV2;
 use tpe::AggregateDecryptionKey;
-use tracing::instrument;
+use tracing::{instrument, warn};
 
 use crate::api::LightningFederationApi;
 use crate::events::ReceivePaymentEvent;
@@ -44,6 +45,11 @@ pub enum ReceiveSMState {
     Pending,
     Claiming(Vec<OutPoint>),
     Expired,
+    /// Claiming the contract costs more in federation fees than the contract is
+    /// worth, so there is nothing to recover. Terminal: the verdict follows
+    /// from the contract amount and the federation's fee consensus, so waiting
+    /// does not change it.
+    Uneconomical,
 }
 
 #[cfg_attr(doc, aquamarine::aquamarine)]
@@ -55,6 +61,7 @@ pub enum ReceiveSMState {
 ///
 ///     Pending -- incoming contract is confirmed --> Claiming
 ///     Pending -- decryption contract expires --> Expired
+///     Pending -- claim fee exceeds the contract --> Uneconomical
 /// ```
 impl State for ReceiveStateMachine {
     type ModuleContext = LightningClientContext;
@@ -82,7 +89,9 @@ impl State for ReceiveStateMachine {
                     },
                 )]
             }
-            ReceiveSMState::Claiming(..) | ReceiveSMState::Expired => {
+            ReceiveSMState::Claiming(..)
+            | ReceiveSMState::Expired
+            | ReceiveSMState::Uneconomical => {
                 vec![]
             }
         }
@@ -128,10 +137,29 @@ impl ReceiveStateMachine {
             keys: vec![old_state.common.claim_keypair],
         };
 
-        let change_range = global_context
+        let change_range = match global_context
             .claim_inputs(dbtx, ClientInputBundle::new_no_sm(vec![client_input]))
             .await
-            .expect("Cannot claim input, additional funding needed");
+        {
+            Ok(change_range) => change_range,
+            // The contract is the transaction's only input, so the primary module has
+            // to top the transaction up exactly when the federation's fees exceed the
+            // contract - and a wallet with nothing in it cannot top it up at all.
+            // Anyone can address an incoming contract to a published lnurl key, so
+            // this has to end in a state rather than a panic: the executor polls this
+            // transition, a panic in it takes the whole client down, and because
+            // nothing commits it would do so again on every restart.
+            Err(err) => {
+                warn!(
+                    target: LOG_CLIENT_MODULE_LNV2,
+                    err = %err.fmt_compact_anyhow(),
+                    amount = %old_state.common.contract.commitment.amount,
+                    "Not claiming incoming contract, its amount does not cover the claim fee"
+                );
+
+                return old_state.update(ReceiveSMState::Uneconomical);
+            }
+        };
 
         // The event reports the invoice amount and the gateway fee separately.
         // Manual receives carry the invoice in their operation meta, so the fee
```

### modules/fedimint-lnv2-tests/tests/tests.rs
```diff
@@ -3,32 +3,45 @@ mod mock;
 use std::pin::pin;
 use std::sync::Arc;
 
+use anyhow::Context as _;
 use async_stream::stream;
+use bitcoin::hashes::{Hash as _, sha256};
 use fedimint_client::ClientHandleArc;
-use fedimint_client::transaction::{ClientInput, ClientInputBundle, TransactionBuilder};
+use fedimint_client::transaction::{
+    ClientInput, ClientInputBundle, ClientOutput, ClientOutputBundle, TransactionBuilder,
+};
 use fedimint_client_module::module::ClientModule;
+use fedimint_core::base32::{FEDIMINT_PREFIX, decode_prefixed};
 use fedimint_core::core::{IntoDynInstance, OperationId};
+use fedimint_core::encoding::Encodable as _;
 use fedimint_core::module::{AmountUnit, Amounts};
-use fedimint_core::util::NextOrPending as _;
-use fedimint_core::{Amount, OutPoint, sats};
+use fedimint_core::secp256k1::{PublicKey, Scalar};
+use fedimint_core::time::duration_since_epoch;
+use fedimint_core::util::{NextOrPending as _, SafeUrl, backoff_util, retry};
+use fedimint_core::{Amount, OutPoint, msats, sats, secp256k1};
 use fedimint_dummy_client::{DummyClientInit, DummyClientModule};
 use fedimint_dummy_server::DummyInit;
 use fedimint_eventlog::{Event, EventLogEntry, EventLogId};
+use fedimint_lnurl::parse_lnurl;
 use fedimint_lnv2_client::events::{
     ReceivePaymentEvent, SendPaymentEvent, SendPaymentStatus, SendPaymentUpdateEvent,
 };
 use fedimint_lnv2_client::{
-    InvoiceSendStatus, LightningClientInit, LightningClientModule, LightningOperationMeta,
-    ReceiveOperationState, SendOperationState, SendPaymentError,
+    FinalReceiveOperationState, InvoiceSendStatus, LightningClientInit, LightningClientModule,
+    LightningOperationMeta, ReceiveOperationState, SendOperationState, SendPaymentError,
 };
+use fedimint_lnv2_common::contracts::{IncomingContract, PaymentImage};
+use fedimint_lnv2_common::lnurl::LnurlRequest;
 use fedimint_lnv2_common::{
-    Bolt11InvoiceDescription, KIND, LightningInput, LightningInputV0, OutgoingWitness,
+    Bolt11InvoiceDescription, KIND, LightningInput, LightningInputV0, LightningOutput,
+    LightningOutputV0, OutgoingWitness, tweak,
 };
 use fedimint_lnv2_server::LightningInit;
 use fedimint_logging::LOG_TEST;
 use fedimint_testing::fixtures::Fixtures;
 use futures::StreamExt;
 use serde_json::Value;
+use tpe::AggregatePublicKey;
 use tracing::warn;
 
 use crate::mock::{MOCK_INVOICE_PREIMAGE, MockGatewayConnection};
@@ -427,6 +440,158 @@ async fn receive_operation_expires() -> anyhow::Result<()> {
     Ok(())
 }
 
+/// Builds an incoming contract addressed to `recipient_pk`, the way a sender
+/// does: the claim key is derived from the recipient's published static key and
+/// a fresh ephemeral key, so anyone who knows that static key can address one.
+fn incoming_contract_for(
+    recipient_pk: PublicKey,
+    aggregate_pk: AggregatePublicKey,
+    amount: Amount,
+) -> IncomingContract {
+    let (ephemeral_tweak, ephemeral_pk) = tweak::generate(recipient_pk);
+
+    let encryption_seed = ephemeral_tweak
+        .consensus_hash::<sha256::Hash>()
+        .to_byte_array();
+
+    let preimage = encryption_seed
+        .consensus_hash::<sha256::Hash>()
+        .to_byte_array();
+
+    let claim_pk = recipient_pk
+        .mul_tweak(
+            secp256k1::SECP256K1,
+            &Scalar::from_be_bytes(ephemeral_tweak).expect("Within curve order"),
+        )
+        .expect("Tweak is valid");
+
+    IncomingContract::new(
+        aggregate_pk,
+        encryption_seed,
+        preimage,
+        PaymentImage::Hash(preimage.consensus_hash()),
+        amount,
+        duration_since_epoch().as_secs().saturating_add(3600),
+        claim_pk,
+        mock::gateway_keypair().public_key(),
+        ephemeral_pk,
+    )
+}
+
+/// Funds `contract` straight from `funder`'s balance. No gateway is involved:
+/// consensus funds an incoming contract of any amount, so this is what an
+/// attacker with a little ecash can do to anyone whose static key they know.
+async fn fund_incoming_contract(
+    funder: &ClientHandleArc,
+    contract: &IncomingContract,
+) -> anyhow::Result<()> {
+    let lnv2_module_id = funder
+        .get_first_instance(&LightningClientModule::kind())
+        .expect("lnv2 module not found");
+
+    funder
+        .finalize_and_submit_transaction(
+            OperationId::new_random(),
+            "Funding an incoming contract",
+            |_| (),
+            TransactionBuilder::new().with_outputs(
+                ClientOutputBundle::new_no_sm(vec![ClientOutput {
+                    output: LightningOutput::V0(LightningOutputV0::Incoming(contract.clone())),
+                    amounts: Amounts::new_bitcoin(contract.commitment.amount),
+                }])
+                .into_dyn(lnv2_module_id),
+            ),
+        )
+        .await?;
+
+    Ok(())
+}
+
+/// A contract worth less than the fee to claim it must be left alone rather
+/// than driven into a claim that cannot be funded.
+///
+/// Anyone can address an incoming contract to a published lnurl key, and
+/// consensus funds one of any amount, so the amount is entirely the sender's
+/// choice. The client used to start a claim for it regardless; with nothing in
+/// the wallet to cover the shortfall the claim panicked inside the state
+/// machine executor, and since nothing commits it panicked again on every
+/// restart — a wallet bricked for the price of a few sats.
+///
+/// The victim here holds no balance at all, which is the state a fresh wallet
+/// publishing an address is in.
+#[tokio::test(flavor = "multi_thread")]
+async fn unsolicited_dust_contract_does_not_wedge_the_client() -> anyhow::Result<()> {
+    let fixtures = fixtures();
+    let fed = fixtures.new_fed_degraded().await;
+    let victim = fed.new_client().await;
+    let attacker = fed.new_client().await;
+
+    attacker
+        .get_first_module::<DummyClientModule>()?
+        .mock_receive(sats(10_000), AmountUnit::BITCOIN)
+        .await?;
+
+    // Everything the attacker needs is in what the victim publishes.
+    let lnurl = victim
+        .get_first_module::<LightningClientModule>()?
+        .generate_lnurl(
+            SafeUrl::parse("https://recurring.xyz/").expect("Valid Url"),
+            Some(mock::gateway()),
+        )
+        .await?;
+    let url = parse_lnurl(&lnurl).expect("Generated lnurl decodes");
+    let payload = url.rsplit("pay/").next().expect("Url carries a payload");
+    let request = decode_prefixed::<LnurlRequest>(FEDIMINT_PREFIX, payload)?;
+
+    let dust = incoming_contract_for(request.recipient_pk, request.aggregate_pk, msats(1));
+    fund_incoming_contract(&attacker, &dust).await?;
+
+    // A second, claimable contract behind the dust one. Waiting for its operation
+    // proves the victim processed past the dust rather than dying on it: the
+    // lnurl task handles the stream in order.
+    let claimable = incoming_contract_for(
+        request.recipient_pk,
+        request.aggregate_pk,
+        Amount::from_sats(100),
+    );
+    fund_incoming_contract(&attacker, &claimable).await?;
+
+    let claimable_operation = OperationId::from_encodable(&claimable);
+    retry(
+        "waiting for the claimable contract to be picked up",
+        backoff_util::aggressive_backoff(),
+        || async {
+            victim
+                .operation_log()
+                .get_operation(claimable_operation)
+                .await
+                .context("Claimable contract was not picked up")
+        },
+    )
+    .await?;
+
+    // The dust never became an operation at all.
+    assert!(
+        victim
+            .operation_log()
+            .get_operation(OperationId::from_encodable(&dust))
+            .await
+            .is_none(),
+        "Dust contract should have been ignored"
+    );
+
+    // And the client is still running: it claimed the contract that was worth it.
+    assert_eq!(
+        victim
+            .get_first_module::<LightningClientModule>()?
+            .await_final_receive_operation_state(claimable_operation)
+            .await?,
+        FinalReceiveOperationState::Claimed
+    );
+
+    Ok(())
+}
+
 #[tokio::test(flavor = "multi_thread")]
 async fn rejects_wrong_network_invoice() -> anyhow::Result<()> {
     let fixtures = fixtures();
```
