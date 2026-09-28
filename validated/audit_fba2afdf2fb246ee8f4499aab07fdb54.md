### Title

Transient Aquarius reserve manipulation makes LP collateral underpriced and liquidatable - (contracts/price-aggregator/src/providers/aquarius.rs)

### Summary

XOXNO Lending prices constant-product Aquarius LP collateral from the pool’s instantaneous reserves and share supply, so an unprivileged trader can skew the pool immediately before calling `liquidate`, depress the reported LP price, and seize more LP units than the debt payment should purchase. The affected path is `AquariusLp` resolution in `contracts/price-aggregator/src/providers/aquarius.rs` and the geometric-mean formula in `common/src/oracle/lp.rs`. [1](#0-0) [2](#0-1) 

### Finding Description

`aquarius::read` resolves the two underlying-token prices, calls the pool’s live `get_reserves` and `get_total_shares`, and passes those values directly into the same transaction’s LP valuation. [1](#0-0)  The constant-product valuation is `2 * sqrt(value_a * value_b) / share_supply`, where each `value` is `reserve * external_price`. [2](#0-1) 

For a pool holding `V` USD in each leg, an attacker who adds `x` of token A receives approximately `V*x/(V+x)` of token B. The reported LP price becomes approximately `sqrt(1/(1+x/V))` of its prior value, while the pool’s actual reserve value is not correspondingly impaired because it retains the larger input leg. [3](#0-2) [4](#0-3) 

The only aggregate-level market-condition checks are the configured sanity band and `min_pool_value_wad`; a sufficiently sized swap that leaves the manipulated quote inside those bounds is accepted. [5](#0-4) [6](#0-5)  Production configures single-source `AquariusLp` collateral oracles with nonzero live reserve reads and finite sanity bands, such as `XLMUSDC_LP`. [7](#0-6) 

`liquidate` builds its plan from account risk totals and requires only that reported `health_factor < 1`. [8](#0-7)  Seizure then divides the USD seizure amount by the manipulated collateral price, so a lower LP quote converts the same debt repayment into more LP units before applying the liquidation bonus. [9](#0-8) 

### Impact Explanation

This allows theft of borrower collateral: an account healthy at the undistorted LP price can be forced below HF 1 and lose LP units valued by the protocol at the transiently depressed reserve-composition price. [10](#0-9) [11](#0-10)  The liquidator can receive the collateral through the normal Transfer or Credit liquidation paths, making the loss permanent even if the attacker later restores the pool price. [12](#0-11) 

### Likelihood Explanation

A single unprivileged address can perform its own Aquarius swap and then call controller `liquidate` with the target `account_id`, debt `payments`, and chosen `seize_mode`; no governance action or privileged oracle role is needed. [4](#0-3) [13](#0-12)  The attacker can size the trade so the quote remains above `min_sanity_price_wad` and the computed pool value remains above `min_pool_value_wad`, avoiding the fail-closed checks. [14](#0-13) [15](#0-14)  Capital can come from a flash loan or the attacker’s inventory because the reserve manipulation and liquidation occur atomically before any later reverse trade. [16](#0-15) 

### Recommendation

Do not derive collateral value from unconstrained same-transaction AMM reserve composition. Track a bounded reserve snapshot or LP virtual-price observation, reject reserve-ratio moves beyond a tightly configured deviation, or require an independent LP-price leg/TWAP before accepting the valuation. [1](#0-0) [5](#0-4) 

### Proof of Concept

1. Let an `AquariusLp` pool have `1,000,000` USD value in each underlying reserve and `2,000,000` LP shares, producing a normal quote near `$1`. [17](#0-16) 
2. In one transaction, the attacker swaps about `560,000` USD-equivalent of token A into the pool and receives about `358,974` USD-equivalent of token B, leaving approximately `1.56m / 0.641m` value across the two reserves.
3. `fair_lp_price_wad` computes `2 * sqrt(1.56m * 0.641m) / 2m`, or approximately `$0.8006`, even though the pool retained the attacker’s input and the shares remain unchanged. [2](#0-1) [18](#0-17) 
4. A borrower whose LP-collateral-weighted value was `1.05 * debt` now reports `HF ≈ 0.84`, satisfying `liquidate`’s `HF < 1` gate. [8](#0-7) 
5. The attacker submits `liquidate(caller, account_id, payments, seize_mode)` with a debt payment sized from `get_liquidation_estimate`; `calculate_seized_collateral` divides the USD seizure by approximately `$0.8006` instead of the undisturbed `$1`, transferring roughly 25% more LP units before bonus. [9](#0-8) 
6. The attacker may reverse the remaining AMM position afterward; the borrower’s excess LP units have already been seized.

### Citations

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L88-114)
```rust
    let price_a = engine::resolve_nested(session, &lp.key_a, depth + 1)?;
    let price_b = engine::resolve_nested(session, &lp.key_b, depth + 1)?;
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

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L115-122)
```rust
    let share_unit = 10i128
        .checked_pow(share_decimals)
        .ok_or(OracleError::InvalidPrice)?;
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
    }
```

**File:** common/src/oracle/lp.rs (L48-56)
```rust
/// Computes the fair-value price of one LP share, in WAD (1e18) scale.
///
/// Converts each leg's reserve into a WAD value (`reserve * price_wad /
/// 10^decimals`), combines the two leg values as `2 * sqrt(value_a *
/// value_b)`, then scales by `WAD` and divides by the share supply
/// converted to WAD (`total_value * WAD / share_supply_wad`). Returns
/// `OracleError::InvalidPrice` if any reserve, price, or share amount is not
/// positive, if a leg's value fails to compute, or if the result does not
/// fit in `i128`.
```

**File:** common/src/oracle/lp.rs (L72-84)
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
```

**File:** common/src/oracle/lp.rs (L188-198)
```rust
    #[test]
    fn balanced_pool_prices_at_reserve_value() {
        let env = Env::default();
        let price = fair_lp_price_wad(
            &env,
            &leg(1_000_000_000, WAD),
            &leg(1_000_000_000, WAD),
            &supply(1_000_000_000),
        )
        .unwrap();
        assert_eq!(price, 2_000_000_000_000_000_000);
```

**File:** common/src/oracle/providers/aquarius.rs (L43-57)
```rust
/// Reads `pool`'s reserves directly via `get_reserves`. Returns `None` if
/// the call fails, the reserve count is not two, or a reserve does not fit in i128.
pub fn aquarius_pool_reserves_call(env: &Env, pool: &Address) -> Option<(i128, i128)> {
    let reserves = match AquariusPoolClient::new(env, pool).try_get_reserves() {
        Ok(Ok(reserves)) => reserves,
        _ => return None,
    };
    if reserves.len() != 2 {
        return None;
    }
    Some((
        i128::try_from(reserves.get_unchecked(0)).ok()?,
        i128::try_from(reserves.get_unchecked(1)).ok()?,
    ))
}
```

**File:** contracts/price-aggregator/src/engine.rs (L139-146)
```rust
        if self.price_wad <= 0 {
            return Some(OracleError::InvalidPrice);
        }
        if self.price_wad < oracle.min_sanity_price_wad
            || self.price_wad > oracle.max_sanity_price_wad
        {
            return Some(OracleError::SanityBoundViolated);
        }
```

**File:** configs/mainnet/markets.json (L1199-1229)
```json
      "name": "XLMUSDC_LP",
      "hub_id": 3,
      "asset_address": "CAVKLYY4RWFQBRA2YI5GTGGXKUKJQI3JLAHDGXMS7L5RDH6X6A47NMOZ",
      "oracle": {
        "asset_decimals": 7,
        "max_price_stale_seconds": 57600,
        "sources": [
          {
            "AquariusLp": {
              "pool": "CA6PUJLBYKZKUEKLZJMKBZLEKP2OTHANDEOWSFF44FTSYLKQPIICCJBE",
              "token_a": "CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA",
              "token_b": "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75",
              "key_a": {
                "Token": "CAS3J7GYLGXMF6TDJBBYYSE3HQ6BBSMLNUQ34T6TZMYMW2EVH34XOWMA"
              },
              "key_b": {
                "Token": "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75"
              },
              "reserve_a_decimals": 7,
              "reserve_b_decimals": 7,
              "min_pool_value_wad": "1000000000000000000000000"
            }
          }
        ],
        "tolerance": {
          "upper_ratio_bps": 0,
          "lower_ratio_bps": 0
        },
        "independence": "RequireDisjoint",
        "min_sanity_price_wad": "450000000000000000",
        "max_sanity_price_wad": "2500000000000000000"
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L14-19)
```rust
pub(crate) fn build_liquidation_plan(
    env: &Env,
    account: &Account,
    raw_payments: &Vec<HubPayment>,
    cache: &mut Context,
) -> LiquidationPlan {
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L34-44)
```rust
    let totals = risk::calculate_account_risk_totals(
        env,
        cache,
        &account.supply_positions,
        &account.borrow_positions,
    );
    assert_with_error!(
        env,
        totals.health_factor < Wad::ONE,
        CollateralError::HealthFactorTooHigh
    );
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L363-399)
```rust
pub(crate) fn calculate_seized_collateral(
    env: &Env,
    account: &Account,
    total_collateral: Wad,
    repayment: &NormalizedRepaymentPlan,
    cache: &mut Context,
) -> (Vec<SeizeEntry>, Wad) {
    let mut seized: Vec<SeizeEntry> = Vec::new(env);
    if total_collateral <= Wad::ZERO {
        return (seized, Wad::ZERO);
    }

    let one_plus_bonus = Wad::ONE.checked_add(env, repayment.bonus.to_wad(env));

    let total_seizure_usd = repayment.repay_usd.mul(env, one_plus_bonus);
    let mut unseized_usd = Wad::ZERO;

    // Units: *_ray = RAY asset value (shares * index); *_scaled = RAY shares;
    // *_amount, pool_gross, realised_excess, fee_asset, and protocol_fee = token
    // units at the feed's decimals.
    for (hub_asset, position) in iter_typed_positions(&account.supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let actual_ray = position.scaled_amount.mul(env, market_index.supply_index);
        let asset_value = risk::position_value(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

        let share = asset_value.div(env, total_collateral);
        let seizure_for_asset_usd = total_seizure_usd.mul(env, share);

        let seizure_amount_wad = seizure_for_asset_usd.div(env, feed.price);
        let mut seizure_ray = seizure_amount_wad.to_ray(env);
```

**File:** contracts/controller/src/external/pool.rs (L94-107)
```rust
/// Lends to `receiver`, invokes its callback, and collects principal plus fee.
/// Returns the fee charged.
pub(crate) fn pool_flash_loan_call(
    env: &Env,
    pool_addr: &Address,
    hub_asset: &HubAssetKey,
    initiator: &Address,
    receiver: &Address,
    amount: i128,
    data: &Bytes,
) -> i128 {
    LiquidityPoolClient::new(env, pool_addr)
        .flash_loan(hub_asset, initiator, receiver, &amount, data)
}
```
