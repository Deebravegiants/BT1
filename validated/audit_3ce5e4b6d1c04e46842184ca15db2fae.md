## Custody Invariant Reduction

The Mantra bug reduces to one invariant: **when multiple asset types are aggregated into a single atomic payout, one poisoned/blockable asset must never be able to permanently lock the legitimate assets bundled with it, and there must be no way to force the payout through or excise the poisoned asset.**

## Local Analog Found

`aptos-move/move-examples/rewards_pool/sources/rewards_pool.move` implements exactly this multi-asset aggregated-claim pattern using Aptos fungible assets, and reproduces the same root cause: mixing a dispatch-hook-aware asset (`dispatchable_fungible_asset`) into a code path that uses the *non-dispatchable* `fungible_asset` API, with no per-token isolation or force-through mechanism.

### Title
Malicious dispatchable reward token permanently locks all legitimate rewards in `rewards_pool::claim_rewards` - (File: `aptos-move/move-examples/rewards_pool/sources/rewards_pool.move`)

### Summary
`rewards_pool::create` accepts an arbitrary list of `Object<Metadata>` reward tokens with no restriction against tokens that have `dispatchable_fungible_asset` withdraw/deposit hooks registered. `claim_rewards` then iterates over all reward tokens in one atomic loop and withdraws each one with the *non-dispatchable* `fungible_asset::withdraw`. If any one reward token in that pool has a withdraw dispatch function registered, every withdrawal of that token aborts with `EINVALID_DISPATCHABLE_OPERATIONS`, reverting the whole `claim_rewards` transaction — including the legitimate reward tokens bundled in the same call — and since share redemption (`pool_u64::redeem_shares`) happens only after the loop completes, claimers' shares are never cleared and the funds become permanently unclaimable.

