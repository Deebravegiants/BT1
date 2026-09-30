# [?] fix(mint-client): add no-timeout OOB spend mode (#8740)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-06-24
Source: https://github.com/fedimint/fedimint/commit/25f817be488764c062d6609144226a69f3b213fe
Type: security-commit

## Details
fix(mint-client): add no-timeout OOB spend mode (#8740)

Summary

Adds an opt-in no-timeout mode for Mint v1 out-of-band spends. Passing
`None` as the `try_cancel_after` argument to `spend_notes_with_selector`
disables automatic recovery/refund and makes `subscribe_spend_notes`
report the spend as complete immediately. Existing timeout callers pass
`Some(timeout)`.

Details

This keeps the API surface to one method while avoiding a public magic
timeout value. The no-timeout mode is recorded as a defaulted JSON
metadata field on `MintOperationMetaVariant::SpendOOB`, so old operation
metadata remains readable. In no-timeout mode, the spend still
atomically removes the notes and logs the OOB send event, but it does
not register an OOB refund state machine. `subscribe_spend_notes` yields
`Created` then `Success` directly, and `await_spend_oob_refund` returns
an empty `transaction_ids` list for this mode.

Reviewing

Potential problems to think through:

- In no-timeout mode the sender intentionally gives up both automatic
and manual reclaim through the OOB spend state machine. If the recipient
never reissues the notes, the normal timeout recovery safety net is
absent.
- The mode is tracked in operation-log JSON metadata, not in the OOB
state-machine encoding, so this avoids adding new persisted OOB state
variants.
- The `OOBNotesSpent` event timeout is now `Option<Duration>` and is
`None` when automatic refund is disabled.

Testing

- `just format`
- `cargo check -q -p fedimint-mint-client`
- `cargo test -q -p fedimint-mint-client
spend_oob_meta_no_timeout_defaults_to_false`
- `cargo test -q -p fedimint-mint-tests
sends_ecash_out_of_band_no_timeout_finishes_without_refund`
- `cargo check -q -p fedimint-cli -p fedimint-load-test-tool -p
fedimint-wasm-tests`
- Previous run before simplification: `just final-lint`
- CI backwards-compatibility and upgrade jobs passed before the squash;
they are rerunning on the updated commit.

Prompted by discussion on #8731.

### fedimint-cli/src/client.rs
```diff
@@ -273,7 +273,7 @@ pub async fn handle_command(
                     .spend_notes_with_selector(
                         &SelectNotesWithAtleastAmount,
                         amount,
-                        timeout,
+                        Some(timeout),
                         include_invite,
                         (),
                     )
@@ -294,7 +294,7 @@ pub async fn handle_command(
                     .spend_notes_with_selector(
                         &SelectNotesWithExactAmount,
                         amount,
-                        timeout,
+                        Some(timeout),
                         include_invite,
                         (),
                     )
```

### fedimint-load-test-tool/src/common.rs
```diff
@@ -98,7 +98,7 @@ pub async fn do_spend_notes(
         .spend_notes_with_selector(
             &SelectNotesWithAtleastAmount,
             amount,
-            Duration::from_mins(10),
+            Some(Duration::from_mins(10)),
             false,
             (),
         )
```

### fedimint-wasm-tests/src/lib.rs
```diff
@@ -274,7 +274,7 @@ mod tests {
             .spend_notes_with_selector(
                 &SelectNotesWithAtleastAmount,
                 Amount::from_sats(11),
-                Duration::from_secs(10000),
+                Some(Duration::from_secs(10000)),
                 false,
                 (),
             )
@@ -309,7 +309,7 @@ mod tests {
                 .spend_notes_with_selector(
                     &SelectNotesWithAtleastAmount,
                     amount,
-                    Duration::from_secs(10000),
+                    Some(Duration::from_secs(10000)),
                     false,
                     (),
                 )
```

### modules/fedimint-mint-client/src/cli.rs
```diff
@@ -74,7 +74,7 @@ async fn spend(
             .spend_notes_with_selector(
                 &SelectNotesWithAtleastAmount,
                 amount,
-                timeout,
+                Some(timeout),
                 include_invite,
                 (),
             )
@@ -90,7 +90,7 @@ async fn spend(
         mint.spend_notes_with_selector(
             &SelectNotesWithExactAmount,
             amount,
-            timeout,
+            Some(timeout),
             include_invite,
             (),
         )
```

### modules/fedimint-mint-client/src/events.rs
```diff
@@ -43,8 +43,9 @@ pub struct OOBNotesSpent {
     /// The actual amount of ecash spent
     pub spent_amount: Amount,
 
-    /// The timeout before attempting to refund
-    pub timeout: Duration,
+    /// The timeout before attempting to refund, or `None` if automatic refund
+    /// is disabled.
+    pub timeout: Option<Duration>,
 
     /// Boolean that indicates if the invite code was included in the note
     /// serialization
```

### modules/fedimint-mint-client/src/lib.rs
```diff
@@ -97,7 +97,6 @@ use futures::{StreamExt, pin_mut};
 use hex::ToHex;
 use input::MintInputStateCreatedBundle;
 use itertools::Itertools as _;
-use oob::MintOOBStatesCreatedMulti;
 use output::MintOutputStatesCreatedMulti;
 use serde::{Deserialize, Serialize};
 use strum::IntoEnumIterator;
@@ -111,13 +110,15 @@ use crate::client_db::{
     NextECashNoteIndexKeyPrefix, NoteKey,
 };
 use crate::input::{MintInputCommon, MintInputStateMachine, MintInputStates};
-use crate::oob::{MintOOBStateMachine, MintOOBStates};
+use crate::oob::{MintOOBStateMachine, MintOOBStates, MintOOBStatesCreatedMulti};
 use crate::output::{
     MintOutputCommon, MintOutputStateMachine, MintOutputStates, NoteIssuanceRequest,
 };
 
 const MINT_E_CASH_TYPE_CHILD_ID: ChildId = ChildId(0);
 
+const OOB_SPEND_NO_TIMEOUT: Duration = Duration::MAX;
+
 #[derive(Clone)]
 struct PeerSelector {
     latency: Arc<RwLock<BTreeMap<PeerId, Duration>>>,
@@ -550,6 +551,8 @@ pub enum MintOperationMetaVariant {
     SpendOOB {
         requested_amount: Amount,
         oob_notes: OOBNotes,
+        #[serde(default)]
+        no_timeout: bool,
     },
 }
 
@@ -1205,15 +1208,15 @@ struct SubscribeReissueExternalNotesRequest {
 #[derive(Deserialize)]
 struct SpendNotesExpertRequest {
     min_amount: Amount,
-    try_cancel_after: Duration,
+    try_cancel_after: Option<Duration>,
     include_invite: bool,
     extra_meta: serde_json::Value,
 }
 
 #[derive(Deserialize)]
 struct SpendNotesRequest {
     amount: Amount,
-    try_cancel_after: Duration,
+    try_cancel_after: Option<Duration>,
     include_invite: bool,
     extra_meta: serde_json::Value,
 }
@@ -1587,7 +1590,7 @@ impl MintClientModule {
         dbtx: &mut DatabaseTransaction<'_>,
         notes_selector: &impl NotesSelector,
         amount: Amount,
-        try_cancel_after: Duration,
+        try_cancel_after: Option<Duration>,
     ) -> anyhow::Result<(
         OperationId,
         Vec<MintClientStateMachines>,
@@ -1611,18 +1614,45 @@ impl MintClientModule {
         let sender = self.balance_update_sender.clone();
         dbtx.on_commit(move || sender.send_replace(()));
 
-        let state_machines = vec![MintClientStateMachines::OOB(MintOOBStateMachine {
-            operation_id,
-            state: MintOOBStates::CreatedMulti(MintOOBStatesCreatedMulti {
-                spendable_notes: selected_notes.clone().into_iter_items().collect(),
-                timeout: fedimint_core::time::now() + try_cancel_after,
-            }),
-        })];
+        let try_cancel_after = try_cancel_after.unwrap_or(OOB_SPEND_NO_TIMEOUT);
+        let state_machines = if try_cancel_after == OOB_SPEND_NO_TIMEOUT {
+            vec![]
+        } else {
+            vec![MintClientStateMachines::OOB(MintOOBStateMachine {
+                operation_id,
+                state: MintOOBStates::CreatedMulti(MintOOBStatesCreatedMulti {
+                    spendable_notes: selected_notes.clone().into_iter_items().collect(),
+                    timeout: fedimint_core::time::now() + try_cancel_after,
+                }),
+            })]
+        };
 
         Ok((operation_id, state_machines, selected_notes))
     }
 
+    async fn is_no_timeout_oob_spend(&self, operation_id: OperationId) -> anyhow::Result<bool> {
+        let operation = self.mint_operation(operation_id).await?;
+        let MintOperationMetaVariant::SpendOOB { no_timeout, .. } =
+            operation.meta::<MintOperationMeta>().variant
+        else {
+            bail!("Operation is not a out-of-band spend");
+        };
+
+        Ok(no_timeout)
+    }
+
     pub async fn await_spend_oob_refund(&self, operation_id: OperationId) -> SpendOOBRefund {
+        if self
+            .is_no_timeout_oob_spend(operation_id)
+            .await
+            .unwrap_or(false)
+        {
+            return SpendOOBRefund {
+                user_triggered: false,
+                transaction_ids: vec![],
+            };
+        }
+
         Box::pin(
             self.notifier
                 .subscribe(operation_id)
@@ -1945,15 +1975,16 @@ impl MintClientModule {
     /// users forgetting about failed out-of-band transactions. The timeout
     /// should be chosen such that the recipient (who is potentially offline at
     /// the time of receiving the e-cash notes) had a reasonable timeframe to
-    /// come online and reissue the notes themselves.
+    /// come online and reissue the notes themselves. Pass `None` to disable
+    /// automatic cancellation.
     #[deprecated(
         since = "0.5.0",
         note = "Use `spend_notes_with_selector` instead, with `SelectNotesWithAtleastAmount` to maintain the same behavior"
     )]
     pub async fn spend_notes<M: Serialize + Send>(
         &self,
         min_amount: Amount,
-        try_cancel_after: Duration,
+        try_cancel_after: Option<Duration>,
         include_invite: bool,
         extra_meta: M,
     ) -> anyhow::Result<(OperationId, OOBNotes)> {
@@ -1981,12 +2012,13 @@ impl MintClientModule {
     /// users forgetting about failed out-of-band transactions. The timeout
     /// should be chosen such that the recipient (who is potentially offline at
     /// the time of receiving the e-cash notes) had a reasonable timeframe to
-    /// come online and reissue the notes themselves.
+    /// come online and reissue the notes themselves. Pass `None` to disable
+    /// automatic cancellation.
     pub async fn spend_notes_with_selector<M: Serialize + Send>(
         &self,
         notes_selector: &impl NotesSelector,
         requested_amount: Amount,
-        try_cancel_after: Duration,
+        try_cancel_after: Option<Duration>,
         include_invite: bool,
         extra_meta: M,
     ) -> anyhow::Result<(OperationId, OOBNotes)> {
@@ -2000,6 +2032,7 @@ impl MintClientModule {
                 |dbtx, _| {
                     let extra_meta = extra_meta.clone();
                     Box::pin(async {
+                        let no_timeout = try_cancel_after.is_none();
                         let (operation_id, states, notes) = self
                             .spend_notes_oob(
                                 dbtx,
@@ -2033,6 +2066,7 @@ impl MintClientModule {
                                     variant: MintOperationMetaVariant::SpendOOB {
                                         requested_amount,
                                         oob_notes: oob_notes.clone(),
+                                        no_timeout,
                                     },
                                     amount: oob_notes.total_amount(),
                                     extra_meta,
@@ -2252,6 +2286,7 @@ impl MintClientModule {
                     variant: MintOperationMetaVariant::SpendOOB {
                         requested_amount: amount,
                         oob_notes: oob_notes.clone(),
+                        no_timeout: true,
                     },
                     amount: oob_notes.total_amount(),
                     extra_meta,
@@ -2348,12 +2383,11 @@ impl MintClientModule {
         operation_id: OperationId,
     ) -> anyhow::Result<UpdateStreamOrOutcome<SpendOOBState>> {
         let operation = self.mint_operation(operation_id).await?;
-        if !matches!(
-            operation.meta::<MintOperationMeta>().variant,
-            MintOperationMetaVariant::SpendOOB { .. }
-        ) {
+        let MintOperationMetaVariant::SpendOOB { no_timeout, .. } =
+            operation.meta::<MintOperationMeta>().variant
+        else {
             bail!("Operation is not a out-of-band spend");
-        }
+        };
 
         let client_ctx = self.client_ctx.clone();
 
@@ -2363,6 +2397,11 @@ impl MintClientModule {
                 stream! {
                     yield SpendOOBState::Created;
 
+                    if no_timeout {
+                        yield SpendOOBState::Success;
+                        return;
+                    }
+
                     let self_ref = client_ctx.self_ref();
 
                     let refund = self_ref
@@ -2499,6 +2538,8 @@ pub fn spendable_notes_to_operation_id(
 #[derive(Debug, Serialize, Deserialize, Clone)]
 pub struct SpendOOBRefund {
     pub user_triggered: bool,
+    /// Empty when the spend disabled automatic refunds and no refund was
+    /// attempted.
     pub transaction_ids: Vec<TransactionId>,
 }
 
@@ -3353,4 +3394,47 @@ mod tests {
             })
         );
     }
+
+    #[test]
+    fn spend_oob_meta_no_timeout_defaults_to_false() {
+        let notes = vec![(
+            Amount::from_sats(1),
+            SpendableNote::consensus_decode_hex("a5dd3ebacad1bc48bd8718eed5a8da1d68f91323bef2848ac4fa2e6f8eed710f3178fd4aef047cc234e6b1127086f33cc408b39818781d9521475360de6b205f3328e490a6d99d5e2553a4553207c8bd", &ModuleRegistry::default()).unwrap(),
+        )]
+        .into_iter()
+        .collect::<TieredMulti<_>>();
+        let oob_notes = OOBNotes::new(FederationId::dummy().to_prefix(), notes);
+        let mut old_meta_json = serde_json::to_value(MintOperationMetaVariant::SpendOOB {
+            requested_amount: Amount::from_sats(42),
+            oob_notes: oob_notes.clone(),
+            no_timeout: false,
+        })
+        .expect("serializing always works");
+        old_meta_json
+            .get_mut("spend_o_o_b")
+            .expect("spend OOB variant should serialize as spend_o_o_b")
+            .as_object_mut()
+            .expect("spend OOB variant should serialize to an object")
+            .remove("no_timeout");
+        assert_eq!(
+            old_meta_json,
+            json!({
+                "spend_o_o_b": {
+                    "requested_amount": Amount::from_sats(42),
+                    "oob_notes": oob_notes.clone(),
+                }
+            })
+        );
+
+        let old_meta: MintOperationMetaVariant =
+            serde_json::from_value(old_meta_json).expect("parsing old spend OOB meta failed");
+        assert_eq!(
+            old_meta,
+            MintOperationMetaVariant::SpendOOB {
+                requested_amount: Amount::from_sats(42),
+                oob_notes,
+                no_timeout: false,
+            }
+        );
+    }
 }
```

### modules/fedimint-mint-tests/tests/tests.rs
```diff
@@ -131,7 +131,13 @@ async fn sends_ecash_out_of_band() -> anyhow::Result<()> {
     let client2_mint = client2.get_first_module::<MintClientModule>()?;
     info!("### SPEND NOTES");
     let (op, notes) = client1_mint
-        .spend_notes_with_selector(&SelectNotesWithAtleastAmount, sats(750), TIMEOUT, false, ())
+        .spend_notes_with_selector(
+            &SelectNotesWithAtleastAmount,
+            sats(750),
+            Some(TIMEOUT),
+            false,
+            (),
+        )
         .await?;
     let sub1 = &mut client1_mint.subscribe_spend_notes(op).await?.into_stream();
     assert_eq!(sub1.ok().await?, SpendOOBState::Created);
@@ -194,7 +200,7 @@ async fn reissue_fee_quote_matches_actual_fee() -> anyhow::Result<()> {
             .spend_notes_with_selector(
                 &SelectNotesWithAtleastAmount,
                 sats(1_000),
-                TIMEOUT,
+                Some(TIMEOUT),
                 false,
                 (),
             )
@@ -368,7 +374,7 @@ async fn sends_ecash_oob_highly_parallel() -> anyhow::Result<()> {
                     .spend_notes_with_selector(
                         &SelectNotesWithAtleastAmount,
                         sats(30),
-                        ECASH_TIMEOUT,
+                        Some(ECASH_TIMEOUT),
                         false,
                         (),
                     )
@@ -502,7 +508,13 @@ async fn sends_ecash_out_of_band_cancel() -> anyhow::Result<()> {
     // Spend from client1 to client2
     let mint_module = client.get_first_module::<MintClientModule>()?;
     let (op, _) = mint_module
-        .spend_notes_with_selector(&SelectNotesWithAtleastAmount, sats(750), TIMEOUT, false, ())
+        .spend_notes_with_selector(
+            &SelectNotesWithAtleastAmount,
+            sats(750),
+            Some(TIMEOUT),
+            false,
+            (),
+        )
         .await?;
     let sub1 = &mut mint_module.subscribe_spend_notes(op).await?.into_stream();
     assert_eq!(sub1.ok().await?, SpendOOBState::Created);
@@ -527,6 +539,24 @@ async fn sends_ecash_out_of_band_cancel() -> anyhow::Result<()> {
     panic!("Did not receive refund in time");
 }
 
+#[tokio::test(flavor = "multi_thread")]
+async fn sends_ecash_out_of_band_no_timeout_finishes_without_refund() -> anyhow::Result<()> {
+    let fed = fixtures().new_fed_degraded().await;
+    let client = fed.new_client().await;
+    issue_ecash(&client, sats(1000)).await?;
+
+    let mint_module = client.get_first_module::<MintClientModule>()?;
+    let (op, _) = mint_module
+        .spend_notes_with_selector(&SelectNotesWithAtleastAmount, sats(750), None, false, ())
+        .await?;
+
+    let sub = &mut mint_module.subscribe_spend_notes(op).await?.into_stream();
+    assert_eq!(sub.ok().await?, SpendOOBState::Created);
+    assert_eq!(sub.ok().await?, SpendOOBState::Success);
+
+    Ok(())
+}
+
 #[tokio::test(flavor = "multi_thread")]
 async fn sends_ecash_out_of_band_cancel_partial() -> anyhow::Result<()> {
     let fed = fixtures().new_fed_degraded().await;
@@ -543,7 +573,7 @@ async fn sends_ecash_out_of_band_cancel_partial() -> anyhow::Result<()> {
         .spend_notes_with_selector(
             &SelectNotesWithAtleastAmount,
             sats(750),
-            TIMEOUT * 3,
+            Some(TIMEOUT * 3),
             false,
             (),
         )
@@ -618,7 +648,7 @@ async fn error_zero_value_oob_spend() -> anyhow::Result<()> {
         .spend_notes_with_selector(
             &SelectNotesWithAtleastAmount,
             Amount::ZERO,
-            TIMEOUT,
+            Some(TIMEOUT),
             false,
             (),
         )
@@ -846,7 +876,7 @@ async fn repair_wallet() -> anyhow::Result<()> {
             .spend_notes_with_selector(
                 &SelectNotesWithExactAmount,
                 Amount::from_msats(1),
-                TIMEOUT,
+                Some(TIMEOUT),
                 false,
                 (),
             )
```
