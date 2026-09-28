### Title
Liquidation base bonus rounds each collateral weight before multiplication, losing up to multiple BPS - (File: contracts/controller/src/positions/liquidation/math.rs)

### Summary
`get_account_bonus_params()` computes each collateral’s USD weight as `value / total_collateral`, rounds that intermediate WAD ratio, and only then multiplies it by the collateral’s liquidation bonus. This divides before multiplying and can materially understate the account’s blended liquidation bonus. Any unprivileged liquidator can reach the path through `liquidate`, and the incorrect bonus directly reduces the collateral seized for the same repayment.

### Finding Description
`process_liquidation()` is permissionless after `liquidator.require_auth()` and builds its plan through `build_liquidation_plan()`. [1](#0-0)  The plan obtains `bonus_bounds` from `calculate_seizure_proportions()`, which delegates the account-level base bonus to `get_account_bonus_params()`. [2](#0-1) 

Inside `get_account_bonus_params()`, each collateral value is first converted to a rounded WAD fraction with `value.div(env, total_collateral)`, and the rounded fraction is then multiplied by that leg’s raw BPS bonus. [3](#0-2)  The mathematically intended weighted average is instead `sum(value_i * bonus_i) / total_collateral`, with one final division after all multiplication. The current implementation can therefore lose approximately half a raw BPS unit per collateral leg, and the loss can exceed 1 BPS on accounts with several collateral positions. [4](#0-3) 

The resulting `base` is passed into the liquidation curve and becomes part of the final `bonus`. [5](#0-4)  `calculate_seized_collateral()` then uses `repayment.bonus` to form `one_plus_bonus` and scales the total USD seizure by that factor, so an understated base bonus produces an understated collateral award. [6](#0-5) 

### Impact Explanation
A liquidator receives less collateral than the protocol’s configured collateral-weighted bonus. With three or more small fractional weights, the discrepancy is at least 1 BPS and can grow with the number of collateral legs; for large liquidations this is a direct economic loss rather than dust-level rounding. The same planning arithmetic is used for the estimate and the executable liquidation path, so the quoted `bonus_rate_bps` and actual seizure are both derived from the lossy value. [7](#0-6) 

### Likelihood Explanation
The condition occurs naturally for accounts holding several collateral positions whose USD weights do not produce exact integer BPS contributions. No privileged action, oracle manipulation, bad parameter, or special market state is required: any account that becomes liquidatable can expose the rounding discrepancy, and any unprivileged caller can invoke `liquidate` with a normal debt payment. [8](#0-7) 

### Recommendation
Compute the weighted bonus as an exact weighted sum and divide by `total_collateral` once. Accumulate `sum(value_i.raw() * bonus_i)` in an overflow-safe intermediate such as the project’s `I256` multiply-divide path, then perform one half-up division by `total_collateral.raw()`; cap the result only after the final division. This preserves precision while retaining the existing `base <= max` bound.

### Proof of Concept
Consider one liquidatable account with three equal-value collateral legs, each stamped with `liquidation_bonus = 1` BPS:

```text
C = 3 USD WAD
value_1 = value_2 = value_3 = 1 USD WAD
bonus_1 = bonus_2 = bonus_3 = 1
```

The correct weighted bonus is:

```text
floor_or_half_up(sum(value_i * 1) / C) = 1 BPS
```

The production algorithm calculates:

```text
weight_i = half_up(1e18 / 3) = 333333333333333333
contribution_i = half_up(333333333333333333 * 1 / 1e18) = 0
base = min(0 + 0 + 0, max) = 0 BPS
```

Thus the account’s base liquidation bonus is reduced from the configured 1 BPS to zero before the curve and HF-preserving cap are applied. [9](#0-8)  Because seizure sizing multiplies repayment by `1 + bonus`, the liquidator receives approximately 1 BPS less collateral on every such liquidation. [6](#0-5)

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L36-58)
```rust
pub(crate) fn process_liquidation(
    env: &Env,
    liquidator: &Address,
    account_id: u64,
    debt_payments: &Vec<HubPayment>,
    seize_mode: SeizeMode,
) -> u64 {
    liquidator.require_auth();
    validation::require_not_flash_loaning(env);

    let mut account = storage::get_account(env, account_id);

    let mut cache = Context::new(env);

    require_non_empty_payments(env, debt_payments);

    // Reject an unusable receiver before moving tokens.
    let mut receiver = resolve_seize_receiver(
        env, liquidator, account_id, &account, seize_mode, &mut cache,
    );

    // Share payment normalization and positivity checks with the estimate view.
    let liquidation_plan = plan::build_liquidation_plan(env, &account, debt_payments, &mut cache);
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L46-75)
```rust
    let (proportion_seized, bonus_bounds) = calculate_seizure_proportions(
        env,
        account,
        totals.total_collateral,
        totals.weighted_collateral,
        cache,
    );

    let snap = LiquidationSnapshot {
        total_debt: totals.total_debt,
        total_collateral: totals.total_collateral,
        weighted_collateral: totals.weighted_collateral,
        proportion_seized,
        hf: totals.health_factor,
    };

    let curve = LiquidationCurve::from_config(&cache.spoke_config(account.spoke_id));
    let mut repayment = normalize_repayment_plan(
        env,
        account,
        raw_payments,
        &snap,
        bonus_bounds,
        &curve,
        cache,
    );

    let (seized_collaterals, unbacked_usd) =
        calculate_seized_collateral(env, account, totals.total_collateral, &repayment, cache);
    release_unbacked_repayment(env, &mut repayment, unbacked_usd);
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L375-399)
```rust
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

**File:** contracts/controller/src/positions/liquidation/math.rs (L578-600)
```rust
    let mut weighted_bonus_sum: i128 = 0;
    for (hub_asset, position) in iter_typed_positions(supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let value = risk::position_value(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

        let weight = value.div(env, total_collateral);
        weighted_bonus_sum = weighted_bonus_sum
            .checked_add(
                weight
                    .mul(env, Wad::from(position.liquidation_bonus.raw()))
                    .raw(),
            )
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    }

    let base = Bps::from(weighted_bonus_sum.min(max.raw()));
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L108-128)
```rust
    let scaled_bonus = calculate_linear_bonus_with_target(
        env,
        snap.hf,
        bounds.base,
        bounds.max,
        curve,
        curve.target_hf,
    );

    let bonus = match max_hf_preserving_bonus_bps(snap) {
        None => scaled_bonus,
        Some(_) if snap.total_collateral < snap.total_debt => {
            let one_plus_base = Wad::ONE.checked_add(env, bounds.base.to_wad(env));
            let backed = snap.total_collateral.div_floor(env, one_plus_base);
            return (backed.min(snap.total_debt), bounds.base);
        }
        Some(cap) if cap < bounds.base.raw() => {
            return (snap.total_debt, Bps::from(cap.max(0)));
        }
        Some(cap) => Bps::from(scaled_bonus.raw().min(cap)),
    };
```

**File:** contracts/controller/src/lib.rs (L136-158)
```rust
    /// Repays debt and seizes collateral at a health-factor-based bonus.
    /// Permissionless, including self-liquidation; requires liquidator authorization.
    /// Residual bad debt is socialized only at or below the collateral dust cap.
    ///
    /// `Transfer` pays pool cash and returns `0`. `Credit(id)` moves net supply
    /// shares to a different, authorized Normal-mode account on the same spoke;
    /// `Credit(0)` creates one. Credit mode needs no free collateral liquidity
    /// and returns the receiving account id.
    fn liquidate(
        env: Env,
        liquidator: Address,
        account_id: u64,
        debt_payments: Vec<(HubAssetKey, i128)>,
        seize_mode: SeizeMode,
    ) -> u64 {
        positions::liquidation::process_liquidation(
            &env,
            &liquidator,
            account_id,
            &debt_payments,
            seize_mode,
        )
    }
```
