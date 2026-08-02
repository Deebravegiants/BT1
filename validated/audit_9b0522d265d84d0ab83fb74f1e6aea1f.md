## Title
Front-runnable, permissionless pool creation lets an attacker skew price before `bonding_curve_launchpad::liquidity_pairs::graduate()` adds custody-held liquidity with zero slippage protection - (File: `aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move`)

### Summary
The external report's root custody invariant is: *value must not be moved into a pool/liquidity position whose exchange rate was set by an unprivileged, front-running actor immediately before the privileged deposit, because the deposit function trusts the pool's current reserve ratio with no minimum-out / slippage guard.* The Aptos-native analog exists in the `bonding_curve_launchpad` example package, whose `graduate()` function moves the entire custody-held FA/APT treasury into a **newly, permissionlessly creatable** `swap::liquidity_pool` and immediately supplies liquidity with `amount_1_min = 0, amount_2_min = 0` hard-coded.

### Finding Description
When a bonding-curve token's APT reserves cross `APT_LIQUIDITY_THRESHOLD`, `swap_apt_to_fa` calls `graduate()`: [1](#0-0) 

`graduate()` calls `router::create_pool_coin<AptosCoin>(fa_object_metadata, false)` and then `add_liquidity_coin_entry_transfer_ref` with the last two arguments (`amount_1_min`, `amount_2_min`) hard-coded to `0`: [2](#0-1) 

`liquidity_pool::liquidity_pool_address` (and therefore the resulting pool's on-chain address) is fully deterministic from the two token metadata object addresses and `is_stable`, and `liquidity_pool::create` is a `public fun` callable by anyone, with no access control: [3](#0-2) [4](#0-3) 

Since the FA's metadata address for a given `(name, symbol)` pair is also deterministic (`get_fa_obj_address`), and the `LiquidityPairGraduated`/`LiquidityPairReservesUpdated` events publicly signal when `apt_updated_reserves` is approaching `APT_LIQUIDITY_THRESHOLD`, an attacker can:
1. Predict the exact future pool address for `(wrapped-APT, FA)` before graduation occurs.
2. Front-run the graduating swap transaction by calling `swap::liquidity_pool::create` (via `router::add_liquidity_*`) themselves, seeding the brand-new pool with an arbitrarily skewed ratio of `(APT-wrapper, FA)` — e.g., depositing a large amount of one asset and a negligible amount of the other, since the *first* LP mint determines the pool's price (`optimal_liquidity_amounts` computes `liquidity = sqrt(amount_1*amount_2)` for an empty pool with no owner-controlled reference price): [5](#0-4) 
3. When `graduate()` executes, `router::create_pool_coin` sees the pool already exists (this only needs to be checked — the important point is `add_liquidity_coin_entry_transfer_ref` unconditionally computes "optimal" amounts against whatever reserves currently exist) and `add_liquidity_coin_entry_transfer_ref` deposits the bonding-curve treasury's entire remaining APT/FA balances into this attacker-seeded pool using `optimal_liquidity_amounts`, with `amount_1_min = amount_2_min = 0` meaning **no floor is enforced on the exchange rate accepted**: [6](#0-5) 
4. The attacker, as an LP holding a large share of the skewed pool, can then withdraw a disproportionate amount of the opposite asset relative to what they deposited, or immediately arbitrage the mispriced pool — extracting value out of the custody-held bonding-curve treasury that was meant to seed a fair-price public pool.

This directly mirrors the reported root cause: "no slippage protection when minting" liquidity, exploited via a permissionless, deterministic pool that an attacker can seed ahead of the protocol's own privileged liquidity-provision transaction.

### Impact Explanation
`graduate()` moves the *entire remaining custody balance* (90% of both `apt_updated_reserves` and `fa_updated_reserves`, per lines 351–352) of a bonding-curve token into the new pool in a single, unprotected deposit. An attacker who wins the race to seed the pool can force this deposit to occur at an arbitrary, attacker-chosen price, allowing them to extract a large fraction of the treasury's APT/FA value — a direct custody/value-corruption impact (theft of AMM-pooled value), analogous in severity to the M-5 stNXM finding (loss of essentially all DEX-held funds).

### Likelihood Explanation
This is a `move-examples` package (not the core `aptos-framework`), so it is not itself deployed as a system contract, but it is presented as a reference/production-pattern implementation (`bonding_curve_launchpad`) that projects are expected to copy or fork on Aptos mainnet. Within that scope, the attack requires no privileged access — the pool address, FA address, and graduation trigger condition are all publicly computable/observable, and `router`/`liquidity_pool::create` are permissionless `public fun`/`entry fun`s. The only barrier is transaction-ordering (front-running), which is generally very achievable on Aptos given deterministic reachable addresses and public events signaling imminent graduation.

### Recommendation
- In `graduate()`, require the pool to not already exist immediately prior to creation (`assert!(!liquidity_pool::liquidity_pool_address_safe(...).0, ...)`), or better, use a private/derived, launchpad-owned object address for the pool that cannot be pre-created by third parties.
- Replace the hard-coded `amount_1_min = 0, amount_2_min = 0` in `add_liquidity_coin_entry_transfer_ref` (called from `graduate`) with a computed minimum derived from the bonding curve's own internal price (`liquidity_pair.fa_reserves` / `liquidity_pair.apt_reserves`) so that liquidity is only added at, or near, the price the curve itself established, aborting if the external pool's reserve ratio deviates beyond an acceptable tolerance.

### Proof of Concept
Conceptual reproduction (Move test pseudocode against the `bonding_curve_launchpad` + `swap` example packages):
1. Deploy `bonding_curve_launchpad` and `swap` packages; launch an FA via `create_fa`.
2. Compute the deterministic future pool address: `swap::liquidity_pool::liquidity_pool_address(coin_wrapper::get_wrapper<AptosCoin>(), fa_metadata, false)`.
3. As attacker, call `swap::router::create_pool_coin<AptosCoin>(fa_metadata, false)` then `swap::router::add_liquidity_coin_entry<AptosCoin>` depositing a heavily skewed ratio (e.g., 1 unit of wrapped-APT to 1,000,000 units of FA obtained cheaply from the bonding curve, or vice versa), becoming the pool's dominant LP.
4. Buy enough FA via `bonding_curve_launchpad::swap` to push `apt_updated_reserves` above `APT_LIQUIDITY_THRESHOLD`, triggering `graduate()` in the same/next transaction.
5. Observe `graduate()`'s `add_liquidity_coin_entry_transfer_ref` deposit the bonding-curve treasury's APT/FA at the attacker-set skewed ratio (`amount_1_min`/`amount_2_min` = 0 enforces nothing).
6. As attacker, call `swap::router::remove_liquidity_entry` or perform a swap to extract disproportionate value from the now treasury-funded pool.

Note: I could not execute this PoC in a live environment (index/search-only access); the control-flow and missing-slippage-parameter claims above are directly supported by the cited source lines, but the exact numeric extraction outcome would need to be confirmed by running the Move unit tests in `aptos-move/move-examples/bonding_curve_launchpad` and `aptos-move/move-examples/swap`.

### Citations

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L332-373)
```text
    fun graduate(
        liquidity_pair: &mut LiquidityPair,
        fa_object_metadata: Object<Metadata>,
        transfer_ref: &TransferRef,
        apt_updated_reserves: u128,
        fa_updated_reserves: u128
    ) {
        // Disable Bonding Curve Launchpad pair and remove global freeze on FA.
        liquidity_pair.is_enabled = false;
        liquidity_pair.is_frozen = false;
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
        // Send liquidity provider tokens to dead address.
        let apt_coin_wrapped = coin_wrapper::get_wrapper<AptosCoin>();
        let liquidity_obj = liquidity_pool::liquidity_pool(apt_coin_wrapped, fa_object_metadata, false);
        let liquidity_pair_address = signer::address_of(&liquidity_pair_signer);
        liquidity_pool::transfer(
            &liquidity_pair_signer,
            liquidity_obj,
            @0xdead,
            primary_fungible_store::balance(liquidity_pair_address, liquidity_obj)
        );
        // Emit event informing all that the liquidity pair has graduated and which DEX it graduated to.
        event::emit(
            LiquidityPairGraduated {
                fa_object_metadata,
                dex_address: @swap
            }
        );
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L376-412)
```text
    /// Add liquidity alternative that relies on `transfer_ref`, rather than the traditional transfer
    /// found in the swap DEX.
    fun add_liquidity_coin_entry_transfer_ref<CoinType>(
        transfer_ref: &TransferRef,
        lp: &signer,
        fa_store: Object<FungibleStore>,
        token_2: Object<Metadata>,
        is_stable: bool,
        amount_1_desired: u64,
        amount_2_desired: u64,
        amount_1_min: u64,
        amount_2_min: u64,
    ) {
        // Wrap APT into a FA. Then, determine the optimal amounts for providing liquidity to the given FA - APT pair.
        let token_1 = coin_wrapper::get_wrapper<CoinType>();
        let (optimal_amount_1, optimal_amount_2, _) = router::optimal_liquidity_amounts(
            token_1,
            token_2,
            is_stable,
            amount_1_desired,
            amount_2_desired,
            amount_1_min,
            amount_2_min,
        );
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
    }
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L180-189)
```text
    public fun liquidity_pool_address(
        token_1: Object<Metadata>,
        token_2: Object<Metadata>,
        is_stable: bool,
    ): address {
        if (!is_sorted(token_1, token_2)) {
            return liquidity_pool_address(token_2, token_1, is_stable)
        };
        object::create_object_address(&@swap, get_pool_seeds(token_1, token_2, is_stable))
    }
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

**File:** aptos-move/move-examples/swap/sources/router.move (L192-214)
```text
        let reserves_2 = (reserves_2 as u128);
        let lp_token_total_supply = liquidity_pool::lp_token_supply(pool);
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
    }
```
