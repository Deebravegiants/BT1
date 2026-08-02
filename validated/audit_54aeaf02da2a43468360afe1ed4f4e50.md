## Finding

### Title
Multisig timelock protection is enforced only in read-only view functions, not in the on-chain execution validation path - ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
The external report's bug class is: a security-critical value (the allowance) is computed correctly by one code path but a different, actually-invoked code path applies an incorrect/absent check, letting an unprivileged caller exceed the intended authorization limit. The Aptos-native analog here is the `MultisigAccountTimeLock` feature added to `multisig_account.move`: the timelock-and-override logic (`can_execute_with_timelock`) is correctly wired into the `#[view]` functions `can_be_executed` and `can_execute`, but these are advisory read-only helpers. The actual authorization gate for real fund/owner-control-changing execution is the `validate_multisig_transaction` / `successful_transaction_execution_cleanup` path.

### Finding Description
`upsert_timelock`/`upsert_timelock_internal` let an owner-controlled multisig account publish a `MultisigAccountTimeLock` resource that is supposed to delay execution of an approved transaction until either `timelock_period` elapses or an `override_threshold` (stricter than `num_signatures_required`) of approvals is reached: [1](#0-0) 

This check is called from the two `#[view]` functions: [2](#0-1) 

`#[view]` functions in Aptos are for off-chain querying only — they are never invoked as part of on-chain transaction validation/execution. The finding-15 audit note embedded in the doc for this module describes the actual on-chain execution gate (`validate_multisig_transaction`, `execute_rejected_transaction`, `successful_transaction_execution_cleanup`) purely in terms of vote counts, with no mention of timelock: [3](#0-2) 

A repo-wide search for `MultisigAccountTimeLock` shows it is referenced only inside `multisig_account.move` itself (plus its generated doc and formal-spec files) and nowhere in the VM/execution-validation surface, which is consistent with the timelock resource being read only by the two view functions and never consulted by the real execution-authorization function.

This mirrors the Dexter bug pattern exactly: the *documented/intended* formula (delay execution until timelock or override) is implemented, but it is not wired into the code path that unprivileged callers actually invoke to move value/change ownership (executing an approved multisig transaction that can withdraw a resource account's coins, rotate keys, add/remove owners, etc.).

### Impact Explanation
If `validate_multisig_transaction`/execution cleanup does not consult `can_execute_with_timelock`, any multisig owner who has helped reach the *ordinary* `num_signatures_required` threshold can execute a transaction immediately, completely bypassing the timelock delay/override-threshold protection that account owners configured specifically to protect custody of assets held by the multisig (or by a resource account controlled via `signer_cap`, similar to the `resource_account`/`vesting`/`simple_defi` patterns shown in this repo where a signer capability is used to withdraw and transfer coins). This defeats a security control meant to give co-owners a window to detect and reject a malicious/compromised proposal before funds move, directly enabling unauthorized transfer, freeze, or owner-reassignment of multisig-held assets.

### Likelihood Explanation
Likelihood is high if confirmed, because exploitation requires nothing more than normal multisig operation: reaching the already-required `num_signatures_required` votes (which is exactly what would happen in the course of legitimate use, whether by a malicious insider or a compromised owner key) triggers execution regardless of the timelock the account holders explicitly configured for extra protection. However, I was not able to directly inspect the body of `validate_multisig_transaction` in this pass (it was not returned by search) to conclusively confirm it omits the `can_execute_with_timelock` check — this is inferred from (a) the timelock resource/check being referenced nowhere outside `multisig_account.move`'s own view functions and tests, and (b) the audit-table description of the execution-validation functions making no mention of timelock gating. This should be verified directly against `validate_multisig_transaction`'s source before treating this as confirmed.

### Recommendation
- Verify whether `validate_multisig_transaction` (and/or `successful_transaction_execution_cleanup`) calls `can_execute_with_timelock`/`can_be_executed` before permitting execution.
- If it does not, add the timelock/override check directly into the real execution-authorization function (not just the `#[view]` helpers), so that on-chain execution is actually gated by the same rule that `can_be_executed` reports to callers.
- Add an integration/e2e test (not just the unit tests already present around `can_be_executed`) that attempts to execute a timelocked, non-override-threshold-met transaction through the real multisig execution entry point and asserts it aborts.

### Proof of Concept
Not constructed — this requires confirming the concrete signature/body of `validate_multisig_transaction` to demonstrate that it does not invoke `can_execute_with_timelock`; that source was not retrievable in this session. A concrete PoC would: (1) create a multisig account with `num_signatures_required = 2`, (2) call `upsert_timelock` with a long `timelock_period` and `override_threshold = 3`, (3) create and approve a transaction that withdraws multisig-held funds with only 2 approvals, (4) attempt to execute it immediately through the actual transaction-execution flow (not the view functions) and observe whether it succeeds despite `can_be_executed` reporting `false`.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L471-493)
```text
    #[view]
    /// Return true if the transaction with given transaction id can be executed now.
    public fun can_be_executed(multisig_account: address, sequence_number: u64): bool {
        assert_valid_sequence_number(multisig_account, sequence_number);
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);

        sequence_number == last_resolved_sequence_number(multisig_account) + 1 &&
            num_approvals >= num_signatures_required(multisig_account) && can_execute_with_timelock(multisig_account, sequence_number, num_approvals)
    }

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

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L4494-4500)
```markdown
<tr>
<td>15</td>
<td>Only owners are allowed to execute a valid transaction, if the number of approvals meets the k-of-n criteria, finally the executed transaction should be removed.</td>
<td>Critical</td>
<td>Functions execute_rejected_transaction and validate_multisig_transaction can only be called by the owner which validates the transaction and based on the number of approvals and rejections it proceeds to execute the transactions. For rejected transaction, the transactions are immediately removed from the MultisigAccount via remove_executed_transaction. VM validates the transaction via validate_multisig_transaction and cleans up the transaction via successful_transaction_execution_cleanup and failed_transaction_execution_cleanup.</td>
<td>Audited that it aborts if the caller is not in the owner's list (execute_rejected_transaction, validate_multisig_transaction). Audited that it aborts if the transaction with the given sequence number doesn't exist in the account (execute_rejected_transaction, validate_multisig_transaction). Audited that it aborts if the votes (approvals or rejections) are less than num_signatures_required (execute_rejected_transaction, validate_multisig_transaction). Audited that the transaction is removed from the MultisigAccount (execute_rejected_transaction, remove_executed_transaction, successful_transaction_execution_cleanup, failed_transaction_execution_cleanup).</td>
</tr>
```
