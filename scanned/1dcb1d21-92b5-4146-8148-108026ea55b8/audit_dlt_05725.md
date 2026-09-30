# [?] docs: correct NU6.2 security advisory ID to GHSA-jfw5-j458-pfv6

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-06-03
Source: https://github.com/ZcashFoundation/zebra/commit/48381e79143557cb7859aabdf4dfd5c849609cdd
Type: security-commit

## Details
docs: correct NU6.2 security advisory ID to GHSA-jfw5-j458-pfv6

Replace the placeholder/dead advisory ID `GHSA-2x4w-pxqw-58v9` with the
correct published identifier `GHSA-jfw5-j458-pfv6` across the changelog
and source comments/docs (9 occurrences in 7 files). No behavior change.

## Patch
### CHANGELOG.md
```diff
@@ -33,7 +33,7 @@ height, you can sync from that.
 ### Security
 
 - Add a consensus rule that rejects Orchard bundles whose proof has a non-canonical size,
-  effective from the NU6.2 network upgrade (GHSA-2x4w-pxqw-58v9).
+  effective from the NU6.2 network upgrade (GHSA-jfw5-j458-pfv6).
 
 ## [Zebra 4.5.3](https://github.com/ZcashFoundation/zebra/releases/tag/v4.5.3) - 2026-06-01
 
```

### zebra-chain/src/orchard/shielded_data.rs
```diff
@@ -85,7 +85,7 @@ impl ShieldedData {
     /// present but not canonically sized can be padded with arbitrary trailing data
     /// without affecting its validity. Bundles are parsed leniently (so that historical
     /// transactions remain deserializable), so this is enforced separately as a
-    /// height-gated consensus rule. See `GHSA-2x4w-pxqw-58v9`.
+    /// height-gated consensus rule. See `GHSA-jfw5-j458-pfv6`.
     pub fn proof_size_is_canonical(&self) -> bool {
         self.proof.0.len() == expected_proof_size(self.actions.len())
     }
```

### zebra-chain/src/transaction/arbitrary.rs
```diff
@@ -714,7 +714,7 @@ impl Arbitrary for orchard::ShieldedData {
             .prop_flat_map(|(flags, value_balance, shared_anchor, actions, binding_sig)| {
                 // Since NU6.2, an Orchard proof must have the canonical length for its number of
                 // actions (`2272 * num_actions + 2720` bytes), otherwise it is rejected as
-                // non-canonical (GHSA-2x4w-pxqw-58v9). The V5 txid is computed by round-tripping
+                // non-canonical (GHSA-jfw5-j458-pfv6). The V5 txid is computed by round-tripping
                 // through `librustzcash`, which enforces this length, so a proof of any other
                 // size makes the round-trip (and thus `Transaction::hash`) fail. Generate a proof
                 // of exactly the expected length, which depends on the number of actions.
```

### zebra-chain/src/transaction/tests/vectors.rs
```diff
@@ -844,7 +844,7 @@ fn zip244_sighash() -> Result<()> {
 }
 
 /// Real Orchard proofs from mined transactions must have the canonical size, and padding
-/// a proof with trailing bytes must make it non-canonical (GHSA-2x4w-pxqw-58v9). This
+/// a proof with trailing bytes must make it non-canonical (GHSA-jfw5-j458-pfv6). This
 /// also cross-checks `expected_proof_size` against real proofs produced by the chain.
 #[test]
 fn orchard_proof_size_is_canonical() {
```

### zebra-consensus/src/primitives/halo2.rs
```diff
@@ -52,7 +52,7 @@ pub type ItemVerifyingKey = VerifyingKey;
 
 // NU6.2 re-enables Orchard actions and ships the *fixed* variable-base
 // scalar-multiplication Orchard circuit (the circuit bug that caused Orchard to be temporarily
-// disabled; see GHSA-2x4w-pxqw-58v9). The fix changes the Orchard Action circuit, and therefore
+// disabled; see GHSA-jfw5-j458-pfv6). The fix changes the Orchard Action circuit, and therefore
 // its verifying key: a proof produced under one circuit version does not verify under the other
 // key. So we keep BOTH keys, each in its own dedicated verifier, and route each bundle to the
 // correct verifier by the block's network upgrade (see [`verifier_for`]):
@@ -240,7 +240,7 @@ pub static VERIFIER_POST_NU6_2: Lazy<VerifierService> =
 /// Returns the global Halo2 verifier for Orchard bundles in blocks at `network_upgrade`.
 ///
 /// The Orchard Action circuit — and therefore its verifying key — changed at NU6.2 (the fixed
-/// variable-base scalar-multiplication circuit; see GHSA-2x4w-pxqw-58v9), and a proof produced
+/// variable-base scalar-multiplication circuit; see GHSA-jfw5-j458-pfv6), and a proof produced
 /// under one circuit does not verify under the other key. So each bundle must be checked against
 /// the key for the upgrade of the block it appears in:
 ///
```

### zebra-consensus/src/primitives/halo2/tests.rs
```diff
@@ -2,7 +2,7 @@
 //!
 //! The key correctness property of this module is the **era split**: the Orchard Action circuit
 //! (and therefore its verifying key) changed at NU6.2 to fix a variable-base scalar-multiplication
-//! soundness bug (GHSA-2x4w-pxqw-58v9). A proof produced under one circuit does not verify under
+//! soundness bug (GHSA-jfw5-j458-pfv6). A proof produced under one circuit does not verify under
 //! the other key. These tests guard that:
 //!
 //!   * a real pre-NU6.2 Orchard proof verifies under the pre-NU6.2 (insecure) key, so historical
```

### zebra-consensus/src/transaction.rs
```diff
@@ -423,7 +423,7 @@ where
             // A proof that is present but not canonically sized can be padded with
             // arbitrary trailing data without affecting its validity, allowing excess
             // bandwidth and storage costs to be imposed while paying only fees sized to a
-            // canonical proof (GHSA-2x4w-pxqw-58v9).
+            // canonical proof (GHSA-jfw5-j458-pfv6).
             //
             // This is a constricting rule, so it is gated on that network upgrade:
             // Orchard actions mined before it, under earlier rules that did not enforce
@@ -1196,7 +1196,7 @@ where
     /// `network_upgrade` is the network upgrade active at the verified transaction's block
     /// height. It selects the Orchard verifier: the Orchard Action circuit (and its verifying
     /// key) changed at NU6.2 to fix the variable-base scalar-multiplication bug
-    /// (GHSA-2x4w-pxqw-58v9), so pre-NU6.2 bundles must be verified against the historical
+    /// (GHSA-jfw5-j458-pfv6), so pre-NU6.2 bundles must be verified against the historical
     /// (insecure) key and NU6.2+ bundles against the fixed key. A proof from one era does not
     /// verify under the other era's key. [`primitives::halo2::verifier_for`] maps the upgrade to
     /// the verifier holding the matching key; the two verifiers keep separate batches, so eras
```
