Found the analog. This is a genuine custody-grade parallel to the Balancer bug: `mint()` in `swap::liquidity_pool` deposits both provided fungible assets in full at line 428-429 (`fungible_asset::deposit(store_1, fungible_asset_1); fungible_asset::deposit(store_2, fungible_asset_2);`), but the LP-token amount actually credited is `min(token_1_liquidity, token_2_liquidity)` [1](#0-0) . Whichever of the two deposited assets isn't the limiting side is *fully absorbed into the pool's reserves* without a proportional LP-token credit — economically identical to Balancer's "Pool decides how much to actually use, enforces max only" pattern, except here the excess isn't even segregated for a refund; it's unconditionally merged into pool reserves.

### Title
Non-optimal liquidity deposits in `swap::liquidity_pool::mint` permanently donate excess deposited assets to the pool without minting corresponding LP tokens - (File: `aptos-move/move-examples/swap/sources/liquidity_pool.move`)

### Summary
`liquidity_pool::mint` accepts two `FungibleAsset` values and deposits both of them in full into the pool's reserve stores, but only mints LP tokens proportional to the *smaller* of the two contributed ratios [2](#0-1) . If a caller supplies non-optimal amounts (i.e., not exactly matching the pool's current reserve ratio), the excess portion of whichever asset was over-supplied is deposited into the pool and permanently owned by all existing LPs — the depositor receives no LP-token credit and no refund for that excess.

