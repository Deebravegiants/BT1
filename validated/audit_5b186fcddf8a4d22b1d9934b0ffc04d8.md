No vulnerability found for this question.

The premise doesn't match the actual codebase. `FungibleStore` resources are never held in a `vector`; each store is created via `move_to(store_obj, FungibleStore { ... })` under its own uniquely-derived object address in `create_store` [1](#0-0) . Ownership and lookup of a store are determined by that object's address (via `Object<FungibleStore>` / `ConstructorRef`/`DeriveRef` derived addresses), not by positional/vector indexing [2](#0-1) .

A global search across the repo confirms `vector::last_mut` is not used anywhere in custody-related logic — it's only defined in `move-stdlib/sources/vector.move` [3](#0-2)  and has no callers in `fungible_asset.move`, `primary_fungible_store.move`, or any other Move module dealing with `FungibleStore` creation. Since there is no vector-of-stores construct, no `swap_remove`-based reordering of a caller's own store, and no `last_mut`-based store initialization pattern in the codebase, the described attack path against `balance`/`owner` corruption does not exist in this custody logic.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L894-917)
```text
    public fun create_store<T: key>(
        constructor_ref: &ConstructorRef, metadata: Object<T>
    ): Object<FungibleStore> {
        let store_obj = &constructor_ref.generate_signer();
        move_to(
            store_obj,
            FungibleStore { metadata: metadata.convert(), balance: 0, frozen: false }
        );

        if (is_untransferable(metadata)) {
            constructor_ref.set_untransferable();
        };

        if (default_to_concurrent_fungible_balance()) {
            move_to(
                store_obj,
                ConcurrentFungibleBalance {
                    balance: aggregator_v2::create_unbounded_aggregator()
                }
            );
        };

        constructor_ref.object_from_constructor_ref<FungibleStore>()
    }
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L75-89)
```text
    /// Create a primary store object to hold fungible asset for the given address.
    public fun create_primary_store<T: key>(
        owner_addr: address,
        metadata: Object<T>,
    ): Object<FungibleStore> acquires DeriveRefPod {
        let metadata_addr = metadata.object_address();
        object::address_to_object<Metadata>(metadata_addr);
        let derive_ref = &borrow_global<DeriveRefPod>(metadata_addr).metadata_derive_ref;
        let constructor_ref = &object::create_user_derived_object(owner_addr, derive_ref);
        // Disable ungated transfer as deterministic stores shouldn't be transferrable.
        let transfer_ref = &constructor_ref.generate_transfer_ref();
        transfer_ref.disable_ungated_transfer();

        fungible_asset::create_store(constructor_ref, metadata)
    }
```

**File:** aptos-move/framework/move-stdlib/sources/vector.move (L106-111)
```text
    /// Returns a mutable reference to the last element in the vector, or aborts if the vector is empty.
    public fun last_mut<Element>(self: &mut vector<Element>): &mut Element {
        assert!(self.length() > 0, EINDEX_OUT_OF_BOUNDS);
        let len = self.length();
        &mut self[len - 1]
    }
```
