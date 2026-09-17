# [?] [security] make coin reservation rewriter fallible to fix dryRun/devInspect panic (#26528)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-05-07
Source: https://github.com/MystenLabs/sui/commit/9e52010210244236dc824d74e74b40eb1a604ab0
Type: security-commit

## Details
[security] make coin reservation rewriter fallible to fix dryRun/devInspect panic (#26528)

## Summary

`rewrite_transaction_for_coin_reservations` previously called
`.unwrap()` on the coin-reservation resolution result, assuming the
input had been validated upstream. That assumption holds for certified
transactions but **not** for `dryRunTransactionBlock` and
`devInspectTransactionBlock`, which accept arbitrary client-supplied
transaction kinds without prior reservation validation. A client could
submit a fake coin reservation (an `ImmOrOwnedObject` whose `ObjectRef`
matches the masked-coin-reservation encoding but references a
non-existent accumulator) and panic the fullnode thread handling the
dry-run.

This PR:

- Makes `rewrite_transaction_for_coin_reservations` return
`UserInputResult<Option<Vec<bool>>>` so the resolver error surfaces as a
normal user-input error.
- Plumbs the result through both certificate execution (where we still
`expect()` since validation guarantees success) and the dry-run /
dev-inspect paths (where the error is propagated to the client).
- Moves rewriting out of the inner `execute_transaction_to_effects`
helper into each caller, since the certificate path can panic on failure
while the dry-run paths must not.
- Adds 4 e2e simtests under `address_balance_compatibility_tests`:
  - `test_fake_coin_reservation_dry_run_does_not_panic`
  - `test_fake_coin_reservation_dev_inspect_does_not_panic`
  - `test_fake_coin_reservation_dry_run_safe_when_flag_disabled`
  - `test_fake_coin_reservation_dev_inspect_safe_when_flag_disabled`

## Verification

Reverted the fix locally (test commit only) and ran the new tests:
```
FAIL sui-e2e-tests::address_balance_compatibility_tests test_fake_coin_reservation_dev_inspect_does_not_panic
FAIL sui-e2e-tests::address_balance_compatibility_tests test_fake_coin_reservation_dry_run_does_not_panic
PASS sui-e2e-tests::address_balance_compatibility_tests test_fake_coin_reservation_dev_inspect_safe_when_flag_disabled
PASS sui-e2e-tests::address_balance_compatibility_tests test_fake_coin_reservation_dry_run_safe_when_flag_disabled
```
panicking at `rewrite_transaction_for_coin_reservations` with
`InvalidWithdrawReservation { error: "coin reservation object id 0x...
not found" }`.

Reapplied the fix and reran:
```
4 tests run: 4 passed
```

## Test plan

- [x] `cargo simtest -p sui-e2e-tests --test
address_balance_compatibility_tests test_fake_coin_reservation` (4/4
pass)
- [ ] CI green

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Mark Logan <mark@marklgn.com>
Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

### crates/sui-core/src/accumulators/transaction_rewriting.rs
```diff
@@ -4,25 +4,24 @@
 use sui_types::base_types::{SequenceNumber, SuiAddress};
 use sui_types::coin_reservation::{CoinReservationResolverTrait, ParsedObjectRefWithdrawal};
 use sui_types::digests::ChainIdentifier;
+use sui_types::error::UserInputResult;
 use sui_types::transaction::{CallArg, ObjectArg, ProgrammableTransaction, TransactionKind};
 
 /// Rewrites coin reservation inputs (fake coins encoded as masked ObjectRefs) into
 /// FundsWithdrawalArgs so the executor can resolve them as balance withdrawals.
 ///
-/// Returns `Some(rewritten_inputs)` if any inputs were rewritten, where each bool indicates whether
-/// the corresponding input was converted from a coin reservation. Returns `None` if nothing
-/// was rewritten.
+/// Returns `Ok(Some(rewritten))` where each bool flags whether that input was rewritten,
+/// `Ok(None)` if nothing was rewritten, or `Err` if a reservation cannot be resolved.
 ///
-/// `accumulator_version` is the version of the accumulator root object to use for MVCC lookup.
-/// This is required during checkpoint replay to read the accumulator state at the correct version,
-/// before any settlement transactions have modified it.
+/// `accumulator_version` selects the accumulator version for MVCC lookup during checkpoint
+/// replay (read before any settlement modifies it); pass `None` for the latest version.
 pub fn rewrite_transaction_for_coin_reservations(
     chain_identifier: ChainIdentifier,
     coin_reservation_resolver: &dyn CoinReservationResolverTrait,
     sender: SuiAddress,
     transaction_kind: &mut TransactionKind,
     accumulator_version: Option<SequenceNumber>,
-) -> Option<Vec<bool>> {
+) -> UserInputResult<Option<Vec<bool>>> {
     match transaction_kind {
         TransactionKind::ProgrammableTransaction(pt) => {
             rewrite_programmable_transaction_for_coin_reservations(
@@ -33,7 +32,7 @@ pub fn rewrite_transaction_for_coin_reservations(
                 accumulator_version,
             )
         }
-        _ => None,
+        _ => Ok(None),
     }
 }
 
@@ -43,9 +42,9 @@ fn rewrite_programmable_transaction_for_coin_reservations(
     sender: SuiAddress,
     pt: &mut ProgrammableTransaction,
     accumulator_version: Option<SequenceNumber>,
-) -> Option<Vec<bool>> {
+) -> UserInputResult<Option<Vec<bool>>> {
     if pt.coin_reservation_obj_refs().count() == 0 {
-        return None;
+        return Ok(None);
     }
 
     let mut rewritten_inputs = Vec::with_capacity(pt.inputs.len());
@@ -55,22 +54,16 @@ fn rewrite_programmable_transaction_for_coin_reservations(
         {
             rewritten_inputs.push(true);
 
-            // unwrap: This cannot fail because:
-            // 1. Coin reservations are validated in `process_funds_withdrawals_for_signing` before
-            //    execution, which checks that the accumulator exists and is owned by the sender.
-            // 2. The scheduler reserves funds before allowing the transaction to execute. If the
-            //    accumulator were deleted (balance dropped to 0), the reservation would fail and
-            //    the transaction would not enter execution.
-            // 3. During checkpoint replay with MVCC, we read the accumulator at the version before
-            //    any settlement transactions have modified it.
-            let withdraw = coin_reservation_resolver
-                .resolve_funds_withdrawal(sender, parsed, accumulator_version)
-                .unwrap();
+            let withdraw = coin_reservation_resolver.resolve_funds_withdrawal(
+                sender,
+                parsed,
+                accumulator_version,
+            )?;
             *input = CallArg::FundsWithdrawal(withdraw);
         } else {
             rewritten_inputs.push(false);
         }
     }
 
-    Some(rewritten_inputs)
+    Ok(Some(rewritten_inputs))
 }
```

### crates/sui-core/src/authority.rs
```diff
@@ -1884,9 +1884,8 @@ impl AuthorityState {
         );
     }
 
-    /// Helper function that handles transaction rewriting for coin reservations and executes
-    /// the transaction to effects. Returns the execution results along with the command offset
-    /// used for rewriting failure command indices.
+    /// Runs the executor on an already-prepared transaction; the caller is responsible for any
+    /// coin reservation rewriting.
     fn execute_transaction_to_effects(
         &self,
         executor: &dyn Executor,
@@ -1899,32 +1898,17 @@ impl AuthorityState {
         input_objects: CheckedInputObjects,
         gas_data: GasData,
         gas_status: SuiGasStatus,
-        sender: SuiAddress,
-        mut kind: TransactionKind,
+        kind: TransactionKind,
+        rewritten_inputs: Option<Vec<bool>>,
         signer: SuiAddress,
         tx_digest: TransactionDigest,
-        accumulator_version: Option<SequenceNumber>,
     ) -> (
         InnerTemporaryStore,
         SuiGasStatus,
         TransactionEffects,
         Vec<ExecutionTiming>,
         Result<(), ExecutionError>,
     ) {
-        // Skip rewriting if execution_params already indicates an error - the transaction will fail
-        // anyway, and trying to rewrite could fail if the accumulator was deleted.
-        let rewritten_inputs = if execution_params.is_ok() {
-            rewrite_transaction_for_coin_reservations(
-                self.chain_identifier,
-                &*self.coin_reservation_resolver,
-                sender,
-                &mut kind,
-                accumulator_version,
-            )
-        } else {
-            None
-        };
-
         let (inner_temp_store, gas_status, effects, timings, execution_error) = executor
             // TODO only run this function on FullNodes, use `execute_transaction_to_effects` on validators.
             .execute_transaction_to_effects_and_execution_error(
@@ -2008,7 +1992,7 @@ impl AuthorityState {
         let protocol_config = epoch_store.protocol_config();
         let transaction_data = &certificate.data().intent_message().value;
         let sender = transaction_data.sender();
-        let (kind, signer, gas_data) = transaction_data.execution_parts();
+        let (mut kind, signer, gas_data) = transaction_data.execution_parts();
         let early_execution_error = get_early_execution_error(
             &tx_digest,
             &input_objects,
@@ -2020,6 +2004,21 @@ impl AuthorityState {
             None => ExecutionOrEarlyError::Ok(()),
         };
 
+        // Skip on early error: the tx will fail anyway and rewriting may fail if the accumulator
+        // was deleted.
+        let rewritten_inputs = if execution_params.is_ok() {
+            rewrite_transaction_for_coin_reservations(
+                self.chain_identifier,
+                &*self.coin_reservation_resolver,
+                sender,
+                &mut kind,
+                execution_env.assigned_versions.accumulator_version,
+            )
+            .expect("rewriting must succeed for a certified transaction")
+        } else {
+            None
+        };
+
         let tracking_store = TrackingBackingStore::new(self.get_backing_store().as_ref());
 
         #[allow(unused_mut)]
@@ -2042,11 +2041,10 @@ impl AuthorityState {
                 input_objects,
                 gas_data,
                 gas_status,
-                sender,
                 kind,
+                rewritten_inputs,
                 signer,
                 tx_digest,
-                execution_env.assigned_versions.accumulator_version,
             );
 
         let object_funds_checker = self.object_funds_checker.load();
@@ -2352,7 +2350,7 @@ impl AuthorityState {
         };
 
         let protocol_config = epoch_store.protocol_config();
-        let (kind, signer, _) = transaction.execution_parts();
+        let (mut kind, signer, _) = transaction.execution_parts();
 
         let silent = true;
         let executor = sui_execution::executor(protocol_config, silent)
@@ -2375,6 +2373,20 @@ impl AuthorityState {
             None => ExecutionOrEarlyError::Ok(()),
         };
 
+        // Skip on early error: the tx will fail anyway.
+        let rewritten_inputs = if execution_params.is_ok() {
+            rewrite_transaction_for_coin_reservations(
+                self.chain_identifier,
+                &*self.coin_reservation_resolver,
+                transaction.sender(),
+                &mut kind,
+                // dry run reads the latest accumulator
+                None,
+            )?
+        } else {
+            None
+        };
+
         let (inner_temp_store, _, effects, _timings, execution_error) = self
             .execute_transaction_to_effects(
                 executor.as_ref(),
@@ -2390,12 +2402,10 @@ impl AuthorityState {
                 checked_input_objects,
                 gas_data,
                 gas_status,
-                transaction.sender(),
                 kind,
+                rewritten_inputs,
                 signer,
                 transaction_digest,
-                // Use latest accumulator version for dry run/dev inspect
-                None,
             );
 
         let tx_digest = *effects.transaction_digest();
@@ -2609,7 +2619,7 @@ impl AuthorityState {
             signer,
             &mut kind,
             None,
-        );
+        )?;
         let early_execution_error = get_early_execution_error(
             &transaction.digest(),
             &checked_input_objects,
@@ -2927,7 +2937,7 @@ impl AuthorityState {
             sender,
             &mut transaction_kind,
             None,
-        );
+        )?;
         let (inner_temp_store, _, effects, execution_result) = executor.dev_inspect_transaction(
             self.get_backing_store().as_ref(),
             protocol_config,
```

### crates/sui-e2e-tests/tests/address_balance_compatibility_tests.rs
```diff
@@ -8,9 +8,14 @@ use sui_test_transaction_builder::{FundSource, TestTransactionBuilder};
 use sui_types::{
     base_types::{FullObjectRef, ObjectID, SequenceNumber, SuiAddress},
     coin_reservation::ParsedObjectRefWithdrawal,
-    digests::CheckpointDigest,
+    crypto::default_hash,
+    digests::{CheckpointDigest, TransactionDigest},
     effects::TransactionEffectsAPI,
-    transaction::{Argument, CallArg, Command, ObjectArg, TransactionDataAPI, TransactionKind},
+    programmable_transaction_builder::ProgrammableTransactionBuilder,
+    transaction::{
+        Argument, CallArg, Command, GasData, ObjectArg, TransactionData, TransactionDataAPI,
+        TransactionDataV1, TransactionExpiration, TransactionKind,
+    },
 };
 use test_cluster::addr_balance_test_env::{TestEnvBuilder, get_sui_accumulator_object_id};
 
@@ -1363,3 +1368,239 @@ async fn test_mix_coin_reservations_real_coins_and_shared_object() {
 
     test_env.cluster.trigger_reconfiguration().await;
 }
+
+fn build_fake_coin_reservation_pt(
+    chain_id: sui_types::digests::ChainIdentifier,
+) -> TransactionKind {
+    let bogus_accumulator_id = ObjectID::random();
+    let fake_coin_res = ParsedObjectRefWithdrawal::new(bogus_accumulator_id, 0, 100)
+        .encode(SequenceNumber::new(), chain_id);
+
+    let mut pt_builder = ProgrammableTransactionBuilder::new();
+    let coin_arg = pt_builder
+        .obj(ObjectArg::ImmOrOwnedObject(fake_coin_res))
+        .unwrap();
+    let recipient_arg = pt_builder
+        .pure(SuiAddress::random_for_testing_only())
+        .unwrap();
+    pt_builder.command(Command::TransferObjects(vec![coin_arg], recipient_arg));
+    TransactionKind::ProgrammableTransaction(pt_builder.finish())
+}
+
+#[sim_test]
+async fn test_fake_coin_reservation_dry_run_does_not_panic() {
+    if has_mainnet_protocol_config_override() {
+        return;
+    }
+    let test_env = TestEnvBuilder::new()
+        .with_proto_override_cb(Box::new(|_, mut cfg| {
+            cfg.enable_coin_reservation_for_testing();
+            cfg
+        }))
+        .build()
+        .await;
+
+    let (sender, gas) = test_env.get_sender_and_gas(0);
+    let kind = build_fake_coin_reservation_pt(test_env.chain_id);
+    let tx_data = TransactionData::V1(TransactionDataV1 {
+        kind,
+        sender,
+        gas_data: GasData {
+            payment: vec![gas],
+            owner: sender,
+            price: test_env.rgp,
+            budget: 5_000_000_000,
+        },
+        expiration: TransactionExpiration::None,
+    });
+    let digest = TransactionDigest::new(default_hash(&tx_data));
+
+    let state = test_env
+        .cluster
+        .fullnode_handle
+        .sui_node
+        .with(|node| node.state().clone());
+    let join = tokio::task::spawn(async move { state.dry_exec_transaction(tx_data, digest).await });
+
+    match join.await {
+        Ok(Ok(_)) => panic!("dry-run with fake coin reservation should have errored"),
+        Ok(Err(e)) => {
+            let msg = e.to_string();
+            assert!(
+                msg.contains("InvalidWithdrawReservation") || msg.contains("not found"),
+                "unexpected error: {msg}"
+            );
+        }
+        Err(join_err) if join_err.is_panic() => {
+            panic!(
+                "dryRunTransactionBlock panicked on fake coin reservation: {:?}",
+                join_err
+            );
+        }
+        Err(e) => panic!("unexpected join error: {e:?}"),
+    }
+}
+
+#[sim_test]
+async fn test_fake_coin_reservation_dev_inspect_does_not_panic() {
+    if has_mainnet_protocol_config_override() {
+        return;
+    }
+    let test_env = TestEnvBuilder::new()
+        .with_proto_override_cb(Box::new(|_, mut cfg| {
+            cfg.enable_coin_reservation_for_testing();
+            cfg
+        }))
+        .build()
+        .await;
+
+    let sender = test_env.get_sender(0);
+    let tx_kind = build_fake_coin_reservation_pt(test_env.chain_id);
+
+    let state = test_env
+        .cluster
+        .fullnode_handle
+        .sui_node
+        .with(|node| node.state().clone());
+    let join = tokio::task::spawn(async move {
+        state
+            .dev_inspect_transaction_block(
+                sender,
+                tx_kind,
+                None,
+                None,
+                None,
+                None,
+                None,
+                /* skip_checks */ Some(true),
+            )
+            .await
+    });
+
+    match join.await {
+        Ok(Ok(_)) => panic!("dev-inspect with fake coin reservation should have errored"),
+        Ok(Err(e)) => {
+            let msg = e.to_string();
+            assert!(
+                msg.contains("InvalidWithdrawReservation") || msg.contains("not found"),
+                "unexpected error: {msg}"
+            );
+        }
+        Err(join_err) if join_err.is_panic() => {
+            panic!(
+                "devInspectTransactionBlock panicked on fake coin reservation: {:?}",
+                join_err
+            );
+        }
+        Err(e) => panic!("unexpected join error: {e:?}"),
+    }
+}
+
+#[sim_test]
+async fn test_fake_coin_reservation_dry_run_safe_when_flag_disabled() {
+    if has_mainnet_protocol_config_override() {
+        return;
+    }
+    let test_env = TestEnvBuilder::new()
+        .with_proto_override_cb(Box::new(|_, mut cfg| {
+            cfg.disable_coin_reservation_for_testing();
+            cfg
+        }))
+        .build()
+        .await;
+
+    let (sender, gas) = test_env.get_sender_and_gas(0);
+    let kind = build_fake_coin_reservation_pt(test_env.chain_id);
+    let tx_data = TransactionData::V1(TransactionDataV1 {
+        kind,
+        sender,
+        gas_data: GasData {
+            payment: vec![gas],
+            owner: sender,
+            price: test_env.rgp,
+            budget: 5_000_000_000,
+        },
+        expiration: TransactionExpiration::None,
+    });
+    let digest = TransactionDigest::new(default_hash(&tx_data));
+
+    let state = test_env
+        .cluster
+        .fullnode_handle
+        .sui_node
+        .with(|node| node.state().clone());
+    let join = tokio::task::spawn(async move { state.dry_exec_transaction(tx_data, digest).await });
+
+    match join.await {
+        Ok(Ok(_)) => panic!("dry-run with fake coin reservation should have errored"),
+        Ok(Err(e)) => {
+            assert!(
+                e.to_string()
+                    .contains("coin reservation backward compatibility layer is not enabled"),
+                "expected gating rejection, got: {e}"
+            );
+        }
+        Err(join_err) if join_err.is_panic() => {
+            panic!(
+                "dryRunTransactionBlock panicked with coin reservation flag disabled: {:?}",
+                join_err
+            );
+        }
+        Err(e) => panic!("unexpected join error: {e:?}"),
+    }
+}
+
+#[sim_test]
+async fn test_fake_coin_reservation_dev_inspect_safe_when_flag_disabled() {
+    if has_mainnet_protocol_config_override() {
+        return;
+    }
+    let test_env = TestEnvBuilder::new()
+        .with_proto_override_cb(Box::new(|_, mut cfg| {
+            cfg.disable_coin_reservation_for_testing();
+            cfg
+        }))
+        .build()
+        .await;
+
+    let sender = test_env.get_sender(0);
+    let tx_kind = build_fake_coin_reservation_pt(test_env.chain_id);
+
+    let state = test_env
+        .cluster
+        .fullnode_handle
+        .sui_node
+        .with(|node| node.state().clone());
+    let join = tokio::task::spawn(async move {
+        state
+            .dev_inspect_transaction_block(
+                sender,
+                tx_kind,
+                None,
+                None,
+                None,
+                None,
+                None,
+                /* skip_checks */ Some(true),
+            )
+            .await
+    });
+
+    match join.await {
+        Ok(Ok(_)) => panic!("dev-inspect with fake coin reservation should have errored"),
+        Ok(Err(e)) => {
+            assert!(
+                e.to_string()
+                    .contains("coin reservation backward compatibility layer is not enabled"),
+                "expected gating rejection, got: {e}"
+            );
+        }
+        Err(join_err) if join_err.is_panic() => {
+            panic!(
+                "devInspectTransactionBlock panicked with coin reservation flag disabled: {:?}",
+                join_err
+            );
+        }
+        Err(e) => panic!("unexpected join error: {e:?}"),
+    }
+}
```
