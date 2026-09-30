# [?] Land #26816 gas-underflow fix in main (#26828)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-05-29
Source: https://github.com/MystenLabs/sui/commit/124c64e643a2fea059cb369cc6b96b565fadea7d
Type: security-commit

## Details
Land #26816 gas-underflow fix in main (#26828)

## Summary

Lands the address-balance gas-underflow fix from #26816 into `main`.
#26816 went directly to `releases/sui-v1.72.0` as an out-of-band
emergency fix; this brings it to `main`.

On an `InsufficientFundsForWithdraw` early abort, the gas payment's
address-balance entries are pruned before smashing (real coins are
kept). This avoids underflowing the already-drained address balance at
settlement, which otherwise aborts the settlement transaction.

**This is the unconditional fix only.** The follow-up stacked PR adds
the protocol-version + mainnet accumulator-version gating so the rollout
is safe and mainnet replay stays bit-for-bit correct — kept separate so
that gating diff reads cleanly against this fix.

## Test plan

- [x] `cargo check` / `xclippy` on `sui-adapter-latest`
- [x] e2e regression test `test_gas_smash_no_ab_underflow_on_iffw`
- [ ] CI (incl. simtests)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### crates/sui-e2e-tests/tests/address_balance_compatibility_tests.rs
```diff
@@ -1368,6 +1368,94 @@ async fn test_mix_coin_reservations_real_coins_and_shared_object() {
     test_env.cluster.trigger_reconfiguration().await;
 }
 
+/// Regression test: gas smashing must not underflow the address balance on IFFW. TX1 drains the
+/// AB to 0; TX2's gas payment mixes two real coins with a coin reservation and fires IFFW. With
+/// the fix, smashing is skipped (no underflow at settlement, no coins merged/deleted).
+#[sim_test]
+async fn test_gas_smash_no_ab_underflow_on_iffw() {
+    if has_mainnet_protocol_config_override() {
+        return;
+    }
+
+    let mut test_env = TestEnvBuilder::new()
+        .with_proto_override_cb(Box::new(|_, mut cfg| {
+            cfg.enable_coin_reservation_for_testing();
+            cfg
+        }))
+        .build()
+        .await;
+
+    let sender = test_env.get_sender(0);
+
+    // Fund the AB; both per-tx reservations must be ≤ this to pass signing validation.
+    let initial_ab = 20_000_000u64;
+    test_env.fund_one_address_balance(sender, initial_ab).await;
+
+    // Refresh gas list after funding (funding consumes one coin).
+    let mut all_gas = test_env.get_gas_for_sender(sender);
+    assert!(all_gas.len() >= 3, "need ≥3 gas coins");
+
+    // TX1: withdraw all AB (pays gas from a real coin so the full initial_ab is freed).
+    let gas_for_tx1 = all_gas.remove(0);
+    let dummy = SuiAddress::random_for_testing_only();
+    let tx1 = test_env
+        .tx_builder_with_gas(sender, gas_for_tx1)
+        .transfer_sui_to_address_balance(
+            FundSource::address_fund_with_reservation(initial_ab),
+            vec![(initial_ab, dummy)],
+        )
+        .build();
+
+    // TX2: gas_data.payment = [real_coin_a, real_coin_b, coin_reservation].
+    // Using two real coins deliberately exercises the case where smashing would normally
+    // delete real_coin_b — the fix must leave it intact.
+    // Reservation = initial_ab / 2 passes per-tx signing validation (≤ initial_ab) but
+    // exceeds the post-TX1 balance of 0, triggering IFFW.
+    let real_coin_a = all_gas.remove(0);
+    let real_coin_b = all_gas.remove(0);
+    let reservation = initial_ab / 2;
+    let fake_coin = test_env.encode_coin_reservation(sender, 0, reservation);
+    let tx2 = test_env
+        .tx_builder_with_gas_objects(sender, vec![real_coin_a, real_coin_b, fake_coin])
+        .build();
+
+    let tx1_digest = tx1.digest();
+    let tx2_digest = tx2.digest();
+
+    let mut effects = test_env
+        .cluster
+        .sign_and_execute_txns_in_soft_bundle(&[tx1, tx2])
+        .await
+        .unwrap();
+
+    let tx2_effects = effects.pop().unwrap().1;
+    let tx1_effects = effects.pop().unwrap().1;
+
+    assert!(
+        tx1_effects.status().is_ok(),
+        "TX1 should succeed: {:?}",
+        tx1_effects.status()
+    );
+    let status_str = format!("{:?}", tx2_effects.status());
+    assert!(
+        status_str.contains("InsufficientFundsForWithdraw"),
+        "TX2 should fail with InsufficientFundsForWithdraw, got: {status_str}"
+    );
+
+    // Wait for settlement.  Without the fix the settlement transaction aborts trying
+    // to split `reservation` from a 0-balance AB, crashing the node.
+    test_env
+        .cluster
+        .wait_for_tx_settlement(&[tx1_digest, tx2_digest])
+        .await;
+
+    // AB must not have been touched by the failed TX2.
+    let final_ab = test_env.get_sui_balance_ab(sender);
+    assert_eq!(final_ab, 0, "AB should stay 0; got {final_ab}");
+
+    test_env.cluster.trigger_reconfiguration().await;
+}
+
 fn build_fake_coin_reservation_pt(
     chain_id: sui_types::digests::ChainIdentifier,
 ) -> TransactionKind {
```

### sui-execution/latest/sui-adapter/src/execution_engine.rs
```diff
@@ -177,7 +177,7 @@ mod checked {
     pub fn execute_transaction_to_effects<Mode: ExecutionMode>(
         store: &dyn BackingStore,
         input_objects: CheckedInputObjects,
-        gas_data: GasData,
+        mut gas_data: GasData,
         gas_status: SuiGasStatus,
         transaction_kind: TransactionKind,
         rewritten_inputs: Option<Vec<bool>>,
@@ -228,6 +228,20 @@ mod checked {
         let gas_price = gas_status.gas_price();
         let rgp = gas_status.reference_gas_price();
 
+        // On an IFFW abort, drop the address-balance gas payments (keeping real coins) so the
+        // pruned list flows into `payment_kind`/`compute_input_reservations` with no special
+        // handling.
+        if matches!(
+            execution_params,
+            Err(ExecutionErrorKind::InsufficientFundsForWithdraw)
+        ) && gas_data.payment.len() > 1
+            && ParsedDigest::try_from(gas_data.payment[0].2).is_err()
+        {
+            gas_data
+                .payment
+                .retain(|entry| ParsedDigest::try_from(entry.2).is_err());
+        }
+
         let mut gas_charger = GasCharger::new(
             transaction_digest,
             payment_kind(&gas_data, &transaction_kind, protocol_config),
```
