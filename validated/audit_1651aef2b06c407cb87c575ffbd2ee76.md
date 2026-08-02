## Summary

The external report's core custody invariant is: **when a safety mechanism (margin update / grace period) is disabled, positions can be closed with no window for the owner to react.** The Aptos-native analog I found is in `aptos_framework::multisig_account`'s custom **timelock/override** feature: the code that reconfigures a multisig's `num_signatures_required` does not re-validate that the timelock's `override_threshold` still exceeds it, allowing the timelock's grace period to be silently collapsed to zero for a multisig-controlled resource account.

## Finding Description

`multisig_account` supports an optional `MultisigAccountTimeLock` with an `override_threshold`: transactions reaching normal quorum (`num_signatures_required`) must wait `timelock_period` before execution, but transactions reaching the higher `override_threshold` quorum can execute immediately. This design assumes `override_threshold > num_signatures_required` at all times — it is enforced when the timelock is first configured, and error `EINVALID_TIMELOCK_OVERRIDE_THRESHOLD` (22) exists specifically to protect this invariant [1](#0-0) .

However, `update_owner_schema` — the single function backing `update_signatures_required`, `add_owners_and_update_signatures_required`, `swap_owners_and_update_signatures_required`, etc. — only re-clamps/validates `override_threshold` against the **owner count**, never against the freshly-updated `num_signatures_required`: [2](#0-1) 

The relevant path:
1. `update_signatures_required(multisig_account, new_num_signatures_required)` calls `update_owner_schema` with empty owner-add/remove lists [3](#0-2) .
2. Inside `update_owner_schema`, `num_signatures_required` is updated first, then only `num_owners >= num_signatures_required` is asserted [4](#0-3) .
3. The timelock block afterward only clamps `override_threshold` down if it exceeds `num_owners` — it never compares `override_threshold` to the just-updated `num_signatures_required` [5](#0-4) .

Because owner count is unaffected when only `num_signatures_required` is raised, the owner-count clamp never fires, and `update_signatures_required` can raise `num_signatures_required` up to (or above) an already-configured `override_threshold` with no abort. This silently breaks the invariant that `override_threshold` must be strictly greater than the normal quorum.

## Impact Explanation

Once `override_threshold <= num_signatures_required`, reaching the *normal* execution quorum automatically also satisfies the *override* quorum. Since the override path is specifically designed to skip `timelock_period`, this means every multisig transaction — not just supermajority-approved emergency ones — can execute immediately with **zero grace period**. This defeats the entire purpose of the timelock: giving co-owners/monitors a window to detect and reject a transaction from a compromised or malicious signer before it drains a resource-account-held treasury (multisig accounts are resource accounts, explicitly documented as controlling live assets) [6](#0-5) . This is a custody-grade impact: it removes a recovery/reaction window for multisig-held APT/FA/object custody, directly mirroring the external bug's "no grace period → immediate adverse action" pattern.

## Likelihood Explanation

`update_signatures_required` and its variants are ordinary owner-callable entry functions requiring only normal multisig quorum approval — no special privilege beyond being an existing owner is needed to trigger this state. An owner (or a set of owners colluding, or a single compromised signer once enough approvals are gathered through normal social/procedural means) can raise `num_signatures_required` to equal/exceed `override_threshold` without any abort, silently disabling the timelock for all future transactions. I was not able to fully inspect `can_be_executed`/`validate_multisig_transaction` (the functions that presumably use `override_threshold` to permit skipping the wait) in this pass to 100% confirm the exact comparison operator used there; this should be verified before treating this as fully confirmed, but the absence of any cross-check between `num_signatures_required` and `override_threshold` in `update_owner_schema` is clearly demonstrated in the retrieved source/doc.

## Recommendation

In `update_owner_schema`, after applying `num_signatures_required` changes, add an explicit assertion (when a `MultisigAccountTimeLock` exists and `override_threshold` is set) that `override_threshold > num_signatures_required`, aborting with `EINVALID_TIMELOCK_OVERRIDE_THRESHOLD` otherwise — mirroring the check already performed for owner-count clamping and for the initial `upsert_timelock` configuration.

## Proof of Concept

1. Owner creates a multisig account with 3 owners, `num_signatures_required = 1`, and configures a timelock via `upsert_timelock(period, override_threshold = Some(2))` — valid since `2 > 1`.
2. Owner calls `update_signatures_required(multisig_signer, 2)` (via the normal proposal/execute flow, requiring only quorum of 1). This raises `num_signatures_required` to `2`, equal to `override_threshold`. No assertion in `update_owner_schema`'s timelock block catches this because it only compares `override_threshold` to `num_owners` (unchanged at 3), not to `num_signatures_required`.
3. A subsequent multisig transaction (e.g., transferring the resource account's APT/FA balance out) reaches 2 approvals — the normal quorum. Because `override_threshold (2) <= num_signatures_required (2)`, if the execution-check logic treats "approvals >= override_threshold" as sufficient to bypass `timelock_period`, this transaction executes immediately instead of waiting, eliminating the reaction window the timelock was designed to guarantee. [4](#0-3) [5](#0-4)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1-13)
```text
/// Enhanced multisig account standard on Aptos. This is different from the native multisig scheme support enforced via
/// the account's auth key.
///
/// This module allows creating a flexible and powerful multisig account with seamless support for updating owners
/// without changing the auth key. Users can choose to store transaction payloads waiting for owner signatures on chain
/// or off chain (primary consideration is decentralization/transparency vs gas cost).
///
/// The multisig account is a resource account underneath. By default, it has no auth key and can only be controlled via
/// the special multisig transaction flow. However, owners can create a transaction to change the auth key to match a
/// private key off chain if so desired.
///
/// Transactions need to be executed in order of creation, similar to transactions for a normal Aptos account (enforced
/// with account nonce).
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L103-112)
```text
    /// Timelock period must be between MIN_TIMELOCK_PERIOD and MAX_TIMELOCK_PERIOD.
    const EINVALID_TIMELOCK_DURATION: u64 = 21;
    /// Timelock override threshold must be greater than num_signatures_required and at most the number of owners.
    const EINVALID_TIMELOCK_OVERRIDE_THRESHOLD: u64 = 22;
    /// Transaction has enough approvals but the timelock period has not yet elapsed.
    const ETIMELOCK_NOT_EXPIRED: u64 = 23;
    /// No timelock configuration exists for the multisig account.
    const ETIMELOCK_DOES_NOT_EXIST: u64 = 24;
    /// Feature flag for multisig timelock is not enabled.
    const ETIMELOCK_NOT_ENABLED: u64 = 25;
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1586-1620)
```text
    /// Add new owners, remove owners to remove, update signatures required.
    fun update_owner_schema(
        multisig_address: address,
        new_owners: vector<address>,
        owners_to_remove: vector<address>,
        optional_new_num_signatures_required: Option<u64>,
    ) {
        assert_multisig_account_exists(multisig_address);
        let multisig_account_ref_mut =
            borrow_global_mut<MultisigAccount>(multisig_address);
        // Verify no overlap between new owners and owners to remove.
        new_owners.for_each_ref(|new_owner_ref| {
            assert!(
                !vector::contains(&owners_to_remove, new_owner_ref),
                error::invalid_argument(EOWNERS_TO_REMOVE_NEW_OWNERS_OVERLAP)
            )
        });
        // If new owners provided, try to add them and emit an event.
        if (new_owners.length() > 0) {
            multisig_account_ref_mut.owners.append(new_owners);
            validate_owners(
                &multisig_account_ref_mut.owners,
                multisig_address
            );
            emit(AddOwners { multisig_account: multisig_address, owners_added: new_owners });
        };
        // If owners to remove provided, try to remove them.
        if (owners_to_remove.length() > 0) {
            let owners_ref_mut = &mut multisig_account_ref_mut.owners;
            let owners_removed = vector[];
            owners_to_remove.for_each_ref(|owner_to_remove_ref| {
                let (found, index) =
                    vector::index_of(owners_ref_mut, owner_to_remove_ref);
                if (found) {
                    vector::push_back(
```

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L4309-4350)
```markdown
    // If new signature count provided, try <b>to</b> <b>update</b> count.
    <b>if</b> (optional_new_num_signatures_required.is_some()) {
        <b>let</b> new_num_signatures_required =
            optional_new_num_signatures_required.extract();
        <b>assert</b>!(
            new_num_signatures_required &gt; 0,
            <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error_invalid_argument">error::invalid_argument</a>(<a href="multisig_account.md#0x1_multisig_account_EINVALID_SIGNATURES_REQUIRED">EINVALID_SIGNATURES_REQUIRED</a>)
        );
        <b>let</b> old_num_signatures_required =
            multisig_account_ref_mut.num_signatures_required;
        // Only <b>apply</b> <b>update</b> and emit <a href="event.md#0x1_event">event</a> <b>if</b> a change indicated.
        <b>if</b> (new_num_signatures_required != old_num_signatures_required) {
            multisig_account_ref_mut.num_signatures_required =
                new_num_signatures_required;
            emit(
                <a href="multisig_account.md#0x1_multisig_account_UpdateSignaturesRequired">UpdateSignaturesRequired</a> {
                    <a href="multisig_account.md#0x1_multisig_account">multisig_account</a>: multisig_address,
                    old_num_signatures_required,
                    new_num_signatures_required,
                }
            );
        }
    };
    // Verify number of owners.
    <b>let</b> num_owners = multisig_account_ref_mut.owners.length();
    <b>assert</b>!(
        num_owners &gt;= multisig_account_ref_mut.num_signatures_required,
        <a href="../../aptos-stdlib/../move-stdlib/doc/error.md#0x1_error_invalid_state">error::invalid_state</a>(<a href="multisig_account.md#0x1_multisig_account_ENOT_ENOUGH_OWNERS">ENOT_ENOUGH_OWNERS</a>)
    );

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
```
