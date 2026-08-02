### Title
`bonding_curve_launchpad::swap` lacks a slippage/max-price parameter, exposing swappers to unbounded price impact from tx reordering or backrunning - (File: `aptos-move/move-examples/bonding_curve_launchpad/sources/bonding_curve_launchpad.move`)

### Summary
This is a direct Aptos-native analog of the kairos `useLoan`/`AuctionFacet` issue: a value-moving entry point takes only an `amount_in` and derives the executed price/amount entirely from mutable on-chain state at execution time, with no caller-supplied bound (`amount_out_min` / max price). The public entry function `swap` in `bonding_curve_launchpad.move` [1](#0-0)  forwards straight to `liquidity_pairs::swap_fa_to_apt` / `swap_apt_to_fa`, neither of which accept or enforce any minimum-output or maximum-price bound [2](#0-1) [3](#0-2) .

### Finding Description
The output amount is computed on-the-fly from the live `fa_reserves`/`apt_reserves` constant-product state via `get_amount_out` [4](#0-3) , and then transferred unconditionally — there is no assertion comparing the realized `apt_gained`/`fa_gained` against any caller-specified minimum, unlike the sibling `swap` module's `router::swap`, which requires `amount_out_min` and asserts `fungible_asset::amount(&out) >= amount_out_min` before returning [5](#0-4) . Because reserves change with every prior trade in the same block/near-term ordering, any pending or reordered transaction (MEV backrunning, block reorg on validator networks, or simple queued transactions) can shift the effective price the swapper receives, and the swapper has no mechanism to abort the trade if the executed price is worse than what they intended when they signed the transaction. This mirrors exactly the kairos root cause: a caller submits a transaction expecting a certain price based on state at submission time, but the protocol enforces no bound, so execution against a later, less favorable state silently proceeds and moves value away from the swapper to whoever benefited from the intervening trade (i.e., other traders or LP reserves).

### Impact Explanation
A swapper can be forced to accept an economically worse trade than intended — receiving less FA/APT than the price they believed they were locking in — with no on-chain guard to prevent or bound the loss. Because the swap directly moves real APT and fungible-asset custody between the swapper's primary store and the liquidity pair's `fa_store`/`APT` balance [6](#0-5) [7](#0-6) , the missing bound is a genuine custody/value-control gap in an unprivileged, permissionless entry point, satisfying the "theft/loss of asset value via reserve/price manipulation" custody class. Severity is moderate-to-high depending on trade size and pool depth, since large or thinly-traded pairs let an attacker (or accidental reordering) impose significant, uncapped slippage on a victim's swap with no recourse.

### Likelihood Explanation
Likelihood is high on any environment with mempool visibility, transaction batching, or reordering (including MEV searchers front/back-running the `swap` entry function), and does not require any privileged role — any account can call `swap` and any account can submit competing swaps against the same pair to move the price before the victim's transaction lands. The bug is present in the base contract logic itself (not a config or governance issue), so it triggers whenever the pool has any depth and any competing activity, which is the normal operating condition for a bonding-curve/DEX contract.

### Recommendation
Add a caller-specified `min_amount_out` (or `max_amount_in` for APT-side moves) parameter to `bonding_curve_launchpad::swap` and thread it through `liquidity_pairs::swap_fa_to_apt`/`swap_apt_to_fa`, asserting the realized `apt_gained`/`fa_gained` meets the caller's bound before completing the transfer — mirroring the pattern already used in `swap::router::swap` [8](#0-7) .

### Proof of Concept
1. Pool state: `fa_reserves = R_fa`, `apt_reserves = R_apt` (virtual + real).
2. Victim submits `swap(account, name, symbol, /*swap_to_apt=*/false, amount_in = X)` expecting `fa_gained ≈ f(R_fa, R_apt, X)` based on the reserves they observed.
3. Before the victim's transaction executes, an attacker (or a reordering/backrun) submits their own `swap` against the same pair, shifting `R_fa`/`R_apt` unfavorably for the victim (e.g., buying FA to raise its price, or in a reorg-prone chain, simply landing an earlier trade ahead of the victim's).
4. Victim's transaction still executes with `amount_in = X`, but `get_amount_out` [4](#0-3)  now returns a materially smaller `fa_gained` computed off the shifted reserves, and the swap proceeds and settles unconditionally with no check against the victim's originally expected output — the victim's APT is spent for far less FA than intended, with no way to have prevented it at the contract level.

### Citations

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/bonding_curve_launchpad.move (L164-184)
```text
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

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L90-112)
```text
    #[view]
    public fun get_amount_out(
        fa_reserves: u128,
        apt_reserves: u128,
        swap_to_apt: bool,
        amount_in: u64
    ): (u64, u64, u128, u128) {
        if (swap_to_apt) {
            let divisor = fa_reserves + (amount_in as u128);
            let apt_gained = (math128::mul_div(apt_reserves, (amount_in as u128), divisor) as u64);
            let fa_updated_reserves = fa_reserves + (amount_in as u128);
            let apt_updated_reserves = apt_reserves - (apt_gained as u128);
            assert!(apt_gained > 0, ELIQUIDITY_PAIR_SWAP_AMOUNTOUT_INSIGNIFICANT);
            (amount_in, apt_gained, fa_updated_reserves, apt_updated_reserves)
        } else {
            let divisor = apt_reserves + (amount_in as u128);
            let fa_gained = (math128::mul_div(fa_reserves, (amount_in as u128), divisor) as u64);
            let fa_updated_reserves = fa_reserves - (fa_gained as u128);
            let apt_updated_reserves = apt_reserves + (amount_in as u128);
            assert!(fa_gained > 0, ELIQUIDITY_PAIR_SWAP_AMOUNTOUT_INSIGNIFICANT);
            (fa_gained, amount_in, fa_updated_reserves, apt_updated_reserves)
        }
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L212-230)
```text
    public(friend) fun swap_fa_to_apt(
        name: String,
        symbol: String,
        transfer_ref: &TransferRef,
        swapper_account: &signer,
        fa_object_metadata: Object<Metadata>,
        amount_in: u64
    ) acquires Pairs, LiquidityPair {
        // Verify the liquidity pair exists and is enabled for trading.
        assert_liquidity_pair_exists(name, symbol);
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
        // Determine the amount received of APT, when given swapper-supplied amount_in of FA.
        let (fa_given, apt_gained, fa_updated_reserves, apt_updated_reserves) = get_amount_out(
            liquidity_pair.fa_reserves,
            liquidity_pair.apt_reserves,
            true,
            amount_in
        );
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L240-246)
```text
        let liquidity_pair_signer = object::generate_signer_for_extending(&liquidity_pair.extend_ref);
        let from_swapper_store = primary_fungible_store::ensure_primary_store_exists(
            swapper_address,
            fungible_asset::transfer_ref_metadata(transfer_ref)
        );
        fungible_asset::transfer_with_ref(transfer_ref, from_swapper_store, liquidity_pair.fa_store, fa_given);
        aptos_account::transfer(&liquidity_pair_signer, swapper_address, apt_gained);
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L270-299)
```text
    public(friend) fun swap_apt_to_fa(
        name: String,
        symbol: String,
        transfer_ref: &TransferRef,
        swapper_account: &signer,
        fa_object_metadata: Object<Metadata>,
        amount_in: u64
    ) acquires Pairs, LiquidityPair {
        // Verify the liquidity pair exists and is enabled for trading.
        assert_liquidity_pair_exists(name, symbol);
        let liquidity_pair = borrow_global_mut<LiquidityPair>(get_pair_obj_address(name, symbol));
        assert!(liquidity_pair.is_enabled, ELIQUIDITY_PAIR_DISABLED);
        // Determine the amount received of FA, when given swapper-supplied amount_in of APT.
        let (fa_gained, apt_given, fa_updated_reserves, apt_updated_reserves) = get_amount_out(
            liquidity_pair.fa_reserves,
            liquidity_pair.apt_reserves,
            false,
            amount_in
        );
        // Perform the swap.
        // Swapper sends APT to the liquidity pair object. The liquidity pair object sends FA to the swapper, in return.
        // Requires the liquidity pair object's address, which is retrieved using the stored extend_ref.
        let swapper_address = signer::address_of(swapper_account);
        let liquidity_pair_address = object::address_from_extend_ref(&liquidity_pair.extend_ref);
        let to_swapper_store = primary_fungible_store::ensure_primary_store_exists(
            swapper_address,
            fungible_asset::transfer_ref_metadata(transfer_ref)
        );
        aptos_account::transfer(swapper_account, liquidity_pair_address, apt_given);
        fungible_asset::transfer_with_ref(transfer_ref, liquidity_pair.fa_store, to_swapper_store, fa_gained);
```

**File:** aptos-move/move-examples/swap/sources/router.move (L64-92)
```text
    /// Swap an amount of fungible assets for another fungible asset. User can specifies the minimum amount they
    /// expect to receive. If the actual amount received is less than the minimum amount, the transaction will fail.
    public entry fun swap_entry(
        user: &signer,
        amount_in: u64,
        amount_out_min: u64,
        from_token: Object<Metadata>,
        to_token: Object<Metadata>,
        is_stable: bool,
        recipient: address,
    ) {
        let in = primary_fungible_store::withdraw(user, from_token, amount_in);
        let out = swap(in, amount_out_min, to_token, is_stable);
        primary_fungible_store::deposit(recipient, out);
    }

    /// Similar to swap_entry but returns the fungible asset received for composability with other modules.
    public fun swap(
        in: FungibleAsset,
        amount_out_min: u64,
        to_token: Object<Metadata>,
        is_stable: bool,
    ): FungibleAsset {
        let from_token = fungible_asset::asset_metadata(&in);
        let pool = liquidity_pool::liquidity_pool(from_token, to_token, is_stable);
        let out = liquidity_pool::swap(pool, in);
        assert!(fungible_asset::amount(&out) >= amount_out_min, EINSUFFICIENT_OUTPUT_AMOUNT);
        out
    }
```
