[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L72-119)
```text
    public fun withdraw<T: key>(
        owner: &signer,
        store: Object<T>,
        amount: u64,
    ): FungibleAsset acquires TransferRefStore {
        fungible_asset::withdraw_sanity_check(owner, store, false);
        let func_opt = fungible_asset::withdraw_dispatch_function(store);
        if (func_opt.is_some()) {
            let func = func_opt.borrow();
            if (features::is_function_value_dispatch_enabled()) {
                dispatch_withdraw_hook(store, amount, borrow_transfer_ref(store), func)
            } else {
                function_info::load_module_from_function(func);
                dispatchable_withdraw(
                    store,
                    amount,
                    borrow_transfer_ref(store),
                    func,
                )
            }
        } else {
            fungible_asset::unchecked_withdraw(store.object_address(), amount)
        }
    }

    /// Deposit `amount` of the fungible asset to `store`.
    ///
    /// The semantics of deposit will be governed by the function specified in DispatchFunctionStore.
    public fun deposit<T: key>(store: Object<T>, fa: FungibleAsset) acquires TransferRefStore {
        fungible_asset::deposit_sanity_check(store, false);
        let func_opt = fungible_asset::deposit_dispatch_function(store);
        if (func_opt.is_some()) {
            let func = func_opt.borrow();
            if (features::is_function_value_dispatch_enabled()) {
                dispatch_deposit_hook(store, fa, borrow_transfer_ref(store), func)
            } else {
                function_info::load_module_from_function(func);
                dispatchable_deposit(
                    store,
                    fa,
                    borrow_transfer_ref(store),
                    func
                )
            }
        } else {
            fungible_asset::unchecked_deposit(store.object_address(), fa)
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/confidential_asset/confidential_asset.move (L464-491)
```text
        // Note: Gets the "confidential asset pool" for this asset type, or sets it up if this asset type is veiled for the first time
        let pool_fa_store = ensure_pool_fa_store(asset_type);

        // Step 1: Transfer the asset from the user's account into the confidential asset pool.
        //
        // Note: Dispatchable transfers may deliver less than `amount` (e.g., due to fees for deflationary tokens), so
        // we measure the pool balance before & after to credit only what was actually received.
        let before = fungible_asset::balance(pool_fa_store);
        let depositor_fa_store = primary_fungible_store::primary_store(addr, asset_type);
        dispatchable_fungible_asset::transfer(depositor, depositor_fa_store, pool_fa_store, amount);

        // Step 2: "Mint" corresponding confidential assets for the depositor, and add them to their pending balance.
        let ca_store = borrow_confidential_store_mut(addr, asset_type);

        add_assign_pending(&mut ca_store.pending_balance, &new_pending_u64_no_randomness(amount));
        ca_store.transfers_received += 1;

        // Make sure the depositor has "room" in their pending balance for this deposit
        assert!(
            ca_store.transfers_received <= MAX_TRANSFERS_BEFORE_ROLLOVER,
            error::invalid_state(E_PENDING_BALANCE_MUST_BE_ROLLED_OVER)
        );

        event::emit(Deposited::V1 { addr, amount, asset_type, new_pending_balance: ca_store.pending_balance });

        // Abundantly-paranoid: Re-asserting dispatchable FA functionality that charges fees on withdraw/deposit was not invoked.
        assert!(amount == fungible_asset::balance(pool_fa_store) - before, error::invalid_argument(E_UNSAFE_DISPATCHABLE_FA));
    }
```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L1261-1301)
```text
        new_balance = with_rewards(new_balance) + INITIAL_BALANCE;

        // Second round of commission request/withdrawal.
        let expected_commission_2 =
            (new_balance - last_recorded_principal(staker_address, operator_address)) / 10;
        new_balance -= expected_commission_2;
        request_commission(operator, staker_address, operator_address);
        assert_distribution(
            staker_address,
            operator_address,
            operator_address,
            expected_commission_2
        );
        assert!(
            last_recorded_principal(staker_address, operator_address) == new_balance, 0
        );
        stake::fast_forward_to_unlock(pool_address);
        expected_commission_2 = with_rewards(expected_commission_2);
        distribute(staker_address, operator_address);
        operator_balance = coin::balance<AptosCoin>(operator_address);
        expected_operator_balance += expected_commission_2;
        assert!(operator_balance == expected_operator_balance, operator_balance);
        assert_no_pending_distributions(staker_address, operator_address);
        new_balance = with_rewards(new_balance);

        // New rounds of rewards.
        stake::fast_forward_to_unlock(pool_address);
        new_balance = with_rewards(new_balance);

        // Staker withdraws all stake, which should also request commission distribution.
        let unpaid_commission =
            (new_balance - last_recorded_principal(staker_address, operator_address)) / 10;
        unlock_stake(staker, operator_address, new_balance);
        stake::assert_stake_pool(pool_address, 0, 0, 0, new_balance);
        assert_distribution(
            staker_address,
            operator_address,
            operator_address,
            unpaid_commission
        );
        let withdrawn_amount = new_balance - unpaid_commission;
```