### Finding Description
`create()` builds a `reward_stores: SimpleMap<Object<Metadata>, RewardStore>` from any `reward_tokens` vector without checking whether a token has dispatch hooks: [1](#0-0) 

`add_rewards` funds each token store using `fungible_asset::deposit`, which only sanity-checks the *deposit* hook (`deposit_sanity_check(store, true)`), so a token with only a withdraw hook registered can be funded normally: [2](#0-1) 

`claim_rewards` then withdraws every non-zero reward token in a single loop using `fungible_asset::withdraw` (not `dispatchable_fungible_asset::withdraw`): [3](#0-2) 

`fungible_asset::withdraw` enforces `abort_on_dispatch = true`, which aborts if the store's metadata has a withdraw dispatch function registered: [4](#0-3) 

Because the abort happens inside the `vector::for_each` loop over `reward_tokens` — before the claimer's shares are redeemed at the end of `claim_rewards` — an abort on one token blocks the entire transaction, including withdrawal of all other legitimate reward tokens, and leaves the claimer's shares (and thus their entitlement) intact but permanently unexecutable: [5](#0-4) 

There is no per-token try/catch, no `SubMsg`-equivalent partial-failure handling, and no admin/owner function to exclude a poisoned token or force a partial payout — the `RewardsPool` object is explicitly designed with no owner-based permissions (comment at line 66-68), so there is no privileged recovery path at all.

### Impact Explanation
Any reward token registered at pool-creation time with a `dispatchable_fungible_asset` withdraw hook (a fully legitimate, permissionless AIP-73 feature) turns the entire pool into a permanent-lock trap for every other reward token bundled with it. Once a claimer has non-zero allocation for the poisoned token in an epoch, `claim_rewards`/`claim_rewards_entry` will unconditionally abort for that claimer for that epoch, forever, since the share-redemption that would clear their entitlement never executes. This is a permanent, non-recoverable loss of object-held fungible-asset value with no governance or admin override, matching the "Permanent lock or non-recoverable loss of object-held...value" custody-gate criterion.

### Likelihood Explanation
High. `create()` is a public entry function callable by anyone with an arbitrary token list, and registering dispatch hooks on a fungible asset via `dispatchable_fungible_asset::register_dispatch_functions` is a standard, permissionless, unprivileged operation available to any token creator. No special privilege, admin key, or race condition is required — only that the pool creator (who can be the attacker, or an unwitting integrator who lists an already-dispatchable token, e.g., a stablecoin with compliance hooks) includes one dispatchable-token reward type alongside legitimate ones.

### Recommendation
- Reject reward tokens with registered dispatch functions at `create()`/reward-token-registration time (check `fungible_asset::withdraw_dispatch_function`/`deposit_dispatch_function` and abort if present), or
- Use `dispatchable_fungible_asset::withdraw`/`deposit` consistently instead of the raw `fungible_asset` API so dispatchable tokens are handled correctly, and
- Isolate per-token withdrawal failures (e.g., process each token in its own sub-call, or redeem shares before attempting withdrawals) so a single poisoned/reverting token cannot block payout of unrelated tokens, and provide an owner/admin path to exclude or force-settle a malfunctioning reward token.

### Proof of Concept
1. Attacker deploys a fungible asset `M` and registers a withdraw dispatch function via `dispatchable_fungible_asset::register_dispatch_functions` that always aborts (or simply any legitimate-looking dispatch hook module).
2. Attacker calls `rewards_pool::create(vector[LEGIT_TOKEN, M])`, creating a pool that accepts both a legitimate reward token and `M`.
3. A staking/integration module (friend of `rewards_pool`) calls `increase_allocation` to give users shares for the current epoch, as intended by the module's design.
4. Anyone calls `add_rewards(pool, vector[legit_fa, m_fa], epoch)` to fund both tokens — `add_rewards`'s deposit-only sanity check does not block `M` since only a withdraw hook is registered.
5. After the epoch ends, any claimer calls `claim_rewards_entry(claimer, pool, epoch)`. The loop in `claim_rewards` reaches token `M`, calls `fungible_asset::withdraw`, which aborts with `EINVALID_DISPATCHABLE_OPERATIONS` because `M` has a withdraw dispatch hook.
6. The entire transaction reverts. The claimer's shares are never redeemed (step at line 179-184 never runs), so both the `LEGIT_TOKEN` rewards and the `M` rewards remain permanently locked in the pool's `RewardStore` objects for that claimer/epoch, with no admin or recovery function available to unblock them.

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

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L159-177)
```text
        vector::for_each(reward_tokens, |reward_token| {
            let reward = rewards(claimer_addr, rewards_data, reward_token, epoch);
            let reward_store = simple_map::borrow(&rewards_data.reward_stores, &reward_token);
            if (reward == 0) {
                vector::push_back(
                    &mut rewards,
                    fungible_asset::zero(fungible_asset::store_metadata(reward_store.store)),
                );
            } else {
                // Withdraw the reward from the corresponding store.
                let store_signer = &object::generate_signer_for_extending(&reward_store.store_extend_ref);
                vector::push_back(&mut rewards, fungible_asset::withdraw(store_signer, reward_store.store, reward));

                // Update the remaining amount of rewards for the epoch.
                let epoch_rewards = smart_table::borrow_mut(&mut rewards_data.epoch_rewards, epoch);
                let total_token_rewards = simple_map::borrow_mut(&mut epoch_rewards.total_amounts, &reward_token);
                *total_token_rewards = *total_token_rewards - reward;
            };
        });
```

**File:** aptos-move/move-examples/rewards_pool/sources/rewards_pool.move (L179-187)
```text
        // Remove the claimer's allocation in the epoch as they have now claimed all rewards for that epoch.
        let epoch_rewards = smart_table::borrow_mut(&mut rewards_data.epoch_rewards, epoch);
        let all_shares = pool_u64::shares(&epoch_rewards.claimer_pool, claimer_addr);
        if (all_shares > 0) {
            pool_u64::redeem_shares(&mut epoch_rewards.claimer_pool, claimer_addr, all_shares);
        };

        rewards
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

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L956-987)
```text
    public fun withdraw<T: key>(
        owner: &signer, store: Object<T>, amount: u64
    ): FungibleAsset acquires FungibleStore, DispatchFunctionStore, ConcurrentFungibleBalance {
        withdraw_sanity_check(owner, store, true);
        unchecked_withdraw(store.object_address(), amount)
    }

    /// Check the permission for withdraw operation.
    public(friend) fun withdraw_sanity_check<T: key>(
        owner: &signer, store: Object<T>, abort_on_dispatch: bool
    ) acquires FungibleStore, DispatchFunctionStore {
        withdraw_sanity_check_impl(
            signer::address_of(owner),
            store,
            abort_on_dispatch
        )
    }

    inline fun withdraw_sanity_check_impl<T: key>(
        owner_address: address, store: Object<T>, abort_on_dispatch: bool
    ) {
        assert!(
            object::owns(store, owner_address),
            error::permission_denied(ENOT_STORE_OWNER)
        );
        let fa_store = borrow_store_resource(&store);
        assert!(
            !abort_on_dispatch || !has_withdraw_dispatch_function(fa_store.metadata),
            error::invalid_argument(EINVALID_DISPATCHABLE_OPERATIONS)
        );
        assert!(!fa_store.frozen, error::permission_denied(ESTORE_IS_FROZEN));
    }
```
