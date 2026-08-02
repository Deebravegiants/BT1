[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1281-1309)
```text
    inline fun unchecked_withdraw_with_no_events(
        store_addr: address, amount: u64
    ): FungibleAsset {
        assert!(
            exists<FungibleStore>(store_addr),
            error::not_found(EFUNGIBLE_STORE_EXISTENCE)
        );

        let store = borrow_global_mut<FungibleStore>(store_addr);
        let metadata = store.metadata;
        if (amount != 0) {
            if (store.balance == 0
                && concurrent_fungible_balance_exists_inline(store_addr)) {
                let balance_resource =
                    borrow_global_mut<ConcurrentFungibleBalance>(store_addr);
                assert!(
                    balance_resource.balance.try_sub(amount),
                    error::invalid_argument(EINSUFFICIENT_BALANCE)
                );
            } else {
                assert!(
                    store.balance >= amount,
                    error::invalid_argument(EINSUFFICIENT_BALANCE)
                );
                store.balance -= amount;
            };
        };
        FungibleAsset { metadata, amount }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1337-1363)
```text
    /// Decrease the supply of a fungible asset by burning.
    fun decrease_supply<T: key>(metadata: &Object<T>, amount: u64) acquires Supply, ConcurrentSupply {
        if (amount == 0) { return };
        let metadata_address = metadata.object_address();

        if (exists<ConcurrentSupply>(metadata_address)) {
            let supply = borrow_global_mut<ConcurrentSupply>(metadata_address);

            assert!(
                supply.current.try_sub(amount as u128),
                error::out_of_range(ESUPPLY_UNDERFLOW)
            );
        } else if (exists<Supply>(metadata_address)) {
            assert!(
                exists<Supply>(metadata_address),
                error::not_found(ESUPPLY_NOT_FOUND)
            );
            let supply = borrow_global_mut<Supply>(metadata_address);
            assert!(
                supply.current >= (amount as u128),
                error::invalid_state(ESUPPLY_UNDERFLOW)
            );
            supply.current -= (amount as u128);
        } else {
            assert!(false, error::not_found(ESUPPLY_NOT_FOUND));
        }
    }
```

**File:** aptos-move/move-examples/fungible_asset/managed_fungible_asset/sources/managed_fungible_asset.move (L240-261)
```text
    public fun withdraw(
        admin: &signer,
        asset: Object<Metadata>,
        stores: vector<Object<FungibleStore>>,
        amounts: vector<u64>
    ): FungibleAsset acquires ManagingRefs {
        let length = vector::length(&stores);
        assert!(length == vector::length(&amounts), error::invalid_argument(ERR_VECTORS_LENGTH_MISMATCH));
        let transfer_ref = authorized_borrow_transfer_ref(admin, asset);
        let i = 0;
        let sum = fungible_asset::zero(asset);
        while (i < length) {
            let fa = fungible_asset::withdraw_with_ref(
                transfer_ref,
                *vector::borrow(&stores, i),
                *vector::borrow(&amounts, i)
            );
            fungible_asset::merge(&mut sum, fa);
            i = i + 1;
        };
        sum
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
