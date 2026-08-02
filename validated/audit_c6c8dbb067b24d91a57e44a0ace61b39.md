[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/resource_account.move (L83-90)
```text
    /// Creates a new resource account and rotates the authentication key to either
    /// the optional auth key if it is non-empty (though auth keys are 32-bytes)
    /// or the source accounts current auth key.
    public entry fun create_resource_account(
        origin: &signer, seed: vector<u8>, optional_auth_key: vector<u8>
    ) acquires Container {
        let (resource, resource_signer_cap) =
            account::create_resource_account(origin, seed);
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L770-821)
```text
    /// Terminate the vesting contract and send all funds back to the withdrawal address.
    public entry fun terminate_vesting_contract(admin: &signer, contract_address: address) acquires VestingContract {
        assert_active_vesting_contract(contract_address);

        // Distribute all withdrawable coins, which should have been from previous rewards withdrawal or vest.
        distribute(contract_address);

        let vesting_contract = borrow_global_mut<VestingContract>(contract_address);
        verify_admin(admin, vesting_contract);
        let (active_stake, _, pending_active_stake, _) = stake::get_stake(vesting_contract.staking.pool_address);
        assert!(pending_active_stake == 0, error::invalid_state(EPENDING_STAKE_FOUND));

        // Unlock all remaining active stake.
        vesting_contract.state = VESTING_POOL_TERMINATED;
        vesting_contract.remaining_grant = 0;
        unlock_stake(vesting_contract, active_stake);

        emit(
            Terminate {
                admin: vesting_contract.admin,
                vesting_contract_address: contract_address,
            },
        );
    }

    /// Withdraw all funds to the preset vesting contract's withdrawal address. This can only be called if the contract
    /// has already been terminated.
    public entry fun admin_withdraw(admin: &signer, contract_address: address) acquires VestingContract {
        let vesting_contract = borrow_global<VestingContract>(contract_address);
        assert!(
            vesting_contract.state == VESTING_POOL_TERMINATED,
            error::invalid_state(EVESTING_CONTRACT_STILL_ACTIVE)
        );

        let vesting_contract = borrow_global_mut<VestingContract>(contract_address);
        verify_admin(admin, vesting_contract);
        let coins = withdraw_stake(vesting_contract, contract_address);
        let amount = coin::value(&coins);
        if (amount == 0) {
            coin::destroy_zero(coins);
            return
        };
        aptos_account::deposit_coins(vesting_contract.withdrawal_address, coins);

        emit(
            AdminWithdraw {
                admin: vesting_contract.admin,
                vesting_contract_address: contract_address,
                amount,
            },
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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1656-1681)
```text
        // Verify number of owners.
        let num_owners = multisig_account_ref_mut.owners.length();
        assert!(
            num_owners >= multisig_account_ref_mut.num_signatures_required,
            error::invalid_state(ENOT_ENOUGH_OWNERS)
        );

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

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L3103-3118)
```text
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
