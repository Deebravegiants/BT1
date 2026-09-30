# [?] GHSA-2026-011: drop child-side (ParentKeys) cooldown gating

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-16
Source: https://github.com/RaoFoundation/subtensor/commit/7543a925f54f0290bba89fe9ef6e4b9b3905a371
Type: security-commit

## Details
GHSA-2026-011: drop child-side (ParentKeys) cooldown gating

Per review: gate the all-subnets hotkey-swap cooldown on membership OR being a
parent (ChildKeys), but NOT on the child side (ParentKeys). A parent can add any
hotkey as its child without consent (do_set_children), so gating on ParentKeys
would let a third party impose swap-cooldowns on a victim's hotkey — a griefing
vector. The swap still migrates the child relationship; it is just not gated.
Test updated to assert a child-only subnet is not cooldown-stamped.

## Patch
### pallets/subtensor/src/swap/swap_hotkey.rs
```diff
@@ -131,26 +131,28 @@ impl<T: Config> Pallet<T> {
 
         // Start to do everything for swap hotkey on all subnets case
         // 12.1 Enforce the per-subnet hotkey-swap cooldown on the all-subnets path too.
-        // The all-subnets swap moves the identity on every subnet the old hotkey has a
-        // presence on, so it must respect (and record) `LastHotkeySwapOnNetuid` for each of
-        // those subnets, exactly like the per-subnet path.
+        // The all-subnets swap moves the identity on every subnet the old hotkey actively
+        // participates in, so it must respect (and record) `LastHotkeySwapOnNetuid` for each
+        // of those subnets, exactly like the per-subnet path.
         //
-        // "Presence" is NOT just subnet membership: `perform_hotkey_swap_on_one_subnet`
-        // migrates ParentKeys/ChildKeys (`parent_child_swap_hotkey`) UNCONDITIONALLY, so a
-        // hotkey that is a parent (has childkeys) or a child (has parents) on a subnet it is
-        // not a registered member of is still re-homed there. The cooldown must cover those
-        // subnets too, otherwise the all-subnets path could repeatedly re-home parent/child
-        // relationships on a non-member subnet without ever tripping the per-subnet rate
-        // limit. We still skip subnets where the old hotkey has no presence so those do not
-        // accumulate cooldown rows.
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
         let all_netuids = Self::get_all_subnet_netuids();
-        // Up to 3 reads per subnet during filtering (membership + childkeys + parentkeys),
-        // plus the subnet-list read itself.
+        // Up to 2 reads per subnet during filtering (membership + childkeys), plus the
+        // subnet-list read itself.
         weight.saturating_accrue(
             T::DbWeight::get().reads(
                 (all_netuids.len() as u64)
-                    .saturating_mul(3)
+                    .saturating_mul(2)
                     .saturating_add(1),
             ),
         );
@@ -159,7 +161,6 @@ impl<T: Config> Pallet<T> {
             .filter(|netuid| {
                 IsNetworkMember::<T>::get(old_hotkey, *netuid)
                     || !ChildKeys::<T>::get(old_hotkey, *netuid).is_empty()
-                    || !ParentKeys::<T>::get(old_hotkey, *netuid).is_empty()
             })
             .collect();
         for netuid in affected_netuids.iter() {
```

