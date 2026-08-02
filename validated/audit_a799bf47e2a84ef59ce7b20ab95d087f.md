## Custody-grade finding: Multisig timelock bypass via independent `num_signatures_required` changes — (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The external report describes exploiting the fact that a security-relevant state change (large token buy) is not atomically protected from being raced by another action. The Aptos-native analog found here is in the newly added `MultisigAccountTimeLock` feature of `multisig_account.move`: the timelock's `override_threshold` invariant ("must be strictly greater than `num_signatures_required`") is enforced only at the moment the timelock is configured, but `num_signatures_required` can be changed independently and later at any time through the normal owner-quorum flow. Once `num_signatures_required` is raised to meet or exceed the previously configured `override_threshold`, the delay that the timelock was designed to enforce silently disappears for all subsequent transactions, without ever touching the timelock resource itself.

### Finding Description
`upsert_timelock_internal` validates the relationship between `override_threshold` and `num_signatures_required` only once, at configuration time: [1](#0-0) 

The stored `MultisigAccountTimeLock` resource is never re-validated afterward. Separately, `num_signatures_required` can be changed at any time via `update_signatures_required` / `add_owners_and_update_signatures_required` / `swap_owners_and_update_signatures_required`, all of which route through `update_owner_schema` and only touch `MultisigAccount`, with no interaction with `MultisigAccountTimeLock`: [2](#0-1) 

At execution time, `can_execute_with_timelock` checks two independent, un-cross-validated fields — `override_threshold` from `MultisigAccountTimeLock` and the approval count that is separately required to be `>= num_signatures_required` from `MultisigAccount` — as alternative bypass conditions: [3](#0-2) 

If `num_signatures_required` is later raised to a value `>= override_threshold` (which was only guaranteed to be strictly greater than the *original* `num_signatures_required`), then satisfying the now-mandatory quorum check (`num_approvals >= num_signatures_required`) automatically satisfies the override condition (`num_approvals >= override_threshold`) as well, since the two thresholds have converged. The timelock delay — the very protection meant to give honest owners a window to detect and reject a malicious or coerced transaction from a subset of colluding/compromised owners — is silently and permanently voided for the account, with no error, no event distinguishing this, and no re-check anywhere in the codebase (confirmed by scanning `upsert_timelock`, `remove_timelock`, and the owner/threshold update functions for any cross-reference to `MultisigAccountTimeLock`).

### Impact Explanation
This breaks the core custody guarantee of the timelock feature for a resource-account-backed multisig that may hold APT, fungible assets, or object ownership. The timelock is a defense specifically against fast, unreviewed execution by a bare quorum (e.g., a compromised subset of owners); once bypassed, any transaction meeting ordinary quorum — including a malicious drain of multisig-controlled funds — executes immediately instead of being held for the configured `timelock_period`, eliminating the intervention window for the remaining honest owners. This is a corruption of the custody/control-authority guarantee tied to a live multisig account, not a cosmetic or event-only issue.

### Likelihood Explanation
Likelihood is realistic: no special privilege is needed beyond the normal owner quorum already required to change `num_signatures_required` — an operation owners might do for entirely legitimate reasons (e.g., adding owners and raising quorum). No warning or validation prevents this misconfiguration from silently defeating the timelock; nothing in `update_signatures_required`, `add_owners_and_update_signatures_required`, or `swap_owners_and_update_signatures_required` inspects or corrects the coexisting `MultisigAccountTimeLock.override_threshold`. A colluding/compromised majority (meeting normal quorum, not necessarily unanimous) can engineer this state deliberately, then propose and instantly execute a malicious transaction that should have been delayed.

### Recommendation
When `num_signatures_required` is updated (in `update_owner_schema` / all callers that change it), re-validate any existing `MultisigAccountTimeLock.override_threshold` against the new value and either abort the update, force a corresponding timelock re-configuration, or automatically raise `override_threshold` to preserve `override_threshold > num_signatures_required`. Add a spec/invariant asserting `override_threshold > num_signatures_required` holds globally whenever `MultisigAccountTimeLock` exists, not just at the time `upsert_timelock` is called.

### Proof of Concept
1. Owners `{A, B, C, D}` create a multisig account with `num_signatures_required = 2` and configure `MultisigAccountTimeLock { timelock_period = 1 day, override_threshold = Some(3) }` via `upsert_timelock` (valid since `3 > 2` and `3 <= 4`).
2. Through normal governance (a transaction approved by any 2 owners, e.g. `A, B` colluding), call `update_signatures_required` to raise `num_signatures_required` to `3`.
3. `MultisigAccountTimeLock.override_threshold` remains `3` (untouched).
4. `A, B, C` now propose and approve a malicious transaction (e.g., transferring all multisig-held APT/FA to an attacker address) with exactly 3 approvals.
5. At `validate_multisig_transaction`, the mandatory quorum check `num_approvals(3) >= num_signatures_required(3)` passes, and `can_execute_with_timelock` also returns `true` immediately via the override branch `num_approvals(3) >= override_threshold(3)`, even though `timelock_period` (1 day) has not elapsed.
6. The transaction executes instantly, defeating the timelock protection that `D` (the remaining honest owner) relied on to notice and reject it in time.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L495-515)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L943-951)
```text
        let multisig_account_resource = &MultisigAccount[multisig_address];
        assert!(
            override_threshold.is_none() || *override_threshold.borrow() > multisig_account_resource.num_signatures_required,
            error::invalid_argument(EINVALID_TIMELOCK_OVERRIDE_THRESHOLD)
        );
        assert!(
            override_threshold.is_none() || *override_threshold.borrow() <= multisig_account_resource.owners.length(),
            error::invalid_argument(EINVALID_TIMELOCK_OVERRIDE_THRESHOLD)
        );
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1007-1019)
```text
    /// Add owners then update number of signatures required, in a single operation.
    entry fun add_owners_and_update_signatures_required(
        multisig_account: &signer,
        new_owners: vector<address>,
        new_num_signatures_required: u64
    ) {
        update_owner_schema(
            address_of(multisig_account),
            new_owners,
            vector[],
            option::some(new_num_signatures_required)
        );
    }
```
