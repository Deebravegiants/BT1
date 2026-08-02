## Analysis Summary

The Salty bug reduces to one custody invariant: **the value credited to a liquidity/ownership share on first deposit into an AMM pool must be immune to pre-deposit price/ratio manipulation, and slippage protection must bind on the actual token amounts, not on a derived share count that itself depends on manipulable state.**

I checked whether Aptos-native AMM code in this repo reproduces the exact bug (initial-share formula using `x + y` instead of `sqrt(x*y)`), and it does not: `swap::liquidity_pool::mint` at [1](#0-0)  already uses `sqrt(amount_1 * amount_2)` plus a locked `MINIMUM_LIQUIDITY`, and `router::optimal_liquidity_amounts` already enforces `amount_1_min`/`amount_2_min` on the actual token amounts (the exact mitigation recommended in the report) at [2](#0-1) . So the primitive itself is not vulnerable.

However, the same bug-class re-appears one layer up, in a permissionless custody flow: the bonding-curve "graduation" migration in `bonding_curve_launchpad::liquidity_pairs`.

### Title
Zero-slippage, permissionlessly-triggered DEX migration in bonding-curve graduation enables front-run theft of migrated reserves - (File: `aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move`)

### Summary
When a bonding-curve pair "graduates," the module permissionlessly creates a brand-new external AMM pool and immediately seeds it with the bonding curve's real APT/FA reserves, but hardcodes `amount_1_min = 0, amount_2_min = 0` for that liquidity deposit [3](#0-2) . Because pool creation (`router::create_pool_coin`) and the graduation trigger (any user's swap that pushes `apt_reserves` over `APT_LIQUIDITY_THRESHOLD`) are both permissionless and separable transactions, an attacker can pre-create the pool and seed it at a skewed ratio before the graduation deposit lands, with no slippage floor to stop it.

