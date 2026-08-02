[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L910-918)
```text
    /// Note on pending transactions: the timelock check measures elapsed time from a transaction's
    /// `creation_time_secs`, not from when the timelock was activated. Because multisig transactions
    /// execute strictly in sequence order, this is only observable for transactions queued *after*
    /// this `upsert_timelock` call but *before* it executes — those transactions may become
    /// executable sooner than `timelock_period` seconds after this call takes effect, because part
    /// of their elapsed time is counted from before the new timelock was live. Transactions queued
    /// after this call has executed receive the full `timelock_period` protection. This residual
    /// window is bounded by the previous timelock period (or by approval time, if there was no
    /// prior timelock) and is considered an acceptable, operator-visible risk.
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1663-1682)
```text
        // If a timelock is configured, adjust and validate the override threshold
        // after owner/threshold changes.
        if (exists<MultisigAccountTimeLock>(multisig_address)) {
            let timelock = &mut MultisigAccountTimeLock[multisig_address];
            // If override threshold exceeds the new owner count, clamp it down and emit an event
            // so off-chain monitors observe the security-relevant mutation.
            if (timelock.override_threshold.is_some() && timelock.override_threshold.borrow() > &num_owners) {
                timelock.override_threshold = option::some(num_owners);
                emit(TimelockUpdated {
                    multisig_account: multisig_address,
                    timelock_period: timelock.timelock_period,
                    override_threshold: timelock.override_threshold,
                });
            };
            // Override threshold must still be greater than num_signatures_required.
            assert!(
                timelock.override_threshold.is_none() || timelock.override_threshold.borrow() > &multisig_account_ref_mut.num_signatures_required,
                error::invalid_state(EINVALID_TIMELOCK_OVERRIDE_THRESHOLD)
            );
        };
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3103-3134)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    #[expected_failure(abort_code = 0x30016, location = Self)]
    fun test_owner_removal_fails_if_override_becomes_invalid(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure timelock with override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Remove one owner: 3 -> 2 owners, override clamped to 2.
        // But num_signatures_required is also 2, so override (2) is NOT > threshold (2).
        // This should fail.
        remove_owner(multisig_signer, address_of(owner_3));
    }

    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    #[expected_failure(abort_code = 0x30016, location = Self)]
    fun test_raise_threshold_to_match_override_should_fail(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure timelock with override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Raise num_signatures_required to 3 = override_threshold.
        // Override must be strictly greater, so this should fail.
        update_signatures_required(multisig_signer, 3);
    }
```
