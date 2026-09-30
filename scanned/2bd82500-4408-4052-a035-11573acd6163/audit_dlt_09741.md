# [?] fix(client): panic on api calls when primary module is not available

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-09-29
Source: https://github.com/fedimint/fedimint/commit/f30024ae57c0e82b16fd47bf8bdda58ed9edb30c
Type: security-commit

## Details
fix(client): panic on api calls when primary module is not available

## Patch
### fedimint-cli/src/client.rs
```diff
@@ -532,7 +532,7 @@ pub async fn handle_command(
                 // the amount we are withdrawing
                 BitcoinAmountOrAll::All => {
                     let balance =
-                        bitcoin::Amount::from_sat(client.get_balance().await.msats / 1000);
+                        bitcoin::Amount::from_sat(client.get_balance_err().await?.msats / 1000);
                     let fees = wallet_module.get_withdraw_fees(&address, balance).await?;
                     let amount = balance.checked_sub(fees.amount());
                     if amount.is_none() {
```

### fedimint-client/src/client.rs
```diff
@@ -427,9 +427,11 @@ impl Client {
         mut partial_transaction: TransactionBuilder,
     ) -> anyhow::Result<(Transaction, Vec<DynState>, Range<u64>)> {
         let (input_amount, output_amount) = self.transaction_builder_balance(&partial_transaction);
-
-        let (added_input_bundle, change_outputs) = self
+        let primary_module = self
             .primary_module()
+            .ok_or(anyhow!("No primary module available"))?;
+
+        let (added_input_bundle, change_outputs) = primary_module
             .create_final_inputs_and_outputs(
                 self.primary_module_instance,
                 dbtx,
@@ -643,6 +645,7 @@ impl Client {
         out_point: OutPoint,
     ) -> anyhow::Result<()> {
         self.primary_module()
+            .ok_or(anyhow!("Primary module not available"))?
             .await_primary_module_output(operation_id, out_point)
             .await
     }
@@ -739,32 +742,57 @@ impl Client {
     }
 
     /// Get the primary module
-    pub fn primary_module(&self) -> &DynClientModule {
-        self.modules
-            .get(self.primary_module_instance)
-            .expect("primary module must be present")
+    pub fn primary_module(&self) -> Option<&DynClientModule> {
+        self.modules.get(self.primary_module_instance)
     }
 
     /// Balance available to the client for spending
-    pub async fn get_balance(&self) -> Amount {
-        self.primary_module()
-            .get_balance(
-                self.primary_module_instance,
-                &mut self.db().begin_transaction_nc().await,
-            )
+    ///
+    /// Returns `None` if the primary module is not available
+    pub async fn get_balance(&self) -> Option<Amount> {
+        Some(
+            self.primary_module()?
+                .get_balance(
+                    self.primary_module_instance,
+                    &mut self.db().begin_transaction_nc().await,
+                )
+                .await,
+        )
+    }
+
+    // Ideally this would not be in the API, but there's a lot of places where this
+    // makes it easier.
+    #[doc(hidden)]
+    /// Like [`Self::get_balance`] but returns an error if primary module is not
+    /// available
+    pub async fn get_balance_err(&self) -> anyhow::Result<Amount> {
+        self.get_balance()
             .await
+            .ok_or_else(|| anyhow!("Primary module not available"))
     }
 
     /// Returns a stream that yields the current client balance every time it
     /// changes.
     pub async fn subscribe_balance_changes(&self) -> BoxStream<'static, Amount> {
-        let mut balance_changes = self.primary_module().subscribe_balance_changes().await;
-        let initial_balance = self.get_balance().await;
+        let primary_module_things = if let Some(primary_module) = self.primary_module() {
+            let balance_changes = primary_module.subscribe_balance_changes().await;
+            let initial_balance = self.get_balance().await.expect("Primary is present");
+
+            Some((primary_module.clone(), balance_changes, initial_balance))
+        } else {
+            None
+        };
         let db = self.db().clone();
-        let primary_module = self.primary_module().clone();
         let primary_module_instance = self.primary_module_instance;
 
         Box::pin(async_stream::stream! {
+            let Some((primary_module, mut balance_changes, initial_balance)) = primary_module_things else {
+                // If there is no primary module, there will not be one until client is
+                // restarted
+                pending().await
+            };
+
+
             yield initial_balance;
             let mut prev_balance = initial_balance;
             while let Some(()) = balance_changes.next().await {
@@ -1409,7 +1437,7 @@ impl Client {
         Box::pin(try_stream! {
             match method.as_str() {
                 "get_balance" => {
-                    let balance = self.get_balance().await;
+                    let balance = self.get_balance().await.unwrap_or_default();
                     yield serde_json::to_value(balance)?;
                 }
                 "subscribe_balance_changes" => {
```

