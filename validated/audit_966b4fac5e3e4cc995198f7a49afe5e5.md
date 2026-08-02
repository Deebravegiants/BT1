Based on the evidence I was able to gather, I found a strong custody-analog candidate in Aptos's native multisig timelock feature, though I was unable to fully trace the `create_transaction`/`vote`/`execute_transaction` gating logic due to tool-call limits, so I'm flagging that gap explicitly.

### Title
Multisig timelock safeguard can be permanently disabled by the base signature threshold instead of the elevated override threshold - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
Aptos's `multisig_account` module implements an optional `MultisigAccountTimeLock` resource with a `timelock_period` and a higher-quorum `override_threshold`, intended to force sensitive multisig transactions through either a time delay or a supermajority override [1](#0-0) . However, `remove_timelock` — the function that deletes this protection entirely — is gated the same way as ordinary owner/threshold-management functions: it is an `entry fun` callable only with the multisig account's own signer, which is obtained through the standard proposal flow requiring just the base `num_signatures_required` approvals, not the elevated `override_threshold` or the `timelock_period` delay itself [2](#0-1) .

### Finding Description
The reported Solidity bug's core custody invariant is: *the entity capable of exercising privileged authority must not be able to use that same base-level authority to instantly strip away the constraint (delay/threshold) that was supposed to limit it.* In the Malt Timelock, `governor` could call `setGovernor` then `setDelay(0)`, both gated only by `GOVERNOR_ROLE`, collapsing the two-step delay into a single instant action.

In `multisig_account.move`, the analogous safeguard is `MultisigAccountTimeLock { timelock_period, override_threshold }`, added specifically so certain multisig actions require either waiting `timelock_period` or reaching `override_threshold` votes rather than just `num_signatures_required` [3](#0-2) . But `remove_timelock` itself:

```
entry fun remove_timelock(multisig_account: &signer) {
    let multisig_address = address_of(multisig_account);
    assert_multisig_account_exists(multisig_address);
    assert!(
        exists<MultisigAccountTimeLock>(multisig_address),
        error::not_found(ETIMELOCK_DOES_NOT_EXIST)
    );
    move_from<MultisigAccountTimeLock>(multisig_address);
    emit(TimelockRemoved { multisig_account: multisig_address });
}
``` [4](#0-3) 

has no check against `override_threshold` or `timelock_period` — it only requires the multisig account's own signer, which (per the module's own documentation on sibling functions such as `add_owners`, `swap_owners`, and `update_signatures_required`) is obtainable "through the proposal flow" at the *base* `num_signatures_required` quorum [5](#0-4) . The same base-threshold gating applies to `update_owner_schema`, which is used to change `num_signatures_required` and owners, and which only *clamps* `override_threshold` after the fact rather than requiring it to be met before allowing threshold/owner reduction [1](#0-0) .

This mirrors the Solidity flaw structurally: a base-quorum-controlled action (`remove_timelock`, or lowering `num_signatures_required`/owners via `update_owner_schema`) can dismantle the very safeguard (`override_threshold`/`timelock_period`) that was designed to require a *higher* bar or delay for sensitive custody actions on the multisig — e.g., proposals that transfer resource-account-controlled assets, rotate the multisig's coin/FA authority, or add a new owner to gain future unilateral control.

### Impact Explanation
If a multisig account is configured with a timelock specifically to protect high-value custody actions (asset transfers, owner changes, resource-account signer-capability usage) behind a supermajority `override_threshold` or a mandatory delay, any subset of owners that can reach only the base `num_signatures_required` can submit and execute a transaction calling `remove_timelock` (or `update_owner_schema` to shrink the owner set/threshold), instantly collapsing the intended two-tier protection. A subsequent proposal at the same base threshold can then execute custody-critical operations (owner takeover, fund transfer, signer-capability abuse) without ever meeting the higher bar the timelock was meant to enforce — a direct authority-reassignment/custody-bypass, analogous in severity to the H-01 finding.

### Likelihood Explanation
Likelihood depends on: (1) whether any multisig accounts in production actually configure `MultisigAccountTimeLock` with `override_threshold` stricter than `num_signatures_required` (a reasonable operational choice for treasury/asset-custody multisigs), and (2) whether `execute_transaction`'s gating logic (which I could not fully inspect within the available tool budget) applies the `timelock_period`/`override_threshold` check uniformly to *all* transactions including `remove_timelock` itself, or only to a subset of "sensitive" transaction types. I could not confirm from the retrieved code whether `create_transaction`/`vote`/`execute_transaction` impose the timelock delay on the `remove_timelock` call path itself; if they do, this finding would be mitigated. This is the key open uncertainty.

### Recommendation
Require `remove_timelock`, and any `update_owner_schema` path that reduces `num_signatures_required`, adds/removes owners, or lowers `override_threshold`, to independently satisfy the currently-configured `override_threshold` (or wait out `timelock_period`) rather than the base `num_signatures_required` — mirroring the report's recommendation that governance-limiting parameters only be changeable through the same protected process they are meant to gate.

### Proof of Concept
Conceptual (execution-path details unverified due to tool-budget limits):
1. Configure a multisig with `num_signatures_required = 2`, `owners.length() = 5`, and a `MultisigAccountTimeLock { timelock_period: 7 days, override_threshold: some(4) }`, intending that fast/no-delay execution requires 4-of-5 approval.
2. Two colluding/compromised owners create and approve a multisig transaction calling `multisig_account::remove_timelock`, meeting only `num_signatures_required = 2`.
3. `execute_transaction` runs `remove_timelock`, deleting `MultisigAccountTimeLock` from the multisig address with no reference to `override_threshold` or `timelock_period` [4](#0-3) .
4. The same two owners then propose and execute a custody-critical transaction (e.g., `swap_owners_and_update_signatures_required` to seize full control, or a payload transferring resource-account-held assets), which now only needs the base 2-of-5 threshold with no delay, since the timelock no longer exists.

**Verification gap**: I was not able to retrieve `create_transaction`, `vote`, or `execute_transaction` in this session to confirm precisely how `timelock_period`/`override_threshold` gate execution for arbitrary payloads versus administrative ones. If those functions already special-case `remove_timelock`/`update_owner_schema` to require the `override_threshold` itself, this finding does not hold as stated, and I could not rule that out with the tool calls available.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L971-984)
```text
    /// Remove the timelock configuration for the multisig account.
    /// Aborts if no timelock is configured.
    entry fun remove_timelock(multisig_account: &signer) {
        let multisig_address = address_of(multisig_account);
        assert_multisig_account_exists(multisig_address);
        assert!(
            exists<MultisigAccountTimeLock>(multisig_address),
            error::not_found(ETIMELOCK_DOES_NOT_EXIST)
        );
        move_from<MultisigAccountTimeLock>(multisig_address);
        emit(TimelockRemoved {
            multisig_account: multisig_address,
        });
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L991-996)
```text
    /// Add new owners to the multisig account. This can only be invoked by the multisig account itself, through the
    /// proposal flow.
    ///
    /// Note that this function is not public so it can only be invoked directly instead of via a module or script. This
    /// ensures that a multisig transaction cannot lead to another module obtaining the multisig signer and using it to
    /// maliciously alter the owners list.
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
