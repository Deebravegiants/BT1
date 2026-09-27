# [?] fix(wallet): reject peg-out amounts that overflow the selection arithmetic

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/03131e9e191379f63ce07e04141dc87432d5b75e
Type: security-commit

## Details
fix(wallet): reject peg-out amounts that overflow the selection arithmetic

`bitcoin::Amount`'s `Add` is `checked_add(..).expect("Amount addition
error")` with no `MAX_MONEY` clamp, and the UTXO selection loop summed
`peg_out_amount + change_script.minimal_non_dust() + fees` with it. Two
routes fed that sum an unvalidated amount:

  * `PEG_OUT_FEES_ENDPOINT` is a public, unauthenticated endpoint that
    hands the caller's raw `u64` to `bitcoin::Amount::from_sat`. A single
    anonymous call with `sats = u64::MAX` panicked the handler.
  * `process_output` passes `peg_out.amount` to `create_peg_out_tx`
    verbatim and only runs `validate_tx` afterwards.

On the iroh transport a panicking handler takes the guardian process
down, so route one alone was a remote kill switch.

Reject amounts above `MAX_MONEY` up front in `create_tx` -- the single
choke point both routes pass through -- and make the loop's target
computation checked, since fees are not bounded by `MAX_MONEY` and grow
with every selected input. Both cases report `NotEnoughSpendableUTXO`,
which is literally accurate: no federation UTXO set can fund an amount
that cannot exist on chain. Reusing the existing variant also keeps
`WalletOutputError` wire-compatible, so older clients still decode the
submission outcome.

Consensus safety of the `process_output` route: turning a panic into a
rejection changes transaction validity, so it has to be argued rather
than assumed. `bitcoin::Amount`'s `Add` panics in every build profile,
so an output whose amount overflowed that sum panicked every guardian at
the same ordered item and panicked them again on every restart,
permanently halting the federation at that session. A federation that is
still running therefore has no such transaction in its history, and the
new rejection can only ever fire on a transaction that would previously
have bricked the federation instead of being accepted. The rejection is
also behaviour-preserving on every execution that previously returned
`Ok`: `total_selected_value` is a sum of confirmed chain outputs and so
is bounded by the money supply, meaning any amount above `MAX_MONEY`
would have exhausted the UTXO set and returned the very same error. No
module consensus version bump is required.

`Feerate::calculate_fee` has an independent overflow defect on the same
path -- its `weight_to_vbytes(weight) * sats_per_kvb` panics in dev/ci
profiles and silently wraps to a tiny fee in release profiles, and
`sats_per_kvb` is attacker-supplied via `PegOutFees`. It is deliberately
left alone here. Unlike the sum above it does not panic in release, so
the argument that no history can contain such a transaction does not
apply to it: release binaries accepted those transactions, and changing
the result now would make upgraded and un-upgraded peers disagree on an
ordered item. Fixing it is a consensus-visible change that needs a
module consensus version gate, and belongs in its own commit.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9

