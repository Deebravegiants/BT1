### Title
Direct token transfers to an Aquarius pool inflate `fair_lp_price_wad` reserves, letting LP collateral be overvalued for outsized borrows - (File: common/src/oracle/lp.rs)

### Summary
The PancakeBunny analog here is donation-inflated valuation: just as the attacker deposited directly into MiniChefV2 so the vault's measured "interest" (a raw balance read) ballooned and minted 2.1M polyBUNNY, an unprivileged attacker can transfer tokens directly into an Aquarius pool so the live reserve read used by the LP pricing formula inflates the fair value of LP shares used as lending collateral. `fair_lp_price_wad` computes `2 * sqrt(value_a * value_b) / total_shares` from whatever `get_reserves` reports, while `total_shares` stays fixed — donated tokens raise the numerator without minting any shares, exactly the "external deposit attributed to the vault" shape of the original bug.

### Finding Description
`providers::aquarius::read` reads reserves and share supply live from the pool contract on every price resolution: [1](#0-0) . These feed `fair_lp_price_wad`, which converts each leg's raw reserve to a WAD value and prices one LP share as `2 * sqrt(value_a * value_b) / share_supply_wad`: [2](#0-1) . The formula is swap-resistant (`x*y=k` leaves `sqrt(va*vb)` roughly unchanged when leg prices are honest) but is **not** donation-resistant: a plain `token.transfer(attacker → pool)` of token A raises `reserve_a`/`value_a` while `total_shares` is unchanged, so the derived share price scales with `sqrt(1 + donation/reserve_a)`.

This price is trusted for risk decisions: `Context`-cached strict prices feed health factor and `min_borrow_collateral_usd`, so an inflated LP price directly increases the attacker's borrowable amount against LP collateral they supply via `supply`/`multiply`. Production config confirms this is a real collateral path — `AQUAUSDC_LP` is a listed market (hub 3) priced by a single `AquariusLp` source with zero dual-source tolerance, and the sanity band permits roughly a 10x range (`min_sanity_price_wad` 1.285e16 vs `max_sanity_price_wad` 1.285e17): [3](#0-2) . The only defenses are the sanity band (10x headroom) and `min_pool_value_wad`, which caps minimum pool size, not price deviation: [4](#0-3) . There is no check that reserves are consistent with share issuance or any TWAP/smoothing on the pool read — the observation is instantaneous: [5](#0-4) .

### Impact Explanation
Theft of user funds / protocol insolvency. The attacker supplies real LP shares as collateral, donates token A to the pool to inflate the LP share price, and borrows other listed assets (USDC, XLM, etc.) against the inflated collateral value. They then abandon the position; when prices revert (or after partial unwinding) the debt is undercollateralized and is socialized to suppliers via `apply_bad_debt_to_supply_index`: [6](#0-5) . Because `sqrt` dampening requires donating roughly `(k²−1)·reserve_a` for a `k`x price multiple, the attack is capital-intensive, but the donated funds are partially recoverable — the donation stays in the pool and the attacker's own LP shares (or a later balanced withdrawal via a separate wallet's shares) redeem a pro-rata slice of it, so net cost is only the unrecovered fraction, while the borrow proceeds are pure gain up to `LTV · inflated_collateral − collateral_cost`.

### Likelihood Explanation
Every ingredient is reachable by a single unprivileged address: `supply` of LP collateral, direct `token.transfer` to the Aquarius pool address (not a monetary entrypoint, so the flash guard does not block it, and it needs no auth from the protocol), `borrow` at the inflated cached price, and the in-protocol `flash_loan` to fund the donation capital. The same transaction can chain `flash_position`/`multiply` so collateral supply, donation, and borrow execute atomically. The main caveat is whether the deployed Aquarius `get_reserves` reflects raw balance donations immediately or only after a pool operation; if the pool stores internal reserves, a normal unbalanced liquidity operation or the pool's own sync-style entrypoint achieves the same effect since the router and users may interact with it freely. Rated High rather than Critical because profitability requires either owning a large share of the pool's LP supply or a large flash-funded donation, and the 10x sanity band bounds the per-share inflation.

### Recommendation
Do not derive LP fair value from raw, instant `get_reserves` reads that a donation can move. Concretely, in `common/src/oracle/lp.rs` / `lp_stable.rs` and `contracts/price-aggregator/src/providers/aquarius.rs`:
- Clamp each leg's reserve to the amount attributable to outstanding shares (e.g., require the implied pool value to be consistent with a manipulation-resistant virtual price the pool reports, or bound `reserve_i ≤ K · reserve_i_at_last_known_good_state` via a stored/TWAP'd reference).
- Alternatively price the share as `min(leg_value_methods)` — e.g., `2·min(value_a_eq, value_b_eq)·.../supply` or use each leg's "equivalent units" at oracle prices rather than raw balances — so inflating one leg cannot raise the result.
- Tighten the sanity band for LP-derived assets and/or require a second independent source so a single-manipulable read cannot pass `tolerance` alone.

### Proof of Concept
1. Attacker takes `flash_loan` for token A (e.g., AQUA) and a second asset B; deposits balanced A+B into the Aquarius USDC/AQUA constant-product pool, receiving LP shares (or uses existing shares).
2. `supply` the LP shares as collateral on hub 3 (`AQUAUSDC_LP` market).
3. `token::Client(token_a).transfer(attacker, aquarius_pool, D)` with `D ≈ 99·reserve_a` — a plain transfer; no protocol auth needed. (If `get_reserves` is internally tracked, perform the equivalent through the pool's own liquidity/sync entrypoint, which is permissionless.)
4. The next `borrow` (or `multiply`/`flash_position` finalization) resolves the LP price through `engine::resolve` → `providers::aquarius::read` → `fair_lp_price_wad`; `value_a` is now ~100x larger, so the share price is ~10x higher — still inside `[min_sanity_price_wad, max_sanity_price_wad]` — and `calculate_account_risk_totals` values the attacker's collateral ~10x.
5. `borrow` the maximum of a liquid asset (e.g., USDC) against the inflated collateral and withdraw it.
6. Stop touching the position. The inflated price reverts on the next honest read, HF collapses, liquidators seize LP collateral worth far less than the debt, and `clean_bad_debt`/`apply_bad_debt_to_supply_index` socializes the shortfall to USDC suppliers. The attacker later redeems LP shares (held in a second account) to recover most of the donation.

Exact code path: `controller.borrow` → risk totals → `Context::cached_market_index` price → `price_aggregator` `engine::resolve` → `providers::aquarius::read` (`aquarius_pool_reserves_call`, `aquarius_total_shares_call`) → `fair_lp_price_wad` returning `2·sqrt(va·vb)/supply` — with `va` donation-inflated and `supply` fixed: [7](#0-6) [1](#0-0) .

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

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L118-122)
```rust
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
    }
```

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L124-130)
```rust
    Ok(Some((
        OracleObservation {
            price_wad,
            timestamp: price_a.timestamp.min(price_b.timestamp),
        },
        false,
    )))
```

**File:** common/src/oracle/lp.rs (L57-86)
```rust
pub fn fair_lp_price_wad(
    env: &Env,
    a: &LpLeg,
    b: &LpLeg,
    supply: &LpSupply,
) -> Result<i128, OracleError> {
    if a.reserve <= 0
        || b.reserve <= 0
        || a.price_wad <= 0
        || b.price_wad <= 0
        || supply.total_shares <= 0
    {
        return Err(OracleError::InvalidPrice);
    }

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

**File:** configs/mainnet/markets.json (L1646-1653)
```json
        "tolerance": {
          "upper_ratio_bps": 0,
          "lower_ratio_bps": 0
        },
        "independence": "RequireDisjoint",
        "min_sanity_price_wad": "12851039215266326",
        "max_sanity_price_wad": "128510392152663280"
      },
```

**File:** contracts/pool/src/interest.rs (L73-88)
```rust
pub(crate) fn apply_bad_debt_to_supply_index(cache: &mut Cache, bad_debt: Ray) {
    let total_supplied_value = cache.supplied().mul(cache.env(), cache.supply_index());

    if total_supplied_value == Ray::ZERO {
        return;
    }

    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```
