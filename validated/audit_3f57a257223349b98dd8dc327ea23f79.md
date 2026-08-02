[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L493-512)
```text
    /// Disable direct transfer, transfers can only be triggered via a TransferRef
    public fun disable_ungated_transfer(self: &TransferRef) {
        let object = borrow_global_mut<ObjectCore>(self.self);
        object.allow_ungated_transfer = false;
    }

    /// Prevent moving of the object
    public fun set_untransferable(self: &ConstructorRef) {
        let object = borrow_global_mut<ObjectCore>(self.self);
        object.allow_ungated_transfer = false;
        let object_signer = self.generate_signer();
        move_to(&object_signer, Untransferable {});
    }

    /// Enable direct transfer.
    public fun enable_ungated_transfer(self: &TransferRef) {
        assert!(!exists<Untransferable>(self.self), error::permission_denied(EOBJECT_NOT_TRANSFERRABLE));
        let object = borrow_global_mut<ObjectCore>(self.self);
        object.allow_ungated_transfer = true;
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L534-547)
```text
        let object = borrow_global_mut<ObjectCore>(self.self);
        assert!(
            object.owner == self.owner,
            error::permission_denied(ENOT_OBJECT_OWNER),
        );
        event::emit(
            Transfer {
                object: self.self,
                from: object.owner,
                to,
            },
        );
        object.owner = to;
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1034-1052)
```text
    /// Enable/disable a store's ability to do direct transfers of the fungible asset.
    public fun set_frozen_flag<T: key>(
        self: &TransferRef, store: Object<T>, frozen: bool
    ) acquires FungibleStore {
        assert!(
            self.metadata == store_metadata(store),
            error::invalid_argument(ETRANSFER_REF_AND_STORE_MISMATCH)
        );
        set_frozen_flag_internal(store, frozen)
    }

    public(friend) fun set_frozen_flag_internal<T: key>(
        store: Object<T>, frozen: bool
    ) acquires FungibleStore {
        let store_addr = store.object_address();
        borrow_global_mut<FungibleStore>(store_addr).frozen = frozen;

        event::emit(Frozen { store: store_addr, frozen });
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L991-1005)
```text
    /// Add new owners to the multisig account. This can only be invoked by the multisig account itself, through the
    /// proposal flow.
    ///
    /// Note that this function is not public so it can only be invoked directly instead of via a module or script. This
    /// ensures that a multisig transaction cannot lead to another module obtaining the multisig signer and using it to
    /// maliciously alter the owners list.
    entry fun add_owners(
        multisig_account: &signer, new_owners: vector<address>) {
        update_owner_schema(
            address_of(multisig_account),
            new_owners,
            vector[],
            option::none()
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1034-1042)
```text
    entry fun remove_owners(
        multisig_account: &signer, owners_to_remove: vector<address>) {
        update_owner_schema(
            address_of(multisig_account),
            vector[],
            owners_to_remove,
            option::none()
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1663-1681)
```text
        // If a timelock is configured, adjust and validate the override threshold
        // after owner/threshold changes.
        if (exists<MultisigAccountTimeLock>(multisig_address)) {
            let timelock = &mut MultisigAccountTimeLock[multisig_address];
            // If override threshold exceeds the new owner count, clamp it down and emit an event
            // so off-chain monitors observe the security-relevant mutation.
            if (timelock.override_threshold.is_some() && timelock.override_threshold.borrow() > &num_owners) {
                timelock.override_threshold = option::some(num_owners);
                emit(TimelockUpdated {
                    multisig_account: multisig_address,
                    timelock_period: timelock.timelock_period,
                    override_threshold: timelock.override_threshold,
                });
            };
            // Override threshold must still be greater than num_signatures_required.
            assert!(
                timelock.override_threshold.is_none() || timelock.override_threshold.borrow() > &multisig_account_ref_mut.num_signatures_required,
                error::invalid_state(EINVALID_TIMELOCK_OVERRIDE_THRESHOLD)
            );
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
