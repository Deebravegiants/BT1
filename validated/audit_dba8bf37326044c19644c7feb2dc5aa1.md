### Title
Silent timelock-bypass invariant break in multisig timelock override threshold - ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
The Aptos `multisig_account` module's optional timelock feature enforces the invariant `override_threshold > num_signatures_required` only at the moment `upsert_timelock` is called. That invariant is never re-validated when `num_signatures_required` is subsequently changed by `update_signatures_required` / `swap_owners_and_update_signatures_required` / `add_owners_and_update_signatures_required`, all of which go through `update_owner_schema` without touching or checking `MultisigAccountTimeLock`.

### Finding Description
`upsert_timelock_internal` validates the override threshold relative to the *current* `num_signatures_required` at set time: [1](#0-0) 

The runtime timelock gate is: bypass the delay if `num_approvals >= override_threshold`, otherwise wait `timelock_period`: [2](#0-1) 

Final gating logic combines ordinary quorum with the timelock check: [3](#0-2) 

`num_signatures_required` can later be raised independently via `update_signatures_required` (and related owner/threshold-update entry points), which route to `update_owner_schema` and never reference `MultisigAccountTimeLock` or re-check the override invariant: [4](#0-3) 

If `num_signatures_required` is raised to a value `>= override_threshold` (a value that was valid when the timelock was configured but is not re-validated later), the previously configured `override_threshold` becomes `<= num_signatures_required`. From then on, `num_approvals >= num_signatures_required` (required by ordinary quorum in `can_be_executed`/`can_execute`) automatically implies `num_approvals >= override_threshold`, so `can_execute_with_timelock` is always satisfied instantly on reaching plain quorum. The timelock delay — the entire security control the feature exists to provide — is silently and permanently nullified for that multisig account without `TimelockRemoved`/`TimelockUpdated` being emitted and without any warning, even though `MultisigAccountTimeLock` still exists on-chain and view functions (`timelock_period`, `timelock_override_threshold`) will report the feature as "configured."

### Impact Explanation
Multisig timelocks are meant to give owners/monitoring systems a window to detect and react to a malicious or compromised-quorum transaction (e.g., draining a resource-account-held treasury, rotating owners, or granting upgrade authority) before it executes. Because the override-vs-quorum invariant is not maintained across ordinary, expected owner administrative actions (raising `num_signatures_required`), the delay protection can be silently disabled while every on-chain indicator (`MultisigAccountTimeLock` existence, `timelock_period`, `override_threshold`) still shows the timelock as active and unmodified. This is a custody-relevant regression: it defeats a defense-in-depth control protecting multisig-controlled assets (APT, fungible assets, resource-account/code-object authority held by the multisig) without any explicit action or audit trail pointing at the timelock itself.

### Likelihood Explanation
This does not require any attacker privilege beyond what is already needed to raise `num_signatures_required` (a routine, legitimate multisig governance action reachable by any multisig meeting its own quorum, e.g., a security "hardening" step of increasing required signers). It requires no external exploit, malformed input, or race condition — simply configuring a timelock with an override threshold and later raising the signature requirement to or above that threshold, both of which are supported, documented operations. The resulting bypass state persists silently (no event, no distinguishing on-chain state) which increases the chance operators are unaware the protection has lapsed.

### Recommendation
Re-validate (or automatically adjust) `override_threshold` whenever `num_signatures_required` changes: if `MultisigAccountTimeLock` exists, `update_owner_schema`/`update_signatures_required` should either (a) abort if the new `num_signatures_required` would make `override_threshold <= num_signatures_required`, or (b) clear/require an explicit re-confirmation of the timelock configuration, and emit a `TimelockUpdated`/`TimelockRemoved` event so the change is auditable.

### Proof of Concept
1. Create a multisig account with `num_signatures_required = 3` (of 5 owners).
2. Call `upsert_timelock(multisig_signer, timelock_period=86400, override_threshold=Some(4))` — valid because `4 > 3`.
3. Owners propose and pass (with the current 3-of-5 quorum, subject to the still-effective timelock/override since 3 < 4) a transaction calling `update_signatures_required(multisig_signer, 4)`.
4. After this transaction executes, `num_signatures_required == 4` while `override_threshold` is still `Some(4)`.
5. Any subsequent transaction that reaches ordinary quorum (`num_approvals >= 4`) now also satisfies `num_approvals >= override_threshold (4)` in `can_execute_with_timelock`, so it executes immediately with `elapsed` never being checked — the 24-hour timelock is bypassed for all future transactions, even though `timelock_period`/`override_threshold` view functions still report the timelock as configured at 86400s/4.

**Note on confidence**: I traced this through the on-chain Move source and confirmed no cross-check exists between `update_owner_schema`/`update_signatures_required` and `MultisigAccountTimeLock`. I was not able to execute the Move unit tests in this environment to confirm runtime behavior end-to-end, so this should be validated with an actual Move test (e.g., extending `test_upsert_timelock`) before treating it as fully confirmed.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L473-493)
```text
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
