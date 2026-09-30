# [?] Merge remote-tracking branch 'origin/main' into security/ghsa-2026-010-hotkey-swap-rootclaimed-watermark-inflation

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/6e711d52853af40e7d3d424dca8648863b5acfc9
Type: security-commit

## Details
Merge remote-tracking branch 'origin/main' into security/ghsa-2026-010-hotkey-swap-rootclaimed-watermark-inflation

# Conflicts:
#	pallets/subtensor/src/tests/claim_root.rs

## Patch
### pallets/subtensor/src/staking/claim_root.rs
```diff
@@ -388,6 +388,35 @@ impl<T: Config> Pallet<T> {
         }
     }
 
+    /// Returns true if `coldkey` still holds any root (netuid 0) stake on any of its
+    /// staking hotkeys. Used to decide whether the coldkey should remain indexed in the
+    /// auto-claim staking-coldkey index.
+    pub fn coldkey_has_root_stake(coldkey: &T::AccountId) -> bool {
+        StakingHotkeys::<T>::get(coldkey).iter().any(|hotkey| {
+            !Self::get_stake_for_hotkey_and_coldkey_on_subnet(hotkey, coldkey, NetUid::ROOT)
+                .is_zero()
+        })
+    }
+
+    /// Remove `coldkey` from the staking-coldkey index, compacting by moving the last
+    /// entry into the freed slot so the index stays dense in `[0, n)`. This is the inverse
+    /// of `maybe_add_coldkey_index` and keeps the
+    /// `StakingColdkeys[c] == i <=> StakingColdkeysByIndex[i] == c` bijection consistent.
+    pub fn maybe_remove_coldkey_index(coldkey: &T::AccountId) {
+        if let Some(idx) = StakingColdkeys::<T>::take(coldkey) {
+            let last = NumStakingColdkeys::<T>::get().saturating_sub(1);
+            if idx != last
+                && let Some(moved) = StakingColdkeysByIndex::<T>::take(last)
+            {
+                StakingColdkeysByIndex::<T>::insert(idx, moved.clone());
+                StakingColdkeys::<T>::insert(moved, idx);
+            } else {
+                StakingColdkeysByIndex::<T>::remove(idx);
+            }
+            NumStakingColdkeys::<T>::put(last);
+        }
+    }
+
     pub fn run_auto_claim_root_divs(last_block_hash: T::Hash) -> Weight {
         let mut weight: Weight = Weight::default();
 
```

### pallets/subtensor/src/staking/stake_utils.rs
```diff
@@ -792,6 +792,12 @@ impl<T: Config> Pallet<T> {
         if netuid == NetUid::ROOT {
             // Adjust root claimed value for this hotkey and coldkey.
             Self::remove_stake_adjust_root_claimed_for_hotkey_and_coldkey(hotkey, coldkey, alpha);
+
+            // If the coldkey no longer holds any root stake, remove it from the
+            // auto-claim staking-coldkey index so dead entries do not accumulate.
+            if !Self::coldkey_has_root_stake(coldkey) {
+                Self::maybe_remove_coldkey_index(coldkey);
+            }
         }
 
         // Step 3: Update StakingHotkeys if the hotkey's total alpha, across all subnets, is zero
```

### pallets/subtensor/src/swap/swap_coldkey.rs
```diff
@@ -122,6 +122,14 @@ impl<T: Config> Pallet<T> {
                 }
             }
         }
+
+        // All of the old coldkey's root stake for this subnet has been moved to the new
+        // coldkey, so the old coldkey no longer holds any root stake. Remove its stale
+        // entry from the auto-claim staking-coldkey index (it is added for new_coldkey
+        // above) so swaps do not orphan dead entries.
+        if netuid == NetUid::ROOT {
+            Self::maybe_remove_coldkey_index(old_coldkey);
+        }
     }
 
     /// Transfer staking hotkeys from the old coldkey to the new coldkey.
```

### pallets/subtensor/src/swap/swap_hotkey.rs
```diff
@@ -481,6 +481,17 @@ impl<T: Config> Pallet<T> {
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

### pallets/subtensor/src/tests/claim_root.rs
```diff
@@ -2215,3 +2215,93 @@ fn ghsa_2026_010_hotkey_swap_inflates_rootclaimed_watermark() {
         );
     });
 }
