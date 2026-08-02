Based on my research, I found a genuine custody-analog in this repository's `multisig_account.move` module — specifically in a fork-specific enhancement (`MultisigAccountTimeLock`) that is not present in mainline Aptos and mirrors the exact bug class from the report: **a security-relevant parameter is silently recomputed as a side effect of an unrelated update, without re-validating the invariant that was enforced when the parameter was first set.**

### Title
Silent weakening of multisig timelock override threshold on owner removal — ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
The multisig module implements a `MultisigAccountTimeLock` with a `num_signatures_required` (normal k-of-n) and a separate, stricter `override_threshold` that is meant to let a supermajority bypass the timelock delay. `update_owner_schema()` — invoked by `remove_owners`/`swap_owners`/etc. — auto-clamps `override_threshold` down to the new owner count whenever owners are removed, but never re-validates it against `num_signatures_required`, silently collapsing the intended security gap between "normal execution" and "fast/override execution."

### Finding Description
When the module first configures a timelock, it enforces:
`EINVALID_TIMELOCK_OVERRIDE_THRESHOLD: "Timelock override threshold must be greater than num_signatures_required and at most the number of owners."` [1](#0-0) 

However, `update_owner_schema()`, called by `add_owners`, `remove_owners`, `swap_owner(s)`, and `update_signatures_required` [2](#0-1) , contains this clamp logic (shown in the generated doc, which mirrors the source):

```
if (timelock.override_threshold.is_some() && timelock.override_threshold.borrow() > &num_owners) {
    timelock.override_threshold = option::some(num_owners);
    emit(TimelockUpdated { ... });
}
``` [3](#0-2) 

This clamp only checks `override_threshold > num_owners` — it never re-checks `override_threshold > num_signatures_required`, which is the exact invariant asserted at configuration time. Since `num_owners >= num_signatures_required` is the only lower-bound guarantee enforced elsewhere in the same function [4](#0-3) , a sequence of owner removals can drive `num_owners` down until it equals `num_signatures_required`, at which point the clamp sets `override_threshold == num_signatures_required`. This eliminates the security gap the timelock/override design was meant to provide: the same quorum that satisfies normal execution now also satisfies the "override" (bypass-the-delay) path.

This is structurally identical to the report's bug class: `updateStream()`'s topUp/extendTime silently recompute vested/withdrawn amounts as a side effect of an unrelated parameter change, corrupting an accounting invariant instead of treating the change as "start fresh with validated new state." Here, `update_owner_schema()`'s owner-removal path silently recomputes a *different* protected parameter (`override_threshold`) as a side effect, without re-validating the cross-field invariant it depends on.

### Impact Explanation
The `override_threshold` exists specifically so that a stricter quorum is required to execute multisig transactions immediately, bypassing the `timelock_period` delay that gives other owners a chance to react to (and potentially cancel) a pending transaction on a multisig that custodies APT/fungible assets, controls a resource account, or owns other objects. If `override_threshold` collapses to `num_signatures_required` through ordinary owner-management transactions (which only need to meet the *normal* signature bar, not a decision specifically about weakening the timelock), any owner-subset that can reach the normal quorum can also immediately execute high-value or sensitive transactions without waiting out the timelock — silently defeating the protection the timelock feature was built to guarantee to the remaining owners/stakeholders of custodied funds.

### Likelihood Explanation
This requires no external attacker and no privilege escalation beyond what a normal quorum-holding subset of owners already has: any transaction that removes enough owners (a normal, expected multisig operation) will trigger the clamp as a byproduct, with no separate approval or warning that the timelock's security margin has been reduced. This makes it easy to trigger accidentally (e.g., legitimate owner turnover) or to exploit deliberately by a colluding quorum that wants to remove the "extra owners buffer" specifically to enable fast bypass of the timelock for a later transaction.

### Recommendation
When owners are removed and `override_threshold` must be reduced, additionally re-validate `override_threshold > num_signatures_required` (mirroring the invariant enforced at configuration time), and abort or require an explicit, separate re-configuration transaction for the timelock instead of silently auto-adjusting it as a side effect of `update_owner_schema()`.

### Proof of Concept
1. Multisig account created with `num_signatures_required = 3`, 6 owners, and a timelock configured with `override_threshold = 5` (must be `> num_signatures_required` per `EINVALID_TIMELOCK_OVERRIDE_THRESHOLD`).
2. A transaction (approved by the required 3 signatures) calls `remove_owners` to remove 3 owners, leaving `num_owners = 3`.
3. `update_owner_schema()` detects `override_threshold (5) > num_owners (3)` and silently sets `override_threshold = 3`, equal to `num_signatures_required`.
4. Any subsequent transaction that gathers the normal 3 approvals now also satisfies the override path, executing immediately and bypassing the `timelock_period` delay that was supposed to require distinctly more signers.

**Caveat:** I was unable to retrieve the exact source lines of `update_owner_schema()`'s timelock-clamp block and the code that consumes `override_threshold` during execution (e.g., a `can_be_executed`/`validate_multisig_transaction`-style check) within the available tool calls — my confirmation is based on the generated Move doc file, which mirrors the source, plus the constant definitions and function signatures I did retrieve directly from `multisig_account.move`. If the execution-time enforcement of `override_threshold` differs from the standard "supermajority bypasses timelock" pattern implied by the constants and comments, the precise exploit mechanics would need re-verification against the full function body.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L105-106)
```text
    /// Timelock override threshold must be greater than num_signatures_required and at most the number of owners.
    const EINVALID_TIMELOCK_OVERRIDE_THRESHOLD: u64 = 22;
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L986-1042)
```text
    /// Similar to add_owners, but only allow adding one owner.
    entry fun add_owner(multisig_account: &signer, new_owner: address) {
        add_owners(multisig_account, vector[new_owner]);
    }

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
```

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L4332-4337)
```markdown
    // Verify number of owners.
    <b>let</b> num_owners = multisig_account_ref_mut.owners.length();
    <b>assert</b>!(
        num_owners &gt;= multisig_account_ref_mut.num_signatures_required,
        <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error_invalid_state">error::invalid_state</a>(<a href="multisig_account.md#0x1_multisig_account_ENOT_ENOUGH_OWNERS">ENOT_ENOUGH_OWNERS</a>)
    );
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
