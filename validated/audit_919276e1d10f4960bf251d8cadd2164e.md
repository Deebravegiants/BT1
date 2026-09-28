### Title
Intra-transaction inflation of Aquarius LP collateral price via direct reserve donation enables over-borrowing - (File: contracts/price-aggregator/src/providers/aquarius.rs)

### Summary
The Aquarius LP price source derives the LP share price from the pool's *current* reserves via `aquarius_pool_reserves_call` (`get_reserves`) inside `read`. Although the fair-value formula `2*sqrt(value_a*value_b)/supply` in `fair_lp_price_wad` is immune to one-sided swaps (the reported bug class), it is *not* immune to symmetric inflation: an attacker who raises both reserves within one transaction raises the computed share price proportionally, while `total_shares` is unchanged. There is no TWAP, no reserve checkpoint, and no re-check that reserves correspond to actually-minted shares — the only guards are `min_pool_value_wad` and the configured sanity band, which for e.g. `AQUAUSDC_LP` spans ~10x (`12851039215266326` to `128510392152663280`).

### Finding Description
`aquarius::read` reads `get_reserves` and `get_total_shares` at call time and feeds them straight into `fair_lp_price_wad` (constant product) or `fair_stable_lp_price_wad` (stable). [1](#0-0)  Both formulas scale monotonically in the reserves: for constant product, `total_value = 2*sqrt(value_a*value_b)` [2](#0-1) , and for stable pools `D` grows roughly linearly with both reserves while the multiplier uses `min(price_a, price_b)` [3](#0-2) . The LP tokens priced this way are listed collateral assets (`XLMAQUA_LP`, `AQUAUSDC_LP`) whose valuations feed health factor and `min_borrow_collateral_usd` through the Context-cached price [4](#0-3) , and the configured band for `AQUAUSDC_LP` tolerates ~10x deviation [5](#0-4) .

### Impact Explanation
An attacker holding (or freshly acquiring) a large share of the LP position can inflate the measured collateral value far above its redeemable value, borrow against it via `Controller::borrow`/`flash_position`/`multiply` in the same transaction, then unwind. Because donated reserves remain in the pool, the attacker recovers most of the donation pro-rata by redeeming their LP shares afterward, while the borrowed funds are backed by collateral whose realizable value is much lower — leaving the hub with undercollateralized debt or bad debt that must be absorbed by `clean_bad_debt`/`recapitalize` at suppliers' expense. This is theft of user funds / protocol insolvency.

### Likelihood Explanation
Requires: (a) the LP token is accepted as collateral (true — listed markets), (b) the pool's `get_reserves` reflects balances manipulable within a transaction (direct transfers or flash-deposits; a single attacker leg reaching the aggregator through `borrow` on any hub using that collateral), and (c) the inflated price stays inside the sanity band — the 10x band on `AQUAUSDC_LP` leaves ample headroom, and `min_pool_value_wad` only sets a floor, not a ceiling. No privileged access is needed; `borrow` is permissionless and a flash loan can fund the temporary donation and the LP share acquisition. The main mitigation is that the donation cost is real capital if it cannot be reclaimed, which lowers but does not eliminate profitability when the attacker dominates the LP share supply.

### Recommendation
Do not price LP collateral purely from instantaneous pool state. Options consistent with the existing design: (1) read reserves and total shares from a mechanism that cannot reflect intra-transaction balance changes (e.g., stored reserves updated only by mint/burn/swap, or Aquarius-side TWAP checkpoints), (2) tighten `min_sanity_price_wad`/`max_sanity_price_wad` for LP sources to a narrow band around a reference rate rather than a 10x corridor, (3) cross-check the LP-derived price against a second disjoint source under `independence: RequireDisjoint` with a small tolerance instead of the current `upper_ratio_bps: 0 / lower_ratio_bps: 0` single-source setup, and (4) bound the pool-value check with a ceiling so a sudden multi-x reserve jump fails closed rather than passing as "more liquidity".

### Proof of Concept
1. Attacker flash-borrows token A and token B (or uses `flash_loan`/`flash_position` on the controller where the assets are flashloanable).
2. Attacker acquires a majority of the Aquarius pool's LP shares, then transfers A and B into the pool (or flash-deposits) so `get_reserves` reports k× the real reserves while `get_total_shares` is unchanged.
3. Attacker calls `Controller::borrow(hub_id=3, asset=<underlying>, amount≈LTV×k×collateral_usd)`. `Context::fetch_prices` → aggregator `prices` → `aquarius::read` computes an inflated `price_wad` still inside `max_sanity_price_wad`, and `pool_value_wad ≥ min_pool_value_wad` passes trivially. Solvency gate passes on the inflated collateral value.
4. Attacker repays the flash loan, redeems LP shares to recover the pro-rata donation, and keeps the borrowed assets; the position is now undercollateralized, and eventual liquidation cannot recover full value — the deficit is socialized via `clean_bad_debt`/`recapitalize`.

### Citations

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L90-114)
```rust
    let (reserve_a, reserve_b) =
        aquarius_pool_reserves_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
    let total_shares =
        aquarius_total_shares_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;

    let leg_a = LpLeg {
        reserve: reserve_a,
        decimals: lp.reserve_a_decimals,
        price_wad: price_a.price_wad,
    };
    let leg_b = LpLeg {
        reserve: reserve_b,
        decimals: lp.reserve_b_decimals,
        price_wad: price_b.price_wad,
    };
    let supply = LpSupply {
        total_shares,
        decimals: share_decimals,
    };
    let price_wad = if stable {
        let amp = aquarius_amp_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
        fair_stable_lp_price_wad(&env, &leg_a, &leg_b, &supply, amp)?
    } else {
        fair_lp_price_wad(&env, &leg_a, &leg_b, &supply)?
    };
```

