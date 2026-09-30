# [?] Merge pull request #15 from opentensor/security/ghsa-2026-011-hotkey-swap-subnet-interval-bypass

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/6abd114ffe18f33f0c53954e838e905119a9dd78
Type: security-commit

## Details
Merge pull request #15 from opentensor/security/ghsa-2026-011-hotkey-swap-subnet-interval-bypass

Per-subnet hotkey-swap cooldown (`HotkeySwapOnSubnetInterval`) is bypassable via the all-subnets swap path

## Patch
### pallets/subtensor/src/swap/swap_hotkey.rs
```diff
@@ -129,6 +129,35 @@ impl<T: Config> Pallet<T> {
             );
         };
 
+        // Start to do everything for swap hotkey on all subnets case
+        // 12.1 Enforce the per-subnet hotkey-swap cooldown on the all-subnets path too.
+        // The all-subnets swap moves the identity on every subnet the old hotkey is a
+        // member of, so it must respect (and record) `LastHotkeySwapOnNetuid` for each of
+        // those subnets, exactly like the per-subnet path. Only gate subnets the old
+        // hotkey actually participates in so non-member subnets do not create cooldown rows.
+        let hotkey_swap_interval = T::HotkeySwapOnSubnetInterval::get();
+        let affected_netuids: Vec<NetUid> = Self::get_all_subnet_netuids()
+            .into_iter()
+            .filter(|netuid| IsNetworkMember::<T>::get(old_hotkey, *netuid))
+            .collect();
+        weight.saturating_accrue(
+            T::DbWeight::get().reads(affected_netuids.len().saturating_add(1) as u64),
+        );
+        for netuid in affected_netuids.iter() {
+            let last_hotkey_swap_block = LastHotkeySwapOnNetuid::<T>::get(*netuid, &coldkey);
+            // Only enforce the cooldown when a prior swap was recorded on this subnet.
+            // A first swap (no recorded timestamp) must not be gated by chain age — that
+            // would block the very first swap and never closes a bypass, since any swap
+            // records the timestamp and subsequent swaps within the interval are rejected.
+            if last_hotkey_swap_block != 0 {
+                ensure!(
+                    last_hotkey_swap_block.saturating_add(hotkey_swap_interval) < block,
+                    Error::<T>::HotKeySwapOnSubnetIntervalNotPassed
+                );
+            }
+            weight.saturating_accrue(T::DbWeight::get().reads(1));
+        }
+
         // Start to do everything for swap hotkey on all subnets case
         // 13. Get the cost for swapping the key
         let swap_cost = Self::get_key_swap_cost();
@@ -155,6 +184,14 @@ impl<T: Config> Pallet<T> {
             keep_stake,
         )?;
 
+        // 16.1 Record the per-subnet swap cooldown for every affected subnet, so a
+        // subsequent per-subnet (or all-subnets) swap on the same subnet within the
+        // interval is correctly rejected.
+        for netuid in affected_netuids.iter() {
+            LastHotkeySwapOnNetuid::<T>::insert(*netuid, &coldkey, block);
+            weight.saturating_accrue(T::DbWeight::get().writes(1));
+        }
+
         // 17. Update the last transaction block for the coldkey
         Self::set_last_tx_block(&coldkey, block);
         weight.saturating_accrue(T::DbWeight::get().writes(1));
```