### fedimint-core/src/amount.rs
```diff
@@ -23,7 +23,18 @@ pub fn sats(amount: u64) -> Amount {
 /// Represents an amount of BTC. The base denomination is millisatoshis, which
 /// is why the `Amount` type from rust-bitcoin isn't used instead.
 #[derive(
-    Clone, Copy, Eq, PartialEq, Ord, PartialOrd, Hash, Deserialize, Serialize, Encodable, Decodable,
+    Clone,
+    Copy,
+    Eq,
+    PartialEq,
+    Ord,
+    PartialOrd,
+    Hash,
+    Deserialize,
+    Serialize,
+    Encodable,
+    Decodable,
+    Default,
 )]
 #[serde(transparent)]
 pub struct Amount {
```

### fedimint-load-test-tool/src/main.rs
```diff
@@ -12,7 +12,7 @@ use std::str::FromStr;
 use std::time::Duration;
 use std::vec;
 
-use anyhow::{Context, bail};
+use anyhow::{Context, anyhow, bail};
 use clap::{Args, Parser, Subcommand, ValueEnum};
 use common::{
     gateway_pay_invoice, get_note_summary, ldk_create_invoice, ldk_pay_invoice,
@@ -562,7 +562,11 @@ async fn get_required_notes(
     minimum_amount_required: Amount,
     event_sender: &mpsc::UnboundedSender<MetricEvent>,
 ) -> anyhow::Result<()> {
-    let current_balance = coordinator.get_balance().await;
+    let current_balance = coordinator
+        .get_balance()
+        .await
+        .ok_or_else(|| anyhow!("Primary module not available"))?;
+
     if current_balance < minimum_amount_required {
         let diff = minimum_amount_required.saturating_sub(current_balance);
         info!(
@@ -663,7 +667,7 @@ async fn do_load_test_user_task(
         let amount = oob_note.total_amount();
         reissue_notes(&client, oob_note, &event_sender)
             .await
-            .map_err(|e| anyhow::anyhow!("while reissuing initial {amount}: {e}"))?;
+            .map_err(|e| anyhow!("while reissuing initial {amount}: {e}"))?;
     }
     let mut generated_invoices_per_user_iterator = (0..generated_invoices_per_user).peekable();
     while let Some(_) = generated_invoices_per_user_iterator.next() {
@@ -805,7 +809,7 @@ async fn do_ln_circular_test_user_task(
         let amount = oob_note.total_amount();
         reissue_notes(&client, oob_note, &event_sender)
             .await
-            .map_err(|e| anyhow::anyhow!("while reissuing initial {amount}: {e}"))?;
+            .map_err(|e| anyhow!("while reissuing initial {amount}: {e}"))?;
     }
     let initial_time = fedimint_core::time::now();
     let still_ontime = || async {
```

