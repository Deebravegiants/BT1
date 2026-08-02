[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/configs/staking_config.move (L240-249)
```text
    fun calculate_and_save_latest_rewards_config(): StakingRewardsConfig acquires StakingRewardsConfig {
        let staking_rewards_config = borrow_global_mut<StakingRewardsConfig>(@aptos_framework);
        let current_time_in_secs = timestamp::now_seconds();
        assert!(
            current_time_in_secs >= staking_rewards_config.last_rewards_rate_period_start_in_secs,
            error::invalid_argument(EINVALID_LAST_REWARDS_RATE_PERIOD_START)
        );
        if (current_time_in_secs - staking_rewards_config.last_rewards_rate_period_start_in_secs < staking_rewards_config.rewards_rate_period_in_secs) {
            return *staking_rewards_config
        };
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L179-213)
```text
    /// Withdraw `amount` of fungible asset from the given account's primary store.
    public fun withdraw<T: key>(owner: &signer, metadata: Object<T>, amount: u64): FungibleAsset acquires DeriveRefPod {
        let store = ensure_primary_store_exists(signer::address_of(owner), metadata);
        // Check if the store object has been burnt or not. If so, unburn it first.
        may_be_unburn(owner, store);
        dispatchable_fungible_asset::withdraw(owner, store, amount)
    }

    /// Deposit fungible asset `fa` to the given account's primary store.
    public fun deposit(owner: address, fa: FungibleAsset) acquires DeriveRefPod {
        let metadata = fa.asset_metadata();
        let store = ensure_primary_store_exists(owner, metadata);
        dispatchable_fungible_asset::deposit(store, fa);
    }

    /// Deposit fungible asset `fa` to the given account's primary store using signer.
    public fun deposit_with_signer(owner: &signer, fa: FungibleAsset) acquires DeriveRefPod {
        let metadata = fa.asset_metadata();
        let store = ensure_primary_store_exists(signer::address_of(owner), metadata);
        dispatchable_fungible_asset::deposit(store, fa);
    }

    /// Transfer `amount` of fungible asset from sender's primary store to receiver's primary store.
    public entry fun transfer<T: key>(
        sender: &signer,
        metadata: Object<T>,
        recipient: address,
        amount: u64,
    ) acquires DeriveRefPod {
        let sender_store = ensure_primary_store_exists(signer::address_of(sender), metadata);
        // Check if the sender store object has been burnt or not. If so, unburn it first.
        may_be_unburn(sender, sender_store);
        let recipient_store = ensure_primary_store_exists(recipient, metadata);
        dispatchable_fungible_asset::transfer(sender, sender_store, recipient_store, amount);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L525-547)
```text
    /// Transfer to the destination address using a LinearTransferRef.
    public fun transfer_with_ref(self: LinearTransferRef, to: address) {
        assert!(!exists<Untransferable>(self.self), error::permission_denied(EOBJECT_NOT_TRANSFERRABLE));

        // Undo soft burn if present as we don't want the original owner to be able to reclaim by calling unburn later.
        if (exists<TombStone>(self.self)) {
            let TombStone { original_owner: _ } = move_from<TombStone>(self.self);
        };

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

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L514-542)
```text
    /// Calculate and update the latest amount of fees claimable by the given LP.
    public entry fun update_claimable_fees(lp: address, pool: Object<LiquidityPool>) acquires FeesAccounting {
        let fees_accounting = unchecked_mut_fees_accounting(&pool);
        let current_total_fees_1 = fees_accounting.total_fees_1;
        let current_total_fees_2 = fees_accounting.total_fees_2;
        let lp_balance = (primary_fungible_store::balance(lp, pool) as u128);
        let lp_token_total_supply = lp_token_supply(pool);
        // Calculate and update the amount of fees this LP token store is entitled to, taking into account the last
        // time they claimed.
        if (lp_balance > 0) {
            let last_total_fees_1 = *smart_table::borrow(&fees_accounting.total_fees_at_last_claim_1, lp);
            let last_total_fees_2 = *smart_table::borrow(&fees_accounting.total_fees_at_last_claim_2, lp);
            let delta_1 = current_total_fees_1 - last_total_fees_1;
            let delta_2 = current_total_fees_2 - last_total_fees_2;
            let claimable_1 = math128::mul_div(delta_1, lp_balance, lp_token_total_supply);
            let claimable_2 = math128::mul_div(delta_2, lp_balance, lp_token_total_supply);
            if (claimable_1 > 0) {
                let old_claimable_1 = smart_table::borrow_mut_with_default(&mut fees_accounting.claimable_1, lp, 0);
                *old_claimable_1 = *old_claimable_1 + claimable_1;
            };
            if (claimable_2 > 0) {
                let old_claimable_2 = smart_table::borrow_mut_with_default(&mut fees_accounting.claimable_2, lp, 0);
                *old_claimable_2 = *old_claimable_2 + claimable_2;
            };
        };

        smart_table::upsert(&mut fees_accounting.total_fees_at_last_claim_1, lp, current_total_fees_1);
        smart_table::upsert(&mut fees_accounting.total_fees_at_last_claim_2, lp, current_total_fees_2);
    }
```