### pallets/subtensor/src/tests/swap_hotkey.rs
```diff
@@ -1688,11 +1688,129 @@ fn test_swap_auto_stake_destination_coldkeys() {
 }
 
 // ============================================================
-// GHSA-2026-014 regression test — security audit (June 2026)
+// GHSA-2026-011 regression test — security audit (June 2026)
 // Fails on the vulnerable code; passes with the fix in this PR.
 // ============================================================
 use crate::staking::lock::LockState;
 
+#[test]
+fn ghsa_2026_011_subnet_swap_interval_bypassed_by_all_subnets_path() {
+    new_test_ext(1).execute_with(|| {
+        let netuid = NetUid::from(1); // not root (root == 0)
+        let tempo: u16 = 13;
+        let coldkey = U256::from(3);
+        let old_hotkey = U256::from(1);
+        let hk_a = U256::from(2); // result of the per-subnet swap
+        let hk_contrast = U256::from(6); // attempted per-subnet re-swap (must fail)
+        let hk_b = U256::from(7); // attempted all-subnets bypass swap (must now also fail)
+
+        // The per-subnet cooldown configured in the mock.
+        let interval: u64 = <Test as crate::Config>::HotkeySwapOnSubnetInterval::get();
+        assert_eq!(interval, 15);
+
+        // Setup: coldkey owns old_hotkey, registered on subnet N.
+        add_network(netuid, tempo, 0);
+        register_ok_neuron(netuid, old_hotkey, coldkey, 0);
+        // Fund the coldkey generously for both per-subnet and all-subnets swap costs.
+        add_balance_to_coldkey_account(&coldkey, 1_000_000_000_000_u64.into());
+
+        // Advance the block past the interval so the FIRST per-subnet swap is allowed
+        // (LastHotkeySwapOnNetuid defaults to 0; the check is 0 + interval < block).
+        // Do NOT step further afterwards: the on_finalize cleanup hook would otherwise
+        // purge stale LastHotkeySwapOnNetuid rows once the interval elapses.
+        step_block(20);
+        let block = SubtensorModule::get_current_block_as_u64();
+        assert!(block > interval);
+
+        // Precondition sanity: no swap record yet for (netuid, coldkey).
+        assert_eq!(LastHotkeySwapOnNetuid::<Test>::get(netuid, coldkey), 0);
+
+        // 1. Per-subnet swap old_hotkey -> hk_a on subnet N. This stamps
+        //    LastHotkeySwapOnNetuid(N, coldkey) = current block, opening the cooldown.
+        assert_ok!(SubtensorModule::do_swap_hotkey(
+            RuntimeOrigin::signed(coldkey),
+            &old_hotkey,
+            &hk_a,
+            Some(netuid),
+            false,
+        ));
+        assert_eq!(
+            LastHotkeySwapOnNetuid::<Test>::get(netuid, coldkey),
+            block,
+            "per-subnet swap must record the swap block for the cooldown"
+        );
+
+        // 2. CONTRAST (the rate limit works on the per-subnet path):
+        //    Immediately re-swapping on the SAME subnet within the interval fails.
+        assert_err!(
+            SubtensorModule::do_swap_hotkey(
+                RuntimeOrigin::signed(coldkey),
+                &hk_a,
+                &hk_contrast,
+                Some(netuid),
+                false,
+            ),
+            Error::<Test>::HotKeySwapOnSubnetIntervalNotPassed
+        );
+        // State unchanged by the rejected per-subnet swap.
+        assert!(SubtensorModule::is_hotkey_registered_on_specific_network(
+            &hk_a, netuid
+        ));
+        assert!(!SubtensorModule::is_hotkey_registered_on_specific_network(
+            &hk_contrast,
+            netuid
+        ));
+
+        // 3. FIXED (GHSA-2026-011): the all-subnets path (netuid=None) now also consults
+        //    the per-subnet interval for every subnet the old hotkey is a member of, so an
+        //    immediate swap via netuid=None within the cooldown is rejected with the same
+        //    error and CANNOT bypass the per-subnet cooldown.
+        assert_err!(
+            SubtensorModule::do_swap_hotkey(
+                RuntimeOrigin::signed(coldkey),
+                &hk_a,
+                &hk_b,
+                None,
+                false,
+            ),
+            Error::<Test>::HotKeySwapOnSubnetIntervalNotPassed
+        );
+
+        // The bypass swap did NOT take effect: ownership stays with hk_a (from step 1),
+        // and hk_b never became an owner.
+        assert_eq!(Owner::<Test>::get(hk_a), coldkey);
+        assert!(!Owner::<Test>::contains_key(hk_b));
+        // The per-subnet cooldown record is unchanged (still the step-1 block).
+        assert_eq!(LastHotkeySwapOnNetuid::<Test>::get(netuid, coldkey), block);
+
+        // 4. After the cooldown elapses, the all-subnets swap is allowed again and now
+        //    correctly re-stamps the per-subnet cooldown for the affected subnet.
+        step_block((interval + 1) as u16);
+        let block_after = SubtensorModule::get_current_block_as_u64();
+        assert!(block_after > block.saturating_add(interval));
+        assert_ok!(SubtensorModule::do_swap_hotkey(
+            RuntimeOrigin::signed(coldkey),
+            &hk_a,
+            &hk_b,
+            None,
+            false,
+        ));
+        assert_eq!(Owner::<Test>::get(hk_b), coldkey);
+        assert!(!Owner::<Test>::contains_key(hk_a));
+        // The all-subnets path now records the per-subnet cooldown.
+        assert_eq!(
+            LastHotkeySwapOnNetuid::<Test>::get(netuid, coldkey),
+            block_after,
+            "all-subnets swap must record the per-subnet cooldown block"
+        );
+    });
+}
+
+// ============================================================
+// GHSA-2026-014 regression test — security audit (June 2026)
+// Fails on the vulnerable code; passes with the fix in this PR.
+// ============================================================
+
 #[test]
 fn ghsa_2026_014_childkey_take_not_migrated_on_hotkey_swap() {
     new_test_ext(1).execute_with(|| {
```
