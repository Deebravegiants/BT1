# [?] Merge remote-tracking branch 'origin/main' into security/ghsa-2026-002-swap-hotkey-v2-proxy-gap

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/183c4ebd5fdad6baa119a45f664de122798e4548
Type: security-commit

## Details
Merge remote-tracking branch 'origin/main' into security/ghsa-2026-002-swap-hotkey-v2-proxy-gap

# Conflicts:
#	runtime/tests/ghsa_repro.rs

## Patch
### pallets/subtensor/src/extensions/subtensor.rs
```diff
@@ -47,6 +47,27 @@ where
         Pallet::<T>::check_weights_min_stake(who, netuid)
     }
 
+    /// Mirror the per-neuron `WeightsSetRateLimit` throttle (otherwise only
+    /// enforced inside the dispatch body) into the transaction-validity gate so
+    /// over-rate `set_weights`/`commit_weights` transactions are rejected
+    /// pre-dispatch instead of being included for free (these calls are
+    /// `Pays::No`). Unregistered callers (whose UID cannot be resolved) pass
+    /// through here and are rejected by the dispatch body, preserving existing
+    /// error semantics.
+    pub fn check_weights_rate_limit(
+        who: &T::AccountId,
+        netuid: NetUid,
+        netuid_index: NetUidStorageIndex,
+    ) -> Result<(), CustomTransactionError> {
+        if let Ok(neuron_uid) = Pallet::<T>::get_uid_for_net_and_hotkey(netuid, who) {
+            let current_block = Pallet::<T>::get_current_block_as_u64();
+            if !Pallet::<T>::check_rate_limit(netuid_index, neuron_uid, current_block) {
+                return Err(CustomTransactionError::RateLimitExceeded);
+            }
+        }
+        Ok(())
+    }
+
     pub fn result_to_validity(result: Result<(), Error<T>>, priority: u64) -> TransactionValidity {
         match result {
             Ok(()) => Ok(ValidTransaction {
@@ -112,13 +133,27 @@ where
         };
 
         match call.is_sub_type() {
-            Some(Call::commit_weights { netuid, .. })
-            | Some(Call::commit_mechanism_weights { netuid, .. }) => {
-                if Self::check_weights_min_stake(who, *netuid) {
-                    Ok((Default::default(), (), origin))
-                } else {
-                    Err(CustomTransactionError::StakeAmountTooLow.into())
+            Some(Call::commit_weights { netuid, .. }) => {
+                if !Self::check_weights_min_stake(who, *netuid) {
+                    return Err(CustomTransactionError::StakeAmountTooLow.into());
                 }
+                // Mirror the in-dispatch commit rate limit
+                // (internal_commit_weights always enforces it).
+                Self::check_weights_rate_limit(who, *netuid, NetUidStorageIndex::from(*netuid))?;
+                Ok((Default::default(), (), origin))
+            }
+            Some(Call::commit_mechanism_weights { netuid, mecid, .. }) => {
+                if !Self::check_weights_min_stake(who, *netuid) {
+                    return Err(CustomTransactionError::StakeAmountTooLow.into());
+                }
+                // Mirror the in-dispatch commit rate limit
+                // (internal_commit_weights always enforces it).
+                Self::check_weights_rate_limit(
+                    who,
+                    *netuid,
+                    Pallet::<T>::get_mechanism_storage_index(*netuid, *mecid),
+                )?;
+                Ok((Default::default(), (), origin))
             }
             Some(Call::batch_commit_weights {
                 netuids,
@@ -241,13 +276,35 @@ where
                     Err(CustomTransactionError::InputLengthsUnequal.into())
                 }
             }
-            Some(Call::set_weights { netuid, .. })
-            | Some(Call::set_mechanism_weights { netuid, .. }) => {
-                if Self::check_weights_min_stake(who, *netuid) {
-                    Ok((Default::default(), (), origin))
-                } else {
-                    Err(CustomTransactionError::StakeAmountTooLow.into())
+            Some(Call::set_weights { netuid, .. }) => {
+                if !Self::check_weights_min_stake(who, *netuid) {
+                    return Err(CustomTransactionError::StakeAmountTooLow.into());
+                }
+                // Mirror the in-dispatch rate limit (only enforced when
+                // commit-reveal is disabled, matching internal_set_weights).
+                if !Pallet::<T>::get_commit_reveal_weights_enabled(*netuid) {
+                    Self::check_weights_rate_limit(
+                        who,
+                        *netuid,
+                        NetUidStorageIndex::from(*netuid),
+                    )?;
                 }
+                Ok((Default::default(), (), origin))
+            }
+            Some(Call::set_mechanism_weights { netuid, mecid, .. }) => {
+                if !Self::check_weights_min_stake(who, *netuid) {
+                    return Err(CustomTransactionError::StakeAmountTooLow.into());
+                }
+                // Mirror the in-dispatch rate limit (only enforced when
+                // commit-reveal is disabled, matching internal_set_weights).
+                if !Pallet::<T>::get_commit_reveal_weights_enabled(*netuid) {
+                    Self::check_weights_rate_limit(
+                        who,
+                        *netuid,
+                        Pallet::<T>::get_mechanism_storage_index(*netuid, *mecid),
+                    )?;
+                }
+                Ok((Default::default(), (), origin))
             }
             Some(Call::batch_set_weights {
                 netuids,
```