### gateway/fedimint-gateway-server/src/federation_manager.rs
```diff
@@ -12,7 +12,7 @@ use fedimint_gateway_server_db::GatewayDbtxNcExt as _;
 use fedimint_gw_client::GatewayClientModule;
 use fedimint_gwv2_client::GatewayClientModuleV2;
 use fedimint_logging::LOG_GATEWAY;
-use tracing::info;
+use tracing::{info, warn};
 
 use crate::AdminResult;
 use crate::error::{AdminGatewayError, FederationNotConnected};
@@ -210,7 +210,9 @@ impl FederationManager {
             .expect("`FederationManager.index_to_federation` is out of sync with `FederationManager.clients`! This is a bug.")
             .borrow()
             .with(|client| async move {
-                let balance_msat = client.get_balance().await;
+                let balance_msat = client.get_balance().await
+                    // If primary module is not available, we're not really connected yet
+                    .ok_or_else(|| FederationNotConnected { federation_id_prefix: federation_id.to_prefix() })?;
 
                 let config = dbtx.load_federation_config(federation_id).await.ok_or(FederationNotConnected {
                     federation_id_prefix: federation_id.to_prefix(),
@@ -238,7 +240,11 @@ impl FederationManager {
     ) -> Vec<FederationInfo> {
         let mut federation_infos = Vec::new();
         for (federation_id, client) in &self.clients {
-            let balance_msat = client.borrow().with(|client| client.get_balance()).await;
+            let Some(balance_msat) = client.borrow().with(|client| client.get_balance()).await
+            else {
+                warn!(target: LOG_GATEWAY, "Skipped Federation due to lack of primary module");
+                continue;
+            };
 
             let config = dbtx.load_federation_config(*federation_id).await;
             if let Some(config) = config {
```

### gateway/fedimint-gateway-server/src/lib.rs
```diff
@@ -960,8 +960,17 @@ impl Gateway {
             // If the amount is "all", then we need to subtract the fees from
             // the amount we are withdrawing
             BitcoinAmountOrAll::All => {
-                let balance =
-                    bitcoin::Amount::from_sat(client.value().get_balance().await.msats / 1000);
+                let balance = bitcoin::Amount::from_sat(
+                    client
+                        .value()
+                        .get_balance()
+                        .await
+                        .ok_or_else(|| {
+                            AdminGatewayError::Unexpected(anyhow!("Primary module not available"))
+                        })?
+                        .msats
+                        / 1000,
+                );
                 let fees = wallet_module.get_withdraw_fees(&address, balance).await?;
                 let withdraw_amount = balance.checked_sub(fees.amount());
                 if withdraw_amount.is_none() {
@@ -1221,7 +1230,7 @@ impl Gateway {
         let federation_info = FederationInfo {
             federation_id,
             federation_name: federation_manager.federation_name(&client).await,
-            balance_msat: client.get_balance().await,
+            balance_msat: client.get_balance().await.unwrap_or_default(),
             config: federation_config.clone(),
         };
 
```

