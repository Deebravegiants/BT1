### Title
Timelock override_threshold can be satisfied by an uncast, non-persisted "implicit" approval, allowing an executor to bypass the anti-theft delay for custody-critical multisig transactions - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The Sherlock report's underlying custody invariant is: *a control value that is supposed to be "zeroed out"/excluded from an accounting or authorization decision (market weight → settlement fee) is instead still counted, silently weakening the protection the zeroing was meant to provide.* The Aptos-native analog is in the newly added multisig timelock feature: `can_execute`'s "implicit vote" (added purely for view-function ergonomics to answer "if I approve now, can I execute?") is passed into `can_execute_with_timelock`, where it is also used to satisfy `override_threshold` — the higher, supermajority bar that is supposed to require *more real, recorded owner approvals* than normal execution before the safety timelock can be skipped.

### Finding Description
`multisig_account.move` introduces a per-multisig timelock (`MultisigAccountTimeLock`) with two knobs:
- `timelock_period`: mandatory waiting time before a transaction is executable.
- `override_threshold`: an approval count *stricter than* `num_signatures_required` that, if reached, lets owners skip the wait entirely. [1](#0-0) 

The override is gated by `can_execute_with_timelock`, which receives a `num_approvals` parameter and compares it against `override_threshold`: [2](#0-1) 

That `num_approvals` value is computed differently depending on caller:
- `can_be_executed` (no `owner` argument) computes `num_approvals` strictly from `num_approvals_and_rejections`, i.e. only from votes actually recorded in the `MultisigTransaction.votes` map. [3](#0-2) 
- `can_execute(owner, multisig_account, sequence_number)` adds a synthetic +1 for the calling `owner` if they haven't voted yet, then feeds this inflated count into the *same* `can_execute_with_timelock` function that gates the override bypass: [4](#0-3) 

This mixing is confirmed by the test suite itself, which documents the exact discrepancy: [5](#0-4) 

`test_implicit_vote_counts_toward_override` shows: with `override_threshold = 3` and only 2 *recorded* approvals (owner_1's auto-vote at creation + owner_2's explicit approval), `owner_3` — who has never approved and has no entry in `votes` — can call `can_execute(owner_3, ...)` and get `true`, because their own uncast vote is silently added to reach the override count of 3. Meanwhile `can_be_executed` (the strict, non-owner-specific check) correctly returns `false` for the same state, proving the two functions diverge specifically on the override-threshold path.

The custody invariant broken is the same shape as the Vault bug: `override_threshold` is documented as "must be greater than the number of signatures required normally," i.e., it exists specifically to demand a *stronger, verifiable* consensus before skipping the safety delay that protects custody-critical multisig actions (fund transfers out of a resource account, FA metadata/freeze changes, ownership reassignment of objects controlled by the multisig, etc.). By letting an unrecorded, self-only "phantom" vote count toward that stronger bar, the code effectively still "charges" credit for a vote that was never actually cast/persisted — exactly analogous to the Vault still charging a "zeroed-out" market's settlement fee. The protection the override was designed to require (N distinct, recorded, verifiable approvals) is downgraded to N-1 for whichever owner is the one calling execute.

### Impact Explanation
If the actual on-chain execution path used by the VM (`validate_multisig_transaction`, per the module's own audit table) mirrors `can_execute`'s owner-aware, implicit-vote-inclusive logic rather than `can_be_executed`'s strict logic, then any single one of the k-of-n owners who has NOT approved a pending transaction can still trigger immediate override-bypass execution, effectively needing only `override_threshold - 1` real votes plus themselves. This defeats the entire purpose of a supermajority-gated timelock bypass for a multisig account, which is the standard custody control for resource accounts, code objects, and fungible-asset/administrative capabilities held by that multisig. A malicious or compromised owner (or a colluding minority) could push through a high-value transaction (fund drain, metadata/ownership reassignment, freeze/mint authority change) without the intended extra-approval friction and without giving the remaining owners the deliberate `timelock_period` window to notice and reject it — the very custody safeguard the feature exists to provide.

### Likelihood Explanation
Medium-to-High if `validate_multisig_transaction`'s real VM-invoked path reuses `can_execute`/`can_execute_with_timelock` with the implicit-vote count (as strongly suggested by the audit table wording tying `validate_multisig_transaction` to "the owner" and by `can_execute` being the only public function that answers "can this specific owner execute now"). This requires no privileged access beyond being one of the existing owners (which is expected/normal usage, not a privileged-governance assumption), and the divergence is deterministic and already demonstrated by the project's own test (`test_implicit_vote_counts_toward_override`).

I was not able to view the exact body of `validate_multisig_transaction` (the VM-facing prologue/entry point) in this pass, so I cannot 100% confirm it consumes the implicit-vote-inclusive `can_execute` path versus the strict `can_be_executed` path — this is the key remaining uncertainty. If `validate_multisig_transaction` instead calls `can_be_executed` (or reimplements the strict, non-implicit accounting) for the override check, this finding would not hold at execution time and would only affect the view function's advisory accuracy.

### Recommendation
Decouple the "implicit self-vote" convenience (useful for a UI asking "if I sign now, does this go through immediately under normal threshold?") from the override-threshold bypass check. `can_execute_with_timelock` should only ever be evaluated against strictly recorded, persisted approvals (the same accounting as `can_be_executed`) when deciding whether to skip the timelock, regardless of which function or entry point triggers execution. If an implicit self-vote convenience is kept for `can_execute`, ensure the actual VM execution path (`validate_multisig_transaction`) never derives its override-threshold `num_approvals` from anything but `num_approvals_and_rejections`.

### Proof of Concept
Using the existing test as the reproduction skeleton (already present in the repo): [5](#0-4) 

1. `setup_timelock_multisig` creates a 3-owner multisig with `num_signatures_required = 2` (per the surrounding test helpers).
2. Configure `upsert_timelock(multisig_signer, 3600, option::some(3))` — override requires all 3 owners.
3. `create_transaction(owner_1, ...)` (auto-approves owner_1) then `approve_transaction(owner_2, ...)` — 2 recorded approvals, `owner_3` never votes.
4. `can_be_executed(multisig_account, 1)` correctly returns `false` (only 2 of 3 required for override, no implicit credit).
5. `can_execute(address_of(owner_3), multisig_account, 1)` returns `true` — `owner_3`'s never-cast vote is silently added, satisfying `override_threshold = 3` and bypassing the 3600s timelock, without that vote ever appearing in `MultisigTransaction.votes`.

To confirm actual custody impact, the next step (requiring repo access I didn't have in this pass) is to trace whether the VM's `validate_multisig_transaction`/execution prologue calls this same `can_execute`-style, implicit-vote-inclusive path — if so, `owner_3` (or any single non-approving owner) can force early, under-authorized execution of a custody-critical multisig transaction (e.g., a resource-account fund transfer or FA/object ownership change) that the timelock+override design was meant to prevent.

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L481-493)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L495-515)
```text
    /// Return true if the transaction with given transaction id can be executed immediately, or it has to wait
    /// for the timelock to expire.
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3008-3027)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_implicit_vote_counts_toward_override(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure 1 hour timelock, override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Create transaction, 2 explicit approvals (owner_1 auto-approves, owner_2 approves).
        create_transaction(owner_1, multisig_account, PAYLOAD);
        approve_transaction(owner_2, multisig_account, 1);

        // owner_3 hasn't voted. can_execute counts their implicit vote (2+1=3 >= override).
        assert!(can_execute(address_of(owner_3), multisig_account, 1), 0);

        // But can_be_executed doesn't count implicit votes, so it shouldn't pass.
        assert!(!can_be_executed(multisig_account, 1), 1);
    }
```
