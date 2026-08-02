I'll investigate this properly by examining the relevant custody-related code paths in the Aptos framework rather than assuming a vulnerability exists.Found a genuine custody invariant break in `multisig_account.move`'s timelock feature.

### Title
Timelock override_threshold is never revalidated after owner/signature-threshold changes, allowing quorum bypass or account lockout - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`upsert_timelock_internal` validates `override_threshold` against the multisig account's *current* `num_signatures_required` and `owners.length()` at the time the timelock is set [1](#0-0) . However, `override_threshold` is stored once in `MultisigAccountTimeLock` and is never re-checked or updated when the owners list or `num_signatures_required` changes via `update_owner_schema` (used by `add_owners`, `remove_owners`, `swap_owners`, `update_signatures_required`, etc.) [2](#0-1) . This is directly analogous to the `diffMaxMinRuntime` bug: a derived/cached value that governs a critical calculation is set once but never kept in sync with the state it depends on.

### Finding Description
The `MultisigAccountTimeLock` resource stores `override_threshold: Option<u64>`, which is meant to represent "the number of approvals required to bypass the timelock" and must satisfy `num_signatures_required < override_threshold <= owners.length()` at all times [3](#0-2) . This invariant is enforced only inside `upsert_timelock_internal`, at set time [4](#0-3) .

`can_execute_with_timelock` later uses this stale `override_threshold` to decide whether a transaction can bypass the timelock entirely: `(override_threshold.is_some() && &num_approvals >= override_threshold.borrow()) || elapsed >= timelock` [5](#0-4) .

Because owners/`num_signatures_required` can be changed afterward via `update_owner_schema` (reachable through `remove_owners`, `swap_owners`, `update_signatures_required`, all of which are only guarded by requiring the call to originate from the multisig account itself, not by any re-validation of `MultisigAccountTimeLock`) [6](#0-5) , the stored `override_threshold` can drift out of its intended relationship with the live owner set:
- If owners are removed and `override_threshold` was previously ≤ old owner count but now exceeds the new (smaller) owner count, the override path becomes permanently unreachable — not a security break by itself, just dead config.
- More seriously, if `num_signatures_required` is *increased* to a value ≥ the previously-set `override_threshold` (e.g., threshold set to 3 when `num_signatures_required` was 2 and owners = 4; later `update_signatures_required` raises `num_signatures_required` to 3), the invariant "override_threshold > num_signatures_required" silently breaks. The override threshold no longer represents an elevated quorum above the normal execution quorum — it can become equal to or below the standard quorum needed to execute anyway, making the "requires extra approvals to bypass timelock" protection meaningless without ever being re-validated or rejected.

There is no `assert!` anywhere outside `upsert_timelock_internal` that revalidates `MultisigAccountTimeLock.override_threshold` against the current `MultisigAccount.num_signatures_required` / `owners.length()` after they change.

### Impact Explanation
This weakens (but does not outright disable) a security control intentionally added on top of multisig custody: the timelock is meant to slow down high-value or sensitive multisig executions unless a supermajority (`override_threshold`) agrees to bypass it. If `override_threshold` silently collapses to equal or below the normal quorum after a legitimate owner-schema change, any transaction that meets the *normal* signature threshold also satisfies the (no-longer-elevated) override condition, and the timelock delay protecting custody of multisig-held assets (APT, resource-account signer capabilities, code-object upgrade authority, etc.) can be bypassed with only the standard quorum — defeating the intended additional custody safeguard without any owner ever explicitly re-configuring or being warned about the timelock.

This is a real but comparatively narrow impact: it degrades an optional supplementary control (timelock override) rather than granting unprivileged takeover of ownership/mint/freeze/burn directly. I cannot verify from the code alone whether the timelock is depended upon anywhere else in the framework as a hard security boundary for asset custody (it is a self-contained, opt-in module-level feature); no other module reads `MultisigAccountTimeLock`. I'm rating this Medium rather than the mandatory High/Critical bar requested by the task's gate, and given the custody-impact gate requires high/critical mainnet-relevant asset-control impact, this analog does not clearly meet that bar.

### Likelihood Explanation
Requires a multisig account owner set to (a) enable a timelock with an override threshold, and (b) later legitimately change `num_signatures_required` or remove owners through the normal multisig proposal flow — both of which are expected, routine multisig-administration actions. No external attacker input or unprivileged caller is needed; the "attacker" is simply the multisig's own governance drifting into an inconsistent state, which is a configuration/logic bug rather than an exploit primitive controllable by an unprivileged party.

### Recommendation
Re-validate (or automatically clamp/clear) `MultisigAccountTimeLock.override_threshold` whenever `num_signatures_required` or `owners` change in `update_owner_schema`, mirroring the checks already performed in `upsert_timelock_internal`. If the invariant would be violated by an owner-schema change, either abort the schema-change transaction or explicitly disable/reset the timelock override and emit an event making the behavior change visible to owners.

### Proof of Concept
Conceptual sequence (not independently executed against a live node):
1. Create a multisig account with 4 owners, `num_signatures_required = 2`.
2. Call `upsert_timelock(timelock_period, override_threshold = Some(3))` — valid at this point since `3 > 2` and `3 <= 4` [4](#0-3) .
3. Later call `update_signatures_required(new_num_signatures_required = 3)` via the normal multisig proposal flow — this only calls `update_owner_schema`, which does not touch or re-check `MultisigAccountTimeLock` [7](#0-6) .
4. Now `num_signatures_required == override_threshold == 3`. A transaction with exactly 3 approvals (the new normal quorum) satisfies `num_approvals >= override_threshold` in `can_execute_with_timelock`, bypassing the timelock delay that owners intended to require a genuinely elevated quorum for [8](#0-7) .

I was not able to fully verify whether the timelock feature is exercised in downstream consumers/tests that might mitigate this in practice (e.g., off-chain tooling warnings) — a background Devin session with full repo/test access would be needed to confirm real-world exploitability and whether Move Prover specs already flag this gap (`multisig_account.spec.move` was only partially reviewed).

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L171-177)
```text
        V1 {
            /// The time lock period in seconds after the creation of the multisig transaction.
            timelock_period: u64,
            /// The number of approvals required to bypass the timelock and execute immediately.
            /// Must be greater than the number of signatures required normally and less than or equal to the number of owners.
            override_threshold: Option<u64>,
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L991-1101)
```text
    /// Add new owners to the multisig account. This can only be invoked by the multisig account itself, through the
    /// proposal flow.
    ///
    /// Note that this function is not public so it can only be invoked directly instead of via a module or script. This
    /// ensures that a multisig transaction cannot lead to another module obtaining the multisig signer and using it to
    /// maliciously alter the owners list.
    entry fun add_owners(
        multisig_account: &signer, new_owners: vector<address>) {
        update_owner_schema(
            address_of(multisig_account),
            new_owners,
            vector[],
            option::none()
        );
    }

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

    /// Similar to remove_owners, but only allow removing one owner.
    entry fun remove_owner(
        multisig_account: &signer, owner_to_remove: address) {
        remove_owners(multisig_account, vector[owner_to_remove]);
    }

    /// Remove owners from the multisig account. This can only be invoked by the multisig account itself, through the
    /// proposal flow.
    ///
    /// This function skips any owners who are not in the multisig account's list of owners.
    /// Note that this function is not public so it can only be invoked directly instead of via a module or script. This
    /// ensures that a multisig transaction cannot lead to another module obtaining the multisig signer and using it to
    /// maliciously alter the owners list.
    entry fun remove_owners(
        multisig_account: &signer, owners_to_remove: vector<address>) {
        update_owner_schema(
            address_of(multisig_account),
            vector[],
            owners_to_remove,
            option::none()
        );
    }

    /// Swap an owner in for an old one, without changing required signatures.
    entry fun swap_owner(
        multisig_account: &signer,
        to_swap_in: address,
        to_swap_out: address
    ) {
        update_owner_schema(
            address_of(multisig_account),
            vector[to_swap_in],
            vector[to_swap_out],
            option::none()
        );
    }

    /// Swap owners in and out, without changing required signatures.
    entry fun swap_owners(
        multisig_account: &signer,
        to_swap_in: vector<address>,
        to_swap_out: vector<address>
    ) {
        update_owner_schema(
            address_of(multisig_account),
            to_swap_in,
            to_swap_out,
            option::none()
        );
    }

    /// Swap owners in and out, updating number of required signatures.
    entry fun swap_owners_and_update_signatures_required(
        multisig_account: &signer,
        new_owners: vector<address>,
        owners_to_remove: vector<address>,
        new_num_signatures_required: u64
    ) {
        update_owner_schema(
            address_of(multisig_account),
            new_owners,
            owners_to_remove,
            option::some(new_num_signatures_required)
        );
    }

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
