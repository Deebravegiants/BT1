# [?] Merge pull request #22 from opentensor/fix/ghsa-010-011-review-followups

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-17
Source: https://github.com/RaoFoundation/subtensor/commit/fa83646297f45a1a8108f70ba2ebf32d4f35b5c2
Type: security-commit

## Details
Merge pull request #22 from opentensor/fix/ghsa-010-011-review-followups

## Patch
### pallets/subtensor/src/staking/claim_root.rs
```diff
@@ -460,10 +460,20 @@ impl<T: Config> Pallet<T> {
         RootClaimed::<T>::remove((netuid, old_hotkey, old_coldkey));
 
         RootClaimed::<T>::mutate((netuid, new_hotkey, new_coldkey), |new_root_claimed| {
-            // Take the maximum rather than summing so that a stale residual watermark
-            // already present on the destination cannot inflate the merged value past
-            // the correct claimable high-water mark (GHSA-2026-010).
-            *new_root_claimed = old_root_claimed.max(*new_root_claimed);
+            // Sum the two already-claimed watermarks. When BOTH the source and the
+            // destination hold a legitimate RootClaimed — e.g. a coldkey swap onto a
+            // hotkey the new coldkey has already staked to, or a hotkey swap that merges
+            // two real positions — the merged "already claimed" total is old + new. Taking
+            // the max would drop one side, under-count what has already been claimed, and
+            // cause a future over-payment / double-claim of root dividends.
+            //
+            // GHSA-2026-010 (a *stale residual* watermark on new_hotkey inflating this sum
+            // in the hotkey-swap path) is prevented upstream by the root-swap cleanliness
+            // gate in `do_swap_hotkey`, which now also requires RootClaimed to be empty on
+            // new_hotkey (see `test_do_swap_hotkey_err_new_hotkey_not_clean_for_root`). With
+            // that gate the destination is always clean (new == 0) in the swap path, so the
+            // sum cannot be inflated there.
+            *new_root_claimed = old_root_claimed.saturating_add(*new_root_claimed);
         });
     }
     pub fn transfer_root_claimable_for_new_hotkey(
```

### pallets/subtensor/src/swap/swap_hotkey.rs
```diff
@@ -131,18 +131,38 @@ impl<T: Config> Pallet<T> {
 
         // Start to do everything for swap hotkey on all subnets case
         // 12.1 Enforce the per-subnet hotkey-swap cooldown on the all-subnets path too.
-        // The all-subnets swap moves the identity on every subnet the old hotkey is a
-        // member of, so it must respect (and record) `LastHotkeySwapOnNetuid` for each of
-        // those subnets, exactly like the per-subnet path. Only gate subnets the old
-        // hotkey actually participates in so non-member subnets do not create cooldown rows.
+        // The all-subnets swap moves the identity on every subnet the old hotkey actively
+        // participates in, so it must respect (and record) `LastHotkeySwapOnNetuid` for each
+        // of those subnets, exactly like the per-subnet path.
+        //
+        // "Participates in" is membership OR being a parent (has childkeys). Note a parent
+        // need not be a registered member — `do_set_children` has no membership requirement —
+        // so the childkey case genuinely adds coverage beyond `IsNetworkMember`, and
+        // `parent_child_swap_hotkey` re-homes those childkeys even on non-member subnets.
+        //
+        // We deliberately do NOT gate on the *child* side (`ParentKeys`): being someone's
+        // child is set by the parent via `do_set_children` WITHOUT the child's consent, so a
+        // third party could otherwise add a victim's hotkey as a child on an arbitrary subnet
+        // and impose swap-cooldowns on it — a griefing vector. The swap still migrates the
+        // child relationship for correctness; it simply isn't cooldown-gated.
         let hotkey_swap_interval = T::HotkeySwapOnSubnetInterval::get();
-        let affected_netuids: Vec<NetUid> = Self::get_all_subnet_netuids()
-            .into_iter()
-            .filter(|netuid| IsNetworkMember::<T>::get(old_hotkey, *netuid))
-            .collect();
+        let all_netuids = Self::get_all_subnet_netuids();
+        // Up to 2 reads per subnet during filtering (membership + childkeys), plus the
+        // subnet-list read itself.
         weight.saturating_accrue(
-            T::DbWeight::get().reads(affected_netuids.len().saturating_add(1) as u64),
+            T::DbWeight::get().reads(
+                (all_netuids.len() as u64)
+                    .saturating_mul(2)
+                    .saturating_add(1),
+            ),
         );
+        let affected_netuids: Vec<NetUid> = all_netuids
+            .into_iter()
+            .filter(|netuid| {
+                IsNetworkMember::<T>::get(old_hotkey, *netuid)
+                    || !ChildKeys::<T>::get(old_hotkey, *netuid).is_empty()
+            })
+            .collect();
         for netuid in affected_netuids.iter() {
             let last_hotkey_swap_block = LastHotkeySwapOnNetuid::<T>::get(*netuid, &coldkey);
             // Only enforce the cooldown when a prior swap was recorded on this subnet.
```

