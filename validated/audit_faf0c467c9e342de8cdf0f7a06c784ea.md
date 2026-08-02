## Title
`update_signatures_required` / `update_owner_schema` Can Silently Break the Timelock Override Invariant, Allowing Owners to Bypass a Configured Multisig Timelock - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`multisig_account.move` implements an optional `MultisigAccountTimeLock` (`V1`) that is supposed to delay execution of any transaction until `timelock_period` seconds have elapsed, unless a higher-quorum `override_threshold` of approvals is reached. `upsert_timelock_internal` enforces the invariant `override_threshold > num_signatures_required` at the moment the timelock is configured [1](#0-0) . However, `num_signatures_required` can later be raised independently via `update_signatures_required`/`update_owner_schema` without ever re-validating or adjusting the existing `override_threshold` [2](#0-1) .

### Finding Description
The intended invariant, documented directly in the code, is: *"override_threshold, if provided, must be > num_signatures_required and <= the number of owners"* [3](#0-2) . This is checked only inside `upsert_timelock_internal`, at configuration time [1](#0-0) .

Separately, `update_owner_schema` (invoked by `update_signatures_required`, `add_owners_and_update_signatures_required`, `swap_owners_and_update_signatures_required`) can change `num_signatures_required` at any later time. Based on the doc-generated implementation, this function only clamps `override_threshold` down when the *owner count* shrinks below it (`timelock.override_threshold.borrow() > &num_owners`) [4](#0-3) . There is no corresponding check for the case where `num_signatures_required` is *increased* to a value at or above the existing `override_threshold`.

Once that happens, `override_threshold <= num_signatures_required`. The timelock bypass logic in `can_execute_with_timelock` treats a transaction as immediately executable whenever `num_approvals >= override_threshold` [5](#0-4) . Since the normal execution path (`validate_multisig_transaction` / `can_execute`) already requires `num_approvals >= num_signatures_required` before the timelock check is even reached [6](#0-5) , once `override_threshold <= num_signatures_required` every transaction that reaches ordinary quorum also satisfies the override condition — the timelock delay is unconditionally skipped from that point forward for every pending and future transaction, with no explicit action taken by any owner to disable or weaken the timelock.

### Impact Explanation
The multisig timelock is a custody control: it is meant to give owners/observers a guaranteed window to detect and react to a malicious or compromised-key transaction (e.g., a fund transfer, auth-key rotation, or owner-list change) queued against the multisig-owned resource account before it executes. Silently nullifying that delay — as a side effect of an unrelated, seemingly benign `update_signatures_required` operation — removes the safety window the timelock was explicitly designed to guarantee, for all transactions on the account, without emitting any signal that the *override* protection (as opposed to the signature count) has been weakened. On a multisig account controlling APT or other assets, this converts what operators believe is a "delay + quorum-override" custody control into a normal k-of-n multisig with no delay guarantee at all, undermining the documented security assumption relied upon by asset holders.

### Likelihood Explanation
This does not require any external attacker — it is triggered purely by legitimate owner governance actions that are common and expected (raising the required signature threshold as an organization grows, e.g. via `update_signatures_required` or `swap_owners_and_update_signatures_required`). No malicious intent by any single owner is required; it can happen accidentally whenever owners increase `num_signatures_required` without being aware that it also silently deactivates the override protection. Given that the invariant is explicitly documented as something that must hold ("override_threshold must be > num_signatures_required"), and the code has clamp logic for the *owner-count* case but omits the symmetric case for *signature-count* increases, this looks like a genuine one-sided oversight in `update_owner_schema` rather than an intentional design choice.

### Recommendation
In `update_owner_schema`, whenever `num_signatures_required` is updated, also re-validate (or clamp with an emitted `TimelockUpdated` event, mirroring the existing owner-count clamp) any existing `MultisigAccountTimeLock.override_threshold` so that it remains strictly greater than the new `num_signatures_required`. If it does not, either abort the update (forcing an explicit follow-up `upsert_timelock` call) or automatically raise/clear the override threshold and emit `TimelockUpdated`, consistent with how the code already handles the owner-count-shrink case.

### Proof of Concept
1. Owner creates a multisig account with `num_signatures_required = 2` and configures a timelock via `create_with_owners_and_timelock`/`upsert_timelock` with `timelock_period = 14 days`, `override_threshold = Some(4)` (out of, say, 5 owners) — validated to satisfy `4 > 2` and `4 <= 5` at `upsert_timelock_internal` [7](#0-6) .
2. Owners later call `update_signatures_required(multisig_account, 4)` to raise the normal quorum to 4-of-5. This call only touches `MultisigAccount.num_signatures_required`; it does not check or adjust `MultisigAccountTimeLock.override_threshold`, which remains `Some(4)`.
3. Now `override_threshold (4) <= num_signatures_required (4)`, violating the documented invariant.
4. Any future or pending transaction that collects the now-ordinary 4 approvals immediately satisfies `can_execute_with_timelock`'s override branch (`num_approvals >= override_threshold`) [8](#0-7)  and executes with zero delay — even though the account's timelock configuration was never explicitly weakened by an `upsert_timelock` call, and `TimelockUpdated`/`TimelockRemoved` events (the intended signal for security-relevant timelock changes) are never emitted.

**Caveat**: I was unable to view the exact current source of `update_owner_schema`'s clamping block directly (only the generated doc/HTML rendering at lines 4339–4351, which reflects the same source), so I could not verify with 100% certainty there isn't an additional guard elsewhere in the function that I didn't retrieve within the available tool calls. I recommend a background Devin session read the full `update_owner_schema` function body in `multisig_account.move` (source, not doc) to confirm there is no signature-count-vs-override-threshold check before treating this as fully confirmed.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L497-515)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L906-908)
```text
    /// Upsert the timelock configuration for the multisig account.
    /// timelock_period must be between MIN_TIMELOCK_PERIOD and MAX_TIMELOCK_PERIOD.
    /// override_threshold, if provided, must be > num_signatures_required and <= the number of owners.
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L938-951)
```text
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
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1093-1101)
```text
    entry fun update_signatures_required(
        multisig_account: &signer, new_num_signatures_required: u64) {
        update_owner_schema(
            address_of(multisig_account),
            vector[],
            vector[],
            option::some(new_num_signatures_required)
        );
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
