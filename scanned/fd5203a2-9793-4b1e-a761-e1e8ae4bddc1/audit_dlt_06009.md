# [?] fix(gateway): return errors instead of panicking on unauthenticated lnv2 routes

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/804fc070b8556381f3b5caaa8eab34c2d7f7e857
Type: security-commit

## Details
fix(gateway): return errors instead of panicking on unauthenticated lnv2 routes

`routing_info`, `send_payment` and `create_bolt11_invoice` are registered
with `is_authenticated = false`, and iroh dispatch consults only that
flag, so anyone who can reach the gateway can call them for any
federation it serves. All three resolved the LNv2 client module with
`expect("Must have client module")`.

A federation only has to offer one of the two lightning modules --
`check_federation_network` rejects a federation only when both are
absent -- so an LNv1-only federation is a normal configuration for which
that `expect` always fires. Over iroh a panicking handler exits the
gateway process, and deployments restart it, so this is a boot loop
rather than a single crash.

`public_key_v2` now reports a missing LNv2 module as `None`, which its
two callers already handle, and `send_payment_v2` maps it to an outgoing
payment error. `create_bolt11_invoice_v2` needs no separate change: it
reaches the module only through `routing_info_v2`.

`gateway_pay_bolt11_invoice` had the same shape on the LNv1 side:
`expect("LNv1 invoices should have an amount")` while building the
`OutgoingPaymentStarted` log entry. `validate_outgoing_account` already
reports an amountless invoice as `InvoiceMissingAmount`, but only once
the state machine is under way, which is strictly after the log entry.
Do the check up front and return that same error.

`send_payment_v2` becomes `pub` so the regression test can reach it, next
to the already-public `routing_info_v2`. Both are public API surface in
every sense that matters -- they are served unauthenticated.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9

## Patch
### gateway/fedimint-gateway-server/src/lib.rs
```diff
@@ -3118,13 +3118,14 @@ impl Gateway {
             .read()
             .await
             .client(federation_id)
-            .map(|client| {
+            .and_then(|client| {
+                // A federation only has to offer one of the two lightning modules, so a
+                // client we serve over LNv1 may well have no LNv2 module at all.
                 client
                     .value()
                     .get_first_module::<GatewayClientModuleV2>()
-                    .expect("Must have client module")
-                    .keypair
-                    .public_key()
+                    .ok()
+                    .map(|module| module.keypair.public_key())
             })
     }
 
@@ -3176,15 +3177,19 @@ impl Gateway {
 
     /// Instructs this gateway to pay a Lightning network invoice via the LNv2
     /// protocol.
-    async fn send_payment_v2(
+    pub async fn send_payment_v2(
         &self,
         payload: SendPaymentPayload,
     ) -> Result<std::result::Result<[u8; 32], Signature>> {
-        self.select_client(payload.federation_id)
-            .await?
+        let client = self.select_client(payload.federation_id).await?;
+        // A federation only has to offer one of the two lightning modules, so a
+        // client we serve over LNv1 may well have no LNv2 module at all.
+        let module = client
             .value()
             .get_first_module::<GatewayClientModuleV2>()
-            .expect("Must have client module")
+            .map_err(|err| PublicGatewayError::LNv2(LNv2Error::OutgoingPayment(err)))?;
+
+        module
             .send_payment(payload)
             .await
             .map_err(LNv2Error::OutgoingPayment)
```

