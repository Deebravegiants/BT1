Based on my investigation, the strongest custody-analog to the Solidity `Timelock.updateDelay` self-authorization bug in this codebase is in Aptos's `multisig_account.move` timelock feature — not because the self-call pattern is broken (Aptos's VM-mediated multisig execution model legitimately supports these "self-update" `entry fun`s, unlike the unreachable Solidity check), but because the *invariant* that gives the timelock's override mechanism meaning is never re-validated when the multisig's quorum configuration changes later.

### Title
Multisig timelock override_threshold invariant is not re-validated after `update_signatures_required`, silently disabling timelock protection - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`upsert_timelock_internal` enforces that `override_threshold > num_signatures_required` at the moment the timelock is configured [1](#0-0) . However, `num_signatures_required` can later be changed independently via `update_signatures_required` / `update_owner_schema`, which do not re-check or refresh the `MultisigAccountTimeLock.override_threshold` invariant [2](#0-1) . If `num_signatures_required` is raised to meet or exceed the previously configured `override_threshold`, the timelock's bypass check becomes trivially true for every future transaction.

### Finding Description
The timelock's protective logic is in `can_execute_with_timelock`: [3](#0-2) 

It is invoked from `validate_multisig_transaction` only *after* the code has already asserted `num_approvals >= num_signatures_required` [4](#0-3) .

The override branch is:
```
(override_threshold.is_some() && &num_approvals >= override_threshold.borrow()) || elapsed >= timelock
```
This is only safe as an "emergency bypass, requiring extra approvals beyond the normal quorum" if `override_threshold > num_signatures_required` holds at all times — which is exactly what `upsert_timelock_internal` checks at configuration time [5](#0-4) . But `update_signatures_required` (and the other owner/quorum-changing entry functions that funnel into `update_owner_schema`) never re-check this against any existing `MultisigAccountTimeLock` resource [2](#0-1) . Once `num_signatures_required >= override_threshold`, any transaction that clears ordinary quorum (`num_approvals >= num_signatures_required`) automatically also clears `num_approvals >= override_threshold`, making the `elapsed >= timelock` clause irrelevant — the timelock is bypassed for every subsequent transaction without ever touching `upsert_timelock` or `remove_timelock`, and without emitting `TimelockUpdated`/`TimelockRemoved` events that operators/monitors would watch for.

### Impact Explanation
The timelock is a custody-control feature intended to give owners/monitors a window to detect and react to malicious multisig transactions (e.g., large APT/fungible-asset transfers, owner-set changes, resource-account or code-object control transfers) before they execute. An owner subset that can pass a normal `update_signatures_required` proposal (which requires only the pre-existing quorum, not the override quorum) can silently and permanently neutralize the timelock's delay guarantee for all future transactions, including transfers of custodied assets, without any visible timelock-specific event. This directly undermines a custody/recovery-rights safeguard for multisig-held value.

### Likelihood Explanation
Likely to occur in practice for any multisig that (a) enables the optional timelock feature, and (b) later legitimately grows its owner set or otherwise increases `num_signatures_required` (e.g., in response to onboarding new signers) — a routine operational action that has no reason to be checked against timelock configuration by an operator. No malicious intent is required for the invariant to break; it can happen through normal quorum management.

### Recommendation
In `update_owner_schema` (and thus all functions built on it: `add_owners`, `remove_owners`, `swap_owner(s)`, `update_signatures_required`, `*_and_update_signatures_required`), if `MultisigAccountTimeLock` exists at the account, re-validate that `override_threshold` (if set) remains `> new_num_signatures_required` and `<= new owners.length()`; either abort the owner/quorum-changing transaction or automatically clear/adjust the override threshold and emit a `TimelockUpdated`/`TimelockRemoved` event so the change is auditable.

### Proof of Concept
1. Create a multisig account with `owners.length() == 5`, `num_signatures_required = 2`.
2. Call `upsert_timelock(timelock_period = X, override_threshold = Some(3))` — passes validation since `3 > 2` and `3 <= 5`.
3. Later, propose and execute `update_signatures_required(new_num_signatures_required = 3)` through the normal proposal flow (requires only the pre-existing quorum of 2 approvals) — no re-check of the timelock invariant occurs.
4. Now `num_signatures_required == override_threshold == 3`. Any future transaction that reaches the ordinary 3-approval quorum automatically satisfies `num_approvals >= override_threshold`, so `can_execute_with_timelock` returns `true` immediately in `validate_multisig_transaction`, regardless of `elapsed >= timelock_period`.
5. The timelock delay is bypassed for all subsequent transactions, with no `TimelockUpdated`/`TimelockRemoved` event ever emitted.

**Note on confidence**: I was not able to view the full body of `update_owner_schema` (only its call sites and doc comments) within the available search budget, so I could not directly confirm from source that it lacks any timelock re-validation logic — this is inferred from (a) the absence of any `MultisigAccountTimeLock`/timelock reference in `update_owner_schema`'s call sites, comments, or the pre-existing formal audit checklist (which predates the timelock feature and never mentions it), and (b) the fact that only `upsert_timelock_internal` contains the override-threshold bound checks. If a Devin session with full file access confirms `update_owner_schema` does perform such a check, this finding would not hold.

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1087-1101)
```text
    /// Update the number of signatures required to execute transaction in the specified multisig account.
    ///
    /// This can only be invoked by the multisig account itself, through the proposal flow.
    /// Note that this function is not public so it can only be invoked directly instead of via a module or script. This
    /// ensures that a multisig transaction cannot lead to another module obtaining the multisig signer and using it to
    /// maliciously alter the number of signatures required.
    entry fun update_signatures_required(
        multisig_account: &signer, new_num_signatures_required: u64) {
        update_owner_schema(
            address_of(multisig_account),
            vector[],
            vector[],
            option::some(new_num_signatures_required)
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1348-1359)
```text
        // Count approvals, including the executing owner's implicit vote.
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, address_of(owner))) {
            num_approvals += 1;
        };
        assert!(num_approvals >= num_signatures_required(multisig_account), error::invalid_argument(ENOT_ENOUGH_APPROVALS));

        // Timelock check — separate from quorum so the error is unambiguous.
        assert!(
            can_execute_with_timelock(multisig_account, sequence_number, num_approvals),
            error::invalid_state(ETIMELOCK_NOT_EXPIRED),
        );
```