### modules/fedimint-wallet-server/src/lib.rs
```diff
@@ -2147,9 +2147,19 @@ impl StatelessWallet<'_> {
         change_tweak: &[u8; 33],
         rbf: Option<Rbf>,
     ) -> Result<UnsignedTransaction, WalletOutputError> {
+        // `peg_out_amount` arrives unvalidated from whoever asked for the peg-out,
+        // and `bitcoin::Amount` arithmetic panics on overflow. An amount that
+        // cannot exist on chain can never be funded by our UTXOs anyway, so reject
+        // it before doing any arithmetic with it.
+        if peg_out_amount > bitcoin::Amount::MAX_MONEY {
+            return Err(WalletOutputError::NotEnoughSpendableUTXO);
+        }
+
         // Add the rbf fees to the existing tx fees
         if let Some(rbf) = &rbf {
-            fee_rate.sats_per_kvb += rbf.fees.fee_rate.sats_per_kvb;
+            fee_rate.sats_per_kvb = fee_rate
+                .sats_per_kvb
+                .saturating_add(rbf.fees.fee_rate.sats_per_kvb);
         }
 
         // When building a transaction we need to take care of two things:
@@ -2190,16 +2200,28 @@ impl StatelessWallet<'_> {
         let mut selected_utxos: Vec<(UTXOKey, SpendableUTXO)> = vec![];
         let mut fees = fee_rate.calculate_fee(total_weight);
 
-        while total_selected_value < peg_out_amount + change_script.minimal_non_dust() + fees {
-            match included_utxos.pop() {
-                Some((utxo_key, utxo)) => {
-                    total_selected_value += utxo.amount;
-                    total_weight += max_input_weight;
-                    fees = fee_rate.calculate_fee(total_weight);
-                    selected_utxos.push((utxo_key, utxo));
-                }
-                _ => return Err(WalletOutputError::NotEnoughSpendableUTXO), // Not enough UTXOs
+        loop {
+            // Fees grow with every selected input and are not bounded by `MAX_MONEY`,
+            // so the target has to be recomputed with checked arithmetic on every
+            // iteration. A target we cannot even represent is by definition more than
+            // our UTXOs can cover.
+            let target = peg_out_amount
+                .checked_add(change_script.minimal_non_dust())
+                .and_then(|target| target.checked_add(fees))
+                .ok_or(WalletOutputError::NotEnoughSpendableUTXO)?;
+
+            if total_selected_value >= target {
+                break;
             }
+
+            let Some((utxo_key, utxo)) = included_utxos.pop() else {
+                return Err(WalletOutputError::NotEnoughSpendableUTXO); // Not enough UTXOs
+            };
+
+            total_selected_value += utxo.amount;
+            total_weight += max_input_weight;
+            fees = fee_rate.calculate_fee(total_weight);
+            selected_utxos.push((utxo_key, utxo));
         }
 
         // We always pay ourselves change back to ensure that we don't lose anything due
@@ -2557,6 +2579,60 @@ mod tests {
         );
     }
 
+    /// A peg-out amount reaches `create_tx` straight from an unauthenticated
+    /// caller, both via `PEG_OUT_FEES_ENDPOINT` and via a submitted peg-out
+    /// output. Summing it with the dust limit and the fees used to overflow
+    /// `bitcoin::Amount`'s panicking `Add`, killing the guardian process.
+    #[test]
+    fn create_tx_rejects_amounts_that_cannot_exist_on_chain() {
+        let secp = secp256k1::Secp256k1::new();
+
+        let descriptor = PegInDescriptor::Wsh(
+            Wsh::new_sortedmulti(
+                3,
+                (0..4)
+                    .map(|_| secp.generate_keypair(&mut OsRng))
+                    .map(|(_, key)| CompressedPublicKey { key })
+                    .collect(),
+            )
+            .unwrap(),
+        );
+
+        let (secret_key, _) = secp.generate_keypair(&mut OsRng);
+
+        let wallet = StatelessWallet {
+            descriptor: &descriptor,
+            secret_key: &secret_key,
+            secp: &secp,
+        };
+
+        let recipient = Address::from_str("32iVBEu4dxkUQk9dJbZUiBiQdmypcEyJRf").unwrap();
+        let utxos = vec![(
+            UTXOKey(OutPoint::null()),
+            SpendableUTXO {
+                tweak: [0; 33],
+                amount: bitcoin::Amount::from_sat(100_000),
+            },
+        )];
+
+        for amount in [
+            Amount::from_sat(u64::MAX),
+            Amount::MAX_MONEY + Amount::from_sat(1),
+        ] {
+            let tx = wallet.create_tx(
+                amount,
+                recipient.clone().assume_checked().script_pubkey(),
+                vec![],
+                utxos.clone(),
+                Feerate { sats_per_kvb: 1000 },
+                &[0; 33],
+                None,
+            );
+
+            assert_eq!(tx, Err(WalletOutputError::NotEnoughSpendableUTXO));
+        }
+    }
+
     #[test]
     fn create_tx_should_validate_amounts() {
         let secp = secp256k1::Secp256k1::new();
```
