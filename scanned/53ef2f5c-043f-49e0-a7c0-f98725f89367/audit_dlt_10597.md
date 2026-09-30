# [?] security: fix childkey take not migrated on hotkey swap (GHSA-2026-014) + regression test

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-11
Source: https://github.com/RaoFoundation/subtensor/commit/16a39c1275fef048337c8cfda28d2a35e418ba99
Type: security-commit

## Details
security: fix childkey take not migrated on hotkey swap (GHSA-2026-014) + regression test

## Patch
### pallets/subtensor/src/swap/swap_hotkey.rs
```diff
@@ -478,6 +478,17 @@ impl<T: Config> Pallet<T> {
             weight.saturating_accrue(T::DbWeight::get().reads_writes(1, 2));
         }
 
+        // 3.8. Swap ChildkeyTake.
+        // ChildkeyTake( hotkey, netuid ) --> u16 -- the per-subnet childkey take for the hotkey.
+        // Only migrate when an explicit value exists, to preserve the storage default
+        // semantics (don't materialize a floor value for hotkeys that never set a take).
+        // `take` reads + removes the old row in one operation, avoiding orphaned storage.
+        if ChildkeyTake::<T>::contains_key(old_hotkey, netuid) {
+            let childkey_take = ChildkeyTake::<T>::take(old_hotkey, netuid);
+            ChildkeyTake::<T>::insert(new_hotkey, netuid, childkey_take);
+            weight.saturating_accrue(T::DbWeight::get().reads_writes(1, 2));
+        }
+
         // 4. Swap ChildKeys.
         // 5. Swap ParentKeys.
         // 6. Swap PendingChildKeys.
```

### pallets/subtensor/src/tests/swap_hotkey.rs
```diff
@@ -1686,3 +1686,83 @@ fn test_swap_auto_stake_destination_coldkeys() {
         );
     });
 }
+
+
+// ============================================================
+// GHSA-2026-014 regression test — security audit (June 2026)
+// Fails on the vulnerable code; passes with the fix in this PR.
+// ============================================================
+use crate::staking::lock::LockState;
+
+#[test]
+fn ghsa_2026_014_childkey_take_not_migrated_on_hotkey_swap() {
+    new_test_ext(1).execute_with(|| {
+        let netuid = NetUid::from(1);
+        let coldkey = U256::from(2);
+        let old_hotkey = U256::from(1);
+        let new_hotkey = U256::from(5);
+        let mut weight = Weight::zero();
+
+        add_network(netuid, 1, 0);
+        // Establish coldkey ownership of old_hotkey (Owner(old_hotkey) = coldkey).
+        SubtensorModule::create_account_if_non_existent(&coldkey, &old_hotkey)
+            .expect("account creation should succeed");
+
+        // The effective minimum (floor) childkey take in this mock is 0.
+        let floor_take = SubtensorModule::get_effective_min_childkey_take(netuid);
+        assert_eq!(floor_take, 0);
+
+        // Configure a NON-minimum childkey take on the old hotkey for this subnet.
+        // 5000 is well above the floor (0) and below the max (11_796).
+        let configured_childkey_take: u16 = 5000;
+        assert!(configured_childkey_take > floor_take);
+        ChildkeyTake::<Test>::insert(old_hotkey, netuid, configured_childkey_take);
+
+        // Configure a NON-default delegate take on the old hotkey for contrast.
+        // (Default delegate take in this mock is 11_796.)
+        let configured_delegate_take: u16 = 100;
+        Delegates::<Test>::insert(old_hotkey, configured_delegate_take);
+
+        // Sanity: pre-swap the old hotkey carries the configured values.
+        assert_eq!(
+            ChildkeyTake::<Test>::get(old_hotkey, netuid),
+            configured_childkey_take
+        );
+        assert_eq!(
+            SubtensorModule::get_childkey_take(&old_hotkey, netuid),
+            configured_childkey_take
+        );
+        assert_eq!(Delegates::<Test>::get(old_hotkey), configured_delegate_take);
+
+        // Perform the real hotkey swap on all subnets.
+        assert_ok!(SubtensorModule::perform_hotkey_swap_on_all_subnets(
+            &old_hotkey,
+            &new_hotkey,
+            &coldkey,
+            &mut weight,
+            false
+        ));
+
+        // CONTRAST (safe behavior): Delegates take IS migrated to the new hotkey.
+        assert!(!Delegates::<Test>::contains_key(old_hotkey));
+        assert_eq!(Delegates::<Test>::get(new_hotkey), configured_delegate_take);
+
+        // FIXED (GHSA-2026-014): ChildkeyTake IS now migrated to the new hotkey.
+        // The new hotkey carries over the configured take (5000) instead of
+        // silently dropping to the storage default (0) / floor take.
+        assert_eq!(
+            ChildkeyTake::<Test>::get(new_hotkey, netuid),
+            configured_childkey_take,
+            "ChildkeyTake(new_hotkey) should inherit the configured take after swap"
+        );
+        // The effective getter for the new hotkey returns the configured take, not the floor.
+        assert_eq!(
+            SubtensorModule::get_childkey_take(&new_hotkey, netuid),
+            configured_childkey_take
+        );
+
+        // FIXED: the old hotkey's ChildkeyTake row is removed (no orphan left behind).
+        assert!(!ChildkeyTake::<Test>::contains_key(old_hotkey, netuid));
+        assert_eq!(ChildkeyTake::<Test>::get(old_hotkey, netuid), 0);
+    });
+}
```
