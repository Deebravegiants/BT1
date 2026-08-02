Based on my investigation, the strongest custody-relevant analog I found is in `aptos_framework::multisig_account`'s recently-added timelock feature, though I was not able to fully verify the config-update function (`upsert_timelock_internal`/`update_timelock`) before running out of search budget — the finding below is based on the code path I did confirm.

### Title
Multisig timelock enforcement uses live (mutable) `MultisigAccountTimeLock` config instead of a value locked at transaction-creation time - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
The external report's root cause is that a security-critical numeric check (`dataGasPrice`) is evaluated using the *current, mutable* price at execution time rather than a value fixed/committed when the obligation was created, letting the effective protection (fee amount) diverge from what was intended when the transaction was queued. The same pattern exists in Aptos's `multisig_account` timelock: `can_execute_with_timelock` reads the *live* `MultisigAccountTimeLock` resource (`timelock_period`, `override_threshold`) at call time and combines it with the transaction's original `creation_time_secs`, instead of capturing/locking the timelock parameters that were in effect when the pending transaction was created.

### Finding Description
`can_execute_with_timelock` computes whether a pending multisig transaction may execute: [1](#0-0) 

It fetches `MultisigAccountTimeLock[multisig_account]` fresh from global storage on every call, reads `timelock_period` and `override_threshold` from that live resource, and compares the elapsed time (`now_seconds() - pending_transaction.creation_time_secs`) against the *current* `timelock_period`. The `MultisigTransaction` struct itself only stores `creation_time_secs` (a fixed point in time), not the timelock parameters that were in force when it was created: [2](#0-1) 

`validate_multisig_transaction` and `can_execute`/`can_be_executed` all funnel through this same live-lookup pattern: [3](#0-2) [4](#0-3) 

Because the timelock config is a single global resource per multisig account rather than a value snapshotted into each `MultisigTransaction` at creation, any change to `timelock_period` or `override_threshold` retroactively applies to **all currently-pending transactions**, including ones created before the change. The timelock exists specifically as a custody safety mechanism — a delay window meant to give the full quorum of owners time to detect and reject a malicious pending transaction (e.g., one that drains funds, swaps owners, or rotates the auth key) before it can execute with only a partial/override quorum. If the effective delay for an already-queued transaction can be shortened after the fact, that safety window silently narrows or disappears, exactly analogous to how `dataGasPrice` in the report used a live, mutable price to under-charge a fee that had already been "queued" (calculated) under different volatility assumptions.

### Impact Explanation
If timelock parameters can be reduced by a subsequent multisig transaction (or otherwise mutated) while a high-impact transaction is still pending — for example, a transfer of the multisig-controlled APT/FA balance, or an `add_owners`/`swap_owner` call — the shortened `timelock_period` or lowered `override_threshold` applies retroactively to that pending transaction, allowing it to execute earlier than the protection model intended. This directly undermines the intended custody control on a resource-account/multisig-controlled asset: unauthorized early execution can move value to the wrong holder or hand control (ownership of the multisig, i.e. owner list) to a party that would not have obtained the required consensus under the original timelock terms. This is a High-severity custody-control impact per the given gate (multisig control leaking transfer/ownership authority).

### Likelihood Explanation
Likelihood depends entirely on whether `update_timelock`/`upsert_timelock_internal` (the function that mutates `MultisigAccountTimeLock`) itself goes through the same k-of-n multisig approval flow and whether it can be executed concurrently with other pending transactions in the same `MultisigAccount`. I was unable to load that function's source before running out of search iterations, so I cannot confirm whether: (a) timelock updates can be batched/ordered to land before an already-pending sensitive transaction resolves, or (b) any additional per-transaction guard exists elsewhere that snapshots the timelock. This is a real gap in my verification.

### Recommendation
If confirmed, `MultisigTransaction` should snapshot the `timelock_period` (and `override_threshold`) at creation time (similar to `creation_time_secs`), and `can_execute_with_timelock` should use the snapshotted values for that specific transaction rather than re-reading the live, mutable `MultisigAccountTimeLock` resource. This preserves the invariant that the protection level committed to at transaction-creation time cannot be weakened for transactions already in flight.

### Proof of Concept
Not constructed — I could not verify the exact code path (`update_timelock`/`upsert_timelock_internal`) that mutates the timelock resource, so I cannot demonstrate concrete exploitation ordering (e.g., whether a second transaction lowering `timelock_period` can resolve and take effect before a first, malicious pending transaction's timelock check). This should be verified with full repository access (e.g., via a Devin session) before treating this as a confirmed, exploitable finding rather than a code-pattern concern.

**Caveat:** Given the incomplete verification of the config-mutation function, treat this as a lead requiring confirmation rather than a fully proven vulnerability.

### Citations

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

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L3646-3677)
```markdown
<pre><code><b>fun</b> <a href="multisig_account.md#0x1_multisig_account_validate_multisig_transaction">validate_multisig_transaction</a>(
    owner: &<a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>, <a href="multisig_account.md#0x1_multisig_account">multisig_account</a>: <b>address</b>, payload: <a href="../../aptos-stdlib/../move-stdlib/doc/vector.md#0x1_vector">vector</a>&lt;u8&gt;) {
    <a href="multisig_account.md#0x1_multisig_account_assert_multisig_account_exists">assert_multisig_account_exists</a>(<a href="multisig_account.md#0x1_multisig_account">multisig_account</a>);
    <a href="multisig_account.md#0x1_multisig_account_assert_is_owner">assert_is_owner</a>(owner, <a href="multisig_account.md#0x1_multisig_account">multisig_account</a>);
    <b>let</b> sequence_number = <a href="multisig_account.md#0x1_multisig_account_last_resolved_sequence_number">last_resolved_sequence_number</a>(<a href="multisig_account.md#0x1_multisig_account">multisig_account</a>) + 1;
    <a href="multisig_account.md#0x1_multisig_account_assert_transaction_exists">assert_transaction_exists</a>(<a href="multisig_account.md#0x1_multisig_account">multisig_account</a>, sequence_number);

    <b>if</b> (<a href="../../aptos-stdlib/../move-stdlib/doc/features.md#0x1_features_multisig_v2_enhancement_feature_enabled">features::multisig_v2_enhancement_feature_enabled</a>()) {
        <b>assert</b>!(
            <a href="multisig_account.md#0x1_multisig_account_can_execute">can_execute</a>(address_of(owner), <a href="multisig_account.md#0x1_multisig_account">multisig_account</a>, sequence_number),
            <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error_invalid_argument">error::invalid_argument</a>(<a href="multisig_account.md#0x1_multisig_account_ENOT_ENOUGH_APPROVALS">ENOT_ENOUGH_APPROVALS</a>),
        );
    }
    <b>else</b> {
        <b>assert</b>!(
            <a href="multisig_account.md#0x1_multisig_account_can_be_executed">can_be_executed</a>(<a href="multisig_account.md#0x1_multisig_account">multisig_account</a>, sequence_number),
            <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error_invalid_argument">error::invalid_argument</a>(<a href="multisig_account.md#0x1_multisig_account_ENOT_ENOUGH_APPROVALS">ENOT_ENOUGH_APPROVALS</a>),
        );
    };

    // Count approvals, including the executing owner's implicit vote.
    <b>let</b> (num_approvals, _) = <a href="multisig_account.md#0x1_multisig_account_num_approvals_and_rejections">num_approvals_and_rejections</a>(<a href="multisig_account.md#0x1_multisig_account">multisig_account</a>, sequence_number);
    <b>if</b> (!<a href="multisig_account.md#0x1_multisig_account_has_voted_for_approval">has_voted_for_approval</a>(<a href="multisig_account.md#0x1_multisig_account">multisig_account</a>, sequence_number, address_of(owner))) {
        num_approvals += 1;
    };
    <b>assert</b>!(num_approvals &gt;= <a href="multisig_account.md#0x1_multisig_account_num_signatures_required">num_signatures_required</a>(<a href="multisig_account.md#0x1_multisig_account">multisig_account</a>), <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error_invalid_argument">error::invalid_argument</a>(<a href="multisig_account.md#0x1_multisig_account_ENOT_ENOUGH_APPROVALS">ENOT_ENOUGH_APPROVALS</a>));

    // Timelock check — separate from quorum so the <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error">error</a> is unambiguous.
    <b>assert</b>!(
        <a href="multisig_account.md#0x1_multisig_account_can_execute_with_timelock">can_execute_with_timelock</a>(<a href="multisig_account.md#0x1_multisig_account">multisig_account</a>, sequence_number, num_approvals),
        <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error_invalid_state">error::invalid_state</a>(<a href="multisig_account.md#0x1_multisig_account_ETIMELOCK_NOT_EXPIRED">ETIMELOCK_NOT_EXPIRED</a>),
    );
```
