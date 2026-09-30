# [?] fix emission gate underflow stranding block emission

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-07-27
Source: https://github.com/RaoFoundation/subtensor/commit/7e20eb76c0a9d1068d7d6e536c73a6eedcc06e90
Type: security-commit

## Details
fix emission gate underflow stranding block emission

When a stale theta and steep h drive every gated share to zero in
fixed-point, restore the ungated distribution so get_subnet_block_emissions
cannot emit zero everywhere. Cover with the 256-equal / h=8 boundary case.

Co-authored-by: Cursor <cursoragent@cursor.com>

## Patch
### pallets/subtensor/src/coinbase/subnet_emissions.rs
```diff
@@ -444,7 +444,11 @@ impl<T: Config> Pallet<T> {
     /// of s^h itself, which underflows I32F32 precision for deep-tail shares.
     /// The gate passes exactly 1/2 at the bar, ~1 well above it, and ~0 well
     /// below it. A zero bar (never computed) disables the gate.
-    fn apply_emission_gate(shares: &mut BTreeMap<NetUid, U64F64>) {
+    ///
+    /// When every gated share underflows to zero (e.g. a stale `theta` far above
+    /// all shares with a steep `h`), the ungated shares are restored so the
+    /// block's emission cannot be stranded.
+    pub(crate) fn apply_emission_gate(shares: &mut BTreeMap<NetUid, U64F64>) {
         let zero = U64F64::saturating_from_num(0);
         let one = U64F64::saturating_from_num(1);
 
@@ -454,6 +458,8 @@ impl<T: Config> Pallet<T> {
         }
         let h = EmissionGateExponent::<T>::get();
 
+        let ungated = shares.clone();
+
         for share in shares.values_mut() {
             if *share <= zero {
                 continue;
@@ -474,6 +480,12 @@ impl<T: Config> Pallet<T> {
             for share in shares.values_mut() {
                 *share = share.safe_div(total);
             }
+        } else {
+            // Fixed-point underflow can zero every gated product (stale
+            // theta ≫ share with large h). Restore the pre-gate distribution
+            // rather than emit zero everywhere.
+            *shares = ungated;
+            log::warn!("Emission gate underflowed to zero total; restoring ungated shares");
         }
     }
 
```

### pallets/subtensor/src/tests/subnet_emissions.rs
```diff
@@ -266,6 +266,37 @@ fn emission_gate_concentrates_1_to_2_price_split() {
     });
 }
 
+/// Stale theta ≫ equal shares with max h can underflow every gated product to
+/// zero; the gate must restore the ungated distribution instead of stranding
+/// the block's emission.
+#[test]
+fn emission_gate_underflow_restores_ungated_shares() {
+    new_test_ext(1).execute_with(|| {
+        // theta = 1, 256 equal shares (1/256), h = 8 → ratio = 256; safe_pow
+        // saturates near 2^64, gate rounds to the smallest U64F64, and
+        // share * gate underflows every entry to zero.
+        EmissionGateBar::<Test>::put(u64f64(1.0));
+        EmissionGateExponent::<Test>::set(u64f64(8.0));
+
+        let equal = u64f64(1.0 / 256.0);
+        let mut shares: BTreeMap<NetUid, U64F64> = (1u16..=256)
+            .map(|i| (NetUid::from(i), equal))
+            .collect();
+
+        SubtensorModule::apply_emission_gate(&mut shares);
+
+        let sum: f64 = shares.values().map(|v| v.to_num::<f64>()).sum();
+        assert!(
+            sum > 0.0,
+            "gated underflow must not strand emission (sum was {sum})"
+        );
+        assert_abs_diff_eq!(sum, 1.0_f64, epsilon = 1e-9);
+        for v in shares.values() {
+            assert_abs_diff_eq!(v.to_num::<f64>(), 1.0 / 256.0, epsilon = 1e-9);
+        }
+    });
+}
+
 /// Bar is sticky mid-interval and recomputes on the cadence boundary when the
 /// demand distribution has changed.
 #[test]
```
