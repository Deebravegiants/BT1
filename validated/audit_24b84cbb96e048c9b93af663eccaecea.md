Found the analog. This is a genuinely custom addition to this fork — `MultisigAccountTimeLock` (an AIP-style feature not present in stock aptos-core's `multisig_account.move`) — and its comparison logic in `can_execute_with_timelock` inverts the intended custody guarantee.

### Title
Timelock override comparison uses stale approval count, allowing premature multisig execution bypass - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
`can_execute_with_timelock` is meant to gate immediate execution of a multisig transaction: execution before the timelock expires should only be allowed once approvals reach the configured `override_threshold`. The comparison as implemented uses a borrowed reference comparison `&num_approvals >= override_threshold.borrow()` which is structurally fine, but the surrounding call sites (`can_execute`, `validate_multisig_transaction`) compute `num_approvals` by conditionally incrementing it for the *current caller's implicit vote* before calling into `can_execute_with_timelock` — this optimistic count is then used to satisfy the override check, letting the timelock be bypassed with one fewer real recorded vote than intended.

### Finding Description
In `multisig_account.move`, `can_execute` at [1](#0-0)  computes:
```
if (!has_voted_for_approval(multisig_account, sequence_number, owner)) {
    num_approvals += 1;
};
is_owner(owner, multisig_account) && ... && can_execute_with_timelock(multisig_account, sequence_number, num_approvals)
```
This speculatively adds 1 to `num_approvals` to account for the *executing* owner's implicit vote — before that vote is actually recorded on-chain. This same speculative count is then passed into `can_execute_with_timelock`, which checks:
```
(override_threshold.is_some() && &num_approvals >= override_threshold.borrow()) || elapsed >= timelock
```
at [2](#0-1) .

Because the override check receives the *speculative* (not-yet-recorded) approval count, a transaction that has exactly `override_threshold - 1` real recorded approvals can satisfy the override bypass the moment the executing owner is a new voter — the timelock is skipped even though only `override_threshold - 1` owners actually approved before this call. `validate_multisig_transaction` (the VM prologue) performs the identical pattern at [3](#0-2) , so this is the actual enforced path, not just a view function.

This breaks the intended custody invariant: "the timelock can only be bypassed if `override_threshold` owners have deliberately approved," which exists specifically to give other owners time to react to unauthorized/compromised approvals. In effect, one fewer independent approval is required than the configured override threshold specifies.

### Impact Explanation
Multisig accounts are used to control resource accounts, code objects, and pooled treasuries (custody-grade). The timelock/override mechanism is a security control meant to slow down execution unless a supermajority explicitly agrees to bypass it. Undercounting the required approvals by one weakens this control, letting a smaller-than-configured set of owners (e.g., a colluding or compromised minority) execute a transaction immediately — including transactions that reassign multisig owners, drain resource-account-held APT/FA balances, or transfer code-object ownership — without the safety window the timelock is designed to guarantee. This is a High-severity custody control weakening (off-by-one on trust threshold), not merely cosmetic.

### Likelihood Explanation
The bug triggers deterministically whenever: (1) a timelock with `override_threshold` is configured, (2) exactly `override_threshold - 1` owners have already voted, and (3) any owner who has not yet voted calls `can_execute`/executes the transaction. This is a completely realistic operational sequence for any multisig using this feature — no special conditions or attacker sophistication required beyond normal usage, making likelihood high once the timelock feature is enabled.

### Recommendation
`can_execute_with_timelock`'s override check should be evaluated only against the number of approvals actually recorded on-chain at the time of the check (i.e., before adding the speculative "implicit vote" of the calling/executing owner), or the implicit-vote increment should be applied consistently and be recorded transactionally before the override comparison is trusted. Concretely, pass the *recorded* `num_approvals` (pre-increment) into `can_execute_with_timelock`, and only allow the increment to count toward the plain `num_signatures_required` quorum check, not the override-bypass check — since the override is a stricter security gate that should require genuinely independent, already-recorded approvals.

### Proof of Concept
1. Owner creates a multisig account with `num_signatures_required = 2`, 5 owners, and a `MultisigAccountTimeLock` with `override_threshold = Some(4)`.
2. A transaction is created and 3 owners approve it (3 recorded approvals; `override_threshold` not yet met).
3. A 4th owner, who has not yet voted, calls execute (or the VM prologue calls `validate_multisig_transaction` on their behalf). Inside `can_execute`/`validate_multisig_transaction`, since this owner "has not voted for approval," `num_approvals` is speculatively incremented from 3 to 4 before `can_execute_with_timelock` is invoked.
4. `can_execute_with_timelock` sees `num_approvals == 4 == override_threshold`, and returns `true`, bypassing the timelock — even though only 3 owners had actually recorded approval before this call, one short of the configured override threshold.
5. The transaction executes immediately, defeating the timelock's purpose of giving remaining owners time to detect and reject a transaction before an override-level supermajority is reached. [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L481-514)
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
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1328-1350)
```text
    fun validate_multisig_transaction(
        owner: &signer, multisig_account: address, payload: vector<u8>) {
        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);
        let sequence_number = last_resolved_sequence_number(multisig_account) + 1;
        assert_transaction_exists(multisig_account, sequence_number);

        if (features::multisig_v2_enhancement_feature_enabled()) {
            assert!(
                can_execute(address_of(owner), multisig_account, sequence_number),
                error::invalid_argument(ENOT_ENOUGH_APPROVALS),
            );
        }
        else {
            assert!(
                can_be_executed(multisig_account, sequence_number),
                error::invalid_argument(ENOT_ENOUGH_APPROVALS),
            );
        };

        // Count approvals, including the executing owner's implicit vote.
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, address_of(owner))) {
```
