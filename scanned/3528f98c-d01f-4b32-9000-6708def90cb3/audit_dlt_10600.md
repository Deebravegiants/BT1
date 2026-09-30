# [?] security: fix hotkey swap rootclaimed watermark inflation (GHSA-2026-010) + regression test

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-11
Source: https://github.com/RaoFoundation/subtensor/commit/0b9d53d42d00dbc258c353cbffa8ac014c425aef
Type: security-commit

## Details
security: fix hotkey swap rootclaimed watermark inflation (GHSA-2026-010) + regression test

## Patch
### pallets/subtensor/src/staking/claim_root.rs
```diff
@@ -431,7 +431,10 @@ impl<T: Config> Pallet<T> {
         RootClaimed::<T>::remove((netuid, old_hotkey, old_coldkey));
 
         RootClaimed::<T>::mutate((netuid, new_hotkey, new_coldkey), |new_root_claimed| {
-            *new_root_claimed = old_root_claimed.saturating_add(*new_root_claimed);
+            // Take the maximum rather than summing so that a stale residual watermark
+            // already present on the destination cannot inflate the merged value past
+            // the correct claimable high-water mark (GHSA-2026-010).
+            *new_root_claimed = old_root_claimed.max(*new_root_claimed);
         });
     }
     pub fn transfer_root_claimable_for_new_hotkey(
```

### pallets/subtensor/src/swap/swap_hotkey.rs
```diff
@@ -99,7 +99,10 @@ impl<T: Config> Pallet<T> {
         if touches_root {
             ensure!(
                 RootClaimable::<T>::get(new_hotkey).is_empty()
-                    && Self::get_stake_for_hotkey_on_subnet(new_hotkey, NetUid::ROOT).is_zero(),
+                    && Self::get_stake_for_hotkey_on_subnet(new_hotkey, NetUid::ROOT).is_zero()
+                    && RootClaimed::<T>::iter_prefix((NetUid::ROOT, new_hotkey))
+                        .next()
+                        .is_none(),
                 Error::<T>::NewHotKeyNotCleanForRootSwap
             );
         }
```

### pallets/subtensor/src/tests/claim_root.rs
```diff
@@ -2151,3 +2151,71 @@ fn test_claim_root_with_moved_stake() {
         assert_abs_diff_eq!(bob_stake_diff2, estimated_stake as u64, epsilon = 100u64,);
     });
 }
+
+
+// ============================================================
+// GHSA-2026-010 regression test — security audit (June 2026)
+// Fails on the vulnerable code; passes with the fix in this PR.
+// ============================================================
+
+#[test]
+fn ghsa_2026_010_hotkey_swap_inflates_rootclaimed_watermark() {
+    // GHSA-2026-010 (regression): The root swap path must NOT inflate the RootClaimed
+    // watermark on new_hotkey. `transfer_root_claimed_for_new_keys` now merges by max()
+    // instead of saturating_add, so a residual RootClaimed already sitting on
+    // (subnet, new_hotkey, coldkey) cannot stack under the old_hotkey's RootClaimed and
+    // raise the "already claimed" high-water mark.
+    new_test_ext(1).execute_with(|| {
+        let netuid = NetUid::ROOT;
+        let old_hotkey = U256::from(1002);
+        let new_hotkey = U256::from(1003);
+        let coldkey = U256::from(1004);
+
+        // A = old_hotkey's accumulated RootClaimed watermark for this coldkey.
+        let a: u128 = 1_000_000u128;
+        // B = a residual RootClaimed watermark already sitting on (netuid, new_hotkey, coldkey).
+        // Chosen smaller than A so the safe (max) result is unambiguously A and the buggy
+        // (sum) result A+B would be strictly larger.
+        let b: u128 = 500_000u128;
+
+        // Inject the two watermarks. Storage key order is (subnet, hot, cold) per
+        // RootClaimed StorageNMap in lib.rs.
+        RootClaimed::<Test>::insert((netuid, &old_hotkey, &coldkey), a);
+        RootClaimed::<Test>::insert((netuid, &new_hotkey, &coldkey), b);
+
+        // Sanity: the residual watermark B is present on new_hotkey before the transfer.
+        assert_eq!(
+            RootClaimed::<Test>::get((netuid, &new_hotkey, &coldkey)),
+            b
+        );
+
+        // Perform exactly the per-coldkey transfer the ROOT swap path executes in
+        // do_swap_hotkey for each claimed coldkey.
+        SubtensorModule::transfer_root_claimed_for_new_keys(
+            netuid,
+            &old_hotkey,
+            &new_hotkey,
+            &coldkey,
+            &coldkey,
+        );
+
+        // Old hotkey watermark is cleared (as expected).
+        assert_eq!(
+            RootClaimed::<Test>::get((netuid, &old_hotkey, &coldkey)),
+            0u128
+        );
+
+        // FIXED: the new watermark equals A (the larger of A and B), NOT the inflated A + B.
+        let observed = RootClaimed::<Test>::get((netuid, &new_hotkey, &coldkey));
+        assert_eq!(
+            observed, a,
+            "watermark must not be inflated: merged value must equal A, not A+B"
+        );
+        // Explicitly assert the bug is gone: the watermark is not the stacked sum.
+        assert_ne!(
+            observed,
+            a.saturating_add(b),
+            "vulnerability would stack residual B under A; it must not"
+        );
+    });
+}
```
