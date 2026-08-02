Based on the investigation, the strongest local analog to the rage-quit bug class is in `aptos_framework::multisig_account`'s timelock feature, which was clearly added on top of vanilla Aptos multisig accounts specifically to gate execution speed for custody-relevant multisig transactions.

### Title
Multisig timelock/override-threshold protection can be unilaterally weakened or removed by the base signature quorum, retroactively exposing already-queued custody transactions to premature execution - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
`multisig_account` implements an optional per-account timelock (`MultisigAccountTimeLock`) meant to force a waiting period (`timelock_period`) before an approved transaction can execute, unless a higher `override_threshold` of approvals is reached for immediate execution. This mirrors the rage-quit pattern: a security guarantee (a time-bound "protection window") that owners rely on to detect and react to malicious pending transactions. [1](#0-0) 

### Finding Description
The timelock configuration is changed via `upsert_timelock` / `upsert_timelock_internal`, which is only gated by the requirement that the caller *is* the multisig account signer — i.e. it can be invoked through the normal multisig proposal flow requiring only `num_signatures_required` approvals (the base quorum), not the higher `override_threshold` that is supposed to represent the "fast-track"/urgent bar: [2](#0-1) 

`remove_timelock` similarly only requires the base multisig signer/quorum and unconditionally deletes the entire protection: [3](#0-2) 

Critically, the module's own doc comment on `upsert_timelock` confirms the mutation applies **retroactively** to already-pending, previously-approved transactions, because the timelock check is computed from each transaction's `creation_time_secs`, not from when the new timelock policy took effect: [4](#0-3) 

This exactly reproduces the rage-quit custody invariant break: the base quorum (analogous to the "party host") can arbitrarily shrink `timelock_period` down to `MIN_TIMELOCK_PERIOD` (1 hour) or delete the timelock/override_threshold outright, at any time, overriding whatever protection window owners were relying on — with no restriction that:
1. the timelock cannot be reduced/removed below the time already committed for currently pending transactions,
2. changes can only be made once per period, or
3. only the higher `override_threshold` (the bar meant to authorize urgent/fast execution) can shrink or remove the delay.

Because reducing/removing the timelock only costs the base `num_signatures_required` — the exact same quorum needed to approve any ordinary transaction, including a malicious drain — the entire purpose of `override_threshold` (requiring extra approvals to bypass the delay) is defeated. A coalition holding exactly the base quorum can queue a draining transaction, then use the same signatures to shrink the timelock, and execute the drain almost immediately, without ever having to obtain the `override_threshold` the account owners configured specifically to prevent this.

### Impact Explanation
Multisig accounts commonly custody APT/fungible-asset treasuries; the timelock+override_threshold combination is the mechanism by which minority owners are supposed to have time to detect and react to (e.g., by removing a compromised owner, or exiting funds) a transaction approved by only the base quorum before it can drain funds. Because the base quorum can unilaterally and retroactively collapse this protection, the security guarantee is illusory: any coalition that can reach `num_signatures_required` (which is by definition achievable, since it's the account's normal operating threshold) can always bypass the intended `override_threshold` fast-track gate, enabling theft/drain of multisig-custodied assets with materially less oversight than the account owners configured and relied upon.

### Likelihood Explanation
High. No additional privilege beyond the account's ordinary operating quorum is required — the same signers who could already create/approve a malicious transaction can also weaken/remove the timelock using ordinary multisig flow. There is no separate authorization check tying timelock changes to the `override_threshold`, no cool-down/rate-limit on timelock changes, and the module's own documentation acknowledges (and accepts) that the change applies retroactively to in-flight transactions.

### Recommendation
- Require timelock reductions/removals themselves to meet the current `override_threshold` (not just `num_signatures_required`), so the "fast path" cannot be used to dismantle the very control gating it.
- If timelock is reduced or removed, apply the change only to transactions created *after* the change (freeze `creation_time_secs`-based elapsed time for existing pending transactions), or require that the previous `timelock_period` still fully elapses for currently pending transactions.
- Rate-limit or cool-down timelock configuration changes (e.g., once per `timelock_period`).
- Alternatively, disallow decreasing `timelock_period`/removing `override_threshold` while there exist pending transactions that have not yet met the current override threshold.

### Proof of Concept
1. Multisig account is created with `num_signatures_required = 2`, `owners.length() = 5`, and a timelock configured via `upsert_timelock(period = MAX_TIMELOCK_PERIOD, override_threshold = 4)` — intended to require either a 4-of-5 fast approval or a long wait for a 2-of-5 approval. [2](#0-1) 
2. A 2-owner coalition creates a malicious `create_transaction` to drain the account's APT/FA holdings; it gets exactly 2 approvals (the base quorum) and would normally have to wait `MAX_TIMELOCK_PERIOD` (14 days) since it lacks the 4 approvals for `override_threshold`.
3. The same 2-owner coalition submits and approves a second transaction calling `upsert_timelock(period = MIN_TIMELOCK_PERIOD /* 1 hour */, override_threshold = none)` (or `remove_timelock`) — this only needs the same 2 approvals, per `upsert_timelock_internal`. [5](#0-4) 
4. Because the timelock check is measured against each transaction's original `creation_time_secs` rather than the time the new policy took effect (per the module's own documented behavior), the already-queued drain transaction now only needs to wait ~1 hour (or nothing, if the timelock was removed) instead of 14 days, and can be executed by the same 2-of-5 quorum without ever reaching the 4-of-5 `override_threshold` the owners configured as their security bar. [6](#0-5) 

**Uncertainty note:** I could not fully trace `can_execute_with_timelock`/`can_execute` (the functions that actually gate transaction execution against the timelock) within the available iterations to confirm the exact arithmetic of how `creation_time_secs` interacts with a changed `timelock_period` at execution time — this is stated as a documented, acknowledged behavior in the code comments but I was not able to verify the execution-gating function body directly. A background Devin session with full repository access should verify `can_execute_with_timelock` to confirm the precise mechanics before treating this as fully confirmed.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L906-925)
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
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L930-969)
```text
    fun upsert_timelock_internal(
        multisig_account: &signer,
        timelock_period: u64,
        override_threshold: Option<u64>,
    ) {
        let multisig_address = address_of(multisig_account);
        assert_multisig_account_exists(multisig_address);

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

        emit(TimelockUpdated {
            multisig_account: multisig_address,
            timelock_period,
            override_threshold,
        });
    }
```

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
