Confirmed: after `graduate()` disables the bonding-curve pair (`liquidity_pair.is_enabled = false`), there is no remaining function anywhere in `bonding_curve_launchpad` or `liquidity_pairs` that can withdraw from `liquidity_pair.fa_store` or transfer out the residual APT held at the `liquidity_pair` object's address. This matches the report's custody invariant: value calculated as "leftover" during a liquidity-migration/initialization event must be recoverable, not stranded.

### Title
Permanent lock of 10% of migrated APT/FA reserves in the graduated `LiquidityPair` object with no withdraw path - (File: aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move)

### Summary
When a bonding-curve pair "graduates" (crosses the APT reserve threshold), `graduate()` [1](#0-0)  intentionally moves only 90% of the accumulated APT and FA reserves to the external `swap` DEX pool, computed as `apt_updated_reserves - apt_updated_reserves/10` and `fa_updated_reserves - fa_updated_reserves/10` [2](#0-1) . The remaining ~10% of both assets stays custodied at the `liquidity_pair` object address (APT balance) and inside `liquidity_pair.fa_store` (FA balance) [3](#0-2) . After graduation, `is_enabled` is set to `false` [4](#0-3) , which is checked by both swap entrypoints (`swap_fa_to_apt`/`swap_apt_to_fa`) to gate any further custodial movement of `fa_store`/pool APT [5](#0-4) . There is no other function in `liquidity_pairs.move` or `bonding_curve_launchpad.move` that uses `liquidity_pair.extend_ref` to generate a signer and sweep the residual APT/FA out, nor any admin/creator withdrawal entrypoint.

### Finding Description
The custody invariant borrowed from the Uniswap V4 report is: when a contract computes and moves only a partial amount of custodied assets during an initialization/migration action, the leftover must remain recoverable by its rightful owner, not become permanently stuck in the holding contract.

Here, `graduate()` is the terminal, one-time transition of a `LiquidityPair` object from bonding-curve mode to "migrated" mode. It deliberately withholds 10% of both reserves (`apt_updated_reserves / 10` and `fa_updated_reserves / 10`) from the migration call to `add_liquidity_coin_entry_transfer_ref` [2](#0-1) . That helper further only withdraws the "optimal" amounts computed by `router::optimal_liquidity_amounts` [6](#0-5) , which for the initial add-liquidity leg is dictated purely by the desired amounts passed in (the 90% figures) — so this is not itself a rounding dust issue, but the module-authors' own 10%-withholding design has no corresponding recovery mechanism.

After `graduate()` runs:
- `liquidity_pair.is_enabled = false` blocks `swap_fa_to_apt`/`swap_apt_to_fa`, which are the only functions that move funds in/out of `liquidity_pair.fa_store` or debit/credit the `liquidity_pair` object's APT balance.
- `liquidity_pair.extend_ref` (the only capability that could generate the `LiquidityPair`'s signer to move its residual APT or `fa_store` balance) is never used again in any subsequent function.
- No entry function in `bonding_curve_launchpad.move` references `liquidity_pairs::graduate` results or exposes a way to reclaim the residual reserves for the creator, the protocol, or LPs.

As a result the residual APT (an intentional custody-relevant asset, not merely a rounding remainder) and the residual FA held in `fa_store` are permanently orphaned at the `LiquidityPair` object address, since the object's `ExtendRef`-derived signer capability is architecturally reachable only from within functions that are now unreachable post-graduation.

### Impact Explanation
This is a permanent, non-recoverable loss of custodied value: ~10% of all APT and ~10% of the associated FA supply that accumulated in every bonding-curve pair up to the graduation threshold (600B micro-APT per the `APT_LIQUIDITY_THRESHOLD` constant [7](#0-6) ) becomes permanently locked with no owner able to reassign, withdraw, or reclaim it. This meets the custody gate criterion of "permanent lock or non-recoverable loss of object-held ... value," since the loss is deterministic and occurs on every graduation, not merely from adversarial input.

### Likelihood Explanation
This triggers deterministically and unconditionally on every successful graduation event (any FA/APT pair that reaches `APT_LIQUIDITY_THRESHOLD`), which is the expected, intended end-state of the bonding curve lifecycle — not an edge case. No attacker action, privileged bypass, or malicious input is required; it is a design gap in the "happy path."

### Recommendation
Add a recovery path (e.g., a `withdraw_residual_reserves` function, callable by an authorized `LaunchPad` admin/creator role or automatically invoked at the end of `graduate()`) that uses `liquidity_pair.extend_ref` to generate the object signer, withdraws the remaining `fa_store` balance and the object's residual APT balance, and forwards them to a designated recipient (e.g., the creator, treasury, or directly merges them into the newly created DEX pool instead of holding back 10%). Alternatively, remove the 10%-withholding logic entirely and migrate 100% of `apt_updated_reserves`/`fa_updated_reserves` in `graduate()`.

### Proof of Concept
1. Call `bonding_curve_launchpad::create_fa_pair` to launch a new FA/APT pair.
2. Repeatedly call `bonding_curve_launchpad::swap` (`swap_to_apt = false`) buying FA with APT until `apt_updated_reserves > APT_LIQUIDITY_THRESHOLD`, which triggers `graduate()` internally [8](#0-7) .
3. Observe `graduate()` executes `add_liquidity_coin_entry_transfer_ref` with only 90% of `apt_updated_reserves`/`fa_updated_reserves` [9](#0-8) .
4. After graduation, query `primary_fungible_store::balance` on `liquidity_pair.fa_store` and the APT balance at the `LiquidityPair` object address — both will show non-zero residual balances equal to ~10% of pre-graduation reserves.
5. Attempt to call any function in `liquidity_pairs.move` or `bonding_curve_launchpad.move` to withdraw these balances — none exists; `swap_fa_to_apt`/`swap_apt_to_fa` both abort on `assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED)` since `is_enabled` was set to `false` in step 3, confirming the funds are permanently stranded.

### Citations

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L20-21)
```text
    const INITIAL_VIRTUAL_APT_LIQUIDITY: u128 = 50_000_000_000;
    const APT_LIQUIDITY_THRESHOLD: u128 = 600_000_000_000;
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L177-196)
```text
        // Store all minted FA inside the liquidity_pair struct, within a Fungible Store. This object is responsible
        // for *only* it's own reserves.
        let fa_store_obj_constructor = object::create_object(@bonding_curve_launchpad);
        let fa_store = fungible_asset::create_store(&fa_store_obj_constructor, fa_object_metadata);
        fungible_asset::deposit(fa_store, fa_minted);

        // Define and store the state of the liquidity pair as:
        // Reserves, FA store, global frozen status (`is_frozen`), and enabled trading (`is_enabled`).
        // Initial APT reserves are virtual liquidity, for less extreme initial swaps (avoiding early adopter's
        // advantage, for fairness). README covers this topic in more depth.
        move_to(
            &liquidity_pair_signer,
            LiquidityPair {
                extend_ref: liquidity_pair_extend_ref,
                is_enabled: true,
                is_frozen: true,
                fa_reserves: fa_initial_liquidity,
                apt_reserves: INITIAL_VIRTUAL_APT_LIQUIDITY,
                fa_store
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

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L320-325)
```text
        // Check for graduation requirements. The APT reserves must be above the pre-defined
        // threshold to allow for graduation.
        if (liquidity_pair.is_enabled && apt_updated_reserves > APT_LIQUIDITY_THRESHOLD) {
            graduate(liquidity_pair, fa_object_metadata, transfer_ref, apt_updated_reserves, fa_updated_reserves);
        }
    }
```

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

**File:** aptos-move/move-examples/swap/sources/router.move (L391-411)
```text
    ): (Coin<CoinType>, FungibleAsset) {
        let token_1 = coin_wrapper::get_wrapper<CoinType>();
        assert!(!coin_wrapper::is_wrapper(token_2), ENOT_NATIVE_FUNGIBLE_ASSETS);
        let (amount_1, amount_2) =
            remove_liquidity_internal(lp, token_1, token_2, is_stable, liquidity, amount_1_min, amount_2_min);
        (coin_wrapper::unwrap(amount_1), amount_2)
    }

    /// Remove liquidity from a pool consisting of two coins. The user can specify the min amounts of each token they
    /// expect to receive to avoid slippage.
    public entry fun remove_liquidity_both_coins_entry<CoinType1, CoinType2>(
        lp: &signer,
        is_stable: bool,
        liquidity: u64,
        amount_1_min: u64,
        amount_2_min: u64,
        recipient: address,
    ) {
        let (amount_1, amount_2) =
            remove_liquidity_both_coins<CoinType1, CoinType2>(lp, is_stable, liquidity, amount_1_min, amount_2_min);
        aptos_account::deposit_coins<CoinType1>(recipient, amount_1);
```