**File:** common/src/oracle/lp.rs (L72-86)
```rust
    let value_a = reserve_value_wad(env, a)?;
    let value_b = reserve_value_wad(env, b)?;

    let total_value =
        isqrt_of_product(env, value_a as u128, value_b as u128).mul(&U256::from_u32(env, 2));

    let share_supply_wad = try_amount_to_wad(env, supply.total_shares, supply.decimals)?;
    if share_supply_wad <= 0 {
        return Err(OracleError::InvalidPrice);
    }
    let fair = total_value
        .mul(&U256::from_u128(env, WAD as u128))
        .div(&U256::from_u128(env, share_supply_wad as u128));

    try_u256_to_i128(&fair).ok_or(OracleError::InvalidPrice)
```

**File:** common/src/oracle/lp_stable.rs (L96-109)
```rust
    let xa_wad = try_amount_to_wad(env, a.reserve, a.decimals)?;
    let xb_wad = try_amount_to_wad(env, b.reserve, b.decimals)?;
    let d = solve_stable_d(env, xa_wad, xb_wad, amp)?;

    let min_price = a.price_wad.min(b.price_wad);
    let share_supply_wad = try_amount_to_wad(env, supply.total_shares, supply.decimals)?;
    if share_supply_wad <= 0 {
        return Err(OracleError::InvalidPrice);
    }

    let fair = d
        .mul(&U256::from_u128(env, min_price as u128))
        .div(&U256::from_u128(env, share_supply_wad as u128));
    try_u256_to_i128(&fair).ok_or(OracleError::InvalidPrice)
```

**File:** contracts/controller/src/context.rs (L142-160)
```rust
    pub(crate) fn fetch_prices(&mut self, assets: &Vec<Address>) {
        let missing = collect_uncached_keys(&self.env, assets, &self.token_prices);
        if missing.is_empty() {
            return;
        }
        let fetched = external::price_aggregator::fetch_prices(&self.env, &missing);
        for (asset, feed) in fetched.iter() {
            self.token_prices.set(asset, feed);
        }
    }

    /// Returns a previously loaded price; fails if the cache has no entry.
    pub(crate) fn cached_price(&mut self, asset: &Address) -> PriceFeed {
        let raw = self
            .token_prices
            .get(asset.clone())
            .unwrap_or_else(|| panic_with_error!(&self.env, OracleError::OracleNotConfigured));
        (&raw).into()
    }
```

**File:** configs/mainnet/markets.json (L1651-1652)
```json
        "min_sanity_price_wad": "12851039215266326",
        "max_sanity_price_wad": "128510392152663280"
```
