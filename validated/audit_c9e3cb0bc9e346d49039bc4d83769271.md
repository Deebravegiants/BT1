[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L572-594)
```text
    public fun transfer_raw(
        owner: &signer,
        object: address,
        to: address,
    ) {
        let owner_address = signer::address_of(owner);
        verify_ungated_and_descendant(owner_address, object);
        transfer_raw_inner(object, to);
    }

    inline fun transfer_raw_inner(object: address, to: address) {
        let object_core = borrow_global_mut<ObjectCore>(object);
        if (object_core.owner != to) {
            event::emit(
                Transfer {
                    object,
                    from: object_core.owner,
                    to,
                },
            );
            object_core.owner = to;
        };
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1591-1650)
```text
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
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3064-3118)
```text
    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_remove_timelock_allows_immediate_execution(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure then remove timelock.
        upsert_timelock(multisig_signer, 3600, option::some(3));
        remove_timelock(multisig_signer);

        // Create and approve a transaction.
        create_transaction(owner_1, multisig_account, PAYLOAD);
        approve_transaction(owner_2, multisig_account, 1);

        // No timelock — immediately executable.
        assert!(can_be_executed(multisig_account, 1), 0);
        successful_transaction_execution_cleanup(address_of(owner_1), multisig_account, vector[]);
    }

    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    fun test_owner_removal_clamps_override_threshold(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure timelock with override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));
        assert!(timelock_override_threshold(multisig_account) == option::some(3), 0);

        // Remove one owner (3 -> 2 owners). Override threshold should be clamped to 2.
        // Signature threshold is 2, so we need to lower it first to allow removing an owner
        // while keeping override_threshold > num_signatures_required.
        update_signatures_required(multisig_signer, 1);
        remove_owner(multisig_signer, address_of(owner_3));
        assert!(timelock_override_threshold(multisig_account) == option::some(2), 1);
    }

    #[test(owner_1 = @0x123, owner_2 = @0x124, owner_3 = @0x125)]
    #[expected_failure(abort_code = 0x30016, location = Self)]
    fun test_owner_removal_fails_if_override_becomes_invalid(
        owner_1: &signer, owner_2: &signer, owner_3: &signer
    ) {
        let multisig_account = setup_timelock_multisig(owner_1, owner_2, owner_3);
        let multisig_signer = &create_signer(multisig_account);

        // Configure timelock with override at 3-of-3.
        upsert_timelock(multisig_signer, 3600, option::some(3));

        // Remove one owner: 3 -> 2 owners, override clamped to 2.
        // But num_signatures_required is also 2, so override (2) is NOT > threshold (2).
        // This should fail.
        remove_owner(multisig_signer, address_of(owner_3));
    }
```

**File:** aptos-move/framework/aptos-framework/sources/resource_account.move (L165-196)
```text
    /// When called by the resource account, it will retrieve the capability associated with that
    /// account and rotate the account's auth key to 0x0 making the account inaccessible without
    /// the SignerCapability.
    public fun retrieve_resource_account_cap(
        resource: &signer, source_addr: address
    ): account::SignerCapability acquires Container {
        assert!(
            exists<Container>(source_addr),
            error::not_found(ECONTAINER_NOT_PUBLISHED)
        );

        let resource_addr = signer::address_of(resource);
        let (resource_signer_cap, empty_container) = {
            let container = borrow_global_mut<Container>(source_addr);
            assert!(
                container.store.contains_key(&resource_addr),
                error::invalid_argument(EUNAUTHORIZED_NOT_OWNER)
            );
            let (_resource_addr, signer_cap) =
                container.store.remove(&resource_addr);
            (signer_cap, container.store.length() == 0)
        };

        if (empty_container) {
            let container = move_from<Container>(source_addr);
            let Container { store } = container;
            store.destroy_empty();
        };

        account::rotate_authentication_key_internal(resource, ZERO_AUTH_KEY);
        resource_signer_cap
    }
```