### pallets/subtensor/src/staking/claim_root.rs
```diff
@@ -460,7 +460,10 @@ impl<T: Config> Pallet<T> {
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
@@ -126,6 +129,35 @@ impl<T: Config> Pallet<T> {
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
@@ -152,6 +184,14 @@ impl<T: Config> Pallet<T> {
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

### pallets/subtensor/src/tests/claim_root.rs
```diff
@@ -2152,6 +2152,70 @@ fn test_claim_root_with_moved_stake() {
     });
 }
 
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
+        assert_eq!(RootClaimed::<Test>::get((netuid, &new_hotkey, &coldkey)), b);
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
+
 // ============================================================
 // GHSA-2026-012 regression test — security audit (June 2026)
 // Fails on the vulnerable code; passes with the fix in this PR.
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

### pallets/subtensor/src/tests/transaction_extension_pays_no.rs
```diff
@@ -685,3 +685,89 @@ fn extension_associate_evm_key_rejects_associate_rate_limit() {
         );
     });
 }
+
+// ============================================================
+// GHSA-2026-006 regression test — security audit (June 2026)
+// Fails on the vulnerable code; passes with the fix in this PR.
+// ============================================================
+use frame_support::assert_err;
+
+#[test]
+fn ghsa_2026_006_set_weights_paysno_validate_omits_ratelimit() {
+    new_test_ext(0).execute_with(|| {
+        let netuid = NetUid::from(1);
+        let hotkey = U256::from(1);
+        let coldkey = U256::from(2);
+
+        // Subnet with commit-reveal disabled so do_set_weights runs the
+        // per-neuron SetWeightsRateLimit check (weights.rs step 9).
+        add_network_disable_commit_reveal(netuid, 1, 0);
+        setup_reserves(
+            netuid,
+            1_000_000_000_000_u64.into(),
+            1_000_000_000_000_u64.into(),
+        );
+        // Register a real neuron (uid 0) so it exists on-network and its
+        // LastUpdate vector is sized for set_last_update_for_uid below.
+        register_ok_neuron(netuid, hotkey, coldkey, 0);
+        let uid = SubtensorModule::get_uid_for_net_and_hotkey(netuid, &hotkey).unwrap();
+
+        // Drop the min-stake threshold to 0 so the ONLY thing that validate()
+        // could reject for is the rate limit. This isolates the fix: the
+        // min-stake mempool gate passes, and the rate-limit gate must now also
+        // be enforced in validate().
+        SubtensorModule::set_stake_threshold(0);
+        assert!(SubtensorModule::check_weights_min_stake(&hotkey, netuid));
+
+        // Configure a non-zero per-neuron rate limit and mark this neuron as
+        // having "just" set weights at the current block, so the next
+        // set_weights is over-rate.
+        SubtensorModule::set_weights_set_rate_limit(netuid, 100);
+        System::set_block_number(10u64.into());
+        let current_block = SubtensorModule::get_current_block_as_u64();
+        let netuid_index = SubtensorModule::get_mechanism_storage_index(netuid, MechId::MAIN);
+        SubtensorModule::set_last_update_for_uid(netuid_index, uid, current_block);
+
+        // Sanity: the in-dispatch rate-limit helper now reports over-rate.
+        assert!(!SubtensorModule::check_rate_limit(
+            netuid_index,
+            uid,
+            current_block
+        ));
+
+        // Self-weight call (uids/weights == [uid]/[1]) avoids needing a
+        // validator permit, so dispatch reaches the rate-limit gate.
+        let call = RuntimeCall::SubtensorModule(SubtensorCall::set_weights {
+            netuid,
+            dests: vec![uid],
+            weights: vec![1],
+            version_key: 0,
+        });
+
+        // (a) set_weights is declared Pays::No -> if validate accepted it, it
+        //     would be included into a block for free.
+        let info = call.get_dispatch_info();
+        assert_eq!(info.pays_fee, frame_support::dispatch::Pays::No);
+
+        // (b) THE FIX: SubtensorTransactionExtension::validate now enforces the
+        //     per-neuron SetWeightsRateLimit. An over-rate set_weights is
+        //     rejected pre-dispatch with RateLimitExceeded, so it can never be
+        //     admitted to the mempool / included for free.
+        let err = validate_signed(hotkey, &call).unwrap_err();
+        assert_eq!(err, CustomTransactionError::RateLimitExceeded.into());
+
+        // (c) The dispatch path still enforces the rate limit as the
+        //     authoritative check (defence in depth for any tx that slips past
+        //     the pool-level filter, e.g. two over-rate txs in the same block).
+        assert_err!(
+            SubtensorModule::set_weights(
+                RuntimeOrigin::signed(hotkey),
+                netuid,
+                vec![uid],
+                vec![1],
+                0,
+            ),
+            Error::<Test>::SettingWeightsTooFast
+        );
+    });
+}
```