### Finding Description
`mint()` computes `token_1_liquidity` and `token_2_liquidity` from the current reserves and pool supply, takes `math64::min` of the two as the amount of LP tokens to issue, and then unconditionally calls `fungible_asset::deposit(store_1, fungible_asset_1)` and `fungible_asset::deposit(store_2, fungible_asset_2)` with the *entire* fungible assets that were passed in [3](#0-2) . There is no `extract`/refund path: whatever fraction of `fungible_asset_1` or `fungible_asset_2` exceeds the optimal ratio is absorbed by the pool reserves and diluted among all existing LP-token holders, permanently, with zero compensation to the depositor.

This is a direct structural analog to the Balancer `joinBalancerPool()` bug: the caller supplies "up to" two amounts, the pool (not the caller) decides how much of each is actually "used" (i.e., proportionally credited via LP tokens), and the un-credited remainder is silently retained by the custodying contract rather than returned to the depositor.

The function's own doc comment even acknowledges the underlying risk ("Note that the LP would receive a smaller amount of LP tokens if the amounts of liquidity provided are not optimal... Users should compute the optimal amounts before calling this function") [4](#0-3) , but this only shifts the burden onto callers of the public `mint` API. The router's `add_liquidity_entry` mitigates this by pre-computing `optimal_liquidity_amounts` before calling `mint` [5](#0-4) , but `mint` is `public`, not `friend`-restricted, so any other module, composed transaction, or future integrator that calls it directly with unbalanced or naively-user-supplied amounts (e.g., `add_liquidity` inline wrapper at router.move:244-251, which explicitly states "the user should have computed the amounts to add themselves") will silently donate the imbalance to the pool with no recovery mechanism.

### Impact Explanation
Any depositor who calls `mint` (directly, or through the `add_liquidity` inline wrapper that does not enforce optimal ratios) with an imperfectly balanced pair permanently loses the excess portion of whichever token was over-supplied — that value is transferred to existing LP holders without consent or compensation. Because `mint` is a `public fun` (not gated to the router/friend module) and is example/reference code likely to be copied or directly integrated by third-party protocols on mainnet, this is a realistic custody-loss vector for any FA-based value routed through it with non-optimal ratios.

### Likelihood Explanation
Likelihood is moderate: it requires a caller (user, script, or integrating contract) to invoke `mint` with amounts that don't exactly match the live pool ratio at execution time — which is easy to happen accidentally due to price movement between quote and execution (classic AMM front-running/slippage window), not just deliberate misuse. The safe path (`router::add_liquidity_entry`) exists but is opt-in, not enforced by `mint` itself.

### Recommendation
Have `mint` return any unconsumed excess (e.g., by computing exact required amounts, extracting only that much from each `FungibleAsset`, depositing the extracted parts, and returning the leftover `FungibleAsset` remainders to the caller for refund) instead of unconditionally depositing full amounts, or restrict `mint` to `public(friend)` so it can only be reached through the router's `optimal_liquidity_amounts` pre-computation, closing off the direct-call donation path.

### Proof of Concept
1. Pool for token A/B exists with reserves 100,000 A / 200,000 B (ratio 1:2), non-zero LP supply.
2. Attacker/careless integrator calls `liquidity_pool::mint(lp, fa_a(10,000), fa_b(30,000), false)` directly (bypassing `router::add_liquidity_entry`'s ratio computation).
3. `token_1_liquidity = 10,000 * supply / 100,000`; `token_2_liquidity = 30,000 * supply / 200,000` — the second is proportionally larger; `liquidity_token_amount = min(...)` uses only the token_1-derived value.
4. Full `fa_b(30,000)` is deposited into `store_2` regardless (line 429), but LP tokens are minted based only on the amount matching the smaller ratio — the extra ~10,000 B (the amount above the 1:2-proportional 20,000) is absorbed into the pool and shared by existing LPs with no LP tokens or refund issued to the depositor.

### Citations

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L384-386)
```text
    /// Mint LP tokens for the given liquidity. Note that the LP would receive a smaller amount of LP tokens if the
    /// amounts of liquidity provided are not optimal (do not conform with the constant formula of the pool). Users
    /// should compute the optimal amounts before calling this function.
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L404-429)
```text
        let pool_data = liquidity_pool_data(&pool);
        let store_1 = pool_data.token_store_1;
        let store_2 = pool_data.token_store_2;

        // Before depositing the added liquidity, compute the amount of LP tokens the LP will receive.
        let reserve_1 = fungible_asset::balance(store_1);
        let reserve_2 = fungible_asset::balance(store_2);
        let lp_token_supply = option::destroy_some(fungible_asset::supply(pool));
        let mint_ref = &pool_data.lp_token_refs.mint_ref;
        let liquidity_token_amount = if (lp_token_supply == 0) {
            let total_liquidity = (math128::sqrt((amount_1 as u128) * (amount_2 as u128)) as u64);
            // Permanently lock the first MINIMUM_LIQUIDITY tokens.
            fungible_asset::mint_to(mint_ref, pool, MINIMUM_LIQUIDITY);
            total_liquidity - MINIMUM_LIQUIDITY
        } else {
            // Only the smaller amount between the token 1 or token 2 is considered. Users should make sure to either
            // use the router module or calculate the optimal amounts to provide before calling this function.
            let token_1_liquidity = math64::mul_div(amount_1, (lp_token_supply as u64), reserve_1);
            let token_2_liquidity = math64::mul_div(amount_2, (lp_token_supply as u64), reserve_2);
            math64::min(token_1_liquidity, token_2_liquidity)
        };
        assert!(liquidity_token_amount > 0, EINSUFFICIENT_LIQUIDITY_MINTED);

        // Deposit the received liquidity into the pool.
        fungible_asset::deposit(store_1, fungible_asset_1);
        fungible_asset::deposit(store_2, fungible_asset_2);
```

**File:** aptos-move/move-examples/swap/sources/router.move (L216-240)
```text
    /// Add liquidity to a pool. The user specifies the desired amount of each token to add and this will add the
    /// optimal amounts. If no optimal amounts can be found, this will fail.
    public entry fun add_liquidity_entry(
        lp: &signer,
        token_1: Object<Metadata>,
        token_2: Object<Metadata>,
        is_stable: bool,
        amount_1_desired: u64,
        amount_2_desired: u64,
        amount_1_min: u64,
        amount_2_min: u64,
    ) {
        let (optimal_amount_1, optimal_amount_2, _) = optimal_liquidity_amounts(
            token_1,
            token_2,
            is_stable,
            amount_1_desired,
            amount_2_desired,
            amount_1_min,
            amount_2_min,
        );
        let optimal_1 = primary_fungible_store::withdraw(lp, token_1, optimal_amount_1);
        let optimal_2 = primary_fungible_store::withdraw(lp, token_2, optimal_amount_2);
        add_liquidity(lp, optimal_1, optimal_2, is_stable);
    }
```