### gateway/fedimint-gateway-server/tests/tests.rs
```diff
@@ -244,7 +244,7 @@ async fn test_gateway_client_pay_valid_invoice() -> anyhow::Result<()> {
             let dummy_module = user_client.get_first_module::<DummyClientModule>()?;
             let (_, outpoint) = dummy_module.print_money(sats(1000)).await?;
             dummy_module.receive_money_hack(outpoint).await?;
-            assert_eq!(user_client.get_balance().await, sats(1000));
+            assert_eq!(user_client.get_balance_err().await?, sats(1000));
 
             // Create test invoice
             let invoice = other_lightning_client.invoice(sats(250), None)?;
@@ -257,8 +257,8 @@ async fn test_gateway_client_pay_valid_invoice() -> anyhow::Result<()> {
             )
             .await?;
 
-            assert_eq!(user_client.get_balance().await, sats(1000 - 250));
-            assert_eq!(gateway_client.get_balance().await, sats(250));
+            assert_eq!(user_client.get_balance_err().await?, sats(1000 - 250));
+            assert_eq!(gateway_client.get_balance_err().await?, sats(250));
 
             Ok(())
         },
@@ -274,7 +274,7 @@ async fn test_gateway_enforces_fees() -> anyhow::Result<()> {
             let dummy_module = user_client.get_first_module::<DummyClientModule>()?;
             let (_, outpoint) = dummy_module.print_money(sats(1000)).await?;
             dummy_module.receive_money_hack(outpoint).await?;
-            assert_eq!(user_client.get_balance().await, sats(1000));
+            assert_eq!(user_client.get_balance_err().await?, sats(1000));
 
             let user_lightning_module = user_client.get_first_module::<LightningClientModule>()?;
             let gateway_id = gateway.gateway_id();
@@ -363,7 +363,7 @@ async fn test_gateway_cannot_claim_invalid_preimage() -> anyhow::Result<()> {
             let dummy_module = user_client.get_first_module::<DummyClientModule>().unwrap();
             let (_, outpoint) = dummy_module.print_money(sats(1000)).await?;
             dummy_module.receive_money_hack(outpoint).await?;
-            assert_eq!(user_client.get_balance().await, sats(1000));
+            assert_eq!(user_client.get_balance_err().await?, sats(1000));
 
             // Fund outgoing contract that the user client expects the gateway to pay
             let invoice = other_lightning_client.invoice(sats(250), None)?;
@@ -425,7 +425,7 @@ async fn test_gateway_cannot_claim_invalid_preimage() -> anyhow::Result<()> {
                     .await
                     .is_err()
             );
-            assert_eq!(gateway_client.get_balance().await, sats(0));
+            assert_eq!(gateway_client.get_balance_err().await?, sats(0));
             Ok::<_, anyhow::Error>(())
         },
     )
@@ -443,7 +443,7 @@ async fn test_gateway_client_pay_unpayable_invoice() -> anyhow::Result<()> {
             let lightning_module = user_client.get_first_module::<LightningClientModule>()?;
             let (_, outpoint) = dummy_module.print_money(sats(1000)).await?;
             dummy_module.receive_money_hack(outpoint).await?;
-            assert_eq!(user_client.get_balance().await, sats(1000));
+            assert_eq!(user_client.get_balance_err().await?, sats(1000));
 
             // Create invoice that cannot be paid
             let invoice = other_lightning_client.unpayable_invoice(sats(250), None);
@@ -504,7 +504,7 @@ async fn test_gateway_client_intercept_valid_htlc() -> anyhow::Result<()> {
         let dummy_module = gateway_client.get_first_module::<DummyClientModule>()?;
         let (_, outpoint) = dummy_module.print_money(initial_gateway_balance).await?;
         dummy_module.receive_money_hack(outpoint).await?;
-        assert_eq!(gateway_client.get_balance().await, sats(1000));
+        assert_eq!(gateway_client.get_balance_err().await?, sats(1000));
 
         // User client creates invoice in federation
         let invoice_amount = sats(100);
@@ -547,7 +547,7 @@ async fn test_gateway_client_intercept_valid_htlc() -> anyhow::Result<()> {
         );
         assert_eq!(
             initial_gateway_balance.saturating_sub(invoice_amount),
-            gateway_client.get_balance().await
+            gateway_client.get_balance_err().await?
         );
 
         Ok(())
@@ -564,7 +564,7 @@ async fn test_gateway_client_intercept_offer_does_not_exist() -> anyhow::Result<
         let dummy_module = gateway_client.get_first_module::<DummyClientModule>()?;
         let (_, outpoint) = dummy_module.print_money(initial_gateway_balance).await?;
         dummy_module.receive_money_hack(outpoint).await?;
-        assert_eq!(gateway_client.get_balance().await, sats(1000));
+        assert_eq!(gateway_client.get_balance_err().await?, sats(1000));
 
         // Create HTLC that doesn't correspond to an offer in the federation
         let htlc = Htlc {
@@ -650,7 +650,7 @@ async fn test_gateway_client_intercept_htlc_invalid_offer() -> anyhow::Result<()
                 .print_money(initial_gateway_balance)
                 .await?;
             gateway_dummy_module.receive_money_hack(outpoint).await?;
-            assert_eq!(gateway_client.get_balance().await, sats(1000));
+            assert_eq!(gateway_client.get_balance_err().await?, sats(1000));
 
             // Create test invoice
             let invoice = other_lightning_client.unpayable_invoice(sats(250), None);
@@ -742,7 +742,10 @@ async fn test_gateway_client_intercept_htlc_invalid_offer() -> anyhow::Result<()
                         gateway_dummy_module.receive_money_hack(outpoint).await?;
                     }
 
-                    assert_eq!(initial_gateway_balance, gateway_client.get_balance().await);
+                    assert_eq!(
+                        initial_gateway_balance,
+                        gateway_client.get_balance_err().await?
+                    );
                 }
                 unexpected_state => panic!(
                     "Gateway receive state machine entered unexpected state: {unexpected_state:?}"
@@ -773,7 +776,7 @@ async fn test_gateway_cannot_pay_expired_invoice() -> anyhow::Result<()> {
             let dummy_module = user_client.get_first_module::<DummyClientModule>()?;
             let (_, outpoint) = dummy_module.print_money(sats(2000)).await?;
             dummy_module.receive_money_hack(outpoint).await?;
-            assert_eq!(user_client.get_balance().await, sats(2000));
+            assert_eq!(user_client.get_balance_err().await?, sats(2000));
 
             // User client pays test invoice
             let lightning_module = user_client.get_first_module::<LightningClientModule>()?;
@@ -817,7 +820,7 @@ async fn test_gateway_cannot_pay_expired_invoice() -> anyhow::Result<()> {
             }
 
             // Balance should be unchanged
-            assert_eq!(gateway_client.get_balance().await, sats(0));
+            assert_eq!(gateway_client.get_balance_err().await?, sats(0));
 
             Ok(())
         },
@@ -869,7 +872,7 @@ async fn test_gateway_executes_swaps_between_connected_federations() -> anyhow::
         let client1_dummy_module = client1.get_first_module::<DummyClientModule>()?;
         let (_, outpoint) = client1_dummy_module.print_money(deposit_amt).await?;
         client1_dummy_module.receive_money_hack(outpoint).await?;
-        assert_eq!(client1.get_balance().await, deposit_amt);
+        assert_eq!(client1.get_balance_err().await?, deposit_amt);
 
         // User creates invoice in federation 2
         let invoice_amt = msats(2_500);
@@ -905,12 +908,12 @@ async fn test_gateway_executes_swaps_between_connected_federations() -> anyhow::
         assert_matches!(waiting_funds, LnReceiveState::AwaitingFunds);
         let claimed = receive_sub.ok().await?;
         assert_matches!(claimed, LnReceiveState::Claimed);
-        assert_eq!(client2.get_balance().await, invoice_amt);
+        assert_eq!(client2.get_balance_err().await?, invoice_amt);
 
         // Check gateway balances after facilitating direct swap between federations
-        let gateway_fed1_balance = gateway_client.get_balance().await;
+        let gateway_fed1_balance = gateway_client.get_balance_err().await?;
         let gateway_fed2_client = gateway.select_client(id2).await?.into_value();
-        let gateway_fed2_balance = gateway_fed2_client.get_balance().await;
+        let gateway_fed2_balance = gateway_fed2_client.get_balance_err().await?;
 
         // Balance in gateway of sending federation is deducted the invoice amount
         assert_eq!(
@@ -980,7 +983,13 @@ async fn send_msats_to_gateway(gateway: &Gateway, federation_id: FederationId, m
         .await
         .expect("Could not await primary module liquidity");
 
-    assert_eq!(client.get_balance().await, Amount::from_msats(msats));
+    assert_eq!(
+        client
+            .get_balance_err()
+            .await
+            .expect("Must have primary module"),
+        Amount::from_msats(msats)
+    );
 }
 
 #[tokio::test(flavor = "multi_thread")]
```

