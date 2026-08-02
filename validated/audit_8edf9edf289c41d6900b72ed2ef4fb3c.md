[1](#0-0) [2](#0-1)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L163-178)
```text
    /// Support for Multisig TimeLock.
    /// `drop` is safe here because this resource holds only primitives (no capabilities, no
    /// event handles). It's used so that `remove_timelock` can `move_from` without destructuring.
    /// Note that because on-chain transactions cannot realistically be executed in less than a
    /// second, the resolution of `creation_time_secs` is at-second granularity — setting/removing
    /// a timelock within the same on-chain second as a pending transaction's creation is not a
    /// concern in practice.
    enum MultisigAccountTimeLock has key, drop {
        V1 {
            /// The time lock period in seconds after the creation of the multisig transaction.
            timelock_period: u64,
            /// The number of approvals required to bypass the timelock and execute immediately.
            /// Must be greater than the number of signatures required normally and less than or equal to the number of owners.
            override_threshold: Option<u64>,
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1656-1681)
```text
        // Verify number of owners.
        let num_owners = multisig_account_ref_mut.owners.length();
        assert!(
            num_owners >= multisig_account_ref_mut.num_signatures_required,
            error::invalid_state(ENOT_ENOUGH_OWNERS)
        );

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
```
