## Title
Donation/inflation attack on `swap::liquidity_pool` via unpermissioned `fungible_asset::deposit` into pool token stores - (File: `aptos-move/move-examples/swap/sources/liquidity_pool.move`)

### Summary
`swap::liquidity_pool` computes LP share issuance (`mint`), redemption (`burn`), and swap pricing (`get_amount_out`, `calculate_constant_k`) directly from the *live on-chain balance* of the pool's `FungibleStore` objects (`fungible_asset::balance(store_1/2)`), rather than from an internally-tracked, module-controlled reserve counter. Because `fungible_asset::deposit` is a public, permissionless function that accepts *any* `Object<T>` store address [1](#0-0) , and the pool's store addresses are trivially discoverable from the publicly-readable `LiquidityPool` resource, any external account can "donate" tokens straight into `token_store_1`/`token_store_2`, inflating the reserve used for share-price math without minting any LP tokens. This is the same custody-invariant break described in the external report: state used to compute a ratio (utilization there, share price here) can be manipulated out-of-band from the accounting path that is supposed to be the sole source of truth, enabling a first-deposit/inflation attack that reallocates a victim LP's deposited assets to the attacker.

### Finding Description
In `mint()`, the reserves are read directly from the stores: [2](#0-1) 

In `burn()`, redemption amounts are likewise computed from live balances divided by total LP supply: [3](#0-2) 

`calculate_constant_k` and `get_amount_out` use the same live-balance pattern: [4](#0-3) 

The pool's token stores are ordinary `FungibleStore` objects created with `fungible_asset::create_store`, owned by the pool object's signer: [5](#0-4) 

`fungible_asset::deposit`/`dispatchable_fungible_asset::deposit` perform only a sanity/frozen check — not an ownership or caller-identity check — before crediting any `Object<T>` store: [6](#0-5) 

Because Aptos on-chain state is publicly readable, and `LiquidityPool` (containing `token_store_1`/`token_store_2` addresses) is a normal resource stored at the pool's object address (itself derivable via the public `liquidity_pool_address` view function), an attacker can read the exact store addresses off-chain and then call `fungible_asset::deposit(store_1, fa)` directly — completely bypassing `mint()` and its share-issuance bookkeeping.

**Attack chain:**
1. Attacker creates a pool and becomes the first LP with a minimal deposit (e.g. slightly above `MINIMUM_LIQUIDITY`), holding LP shares of `total_liquidity - MINIMUM_LIQUIDITY`.
2. Attacker reads `token_store_1`/`token_store_2` addresses from the public `LiquidityPool` resource.
3. Attacker calls `fungible_asset::deposit` to directly transfer a large amount of token_1 (and/or token_2) into `store_1`/`store_2`, inflating `reserve_1`/`reserve_2` without any LP-token mint.
4. A victim then calls `mint()` to add liquidity; `token_1_liquidity = amount_1 * lp_token_supply / reserve_1` is computed against the artificially inflated `reserve_1`, so the victim receives far fewer LP shares than their deposit is actually worth (rounding down toward the inflated reserve), while their real tokens are deposited into the shared stores.
5. Attacker calls `burn()` with their (small) LP share count; `amount_to_redeem = amount * reserve / lp_token_supply` now pays out a disproportionately large amount of tokens — including the victim's freshly-deposited funds — because `reserve` includes both the attacker's donation and the victim's deposit while `lp_token_supply` was barely increased by the victim's rounded-down mint.

This is a custody accounting corruption: the value backing LP shares (`reserve_1`/`reserve_2` measured as live balance) no longer matches the value that was properly recorded through `mint()`, and the mismatch is realized as a transfer of the victim's deposited assets to the attacker upon `burn()`.

### Impact Explanation
This allows direct theft of a subsequent liquidity provider's deposited fungible assets (APT or any FA paired in the pool) by an unprivileged attacker who only needs to observe public on-chain state and make two ordinary calls (`fungible_asset::deposit`, then `swap::liquidity_pool::burn`/router). It corrupts the supply/custody accounting invariant that LP-token supply must proportionally track pooled assets, moving value to the wrong holder — satisfying the "Supply or custody accounting corruption that moves value to the wrong holder" and "theft of user funds" custody-impact gates. The `move-examples/swap` package is example/reference code rather than the core Aptos framework, which somewhat limits mainnet blast radius, but the pattern (using live FungibleStore balance instead of a tracked reserve for share math, combined with permissionless `fungible_asset::deposit`) is directly reusable in any FA-based AMM/vault built on top of the Aptos Object/FA framework, and the framework-level enabler (`fungible_asset::deposit` having no ownership check) is itself part of `aptos-framework`.

### Likelihood Explanation
High for any deployment of this exact module or a derivative reusing the same reserve-computation pattern: no privileged role, no race condition, and no reliance on cross-chain message timing is required — only reading a public resource and calling two permissionless entry-adjacent functions (`fungible_asset::deposit`, `mint`, `burn`). The classic ERC-4626/Uniswap-style "donation attack" is well known, and this codebase's use of `fungible_asset::balance(store)` (rather than an internally tracked `u64 reserve` field updated exclusively through `mint`/`burn`/`swap`) reproduces exactly the missing-invariant-check pattern from the external report (state derived from an externally-manipulable source instead of validated, module-controlled bookkeeping).

### Recommendation
- Track reserves as first-class state (`reserve_1: u64`, `reserve_2: u64`) inside `LiquidityPool`, updated only by `mint`, `burn`, and `swap`, and use these tracked values (not `fungible_asset::balance`) for all share-price and swap-pricing math.
- Alternatively/additionally, reconcile any excess balance (`actual_balance - tracked_reserve`) as protocol-owned "skim" rather than silently folding it into LP share value, mirroring Uniswap V2's `skim`/`sync` pattern.
- Consider restricting `fungible_asset::deposit` targets for protocol-critical stores (e.g., via dispatchable deposit hooks that reject unsolicited deposits, similar to the frozen-until-graduation pattern used in `bonding_curve_launchpad.move`) so pool accounting cannot be perturbed by non-protocol callers.

### Proof of Concept
Conceptual PoC (Move pseudocode against `swap::liquidity_pool` test harness):
```
// 1. Attacker creates pool and mints minimal initial liquidity.
liquidity_pool::create(token_1, token_2, false);
liquidity_pool::mint(&attacker, fa1_small, fa2_small, false); // attacker gets shares = sqrt(a*b) - MINIMUM_LIQUIDITY

// 2. Attacker reads LiquidityPool resource off-chain to get token_store_1/2 addresses,
//    then donates a large amount directly, bypassing mint():
fungible_asset::deposit(store_1_addr_obj, large_fa1_donation);
fungible_asset::deposit(store_2_addr_obj, large_fa2_donation);

// 3. Victim adds liquidity normally.
liquidity_pool::mint(&victim, fa1_victim, fa2_victim, false);
// victim_shares = amount * lp_token_supply / (inflated reserve) -> rounds far below fair value

// 4. Attacker burns their small share count.
let (fa1_out, fa2_out) = liquidity_pool::burn(&attacker, token_1, token_2, false, attacker_shares);
// fa1_out/fa2_out disproportionately include victim's deposited tokens plus the donation,
// net profit to attacker at victim's expense.
```
A full runnable PoC would require instantiating the `swap` test harness (`package_manager`, `coin_wrapper`) and asserting the attacker's post-burn balance exceeds their pre-donation input plus the victim's deposit share — this was not executed in this analysis; the trace above is derived directly from the arithmetic in `mint`/`burn` shown above and the unrestricted nature of `fungible_asset::deposit`.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L97-119)
```text
    /// Deposit `amount` of the fungible asset to `store`.
    ///
    /// The semantics of deposit will be governed by the function specified in DispatchFunctionStore.
    public fun deposit<T: key>(store: Object<T>, fa: FungibleAsset) acquires TransferRefStore {
        fungible_asset::deposit_sanity_check(store, false);
        let func_opt = fungible_asset::deposit_dispatch_function(store);
        if (func_opt.is_some()) {
            let func = func_opt.borrow();
            if (features::is_function_value_dispatch_enabled()) {
                dispatch_deposit_hook(store, fa, borrow_transfer_ref(store), func)
            } else {
                function_info::load_module_from_function(func);
                dispatchable_deposit(
                    store,
                    fa,
                    borrow_transfer_ref(store),
                    func
                )
            }
        } else {
            fungible_asset::unchecked_deposit(store.object_address(), fa)
        }
    }
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L408-424)
```text
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
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L486-501)
```text
        // Calculate the amounts of tokens redeemed from the pool.
        let store_1 = pool_data.token_store_1;
        let store_2 = pool_data.token_store_2;
        let reserve_1 = fungible_asset::balance(store_1);
        let reserve_2 = fungible_asset::balance(store_2);
        let amount_to_redeem_1 = (math128::mul_div(
            (amount as u128),
            (reserve_1 as u128),
            lp_token_supply
        ) as u64);
        let amount_to_redeem_2 = (math128::mul_div(
            (amount as u128),
            (reserve_2 as u128),
            lp_token_supply
        ) as u64);
        assert!(amount_to_redeem_1 > 0 && amount_to_redeem_2 > 0, EINSUFFICIENT_LIQUIDITY_REDEEMED);
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L670-673)
```text
    inline fun create_token_store(pool_signer: &signer, token: Object<Metadata>): Object<FungibleStore> {
        let constructor_ref = &object::create_object_from_object(pool_signer);
        fungible_asset::create_store(constructor_ref, token)
    }
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L683-693)
```text
    inline fun calculate_constant_k(pool: &LiquidityPool): u256 {
        let r1 = (fungible_asset::balance(pool.token_store_1) as u256);
        let r2 = (fungible_asset::balance(pool.token_store_2) as u256);
        if (pool.is_stable) {
            // k = x^3 * y + y^3 * x. This is a modified constant for stable pairs.
            r1 * r1 * r1 * r2 + r2 * r2 * r2 * r1
        } else {
            // k = x * y. This is standard constant product for volatile asset pairs.
            r1 * r2
        }
    }
```
