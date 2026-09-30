# [?] Fix fuzz-found panic in Prng::u64_in_inclusive_range (#1172)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2023-11-03
Source: https://github.com/stellar/rs-soroban-env/commit/696d6f920b4b673e04cc01aeb09034ef2cdc15b8
Type: security-commit

## Details
Fix fuzz-found panic in Prng::u64_in_inclusive_range (#1172)

This allowed a contract to panic the host.

## Patch
### soroban-env-host/src/host/prng.rs
```diff
@@ -6,7 +6,7 @@ use crate::{
     budget::Budget,
     host::metered_clone::MeteredClone,
     host_object::HostVec,
-    xdr::{ContractCostType, ScBytes},
+    xdr::{ContractCostType, ScBytes, ScErrorCode, ScErrorType},
     HostError,
 };
 use rand::{distributions::Uniform, prelude::Distribution, seq::SliceRandom, RngCore};
@@ -98,6 +98,11 @@ impl Prng {
         range: RangeInclusive<u64>,
         budget: &Budget,
     ) -> Result<u64, HostError> {
+        // rand::Uniform panics if start > end.
+        if range.start() > range.end() {
+            return Err((ScErrorType::Value, ScErrorCode::InvalidInput).into());
+        }
+
         // We over-estimate the number of bytes drawn by a factor of 2, to
         // account for the fact that a range sample is rejection-sampling which
         // is expected to only do one draw but might do more than one.
```
