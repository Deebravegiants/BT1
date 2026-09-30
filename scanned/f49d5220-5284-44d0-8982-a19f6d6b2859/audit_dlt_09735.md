# [?] fix(gw): dont panic on amountless invoice (#8984)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-08
Source: https://github.com/fedimint/fedimint/commit/f054a825535b6f8f67f781ef8bee2d0b867c8a40
Type: security-commit

## Details
fix(gw): dont panic on amountless invoice (#8984)

Adds check to the gateway to check for the amount and fail (instead of
panic) if given an amountless invoice.

## Patch
### gateway/fedimint-gateway-server/src/lib.rs
```diff
@@ -115,7 +115,7 @@ use fedimint_lnv2_common::gateway_api::{
     CreateBolt11InvoicePayload, PaymentFee, RoutingInfo, SendPaymentPayload,
 };
 use fedimint_logging::LOG_GATEWAY;
-use fedimint_mint_client::{MintClientInit, MintClientModule, OOBNotes};
+use fedimint_mint_client::{MintClientInit, MintClientModule, OOBNotes, ReissueExternalNotesState};
 use fedimint_mintv2_client::{
     MintClientInit as MintV2ClientInit, MintClientModule as MintV2ClientModule,
 };
@@ -1551,16 +1551,34 @@ impl Gateway {
                 let mut updates = mint
                     .subscribe_reissue_external_notes(operation_id)
                     .await
-                    .unwrap()
+                    .map_err(|e| PublicGatewayError::ReceiveEcashError {
+                        failure_reason: format!("Could not subscribe to reissue operation: {e}"),
+                    })?
                     .into_stream();
 
+                // Only `Done` and `Failed` are terminal for this stream. Ending on
+                // `Created` or `Issuing` means the outputs were never finalized, so
+                // their blind signatures were never verified, and reporting the
+                // notes' claimed amount would credit e-cash the gateway does not
+                // hold.
+                let mut reissued = false;
                 while let Some(update) = updates.next().await {
-                    if let fedimint_mint_client::ReissueExternalNotesState::Failed(e) = update {
-                        return Err(PublicGatewayError::ReceiveEcashError {
-                            failure_reason: e.clone(),
-                        });
+                    match update {
+                        ReissueExternalNotesState::Failed(failure_reason) => {
+                            return Err(PublicGatewayError::ReceiveEcashError { failure_reason });
+                        }
+                        ReissueExternalNotesState::Done => reissued = true,
+                        ReissueExternalNotesState::Created | ReissueExternalNotesState::Issuing => {
+                        }
                     }
                 }
+
+                if !reissued {
+                    return Err(PublicGatewayError::ReceiveEcashError {
+                        failure_reason: "Reissue operation ended before the notes were reissued"
+                            .to_string(),
+                    });
+                }
             }
 
             Ok(ReceiveEcashResponse { amount })
```

### gateway/fedimint-gateway-server/tests/tests.rs
```diff
@@ -46,7 +46,9 @@ use fedimint_ln_client::{
 };
 use fedimint_ln_common::contracts::incoming::IncomingContractOffer;
 use fedimint_ln_common::contracts::outgoing::OutgoingContractAccount;
-use fedimint_ln_common::contracts::{EncryptedPreimage, FundedContract, Preimage, PreimageKey};
+use fedimint_ln_common::contracts::{
+    ContractId, EncryptedPreimage, FundedContract, Preimage, PreimageKey,
+};
 use fedimint_ln_common::{LightningGateway, LightningInput, LightningOutput, PrunedInvoice};
 use fedimint_ln_server::LightningInit;
 use fedimint_lnv2_common::contracts::{IncomingContract, OutgoingContract, PaymentImage};
@@ -60,8 +62,11 @@ use fedimint_testing::ln::FakeLightningTest;
 use fedimint_unknown_server::UnknownInit;
 use futures::Future;
 use itertools::Itertools;
-use lightning_invoice::{Bolt11Invoice, Bolt11InvoiceDescription, Description, RoutingFees};
-use secp256k1::{Keypair, PublicKey};
+use lightning_invoice::{
+    Bolt11Invoice, Bolt11InvoiceDescription, Currency, Description, InvoiceBuilder, PaymentSecret,
+    RoutingFees,
+};
+use secp256k1::{Keypair, PublicKey, SecretKey};
 use tpe::G1Affine;
 use tracing::info;
 
@@ -872,6 +877,58 @@ async fn test_gateway_cannot_pay_expired_invoice() -> anyhow::Result<()> {
     .await
 }
 
+/// `/pay_invoice` is unauthenticated and its `payment_data` is caller-supplied,
+/// so an amountless BOLT11 invoice reaches `gateway_pay_bolt11_invoice`
+/// directly. It must be rejected as an error rather than panicking: the
+/// gateway's iroh dispatch spawns handlers on the root task group, where a
+/// panic takes down the whole `gatewayd` process.
+///
+/// No contract has to exist for this — `contract_id` only seeds the
+/// `OperationId`, and nothing looks it up before the amount is read.
+#[tokio::test(flavor = "multi_thread")]
+async fn test_gateway_rejects_amountless_invoice() -> anyhow::Result<()> {
+    single_federation_test(|gateway, _, fed, user_client, _| async move {
+        let gateway_client = gateway.select_client(fed.id()).await?.into_value();
+
+        let ctx = secp256k1::Secp256k1::new();
+        let keypair = Keypair::from_secret_key(&ctx, &SecretKey::from_slice(&[1; 32])?);
+        let amountless_invoice = InvoiceBuilder::new(Currency::Regtest)
+            .payee_pub_key(keypair.public_key())
+            .description(String::new())
+            .payment_hash(sha256(&[0; 32]))
+            .current_timestamp()
+            .min_final_cltv_expiry_delta(0)
+            .payment_secret(PaymentSecret([0; 32]))
+            .build_signed(|m| ctx.sign_ecdsa_recoverable(m, &SecretKey::from_keypair(&keypair)))?;
+        assert!(
+            amountless_invoice.amount_milli_satoshis().is_none(),
+            "Invoice must carry no amount for this test to be meaningful"
+        );
+
+        let payload = PayInvoicePayload {
+            federation_id: user_client.federation_id(),
+            contract_id: ContractId::from_raw_hash(sha256(&[42; 32])),
+            payment_data: PaymentData::Invoice(amountless_invoice),
+            preimage_auth: Hash::hash(&[0; 32]),
+        };
+
+        let error = gateway_client
+            .get_first_module::<GatewayClientModule>()?
+            .gateway_pay_bolt11_invoice(payload)
+            .await
+            .expect_err("Amountless invoice should be rejected");
+        assert!(
+            error
+                .downcast_ref::<OutgoingContractError>()
+                .is_some_and(|error| matches!(error, OutgoingContractError::InvoiceMissingAmount)),
+            "Expected InvoiceMissingAmount, got: {error}"
+        );
+
+        Ok(())
+    })
+    .await
+}
+
 #[tokio::test(flavor = "multi_thread")]
 async fn test_gateway_executes_swaps_between_connected_federations() -> anyhow::Result<()> {
     multi_federation_test(|gateway, fed1, fed2, _| async move {
```

### modules/fedimint-gw-client/src/lib.rs
```diff
@@ -69,7 +69,7 @@ use tracing::{debug, error, info, warn};
 use self::complete::GatewayCompleteStateMachine;
 use self::pay::{
     GatewayPayCommon, GatewayPayInvoice, GatewayPayStateMachine, GatewayPayStates,
-    OutgoingPaymentError,
+    OutgoingContractError, OutgoingPaymentError,
 };
 
 /// The high-level state of a reissue operation started with
@@ -710,6 +710,17 @@ impl GatewayClientModule {
         pay_invoice_payload: PayInvoicePayload,
     ) -> anyhow::Result<OperationId> {
         let payload = pay_invoice_payload.clone();
+
+        // `payment_data` is caller-supplied on the unauthenticated `/pay_invoice`
+        // route, so an amountless BOLT11 reaches us here. The state machine
+        // rejects it in `validate_outgoing_account`, but that runs only after
+        // this function has already recorded the invoice amount, so the amount
+        // has to be resolved before any of that work starts.
+        let invoice_amount = pay_invoice_payload
+            .payment_data
+            .amount()
+            .ok_or(OutgoingContractError::InvoiceMissingAmount)?;
+
         self.lightning_manager
             .verify_pruned_invoice(pay_invoice_payload.payment_data)
             .await?;
@@ -722,7 +733,7 @@ impl GatewayClientModule {
 
                         self.client_ctx.log_event(dbtx, OutgoingPaymentStarted {
                             contract_id: payload.contract_id,
-                            invoice_amount: payload.payment_data.amount().expect("LNv1 invoices should have an amount"),
+                            invoice_amount,
                             operation_id,
                         }).await;
 
```
