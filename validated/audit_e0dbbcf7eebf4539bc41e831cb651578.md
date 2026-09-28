### Title
Whole-unit liquidation rounding can make every offer revert - (File: contracts/controller/src/positions/liquidation/math.rs)

### Summary
An unhealthy account whose only collateral is a listed asset with fewer than `MIN_BORROWABLE_ASSET_DECIMALS` can enter a narrow debt band in which `liquidate` has no executable payment amount. `can_be_liquidated` reports true because it only checks `HF < 1`, but repayment normalization leaves the quote unchanged, whole-unit seizure rounds to zero, all repayment is released, and execution reverts on the empty repayment plan. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Finding Description
`whole_unit_repayment` raises a partial quote only when a low-decimal collateral leg can sell one whole unit. It first computes `unit_at_bonus = floor(U / (1 + bonus))`, `unit_repayment = ceil((U + margin) / (1 + bonus))`, and `full_close_ceiling = D + R`, where `D` is total debt and `R` is the aggregate value of one base unit per debt leg. [5](#0-4) 

The function returns a full-close quote when `unit_at_bonus >= D + R`, and otherwise returns `unit_repayment` only when `unit_repayment < D`. Consequently, when

```text
floor(U / (1 + bonus)) - R < D <= ceil((U + margin) / (1 + bonus))
```

neither promotion applies and the original curve quote remains. If that curve quote backs less than one collateral unit, partial liquidation seizure is floored to zero by `calculate_seized_collateral`. [6](#0-5) [7](#0-6) 

`build_liquidation_plan` then releases the now-unbacked repayment and leaves both vectors empty; `process_liquidation` rejects the empty `result.repaid` vector. Larger offers do not help because a non-full-close plan is trimmed back to the unchanged ideal quote, while a full offer is not treated as a full close because `ideal_repayment_usd < total_debt`. [8](#0-7) [3](#0-2) [9](#0-8) 

### Impact Explanation
The affected borrower’s collateral remains locked by outstanding debt, while third-party liquidation cannot execute: every payment size either backs less than one whole collateral unit or is trimmed to an amount that does so. The account is still unhealthy and can continue accruing debt, so the protocol temporarily loses its risk-reduction mechanism even though `can_be_liquidated(account_id)` returns true. [10](#0-9) [11](#0-10) 

This is a temporary freezing/loss-of-liquidation condition rather than an immediate permanent loss. Debt accrual or a price movement can move `D` outside the band and restore liquidation, but until then neither partial nor full payment amounts can produce a nonzero executable plan. [12](#0-11) 

### Likelihood Explanation
A single unprivileged borrower can create the required shape: open an account, supply one sub-3-decimal collateral asset as the only supply position, and borrow debt whose USD value later enters the formula’s narrow interval after interest or price changes. The interval is approximately one debt-token unit plus the `U / 1e6` margin, so it is reachable for low-decimal collateral whose unit value is close to the debt value; it does not require governance, privileged access, oracle manipulation outside accepted prices, or a flash loan. [13](#0-12) [14](#0-13) 

The state is narrow and ordinarily self-corrects as debt accrues, which limits severity to Medium rather than High.

### Recommendation
Expose an explicit “liquidation cannot currently seize collateral” status or error from `get_liquidation_estimate` instead of returning an empty plan that is indistinguishable from malformed input. The estimate should report the blocking reason and the debt bounds for the non-executable band.

At execution time, consider handling this state with a dedicated quote rule rather than allowing normalization to produce an empty repayment/seizure plan. Any change should preserve the invariant that repayment and seizure remain coupled and should be covered by boundary tests around:

```text
floor(U / (1 + bonus)) - R < D <= ceil((U + margin) / (1 + bonus))
```

At minimum, document that `can_be_liquidated` is only an HF predicate and does not prove that any payment amount will execute. [1](#0-0) [15](#0-14) 

### Proof of Concept
Let the account have:

- one collateral leg `COL` with `asset_decimals < MIN_BORROWABLE_ASSET_DECIMALS`;
- at least one whole `COL` unit worth `U` USD;
- one debt leg worth `D` USD;
- `HF < 1` and `C >= D`, so `whole_unit_repayment` is evaluated;
- liquidation bonus `b` such that the curve quote `Q` satisfies `Q * (1 + b) < U + max(U / 1e6, 1 WAD)`;
- `R` equal to the USD value of one base unit of the debt token;
- `floor(U / (1 + b)) < D + R`, preventing the full-close promotion;
- `ceil((U + max(U / 1e6, 1 WAD)) / (1 + b)) >= D`, preventing the one-unit promotion.

Then:

1. `can_be_liquidated(account_id)` returns true because `health_factor < WAD`.
2. For any `debt_payments`, `normalize_repayment_plan` keeps `ideal_repayment_usd = Q`, because both whole-unit promotions are skipped.
3. `calculate_seized_collateral` computes less than one whole `COL` unit and floors the partial seizure to zero.
4. `unbacked_usd > 0` and `seized_collaterals.is_empty()` cause `release_unbacked_repayment` to remove all planned repayment.
5. `process_liquidation` calls `require_non_empty_payments(result.repaid)` and reverts with `InvalidPayments`.
6. Repeating the call with smaller, larger, or full-debt payments reaches the same result: smaller payments still seize zero units, while larger payments are trimmed to `Q` because the plan is not marked `full_close`.

### Citations

**File:** contracts/controller/src/views.rs (L30-49)
```rust
pub(crate) fn health_factor(env: &Env, account_id: u64) -> i128 {
    let mut cache = Context::new_view(env);
    match storage::try_get_account(env, account_id) {
        Some(account) if !account.debt_free() => risk::calculate_account_risk_totals(
            env,
            &mut cache,
            &account.supply_positions,
            &account.borrow_positions,
        )
        .health_factor
        .raw(),
        _ => i128::MAX,
    }
}

/// Returns whether the account's health factor is below 1.0 (WAD), making it
/// eligible for liquidation.
pub(crate) fn can_be_liquidated(env: &Env, account_id: u64) -> bool {
    health_factor(env, account_id) < WAD
}
```

**File:** contracts/controller/src/views.rs (L190-210)
```rust
/// Simulates liquidating the account with `debt_payments` under `seize_mode` and returns the
/// resulting seized collateral, protocol fees, refunds, and bonus rate, without persisting any
/// state changes.
///
/// The reported units follow the mode, so the estimate describes what execution would actually
/// move: `Transfer` reports asset units (what the pool would pay out and withhold), `Credit`
/// reports RAY-scaled supply shares (what would leave the liquidated account and what would be
/// reclassified as revenue). In credit mode the liquidator receives
/// `seized_collaterals - protocol_fees` shares.
pub(crate) fn liquidation_estimations_detailed(
    env: &Env,
    account_id: u64,
    debt_payments: &Vec<HubPayment>,
    seize_mode: SeizeMode,
) -> LiquidationEstimate {
    require_view_inputs_bound(env, debt_payments);
    let mut cache = Context::new_view(env);
    let account = storage::get_account(env, account_id);

    let result = build_liquidation_plan(env, &account, debt_payments, &mut cache).into_result();

```

**File:** contracts/controller/src/positions/liquidation/math.rs (L186-204)
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
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L235-290)
```rust
fn whole_unit_repayment(
    env: &Env,
    account: &Account,
    snap: &LiquidationSnapshot,
    quote_usd: Wad,
    bonus: Bps,
    cache: &mut Context,
) -> Wad {
    if account.supply_positions.len() != 1 {
        return quote_usd;
    }
    let Some((hub_asset, position)) = iter_typed_positions(&account.supply_positions).next() else {
        return quote_usd;
    };
    let feed = cache.cached_price(&hub_asset.asset);
    if feed.asset_decimals >= MIN_BORROWABLE_ASSET_DECIMALS {
        return quote_usd;
    }
    let supply_index = cache.cached_market_index(&hub_asset).supply_index;
    let held_units = position
        .scaled_amount
        .mul(env, supply_index)
        .to_asset_floor(env, feed.asset_decimals);
    if held_units < 1 {
        return quote_usd;
    }

    let one_plus_bonus = Wad::ONE.checked_add(env, bonus.to_wad(env));
    let unit_usd = Wad::from_token(env, 1, feed.asset_decimals).mul(env, feed.price);
    let unit_with_margin =
        unit_usd.checked_add(env, Wad::from((unit_usd.raw() / 1_000_000).max(1)));
    if quote_usd.mul(env, one_plus_bonus) >= unit_with_margin {
        return quote_usd;
    }
    let unit_at_bonus = Wad::from(mul_div_floor(
        env,
        unit_usd.raw(),
        Wad::ONE.raw(),
        one_plus_bonus.raw(),
    ));
    let full_close_ceiling = snap
        .total_debt
        .checked_add(env, one_unit_per_debt_leg_usd(env, account, cache));
    if unit_at_bonus >= full_close_ceiling {
        return snap.total_debt;
    }
    let unit_repayment = Wad::from(mul_div_ceil(
        env,
        unit_with_margin.raw(),
        Wad::ONE.raw(),
        one_plus_bonus.raw(),
    ));
    if unit_repayment >= snap.total_debt {
        return quote_usd;
    }
    unit_repayment
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L401-416)
```rust
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

**File:** contracts/controller/src/positions/liquidation/plan.rs (L73-96)
```rust
    let (seized_collaterals, unbacked_usd) =
        calculate_seized_collateral(env, account, totals.total_collateral, &repayment, cache);
    release_unbacked_repayment(env, &mut repayment, unbacked_usd);
    if unbacked_usd > Wad::ZERO && seized_collaterals.is_empty() {
        let repay_usd = repayment.repay_usd;
        release_unbacked_repayment(env, &mut repayment, repay_usd);
    }

    for entry in seized_collaterals.iter() {
        enforce_spoke_asset_flags(
            env,
            cache,
            account.spoke_id,
            &entry.hub_asset,
            FreezePolicy::SeizureLeg,
        );
    }

    let plan = LiquidationPlan {
        repayment,
        seized: seized_collaterals,
    };
    plan.validate(env);
    plan
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L58-67)
```rust
    let liquidation_plan = plan::build_liquidation_plan(env, &account, debt_payments, &mut cache);
    let offered = liquidation_plan
        .repayment
        .full_close
        .then(|| payments::aggregate_positive_payments(env, debt_payments));

    let result = liquidation_plan.into_result();

    require_non_empty_payments(env, &result.repaid);

```
