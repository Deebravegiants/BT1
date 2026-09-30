# [?] Prevent conviction overflow

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-04-23
Source: https://github.com/RaoFoundation/subtensor/commit/532e3e16e58ef6ff6cfde0284829d06b43b505b5
Type: security-commit

## Details
Prevent conviction overflow

## Patch
### pallets/subtensor/src/staking/lock.rs
```diff
@@ -1,4 +1,5 @@
 use super::*;
+use safe_math::FixedExt;
 use sp_std::collections::btree_map::BTreeMap;
 use sp_std::ops::Neg;
 use substrate_fixed::transcendental::exp;
@@ -58,12 +59,14 @@ impl<T: Config> Pallet<T> {
         let decay = Self::exp_decay(dt, tau);
         let dt_fixed = U64F64::saturating_from_num(dt);
         let mass_fixed = U64F64::saturating_from_num(locked_mass);
+        let tau_fixed = U64F64::saturating_from_num(tau);
         let new_locked_mass = decay
             .saturating_mul(mass_fixed)
             .saturating_to_num::<u64>()
             .into();
-        let new_conviction =
-            decay.saturating_mul(conviction.saturating_add(dt_fixed.saturating_mul(mass_fixed)));
+        let new_conviction = decay.saturating_mul(
+            conviction.saturating_add(dt_fixed.safe_div(tau_fixed).saturating_mul(mass_fixed)),
+        );
         (new_locked_mass, new_conviction)
     }
 
```

### runtime/src/lib.rs
```diff
@@ -272,7 +272,7 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
     //   `spec_version`, and `authoring_version` are the same between Wasm and native.
     // This value is set to 100 to notify Polkadot-JS App (https://polkadot.js.org/apps) to use
     //   the compatible custom types.
-    spec_version: 400,
+    spec_version: 401,
     impl_version: 1,
     apis: RUNTIME_API_VERSIONS,
     transaction_version: 1,
```