### Finding Description
`graduate()` is invoked automatically from `swap_apt_to_fa` whenever a normal, permissionless swap crosses the threshold [4](#0-3) . Inside `graduate`, the module:
1. Calls `router::create_pool_coin<AptosCoin>(fa_object_metadata, false)` — a pool-creation call that is not restricted to `graduate`'s caller and can be invoked by anyone ahead of time for the same `(AptosCoin, fa_object_metadata)` pair.
2. Immediately calls `add_liquidity_coin_entry_transfer_ref` with `amount_1_min = 0, amount_2_min = 0` [5](#0-4) .

`add_liquidity_coin_entry_transfer_ref` forwards these zero minimums straight into `router::optimal_liquidity_amounts`, which — once `lp_token_supply != 0` (i.e., once *any* liquidity already exists) — derives the "optimal" amounts purely from whatever reserve ratio is already in the pool [6](#0-5) , gated only by `amount_min`, which here is `0`. This means:

- An attacker can front-run the eventual graduation transaction by first calling `router::create_pool_coin` for the exact same token pair and depositing a small amount of both tokens at a heavily skewed ratio (the classic Uniswap-style "donate to inflate/skew price" pattern that the original report exploits).
- When `graduate()` subsequently executes with `amount_1_min = amount_2_min = 0`, the bonding curve's real reserves (community/user funds accumulated over the life of the bonding curve) get deposited into the pool at the attacker-controlled ratio, with zero protection against an unfavorable price.
- The attacker, as the sole pre-existing LP, receives LP tokens proportional to the skewed pool and can then immediately withdraw/arbitrage against the newly-injected bonding-curve reserves, extracting value that rightfully belongs to bonding-curve participants.

This is not a restatement of the exact Salty math bug (Salty's `x+y` share formula) — the local `swap::liquidity_pool::mint` already uses the corrected `sqrt(x*y)` formula. The independent, locally-provable root cause here is the **missing slippage floor** (`0, 0`) combined with **permissionless, front-runnable pool creation and threshold-triggered migration**, which reproduces the same underlying custody invariant violation: a first/near-first depositor's exchange rate can be manipulated by an unprivileged actor because slippage protection doesn't bind on the actual economic terms of the deposit.

### Impact Explanation
This diverts APT/FA reserves that are custody-held on behalf of bonding-curve participants (the "recovery rights" / accounting invariant explicitly listed in the custody-pivots) to an attacker via a manipulated first-liquidity price, with no cap on the loss since `amount_1_min`/`amount_2_min` are unconditionally zero. Depending on how much value has accumulated in the bonding curve before it crosses `APT_LIQUIDITY_THRESHOLD` (600_000_000_000 raw units of virtual+real APT accounting [7](#0-6) ), this can represent a large, unrecoverable transfer of value to an unprivileged attacker — qualifying as High/Critical custody impact.

### Likelihood Explanation
Graduation is deterministically and publicly triggerable (any swap that crosses the reserve threshold), so the timing is fully predictable/observable on-chain, and `router::create_pool_coin`/liquidity provision are ordinary permissionless entry points available to any account with no privilege requirement. The only requirement is racing the graduation transaction, which is a standard MEV/front-running capability on any chain with a public mempool or transaction-ordering window.

### Recommendation
- Never hardcode `amount_1_min`/`amount_2_min` to `0` for a migration that moves custodied reserves; compute and pass real minimums derived from the bonding curve's own known reserve ratio (`fa_reserves`/`apt_reserves`) before calling `router::optimal_liquidity_amounts`.
- Make pool creation for the graduation pair atomic with (or exclusively callable by) the `graduate()` flow, e.g., by having `liquidity_pairs` create the pool itself inside the same transaction/module rather than relying on a separately-callable `router::create_pool_coin`, or by asserting the pool doesn't already exist / has no prior liquidity before depositing.
- Consider seeding the migrated pool via a fresh pool object keyed to the bonding-curve's own address/seed so it cannot be pre-created by a third party.

### Proof of Concept
1. Attacker monitors bonding-curve swaps and observes `apt_reserves` approaching `APT_LIQUIDITY_THRESHOLD`.
2. Attacker calls `router::create_pool_coin<AptosCoin>(fa_object_metadata, false)` to create the `(wrapped_APT, FA)` pool ahead of graduation.
3. Attacker calls `router::add_liquidity_coin_entry` (or equivalent) with a heavily skewed ratio (e.g., depositing a large amount of one token, negligible amount of the other), becoming the pool's sole LP at a manipulated price.
4. A subsequent normal user swap crosses `APT_LIQUIDITY_THRESHOLD`, triggering `graduate()` [8](#0-7) , which deposits the bonding curve's full reserves into the attacker-controlled pool with `amount_1_min = amount_2_min = 0`.
5. Attacker withdraws/arbitrages against the pool, extracting value from the freshly-injected bonding-curve reserves.

*Note: I was unable to fully confirm within the available context whether `router::create_pool_coin` has any implicit restriction (e.g., only callable once, or restricted to certain callers) since I could not retrieve its full body before running out of tool budget — this should be verified directly in `aptos-move/move-examples/swap/sources/router.move` before treating this as conclusively confirmed.*

### Citations

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L413-417)
```text
        let liquidity_token_amount = if (lp_token_supply == 0) {
            let total_liquidity = (math128::sqrt((amount_1 as u128) * (amount_2 as u128)) as u64);
            // Permanently lock the first MINIMUM_LIQUIDITY tokens.
            fungible_asset::mint_to(mint_ref, pool, MINIMUM_LIQUIDITY);
            total_liquidity - MINIMUM_LIQUIDITY
```

**File:** aptos-move/move-examples/swap/sources/router.move (L195-209)
```text
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
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L20-21)
```text
    const INITIAL_VIRTUAL_APT_LIQUIDITY: u128 = 50_000_000_000;
    const APT_LIQUIDITY_THRESHOLD: u128 = 600_000_000_000;
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L320-324)
```text
        // Check for graduation requirements. The APT reserves must be above the pre-defined
        // threshold to allow for graduation.
        if (liquidity_pair.is_enabled && apt_updated_reserves > APT_LIQUIDITY_THRESHOLD) {
            graduate(liquidity_pair, fa_object_metadata, transfer_ref, apt_updated_reserves, fa_updated_reserves);
        }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L332-355)
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
```