### pallets/subtensor/src/tests/claim_root.rs
```diff
@@ -2158,12 +2158,20 @@ fn test_claim_root_with_moved_stake() {
 // ============================================================
 
 #[test]
-fn ghsa_2026_010_hotkey_swap_inflates_rootclaimed_watermark() {
-    // GHSA-2026-010 (regression): The root swap path must NOT inflate the RootClaimed
-    // watermark on new_hotkey. `transfer_root_claimed_for_new_keys` now merges by max()
-    // instead of saturating_add, so a residual RootClaimed already sitting on
-    // (subnet, new_hotkey, coldkey) cannot stack under the old_hotkey's RootClaimed and
-    // raise the "already claimed" high-water mark.
+fn ghsa_2026_010_transfer_root_claimed_merges_legit_positions_by_sum() {
+    // GHSA-2026-010 (review follow-up): `transfer_root_claimed_for_new_keys` must SUM the
+    // two already-claimed watermarks, not take the max. When both the source and the
+    // destination hold a *legitimate* RootClaimed (e.g. a coldkey swap onto a hotkey the
+    // new coldkey already staked to), the merged "already claimed" total is A + B. Taking
+    // the max would drop one side, under-count what was already claimed, and cause a future
+    // over-payment / double-claim.
+    //
+    // The real GHSA-2026-010 protection — a *stale residual* watermark on new_hotkey
+    // inflating the merge in the hotkey-swap path — is the root-swap cleanliness gate,
+    // which now also requires RootClaimed to be empty on new_hotkey. That gate is covered
+    // by `tests::swap_hotkey::test_do_swap_hotkey_err_new_hotkey_not_clean_for_root`; with
+    // it, the destination is always clean (B == 0) in the swap path so the sum cannot be
+    // inflated there.
     new_test_ext(1).execute_with(|| {
         let netuid = NetUid::ROOT;
         let old_hotkey = U256::from(1002);
@@ -2172,21 +2180,15 @@ fn ghsa_2026_010_hotkey_swap_inflates_rootclaimed_watermark() {
 
         // A = old_hotkey's accumulated RootClaimed watermark for this coldkey.
         let a: u128 = 1_000_000u128;
-        // B = a residual RootClaimed watermark already sitting on (netuid, new_hotkey, coldkey).
-        // Chosen smaller than A so the safe (max) result is unambiguously A and the buggy
-        // (sum) result A+B would be strictly larger.
+        // B = a legitimate RootClaimed watermark already sitting on (netuid, new_hotkey,
+        // coldkey) — e.g. a real prior position being merged into.
         let b: u128 = 500_000u128;
 
         // Inject the two watermarks. Storage key order is (subnet, hot, cold) per
         // RootClaimed StorageNMap in lib.rs.
         RootClaimed::<Test>::insert((netuid, &old_hotkey, &coldkey), a);
         RootClaimed::<Test>::insert((netuid, &new_hotkey, &coldkey), b);
 
-        // Sanity: the residual watermark B is present on new_hotkey before the transfer.
-        assert_eq!(RootClaimed::<Test>::get((netuid, &new_hotkey, &coldkey)), b);
-
-        // Perform exactly the per-coldkey transfer the ROOT swap path executes in
-        // do_swap_hotkey for each claimed coldkey.
         SubtensorModule::transfer_root_claimed_for_new_keys(
             netuid,
             &old_hotkey,
@@ -2201,17 +2203,13 @@ fn ghsa_2026_010_hotkey_swap_inflates_rootclaimed_watermark() {
             0u128
         );
 
-        // FIXED: the new watermark equals A (the larger of A and B), NOT the inflated A + B.
+        // FIXED: the merged watermark is the SUM of the two legitimate positions; neither
+        // side is silently dropped (which max() would do, leading to an over-claim).
         let observed = RootClaimed::<Test>::get((netuid, &new_hotkey, &coldkey));
         assert_eq!(
-            observed, a,
-            "watermark must not be inflated: merged value must equal A, not A+B"
-        );
-        // Explicitly assert the bug is gone: the watermark is not the stacked sum.
-        assert_ne!(
             observed,
             a.saturating_add(b),
-            "vulnerability would stack residual B under A; it must not"
+            "merged watermark must be A + B (sum of both positions), not max(A, B)"
         );
     });
 }
```

