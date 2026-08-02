[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L370-448)
```text
    public(friend) fun register_dispatch_functions(
        constructor_ref: &ConstructorRef,
        withdraw_function: Option<FunctionInfo>,
        deposit_function: Option<FunctionInfo>,
        derived_balance_function: Option<FunctionInfo>
    ) {
        // Verify that caller type matches callee type so wrongly typed function cannot be registered.
        withdraw_function.for_each_ref(|withdraw_function| {
                let dispatcher_withdraw_function_info =
                    function_info::new_function_info_from_address(
                        @aptos_framework,
                        string::utf8(b"dispatchable_fungible_asset"),
                        string::utf8(b"dispatchable_withdraw")
                    );

                assert!(
                    function_info::check_dispatch_type_compatibility(
                        &dispatcher_withdraw_function_info,
                        withdraw_function
                    ),
                    error::invalid_argument(EWITHDRAW_FUNCTION_SIGNATURE_MISMATCH)
                );
            });

        deposit_function.for_each_ref(|deposit_function| {
                let dispatcher_deposit_function_info =
                    function_info::new_function_info_from_address(
                        @aptos_framework,
                        string::utf8(b"dispatchable_fungible_asset"),
                        string::utf8(b"dispatchable_deposit")
                    );
                // Verify that caller type matches callee type so wrongly typed function cannot be registered.
                assert!(
                    function_info::check_dispatch_type_compatibility(
                        &dispatcher_deposit_function_info,
                        deposit_function
                    ),
                    error::invalid_argument(EDEPOSIT_FUNCTION_SIGNATURE_MISMATCH)
                );
            });

        derived_balance_function.for_each_ref(|balance_function| {
                let dispatcher_derived_balance_function_info =
                    function_info::new_function_info_from_address(
                        @aptos_framework,
                        string::utf8(b"dispatchable_fungible_asset"),
                        string::utf8(b"dispatchable_derived_balance")
                    );
                // Verify that caller type matches callee type so wrongly typed function cannot be registered.
                assert!(
                    function_info::check_dispatch_type_compatibility(
                        &dispatcher_derived_balance_function_info,
                        balance_function
                    ),
                    error::invalid_argument(
                        EDERIVED_BALANCE_FUNCTION_SIGNATURE_MISMATCH
                    )
                );
            });
        register_dispatch_function_sanity_check(constructor_ref);
        assert!(
            !exists<DispatchFunctionStore>(
                constructor_ref.address_from_constructor_ref()
            ),
            error::already_exists(EALREADY_REGISTERED)
        );

        let store_obj = &constructor_ref.generate_signer();

        // Store the overload function hook.
        move_to<DispatchFunctionStore>(
            store_obj,
            DispatchFunctionStore {
                withdraw_function,
                deposit_function,
                derived_balance_function
            }
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1086-1106)
```text
    /// Withdraw `amount` of the fungible asset from the `store` ignoring `frozen`.
    public fun withdraw_with_ref<T: key>(
        self: &TransferRef, store: Object<T>, amount: u64
    ): FungibleAsset acquires FungibleStore, ConcurrentFungibleBalance {
        assert!(
            self.metadata == store_metadata(store),
            error::invalid_argument(ETRANSFER_REF_AND_STORE_MISMATCH)
        );
        unchecked_withdraw(store.object_address(), amount)
    }

    /// Deposit the fungible asset into the `store` ignoring `frozen`.
    public fun deposit_with_ref<T: key>(
        self: &TransferRef, store: Object<T>, fa: FungibleAsset
    ) acquires FungibleStore, ConcurrentFungibleBalance {
        assert!(
            self.metadata == fa.metadata,
            error::invalid_argument(ETRANSFER_REF_AND_FUNGIBLE_ASSET_MISMATCH)
        );
        unchecked_deposit(store.object_address(), fa);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1227-1252)
```text
    inline fun unchecked_deposit_with_no_events_inline(
        store_addr: address, fa: FungibleAsset
    ): u64 {
        let FungibleAsset { metadata, amount } = fa;
        assert!(
            exists<FungibleStore>(store_addr),
            error::not_found(EFUNGIBLE_STORE_EXISTENCE)
        );
        let store = borrow_global_mut<FungibleStore>(store_addr);
        assert!(
            metadata == store.metadata,
            error::invalid_argument(EFUNGIBLE_ASSET_AND_STORE_MISMATCH)
        );

        if (amount != 0) {
            if (store.balance == 0
                && concurrent_fungible_balance_exists_inline(store_addr)) {
                let balance_resource =
                    borrow_global_mut<ConcurrentFungibleBalance>(store_addr);
                balance_resource.balance.add(amount);
            } else {
                store.balance += amount;
            };
        };
        amount
    }
```

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L206-213)
```text
    inline fun borrow_transfer_ref<T: key>(metadata: Object<T>): &TransferRef {
        let metadata_addr = fungible_asset::store_metadata(metadata).object_address();
        assert!(
            exists<TransferRefStore>(metadata_addr),
            error::not_found(ESTORE_NOT_FOUND)
        );
        &borrow_global<TransferRefStore>(metadata_addr).transfer_ref
    }
```
