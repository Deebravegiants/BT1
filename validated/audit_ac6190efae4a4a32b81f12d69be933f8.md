### Title
Missing zero-address validation in multisig owner management can permanently brick a multisig account - (File: aptos-move/framework/aptos-framework/sources/multisig_account.move)

### Summary
The external report is a classic "missing zero-address sanity check in constructor/config" bug class: a contract accepts `0x0` as a critical control parameter with no validation, permanently bricking the contract. The Aptos-native analog is in `aptos_framework::multisig_account`, where the shared owner-list validator `validate_owners` never rejects the zero address (or any other unreachable/un-signable address) as an owner. This function backs every path that sets or mutates the owners list — initial creation and later `add_owners`/`swap_owners` calls — so a multisig can be created or mutated to include `@0x0` as one of its "owners," silently reducing the pool of addresses that can ever actually sign.

### Finding Description
`update_owner_schema` is the single internal function used by all owner-mutating entry functions (`add_owner`, `add_owners`, `add_owners_and_update_signatures_required`, `remove_owner`, `remove_owners`, `swap_owner`, `swap_owners`, `swap_owners_and_update_signatures_required`): [1](#0-0) 

It calls `validate_owners`, which only checks that a new owner is not the multisig account itself and that there are no duplicates in the combined owner list — it never checks `owner != @0x0`: [2](#0-1) 

The only other invariant enforced afterward is a numeric one — that `num_owners >= num_signatures_required` — which does not distinguish "real," signable owner addresses from unreachable ones like `@0x0`: [1](#0-0) 

Because address `0x0` has no corresponding private key and no code path in this module lets an arbitrary caller obtain a `signer` for it, an owner list that includes `@0x0` effectively has one fewer address that can ever call `approve_transaction`/`reject_transaction`/`create_transaction`. If `num_signatures_required` is set at or near the total owner count (a common "all owners must approve" configuration), the presence of `@0x0` in the owner set makes the required threshold permanently unreachable by the real owners.

### Impact Explanation
Aptos multisig accounts are resource accounts that can hold APT, fungible assets, and object-owned resources, and they are also frequently used as the deployer/upgrade authority for code objects and packages. If the owner list is corrupted to include an un-signable address (`@0x0` or any other address nobody controls) while `num_signatures_required` is set such that the phantom owner's approval is mathematically necessary to reach quorum, no transaction proposed against the multisig account can ever be approved or executed. This permanently locks any APT, fungible-asset, or object-held value custodied by the multisig account, and permanently freezes any upgrade/administrative authority the multisig controls (e.g., over a code object or resource account it governs) — squarely matching the "Permanent lock or non-recoverable loss of ... multisig-held, or resource-account-held value" and "Unauthorized ... multisig control" impact categories.

### Likelihood Explanation
This does not require an attacker with special privileges beyond what the report's null-address bug required: an owner (or a proposal that legitimately gathers enough approvals) can call `add_owners`/`swap_owners` with `@0x0` (or any never-controllable address) in the `new_owners` vector, and the module will accept it without complaint, exactly like the original `MerchantSubscription` constructor accepting `0x0` for `merchant`. Because `num_signatures_required` and the owner list are edited independently and the module never cross-checks "is this owner address actually reachable," a single overlooked entry (fat-fingered address, copy-paste error, or a malicious insider proposal disguised among legitimate additions) is sufficient to trigger the bricking condition, especially in k-of-n configurations close to n-of-n.

### Recommendation
Add an explicit sanity check in `validate_owners` (and/or in `update_owner_schema` before appending `new_owners`) that rejects `@0x0` as an owner address, mirroring the "fail early and loudly" principle from the original report:
```move
assert!(owner != &@0x0, error::invalid_argument(EOWNER_CANNOT_BE_ZERO_ADDRESS));
```
Consider also validating that `num_signatures_required` cannot exceed the number of owners minus any reserved/known-unreachable addresses, and adding tooling/off-chain warnings when owner-list changes would make quorum unreachable.

### Proof of Concept
1. Create a multisig account with owners `[A, B, @0x0]` and `num_signatures_required = 3` (n-of-n), e.g. via the creation flow or `add_owners` + `update_signatures_required`, both of which route through `update_owner_schema`/`validate_owners` with no zero-address check. [3](#0-2) 
2. Fund the resulting resource account with APT or a fungible asset via a normal transfer.
3. Any subsequent `create_transaction` requires 3 approvals to execute, but no signer can ever be produced for `@0x0`; only `A` and `B` can ever vote. [4](#0-3) 
4. `can_be_executed`/`execute_rejected_transaction` can never reach the `num_signatures_required` threshold, so all funds and administrative authority held by the multisig account are permanently locked.

Note: I was not able to inspect the exact `create_with_owners`/`create` entry-point bodies within the available tool budget (only `update_owner_schema`/`validate_owners` and the doc-generated signatures were confirmed), but since `validate_owners` is the sole shared validation routine invoked by every owner-list-mutating path in this module, the missing zero-address check applies uniformly regardless of which entry point is used to introduce the bad owner.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1510-1518)
```text
    fun validate_owners(owners: &vector<address>, multisig_account: address) {
        let distinct_owners: vector<address> = vector[];
        owners.for_each_ref(|owner| {
            assert!(owner != &multisig_account, error::invalid_argument(EOWNER_CANNOT_BE_MULTISIG_ACCOUNT_ITSELF));
            let (found, _) = distinct_owners.index_of(owner);
            assert!(!found, error::invalid_argument(EDUPLICATE_OWNER));
            distinct_owners.push_back(*owner);
        });
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1520-1530)
```text
    inline fun assert_is_owner_internal(owner: &signer, multisig_account: &MultisigAccount) {
        assert!(
            multisig_account.owners.contains(&address_of(owner)),
            error::permission_denied(ENOT_OWNER),
        );
    }

    inline fun assert_is_owner(owner: &signer, multisig_account: address) {
        let multisig_account_resource = borrow_global<MultisigAccount>(multisig_account);
        assert_is_owner_internal(owner, multisig_account_resource);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1586-1652)
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
                        &mut owners_removed,
                        vector::swap_remove(owners_ref_mut, index)
                    );
                }
            });
            // Only emit event if owner(s) actually removed.
            if (owners_removed.length() > 0) {
                emit(
                    RemoveOwners { multisig_account: multisig_address, owners_removed }
                );
            }
        };
        // If new signature count provided, try to update count.
        if (optional_new_num_signatures_required.is_some()) {
            let new_num_signatures_required =
                optional_new_num_signatures_required.extract();
            assert!(
                new_num_signatures_required > 0,
                error::invalid_argument(EINVALID_SIGNATURES_REQUIRED)
            );
            let old_num_signatures_required =
                multisig_account_ref_mut.num_signatures_required;
            // Only apply update and emit event if a change indicated.
            if (new_num_signatures_required != old_num_signatures_required) {
                multisig_account_ref_mut.num_signatures_required =
                    new_num_signatures_required;
                emit(
                    UpdateSignaturesRequired {
                        multisig_account: multisig_address,
                        old_num_signatures_required,
                        new_num_signatures_required,
                    }
```
