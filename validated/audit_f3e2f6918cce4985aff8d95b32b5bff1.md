### Title
Multisig timelock bypass threshold (`override_threshold`) can be silently weakened as a side effect of an owner-removal transaction - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
`multisig_account.move` implements an optional timelock (`MultisigAccountTimeLock`) that delays execution of multisig transactions unless a higher `override_threshold` number of approvals is reached immediately [1](#0-0) . Changing `override_threshold` is normally supposed to require an explicit, separately validated `upsert_timelock`/`upsert_timelock_internal` call, which re-checks that `override_threshold > num_signatures_required` and `override_threshold <= owners.length()` against the account's *current* state at the time of that call [2](#0-1) . However, `update_owner_schema` — the shared function backing `add_owners`, `remove_owners`, `swap_owners`, and `update_signatures_required` — independently mutates `override_threshold` as a side effect whenever it shrinks the owner count below the currently configured `override_threshold`, without going through `upsert_timelock_internal`'s validated path [3](#0-2) .

### Finding Description
This mirrors the Hats `checkAfterExecution()` bug class: a post-mutation invariant check is validated against values that were *themselves* changed within the same operation, rather than against a value snapshotted before the operation began. In Hats, the post-check verified `threshold == f(current_owner_count)`, but `owner_count` could be altered in the same transaction, letting signers legitimize an arbitrary threshold change. Here, the analogous invariant is: "the number of approvals required to bypass the timelock (`override_threshold`) may only be changed via the explicitly validated `upsert_timelock` path."

`update_owner_schema` violates this: when owners are removed (or swapped) such that `num_owners < override_threshold`, the code clamps `override_threshold` down to `num_owners` in the very same call that removed those owners [4](#0-3) , and then only re-validates that the new (already-clamped) `override_threshold` is `> num_signatures_required` [5](#0-4) . There is no check that `override_threshold` (the bar to instantly bypass the timelock) hasn't decreased as a fraction/absolute count of trust compared to what governance originally set.

`update_owner_schema` is only invokable by the multisig account's own signer (i.e., through the standard multisig approval flow, requiring `num_signatures_required` approvals) [6](#0-5) [7](#0-6) . Because this transaction itself is subject to the timelock, an owner-coalition that manages to hit the *current* `override_threshold` once (to instantly execute a plausible-looking "remove inactive/compromised owner" transaction) can, as an unreviewed side effect of that single approval, permanently lower the number of approvals needed to bypass the timelock for all future transactions — including transactions that drain APT/fungible-asset/resource-account funds controlled by the multisig.

### Impact Explanation
The timelock's `override_threshold` is a custody control gating instant execution of transactions from a resource account / multisig-controlled treasury. Silently weakening it (e.g., from "10 of 10 owners" down to "3 of 3 remaining owners") within an ordinary owner-management transaction lets a shrinking coalition of signers gain unreviewed, amplified control to bypass the time-delay safety net on future asset-moving transactions — directly undermining the multisig's ability to protect custody of any APT, fungible assets, or resource-account funds it controls. This is a broken custody invariant (unauthorized elevation of transfer authority) rather than a cosmetic bug.

### Likelihood Explanation
Exploitation only requires a coalition that can already reach the account's *current* `num_signatures_required` (a normal, expected multisig operation) to also include owner removals/swaps in the same `update_owner_schema`-backed transaction (`remove_owners`, `swap_owners`, `swap_owners_and_update_signatures_required`) that shrinks `owners.length()` below the currently configured `override_threshold`. No privileged capability is needed beyond the ordinary quorum, and the clamp logic executes unconditionally whenever this owner-count condition is met, so likelihood is moderate-to-high in any deployment that uses the timelock feature with an override threshold near the owner count.

### Recommendation
Do not implicitly mutate `override_threshold` inside `update_owner_schema`. Instead, either (a) abort the owner-removal/swap transaction if it would make the existing `override_threshold` invalid (i.e., require operators to explicitly call `upsert_timelock` first to lower `override_threshold`), or (b) require that any automatic reduction of `override_threshold` go through the same validated, separately-timelocked `upsert_timelock_internal` path (including its own `TimelockUpdated` audit event flow) rather than being folded into `update_owner_schema`'s single pass.

### Proof of Concept
1. Multisig account `M` has owners `{A,B,C,D,E,F,G,H,I,J}` (10 owners), `num_signatures_required = 6`, and a timelock configured with `override_threshold = 10` (i.e., unanimous approval needed to bypass the timelock) [8](#0-7) .
2. Owners `A..F` (meeting `num_signatures_required = 6`) create and approve a transaction calling `remove_owners(multisig_signer, vector[G,H,I,J])`, removing 4 owners in one call [7](#0-6) .
3. Inside `update_owner_schema`, after removal `num_owners = 6`. Since `override_threshold (10) > num_owners (6)`, the code clamps `override_threshold` down to `6` and emits `TimelockUpdated` as an incidental side effect, with no separate `upsert_timelock` validation flow [4](#0-3) .
4. Now the same 6 colluding owners `A..F` can submit any asset-draining transaction and instantly reach the new `override_threshold = 6`, bypassing the timelock delay that was originally meant to require all 10 original owners' consent — despite never having gone through the account's intended timelock-update governance path.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L906-924)
```text
    /// Upsert the timelock configuration for the multisig account.
    /// timelock_period must be between MIN_TIMELOCK_PERIOD and MAX_TIMELOCK_PERIOD.
    /// override_threshold, if provided, must be > num_signatures_required and <= the number of owners.
    ///
    /// Note on pending transactions: the timelock check measures elapsed time from a transaction's
    /// `creation_time_secs`, not from when the timelock was activated. Because multisig transactions
    /// execute strictly in sequence order, this is only observable for transactions queued *after*
    /// this `upsert_timelock` call but *before* it executes — those transactions may become
    /// executable sooner than `timelock_period` seconds after this call takes effect, because part
    /// of their elapsed time is counted from before the new timelock was live. Transactions queued
    /// after this call has executed receive the full `timelock_period` protection. This residual
    /// window is bounded by the previous timelock period (or by approval time, if there was no
    /// prior timelock) and is considered an acceptable, operator-visible risk.
    entry fun upsert_timelock(multisig_account: &signer, timelock_period: u64, override_threshold: Option<u64>) {
        assert!(
            features::is_multisig_timelock_enabled(),
            error::unavailable(ETIMELOCK_NOT_ENABLED)
        );
        upsert_timelock_internal(multisig_account, timelock_period, override_threshold);
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L943-962)
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

        if (exists<MultisigAccountTimeLock>(multisig_address)) {
            let multisig_account_resource = &mut MultisigAccountTimeLock[multisig_address];
            multisig_account_resource.timelock_period = timelock_period;
            multisig_account_resource.override_threshold = override_threshold;
        } else {
            move_to(multisig_account, MultisigAccountTimeLock::V1 {
                timelock_period,
                override_threshold,
            });
        }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L991-1005)
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1663-1682)
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
        };
```
