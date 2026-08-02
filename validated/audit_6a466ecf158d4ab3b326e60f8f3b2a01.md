[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** aptos-move/framework/aptos-stdlib/sources/pool_u64.move (L128-145)
```text
    /// Update `self`'s total balance of coins.
    public fun update_total_coins(self: &mut Pool, new_total_coins: u64) {
        self.total_coins = new_total_coins;
    }

    /// Allow an existing or new shareholder to add their coins to the pool in exchange for new shares.
    public fun buy_in(self: &mut Pool, shareholder: address, coins_amount: u64): u64 {
        if (coins_amount == 0) return 0;

        let new_shares = self.amount_to_shares(coins_amount);
        assert!(MAX_U64 - self.total_coins >= coins_amount, error::invalid_argument(EPOOL_TOTAL_COINS_OVERFLOW));
        assert!(MAX_U64 - self.total_shares >= new_shares, error::invalid_argument(EPOOL_TOTAL_COINS_OVERFLOW));

        self.total_coins += coins_amount;
        self.total_shares += new_shares;
        self.add_shares(shareholder, new_shares);
        new_shares
    }
```

**File:** aptos-move/framework/aptos-stdlib/sources/pool_u64.move (L262-264)
```text
    public fun multiply_then_divide(self: &Pool, x: u64, y: u64, z: u64): u64 {
        math64::mul_div(x, y, z)
    }
```

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L217-237)
```text
    /// This should only be called by system modules to increase the shares of a claimer for the current epoch.
    public(friend) fun increase_allocation(
        claimer: address,
        rewards_pool: Object<RewardsPool>,
        amount: u64,
    ) acquires RewardsPool {
        let epoch_rewards = &mut unchecked_mut_rewards_pool_data(&rewards_pool).epoch_rewards;
        let current_epoch_rewards = epoch_rewards_or_default(epoch_rewards, epoch::now());
        pool_u64::buy_in(&mut current_epoch_rewards.claimer_pool, claimer, amount);
    }

    /// This should only be called by system modules to decrease the shares of a claimer for the current epoch.
    public(friend) fun decrease_allocation(
        claimer: address,
        rewards_pool: Object<RewardsPool>,
        amount: u64,
    ) acquires RewardsPool {
        let epoch_rewards = &mut unchecked_mut_rewards_pool_data(&rewards_pool).epoch_rewards;
        let current_epoch_rewards = epoch_rewards_or_default(epoch_rewards, epoch::now());
        pool_u64::redeem_shares(&mut current_epoch_rewards.claimer_pool, claimer, (amount as u128));
    }
```
