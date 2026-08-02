### Title
Rewards Permanently Stuck In `RewardsPool` When `add_rewards` Targets An Epoch With Zero Claimer Shares - (File: `aptos-move/move-examples/rewards_pool/sources/rewards_pool.move`)

### Summary
`rewards_pool::add_rewards` lets **anyone** deposit fungible-asset rewards into an arbitrary, caller-chosen `epoch`, while claimer shares for that epoch are only ever recorded by privileged (`friend`) callers via `increase_allocation`/`decrease_allocation`, which always target `epoch::now()`. If rewards are deposited for an epoch whose `claimer_pool` has zero (or insufficient) total shares — e.g. epoch 0 before any allocation ever happened, a future epoch, or any epoch where all claimers have already fully redeemed their shares — the deposited value becomes permanently unclaimable, exactly mirroring the Velodrome `Bribe` bug where value is deposited into a period that no claimant can ever draw from.

### Finding Description
`add_rewards` is a public, unrestricted function that deposits `FungibleAsset`s into the `RewardStore` for a caller-supplied `epoch` and increments `total_amounts` for that epoch, independent of whether any claimer shares exist for that epoch: [1](#0-0) 

Claimer shares, however, are only added by `friend` modules through `increase_allocation`/`decrease_allocation`, and critically these always operate on `epoch::now()`, never on an arbitrary epoch: [2](#0-1) 

When a claimer later tries to claim for a given epoch, the payout is computed via `pool_u64_unbound::shares_to_amount_with_total_coins`, which returns `0` whenever `total_shares == 0` for that pool, regardless of how many tokens (`total_amounts`) were deposited: [3](#0-2) [4](#0-3) 

Consequently, any epoch for which `add_rewards` is called before (or without) a matching `increase_allocation` call for that same epoch permanently locks the deposited fungible assets in the `RewardStore` object. There is no rescue path: `claim_rewards`/`claim_rewards_entry` only pay out proportional to `claimer_shares / total_shares`, and there is no admin/owner withdrawal function in the module — the `RewardsPool` object explicitly discards its `ExtendRef` for the pool itself (comment: "there would be no way to obtain its signer") and only keeps `store_extend_ref` for the internal `RewardStore`, which is only used inside `claim_rewards`: [5](#0-4) 

This is the same custody invariant break as the external report: value custodied for a distribution period is orphaned because the reward-accrual window and the entitlement/share-accrual window are not required to be synchronized, and once shares for an epoch don't exist (or are all redeemed to zero), the epoch's `EpochRewards.total_amounts` can never be reduced to zero via legitimate claims — the FA sits in the object-owned `FungibleStore` forever.

### Impact Explanation
Any fungible-asset value sent into the rewards pool for an epoch lacking claimer shares is a **permanent, non-recoverable loss of object-held value** — meeting the custody impact gate's "permanent lock or non-recoverable loss of object-held ... value." Because `add_rewards` is a fully public entry point callable by anyone (unlike `increase_allocation`/`decrease_allocation` which are `friend`-gated), any integrator or user calling it with a mistimed/mismatched `epoch` argument (e.g. epoch 0, a future epoch not yet reached, or an epoch that has already been fully redeemed by all shareholders) will have their deposit permanently stranded with no admin recovery mechanism.

### Likelihood Explanation
This is a `move-examples` template module (`aptos-move/move-examples/rewards_pool`), not a core mainnet framework module, so it is not directly deployed as part of the Aptos framework itself. It is intended to be copied/integrated by third-party protocols. The likelihood of triggering it is high once deployed, since `add_rewards` takes an arbitrary `epoch: u64` parameter with no validation against `epoch::now()` or against whether the target epoch's `claimer_pool` has any shares, and no integration guardrail prevents rewards from being added for an epoch before allocation begins (directly analogous to the "permissionless bribe/gauge deployment" concern the original judge flagged as making the bug apply to every new instance).

### Recommendation
- Restrict `add_rewards` to only accept the current epoch (`epoch::now()`) or validate that `epoch >= epoch::now()`... more importantly, ensure the target epoch already has (or will have) non-zero claimer shares before allowing deposits, or auto-carry-forward/roll unclaimed epoch rewards into a future epoch's pool instead of leaving them permanently orphaned.
- Add a recovery/admin path (e.g., an `ExtendRef`-gated sweep function) that allows unclaimed rewards for epochs with zero total shares to be reclaimed or redirected, mirroring the "consider aligning bribe period with reward emission" mitigation from the original report.
- Emit and monitor an event when `add_rewards` targets an epoch with a `claimer_pool.total_shares() == 0`, and consider reverting in that case to force depositors to only fund matching epochs.

### Proof of Concept
1. Deploy a `RewardsPool` via `create`/`create_entry` for reward token `T`.
2. Before any `friend` module ever calls `increase_allocation` for the current epoch (i.e., `claimer_pool` for `epoch::now()` has `total_shares == 0`), call `add_rewards(rewards_pool, vector[fa_of_T], epoch::now())`. This succeeds and deposits `amount` of `T` into the `RewardStore`, incrementing `EpochRewards.total_amounts` for that epoch — per `add_rewards` at lines 189–215.
3. Later, once claimers do get shares allocated, they only get shares for the epoch **the friend module currently calls `increase_allocation` on** (i.e., whatever `epoch::now()` is at call time — lines 217–226), never retroactively for the earlier epoch where rewards were deposited.
4. Any claimer calling `claim_rewards(claimer, rewards_pool, <that earlier epoch>)` computes `rewards()` via `shares_to_amount_with_total_coins` with `total_shares == 0` for that epoch's `claimer_pool`, returning `0` for every claimer regardless of the non-zero `total_amounts` — per pool_u64_unbound lines 231–243 and rewards_pool.move lines 239–259.
5. `total_amounts[T]` for that epoch is never decremented (no `claim_rewards` call reduces it since claimable amount is always `0`), and the module has no owner/admin withdrawal function, so the deposited `T` tokens remain permanently stuck in the `RewardStore` object.

### Citations

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L64-89)
```text
    /// Create a new rewards pool with the given reward tokens (fungible assets only)
    public fun create(reward_tokens: vector<Object<Metadata>>): Object<RewardsPool> {
        // The owner of the object doesn't matter as there are no owner-based permissions.
        // If developers want to be extra cautious here, they can make the owner @0x0.
        // Here the reward pool also doesn't keep an ExtendRef so there would be no way to obtain its signer.
        let rewards_pool_constructor_ref = &object::create_object(@rewards_pool);
        let rewards_pool_signer = &object::generate_signer(rewards_pool_constructor_ref);
        let rewards_pool_addr = signer::address_of(rewards_pool_signer);
        let reward_stores = simple_map::new();
        vector::for_each(reward_tokens, |reward_token| {
            let reward_token: Object<Metadata> = reward_token;
            let store_constructor_ref = &object::create_object(rewards_pool_addr);
            let store = fungible_asset::create_store(store_constructor_ref, reward_token);
            simple_map::add(&mut reward_stores, reward_token, RewardStore {
                store,
                // The extend ref for the rewards store is kept so we can withdraw rewards from it later when
                // claimers claim their rewards.
                store_extend_ref: object::generate_extend_ref(store_constructor_ref),
            });
        });
        move_to(rewards_pool_signer, RewardsPool {
            epoch_rewards: smart_table::new(),
            reward_stores,
        });
        object::object_from_constructor_ref(rewards_pool_constructor_ref)
    }
```

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L189-215)
```text
    /// Add rewards to the specified rewards pool. This can be called with multiple reward tokens.
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

**File:** aptos-move/framework/aptos-stdlib/sources/pool_u64_unbound.move (L231-243)
```text
    /// Return the number of coins `shares` are worth in `self` with a custom total coins number.
    /// `shares` needs to big enough to avoid rounding number.
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