### gateway/fedimint-gateway-server/tests/tests.rs
```diff
@@ -19,7 +19,7 @@ use fedimint_core::module::{AmountUnit, Amounts};
 use fedimint_core::task::{TaskGroup, sleep_in_test, timeout};
 use fedimint_core::time::now;
 use fedimint_core::util::{NextOrPending, backoff_util, retry};
-use fedimint_core::{Amount, OutPoint, msats, sats, secp256k1};
+use fedimint_core::{Amount, OutPoint, TransactionId, msats, sats, secp256k1};
 use fedimint_dummy_client::{DummyClientInit, DummyClientModule};
 use fedimint_dummy_server::DummyInit;
 use fedimint_eventlog::Event;
@@ -54,8 +54,9 @@ use fedimint_ln_common::contracts::{
 };
 use fedimint_ln_common::{LightningGateway, LightningInput, LightningOutput, PrunedInvoice};
 use fedimint_ln_server::LightningInit;
+use fedimint_lnv2_common::LightningInvoice;
 use fedimint_lnv2_common::contracts::{IncomingContract, OutgoingContract, PaymentImage};
-use fedimint_lnv2_common::gateway_api::PaymentFee;
+use fedimint_lnv2_common::gateway_api::{PaymentFee, SendPaymentPayload};
 use fedimint_logging::LOG_TEST;
 use fedimint_testing::btc::BitcoinTest;
 use fedimint_testing::db::BYTE_33;
@@ -1853,3 +1854,100 @@ async fn gateway_read_payment_log() -> anyhow::Result<()> {
 
     Ok(())
 }
+
+/// A federation only has to offer one of the two lightning modules, so a
+/// gateway routinely serves federations with an LNv1 module and no LNv2 one.
+fn lnv1_only_fixtures() -> Fixtures {
+    Fixtures::new_primary(DummyClientInit, DummyInit)
+        .with_server_only_module(UnknownInit)
+        .with_module(
+            LightningClientInit {
+                gateway_conn: Some(Arc::new(MockGatewayConnection)),
+            },
+            LightningInit,
+        )
+}
+
+/// The LNv2 routes are registered unauthenticated, so anyone can point them at
+/// any federation the gateway serves. Looking up the LNv2 client module used to
+/// `expect` it into existence, which panics for an LNv1-only federation and
+/// takes the gateway process down with it over iroh.
+#[tokio::test(flavor = "multi_thread")]
+async fn lnv2_routes_reject_a_federation_without_an_lnv2_module() -> anyhow::Result<()> {
+    let fixtures = lnv1_only_fixtures();
+    let fed = fixtures.new_fed_degraded().await;
+    let gateway = fixtures.new_gateway().await;
+    fed.connect_gateway(&gateway).await;
+
+    assert!(
+        gateway.routing_info_v2(&fed.id()).await?.is_none(),
+        "a federation without an LNv2 module has no LNv2 routing info"
+    );
+
+    let keypair = Keypair::new(secp256k1::SECP256K1, &mut rand::thread_rng());
+    let payload = SendPaymentPayload {
+        federation_id: fed.id(),
+        outpoint: OutPoint {
+            txid: TransactionId::from_slice(&[0; 32]).expect("32 bytes is a valid txid"),
+            out_idx: 0,
+        },
+        contract: OutgoingContract {
+            payment_image: PaymentImage::Hash([0_u8; 32].consensus_hash()),
+            amount: Amount::from_msats(1000),
+            expiration: 120,
+            claim_pk: keypair.public_key(),
+            refund_pk: keypair.public_key(),
+            ephemeral_pk: keypair.public_key(),
+        },
+        invoice: LightningInvoice::Bolt11(FakeLightningTest::new().invoice(sats(1), None)?),
+        auth: secp256k1::SECP256K1
+            .sign_schnorr(&secp256k1::Message::from_digest([0; 32]), &keypair),
+    };
+
+    assert!(
+        gateway.send_payment_v2(payload).await.is_err(),
+        "a federation without an LNv2 module cannot be asked to send an LNv2 payment"
+    );
+
+    Ok(())
+}
+
+/// An amountless BOLT11 invoice is rejected by `validate_outgoing_account`, but
+/// the operation log entry written when the payment starts needs the amount
+/// before the state machine ever gets that far, and used to `expect` it.
+#[tokio::test(flavor = "multi_thread")]
+async fn test_gateway_client_rejects_amountless_invoice() -> anyhow::Result<()> {
+    single_federation_test(|gateway, _, fed, user_client, _| async move {
+        let gateway_client = gateway.select_client(fed.id()).await?.into_value();
+
+        let ctx = secp256k1::Secp256k1::new();
+        let keypair = Keypair::new(&ctx, &mut rand::thread_rng());
+        let amountless_invoice =
+            lightning_invoice::InvoiceBuilder::new(lightning_invoice::Currency::Regtest)
+                .description(String::new())
+                .payment_hash(sha256(&[0; 32]))
+                .current_timestamp()
+                .min_final_cltv_expiry_delta(0)
+                .payment_secret(lightning_invoice::PaymentSecret([0; 32]))
+                .build_signed(|m| ctx.sign_ecdsa_recoverable(m, &keypair.secret_key()))?;
+
+        let error = gateway_client
+            .get_first_module::<GatewayClientModule>()?
+            .gateway_pay_bolt11_invoice(PayInvoicePayload {
+                federation_id: user_client.federation_id(),
+                contract_id: sha256(&[0; 32]).into(),
+                payment_data: PaymentData::Invoice(amountless_invoice),
+                preimage_auth: Hash::hash(&[0; 32]),
+            })
+            .await
+            .expect_err("an invoice without an amount is rejected");
+
+        assert_eq!(
+            error.downcast::<OutgoingContractError>()?,
+            OutgoingContractError::InvoiceMissingAmount
+        );
+
+        Ok(())
+    })
+    .await
+}
```