### modules/fedimint-dummy-tests/tests/tests.rs
```diff
@@ -28,14 +28,14 @@ async fn can_print_and_send_money() -> anyhow::Result<()> {
     let client2_dummy_module = client2.get_first_module::<DummyClientModule>()?;
     let (_, outpoint) = client1_dummy_module.print_money(sats(1000)).await?;
     client1_dummy_module.receive_money_hack(outpoint).await?;
-    assert_eq!(client1.get_balance().await, sats(1000));
+    assert_eq!(client1.get_balance_err().await?, sats(1000));
 
     let outpoint = client1_dummy_module
         .send_money(client2_dummy_module.account(), sats(250))
         .await?;
     client2_dummy_module.receive_money_hack(outpoint).await?;
-    assert_eq!(client1.get_balance().await, sats(750));
-    assert_eq!(client2.get_balance().await, sats(250));
+    assert_eq!(client1.get_balance_err().await?, sats(750));
+    assert_eq!(client2.get_balance_err().await?, sats(250));
     Ok(())
 }
 
```

### modules/fedimint-ln-tests/tests/tests.rs
```diff
@@ -201,7 +201,7 @@ async fn cannot_pay_same_internal_invoice_twice() -> anyhow::Result<()> {
 
     // Pay the invoice again and verify that it does not deduct the balance, but it
     // does return the preimage
-    let prev_balance = client2.get_balance().await;
+    let prev_balance = client2.get_balance_err().await?;
     let OutgoingLightningPayment {
         payment_type,
         contract_id: _,
@@ -220,7 +220,7 @@ async fn cannot_pay_same_internal_invoice_twice() -> anyhow::Result<()> {
         _ => panic!("Expected internal payment!"),
     }
 
-    let same_balance = client2.get_balance().await;
+    let same_balance = client2.get_balance_err().await?;
     assert_eq!(prev_balance, same_balance);
 
     Ok(())
@@ -262,7 +262,7 @@ async fn cannot_pay_same_external_invoice_twice() -> anyhow::Result<()> {
         _ => panic!("Expected lightning payment!"),
     }
 
-    let prev_balance = client.get_balance().await;
+    let prev_balance = client.get_balance_err().await?;
 
     // Pay the invoice again and verify that it does not deduct the balance, but it
     // does return the preimage
@@ -286,7 +286,7 @@ async fn cannot_pay_same_external_invoice_twice() -> anyhow::Result<()> {
         _ => panic!("Expected lightning payment!"),
     }
 
-    let same_balance = client.get_balance().await;
+    let same_balance = client.get_balance_err().await?;
     assert_eq!(prev_balance, same_balance);
 
     drop(gw);
@@ -459,7 +459,7 @@ async fn can_receive_for_other_user() -> anyhow::Result<()> {
         .into_stream();
     assert_eq!(sub3.ok().await?, LnReceiveState::AwaitingFunds);
     assert_eq!(sub3.ok().await?, LnReceiveState::Claimed);
-    assert_eq!(new_client.get_balance().await, sats(250));
+    assert_eq!(new_client.get_balance_err().await?, sats(250));
 
     // TEST internal payment when there is a registered gateway
     let gw = gateway(&fixtures, &fed).await;
@@ -518,7 +518,7 @@ async fn can_receive_for_other_user() -> anyhow::Result<()> {
         .into_stream();
     assert_eq!(sub3.ok().await?, LnReceiveState::AwaitingFunds);
     assert_eq!(sub3.ok().await?, LnReceiveState::Claimed);
-    assert_eq!(new_client.get_balance().await, sats(250));
+    assert_eq!(new_client.get_balance_err().await?, sats(250));
 
     Ok(())
 }
@@ -595,7 +595,7 @@ async fn can_receive_for_other_user_tweaked() -> anyhow::Result<()> {
         assert_eq!(sub3.ok().await?, LnReceiveState::AwaitingFunds);
         assert_eq!(sub3.ok().await?, LnReceiveState::Claimed);
     }
-    assert_eq!(new_client.get_balance().await, sats(250));
+    assert_eq!(new_client.get_balance_err().await?, sats(250));
 
     Ok(())
 }
```

