Based on my investigation, the strongest Aptos-native analog to the Starknet bug's boundary-condition failure is in the custom multisig timelock override mechanism added to `multisig_account.move`. Note: I was unable to fetch the body of `num_approvals_and_rejections` in this final pass, so the vote-persistence claim below rests on the documented owner-list check happening only at vote time (per the spec table) plus the observed clamp logic — I flag this uncertainty explicitly.

### Title
Stale owner votes retained after removal can satisfy the timelock override threshold, bypassing the safety delay - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
The multisig account module implements an optional `MultisigAccountTimeLock` that requires either a time delay (`timelock_period`) or a super-majority "override" of approvals (`override_threshold`) before a transaction can execute early. `can_be_executed`/`can_execute` and `can_be_rejected` all rely on `num_approvals_and_rejections`, which counts votes stored in the transaction's `votes: SimpleMap<address,bool>` map at execution time. Votes are recorded against an address at the time of approval, and nothing in the reviewed owner-removal path (`update_owner_schema`, `remove_owners`) purges or invalidates votes cast by owners who are later removed.

### Finding Description
The timelock is a custody-relevant safety control: it exists specifically to give the account time to react before a transaction with `num_signatures_required` approvals (but below `override_threshold`) can move resource-account-held funds. Reaching `override_threshold` is meant to represent a strong, current consensus among *live* owners to bypass that delay. [1](#0-0) 

However, `can_execute_with_timelock` compares `num_approvals` (derived from `num_approvals_and_rejections`, which reads the persisted votes map) against `override_threshold` without any re-validation that each counted voter is still a current owner: [2](#0-1) 

Meanwhile, owner removal (`remove_owners` → `update_owner_schema`) only clamps the `override_threshold` numeric value down if it now exceeds the new owner count — it does not touch any pending transaction's vote map: [3](#0-2) 

This mirrors the structure of the Starknet bug: a boundary/consistency check (`assert_healthy_or_healthier` comparing against a stale `total_risk`) is evaluated against state that no longer reflects the true post-change condition. Here, `override_threshold` count is evaluated against a votes map that can contain approvals from addresses no longer in `owners`, so the "supermajority of live owners" invariant that justifies bypassing the timelock is broken.

### Impact Explanation
If exploitable as described, a removed/compromised owner's earlier approval could still count toward the override threshold, allowing the remaining owners (with fewer live signatures than the override policy actually requires) to execute a transaction immediately instead of waiting out the timelock. Because the resource account underlying the multisig can hold APT and other fungible assets, this would let a transaction move or reconfigure account-controlled assets before the safety window elapses — undermining the entire purpose of the timelock as a custody protection and potentially enabling fund extraction that the delay was meant to allow victims to stop.

### Likelihood Explanation
This requires a specific sequence (an owner votes, is later removed, and a threshold-sensitive transaction is executed while their stale vote is still counted) which needs a compromised/malicious owner or coordination among remaining owners, and is only relevant for multisig accounts that opt into the timelock feature. I was not able to fully confirm the implementation of `num_approvals_and_rejections` (its body was not retrieved) to prove definitively that it does not filter by current owner membership, so this should be verified before treating it as confirmed.

### Recommendation
Re-validate that every address counted in `num_approvals_and_rejections` (or specifically in the override-threshold check) is still present in `owners` at execution time, or purge/invalidate stale votes whenever the owner list changes, similar to how a fully-liquidated position should skip a stale risk check rather than evaluate against outdated totals.

### Proof of Concept
Not executed — this requires confirming `num_approvals_and_rejections`'s exact behavior (source not retrieved in this session) and running a Move test: create a timelocked multisig with 3 owners and `num_signatures_required = 1`, `override_threshold = 2`; have owner B approve a large-transfer transaction; remove owner B via a separate transaction; then attempt to execute the original transaction immediately (before `timelock_period` elapses) and observe whether B's stale approval still satisfies `override_threshold`.

**Caveat:** Given the incomplete verification of `num_approvals_and_rejections`, this finding should be treated as a strong candidate requiring confirmation rather than a fully proven vulnerability.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L481-515)
```text
    #[view]
    /// Return true if the owner can execute the transaction with given transaction id now.
    public fun can_execute(owner: address, multisig_account: address, sequence_number: u64): bool {
        assert_valid_sequence_number(multisig_account, sequence_number);
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, owner)) {
            num_approvals += 1;
        };

        is_owner(owner, multisig_account) &&
            sequence_number == last_resolved_sequence_number(multisig_account) + 1 &&
            num_approvals >= num_signatures_required(multisig_account) && can_execute_with_timelock(multisig_account, sequence_number, num_approvals)
    }

    /// Return true if the transaction with given transaction id can be executed immediately, or it has to wait
    /// for the timelock to expire.
    inline fun can_execute_with_timelock(multisig_account: address, sequence_number: u64, num_approvals: u64): bool {
        if (exists<MultisigAccountTimeLock>(multisig_account)) {
            let multisig_account_resource = &MultisigAccountTimeLock[multisig_account];
            let timelock = multisig_account_resource.timelock_period;
            let override_threshold = multisig_account_resource.override_threshold;

            // Get the pending transaction to check if the timelock has expired
            // Assume that the transaction has already been checked to exist and is valid
            let pending_transaction = get_transaction(multisig_account, sequence_number);

            // Use subtraction to avoid overflow (now_seconds() >= creation_time_secs is always true)
            let elapsed = now_seconds() - pending_transaction.creation_time_secs;

            // If the number of approvals meets the override threshold, or the timelock has expired, allow execution
            (override_threshold.is_some() && &num_approvals >= override_threshold.borrow()) || elapsed >= timelock
        } else {
            true
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1663-1683)
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
    }
```
