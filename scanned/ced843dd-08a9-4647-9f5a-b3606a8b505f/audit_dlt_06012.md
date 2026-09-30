# [?] fix: deadlock when shutting down gateway (#8990)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-11
Source: https://github.com/fedimint/fedimint/commit/5242f22969886f0e64162ea82ccefef2be260a76
Type: security-commit

## Details
fix: deadlock when shutting down gateway (#8990)

There is a deadlock that can happen in the gateway when the `/stop`
endpoint is called to safely shutdown the gateway. It is supposed to
allow current payments to finish, but this deadlock prevents that and
stalls the gateway indefinitely.

Fix is to make the `ShuttingDown` state terminal, so that the lightning
re-connect thread cannot change it back to running and also release the
write lock when shutting down, which allows for concurrent payments to
finish.

A test has been added to cover this scenario.

## Patch
### gateway/fedimint-gateway-server/src/lib.rs
```diff
@@ -973,9 +973,17 @@ impl Gateway {
             lightning_alias,
             lightning_network,
         };
-        self.set_gateway_state(GatewayState::Running { lightning_context })
-            .await;
-        info!(target: LOG_GATEWAY, "Gateway is running");
+        if let GatewayState::ShuttingDown { .. } = self
+            .set_gateway_state(GatewayState::Running { lightning_context })
+            .await
+        {
+            info!(
+                target: LOG_GATEWAY,
+                "Reconnected to the lightning node while shutting down, not accepting payments"
+            );
+        } else {
+            info!(target: LOG_GATEWAY, "Gateway is running");
+        }
 
         if matches!(self.lightning_mode, LightningMode::Lnd { .. }) {
             // Re-register the gateway with all federations after connecting to the
@@ -1320,9 +1328,36 @@ impl Gateway {
     }
 
     /// Helper function for atomically changing the Gateway's internal state.
-    async fn set_gateway_state(&self, state: GatewayState) {
+    ///
+    /// Shutting down is one-way. The lightning connection loop keeps running
+    /// while `handle_shutdown_msg` drains the payments that are still in
+    /// flight, and a reconnect in that window must not move the gateway back
+    /// into a state that accepts new payments. A reconnect may still hand over
+    /// a fresh `LightningContext`, which the drain needs to complete the
+    /// payments it is waiting for.
+    /// Returns the state that is in effect afterwards, which is not the
+    /// requested one if the gateway is shutting down.
+    async fn set_gateway_state(&self, state: GatewayState) -> GatewayState {
         let mut lock = self.state.write().await;
-        *lock = state;
+
+        if let GatewayState::ShuttingDown { .. } = *lock {
+            match state {
+                GatewayState::Running { lightning_context } => {
+                    *lock = GatewayState::ShuttingDown { lightning_context };
+                }
+                ignored => {
+                    info!(
+                        target: LOG_GATEWAY,
+                        ignored_state = %ignored,
+                        "Gateway is shutting down, ignoring state change"
+                    );
+                }
+            }
+        } else {
+            *lock = state;
+        }
+
+        lock.clone()
     }
 
     /// If the Gateway is connected to the Lightning node, returns the
@@ -1666,11 +1701,25 @@ impl Gateway {
     }
 
     /// Registers the gateway with each specified federation.
+    ///
+    /// Does nothing once the gateway is shutting down: the lightning connection
+    /// loop keeps reconnecting while `handle_shutdown_msg` drains the payments
+    /// that are still in flight, and re-announcing there would advertise a
+    /// route that is about to disappear, undoing the
+    /// `unannounce_from_all_federations` the shutdown just performed.
     async fn register_federations(
         &self,
         federations: &BTreeMap<FederationId, FederationConfig>,
         register_task_group: &TaskGroup,
     ) {
+        if let GatewayState::ShuttingDown { .. } = self.get_state().await {
+            info!(
+                target: LOG_GATEWAY,
+                "Gateway is shutting down, skipping federation registration"
+            );
+            return;
+        }
+
         if let Ok(lightning_context) = self.get_lightning_context().await {
             let route_hints = lightning_context
                 .lnrpc
@@ -2637,11 +2686,27 @@ impl IAdminGateway for Gateway {
     /// Instructs the gateway to shutdown, but only after all incoming payments
     /// have been handled.
     async fn handle_shutdown_msg(&self, task_group: TaskGroup) -> AdminResult<()> {
-        // Take the write lock on the state so that no additional payments are processed
-        let mut state_guard = self.state.write().await;
-        if let GatewayState::Running { lightning_context } = state_guard.clone() {
-            *state_guard = GatewayState::ShuttingDown { lightning_context };
+        // Take the write lock on the state so that no additional payments are
+        // processed. `ShuttingDown` is terminal, so the state cannot move back to
+        // `Running` once this returns.
+        let was_running = {
+            let mut state_guard = self.state.write().await;
+            if let GatewayState::Running { lightning_context } = state_guard.clone() {
+                *state_guard = GatewayState::ShuttingDown { lightning_context };
+                true
+            } else {
+                false
+            }
+        };
 
+        // The guard has to be released before waiting. Finishing an incoming payment
+        // that already bought the preimage from the federation goes through
+        // `complete_htlc`, which loops on `get_lightning_context` and would block on
+        // the write guard forever. `/stop` would never return, the HTLC would expire,
+        // and the gateway would be left having spent ecash for a payment its sender
+        // gets refunded. `get_lightning_context` accepts `ShuttingDown`, so the
+        // in-flight payments can complete while the gateway drains.
+        if was_running {
             self.federation_manager
                 .read()
                 .await
```

### gateway/fedimint-gateway-server/tests/tests.rs
```diff
@@ -16,7 +16,7 @@ use fedimint_core::config::FederationId;
 use fedimint_core::core::{IntoDynInstance, OperationId};
 use fedimint_core::encoding::Encodable;
 use fedimint_core::module::{AmountUnit, Amounts};
-use fedimint_core::task::sleep_in_test;
+use fedimint_core::task::{TaskGroup, sleep_in_test, timeout};
 use fedimint_core::time::now;
 use fedimint_core::util::{NextOrPending, backoff_util, retry};
 use fedimint_core::{Amount, OutPoint, msats, sats, secp256k1};
@@ -567,6 +567,89 @@ async fn test_gateway_client_intercept_valid_htlc() -> anyhow::Result<()> {
     .await
 }
 
+/// `/stop` drains the payments that are still in flight before shutting the
+/// gateway down. It must not hold the state write lock while it does, because
+/// finishing an incoming payment goes through `complete_htlc`, which loops on
+/// `get_lightning_context` and so needs to read that same lock. Holding it
+/// deadlocks the shutdown: the HTLC expires, its sender is refunded, and the
+/// ecash the gateway already spent buying the preimage is gone.
+#[tokio::test(flavor = "multi_thread")]
+async fn test_gateway_shutdown_completes_in_flight_payment() -> anyhow::Result<()> {
+    single_federation_test(|gateway, _, fed, user_client, _| async move {
+        let gateway_id = gateway.http_gateway_id().await;
+        let gateway_client = gateway.select_client(fed.id()).await?.into_value();
+        let initial_gateway_balance = sats(1000);
+        let dummy_module = gateway_client.get_first_module::<DummyClientModule>()?;
+        dummy_module
+            .mock_receive(initial_gateway_balance, AmountUnit::BITCOIN)
+            .await?;
+
+        let invoice_amount = sats(100);
+        let ln_module = user_client.get_first_module::<LightningClientModule>()?;
+        let lightning_gateway = ln_module.select_gateway(&gateway_id).await;
+        let desc = Description::new("description".to_string())?;
+        let (_invoice_op, invoice, _) = ln_module
+            .create_bolt11_invoice(
+                invoice_amount,
+                Bolt11InvoiceDescription::Direct(desc),
+                None,
+                "test shutdown with a payment in flight",
+                lightning_gateway,
+            )
+            .await?;
+
+        let htlc = Htlc {
+            payment_hash: *invoice.payment_hash(),
+            incoming_amount_msat: Amount::from_msats(invoice.amount_milli_satoshis().unwrap()),
+            outgoing_amount_msat: Amount::from_msats(invoice.amount_milli_satoshis().unwrap()),
+            incoming_expiry: u32::MAX,
+            short_channel_id: Some(1),
+            incoming_chan_id: 2,
+            htlc_id: 1,
+        };
+        let intercept_op = gateway_client
+            .get_first_module::<GatewayClientModule>()?
+            .gateway_handle_intercepted_htlc(htlc)
+            .await?;
+        let mut intercept_sub = gateway_client
+            .get_first_module::<GatewayClientModule>()?
+            .gateway_subscribe_ln_receive(intercept_op)
+            .await?
+            .into_stream();
+
+        // Shut down before the payment had a chance to finish, so the drain has to
+        // wait for a completion that calls `complete_htlc`. The task group is a
+        // throwaway one: only the draining half of the shutdown is under test.
+        timeout(
+            Duration::from_secs(30),
+            gateway.handle_shutdown_msg(TaskGroup::new()),
+        )
+        .await
+        .expect("Shutdown deadlocked while draining an in-flight payment")?;
+
+        // Shutting down is one-way, so the gateway accepts no further payments.
+        assert_eq!(
+            gateway.handle_get_info().await?.gateway_state,
+            "ShuttingDown"
+        );
+
+        // The drained payment ran to completion, so the gateway holds the preimage
+        // it paid the federation for.
+        assert_eq!(intercept_sub.ok().await?, GatewayExtReceiveStates::Funding);
+        assert_matches!(
+            intercept_sub.ok().await?,
+            GatewayExtReceiveStates::Preimage { .. }
+        );
+        assert_eq!(
+            initial_gateway_balance.saturating_sub(invoice_amount),
+            gateway_client.get_balance_for_btc().await?
+        );
+
+        Ok(())
+    })
+    .await
+}
+
 #[tokio::test(flavor = "multi_thread")]
 async fn test_gateway_client_intercept_same_circuit_replay_is_idempotent() -> anyhow::Result<()> {
     single_federation_test(|gateway, _, fed, user_client, _| async move {
```