### modules/fedimint-mint-tests/tests/tests.rs
```diff
@@ -136,8 +136,8 @@ async fn sends_ecash_out_of_band() -> anyhow::Result<()> {
     assert_eq!(sub1.ok().await?, SpendOOBState::Success);
     info!("### REISSUE: DONE");
 
-    assert!(client1.get_balance().await >= sats(250).saturating_sub(EXPECTED_MAXIMUM_FEE));
-    assert!(client2.get_balance().await >= sats(750).saturating_sub(EXPECTED_MAXIMUM_FEE));
+    assert!(client1.get_balance_err().await? >= sats(250).saturating_sub(EXPECTED_MAXIMUM_FEE));
+    assert!(client2.get_balance_err().await? >= sats(750).saturating_sub(EXPECTED_MAXIMUM_FEE));
     Ok(())
 }
 
@@ -247,7 +247,7 @@ async fn sends_ecash_oob_highly_parallel() -> anyhow::Result<()> {
     let total_amount_spent: Amount = note_bags.iter().map(|bag| bag.total_amount()).sum();
 
     assert_eq!(
-        client1.get_balance().await,
+        client1.get_balance_err().await?,
         sats(1000).saturating_sub(total_amount_spent)
     );
 
@@ -284,7 +284,9 @@ async fn sends_ecash_oob_highly_parallel() -> anyhow::Result<()> {
         task.await.expect("reissue task failed");
     }
 
-    assert!(client2.get_balance().await >= total_amount_spent.saturating_sub(EXPECTED_MAXIMUM_FEE));
+    assert!(
+        client2.get_balance_err().await? >= total_amount_spent.saturating_sub(EXPECTED_MAXIMUM_FEE)
+    );
 
     Ok(())
 }
@@ -363,7 +365,7 @@ async fn sends_ecash_out_of_band_cancel() -> anyhow::Result<()> {
 
     // FIXME: UserCanceledSuccess should mean the money is in our wallet
     for _ in 0..120 {
-        let balance = client.get_balance().await;
+        let balance = client.get_balance_err().await?;
         let expected_min_balance = sats(1000).saturating_sub(EXPECTED_MAXIMUM_FEE);
         if expected_min_balance <= balance {
             return Ok(());
@@ -440,7 +442,7 @@ async fn sends_ecash_out_of_band_cancel_partial() -> anyhow::Result<()> {
 
     // FIXME: UserCanceledSuccess should mean the money is in our wallet
     for _ in 0..120 {
-        let balance = client.get_balance().await;
+        let balance = client.get_balance_err().await?;
         let expected_min_balance = sats(1000)
             .saturating_sub(EXPECTED_MAXIMUM_FEE)
             .saturating_sub(single_note.0);
```

