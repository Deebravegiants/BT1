### Title
Borrower can keep an HF < 1 account permanently inside the whole-unit liquidation "revert band" by repaying accrued interest, indefinitely denying liquidation - (File: contracts/controller/src/positions/liquidation/math.rs)

### Summary
For an account whose only supply leg is a collateral asset below `MIN_BORROWABLE_ASSET_DECIMALS` (3 decimals), `whole_unit_repayment` can leave the curve quote unchanged when the debt `D` sits in the band `floor(U / (1 + b)) - R < D <= ceil((U + m) / (1 + b))`. In that state every `liquidate` offer either backs less than one whole unit — and is dropped with the whole repayment released — or is left unraised, so `plan.validate` reverts with `InvalidPayments` (16). The documentation treats this as a transient state that "accrual or a price move ends" — but the borrower can re-enter the band at will by repaying the accrued interest through the permissionless `repay` path, keeping `D` pinned inside the band forever while `HF < 1`.

### Finding Description
`normalize_repayment_plan` only raises the ideal repayment for a solvent account whose single supply leg is below 3 decimals via `whole_unit_repayment`, and the function returns the unmodified curve quote in the band between the rule-1 full-close ceiling and the rule-2 one-unit raise. [1](#0-0)  With the quote unchanged, `calculate_seized_collateral` floors the partial seizure of the sub-3-decimal leg to zero whole units, dropping the leg. [2](#0-1)  `build_liquidation_plan` then releases the unbacked repayment entirely and `plan.validate` reverts `InvalidPayments`, so no offer — partial or debt-sized — can execute. [3](#0-2)  The documented escape is interest accrual pushing `D` above `raised`, but `repay` remains callable on an unhealthy account, so the owner can repay exactly the accrued delta each time `D` approaches `raised`, re-centering `D` inside the band. Because the account stays solvent (`C >= D`), the permissionless `clean_bad_debt` gate (`total_debt > total_collateral` and collateral <= $5) can never open, and there is no other unprivileged path that removes the position. [4](#0-3) 

### Impact Explanation
A borrower can hold a permanently under-threshold (`HF < 1`) position that no liquidator can touch, for the cost of paying the interest that would accrue anyway. The protocol's only unprivileged risk-removal mechanisms — `liquidate` and `clean_bad_debt` — both fail for such an account, so the unhealthy debt persists until governance intervenes (`force_socialize_bad_debt` is owner-only and also requires `D > C`) or the collateral price moves on its own. Any adverse price move while liquidation is denied converts directly into socialized bad debt for suppliers, i.e., the DoS of the liquidation path is a direct precursor to protocol insolvency.

### Likelihood Explanation
Fully attacker-controlled and cheap: the borrower chooses the debt size at open (`borrow`), the band `raised - (unit_at_bonus - R) = m + R` is non-empty for every debt leg composition, and maintaining the state only requires periodic small `repay` calls against the same interest the debt owes regardless. No privileged action, no oracle manipulation, and no timing race is needed; any account built around a single sub-3-decimal collateral listing qualifies.

### Recommendation
Close the band deterministically: when neither rule 1 nor rule 2 applies, promote the ideal to `D` (full close, leg rounds up to the held unit) or clamp it to `ceil((U + m) / (1 + b))` unconditionally when that value backs at least one unit, rather than leaving the curve quote. Alternatively, let a partial plan that seizes zero units still settle the repayment, or treat accounts parked in this band as eligible for `clean_bad_debt`/`force_socialize_bad_debt` without requiring `D > C`.

### Proof of Concept
1. Borrower supplies `k` whole units of a listed sub-3-decimal collateral `LIQ` and borrows a USD-denominated debt `D0` sized so that after a moderate price drop, `HF < 1` and `floor(U/(1+b)) - R < D <= ceil((U+m)/(1+b))` — exactly the band exercised by the `wul_*` margin-band fixtures. [5](#0-4) 
2. Any liquidator calling `liquidate(account_id, payments, SeizeMode::Transfer)` receives `InvalidPayments` for every offer size: sub-unit offers seize nothing, and debt-sized offers are neither promoted to full close nor raised to one unit.
3. Whenever interest accrual pushes `D` to the top of the band, the borrower calls `repay` with the accrued delta, returning `D` inside the band. `is_liquidatable` stays true the entire time, yet no liquidation can execute; `clean_bad_debt` reverts `CannotCleanBadDebt` because `C >= D`.

### Citations

**File:** contracts/controller/src/positions/liquidation/math.rs (L275-290)
```rust
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

**File:** contracts/controller/src/positions/liquidation/plan.rs (L73-95)
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
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L229-235)
```rust
    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);
```

**File:** tests/test-harness/tests/fuzz/whole_unit_liquidation.rs (L856-868)
```rust
            if debt_sized && units_before >= 1 {
                prop_assert!(
                    solvent && band,
                    "P8: a debt-sized offer reverted outside the margin band; {}",
                    ctx
                );
                bump(stats, "revert InvalidPayments: debt-sized, margin band");
                record_max(
                    stats,
                    "debt-sized band revert: k * LT * (1 + b)",
                    &(rat(units_before) * rat(w.lt) * rat(BPS + bonus_m) / rat(BPS * BPS)),
                );
                if units_before == 1 {
```