### pallets/subtensor/src/tests/swap_hotkey.rs
```diff
@@ -1807,46 +1807,53 @@ fn ghsa_2026_011_subnet_swap_interval_bypassed_by_all_subnets_path() {
 }
 
 // ============================================================
-// GHSA-2026-011 follow-up (review): the all-subnets cooldown must also cover subnets
-// where the old hotkey is only a PARENT/CHILD (parent/child keys are migrated even on
-// subnets the hotkey is not a member of), not just member subnets.
-// Fails on the member-only filter; passes with the parent/child-aware filter in this PR.
+// GHSA-2026-011 follow-up (review): the all-subnets cooldown must cover subnets where the
+// old hotkey is a PARENT (has childkeys) — those are migrated even on subnets it is not a
+// member of — but must NOT gate on the CHILD side (ParentKeys), since a third party can set
+// any hotkey as its child without consent (that would be a griefing vector).
+// Fails on the member-only filter; passes with the membership-or-parent filter in this PR.
 // ============================================================
 #[test]
-fn ghsa_2026_011_all_subnets_swap_covers_parent_key_only_subnets() {
+fn ghsa_2026_011_all_subnets_swap_covers_parent_key_subnets_not_child_side() {
     new_test_ext(1).execute_with(|| {
         let coldkey = U256::from(3);
         let old_hotkey = U256::from(1);
         let new_hotkey = U256::from(2);
         let child = U256::from(8);
+        let foreign_parent = U256::from(9);
 
         // member_netuid: old_hotkey is a registered member here.
         let member_netuid = NetUid::from(1);
         // parent_netuid: old_hotkey is ONLY a parent here (has a childkey), NOT a member.
         let parent_netuid = NetUid::from(2);
+        // child_netuid: old_hotkey is ONLY a child here (some other hotkey's child), NOT a
+        // member and not a parent. This must NOT be cooldown-gated (anti-griefing).
+        let child_netuid = NetUid::from(3);
 
         let interval: u64 = <Test as crate::Config>::HotkeySwapOnSubnetInterval::get();
 
         add_network(member_netuid, 13, 0);
         add_network(parent_netuid, 13, 0);
+        add_network(child_netuid, 13, 0);
         register_ok_neuron(member_netuid, old_hotkey, coldkey, 0);
         add_balance_to_coldkey_account(&coldkey, 1_000_000_000_000_u64.into());
 
-        // old_hotkey is a parent on parent_netuid (has a child) but NOT a network member there.
+        // old_hotkey is a PARENT on parent_netuid (has a child) but NOT a network member there.
         ChildKeys::<Test>::insert(old_hotkey, parent_netuid, vec![(u64::MAX, child)]);
         assert!(!IsNetworkMember::<Test>::get(old_hotkey, parent_netuid));
-        assert!(!ChildKeys::<Test>::get(old_hotkey, parent_netuid).is_empty());
+        // old_hotkey is only a CHILD on child_netuid (set by foreign_parent, no consent).
+        ParentKeys::<Test>::insert(old_hotkey, child_netuid, vec![(u64::MAX, foreign_parent)]);
+        assert!(!IsNetworkMember::<Test>::get(old_hotkey, child_netuid));
+        assert!(ChildKeys::<Test>::get(old_hotkey, child_netuid).is_empty());
 
         // Advance past the interval so the swap itself is allowed (first swap on each subnet).
         step_block(20);
         let block = SubtensorModule::get_current_block_as_u64();
         assert!(block > interval);
 
-        // Precondition: no cooldown recorded on the parent-only subnet.
-        assert_eq!(
-            LastHotkeySwapOnNetuid::<Test>::get(parent_netuid, coldkey),
-            0
-        );
+        // Preconditions: no cooldown recorded on the parent-only or child-only subnets.
+        assert_eq!(LastHotkeySwapOnNetuid::<Test>::get(parent_netuid, coldkey), 0);
+        assert_eq!(LastHotkeySwapOnNetuid::<Test>::get(child_netuid, coldkey), 0);
 
         // All-subnets swap (netuid = None).
         assert_ok!(SubtensorModule::do_swap_hotkey(
@@ -1857,27 +1864,34 @@ fn ghsa_2026_011_all_subnets_swap_covers_parent_key_only_subnets() {
             false,
         ));
 
-        // The parent relationship was re-homed onto new_hotkey on the parent-only subnet
-        // (this migration happens regardless of membership).
-        assert!(ChildKeys::<Test>::get(old_hotkey, parent_netuid).is_empty());
+        // The relationships are re-homed onto new_hotkey regardless of membership.
         assert_eq!(
             ChildKeys::<Test>::get(new_hotkey, parent_netuid),
             vec![(u64::MAX, child)],
             "parent relationship must migrate to new_hotkey on the parent-only subnet"
         );
+        assert_eq!(
+            ParentKeys::<Test>::get(new_hotkey, child_netuid),
+            vec![(u64::MAX, foreign_parent)],
+            "child relationship must still migrate to new_hotkey on the child-only subnet"
+        );
 
-        // FIXED: the per-subnet cooldown is recorded on the parent-only subnet too — the
-        // member-only filter would have left this at 0, leaving an un-rate-limited path to
-        // re-home parent/child relationships on that subnet.
+        // FIXED: the per-subnet cooldown is recorded on the member subnet AND the parent-only
+        // subnet (the member-only filter would have left the latter at 0).
+        assert_eq!(LastHotkeySwapOnNetuid::<Test>::get(member_netuid, coldkey), block);
         assert_eq!(
             LastHotkeySwapOnNetuid::<Test>::get(parent_netuid, coldkey),
             block,
             "all-subnets swap must record the cooldown on parent-key subnets, not just member subnets"
         );
-        // And the member subnet is still recorded, as before.
+
+        // Anti-griefing: the child-only subnet is NOT cooldown-gated. A third party (the
+        // foreign parent) set old_hotkey as its child without consent; gating on that would
+        // let it impose swap-cooldowns on the victim.
         assert_eq!(
-            LastHotkeySwapOnNetuid::<Test>::get(member_netuid, coldkey),
-            block
+            LastHotkeySwapOnNetuid::<Test>::get(child_netuid, coldkey),
+            0,
+            "child-only subnet must NOT be cooldown-gated (no-consent child assignment is a griefing vector)"
         );
     });
 }
```
