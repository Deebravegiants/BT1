## Custody Analog Found: Rejected-Owner Vote Silently Counted as Approval Bypasses Multisig Timelock Override

### Title
Executing owner's own explicit rejection is silently converted into a phantom approval, letting a dissenting owner unilaterally satisfy the unanimous `override_threshold` and bypass the treasury timelock - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The multisig timelock feature (`MultisigAccountTimeLock`) is designed so that immediate execution of a pending transaction bypassing the safety delay requires `override_threshold` genuine approvals - stricter than the normal `num_signatures_required` quorum. However, both `can_execute` and the VM-invoked `validate_multisig_transaction` compute the "implicit vote" of the executing owner using `has_voted_for_approval`, which returns `false` both when an owner has *not voted* and when an owner has *explicitly voted reject*. This means an owner who explicitly voted **against** a transaction can later call execute themselves and have that same rejection silently counted as a "yes" toward `num_approvals`, potentially completing the unanimous `override_threshold` and skipping the timelock entirely - despite their own vote of record being "no."

### Finding Description
`MultisigAccountTimeLock` stores an `override_threshold`, documented as requiring more approvals than `num_signatures_required`, specifically to gate immediate (delay-free) execution behind a stronger, closer-to-unanimous bar: [1](#0-0) 

The check for whether the timelock can be skipped is `can_execute_with_timelock`, which is driven entirely by the caller-supplied `num_approvals`: [2](#0-1) 

Both the view-function path (`can_execute`) and the real VM execution path (`validate_multisig_transaction`, invoked from `run_multisig_prologue`) compute `num_approvals` the same way: take the genuine tally from `num_approvals_and_rejections`, then add **+1** if the *executing* owner's `has_voted_for_approval` is false: [3](#0-2) [4](#0-3) 

`has_voted_for_approval` conflates "never voted" with "voted reject" - both return `false`: [5](#0-4) 

Consequently, an owner who has cast an explicit **reject** vote (recorded as `false` in `transaction.votes`, and counted in `num_rejections` via `num_approvals_and_rejections_internal`) is *also* eligible to have that same vote silently converted into a `+1` approval the moment they call execute themselves. The same owner is simultaneously counted as a rejecter (in the real vote map, affecting `can_be_rejected`) and as an approver (in the phantom implicit count used for both `num_signatures_required` and, critically, `override_threshold`).

This breaks the custody invariant that `override_threshold` genuine approvals are required to bypass the timelock protecting a resource-account-controlled multisig's assets (e.g., APT or fungible-asset balances held directly by the multisig resource account, or a `SignerCapability` gated by that multisig). The override path is meant to require real, affirmative consent from that many distinct owners before allowing an immediate, delay-free spend; instead, one dissenting owner's own "no" can be laundered into the missing "yes" needed to hit `override_threshold`.

### Impact Explanation
Concretely, for a 3-of-3-owner multisig with `num_signatures_required = 2` and `override_threshold = 3` (i.e., unanimous consent required to skip the timelock on a high-value transfer):
- Owner_1 creates the transaction (auto-approve, 1 genuine "yes").
- Owner_2 explicitly approves (2 genuine "yes").
- Owner_3 explicitly **rejects** — signaling they do not want this transaction executed immediately (or at all).
- Owner_3 (the very owner who voted "no") then calls execute. `has_voted_for_approval(owner_3)` returns `false` (since their vote is `false`), so `num_approvals` is bumped from 2 to 3, exactly meeting `override_threshold = 3`, and `can_execute_with_timelock` returns `true` — the timelock is bypassed and the transaction executes immediately, funds move out of the multisig-controlled resource account with no genuine unanimous consent.

This is a custody-grade violation: it corrupts the approval accounting used to gate value-moving execution (APT/FA/resource-account-controlled transfers, ownership/auth-key rotations, or any entry function executed as the multisig signer), allowing a single account (even one that explicitly voted to block/delay the action) to defeat the stronger `override_threshold` safety gate that the multisig owners configured specifically to prevent premature high-risk execution.

### Likelihood Explanation
The path requires no special privilege beyond being one of the multisig's existing owners (a normal participant, not an attacker with elevated access) and requires only the `multisig_v2_enhancement_feature_enabled` feature flag plus a timelock/override configuration - both are supported, in-scope, real network configurations. No race condition or unusual timing is needed; the flaw is deterministic given the vote sequence described. Any deployed multisig using `override_threshold` timelock bypass is exposed to a dissenting owner turning their own rejection into the deciding "approval."

### Recommendation
Distinguish "has not voted" from "explicitly voted reject" when computing the implicit executor vote. The implicit approval bump should only apply if the executing owner has genuinely never cast a vote (`vote()` returns `voted == false`), not merely `has_voted_for_approval == false`. Concretely, in both `can_execute` and `validate_multisig_transaction`:
```
let (has_voted, vote_value) = vote(multisig_account, sequence_number, owner);
if (!has_voted) {
    num_approvals += 1;
} else if (!vote_value) {
    // Owner explicitly rejected; do not silently convert to approval.
    // Optionally abort/require explicit approve_transaction call to change vote.
};
```
This ensures `num_approvals` (used for both `num_signatures_required` and, especially, `override_threshold`) only reflects genuine "yes" votes plus a legitimate first-time implicit approval from an owner who never voted, never silently overriding an owner's explicit "no."

### Proof of Concept
Using the existing test harness in `multisig_account.move`'s test module (`setup_timelock_multisig`, `upsert_timelock`, `create_transaction`, `approve_transaction`, `reject_transaction`, `can_execute`), configure `num_signatures_required = 2`, `override_threshold = option::some(3)`, with 3 owners:
```
let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
let multisig_signer = &create_signer(multisig_account);
upsert_timelock(multisig_signer, 3600, option::some(3)); // unanimous override required

create_transaction(owner_1, multisig_account, PAYLOAD);   // owner_1 implicit "yes"
approve_transaction(owner_2, multisig_account, 1);        // owner_2 explicit "yes" (2/3 genuine yes)
reject_transaction(owner_3, multisig_account, 1);         // owner_3 explicit "no"

// Timelock has NOT expired, and only 2 genuine "yes" votes exist.
assert!(!can_be_executed(multisig_account, 1), 0);

// But owner_3 (who voted NO) can trigger override bypass by calling execute themselves:
assert!(can_execute(address_of(owner_3), multisig_account, 1), 1); // TRUE - bypasses timelock
```
`can_execute(owner_3, ...)` returns `true` even though only 2 of 3 owners genuinely approved and owner_3's actual, on-chain vote is a rejection — demonstrating the override threshold is satisfiable via a phantom "self-approval" derived from an explicit reject vote, referencing the exact logic at [3](#0-2)  and [5](#0-4) .

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L170-178)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L483-493)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1348-1359)
```text
        // Count approvals, including the executing owner's implicit vote.
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, address_of(owner))) {
            num_approvals += 1;
        };
        assert!(num_approvals >= num_signatures_required(multisig_account), error::invalid_argument(ENOT_ENOUGH_APPROVALS));

        // Timelock check — separate from quorum so the error is unambiguous.
        assert!(
            can_execute_with_timelock(multisig_account, sequence_number, num_approvals),
            error::invalid_state(ETIMELOCK_NOT_EXPIRED),
        );
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1556-1559)
```text
    inline fun has_voted_for_approval(multisig_account: address, sequence_number: u64, owner: address): bool {
        let (voted, vote) = vote(multisig_account, sequence_number, owner);
        voted && vote
    }
```
