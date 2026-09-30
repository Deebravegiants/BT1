# [?] fix: race condition in wallet tests

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-01-17
Source: https://github.com/fedimint/fedimint/commit/46407f8f058a3448b687823078cf79cd917104e3
Type: security-commit

## Details
fix: race condition in wallet tests

## Patch
### modules/fedimint-wallet-tests/tests/tests.rs
```diff
@@ -14,7 +14,7 @@ use fedimint_core::db::{DatabaseTransaction, IRawDatabaseExt};
 use fedimint_core::envs::BitcoinRpcConfig;
 use fedimint_core::module::serde_json;
 use fedimint_core::task::sleep_in_test;
-use fedimint_core::util::{BoxStream, NextOrPending};
+use fedimint_core::util::{retry, BoxStream, NextOrPending};
 use fedimint_core::{sats, Amount, Feerate, PeerId};
 use fedimint_dummy_client::DummyClientInit;
 use fedimint_dummy_common::config::DummyGenParams;
@@ -57,12 +57,7 @@ async fn peg_in<'a>(
     let mut balance_sub = client.subscribe_balance_changes().await;
     let initial_balance = balance_sub.ok().await?;
 
-    assert!(
-        client
-            .get_first_module::<WalletClientModule>()?
-            .btc_tx_has_no_size_limit()
-            .await?
-    );
+    await_consensus_upgrade(client).await;
 
     let wallet_module = &client.get_first_module::<WalletClientModule>()?;
     let (op, address, _) = wallet_module
@@ -121,6 +116,23 @@ async fn await_consensus_to_catch_up(
     }
 }
 
+async fn await_consensus_upgrade(client: &ClientHandleArc) {
+    retry(
+        "waiting for consensus upgrade",
+        fedimint_core::util::backoff_util::aggressive_backoff(),
+        || async {
+            client
+                .get_first_module::<WalletClientModule>()?
+                .btc_tx_has_no_size_limit()
+                .await?;
+
+            Ok(())
+        },
+    )
+    .await
+    .expect("Consensus upgrade didn't happen in time");
+}
+
 #[tokio::test(flavor = "multi_thread")]
 async fn sanity_check_bitcoin_blocks() -> anyhow::Result<()> {
     let fixtures = fixtures();
@@ -176,13 +188,7 @@ async fn on_chain_peg_in_and_peg_out_happy_case() -> anyhow::Result<()> {
     let finality_delay = 10;
     bitcoin.mine_blocks(finality_delay).await;
     await_consensus_to_catch_up(&client, 1).await?;
-
-    assert!(
-        client
-            .get_first_module::<WalletClientModule>()?
-            .btc_tx_has_no_size_limit()
-            .await?
-    );
+    await_consensus_upgrade(&client).await;
 
     assert_eq!(client.get_balance().await, sats(0));
     let (op, address, _) = wallet_module
@@ -335,12 +341,7 @@ async fn on_chain_peg_in_detects_multiple() -> anyhow::Result<()> {
     let starting_balance = client.get_balance().await;
     info!(?starting_balance, "Starting balance");
 
-    assert!(
-        client
-            .get_first_module::<WalletClientModule>()?
-            .btc_tx_has_no_size_limit()
-            .await?
-    );
+    await_consensus_upgrade(&client).await;
 
     let wallet_module = &client.get_first_module::<WalletClientModule>()?;
     let (op, address, tweak_idx) = wallet_module
```
