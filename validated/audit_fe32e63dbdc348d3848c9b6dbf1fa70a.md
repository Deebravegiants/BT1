Confirmed: `shares_to_amount_with_total_coins` returns 0 when `total_shares == 0` [1](#0-0) , which validates the custody analog below.

### Title
Rewards deposited into a closed/empty-share epoch are permanently unclaimable in `rewards_pool` example module - (File: aptos-move/move-examples/rewards_pool/sources/rewards_pool.move)

### Summary
The `rewards_pool` example module (an Aptos analog for the Velodrome `Bribe` contract pattern) lets `add_rewards` deposit fungible assets into the reward store for **any** epoch, including epochs whose `claimer_pool` already has zero total shares (either because no one ever staked in that epoch, or because every claimer already claimed and had their shares redeemed to zero). Because `pool_u64_unbound::shares_to_amount_with_total_coins` returns `0` whenever `total_shares == 0`, any reward token deposited for such an epoch becomes permanently unclaimable by anyone, mirroring the "bribe rewards not collected are lost forever" bug class from the external report.

### Finding Description
`add_rewards` takes an arbitrary `epoch` parameter and unconditionally transfers the fungible asset into `reward_store.store`, then bumps `total_amounts` for that epoch: [2](#0-1) 

There is no check that the target epoch's `claimer_pool` currently has non-zero `total_shares`. If the epoch doesn't exist yet, `epoch_rewards_or_default` creates a brand-new, empty `pool_u64::create()` pool with `total_shares = 0`: [3](#0-2) 

Later, when computing a claimer's entitlement, `rewards()` calls `pool_u64::shares_to_amount_with_total_coins`, whose underlying implementation explicitly returns `0` whenever `total_shares == 0`: [1](#0-0) [4](#0-3) 

Two concrete paths produce a `total_shares == 0` epoch that still holds real custodied assets:
1. Someone calls `add_rewards(pool, assets, epoch)` for an epoch in which `increase_allocation` was never called (no claimer ever bought shares for that epoch) — `epoch_rewards_or_default` creates a fresh empty pool.
2. `add_rewards` is called for a past epoch **after** all claimers have already called `claim_rewards`, since `claim_rewards` redeems 100% of each claimer's shares back to zero at the end of the call: [5](#0-4) 

In both cases the fungible asset is physically deposited into `RewardStore.store` (an object-held fungible store) via `fungible_asset::deposit`, so the custodied value is real and on-chain, but no claimer can ever redeem shares to extract it — `total_amounts` for the token is permanently non-zero while every claimer's computed reward for that token/epoch is `0`. There is also no admin/sweep function to recover stranded balances from `RewardStore`; the module never exposes the `store_extend_ref` for anything other than internal claim withdrawal.

### Impact Explanation
This is a permanent, non-recoverable loss of object-held fungible-asset value: deposited reward tokens sit in the `RewardStore`'s `FungibleStore` object forever with no code path capable of withdrawing them (claimers always compute `0` shares of the total, and there's no owner/admin rescue function). This satisfies the "Permanent lock or non-recoverable loss of object-held ... value" custody-impact gate. Severity is bounded by the fact that this is a `move-examples` reference module, not deployed framework code with live mainnet value by default — but any protocol adopting this example pattern verbatim inherits the bug, and reward-pool integrators are the stated intended reuse path (the module doc explicitly says "this module is designed to be integrated into a complete system").

### Likelihood Explanation
Likelihood is moderate-to-high in real deployments of this pattern: any briber/funder who adds rewards slightly early for a not-yet-populated epoch, or any second/late funder who tops up an epoch after all current claimers have already exited (a very plausible operational sequence — e.g., a DAO treasury adding a bonus reward after the epoch's participants already claimed), triggers the loss without any privileged or malicious actor required. No special permissions are needed to call `add_rewards`.

### Recommendation
- Require `total_shares(epoch_rewards.claimer_pool) > 0` before allowing `add_rewards` for a given epoch, or auto-forward/roll-over rewards deposited into a zero-share epoch to the next epoch with shares (as the real Solidly `Bribe` design does).
- Alternatively, add an explicit rescue/sweep entry function (gated to the pool creator or DAO) that can reclaim `total_amounts` value from any epoch whose `claimer_pool.total_shares() == 0`, using the already-stored `store_extend_ref`.
- Document/enforce in `add_rewards` that epoch must be currently "open" (has active allocations) rather than accepting an arbitrary `epoch: u64`.

### Proof of Concept
1. Create a rewards pool with one reward token via `rewards_pool::create`.
2. Do **not** call `increase_allocation` for `epoch = N` (or, alternatively, have claimer A call `increase_allocation` for epoch N, then after the epoch ends call `claim_rewards(A, pool, N)`, which redeems A's shares to 0 via `pool_u64::redeem_shares` at line 183).
3. Call `add_rewards(pool, vector[fa_of_amount_X], N)`. The FA of amount X is deposited into `RewardStore.store` and `total_amounts[token] = X` for epoch N.
4. For any address (existing or new) call `claimable_rewards(addr, pool, N)` — the returned amount is `0` for every address, since `pool_u64::shares(claimer_pool, addr) == 0` and `total_shares == 0`, and `shares_to_amount_with_total_coins` returns `0` unconditionally in that state (lines 233–243 of `pool_u64_unbound.move`).
5. No entry point in `rewards_pool.move` allows extracting the `X` amount from `RewardStore.store` — the value is permanently stranded, matching the external report's "bribe rewards not collected are lost forever" impact.

### Citations

**File:** aptos-move/framework/aptos-stdlib/sources/pool_u64_unbound.move (L233-243)
```text
    public fun shares_to_amount_with_total_coins(self: &Pool, shares: u128, total_coins: u64): u64 {
        // No shares or coins yet so shares are worthless.
        if (self.total_coins == 0 || self.total_shares == 0) {
            0
        } else {
            // Shares price = total_coins / total existing shares.
            // Shares worth = shares * shares price = shares * total_coins / total existing shares.
            // We rearrange the calc and do multiplication first to avoid rounding errors.
            (self.multiply_then_divide(shares, total_coins as u128, self.total_shares) as u64)
        }
    }
```

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L179-184)
```text
        // Remove the claimer's allocation in the epoch as they have now claimed all rewards for that epoch.
        let epoch_rewards = smart_table::borrow_mut(&mut rewards_data.epoch_rewards, epoch);
        let all_shares = pool_u64::shares(&epoch_rewards.claimer_pool, claimer_addr);
        if (all_shares > 0) {
            pool_u64::redeem_shares(&mut epoch_rewards.claimer_pool, claimer_addr, all_shares);
        };
```

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L190-215)
```text
    public fun add_rewards(
        rewards_pool: Object<RewardsPool>,
        fungible_assets: vector<FungibleAsset>,
        epoch: u64,
    ) acquires RewardsPool {
        let rewards_data = unchecked_mut_rewards_pool_data(&rewards_pool);
        let reward_stores = &rewards_data.reward_stores;
        vector::for_each(fungible_assets, |fa| {
            let amount = fungible_asset::amount(&fa);
            let reward_token = fungible_asset::asset_metadata(&fa);
            assert!(simple_map::contains_key(reward_stores, &reward_token), EREWARD_TOKEN_NOT_SUPPORTED);

            // Deposit the rewards into the corresponding store.
            let reward_store = simple_map::borrow(reward_stores, &reward_token);
            fungible_asset::deposit(reward_store.store, fa);

            // Update total amount of rewards for this token for this epoch.
            let total_amounts = &mut epoch_rewards_or_default(&mut rewards_data.epoch_rewards, epoch).total_amounts;
            if (simple_map::contains_key(total_amounts, &reward_token)) {
                let current_amount = simple_map::borrow_mut(total_amounts, &reward_token);
                *current_amount = *current_amount + amount;
            } else {
                simple_map::add(total_amounts, reward_token, amount);
            };
        });
    }
```

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L239-259)
```text
    fun rewards(
        claimer: address,
        rewards_pool_data: &RewardsPool,
        reward_token: Object<Metadata>,
        epoch: u64,
    ): u64 {
        // No rewards (in any tokens) have been added for this epoch.
        if (!smart_table::contains(&rewards_pool_data.epoch_rewards, epoch)) {
            return 0
        };
        let epoch_rewards = smart_table::borrow(&rewards_pool_data.epoch_rewards, epoch);
        // No rewards have been added for this reward token.
        if (!simple_map::contains_key(&epoch_rewards.total_amounts, &reward_token)) {
            return 0
        };

        // Return the claimer's shares of the current total rewards for the epoch.
        let total_token_rewards = *simple_map::borrow(&epoch_rewards.total_amounts, &reward_token);
        let claimer_shares = pool_u64::shares(&epoch_rewards.claimer_pool, claimer);
        pool_u64::shares_to_amount_with_total_coins(&epoch_rewards.claimer_pool, claimer_shares, total_token_rewards)
    }
```

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L267-278)
```text
    inline fun epoch_rewards_or_default(
        epoch_rewards: &mut SmartTable<u64, EpochRewards>,
        epoch: u64,
    ): &mut EpochRewards acquires RewardsPool {
        if (!smart_table::contains(epoch_rewards, epoch)) {
            smart_table::add(epoch_rewards, epoch, EpochRewards {
                total_amounts: simple_map::new(),
                claimer_pool: pool_u64::create(),
            });
        };
        smart_table::borrow_mut(epoch_rewards, epoch)
    }
```
