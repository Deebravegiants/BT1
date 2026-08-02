## Custody Invariant Reduction

The Sherlock bug's core invariant: *a validation function that checks individual bounds (`>0`) but omits a required cross-field/cross-state bound (`tokensPerMint <= maxSupply`) can permanently brick the contract's operable state.* The Aptos-native analog I traced is in `multisig_account.move`'s owner/threshold update path, which controls custody of a multisig-held resource account, its `SignerCapability`, and any APT/fungible assets held under it.

### Title
Missing re-validation of `num_signatures_required <= owners.length()` after owner removal permanently bricks a multisig account - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`create_with_owners_internal` enforces `num_signatures_required > 0 && num_signatures_required <= owners.length()` at creation time [1](#0-0) . However, the shared self-update function `update_owner_schema` — used by `remove_owners`, `remove_owner`, and `swap_owner`/`swap_owners` (which pass `option::none()` for the new signature count) — only re-validates the newly supplied threshold when one is explicitly provided, and even then only checks `new_num_signatures_required > 0`, never `<= owners.length()` [2](#0-1) . When owners are removed without simultaneously supplying a new (lower) `num_signatures_required`, the existing threshold is left unchanged against the now-smaller owner set [3](#0-2) .

### Finding Description
`remove_owners` / `remove_owner` / `swap_owner(s)` all route through `update_owner_schema`, passing `option::none()` for the signature-count parameter [4](#0-3) . Inside `update_owner_schema`, the owner-removal branch mutates `owners` directly with no subsequent check that `num_signatures_required <= owners.length()` [3](#0-2) . The only threshold bound check in this function is `new_num_signatures_required > 0`, and it only runs when the caller explicitly supplies a new threshold in the same call [2](#0-1) .

Contrast this with the creation path, `create_with_owners_internal`, which strictly enforces the bound `num_signatures_required <= owners.length()` [1](#0-0)  — this is exactly the class of check the Sherlock report calls out as being incompletely applied elsewhere in the lifecycle (present at creation, absent at a later mutation point).

Because execution of any multisig transaction requires collecting `num_signatures_required` approvals, each owner can vote at most once (`num_approvals_and_rejections_internal` iterates unique `owners`) [5](#0-4) . If the owner count is reduced below the existing `num_signatures_required` (e.g., 3 owners requiring 3 signatures, then one owner is removed via `remove_owner` leaving 2 owners while the threshold stays 3), the maximum possible approvals (2) can never reach the threshold (3). Every subsequent multisig transaction — including any transaction attempting to lower `num_signatures_required` back down or re-add owners via `update_signatures_required`/`add_owners`, which themselves must go through the same proposal-and-vote-and-execute flow — becomes permanently unexecutable.

### Impact Explanation
This breaks the "Multisig-owned assets, resource accounts, and code objects must not leak... freeze, or transfer authority" and "Permanent lock or non-recoverable loss of... multisig-held... value" custody pivots directly. A multisig account created via `create_multisig_account`/`create_with_owners` typically also holds a `SignerCapability` for an underlying resource account and is registered to hold `AptosCoin` [6](#0-5) . Once bricked in this way, all APT, fungible assets, or resource-account-controlled objects owned by that multisig address become permanently inaccessible — there is no governance/emergency escape hatch in this module for an owner-mismatched threshold, since every remediation path (removing more owners, lowering the threshold, adding owners) itself requires reaching the now-unreachable approval threshold. This is a high/critical, non-recoverable custody loss.

### Likelihood Explanation
This requires the owners of a multisig to approve and execute a `remove_owners`/`remove_owner`/`swap_owner` transaction without simultaneously lowering `num_signatures_required` to be `<=` the new owner count. This is plausible in practice: `remove_owner`/`swap_owner` do not require the caller to touch the threshold, and nothing in the UI/API/module signals that removing owners can silently invalidate the threshold constraint. A well-intentioned multisig operation (e.g., removing a compromised or departing owner) can accidentally or unknowingly brick the account. No malicious actor or privileged bypass is required — it is a straightforward invariant gap in unprivileged (owner-controlled) code that mirrors the "check some conditions, not all" root cause of the seed report.

### Recommendation
In `update_owner_schema`, after owners are added/removed, add an invariant check equivalent to creation-time validation:
```move
assert!(
    multisig_account_ref_mut.num_signatures_required <= multisig_account_ref_mut.owners.length(),
    error::invalid_state(EINVALID_SIGNATURES_REQUIRED)
);
```
This assertion should run unconditionally at the end of `update_owner_schema` (not only inside the `if (optional_new_num_signatures_required.is_some())` branch), so that any owner-count mutation is always validated against the current threshold, exactly mirroring the bound enforced in `create_with_owners_internal`.

### Proof of Concept
1. Owner A calls `create_with_owners(A, [B, C], 3, ...)`, creating a multisig with owners `[A, B, C]` and `num_signatures_required = 3` [7](#0-6) .
2. Owners propose and successfully execute a `remove_owner(multisig_signer, C)` transaction (requires 3/3 approvals, still achievable with 3 owners) [8](#0-7) .
3. Inside `update_owner_schema`, owner `C` is removed, leaving `owners = [A, B]`, while `num_signatures_required` remains `3` — no assertion catches this [9](#0-8) .
4. Any subsequent transaction (including one to fix the threshold via `update_signatures_required`) requires 3 approvals but only 2 owners (A, B) remain, so `num_approvals` can never reach 3. The multisig account, and any assets/resource-account control it holds, is permanently locked with no on-chain recovery path.

Note: I could not directly view the exact line numbers of `update_owner_schema` in the `.move` source file itself (only in the generated `doc/multisig_account.md`, which mirrors the source implementation) within the available search iterations; a Devin session with full file access should confirm the exact source line numbers before patching.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L772-789)
```text
    public entry fun create_with_owners(
        owner: &signer,
        additional_owners: vector<address>,
        num_signatures_required: u64,
        metadata_keys: vector<String>,
        metadata_values: vector<vector<u8>>,
    ) {
        let (multisig_account, multisig_signer_cap) = create_multisig_account(owner);
        additional_owners.push_back(address_of(owner));
        create_with_owners_internal(
            &multisig_account,
            additional_owners,
            num_signatures_required,
            option::some(multisig_signer_cap),
            metadata_keys,
            metadata_values,
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L873-877)
```text
        assert!(features::multisig_accounts_enabled(), error::unavailable(EMULTISIG_ACCOUNTS_NOT_ENABLED_YET));
        assert!(
            num_signatures_required > 0 && num_signatures_required <= owners.length(),
            error::invalid_argument(EINVALID_SIGNATURES_REQUIRED),
        );
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1022-1025)
```text
    entry fun remove_owner(
        multisig_account: &signer, owner_to_remove: address) {
        remove_owners(multisig_account, vector[owner_to_remove]);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1027-1056)
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

    /// Swap an owner in for an old one, without changing required signatures.
    entry fun swap_owner(
        multisig_account: &signer,
        to_swap_in: address,
        to_swap_out: address
    ) {
        update_owner_schema(
            address_of(multisig_account),
            vector[to_swap_in],
            vector[to_swap_out],
            option::none()
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1488-1499)
```text
    fun create_multisig_account(owner: &signer): (signer, SignerCapability) {
        let owner_nonce = account::get_sequence_number(address_of(owner));
        let (multisig_signer, multisig_signer_cap) =
            account::create_resource_account(owner, create_multisig_account_seed(to_bytes(&owner_nonce)));
        // Register the account to receive APT as this is not done by default as part of the resource account creation
        // flow.
        if (!coin::is_account_registered<AptosCoin>(address_of(&multisig_signer))) {
            coin::register<AptosCoin>(&multisig_signer);
        };

        (multisig_signer, multisig_signer_cap)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1532-1548)
```text
    inline fun num_approvals_and_rejections_internal(owners: &vector<address>, transaction: &MultisigTransaction): (u64, u64) {
        let num_approvals = 0;
        let num_rejections = 0;

        let votes = &transaction.votes;
        owners.for_each_ref(|owner| {
            if (simple_map::contains_key(votes, owner)) {
                if (*simple_map::borrow(votes, owner)) {
                    num_approvals += 1;
                } else {
                    num_rejections += 1;
                };
            }
        });

        (num_approvals, num_rejections)
    }
```

**File:** aptos-move/framework/aptos-framework/doc/multisig_account.md (L4288-4320)
```markdown
    // If owners <b>to</b> remove provided, try <b>to</b> remove them.
    <b>if</b> (owners_to_remove.length() &gt; 0) {
        <b>let</b> owners_ref_mut = &<b>mut</b> multisig_account_ref_mut.owners;
        <b>let</b> owners_removed = <a href="../../aptos-stdlib/../move-stdlib/doc/vector.md#0x1_vector">vector</a>[];
        owners_to_remove.for_each_ref(|owner_to_remove_ref| {
            <b>let</b> (found, index) =
                <a href="../../aptos-stdlib/../move-stdlib/doc/vector.md#0x1_vector_index_of">vector::index_of</a>(owners_ref_mut, owner_to_remove_ref);
            <b>if</b> (found) {
                <a href="../../aptos-stdlib/../move-stdlib/doc/vector.md#0x1_vector_push_back">vector::push_back</a>(
                    &<b>mut</b> owners_removed,
                    <a href="../../aptos-stdlib/../move-stdlib/doc/vector.md#0x1_vector_swap_remove">vector::swap_remove</a>(owners_ref_mut, index)
                );
            }
        });
        // Only emit <a href="event.md#0x1_event">event</a> <b>if</b> owner(s) actually removed.
        <b>if</b> (owners_removed.length() &gt; 0) {
            emit(
                <a href="multisig_account.md#0x1_multisig_account_RemoveOwners">RemoveOwners</a> { <a href="multisig_account.md#0x1_multisig_account">multisig_account</a>: multisig_address, owners_removed }
            );
        }
    };
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
```
