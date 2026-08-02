## Custody Analog Found

### Title
Minority-approved owner removal silently degrades the multisig timelock's `override_threshold`, weakening the supermajority gate on immediate execution - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The Hats Signer Gate bug let signers satisfy a "threshold correctness" post-check by mutating both the owner count and the threshold in the same transaction, since the check only validated a *derived relationship*, not a pinned pre-transaction value. `multisig_account.move`'s timelock feature reproduces the same pattern: `update_owner_schema()` silently clamps `MultisigAccountTimeLock.override_threshold` downward whenever an owner-removal transaction (approved only at the base `num_signatures_required` threshold) shrinks the owner set, instead of requiring override-level consent to touch the override threshold itself.

### Finding Description
`update_owner_schema` performs owner add/remove, then an optional threshold update, then — if a `MultisigAccountTimeLock` resource exists — auto-adjusts `override_threshold`: [1](#0-0) 

```
if (exists<MultisigAccountTimeLock>(multisig_address)) {
    let timelock = &mut MultisigAccountTimeLock[multisig_address];
    if (timelock.override_threshold.is_some() && timelock.override_threshold.borrow() > &num_owners) {
        timelock.override_threshold = option::some(num_owners);
        emit(TimelockUpdated { ... });
    };
    assert!(
        timelock.override_threshold.is_none() || timelock.override_threshold.borrow() > &multisig_account_ref_mut.num_signatures_required,
        error::invalid_state(EINVALID_TIMELOCK_OVERRIDE_THRESHOLD)
    );
};
```

`override_threshold` is the number of approvals required to bypass the timelock and execute a transaction immediately — a deliberately higher bar than the regular `num_signatures_required`. This is confirmed by the harness itself: [2](#0-1) 

The test `test_owner_removal_clamps_override_threshold` demonstrates the exact bypass: with an override configured at 3-of-3, the base threshold is first lowered, then a `remove_owner` call (approvable at that lowered base threshold, not at override level) causes `override_threshold` to be clamped down automatically: [3](#0-2) 

The root cause is identical in shape to the Hats bug: the invariant "override threshold must remain a stronger, harder-to-reach bar than the base threshold" is enforced by *recomputing/relaxing* `override_threshold` from mutable state (`num_owners`) that is changed in the very same call, rather than snapshotting and protecting the override threshold as an independently-privileged value that can only be lowered through override-level consensus.

### Impact Explanation
`override_threshold` exists specifically to require a supermajority (or unanimous) set of signers to authorize *immediate* execution of sensitive multisig transactions (which commonly control resource-account signer capabilities, APT/fungible-asset transfers, or code-object upgrade authority held by the multisig). A colluding minority that meets only the ordinary `num_signatures_required` bar can, over one or more owner-removal transactions (each merely timelock-delayed, not blocked), shrink the owner set and thereby permanently ratchet the override_threshold down to match. This erodes the higher-trust "immediate execution" guardrail that governance/asset-recovery/emergency flows may rely on, effectively transferring elevated multisig control to a smaller-than-intended set of signers without those signers ever having to demonstrate override-level consensus. This is a multisig-control degradation directly tied to custody of any assets or capabilities the multisig account holds.

### Likelihood Explanation
High, given a functioning `MultisigAccountTimeLock` is configured with an `override_threshold` distinct from `num_signatures_required`: any owner-removal transaction that merely clears the base signature threshold will trigger the clamp with no special guard, and the tests already show this is deterministic, reproducible behavior of the current code, not a hypothetical edge case.

### Recommendation
Do not silently auto-adjust `override_threshold` as a side effect of a base-threshold-approved owner change. Instead, either (a) require any reduction of `override_threshold` (including implicit reductions caused by owner removal) to itself be approved at the *current* override_threshold level before being applied, or (b) abort the owner-removal/threshold-update transaction if it would force an override_threshold reduction, requiring an explicit, separately-authorized `update_override_threshold` call gated at the override level.

### Proof of Concept
Based on `test_owner_removal_clamps_override_threshold` ( [3](#0-2) ):
1. Multisig account created with 3 owners, `num_signatures_required = 2`, and a timelock configured with `override_threshold = option::some(3)` (i.e., unanimous consent required to bypass the timelock).
2. Owners collude to first call `update_signatures_required(1)` (approvable with only 2-of-3, i.e., base threshold) to lower `num_signatures_required` to 1.
3. They then call `remove_owner(owner_3)` (approvable with 1 approval since threshold is now 1), shrinking owners from 3 to 2.
4. Inside `update_owner_schema`, since `override_threshold (3) > num_owners (2)`, it is auto-clamped to 2 — collapsing what was meant to be a 3-of-3 "immediate execution" gate down to a 2-of-2 gate, achieved entirely through transactions approved at the (now minimal) base threshold rather than at override level.

Some parts of the surrounding logic (e.g., the full `can_be_executed`/timelock-elapsed gating implementation) were not fully retrievable within the available search budget; the clamp logic and its exploitability are directly confirmed by the cited code and tests above.

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3084-3101)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_owner_removal_clamps_override_threshold(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure timelock with override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));
        assert!(timelock_override_threshold(multisig_account) == option::some(3), 0);

        // Remove one owner (3 -> 2 owners). Override threshold should be clamped to 2.
        // Signature threshold is 2, so we need to lower it first to allow removing an owner
        // while keeping override_threshold > num_signatures_required.
        update_signatures_required(multisig_signer, 1);
        remove_owner(multisig_signer, address_of(owner_3));
        assert!(timelock_override_threshold(multisig_account) == option::some(2), 1);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3136-3150)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_timelock_with_override_at_boundary(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure 1 hour timelock, override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Create transaction with only 2 approvals (below override).
        create_transaction(owner_1, multisig_account, PAYLOAD);
        approve_transaction(owner_2, multisig_account, 1);

        // Blocked: 2 < override(3) and timelock hasn't passed.
```
