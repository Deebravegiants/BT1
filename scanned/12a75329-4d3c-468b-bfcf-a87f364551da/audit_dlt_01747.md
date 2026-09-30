# [?] fix: don't overflow when token supply is close to u128::MAX (#14170)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-09-03
Source: https://github.com/near/nearcore/commit/d45f06876662c6676d947d22ab3a20c99a300962
Type: security-commit

## Details
fix: don't overflow when token supply is close to u128::MAX (#14170)

One of issues we've hit during testing [#releases/2.8 > 2.8 @
💬](https://near.zulipchat.com/#narrow/channel/522473-releases.2F2.2E8/topic/2.2E8/near/537292816).
There are spontaneous stake tx from mainnet validators which we don't
clean up properly; for now we ignore them by multiplying all stakes by
10**5. This, however, brings token supply closer to `u128::MAX`. This,
in turn, breaks all formulas of kind `stake * a / b` where `a / b <= 1`.

We could try `stake / b * a`, but I guess using `U256` is safer and
shouldn't really slow down the chain.

## Patch
### chain/epoch-manager/src/lib.rs
```diff
@@ -34,6 +34,7 @@ use near_store::adapter::StoreAdapter;
 use near_store::{DBCol, HEADER_HEAD_KEY, Store, StoreUpdate};
 use num_rational::BigRational;
 use parking_lot::{RwLock, RwLockReadGuard, RwLockWriteGuard};
+use primitive_types::U256;
 use reward_calculator::ValidatorOnlineThresholds;
 use shard_assignment::build_assignment_restrictions_v77_to_v78;
 use std::collections::{BTreeMap, HashMap, HashSet};
@@ -305,7 +306,9 @@ impl EpochManager {
         // Later when we perform the check to kick out validators, we don't kick out validators in
         // exempted_validators.
         let mut exempted_validators = HashSet::new();
-        let min_keep_stake = total_stake * (exempt_perc as u128) / 100;
+        let min_keep_stake = (U256::from(total_stake) * U256::from(exempt_perc as u128)
+            / U256::from(100u128))
+        .as_u128();
         let mut exempted_stake: Balance = 0;
         for account_id in accounts_sorted_by_online_ratio.into_iter().rev() {
             if exempted_stake >= min_keep_stake {
@@ -515,8 +518,9 @@ impl EpochManager {
         }
         PROTOCOL_VERSION_VOTES.reset();
         for (version, stake) in &versions {
-            let stake_percent = 100 * stake / total_block_producer_stake;
-            let stake_percent = stake_percent as i64;
+            let stake_percent = (U256::from(*stake) * U256::from(100u128)
+                / U256::from(total_block_producer_stake))
+            .as_u128() as i64;
             PROTOCOL_VERSION_VOTES.with_label_values(&[&version.to_string()]).set(stake_percent);
             tracing::info!(target: "epoch_manager", ?version, ?stake_percent, "Protocol version voting.");
         }
@@ -531,7 +535,9 @@ impl EpochManager {
         {
             let numer = *config.protocol_upgrade_stake_threshold.numer() as u128;
             let denom = *config.protocol_upgrade_stake_threshold.denom() as u128;
-            let threshold = total_block_producer_stake * numer / denom;
+            let threshold = (U256::from(total_block_producer_stake) * U256::from(numer)
+                / U256::from(denom))
+            .as_u128();
             if stake > threshold { version } else { protocol_version }
         } else {
             protocol_version
```
