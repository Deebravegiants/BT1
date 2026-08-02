This is a custom `MultisigAccountTimeLock` feature added on top of `multisig_account.move` — not present in stock Aptos framework. It introduces an `override_threshold` that lets a smaller number of approvals bypass the normal `num_signatures_required` after a timelock period elapses. I found a real custody-relevant defect in `update_owner_schema`, but I could not fully verify the execution-path functions (`can_be_executed`, timelock check logic) within the remaining iterations, so I cannot confirm end-to-end exploitability with full confidence.

### Title
Silent clamping of multisig timelock `override_threshold` in `update_owner_schema` weakens approval requirement without owner consent - ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
`update_owner_schema`, the internal function backing `add_owners`, `remove_owners`, `swap_owner(s)`, and `update_signatures_required`, silently clamps a configured `MultisigAccountTimeLock.override_threshold` down to the new owner count whenever owners are removed and the override threshold exceeds the new count, rather than rejecting the change or requiring an explicit timelock reconfiguration.

### Finding Description
In `update_owner_schema` [1](#0-0) , after adjusting owners and `num_signatures_required`, the code checks the `MultisigAccountTimeLock` resource and clamps `override_threshold` if it now exceeds the owner count: [2](#0-1) 

The timelock/override mechanism is intended to let a *reduced* number of approvals (the "override threshold") execute a transaction once a timelock period has elapsed — a deliberate governance safety valve, presumably requiring the override threshold to always be `> num_signatures_required` per `EINVALID_TIMELOCK_OVERRIDE_THRESHOLD` [3](#0-2) . `remove_owners` is an operation that, once approved as a normal multisig transaction, executes with the multisig account as signer [4](#0-3) . Because the clamp happens automatically inside `update_owner_schema` as a side effect of owner removal, a transaction whose *stated intent* was only "remove owner X" implicitly and silently lowers the override_threshold safety margin (potentially down to a value equal to, or effectively controlling, the reduced owner count) without a dedicated timelock-reconfiguration proposal being voted on by owners. This breaks the custody invariant that changing the multisig's approval/override authority structure requires explicit, transparent owner consent tied to that specific change.

I was not able to fully trace the downstream `can_be_executed`/timelock-execution logic (e.g., whether `override_threshold` can equal `num_signatures_required` after clamping, effectively nullifying the extra security margin the timelock override was meant to enforce, or whether it can reach 0/1 letting a single remaining owner unilaterally execute high-value transactions) within the available iterations. This is the key unresolved uncertainty.

### Impact Explanation
If the clamp can drive `override_threshold` to a value that lets a minority of owners (post-removal) execute previously "hard" k-of-n approved transactions after only a timelock delay, this constitutes unauthorized reduction of multisig control authority over any assets (APT, fungible assets, objects) held by the multisig-owned resource account — a custody-grade impact per the gate (unauthorized takeover of multisig control). However, since I could not confirm the exact bound enforced on `override_threshold` at execution time versus at configuration time, I cannot assert with certainty that this reaches Critical/High severity rather than being properly re-validated elsewhere.

### Likelihood Explanation
Low-to-Medium: it requires the multisig to have configured a `MultisigAccountTimeLock` with an `override_threshold` and then later removing owners via a normal multisig-approved transaction — a plausible, ordinary lifecycle operation (owner rotation) that is not itself flagged as security-sensitive by users, making this an easy scenario to trigger without malicious intent.

### Recommendation
Do not silently clamp `override_threshold` inside `update_owner_schema`. Instead, either (a) abort the owner-removal/threshold-update transaction if it would violate `override_threshold`'s invariant relative to the new owner count, forcing owners to explicitly resolve the timelock configuration first, or (b) require a separate, explicitly-voted timelock reconfiguration transaction whenever owner-count changes affect `override_threshold` validity, emitting a distinct high-visibility event that is reviewed by owners rather than being an implicit side effect.

### Proof of Concept
Conceptual sequence (not fully verified against execution-time checks due to tool-call limits):
1. Multisig account created with owners `[A,B,C,D,E]`, `num_signatures_required = 3`, and a `MultisigAccountTimeLock` configured with `override_threshold = 4` (i.e., 4-of-5 can execute early with timelock elapsed as an extra-safe override, while normal execution requires only 3).
2. Owners approve a routine `remove_owners([D, E])` transaction (3 approvals, meeting normal `num_signatures_required`).
3. `update_owner_schema` executes: owner count drops to 3; since `override_threshold (4) > num_owners (3)`, it clamps `override_threshold` to 3 automatically [5](#0-4) .
4. Now `override_threshold == num_signatures_required == 3`, collapsing the distinction the timelock mechanism was meant to provide, with no dedicated owner vote on this specific consequence — only the `TimelockUpdated` event as an after-the-fact notification.

Because I could not verify within the remaining budget whether downstream execution logic re-validates `override_threshold > num_signatures_required` at execute-time (which would neutralize this issue) or trusts the clamped value as-is, this finding should be treated as requiring further code review of the transaction-execution path (`can_be_executed`, timelock expiry checks) before being treated as fully confirmed.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L105-106)
```text
    /// Timelock override threshold must be greater than num_signatures_required and at most the number of owners.
    const EINVALID_TIMELOCK_OVERRIDE_THRESHOLD: u64 = 22;
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1027-1042)
```text
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
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1586-1596)
```text
    /// Add new owners, remove owners to remove, update signatures required.
    fun update_owner_schema(
        multisig_address: address,
        new_owners: vector<address>,
        owners_to_remove: vector<address>,
        optional_new_num_signatures_required: Option<u64>,
    ) {
        assert_multisig_account_exists(multisig_address);
        let multisig_account_ref_mut =
            borrow_global_mut<MultisigAccount>(multisig_address);
        // Verify no overlap between new owners and owners to remove.
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
