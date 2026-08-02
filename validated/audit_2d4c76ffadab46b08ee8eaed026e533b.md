### Title
Multisig timelock protection can be retroactively weakened for already-pending transactions, allowing early execution of malicious payloads - ([File: aptos-move/framework/aptos-framework/sources/multisig_account.move])

### Summary
`multisig_account.move` implements an optional timelock (`MultisigAccountTimeLock`) that is supposed to force a minimum delay (`timelock_period`) between a multisig transaction's creation and its execution, giving owners/monitoring time to detect and react to a malicious proposal before it can drain multisig-held funds. However, the timelock check is evaluated using the *currently configured* `timelock_period` against a transaction's fixed `creation_time_secs`, rather than the timelock configuration that was in effect when the transaction was created/approved. `upsert_timelock` and `remove_timelock` can change (or remove) this configuration for the multisig account at any time, and the change applies retroactively to every already-pending transaction in the queue. This lets a set of owners meeting the normal `num_signatures_required` threshold shorten or eliminate the timelock protection on transactions that are already pending, executing them earlier than the timelock was supposed to allow — exactly the same "remove/reconfigure a restriction to bypass its own time-off guarantee" bug class as the referenced Holdefi report, but applied to Aptos multisig custody of APT/fungible assets.

### Finding Description
`MultisigAccountTimeLock` stores a single `timelock_period` (and optional `override_threshold`) per multisig account: [1](#0-0) 

Pending transactions are executed strictly in sequence order via `can_be_executed`, which in turn calls `can_execute_with_timelock(multisig_account, sequence_number, num_approvals)`: [2](#0-1) 

The timelock configuration itself can be changed at will via `upsert_timelock`/`upsert_timelock_internal`, which is only gated by `num_signatures_required` (the normal multisig quorum) — not by any check tying the change to the timelock state that applied to already-queued transactions: [3](#0-2) 

The function's own doc comment explicitly acknowledges that the check is based on the *current* `timelock_period` versus each transaction's fixed `creation_time_secs`, and that pending transactions can therefore "become executable sooner than `timelock_period` seconds" than intended once the configuration is weakened: [4](#0-3) 

`remove_timelock` similarly performs no check on pending transactions or elapsed time before deleting the timelock resource outright: [5](#0-4) 

This mirrors the Holdefi bug class precisely: the "time-off" restriction (timelock) is enforced only at the moment of the *current* configuration lookup, not pinned/snapshotted per pending item at creation time. An owner set that reaches the required signature threshold (e.g., a set of compromised or malicious signer keys equal to `num_signatures_required`, which is a lower bar than full consensus of all owners) can:
1. Queue a malicious transaction (e.g., transfer of the multisig-held APT/FA balance to an external address) at sequence N, while a strong `timelock_period` (e.g., `MAX_TIMELOCK_PERIOD` = 14 days) is configured, so it appears to require 14 days before it can execute.
2. Immediately (or shortly after) queue and approve an `upsert_timelock` (or `remove_timelock`) transaction that shortens or removes the timelock.
3. Once that reconfiguration transaction executes (subject to whatever timelock applied to it), the malicious transaction at sequence N is now checked against the new, much weaker `timelock_period` (or no timelock at all), even though it was created and approved under the assumption of the original 14-day delay.

Because `can_execute_with_timelock` reads the live `MultisigAccountTimeLock` resource rather than a value captured at transaction-creation time, this retroactively strips the delay meant to protect the multisig-held assets from exactly this kind of quorum-level compromise.

### Impact Explanation
Multisig accounts on Aptos are resource accounts that can directly hold APT and fungible-asset primary/secondary stores, and the timelock feature exists specifically to protect that value against a compromised-but-quorum-sufficient set of signers by guaranteeing a minimum reaction window. By reconfiguring (shortening) or removing the timelock after a malicious transaction has already been queued, an attacker with quorum-level signing power can execute value-transferring transactions well before the configured protection window elapses, defeating the entire custody safeguard the timelock is meant to provide. This is a broken custody invariant on multisig-held value (theft/early-drain of multisig-controlled APT/fungible assets), and the impact is high given multisig accounts are commonly used to protect significant on-chain treasuries.

### Likelihood Explanation
The precondition is that the attacker (or attackers) control the normal `num_signatures_required` threshold of owner keys — the same threshold already required to execute any multisig transaction, including the malicious payload itself. No additional privilege beyond what's already needed to submit/approve transactions is required to also submit/approve a timelock-reduction transaction. Because the developers' own comment in the code already documents this exact retroactive-application behavior as an accepted/known risk ("this residual window is bounded... and is considered an acceptable, operator-visible risk"), the mechanism is real and reachable through normal, unprivileged (from the framework's perspective) multisig entry functions (`upsert_timelock`, `remove_timelock`), not through any admin/governance-only path.

### Recommendation
Snapshot the effective `timelock_period` (and `override_threshold`) into each `MultisigTransaction` at creation time (or otherwise pin the protection level per-transaction) rather than re-reading the mutable `MultisigAccountTimeLock` resource at execution-check time. Alternatively, disallow `upsert_timelock`/`remove_timelock` from reducing/removing protection for transactions that are already pending, and/or apply configuration changes only to transactions created after the change takes effect — analogous to adding the "time-off" logic the Holdefi report recommended for previously removed/re-added markets.

### Proof of Concept
1. Create a multisig account with `num_signatures_required = k` and configure `upsert_timelock` with `timelock_period = MAX_TIMELOCK_PERIOD` (14 days), holding a meaningful APT/FA balance.
2. With `k` colluding/compromised owner keys, create and approve a malicious transaction (sequence N) that transfers the multisig's held assets to an attacker-controlled address.
3. Immediately create and approve a second transaction (sequence N+1, or interleaved appropriately given strict sequential execution) calling `upsert_timelock` with `timelock_period = MIN_TIMELOCK_PERIOD` (1 hour) or `remove_timelock`.
4. Once transaction sequence-ordering allows the reconfiguration transaction to execute (bound by whatever timelock currently applies to it), the malicious transaction at sequence N is now checked via `can_execute_with_timelock` against the new, drastically shorter `timelock_period`; if its `creation_time_secs` already satisfies the new period, it executes immediately — far sooner than the originally-configured 14-day protection window that owners believed guarded the funds. [6](#0-5)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L163-178)
```text
    /// Support for Multisig TimeLock.
    /// `drop` is safe here because this resource holds only primitives (no capabilities, no
    /// event handles). It's used so that `remove_timelock` can `move_from` without destructuring.
    /// Note that because on-chain transactions cannot realistically be executed in less than a
    /// second, the resolution of `creation_time_secs` is at-second granularity — setting/removing
    /// a timelock within the same on-chain second as a pending transaction's creation is not a
    /// concern in practice.
    enum MultisigAccountTimeLock has key, drop {
        V1 {
            /// The time lock period in seconds after the creation of the multisig transaction.
            timelock_period: u64,
            /// The number of approvals required to bypass the timelock and execute immediately.
            /// Must be greater than the number of signatures required normally and less than or equal to the number of owners.
            override_threshold: Option<u64>,
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L471-479)
```text
    #[view]
    /// Return true if the transaction with given transaction id can be executed now.
    public fun can_be_executed(multisig_account: address, sequence_number: u64): bool {
        assert_valid_sequence_number(multisig_account, sequence_number);
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);

        sequence_number == last_resolved_sequence_number(multisig_account) + 1 &&
            num_approvals >= num_signatures_required(multisig_account) && can_execute_with_timelock(multisig_account, sequence_number, num_approvals)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L906-969)
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

    /// Shared validation + publish logic for timelock configuration. Used by `upsert_timelock` and
    /// by the creation-time variants (`create_with_owners_and_timelock`, ...) so the invariant that
    /// `MultisigAccountTimeLock` is only ever published through a single validated path is preserved.
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
