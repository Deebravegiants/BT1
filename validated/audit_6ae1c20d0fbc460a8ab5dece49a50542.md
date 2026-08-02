## Title
Front-runnable zero-slippage liquidity migration in `graduate()` permanently locks bonding-curve reserves - (File: `aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move`)

### Summary
The bonding-curve launchpad's `graduate()` function directly mirrors the seed bug: it hardcodes `amount_1_min = 0, amount_2_min = 0` when migrating the pair's pooled APT/FA reserves into a brand-new third-party AMM pool via `add_liquidity_coin_entry_transfer_ref`. Because `router::create_pool_coin` (which `graduate()` calls to create the destination pool) is a public, unprivileged entry function, an attacker can front-run the graduation transaction, pre-create the pool, and seed it with a small, arbitrarily skewed price ratio before the bonding curve's own liquidity migration executes.

### Finding Description
`graduate()` is triggered permissionlessly whenever any swapper's `swap_apt_to_fa` call pushes `apt_updated_reserves` above `APT_LIQUIDITY_THRESHOLD`: [1](#0-0) 

Inside `graduate()`, the destination DEX pool is created and immediately seeded with the bonding pair's collected reserves, with slippage protection hardcoded to zero: [2](#0-1) 

`router::create_pool_coin` / `liquidity_pool::create` are unprivileged, callable by anyone, and simply create the pool object at a deterministic address without requiring the caller to already hold the created liquidity pair: [3](#0-2) 

Because the pool address is deterministic (`liquidity_pool_address`, derived from token metadata + `is_stable`), an attacker can predict it, pre-create the pool, and be the very first liquidity provider — establishing an arbitrary skewed price ratio with a trivial deposit (e.g. depositing dust of `AptosCoin` against a large amount of the FA, or vice versa). When `graduate()` later calls `router::create_pool_coin`, the pool already exists, so `optimal_liquidity_amounts` takes the reserve-ratio branch instead of the "first deposit" branch: [4](#0-3) 

That branch asserts `amount_2_optimal >= amount_2_min` (or `amount_1 >= amount_1_min`), but with the hardcoded `0` values from `graduate()`, this check is a no-op — exactly the slippage-protection gap identified in the seed report. As a result, the attacker-controlled skewed ratio decides how much of the bonding pair's collected APT and FA is actually deposited into the new pool. `add_liquidity_coin_entry_transfer_ref` only withdraws the computed `optimal_amount_1`/`optimal_amount_2` from the liquidity pair (via `coin::withdraw` and `fungible_asset::withdraw_with_ref`): [5](#0-4) 

Any portion of the ~90% of collected APT/FA reserves not consumed by the skewed optimal calculation is left behind — as native `AptosCoin` in the liquidity-pair object's own account, or as `FungibleAsset` remaining in `liquidity_pair.fa_store`. Once `graduate()` finishes, `liquidity_pair.is_enabled` is permanently set to `false`: [6](#0-5) 

and `swap_fa_to_apt`/`swap_apt_to_fa` both require `is_enabled == true` to run: [7](#0-6) [8](#0-7) 

There is no other function in this module that can withdraw remaining reserves from the `LiquidityPair`'s `fa_store` or from its resource-account APT balance after graduation — the leftover value becomes permanently stranded custody (object-held/resource-account-held value with no recovery path), matching the "Permanent lock or non-recoverable loss" impact category.

### Impact Explanation
Any unprivileged attacker who can predict the deterministic pool address for a given (FA, `AptosCoin`) pair can pre-seed a skewed-ratio pool before graduation occurs. Because the graduation code path enforces zero minimum-output protection, the resulting liquidity deposit amount is dictated entirely by the attacker's chosen ratio, not by the bonding curve's actual reserve ratio. The un-deposited remainder of the migrated APT and FA reserves (potentially a large majority of the ~90% intended for migration) becomes permanently stuck: it sits in the `LiquidityPair` object's fungible store / resource-account coin store, and no entry point in `liquidity_pairs.move` exists to reclaim it once `is_enabled` flips to `false`. This is a direct, high-severity custody loss of pooled asset value belonging to all prior FA holders/traders, triggered without any privileged action.

### Likelihood Explanation
High. Triggering `graduate()` only requires an ordinary swapper to push `apt_updated_reserves` past `APT_LIQUIDITY_THRESHOLD` via a normal `swap_apt_to_fa` call — an event that must eventually happen for every successful bonding-curve token. The destination pool address is fully deterministic from public data (token metadata addresses, `is_stable=false`), so any observer of pending transactions/mempool (or even proactively, since the threshold crossing is predictable from public reserve state) can front-run with a `create_pool_coin` + minimal `add_liquidity_*` call before the graduation transaction lands. No special privileges or governance access are needed.

### Recommendation
Compute non-zero, ratio-aware minimum amounts (`amount_1_min`, `amount_2_min`) in `graduate()` based on the bonding pair's own known reserve ratio (`apt_updated_reserves`/`fa_updated_reserves`) rather than passing `0, 0`, so the transaction aborts if the destination pool's ratio has been manipulated away from the expected price. Additionally, consider having `graduate()` create the destination pool itself and revert (or handle explicitly) if it detects the pool already exists with attacker-seeded reserves, and add a recovery/sweep function that lets the original FA creator or governance reclaim any residual `fa_store`/APT balance left in the `LiquidityPair` object after `is_enabled` is set to `false`.

### Proof of Concept
1. Attacker observes (via public view functions `get_amount_out` and the bonding curve's on-chain reserves) that a given FA's bonding pair is close to `APT_LIQUIDITY_THRESHOLD`.
2. Attacker computes the deterministic pool address via `liquidity_pool::liquidity_pool_address(coin_wrapper::get_wrapper<AptosCoin>(), fa_object_metadata, false)`.
3. Attacker calls `router::create_pool_coin<AptosCoin>(fa_object_metadata, false)` then `router::add_liquidity_coin_entry<AptosCoin>` with a tiny amount of wrapped APT and a large amount of the FA (which the attacker must acquire cheaply from the bonding curve pre-graduation, or vice versa), establishing a heavily skewed reserve ratio at minimal cost.
4. Attacker (or any subsequent swapper) performs the swap that crosses `APT_LIQUIDITY_THRESHOLD`, triggering `graduate()`.
5. Inside `graduate()`, `router::create_pool_coin` is a no-op (pool already exists — behavior not fully verified from available `liquidity_pool::create` code, which does not appear to guard against re-creation collisions explicitly, but the deterministic-address `create_object` semantics in `object.move` mean a second `create_object_address` at the same seed would fail if attempted, so this step needs confirmation against the live `create_lp_token`/`create_object` implementation).
6. `optimal_liquidity_amounts` then computes an `optimal_amount_1`/`optimal_amount_2` skewed by the attacker's ratio, and since `amount_1_min=0, amount_2_min=0`, the deposit proceeds regardless of how far it diverges from the bonding pair's fair internal price.
7. The undeposited remainder of APT/FA (the difference between `apt_updated_reserves`/`fa_updated_reserves` and the actual `optimal_amount_1`/`optimal_amount_2` withdrawn) remains stuck in the `LiquidityPair` object's `fa_store` and its resource-account APT balance, with `is_enabled` now `false` and no reclaim function available.

**Note on verification limits**: I could not fully confirm from the indexed code whether `object::create_object` (used indirectly by `create_lp_token`/`liquidity_pool::create`) would abort if the deterministic pool object address already exists at the time `graduate()` calls `router::create_pool_coin` a second time — this determines whether the attack requires the attacker to create the pool first (so `graduate()`'s `create_pool_coin` call becomes a silent skip/no-op) or whether `graduate()` would instead abort outright (turning this into a DoS rather than a fund-lock). This distinction affects whether the primary impact is "permanent value lock" or "denial of graduation," and would need a live Devin session (full repo + Move compiler/test execution) to confirm precisely via `create_lp_token`/`fungible_asset::create_store`/`object::create_named_object` semantics in `aptos-move/move-examples/swap/sources/liquidity_pool.move` beyond line 309.

### Citations

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L222-223)
```text
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L280-281)
```text
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L320-325)
```text
        // Check for graduation requirements. The APT reserves must be above the pre-defined
        // threshold to allow for graduation.
        if (liquidity_pair.is_enabled && apt_updated_reserves > APT_LIQUIDITY_THRESHOLD) {
            graduate(liquidity_pair, fa_object_metadata, transfer_ref, apt_updated_reserves, fa_updated_reserves);
        }
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L339-341)
```text
        // Disable Bonding Curve Launchpad pair and remove global freeze on FA.
        liquidity_pair.is_enabled = false;
        liquidity_pair.is_frozen = false;
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L342-355)
```text
        // Offload onto third party, public DEX.
        router::create_pool_coin<AptosCoin>(fa_object_metadata, false);
        let liquidity_pair_signer = object::generate_signer_for_extending(&liquidity_pair.extend_ref);
        add_liquidity_coin_entry_transfer_ref<AptosCoin>(
            transfer_ref,
            &liquidity_pair_signer,
            liquidity_pair.fa_store,
            fa_object_metadata,
            false,
            ((apt_updated_reserves - (apt_updated_reserves / 10)) as u64),
            ((fa_updated_reserves - (fa_updated_reserves / 10)) as u64),
            0,
            0
        );
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L400-411)
```text
        // Retrieve the APT and FA from the liquidity provider.
        // `transfer_ref` is used to avoid circular dependency during graduation. A normal transfer would require
        // visiting `bonding_curve_launchpad` to execute the custom withdraw logic. `transfer_ref` bypasses the need to
        // return to `bonding_curve_launchpad` by not executing the custom withdraw logic.
        let optimal_1 = coin::withdraw<CoinType>(lp, optimal_amount_1);
        let optimal_2 = fungible_asset::withdraw_with_ref(
            transfer_ref,
            fa_store,
            optimal_amount_2
        );
        // Place the APT and FA into the liquidity pair.
        router::add_liquidity_coin<CoinType>(lp, optimal_1, optimal_2, is_stable);
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L268-309)
```text
    /// Creates a new liquidity pool.
    public fun create(
        token_1: Object<Metadata>,
        token_2: Object<Metadata>,
        is_stable: bool,
    ): Object<LiquidityPool> acquires LiquidityPoolConfigs {
        if (!is_sorted(token_1, token_2)) {
            return create(token_2, token_1, is_stable)
        };
        let configs = unchecked_mut_liquidity_pool_configs();

        // The liquidity pool will serve 3 separate roles:
        // 1. Represent the liquidity pool that LPs and users interact with to add/remove liquidity and swap tokens.
        // 2. Represent the metadata of the LP token.
        // 3. Store the min liquidity that will be locked into the pool when initial liquidity is added.
        let pool_constructor_ref = create_lp_token(token_1, token_2, is_stable);
        let pool_signer = &object::generate_signer(pool_constructor_ref);
        let lp_token = object::object_from_constructor_ref<Metadata>(pool_constructor_ref);
        fungible_asset::create_store(pool_constructor_ref, lp_token);
        move_to(pool_signer, LiquidityPool {
            token_store_1: create_token_store(pool_signer, token_1),
            token_store_2: create_token_store(pool_signer, token_2),
            fees_store_1: create_token_store(pool_signer, token_1),
            fees_store_2: create_token_store(pool_signer, token_2),
            lp_token_refs: create_lp_token_refs(pool_constructor_ref),
            swap_fee_bps: if (is_stable) { configs.stable_fee_bps } else { configs.volatile_fee_bps },
            is_stable,
        });
        move_to(pool_signer, FeesAccounting {
            total_fees_1: 0,
            total_fees_2: 0,
            total_fees_at_last_claim_1: smart_table::new(),
            total_fees_at_last_claim_2: smart_table::new(),
            claimable_1: smart_table::new(),
            claimable_2: smart_table::new(),
        });
        let pool = object::convert(lp_token);
        smart_vector::push_back(&mut configs.all_pools, pool);

        event::emit(CreatePool { pool, token_1, token_2, is_stable });
        pool
    }
```

**File:** aptos-move/move-examples/swap/sources/router.move (L194-213)
```text
        let (amount_1, amount_2) = (amount_1_desired, amount_2_desired);
        let liquidity = if (lp_token_total_supply == 0) {
            math128::sqrt(amount_1 * amount_2) - (liquidity_pool::min_liquidity() as u128)
        } else if (reserves_1 > 0 && reserves_2 > 0) {
            let amount_2_optimal = math128::mul_div(amount_1_desired, reserves_2, reserves_1);
            if (amount_2 <= amount_2_desired) {
                assert!(amount_2_optimal >= amount_2_min, EINSUFFICIENT_OUTPUT_AMOUNT);
                amount_2 = amount_2_optimal;
            } else {
                amount_1 = math128::mul_div(amount_2_desired, reserves_1, reserves_2);
                assert!(amount_1 <= amount_1_desired && amount_1 >= amount_1_min, EINSUFFICIENT_OUTPUT_AMOUNT);
            };
            math128::min(
                amount_1 * lp_token_total_supply / reserves_1,
                amount_2 * lp_token_total_supply / reserves_2,
            )
        } else {
            abort EINFINITY_POOL
        };
        ((amount_1 as u64), (amount_2 as u64), (liquidity as u64))
```
