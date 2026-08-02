## Analysis

The external bug reduces to one custody invariant: **when a reward/fee-accruing LP token is recursively deposited into another pool, the receiving pool's internal accounting must still correctly attribute the accrued rewards/fees to a real, claimable owner** — otherwise value is either stolen by, or permanently orphaned to, an entity that has no legitimate claim to it.

I traced this invariant through the Aptos-native AMM analog in `swap::liquidity_pool` and confirmed a genuine, independently-provable custody defect there (fee accounting corruption/orphaning), distinct from the original Solidity theft mechanic (which relies on Uniswap v4's delegated/flash-accounting claim pattern that has no equivalent here, since `claim_fees` strictly requires the real balance-holder's `&signer` [1](#0-0) ).

### Title
Recursive LP-token liquidity permanently orphans pro-rata swap fees in `swap::liquidity_pool` - (File: aptos-move/move-examples/swap/sources/liquidity_pool.move)

### Summary
`swap::liquidity_pool` tracks per-LP fee entitlement using each address's **primary fungible store** balance of the LP token, while pool reserves (`token_store_1`/`token_store_2`) are plain, non-primary `FungibleStore` objects owned by the pool object itself. Because the LP token is a normal fungible asset, it can be used as one of the two underlying tokens of a second pool. When it is, the recursive pool's raw reserve store absorbs LP-token supply that is permanently excluded from fee-claim accounting, while still counting toward the fee-sharing denominator, orphaning a portion of collected swap fees forever.

### Finding Description
`update_claimable_fees` computes each claimer's share strictly from `primary_fungible_store::balance(lp, pool)`: [2](#0-1) 

The pool's own token reserves (`token_store_1`, `token_store_2`), however, are created as plain secondary `FungibleStore` objects, not primary stores of any address: [3](#0-2) 

Since the LP token issued by `create_lp_token` is a standard fungible asset (with a primary-store-enabled `Metadata`), any user can create a second pool where the LP token of pool A is `token_1`/`token_2` of pool B and add liquidity via `mint`: [4](#0-3) 

Once deposited, that LP-A balance sits in pool B's `store_1`/`store_2` — a non-primary store. It is:
- **Included** in `lp_token_total_supply` (via `fungible_asset::supply`) used as the denominator in every subsequent `claimable_1`/`claimable_2` calculation for pool A, diluting/limiting the total distributable share.
- **Never included** as anyone's `lp_balance` in `update_claimable_fees`, because no address's primary store increased — the tokens live in an object-owned secondary store that no code path ever passes into `update_claimable_fees`.

There is no sweep/rescue function for `fees_store_1`/`fees_store_2` in this module. The portion of `total_fees_1`/`total_fees_2` attributable to the LP-A supply now locked in pool B's reserve store can never be credited to any `claimable_1`/`claimable_2` entry and is not later reallocated — it is permanently stranded in the `fees_store_1`/`fees_store_2` objects, unreachable by `claim_fees`: [5](#0-4) 

### Impact Explanation
This is a custody/accounting-corruption bug: value (accrued swap fees legitimately owed to LPs of pool A, including the user who recursively supplied LP-A tokens to pool B) is permanently and non-recoverably locked, with no admin or user-facing recovery path in this module. This matches the "supply or custody accounting corruption that ... destroys recovery rights" and "permanent lock or non-recoverable loss of ... value" impact classes. The design explicitly supports recursive composition (LP tokens are plain fungible assets, fully composable with `mint`/`swap`), so this is not a contrived edge case but a natural consequence of the module's own architecture.

### Likelihood Explanation
High likelihood: recursive LP staking/farming (an LP token used as one leg of another pool) is a common DeFi pattern that this module does nothing to prevent — the LP token is created via `primary_fungible_store::create_primary_store_enabled_fungible_asset` and only *transfers* are gated through `liquidity_pool::transfer`/frozen primary stores; deposits into arbitrary secondary `FungibleStore` objects (like another pool's reserve store) are unrestricted `fungible_asset::deposit` calls requiring no special privilege, callable by any unprivileged user who creates or uses a second pool with the LP token as an underlying asset.

### Recommendation
Either (a) disallow LP tokens issued by this module from being used as `token_1`/`token_2` of another pool (reject at `create`/`mint` time when the underlying `Metadata` corresponds to an existing `LiquidityPool` object), or (b) change the fee-accrual accounting to operate on `fungible_asset::supply`/derived balance in a way that accounts for all stores (not just primary stores), or (c) add an explicit, permissioned sweep mechanism for `fees_store_1`/`fees_store_2` residual balances that documents and handles the orphaned-fee case, consistent with how the original report's mitigation (wrapping or explicit user communication) was applied.

### Proof of Concept
1. Create pool A for tokens `X`/`Y`; call `swap::liquidity_pool::mint` to receive LP-A tokens into a normal (frozen) primary store.
2. Perform swaps on pool A to accrue `total_fees_1`/`total_fees_2`.
3. Create pool B using LP-A token as `token_1` and some token `Z` as `token_2`.
4. Call `mint` on pool B with `fungible_asset_1` = withdrawn LP-A tokens (requires calling `liquidity_pool::transfer`/withdrawing from the frozen primary store is not needed here — the LP-A `FungibleAsset` object is extracted before deposit, same as any other token argument to `mint`), depositing them into pool B's `token_store_1` (a secondary, non-primary store).
5. Continue swapping on pool A; call `update_claimable_fees`/`claimable_fees` for every real primary-store holder of LP-A and sum their claimable amounts — the sum will be strictly less than the actual `fees_store_1`/`fees_store_2` balances by an amount proportional to the LP-A supply now held in pool B's `token_store_1`.
6. Confirm no function in `liquidity_pool.move` can withdraw that residual from `fees_store_1`/`fees_store_2` — it is permanently stranded. [6](#0-5)

### Citations

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L387-429)
```text
    public fun mint(
        lp: &signer,
        fungible_asset_1: FungibleAsset,
        fungible_asset_2: FungibleAsset,
        is_stable: bool,
    ) acquires FeesAccounting, LiquidityPool {
        let token_1 = fungible_asset::asset_metadata(&fungible_asset_1);
        let token_2 = fungible_asset::asset_metadata(&fungible_asset_2);
        if (!is_sorted(token_1, token_2)) {
            return mint(lp, fungible_asset_2, fungible_asset_1, is_stable)
        };
        // The LP store needs to exist before we can mint LP tokens.
        let pool = liquidity_pool(token_1, token_2, is_stable);
        let lp_store = ensure_lp_token_store(signer::address_of(lp), pool);
        let amount_1 = fungible_asset::amount(&fungible_asset_1);
        let amount_2 = fungible_asset::amount(&fungible_asset_2);
        assert!(amount_1 > 0 && amount_2 > 0, EZERO_AMOUNT);
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

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L544-578)
```text
    /// Claim the fees that the given LP is entitled to.
    /// This is friend-only as the returned fungible assets might be of an internal wrapper type. If this is not the
    /// case, this function can be made public.
    public(friend) fun claim_fees(
        lp: &signer,
        pool: Object<LiquidityPool>,
    ): (FungibleAsset, FungibleAsset) acquires FeesAccounting, LiquidityPool {
        let lp_address = signer::address_of(lp);
        update_claimable_fees(lp_address, pool);

        let pool_data = liquidity_pool_data(&pool);
        let fees_accounting = unchecked_mut_fees_accounting(&pool);
        let claimable_1 = if (smart_table::contains(&fees_accounting.claimable_1, lp_address)) {
            smart_table::remove(&mut fees_accounting.claimable_1, lp_address)
        } else {
            0
        };
        let claimable_2 = if (smart_table::contains(&fees_accounting.claimable_2, lp_address)) {
            smart_table::remove(&mut fees_accounting.claimable_2, lp_address)
        } else {
            0
        };
        let swap_signer = &package_manager::get_signer();
        let fees_1 = if (claimable_1 > 0) {
            fungible_asset::withdraw(swap_signer, pool_data.fees_store_1, (claimable_1 as u64))
        } else {
            fungible_asset::zero(fungible_asset::store_metadata(pool_data.fees_store_1))
        };
        let fees_2 = if (claimable_2 > 0) {
            fungible_asset::withdraw(swap_signer, pool_data.fees_store_2, (claimable_2 as u64))
        } else {
            fungible_asset::zero(fungible_asset::store_metadata(pool_data.fees_store_2))
        };
        (fees_1, fees_2)
    }
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L670-673)
```text
    inline fun create_token_store(pool_signer: &signer, token: Object<Metadata>): Object<FungibleStore> {
        let constructor_ref = &object::create_object_from_object(pool_signer);
        fungible_asset::create_store(constructor_ref, token)
    }
```
