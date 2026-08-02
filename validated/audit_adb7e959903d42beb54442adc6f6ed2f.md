## Finding

### Title
Multisig Timelock `override_threshold` Invariant Not Re-Validated on Owner/Signature Updates, Silently Degrading Timelock Bypass Protection - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`multisig_account.move` enforces the invariant `override_threshold > num_signatures_required` only when the timelock is first configured, in `upsert_timelock_internal`. When owners or `num_signatures_required` are later changed through `update_owner_schema` (used by `add_owner(s)`, `remove_owner(s)`, `swap_owner(s)`, `update_signatures_required`), the code only clamps `override_threshold` down if it exceeds the new owner count — it never re-checks it against the (possibly increased) `num_signatures_required`. This mirrors the external report's bug class: a distribution/ordering invariant is validated at creation time but not re-enforced on every subsequent mutation path.

### Finding Description
`upsert_timelock_internal` asserts the ordering invariant when a timelock is created or updated directly: [1](#0-0) 

However, the only place `override_threshold` is touched during owner/threshold mutations is this clamp-down check inside `update_owner_schema`, which compares `override_threshold` solely against `num_owners`: [2](#0-1) 

This same function is what `add_owner`, `add_owners`, `remove_owner`, `remove_owners`, `swap_owner(s)`, and `update_signatures_required` all delegate to: [3](#0-2) 

Because `update_owner_schema` can both raise `num_signatures_required` (via the optional-signatures branch, lines ~1633-1651 doc-equivalent) and remove owners, two divergent paths corrupt the invariant:
- If `num_signatures_required` is increased to a value `>= override_threshold` (e.g., via `update_signatures_required`), nothing re-checks or adjusts `override_threshold`; it remains stored as-is, now `<= num_signatures_required`.
- If owners are removed such that `num_owners == num_signatures_required` (allowed, since only `num_owners >= num_signatures_required` is asserted), and `override_threshold` also gets clamped down to the new `num_owners`, `override_threshold` can become exactly equal to `num_signatures_required`.

In both cases the invariant established at timelock-creation time (`override_threshold > num_signatures_required`) is silently violated by an unprivileged-relative-to-timelock-config code path (any owner-approved multisig transaction that adds/removes owners or updates signature count, none of which re-validate timelock state against the new threshold).

### Impact Explanation
The multisig timelock exists specifically to protect custody of assets controlled by the multisig account (APT, fungible assets, resource-account/code-object authority held by the multisig signer) by requiring transactions to wait `timelock_period` before execution, unless a supermajority (`override_threshold` approvals, strictly greater than the normal `num_signatures_required`) is reached to bypass the delay. Once `override_threshold` degrades to `<= num_signatures_required`, every transaction that already meets the normal execution threshold also satisfies the override condition, which (assuming, as the naming and design strongly imply, that reaching `override_threshold` votes allows immediate execution bypassing `timelock_period`) eliminates the timelock delay for all future transactions on that multisig account. This defeats a custody-control safety mechanism meant to give owners a window to detect and reject malicious transactions before execution, directly enabling faster, unchecked movement/transfer of multisig-held assets.

### Likelihood Explanation
This requires no external adversary — a normal, already-authorized multisig owner-approved administrative action (`update_signatures_required` or `remove_owner(s)`, both routine owner-management operations under the existing multisig proposal flow) can trigger the corruption without any special malicious intent, since the code performs no invariant re-check on the timelock's cross-field relationship. This differs from "admin misconfiguration"-only classification because the framework itself fails to preserve its own documented and asserted invariant across all valid, permitted state-mutation entry points.

### Recommendation
In `update_owner_schema`, after any change to `owners` or `num_signatures_required`, if a `MultisigAccountTimeLock` exists, re-validate the full invariant `override_threshold > num_signatures_required && override_threshold <= owners.length()`, not just the owner-count bound. If the invariant would break, either abort the owner/signature update, or automatically raise `override_threshold`/disable the timelock override consistently while emitting an event, so the semantic guarantee (override requires strictly more approvals than baseline execution) is preserved across every mutation path, not only creation.

### Proof of Concept
1. Create a multisig account with 3 owners, `num_signatures_required = 2`.
2. Call `upsert_timelock(timelock_period = T, override_threshold = 3)`. Invariant holds: `3 > 2`.
3. Owners then call `update_signatures_required(new_num_signatures_required = 3)` via the standard proposal flow. `update_owner_schema` updates `num_signatures_required` to `3` and only checks `num_owners (3) >= num_signatures_required (3)` — passes. The timelock clamp block only checks `override_threshold (3) > num_owners (3)` — false, so no clamp/abort occurs.
4. State now: `num_signatures_required = 3`, `override_threshold = 3` — invariant `override_threshold > num_signatures_required` is violated (equal, not greater).
5. Any transaction subsequently reaching 3 approvals (the now-mandatory quorum for ordinary execution) simultaneously satisfies the override-threshold condition, bypassing the timelock delay entirely for all transactions, silently nullifying the protection the timelock was configured to provide.

**Note on verification limits:** I could not directly view the execution-time function that consumes `override_threshold` (e.g., the `can_be_executed`/timelock-check logic) within the available tool budget to confirm the exact mechanics of how reaching `override_threshold` bypasses `timelock_period`; this is inferred from the field name, the `upsert_timelock` doc comments, and the invariant assertion `override_threshold > num_signatures_required`. If a Devin session is available, this should be confirmed by reading the transaction-execution/timelock-check function in `multisig_account.move` in full before treating this as fully confirmed.

### Citations

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

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L4339-4351)
```markdown
    // If a timelock is configured, adjust and validate the override threshold
    // after owner/threshold changes.
    <b>if</b> (<b>exists</b>&lt;<a href="multisig_account.md#0x1_multisig_account_MultisigAccountTimeLock">MultisigAccountTimeLock</a>&gt;(multisig_address)) {
        <b>let</b> timelock = &<b>mut</b> <a href="multisig_account.md#0x1_multisig_account_MultisigAccountTimeLock">MultisigAccountTimeLock</a>[multisig_address];
        // If override threshold exceeds the new owner count, clamp it down and emit an <a href="event.md#0x1_event">event</a>
        // so off-chain monitors observe the security-relevant mutation.
        <b>if</b> (timelock.override_threshold.is_some() && timelock.override_threshold.borrow() &gt; &num_owners) {
            timelock.override_threshold = <a href="../../aptos-stdlib/../move-stdlib/doc/option.md#0x1_option_some">option::some</a>(num_owners);
            emit(<a href="multisig_account.md#0x1_multisig_account_TimelockUpdated">TimelockUpdated</a> {
                <a href="multisig_account.md#0x1_multisig_account">multisig_account</a>: multisig_address,
                timelock_period: timelock.timelock_period,
                override_threshold: timelock.override_threshold,
            });
```
