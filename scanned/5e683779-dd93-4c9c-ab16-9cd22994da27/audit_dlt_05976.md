# [?] Merge pull request #10 from opentensor/security/ghsa-2026-006-weights-pays-no-dispatch-only-ratelimit-flood

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/03a79d08e43d6178e6a6d52cfffcfc7b856bf32c
Type: security-commit

## Details
Merge pull request #10 from opentensor/security/ghsa-2026-006-weights-pays-no-dispatch-only-ratelimit-flood

set_weights / commit_weights family is `Pays::No` with the per-neuron rate limit enforced only in the dispatch body, enabling fee-free block-fill flooding

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