### pallets/subtensor/src/tests/swap_hotkey.rs
```diff
@@ -1806,6 +1806,96 @@ fn ghsa_2026_011_subnet_swap_interval_bypassed_by_all_subnets_path() {
     });
 }
 
+// ============================================================
+// GHSA-2026-011 follow-up (review): the all-subnets cooldown must cover subnets where the
+// old hotkey is a PARENT (has childkeys) — those are migrated even on subnets it is not a
+// member of — but must NOT gate on the CHILD side (ParentKeys), since a third party can set
+// any hotkey as its child without consent (that would be a griefing vector).
+// Fails on the member-only filter; passes with the membership-or-parent filter in this PR.
+// ============================================================
+#[test]
+fn ghsa_2026_011_all_subnets_swap_covers_parent_key_subnets_not_child_side() {
+    new_test_ext(1).execute_with(|| {
+        let coldkey = U256::from(3);
+        let old_hotkey = U256::from(1);
+        let new_hotkey = U256::from(2);
+        let child = U256::from(8);
+        let foreign_parent = U256::from(9);
+
+        // member_netuid: old_hotkey is a registered member here.
+        let member_netuid = NetUid::from(1);
+        // parent_netuid: old_hotkey is ONLY a parent here (has a childkey), NOT a member.
+        let parent_netuid = NetUid::from(2);
+        // child_netuid: old_hotkey is ONLY a child here (some other hotkey's child), NOT a
+        // member and not a parent. This must NOT be cooldown-gated (anti-griefing).
+        let child_netuid = NetUid::from(3);
+
+        let interval: u64 = <Test as crate::Config>::HotkeySwapOnSubnetInterval::get();
+
+        add_network(member_netuid, 13, 0);
+        add_network(parent_netuid, 13, 0);
+        add_network(child_netuid, 13, 0);
+        register_ok_neuron(member_netuid, old_hotkey, coldkey, 0);
+        add_balance_to_coldkey_account(&coldkey, 1_000_000_000_000_u64.into());
+
+        // old_hotkey is a PARENT on parent_netuid (has a child) but NOT a network member there.
+        ChildKeys::<Test>::insert(old_hotkey, parent_netuid, vec![(u64::MAX, child)]);
+        assert!(!IsNetworkMember::<Test>::get(old_hotkey, parent_netuid));
+        // old_hotkey is only a CHILD on child_netuid (set by foreign_parent, no consent).
+        ParentKeys::<Test>::insert(old_hotkey, child_netuid, vec![(u64::MAX, foreign_parent)]);
+        assert!(!IsNetworkMember::<Test>::get(old_hotkey, child_netuid));
+        assert!(ChildKeys::<Test>::get(old_hotkey, child_netuid).is_empty());
+
+        // Advance past the interval so the swap itself is allowed (first swap on each subnet).
+        step_block(20);
+        let block = SubtensorModule::get_current_block_as_u64();
+        assert!(block > interval);
+
+        // Preconditions: no cooldown recorded on the parent-only or child-only subnets.
+        assert_eq!(LastHotkeySwapOnNetuid::<Test>::get(parent_netuid, coldkey), 0);
+        assert_eq!(LastHotkeySwapOnNetuid::<Test>::get(child_netuid, coldkey), 0);
+
+        // All-subnets swap (netuid = None).
+        assert_ok!(SubtensorModule::do_swap_hotkey(
+            RuntimeOrigin::signed(coldkey),
+            &old_hotkey,
+            &new_hotkey,
+            None,
+            false,
+        ));
+
+        // The relationships are re-homed onto new_hotkey regardless of membership.
+        assert_eq!(
+            ChildKeys::<Test>::get(new_hotkey, parent_netuid),
+            vec![(u64::MAX, child)],
+            "parent relationship must migrate to new_hotkey on the parent-only subnet"
+        );
+        assert_eq!(
+            ParentKeys::<Test>::get(new_hotkey, child_netuid),
+            vec![(u64::MAX, foreign_parent)],
+            "child relationship must still migrate to new_hotkey on the child-only subnet"
+        );
+
+        // FIXED: the per-subnet cooldown is recorded on the member subnet AND the parent-only
+        // subnet (the member-only filter would have left the latter at 0).
+        assert_eq!(LastHotkeySwapOnNetuid::<Test>::get(member_netuid, coldkey), block);
+        assert_eq!(
+            LastHotkeySwapOnNetuid::<Test>::get(parent_netuid, coldkey),
+            block,
+            "all-subnets swap must record the cooldown on parent-key subnets, not just member subnets"
+        );
+
+        // Anti-griefing: the child-only subnet is NOT cooldown-gated. A third party (the
+        // foreign parent) set old_hotkey as its child without consent; gating on that would
+        // let it impose swap-cooldowns on the victim.
+        assert_eq!(
+            LastHotkeySwapOnNetuid::<Test>::get(child_netuid, coldkey),
+            0,
+            "child-only subnet must NOT be cooldown-gated (no-consent child assignment is a griefing vector)"
+        );
+    });
+}
+
 // ============================================================
 // GHSA-2026-014 regression test — security audit (June 2026)
 // Fails on the vulnerable code; passes with the fix in this PR.
```

### runtime/src/lib.rs
```diff
@@ -277,7 +277,7 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
     //   `spec_version`, and `authoring_version` are the same between Wasm and native.
     // This value is set to 100 to notify Polkadot-JS App (https://polkadot.js.org/apps) to use
     //   the compatible custom types.
-    spec_version: 418,
+    spec_version: 419,
     impl_version: 1,
     apis: RUNTIME_API_VERSIONS,
     transaction_version: 1,
```