+
+// ============================================================
+// GHSA-2026-012 regression test — security audit (June 2026)
+// Fails on the vulnerable code; passes with the fix in this PR.
+// ============================================================
+
+#[test]
+fn ghsa_2026_012_staking_coldkey_index_never_decremented() {
+    // GHSA-2026-012 (regression): the staking-coldkey index must be pruned when a coldkey
+    // ceases to hold root stake. After a full root unstake and a coldkey swap, the old,
+    // now-zero-stake coldkey must be removed from StakingColdkeys / StakingColdkeysByIndex
+    // and NumStakingColdkeys must be decremented (swap-last-into-gap compaction).
+    new_test_ext(1).execute_with(|| {
+        let owner_coldkey = U256::from(1001);
+        let hotkey = U256::from(1002);
+        let coldkey = U256::from(1003);
+        let new_coldkey = U256::from(10030);
+        let netuid = add_dynamic_network(&hotkey, &owner_coldkey);
+        remove_owner_registration_stake(netuid);
+
+        SubtensorModule::set_tao_weight(u64::MAX); // Set TAO weight to 1.0
+
+        // Index starts empty.
+        assert_eq!(NumStakingColdkeys::<Test>::get(), 0);
+
+        // Give `coldkey` root stake and index it via the exact path this file's
+        // claim-root tests use (see test_claim_root_with_block_emissions line ~995).
+        let root_stake = 2_000_000u64;
+        mock_increase_stake_for_hotkey_and_coldkey_on_subnet(
+            &hotkey,
+            &coldkey,
+            NetUid::ROOT,
+            root_stake.into(),
+        );
+        SubtensorModule::maybe_add_coldkey_index(&coldkey);
+
+        // Index now contains the coldkey: NumStakingColdkeys 0 -> 1.
+        assert_eq!(NumStakingColdkeys::<Test>::get(), 1);
+        assert!(StakingColdkeys::<Test>::contains_key(coldkey));
+        assert!(StakingColdkeysByIndex::<Test>::contains_key(0));
+        assert_eq!(StakingColdkeysByIndex::<Test>::get(0), Some(coldkey));
+
+        // Fully remove the coldkey's root stake (now a dead, zero-stake entry).
+        let alpha = SubtensorModule::get_stake_for_hotkey_and_coldkey_on_subnet(
+            &hotkey,
+            &coldkey,
+            NetUid::ROOT,
+        );
+        SubtensorModule::decrease_stake_for_hotkey_and_coldkey_on_subnet(
+            &hotkey,
+            &coldkey,
+            NetUid::ROOT,
+            alpha,
+        );
+        assert_eq!(
+            u64::from(SubtensorModule::get_stake_for_hotkey_and_coldkey_on_subnet(
+                &hotkey,
+                &coldkey,
+                NetUid::ROOT,
+            )),
+            0u64,
+            "precondition: coldkey now has zero root stake"
+        );
+
+        // Swap the coldkey via the real extrinsic helper.
+        assert_ok!(SubtensorModule::do_swap_coldkey(&coldkey, &new_coldkey));
+
+        // FIXED (GHSA-2026-012): the swap prunes the now-zero-stake old coldkey from the
+        // index and decrements the counter. The index is empty again.
+        assert_eq!(
+            NumStakingColdkeys::<Test>::get(),
+            0,
+            "NumStakingColdkeys must be decremented on full unstake + coldkey swap"
+        );
+        assert!(
+            !StakingColdkeysByIndex::<Test>::contains_key(0),
+            "dead index slot must be removed"
+        );
+        assert!(
+            !StakingColdkeys::<Test>::contains_key(coldkey),
+            "stale coldkey->index mapping must be removed after swap"
+        );
+        // The swapped-away new coldkey had no root stake transferred (the old coldkey was
+        // fully unstaked first), so it must not occupy the index either.
+        assert!(
+            !StakingColdkeys::<Test>::contains_key(new_coldkey),
+            "new coldkey with no root stake must not be indexed"
+        );
+    });
+}
```

### pallets/subtensor/src/tests/swap_hotkey.rs
```diff
@@ -1686,3 +1686,84 @@ fn test_swap_auto_stake_destination_coldkeys() {
         );
     });
 }
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
+        assert_ok!(SubtensorModule::create_account_if_non_existent(
+            &coldkey,
+            &old_hotkey
+        ));
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
