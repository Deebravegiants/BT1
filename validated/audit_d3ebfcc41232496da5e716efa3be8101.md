### Title
Liquidator overpays when dust-debt promotion bypasses the collateral-backed cap on zero-threshold collateral - (File: contracts/controller/src/positions/liquidation/curve.rs)

### Summary
The liquidation quote protects liquidators against paying more than the seized collateral is worth only inside the `p > 0` insolvency branch of `estimate_liquidation_amount`. That branch is skipped whenever `proportion_seized == 0` (all collateral legs carry a zero liquidation threshold, so weighted collateral is zero even though `total_collateral > 0`). On such an insolvent account (`C < D`), the dust-debt promotion then raises the quote to the full debt `D` even though the collateral backs strictly less, and the full-close path disables repayment trimming. The plan seizes `repay_usd * (1 + bonus)` capped at the held collateral `C < D`, so the liquidator burns more debt tokens than the collateral it receives — the same loss class as the external report's missing `collatValue >= repay` check.

### Finding Description
In `estimate_liquidation_amount`, `max_hf_preserving_bonus_bps` returns `None` when `proportion_seized <= 0`, so the `Some(_) if snap.total_collateral < snap.total_debt` insolvency arm — the only place the quote is clamped to `min(D, floor(C / (1 + base)))` — is skipped for zero-weighted collateral [1](#0-0) [2](#0-1) 

With `p == 0`, `liquidation_at_target` takes the `denominator` branch, computing `(target_debt - W) / target_hf = D` and capping at `d_max = C / (1 + bonus)`, so `ideal = C / (1 + b) < D` [3](#0-2) 

The dust-debt promotion then fires unconditionally: if `0 < D - ideal < BAD_DEBT_USD_THRESHOLD` (5 WAD USD), the quote is promoted to the full `total_debt` with no check that the collateral backs it [4](#0-3) 

Back in `normalize_repayment_plan`, `full_close = ideal_repayment_usd >= snap.total_debt` is now true, so `process_excess_payment` — the trim that normally prevents a liquidator paying above the collateral-backed quote — never runs, and each leg is recorded at its ceiling-rounded debt cap (`repay_usd ≈ D`, possibly slightly above by per-leg unit rounding) [5](#0-4) 

Seizure sizes each leg as `repay_usd * (1 + bonus)` pro-rata and caps it at the held collateral (`seizure_ray.min(actual_ray)`), so total seized value is at most `C < D` — there is no `seized_value >= repay_usd` invariant anywhere in `calculate_seized_collateral`, `LiquidationPlan::validate`, or `process_liquidation` [6](#0-5) [7](#0-6) 

Execution confirms the flow: `apply_liquidation_repayments` pulls the planned (full-close, untrimmed) payment from the liquidator, and `apply_liquidation_seizures` pays out only the capped collateral; `scale_seizures_to_received` only scales seizures *down* on under-delivery, never the repayment [8](#0-7) 

The docs explicitly acknowledge the gap: "With `p == 0`, the target formula and dust promotion below apply instead" of the insolvency cap, yet the promotion still quotes the full debt [9](#0-8) 

### Impact Explanation
A liquidator calling `liquidate(account_id, debt_payments, seize_mode)` on such an account burns `D` worth of debt tokens and receives collateral worth `C < D`, realizing an immediate loss of `D - C` (bounded below `BAD_DEBT_USD_THRESHOLD` ≈ $5 plus per-leg ceiling rounding per account). The loss is unrecoverable: seizure is capped at held collateral, `Transfer` mode pays only existing pool underlying, and `Credit` mode credits shares worth the same capped `C`. Repeated across many such accounts (each holds debt independently), the aggregate loss grows. This matches the external report's class: liquidation executes even though the oracle-priced collateral value does not cover the required repayment.

### Likelihood Explanation
Requires an account whose supply positions all have `liquidation_threshold == 0` (so `proportion_seized = W/C = 0`) while holding `0 < C < D` with `D - C/(1+b) < 5` USD. Zero-threshold collateral is reachable through governance listing/config changes or `update_account_threshold` restamping cached thresholds to zero on a position that still holds value — an account that borrowed before thresholds fell keeps its debt. The liquidator path itself is permissionless (`liquidator.require_auth()` only, self-liquidation allowed, no collateral-value floor in the plan), so any unprivileged address can trigger the quote. Likelihood is Medium-low: it needs a specific threshold configuration plus a narrow debt band, but no privileged or off-chain action in the liquidator path itself.

### Recommendation
Apply the insolvency cap before the dust-debt promotion regardless of `proportion_seized`: in `estimate_liquidation_amount`, move the `total_collateral < total_debt` check ahead of the `max_hf_preserving_bonus_bps` match (returning `min(D, floor(C / (1 + base)))` at the base bonus whenever `C < D`), or equivalently gate the `remaining_debt < BAD_DEBT_USD_THRESHOLD` promotion on `snap.total_collateral >= snap.total_debt`. Additionally, add an explicit plan-level invariant in `LiquidationPlan::validate` or `normalize_repayment_plan` asserting `repay_usd <= seized_value_usd` (or that `full_close` implies `C >= D`), so no future quote path can record a repayment exceeding the collateral it seizes.

### Proof of Concept
1. Governance lists collateral asset `COLL` with `liquidation_threshold = 0` (or later lowers it to 0); a borrower account holds `scaled_amount` of `COLL` worth `C = $100` and debt `DEBT` worth `D = $102` (borrowed earlier, or via threshold restamping through `update_account_threshold`). `W = 0`, `p = W/C = 0`, `HF = 0 < 1`.
2. `estimate_liquidation_amount`: `max_hf_preserving_bonus_bps` → `None` (proportion = 0). `liquidation_at_target` returns `ideal = C/(1+b) = $96.15` for `b = 4%` base. `remaining = $102 - $96.15 = $5.85 ≥ 5`? Pick `C = $97.5`, `D = $100` → `ideal = $93.75`, `remaining = $6.25`? Adjust: `C = $99`, `D = $100`, `b = 4%` → `ideal = $95.19`, `remaining = $4.81 < 5` → quote promoted to `D = $100`.
3. Liquidator calls `liquidate(account_id, [(DEBT_asset, debt_amount)], SeizeMode::Transfer)`. `full_close = true` → no excess trim; `repay_usd = $100` (plus unit rounding). `calculate_seized_collateral` computes `total_seizure_usd = $104` but caps each leg at `actual_ray` → seized value = `C = $99`.
4. `apply_liquidation_repayments` transfers ~$100 of debt tokens from the liquidator; `apply_liquidation_seizures` pays only $99 of collateral. Liquidator loses ~$1 plus rounding — repeat per account while the configuration persists; the borrower/residual `D - C` debt then routes to `clean_bad_debt` socialization.

### Citations

**File:** contracts/controller/src/positions/liquidation/curve.rs (L85-94)
```rust
pub(super) fn max_hf_preserving_bonus_bps(snap: &LiquidationSnapshot) -> Option<i128> {
    let proportion = snap.proportion_seized.raw();
    if proportion <= 0 || snap.hf.raw() >= WAD {
        return None;
    }

    // Nonnegative HF below 1e18 bounds `hf * BPS` below 1e22, within i128;
    // positive proportion prevents division by zero.
    Some(snap.hf.raw() * BPS / proportion - BPS)
}
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L117-128)
```rust
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

**File:** contracts/controller/src/positions/liquidation/curve.rs (L130-137)
```rust
    let ideal = liquidation_at_target(env, snap, bonus, curve.target_hf);

    let remaining_debt = snap.total_debt.checked_sub(env, ideal);
    if remaining_debt > Wad::ZERO && remaining_debt < Wad::from(BAD_DEBT_USD_THRESHOLD) {
        return (snap.total_debt, bonus);
    }

    (ideal, bonus)
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L171-188)
```rust
fn liquidation_at_target(env: &Env, snap: &LiquidationSnapshot, bonus: Bps, target_hf: Wad) -> Wad {
    let one_plus_bonus = Wad::ONE.checked_add(env, bonus.to_wad(env));
    let d_max = snap.total_collateral.div(env, one_plus_bonus);
    let denom_term = snap.proportion_seized.mul(env, one_plus_bonus);
    let target_debt = target_hf.mul(env, snap.total_debt);

    if target_hf <= denom_term || target_debt <= snap.weighted_collateral {
        return d_max.min(snap.total_debt);
    }

    // Both subtractions are positive by the branch above.
    let numerator = target_debt.checked_sub(env, snap.weighted_collateral);
    let denominator = target_hf.checked_sub(env, denom_term);
    numerator
        .div(env, denominator)
        .min(d_max)
        .min(snap.total_debt)
}
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L54-69)
```rust
    pub(crate) fn validate(&self, env: &Env) {
        self.repayment.validate(env);

        for entry in self.seized.iter() {
            if entry.amount <= 0 || entry.protocol_fee < 0 || entry.protocol_fee > entry.amount {
                panic_with_error!(env, GenericError::InternalError);
            }
            if entry.scaled_amount <= 0
                || entry.bonus_scaled < 0
                || entry.bonus_scaled > entry.scaled_amount
                || i128::from(entry.liquidation_fees) >= BPS
            {
                panic_with_error!(env, GenericError::InternalError);
            }
        }
    }
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L186-214)
```rust
    let (curve_repayment_usd, bonus) = estimate_liquidation_amount(env, snap, bonus_bounds, curve);
    let insolvent = snap.total_collateral < snap.total_debt;
    let ideal_repayment_usd = if insolvent || curve_repayment_usd >= snap.total_debt {
        curve_repayment_usd
    } else {
        whole_unit_repayment(env, account, snap, curve_repayment_usd, bonus, cache)
    };
    let full_close = ideal_repayment_usd >= snap.total_debt;

    let mut final_repayment_tokens = repaid_tokens;
    if !full_close && total_debt_payment_usd > ideal_repayment_usd {
        let excess_usd = total_debt_payment_usd.checked_sub(env, ideal_repayment_usd);
        process_excess_payment(
            env,
            &mut final_repayment_tokens,
            &mut refunds,
            excess_usd,
            insolvent,
        );
    }

    // Sum the final entries before moving them; plan validation checks equality.
    let repay_usd = sum_repaid_usd(env, &final_repayment_tokens);
    let seize_all = insolvent
        && repay_usd > Wad::ZERO
        && repay_usd.checked_add(env, one_unit_per_leg_usd(env, &final_repayment_tokens))
            >= ideal_repayment_usd;
    let repays_all_debt =
        full_close && repays_every_debt_leg(env, account, &final_repayment_tokens, cache);
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L375-427)
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

        if !repayment.seize_all
            && feed.asset_decimals < MIN_BORROWABLE_ASSET_DECIMALS
            && seizure_ray < actual_ray
        {
            if repayment.repays_all_debt {
                let whole = seizure_ray.to_asset_ceil(env, feed.asset_decimals);
                seizure_ray = Ray::from_asset(env, whole, feed.asset_decimals).min(actual_ray);
            } else {
                let whole = seizure_ray.to_asset_floor(env, feed.asset_decimals);
                seizure_ray = Ray::from_asset(env, whole, feed.asset_decimals);
                let whole_usd = seizure_ray.to_wad(env).mul(env, feed.price);
                if seizure_for_asset_usd > whole_usd {
                    unseized_usd = unseized_usd
                        .checked_add(env, seizure_for_asset_usd.checked_sub(env, whole_usd));
                }
            }
        }

        if seizure_ray <= Ray::ZERO {
            continue;
        }

        let capped_ray = if repayment.seize_all {
            actual_ray
        } else {
            seizure_ray.min(actual_ray)
        };
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L64-94)
```rust
    let result = liquidation_plan.into_result();

    require_non_empty_payments(env, &result.repaid);

    let received_usd = apply::apply_liquidation_repayments(
        env,
        liquidator,
        &mut account,
        &result.repaid,
        offered.as_ref(),
        &mut cache,
    );

    // Under-delivering debt tokens must reduce the collateral awarded.
    let repay_usd = math::sum_repaid_usd(env, &result.repaid);
    let seized = math::scale_seizures_to_received(env, &result.seized, received_usd, repay_usd);
    match &mut receiver {
        None => {
            apply::apply_liquidation_seizures(env, liquidator, &mut account, &seized, &mut cache)
        }
        Some((_, receiving_account)) => {
            apply::require_credit_position_limit(env, receiving_account, &seized, &mut cache);
            apply::apply_liquidation_share_credit(
                env,
                &mut account,
                receiving_account,
                &seized,
                &mut cache,
            );
        }
    }
```

**File:** docs/reference/formulas.md (L255-264)
```markdown
Insolvency is the exact unweighted comparison `C < D`. With positive `p`, the
insolvency branch quotes the repayment the collateral backs at the base bonus,
floored, so an offer above it is trimmed and the liquidator never pays more
than it seizes. On an insolvent account the trim rounds each kept leg down to
whole token units, so the kept
value never exceeds the quote. A leg whose kept amount rounds to zero is
dropped and its whole offer refunded; if no leg remains, `liquidate` reverts
with `InvalidPayments` (16) and the estimate shows a zero payment. This insolvency
branch does not promote the quote to full debt; bad-debt cleanup takes the unbacked
residue. With `p == 0`, the target formula and dust promotion below apply instead.
```