### modules/fedimint-wallet-tests/tests/tests.rs
```diff
@@ -87,7 +87,7 @@ async fn peg_in<'a>(
         .await_num_deposits_by_operation_id(op, 1)
         .await?;
     assert_eq!(
-        client.get_balance().await,
+        client.get_balance_err().await?,
         initial_balance + sats(PEG_IN_AMOUNT_SATS)
     );
     assert_eq!(
@@ -229,7 +229,7 @@ async fn on_chain_peg_in_and_peg_out_happy_case() -> anyhow::Result<()> {
     await_consensus_to_catch_up(&client, 1).await?;
     await_consensus_upgrade(&client, &fed).await?;
 
-    assert_eq!(client.get_balance().await, sats(0));
+    assert_eq!(client.get_balance_err().await?, sats(0));
     let (op, address, _) = wallet_module
         .allocate_deposit_address_expert_only(())
         .await?;
@@ -321,7 +321,7 @@ async fn on_chain_peg_in_and_peg_out_happy_case() -> anyhow::Result<()> {
 
     info!("Checking balance after deposit");
     let mut balance_sub = client.subscribe_balance_changes().await;
-    assert_eq!(client.get_balance().await, sats(PEG_IN_AMOUNT_SATS));
+    assert_eq!(client.get_balance_err().await?, sats(PEG_IN_AMOUNT_SATS));
     assert_eq!(balance_sub.ok().await?, sats(PEG_IN_AMOUNT_SATS));
 
     assert_eq!(deposit_updates.next().await, None);
@@ -339,7 +339,7 @@ async fn on_chain_peg_in_and_peg_out_happy_case() -> anyhow::Result<()> {
 
     let balance_after_peg_out =
         sats(PEG_IN_AMOUNT_SATS - PEG_OUT_AMOUNT_SATS - fees.amount().to_sat());
-    assert_eq!(client.get_balance().await, balance_after_peg_out);
+    assert_eq!(client.get_balance_err().await?, balance_after_peg_out);
     assert_eq!(balance_sub.ok().await?, balance_after_peg_out);
 
     let sub = wallet_module.subscribe_withdraw_updates(op).await?;
@@ -377,7 +377,7 @@ async fn on_chain_peg_in_detects_multiple() -> anyhow::Result<()> {
     bitcoin.mine_blocks(finality_delay).await;
     await_consensus_to_catch_up(&client, 1).await?;
 
-    let starting_balance = client.get_balance().await;
+    let starting_balance = client.get_balance_err().await?;
     info!(?starting_balance, "Starting balance");
 
     await_consensus_upgrade(&client, &fed).await?;
@@ -407,7 +407,7 @@ async fn on_chain_peg_in_detects_multiple() -> anyhow::Result<()> {
             .await_num_deposits_by_operation_id(op, 1)
             .await?;
         assert_eq!(
-            client.get_balance().await,
+            client.get_balance_err().await?,
             sats(PEG_IN_AMOUNT_SATS) + starting_balance
         );
         info!(?height, ?tx, "First peg-in transaction claimed");
@@ -432,7 +432,7 @@ async fn on_chain_peg_in_detects_multiple() -> anyhow::Result<()> {
         bitcoin.mine_blocks(finality_delay).await;
         wallet_module.await_num_deposits(tweak_idx, 2).await?;
         assert_eq!(
-            client.get_balance().await,
+            client.get_balance_err().await?,
             sats(PEG_IN_AMOUNT_SATS * 2) + starting_balance
         );
         info!(?height, ?tx, "Second peg-in transaction claimed");
@@ -481,7 +481,7 @@ async fn peg_out_fail_refund() -> anyhow::Result<()> {
 
     // Check that we get our money back if the peg-out fails
     assert_eq!(balance_sub.next().await.unwrap(), sats(PEG_IN_AMOUNT_SATS));
-    assert_eq!(client.get_balance().await, sats(PEG_IN_AMOUNT_SATS));
+    assert_eq!(client.get_balance_err().await?, sats(PEG_IN_AMOUNT_SATS));
 
     Ok(())
 }
@@ -522,7 +522,10 @@ async fn rbf_withdrawals_are_rejected() -> anyhow::Result<()> {
     );
     let balance_after_normal_peg_out =
         sats(PEG_IN_AMOUNT_SATS - PEG_OUT_AMOUNT_SATS - fees.amount().to_sat());
-    assert_eq!(client.get_balance().await, balance_after_normal_peg_out);
+    assert_eq!(
+        client.get_balance_err().await?,
+        balance_after_normal_peg_out
+    );
     assert_eq!(balance_sub.ok().await?, balance_after_normal_peg_out);
 
     // RBF by increasing sats per kvb by 1000
@@ -560,7 +563,7 @@ async fn rbf_withdrawals_are_rejected() -> anyhow::Result<()> {
             Some(100),
         ),
         || async {
-            let current_balance = client.get_balance().await;
+            let current_balance = client.get_balance_err().await?;
             if current_balance == balance_after_normal_peg_out {
                 Ok(())
             } else {
@@ -608,7 +611,7 @@ async fn peg_outs_must_wait_for_available_utxos() -> anyhow::Result<()> {
         .await?;
     let balance_after_peg_out =
         sats(PEG_IN_AMOUNT_SATS - PEG_OUT_AMOUNT_SATS - fees1.amount().to_sat());
-    assert_eq!(client.get_balance().await, balance_after_peg_out);
+    assert_eq!(client.get_balance_err().await?, balance_after_peg_out);
     assert_eq!(balance_sub.ok().await?, balance_after_peg_out);
 
     let sub = wallet_module.subscribe_withdraw_updates(op).await?;
@@ -658,7 +661,10 @@ async fn peg_outs_must_wait_for_available_utxos() -> anyhow::Result<()> {
             - fees1.amount().to_sat()
             - fees2.amount().to_sat(),
     );
-    assert_eq!(client.get_balance().await, balance_after_second_peg_out);
+    assert_eq!(
+        client.get_balance_err().await?,
+        balance_after_second_peg_out
+    );
     assert_eq!(balance_sub.ok().await?, balance_after_second_peg_out);
     Ok(())
 }
@@ -824,7 +830,7 @@ async fn dust_deposits_are_ignored() -> anyhow::Result<()> {
     await_consensus_to_catch_up(&client, 1).await?;
     await_consensus_upgrade(&client, &fed).await?;
 
-    assert_eq!(client.get_balance().await, sats(0));
+    assert_eq!(client.get_balance_err().await?, sats(0));
     let (op, address, _) = wallet_module
         .allocate_deposit_address_expert_only(())
         .await?;
@@ -881,7 +887,7 @@ async fn dust_deposits_are_ignored() -> anyhow::Result<()> {
     ));
 
     info!("Checking balance after deposit");
-    assert_eq!(client.get_balance().await, Amount::ZERO);
+    assert_eq!(client.get_balance_err().await?, Amount::ZERO);
     Ok(())
 }
 
```
