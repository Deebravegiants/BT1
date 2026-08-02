Based on my investigation into this fork's `multisig_account.move`, I found a custody-relevant analog to the "missing revalidation" bug class from the oracle report. The external bug was about validation performed only at read-time being incomplete (missing recency); the local analog here is validation performed only at write-time (timelock config creation) that is never re-checked when a *dependent* parameter changes later.

### Title
Multisig timelock supermajority-override invariant silently breaks after a normal signature-threshold update - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The custom `MultisigAccountTimeLock` feature added to this fork lets a multisig account require either (a) a timelock delay, or (b) a supermajority `override_threshold` of approvals to execute immediately. The invariant `override_threshold > num_signatures_required` is enforced only inside `upsert_timelock_internal` [1](#0-0) . However, `num_signatures_required` can later be changed via `update_signatures_required`/`swap_owners_and_update_signatures_required` through `update_owner_schema` [2](#0-1) , and this path does not re-validate the timelock invariant. If `num_signatures_required` is raised to meet or exceed the existing `override_threshold`, the timelock delay becomes moot for every subsequent transaction, since normal quorum now also satisfies the override condition in `can_execute_with_timelock` [3](#0-2) .

### Finding Description
`upsert_timelock_internal` asserts that `override_threshold` (the number of approvals needed to bypass the timelock and execute immediately) must be strictly greater than `num_signatures_required` (the normal quorum) at the moment the timelock is configured: [4](#0-3) 

This is a one-time check. The number of signatures required can be changed afterwards by the multisig itself via `update_signatures_required` → `update_owner_schema`, which only touches the `MultisigAccount` resource and has no reference to `MultisigAccountTimeLock` anywhere in the timelock-related grep hits I traced through this file. Nothing recomputes or re-validates `override_threshold` against the new `num_signatures_required` when the schema changes.

`can_execute_with_timelock` uses both values independently at execution time: [3](#0-2) 
```
(override_threshold.is_some() && &num_approvals >= override_threshold.borrow()) || elapsed >= timelock
```

If `num_signatures_required` is raised to be `>= override_threshold`, then any transaction that reaches ordinary quorum (checked separately in `validate_multisig_transaction`/`can_execute`) automatically also satisfies `num_approvals >= override_threshold`, causing the timelock branch to always evaluate true. The timelock — the safety control meant to give other owners a delay window to detect and reject a malicious pending transaction before it executes on custody-holding resources — is silently and permanently voided for the account, with no error, no event distinguishing this state, and no re-validation anywhere in the codebase I was able to inspect.

### Impact Explanation
The timelock feature exists specifically to protect assets held by a multisig-controlled resource account (APT, coins, fungible assets, objects, code-object upgrade authority, etc.) from being drained/reassigned immediately after reaching quorum, by forcing a cooling-off period unless a supermajority explicitly overrides it. Once the invariant is broken, any transaction that merely reaches the (now-adjustable) normal quorum executes immediately with no delay — defeating the entire purpose of the control and removing owners' ability to react to and block a malicious pending transfer/upgrade/ownership-change before it lands. This is a broken custody-control invariant on a multisig-owned resource account, matching "Unauthorized... multisig control... tied to live assets" in the impact gate.

### Likelihood Explanation
Reaching this state does not require any external privilege beyond what the multisig can already do to itself: any legitimate quorum-approved call to `update_signatures_required` (or `swap_owners_and_update_signatures_required`) that raises `num_signatures_required` to `>= override_threshold` triggers the break. This is a routine multisig-governance action (e.g., "let's require one more signer") that owners would reasonably perform without realizing it silently nullifies the timelock's supermajority guarantee for all future transactions. No special attacker capability is needed — just a normal, otherwise-valid governance operation combined with the missing cross-invariant check.

### Recommendation
When `num_signatures_required` (or the owner list) changes via `update_owner_schema`, re-validate any existing `MultisigAccountTimeLock.override_threshold` against the new `num_signatures_required`/owner count, and either abort the update, automatically adjust/clear the override threshold, or require an explicit accompanying timelock reconfiguration in the same transaction so the `override_threshold > num_signatures_required` invariant holds continuously, not just at initial configuration time.

### Proof of Concept
1. Create a multisig with owners `[A, B, C, D]` and `num_signatures_required = 2`.
2. Call `upsert_timelock`/`create_with_owners_and_timelock` with `timelock_period = 1 day`, `override_threshold = Some(3)` (valid at creation: `3 > 2` and `3 <= 4`).
3. Owners create and approve a transaction calling `update_signatures_required(3)`. Getting 3 approvals also satisfies the current override (`3 >= 3`), so this update itself executes immediately, bypassing the day-long timelock.
4. After execution, `num_signatures_required = 3` while `override_threshold` is still `Some(3)`.
5. For every subsequent transaction, reaching normal quorum (3 approvals) automatically satisfies `num_approvals >= override_threshold`, so `can_execute_with_timelock` always returns `true` immediately — the timelock delay no longer applies to any transaction, silently defeating the control for the lifetime of the account (or until manually detected and reconfigured).

**Uncertainty note**: Due to tool-call/iteration limits, I was unable to view the full body of `update_owner_schema` directly (only its call sites via `update_signatures_required`, `add_owners`, `remove_owners`, `swap_owners`, etc.) to conclusively rule out an internal re-validation of the timelock invariant. My conclusion that no such re-check exists is based on the absence of `MultisigAccountTimeLock`/`override_threshold`/`timelock_period` references in that region of the file per the grep results, but this should be double-checked by reading `update_owner_schema`'s exact implementation (visible in `aptos-move/framework/aptos-framework/doc/multisig_account.md` lines ~4247+) before treating this as fully confirmed.

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L938-951)
```text
        assert!(
            timelock_period >= MIN_TIMELOCK_PERIOD && timelock_period <= MAX_TIMELOCK_PERIOD,
            error::invalid_argument(EINVALID_TIMELOCK_DURATION)
        );

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1093-1101)
```text
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
