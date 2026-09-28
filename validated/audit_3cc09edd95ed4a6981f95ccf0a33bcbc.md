### Title
Whole-unit liquidation rounding lets a liquidator seize excess low-decimal collateral - ([File: contracts/controller/src/positions/liquidation/math.rs](contracts/controller/src/positions/liquidation/math.rs))

### Summary
`liquidate` converts a full-close plan for a collateral asset with fewer than `MIN_BORROWABLE_ASSET_DECIMALS` decimals to whole token units. When the discounted value of one whole unit covers all debt plus per-leg repayment rounding, `whole_unit_repayment` promotes the quote to `total_debt`, and `calculate_seized_collateral` rounds the seizure up to one whole collateral unit. This can transfer collateral worth materially more than `repayment × (1 + bonus)` to an unprivileged liquidator.

### Finding Description
An unprivileged caller can invoke `liquidate` with a liquidator address, target `account_id`, debt-payment legs, and `SeizeMode::Transfer`; the entrypoint only requires the liquidator's authorization and `health_factor < 1`. [1](#0-0) [2](#0-1) 

For a solvent-but-unhealthy account with exactly one supply position whose asset has fewer than three decimals, `whole_unit_repayment` computes `unit_at_bonus = floor(unit_value / (1 + bonus))`. If that amount is at least `total_debt + one_base_unit_per_debt_leg`, the function replaces the curve quote with `snap.total_debt`. [3](#0-2) [4](#0-3) 

The resulting plan is marked `full_close`, so repayment inputs are not trimmed and every debt leg is paid up to its ceiling-rounded amount. [5](#0-4) [6](#0-5)  During seizure sizing, a below-three-decimal leg that repays all debt converts the calculated seizure to `to_asset_ceil` and then rescales that whole-unit amount, capped only by the account's held balance. [7](#0-6) [8](#0-7)  Execution pays that whole-unit amount to the liquidator through the normal liquidation withdrawal path. [9](#0-8) 

### Impact Explanation
This permits theft of borrower collateral above the configured liquidation bonus. The liquidator repays `D`, but receives one whole collateral unit worth `U` whenever `floor(U / (1 + bonus)) >= D + rounding_margin`. The excess transferred is approximately `U - D × (1 + bonus)`, subject to token-unit rounding.

For example, with a two-decimal collateral unit worth `$120,000`, debt worth `$100,000`, a liquidation threshold that makes the account unhealthy, and a 5% bonus, the rule promotes the quote to the full `$100,000` debt. The liquidator pays `$100,000` and receives `$120,000` of collateral, whereas the quoted bonus would justify about `$105,000`. The borrower loses roughly `$15,000` beyond the intended bonus.

### Likelihood Explanation
The attack is permissionless and requires no oracle manipulation, privileged role, callback, flash loan, or external route. It requires a listed collateral asset below three decimals, a target account whose only supply position is that asset, enough held collateral to contain one whole unit, and debt small enough that the discounted unit value covers the full debt plus repayment-unit rounding. Those are market/listing and account-state prerequisites rather than attacker capabilities, so the issue is conditional but directly reachable once such an account exists.

### Recommendation
Do not round full-close seizures up to a collateral unit whose value exceeds the repayment plus configured bonus. At minimum:

- cap the seizure at `repayment × (1 + bonus)` in value after whole-unit rounding;
- reject or partially close plans in which whole-unit granularity would exceed that cap;
- account for the maximum effective bonus introduced by unit rounding when admitting low-decimal collateral;
- emit the effective seized-value premium, not merely the curve `bonus_bps`, so integrators can detect outsized seizures.

### Proof of Concept
1. List or use a collateral market with `asset_decimals < MIN_BORROWABLE_ASSET_DECIMALS`.
2. Arrange a target account with exactly one supply position in that market. Let one whole collateral unit be worth `U = $120,000`.
3. Give the account debt legs totaling `D = $100,000`, with liquidation threshold `80%`, so weighted collateral is `$96,000` and `HF = 0.96 < 1`.
4. Use a liquidation bonus of `5%`. Then `floor(U / 1.05) = floor($114,285.71)`, which exceeds `D` plus one native unit of each debt leg.
5. Call:

```text
liquidate(
  liquidator = attacker,
  account_id = victim_id,
  debt_payments = [
    (HubAssetKey { hub_id, asset: debt_token }, ceiling_rounded_debt)
  ],
  seize_mode = SeizeMode::Transfer
)
```

`whole_unit_repayment` promotes the quote to `snap.total_debt`; `calculate_seized_collateral` then rounds the collateral seizure up to one whole unit and caps it only at the held balance. [10](#0-9) [11](#0-10)  The attacker repays `$100,000` and receives one collateral unit worth `$120,000`, exceeding the intended `$105,000` seizure by approximately `$15,000`.

### Citations

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

**File:** contracts/controller/src/positions/liquidation/math.rs (L164-173)
```rust
/// Trims planned repayments above the ideal WAD USD amount and records unused
/// inputs. A payment below the ideal is accepted as offered. A full-close plan
/// is not trimmed: each leg stays at its own ceiling-rounded debt cap, so
/// `repay_usd` can exceed the total debt by per-leg unit rounding. On an
/// insolvent account the trim rounds kept amounts down, so `repay_usd` never
/// exceeds the collateral-backed quote. On a solvent partial plan whose only
/// collateral leg is below `MIN_BORROWABLE_ASSET_DECIMALS`, the ideal rises to
/// one whole unit when the curve quote seizes less than one unit, or to the
/// whole debt when one unit would repay it.
pub(crate) fn normalize_repayment_plan(
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

**File:** contracts/controller/src/positions/liquidation/math.rs (L226-241)
```rust
/// Raises a solvent partial quote to one whole unit when the account's only
/// supply leg is below `MIN_BORROWABLE_ASSET_DECIMALS` and the quoted seizure
/// is below one unit. The raised repayment backs one unit plus one millionth
/// at `unit / (1 + bonus)`; the seizure refunds the fraction it cannot take.
/// Returns the whole debt when one unit at `unit / (1 + bonus)` covers it with
/// one native unit per debt leg to spare, so the plan closes in full and the
/// leg rounds up to one unit. Keeps the quote
/// when the leg holds no whole unit, or when only the margin separates one
/// unit from the whole debt.
fn whole_unit_repayment(
    env: &Env,
    account: &Account,
    snap: &LiquidationSnapshot,
    quote_usd: Wad,
    bonus: Bps,
    cache: &mut Context,
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L262-290)
```rust
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

**File:** contracts/controller/src/positions/liquidation/math.rs (L350-363)
```rust
/// Allocates repayment plus bonus pro-rata by collateral USD value, capped at
/// each held balance. Principal comes from the uncapped seizure; fees apply
/// only to bonus remaining after the cap.
///
/// Transfer amounts round down for partial closes and half-up for full closes.
/// Positive fees floor to asset units with a one-unit minimum, capped by the
/// whole units the pool pays above the repayment share. Credit mode retains a
/// separate exact share representation.
///
/// A partial leg below `MIN_BORROWABLE_ASSET_DECIMALS` seizes whole units only:
/// rounded up to the held balance when the plan repays all debt, down otherwise.
/// Returns the seizures and the repayment USD that the dropped fractions no
/// longer back, floored so the kept repayment rounds toward the protocol.
pub(crate) fn calculate_seized_collateral(
```

**File:** contracts/controller/src/positions/liquidation/math.rs (L401-427)
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

**File:** contracts/controller/src/positions/liquidation/apply.rs (L95-129)
```rust
/// Executes transfer-mode seizure: burns shares, debits pool cash, and pays
/// underlying to the liquidator after withholding the protocol fee.
pub(crate) fn apply_liquidation_seizures(
    env: &Env,
    liquidator: &Address,
    account: &mut Account,
    seized: &Vec<SeizeEntry>,
    cache: &mut Context,
) {
    let mut entries: Vec<PoolWithdrawEntry> = Vec::new(env);
    for entry in seized.iter() {
        enforce_spoke_asset_flags(
            env,
            cache,
            account.spoke_id,
            &entry.hub_asset,
            FreezePolicy::SeizureLeg,
        );

        let position: AccountPosition =
            (&expect_invariant(env, account.supply_positions.get(entry.hub_asset.clone()))).into();
        entries.push_back(PoolWithdrawEntry {
            action: make_pool_action(&position, entry.amount, entry.hub_asset),
            protocol_fee: entry.protocol_fee,
        });
    }
    apply_withdraw_batch(
        env,
        account,
        liquidator,
        WithdrawKind::Liquidation,
        events::PositionAction::LiqSeize,
        &entries,
        cache,
    );
```