### runtime/src/lib.rs
```diff
@@ -655,6 +655,10 @@ subtensor_macros::define_proxy_filters! {
         SubtensorModule::transfer_stake,
         SubtensorModule::schedule_swap_coldkey,
         SubtensorModule::swap_coldkey,
+        SubtensorModule::announce_coldkey_swap,
+        SubtensorModule::swap_coldkey_announced,
+        SubtensorModule::clear_coldkey_swap_announcement,
+        SubtensorModule::dispute_coldkey_swap,
     }
 
     NonFungible => deny {
@@ -674,7 +678,12 @@ subtensor_macros::define_proxy_filters! {
         SubtensorModule::root_register,
         SubtensorModule::schedule_swap_coldkey,
         SubtensorModule::swap_coldkey,
+        SubtensorModule::announce_coldkey_swap,
+        SubtensorModule::swap_coldkey_announced,
+        SubtensorModule::clear_coldkey_swap_announcement,
+        SubtensorModule::dispute_coldkey_swap,
         SubtensorModule::swap_hotkey,
+        SubtensorModule::swap_hotkey_v2,
     }
 
     Transfer => allow {
@@ -704,6 +713,10 @@ subtensor_macros::define_proxy_filters! {
         SubtensorModule::root_register,
         SubtensorModule::burned_register,
         Sudo::*,
+        SubtensorModule::announce_coldkey_swap,
+        SubtensorModule::swap_coldkey_announced,
+        SubtensorModule::clear_coldkey_swap_announcement,
+        SubtensorModule::dispute_coldkey_swap,
     }
 
     Triumvirate => deny_all;
@@ -743,6 +756,7 @@ subtensor_macros::define_proxy_filters! {
 
     SwapHotkey => allow {
         SubtensorModule::swap_hotkey,
+        SubtensorModule::swap_hotkey_v2,
     }
 
     SubnetLeaseBeneficiary => allow {
```

