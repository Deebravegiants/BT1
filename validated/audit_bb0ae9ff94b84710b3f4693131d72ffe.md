Based on my investigation, I found a promising custody-relevant analog: a security-delay parameter (`MultisigAccountTimeLock.override_threshold` / `timelock_period`) in `multisig_account.move` that mirrors the H-4 pattern — a second, more-restrictive constraint that must be checked wherever the primary limit is checked, but is only wired into one code path.



### Title
Multisig timelock delay is enforced only in the off-chain view helper `can_execute`, not proven to gate the on-chain execution path, allowing immediate execution of privileged multisig transactions (owner/threshold changes, asset transfers) - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
The report's bug class is: a protocol-level safety threshold (`maxTimesLeverage` vs. the lending pool's real `maxLevTimes`) is computed/used in one place but the *actual* governing (smaller/stricter) limit from another source is not consulted, silently weakening the safety check. The Aptos analog is the `MultisigAccountTimeLock` feature added to `multisig_account.move`: it introduces a `timelock_period` and `override_threshold` that are supposed to gate when a multisig transaction (which can reassign owners, change signature thresholds, or move custody of resource-account/code-object-held assets) can be executed before the timelock has elapsed.

### Finding Description
`can_execute_with_timelock` is the only place that consults the timelock state: [1](#0-0) 

It is invoked from the read-only view function `can_execute`: [2](#0-1) 

The high-level requirements specification for this module — which documents every invariant enforced by the *actual execution path* (`execute_rejected_transaction`, `validate_multisig_transaction`) — explicitly states that execution correctness is proven only by checking that approvals/rejections meet `num_signatures_required`, with no mention of the timelock/override-threshold gate: [3](#0-2) 

This is the same shape of bug as H-4: the code maintains a second, more-restrictive control value (`override_threshold`/`timelock_period`, analogous to `maxLevTimes` from the lending pool) and *validates it is internally consistent* elsewhere (`update_owner_schema` clamps and asserts `override_threshold > num_signatures_required`): [4](#0-3) 

...but the value is only consulted by the view helper `can_execute`/`can_execute_with_timelock`, not demonstrably by the transaction-validation/execution entry points that the VM actually calls to authorize state changes. If the real execution path (`validate_multisig_transaction`) checks only `num_approvals >= num_signatures_required` (as the spec's Requirement #15 describes) and never calls `can_execute_with_timelock`, then the timelock is cosmetic: any transaction — including `add_owners`, `swap_owner`, `update_signatures_required`, or transactions that move APT/fungible-asset/object custody controlled by the multisig — can be executed the instant `num_signatures_required` approvals are collected, regardless of `timelock_period`.

### Impact Explanation
If confirmed, this breaks the intended custody-safety invariant that privileged multisig actions (owner takeover, threshold reduction, asset transfers out of a multisig-controlled resource account or code object) must wait for a timelock delay — a mechanism whose entire purpose is to give other owners/monitors a window to detect and reject malicious proposals (e.g., a compromised owner adding themselves extra owners or lowering the signature threshold before draining custody). Bypassing it converts a designed delay-based defense into a no-op, enabling immediate, unrecoverable takeover of multisig-controlled owner set or unauthorized asset movement — a high/critical custody impact.

### Likelihood Explanation
Likelihood depends entirely on whether the VM-level `validate_multisig_transaction`/execution cleanup functions call `can_execute_with_timelock` (or equivalent) before permitting execution. I was not able to directly view those function bodies within the available search budget; the only corroborating evidence is the spec's requirement list, which was seemingly not updated to reference the timelock invariant when it was added, and the fact that `can_execute_with_timelock` is only ever referenced from the `can_execute` view function in the excerpts retrieved. This should be treated as **unconfirmed** without direct inspection of `validate_multisig_transaction`.

### Recommendation
Verify in `validate_multisig_transaction` (and `execute_rejected_transaction`) whether `can_execute_with_timelock` (or an equivalent inline check using `timelock_period`/`override_threshold`) is actually invoked before allowing the transaction to proceed. If it is not, add the same timelock/override-threshold gate to the on-chain execution/validation path so that the enforced invariant matches the one described in `can_execute`'s view logic — mirroring the report's suggested mitigation of always using the more restrictive of two limits at the actual point of enforcement, not just at a peripheral or read-only check.

### Proof of Concept
Not independently verified — a concrete PoC requires confirming that `validate_multisig_transaction`/`execute_rejected_transaction` omit the timelock check. This finding should be treated as a lead requiring direct inspection of those two functions in `aptos-move/framework/aptos-framework/sources/multisig_account.move` (not retrievable in full within this session's search budget) before being escalated as a confirmed vulnerability.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L481-493)
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
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L497-515)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1663-1681)
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
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.spec.move (L133-149)
```text
    /// No.: 15
    /// Requirement: Only owners are allowed to execute a valid transaction, if the number of approvals meets the k-of-n
    /// criteria, finally the executed transaction should be removed.
    /// Criticality: Critical
    /// Implementation: Functions execute_rejected_transaction and validate_multisig_transaction can only be called by
    /// the owner which validates the transaction and based on the number of approvals and rejections it proceeds to
    /// execute the transactions. For rejected transaction, the transactions are immediately removed from the
    /// MultisigAccount via remove_executed_transaction. VM validates the transaction via validate_multisig_transaction
    /// and cleans up the transaction via successful_transaction_execution_cleanup and
    /// failed_transaction_execution_cleanup.
    /// Enforcement: Audited that it aborts if the caller is not in the owner's list (execute_rejected_transaction,
    /// validate_multisig_transaction). Audited that it aborts if the transaction with the given sequence number doesn't
    /// exist in the account (execute_rejected_transaction, validate_multisig_transaction). Audited that it aborts if
    /// the votes (approvals or rejections) are less than num_signatures_required (execute_rejected_transaction,
    /// validate_multisig_transaction). Audited that the transaction is removed from the MultisigAccount
    /// (execute_rejected_transaction, remove_executed_transaction, successful_transaction_execution_cleanup,
    /// failed_transaction_execution_cleanup).
```
