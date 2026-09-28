### Title
A liquidation-threshold increase can invert bonus bounds and permanently revert liquidation - (File: `contracts/controller/src/positions/liquidation/curve.rs`)

### Summary
`calculate_linear_bonus_with_target` assumes the dynamically computed maximum bonus is always at least the stored account base bonus. A threshold refresh can leave `liquidation_bonus` above the new maximum implied by `liquidation_threshold`, after which every liquidation of the account panics at `max.checked_sub(base)`.

### Finding Description
Each supply position stores `liquidation_threshold`, `liquidation_bonus`, and `liquidation_fees`; refreshing a position copies the current asset configuration into all three fields when the configured change does not favor liquidators or clears the health-factor gate. [1](#0-0) 

Liquidation planning computes the account's effective seizure proportion, derives `BonusBounds` from the stored positions, and passes those bounds into `estimate_liquidation_amount`. [2](#0-1) [3](#0-2) 

For a liquidatable account (`hf < target`), the curve computes:

```rust
let bonus_range = max.checked_sub(env, base);
```

If `base > max`, `checked_sub` panics with `MathOverflow`. [4](#0-3) 

A threshold increase raises `proportion_seized` and therefore lowers the threshold-derived maximum bonus returned by `max_bonus_for_threshold`. [5](#0-4)  Because increasing `liquidation_threshold` is borrower-favorable, `favors_liquidator` does not gate the refresh when the bonus remains unchanged; the account can therefore retain an old high base bonus while its new maximum becomes lower. [6](#0-5) 

### Impact Explanation
Once `base > max`, every liquidation attempt reverts before repayment normalization or seizure execution. `process_liquidation` calls `build_liquidation_plan`, which reaches the panicking curve calculation before any debt can be repaid or collateral seized. [7](#0-6) 

The unhealthy account cannot be liquidated while the inverted bounds remain stored. If its collateral value continues to fall, debt can become unbacked and remain uncleansed, creating protocol insolvency. The impact is stronger than a temporary user-funds freeze because no third-party liquidator can reduce the bad debt through the normal liquidation path.

### Likelihood Explanation
This requires governance to execute a ready asset update that raises `liquidation_threshold` while the existing `liquidation_bonus` remains above the bonus ceiling implied by the new threshold. An unprivileged account owner can then call `update_account_threshold(caller, true, account_ids)` while the account remains healthy enough, stamping the inverted terms. A subsequent price movement or interest accrual can push HF below `1 WAD`, after which any unprivileged liquidator calling `liquidate` encounters the revert. [8](#0-7) 

### Recommendation
Handle an inverted range explicitly before subtracting:

```rust
if max <= base {
    return max;
}
let bonus_range = max.checked_sub(env, base);
```

Alternatively, compute the scaled increment only when `max > base`, then clamp the final bonus to `max`. The refresh path should also preserve or validate the invariant `liquidation_bonus <= max_bonus_for_threshold(liquidation_threshold)` when copying `AssetConfig` values into stored positions.

### Proof of Concept
1. A borrower has a supply position stamped with:
   - `liquidation_threshold = 5000` BPS
   - `liquidation_bonus = 5000` BPS
2. Governance executes a ready operation raising `liquidation_threshold` to `8000` BPS while leaving `liquidation_bonus` at `5000` BPS.
3. While the account is healthy, the owner calls:
   ```text
   update_account_threshold(caller, true, [account_id])
   ```
   The higher threshold is not liquidator-favorable, so the refresh proceeds and stores the new threshold.
4. The stored account now has approximately:
   ```text
   base = 5000 BPS
   max  = (10000 / 8000 - 1) * 10000 = 2500 BPS
   ```
5. Collateral value falls or debt accrues until `health_factor < 1 WAD`.
6. A liquidator calls:
   ```text
   liquidate(liquidator, account_id, debt_payments, SeizeMode::Transfer)
   ```
7. `build_liquidation_plan` reaches `calculate_linear_bonus_with_target`; because `hf < target`, it evaluates `2500.checked_sub(5000)` and reverts with `GenericError::MathOverflow`. Any other liquidation payment reaches the same calculation and also reverts.

### Citations

**File:** contracts/controller/src/risk/params.rs (L76-93)
```rust
    if favors_liquidator(position, effective_config)
        && !account.debt_free()
        && !clears_min_hf(
            env,
            cache,
            account,
            hub_asset,
            position,
            effective_config.liquidation_threshold,
        )
    {
        return;
    }

    position.liquidation_threshold = effective_config.liquidation_threshold;
    position.liquidation_bonus = effective_config.liquidation_bonus;
    position.liquidation_fees = effective_config.liquidation_fees;
}
```

**File:** contracts/controller/src/risk/params.rs (L95-100)
```rust
/// Detects a lower threshold or fee, or a higher bonus, than the stored tuple.
fn favors_liquidator(position: &AccountPosition, effective_config: &AssetConfig) -> bool {
    effective_config.liquidation_threshold.raw() < position.liquidation_threshold.raw()
        || effective_config.liquidation_bonus.raw() > position.liquidation_bonus.raw()
        || effective_config.liquidation_fees.raw() < position.liquidation_fees.raw()
}
```

**File:** contracts/controller/src/risk/params.rs (L121-129)
```rust
/// Allows any authenticated caller to refresh listed supply LTV snapshots.
/// `has_risks` also refreshes gated liquidation tuples and enforces health
/// factor >= 1.05. Rejects execution during a flash loan.
pub(crate) fn update_account_threshold(
    env: &Env,
    caller: Address,
    has_risks: bool,
    account_ids: Vec<u64>,
) {
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L81-104)
```rust
/// Returns `weighted_collateral / total_collateral` and the account's bonus
/// bounds. The proportion is zero without collateral.
pub(crate) fn calculate_seizure_proportions(
    env: &Env,
    account: &Account,
    total_collateral: Wad,
    weighted_collateral: Wad,
    cache: &mut Context,
) -> (Wad, BonusBounds) {
    let proportion_seized = if total_collateral > Wad::ZERO {
        weighted_collateral.div(env, total_collateral)
    } else {
        Wad::ZERO
    };

    let bounds = get_account_bonus_params(
        env,
        cache,
        &account.supply_positions,
        total_collateral,
        proportion_seized,
    );

    (proportion_seized, bounds)
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L46-69)
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
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L60-80)
```rust
pub(crate) fn calculate_linear_bonus_with_target(
    env: &Env,
    hf: Wad,
    base: Bps,
    max: Bps,
    curve: &LiquidationCurve,
    target: Wad,
) -> Bps {
    if hf >= target {
        return base;
    }
    let scale = curve.bonus_scale(env, hf, target);

    let bonus_range = max.checked_sub(env, base);
    let bonus_increment = Wad::from(bonus_range.raw()).mul(env, scale).raw();
    let scaled_increment = curve.bonus_factor.apply_to(env, bonus_increment);
    Bps::from(
        base.raw()
            .checked_add(scaled_increment)
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow)),
    )
```

**File:** contracts/controller/src/positions/liquidation/curve.rs (L190-201)
```rust
/// Computes the BPS bonus ceiling for `(1 + bonus) * proportion_seized = 1`.
/// Ceils the proportion to BPS and clamps it to `[1, BPS]`; zero seizure returns zero.
pub(crate) fn max_bonus_for_threshold(env: &Env, proportion_seized: Wad) -> Bps {
    if proportion_seized <= Wad::ZERO {
        return Bps::from(0);
    }

    let eff_thr_bps = mul_div_ceil(env, proportion_seized.raw(), BPS, WAD).clamp(1, BPS);
    let numerator = BPS
        .checked_mul(BPS - eff_thr_bps)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    Bps::from(numerator / eff_thr_bps)
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L36-59)
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
    let offered = liquidation_plan
```