### runtime/tests/ghsa_repro.rs
```diff
@@ -80,6 +80,74 @@ fn set_subnet_owner_hotkey_c64() -> RuntimeCall {
     })
 }
 
+/// GHSA-2026-001 — NonTransfer and NonFungible proxies (the two "cannot move my funds"
+/// types) ALLOW the new coldkey-swap lifecycle, so a restricted delegate can take over
+/// the whole coldkey. Reproduced by asserting the calls are NOT filtered.
+#[test]
+fn ghsa_2026_001_restricted_proxies_allow_coldkey_swap_lifecycle() {
+    let announce = announce_coldkey_swap();
+    let exec = swap_coldkey_announced();
+
+    // These two proxy types DO block direct exfiltration (transfer_stake denied) ...
+    for pt in [ProxyType::NonTransfer, ProxyType::NonFungible] {
+        assert!(
+            !pt.filter(&transfer_stake()),
+            "precondition: {pt:?} should deny transfer_stake (it is a fund-protection type)"
+        );
+        // ... and after the fix they ALSO block the swap lifecycle that would exfiltrate everything:
+        assert!(
+            !pt.filter(&announce),
+            "regression (GHSA-2026-001 fixed): {pt:?} must DENY announce_coldkey_swap"
+        );
+        assert!(
+            !pt.filter(&exec),
+            "regression (GHSA-2026-001 fixed): {pt:?} must DENY swap_coldkey_announced"
+        );
+        // Contrast: the legacy swap_coldkey they replaced IS denied — proving the gap is
+        // specifically the un-listed new lifecycle calls.
+        assert!(
+            !pt.filter(&swap_coldkey_legacy()),
+            "{pt:?} correctly denies legacy swap_coldkey — the new calls were simply never added"
+        );
+    }
+}
+
+/// Scope correction for GHSA-2026-001: NonCritical is NOT a fund-protection type — it
+/// already permits transfer_stake — so the coldkey-swap gap is not an *escalation* for it.
+/// Documents why NonCritical is excluded from the finding.
+#[test]
+fn ghsa_2026_001_noncritical_is_not_a_fund_protection_type() {
+    assert!(
+        ProxyType::NonCritical.filter(&transfer_stake()),
+        "NonCritical already allows transfer_stake, so coldkey-swap adds no new capability"
+    );
+}
+
+/// GHSA-2026-002 — NonFungible denies the deprecated swap_hotkey (call 70) but ALLOWS the
+/// live swap_hotkey_v2 (call 72); and the SwapHotkey allow-list permits only call 70.
+#[test]
+fn ghsa_2026_002_nonfungible_allows_swap_hotkey_v2_gap() {
+    // The denylist blocks the old call but not the live superset.
+    assert!(
+        !ProxyType::NonFungible.filter(&swap_hotkey_v1()),
+        "precondition: NonFungible denies deprecated swap_hotkey (call 70)"
+    );
+    assert!(
+        !ProxyType::NonFungible.filter(&swap_hotkey_v2()),
+        "regression (GHSA-2026-002 fixed): NonFungible must DENY the live swap_hotkey_v2 (call 72)"
+    );
+
+    // Inverse breakage: SwapHotkey allow-list only permits the deprecated call.
+    assert!(
+        ProxyType::SwapHotkey.filter(&swap_hotkey_v1()),
+        "precondition: SwapHotkey allows deprecated swap_hotkey (call 70)"
+    );
+    assert!(
+        ProxyType::SwapHotkey.filter(&swap_hotkey_v2()),
+        "regression (GHSA-2026-002 fixed): SwapHotkey must ALLOW the live swap_hotkey_v2 (call 72)"
+    );
+}
+
 /// GHSA-2026-003 — the Owner proxy excepts sudo_set_sn_owner_hotkey (call 67) but the
 /// duplicate alias sudo_set_subnet_owner_hotkey (call 64) is allowed by the AdminUtils::*
 /// wildcard, bypassing the carve-out.
```
