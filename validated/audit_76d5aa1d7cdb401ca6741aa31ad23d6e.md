### Title
Permanent lock of 10% of graduated liquidity pair reserves (APT and FA) with no sweep mechanism - (File: aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move)

### Summary
The `graduate()` function in `liquidity_pairs.move` moves 90% of a bonding-curve pair's reserves to an external DEX pool and burns the resulting LP tokens by sending them to `@0xdead`. The remaining 10% of both APT and the FA is left behind in the `LiquidityPair` object's own balances, but after graduation the pair is permanently disabled (`is_enabled = false`) and no function exists anywhere in the module to withdraw or sweep the leftover funds.

### Finding Description
`swap_apt_to_fa` triggers `graduate()` once `apt_updated_reserves` crosses `APT_LIQUIDITY_THRESHOLD`: [1](#0-0) 

`graduate()` disables the pair permanently and withdraws only 90% of the tracked reserves to seed the new DEX pool: [2](#0-1) 

The withdrawal helper explicitly computes `optimal_amount_1`/`optimal_amount_2` from the 90% figures and withdraws exactly that much APT (via `coin::withdraw`) and FA (via `fungible_asset::withdraw_with_ref`) from the liquidity pair's own signer/store, depositing the rest nowhere: [3](#0-2) 

Only the resulting LP tokens (representing the 90% that was added) are intentionally burned to `@0xdead`: [4](#0-3) 

The remaining 10% APT (held as a coin balance at the `liquidity_pair` object's own address, credited earlier via `aptos_account::transfer(swapper_account, liquidity_pair_address, apt_given)` in `swap_apt_to_fa`) and 10% FA (held in `liquidity_pair.fa_store`) stay in the object's resources. The `ExtendRef` needed to regenerate a signer for that object is stored only inside the `LiquidityPair` struct itself and is never exposed to any entry function: [5](#0-4) 

After graduation, `is_enabled` is permanently `false`, and both `swap_fa_to_apt` and `swap_apt_to_fa` (the only functions that touch `liquidity_pair.fa_store` or use `liquidity_pair.extend_ref`) hard-require `is_enabled == true`: [6](#0-5) [7](#0-6) 

I checked `bonding_curve_launchpad.move` (the only other module referencing `liquidity_pairs`) and found no function that reads, sweeps, or exposes the `LiquidityPair`'s remaining balances or `extend_ref` post-graduation: [8](#0-7) 

This is a direct custody analog to the Uniswap `M-27` finding: just as `UniswapHandler.addLiquidity` hard-codes a percentage (95%) of contract balances for liquidity provisioning without accounting for the remainder correctly, `graduate()` hard-codes a 90%/10% split with no mechanism to recover the 10% remainder — except here the outcome is strictly worse: instead of a revert (griefing), value is *unconditionally and permanently locked* on every successful graduation.

### Impact Explanation
Every time a bonding-curve pair graduates (a `mainnet`-relevant, expected, non-adversarial event), 10% of both the APT reserves and the FA reserves accumulated in that pair become permanently unrecoverable — they are neither transferred to users, the DEX pool, a fee sink, nor a dead address; they simply become inert resources with no reachable withdrawal path. This satisfies the custody gate's "Permanent lock or non-recoverable loss of object-held ... value" criterion. Given `APT_LIQUIDITY_THRESHOLD` is 600,000,000,000 (600,000 APT-units, i.e., 6,000 APT with 8 decimals), the locked 10% represents a material, recurring loss of real value for every FA that graduates.

### Likelihood Explanation
This is not an edge case requiring an attacker — it is the deterministic, guaranteed outcome of the normal, intended `graduate()` code path, which fires automatically whenever `apt_updated_reserves` crosses the threshold during ordinary trading. High likelihood, no privileged access or adversarial input required.

### Recommendation
After withdrawing the 90% for the DEX pool in `graduate()`, either (a) withdraw and forward the full remaining balance (100% of `fa_store` and the pair's APT balance) into the new liquidity pool / to a designated recipient before disabling the pair, or (b) explicitly sweep the residual 10% to a specified treasury/dead address as part of `graduate()`, or (c) add a permissioned/entry function that uses `liquidity_pair.extend_ref` to sweep any leftover FA/APT balance after `is_enabled` becomes false. Any of these ensures no value is orphaned.

### Proof of Concept
1. Call `create_fa_pair` to launch a new FA/APT bonding-curve pair.
2. Repeatedly call `swap(account, name, symbol, false /* apt_to_fa */, amount_in)` (i.e., `swap_apt_to_fa`) until `apt_updated_reserves` exceeds `APT_LIQUIDITY_THRESHOLD` (600,000,000,000).
3. Observe that `graduate()` executes: `router::create_pool_coin`, then `add_liquidity_coin_entry_transfer_ref` withdraws exactly 90% of `apt_updated_reserves` and `fa_updated_reserves`, and the resulting LP tokens are sent to `@0xdead`.
4. Query the liquidity pair object's address (`get_pair_obj_address(name, symbol)`) after graduation: it still holds ~10% of the pre-graduation APT coin balance, and `liquidity_pair.fa_store` still holds ~10% of the FA.
5. Attempt to call any exposed entry function in `bonding_curve_launchpad` or `liquidity_pairs` that could move these residual balances — none exists; `swap_fa_to_apt`/`swap_apt_to_fa` abort with `ELIQUIDITY_PAIR_DISABLED` since `is_enabled` is now `false`, and `extend_ref` is never surfaced. The 10% remains stuck indefinitely.

### Citations

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L68-76)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    struct LiquidityPair has store, key {
        extend_ref: ExtendRef,
        is_enabled: bool,
        is_frozen: bool,
        fa_reserves: u128,
        apt_reserves: u128,
        fa_store: Object<FungibleStore>,
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L219-223)
```text
    ) acquires Pairs, LiquidityPair {
        // Verify the liquidity pair exists and is enabled for trading.
        assert_liquidity_pair_exists(name, symbol);
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L277-281)
```text
    ) acquires Pairs, LiquidityPair {
        // Verify the liquidity pair exists and is enabled for trading.
        assert_liquidity_pair_exists(name, symbol);
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

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L338-365)
```text
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
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L378-412)
```text
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

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/bonding_curve_launchpad.move (L163-184)
```text
    /// Swap from FA to APT, or vice versa, through `liquidity_pair`.
    public entry fun swap(
        account: &signer,
        name: String,
        symbol: String,
        swap_to_apt: bool,
        amount_in: u64
    ) acquires LaunchPad, FAController {
        // Verify the `amount_in` is valid and that the FA exists.
        assert!(amount_in > 0, ELIQUIDITY_PAIR_SWAP_AMOUNTIN_INVALID);
        // FA Object<Metadata> required for primary_fungible_store interactions.
        // `transfer_ref` is used to bypass the `is_frozen` status of the FA. Without this, the defined dispatchable
        // withdraw function would prevent the ability to transfer the participant's FA onto the liquidity pair.
        let fa_metadata_obj = object::address_to_object(get_fa_obj_address(name, symbol));
        let transfer_ref = &borrow_global<FAController>(get_fa_obj_address(name, symbol)).transfer_ref;
        // Initiate the swap on the associated liquidity pair.
        if (swap_to_apt) {
            liquidity_pairs::swap_fa_to_apt(name, symbol, transfer_ref, account, fa_metadata_obj, amount_in);
        } else {
            liquidity_pairs::swap_apt_to_fa(name, symbol, transfer_ref, account, fa_metadata_obj, amount_in);
        };
    }
```
