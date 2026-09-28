### Title
Accrual overflow permanently freezes an overlarge high-utilization market - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary

An unprivileged borrower can create a market state where future accrual panics while converting scaled debt or supply to its RAY value. Once the product crosses `i128::MAX`, every pool operation that accrues the market first reverts, permanently blocking repayment, withdrawal, and liquidation for that market. [1](#0-0) [2](#0-1) 

### Finding Description

`accrue_step` computes `borrowed_original` and `supplied_original` with `scaled_to_original`, which multiplies the scaled RAY amount by the index before utilization, rates, index updates, rewards, and revenue accounting run. [1](#0-0) [3](#0-2) 

The borrow index itself is bounded at `10^36`, but the code has no equivalent bound on `borrowed * borrow_index` or `supplied * supply_index`, so value multiplication can overflow before either index reaches its ceiling. [4](#0-3) [5](#0-4) 

The production accrual loop calls this step for every elapsed chunk and only marks the market accrued after all chunks succeed. [6](#0-5)  Consequently, one failed multiplication rolls back the entire operation, including economically safe paths such as repayment and withdrawal. [2](#0-1) 

### Impact Explanation

All supplied and borrowed funds in the affected market become permanently inaccessible through the normal pool lifecycle because even reducing exposure requires accrual to complete first. [6](#0-5) [7](#0-6) 

The existing harness demonstrates the terminal state: `update_indexes` fails with `MathOverflow`, followed by both a one-unit withdrawal and a partial repayment failing with the same error. [8](#0-7) 

### Likelihood Explanation

The trigger requires a very large configured cap, a high-utilization/high-rate market, and enough elapsed time for index growth to push the market's RAY value over `i128::MAX`. [9](#0-8) [10](#0-9) 

The required state is nevertheless reachable through the unprivileged `supply`, `borrow`, and permissionless `update_indexes` paths; the controller allows these calls subject to market and account authorization checks. [11](#0-10) 

The harness uses a permitted 175% maximum annual rate and 98% utilization, reaches the cliff before `MAX_BORROW_INDEX_RAY`, and confirms that the borrow-index cap does not prevent the overflow. [2](#0-1) 

### Recommendation

Bound or saturate `scaled * index` wherever accrual consumes the result, rather than relying on index ceilings to keep the derived value representable. [3](#0-2) [5](#0-4) 

Enforce caps against the projected future value at `MAX_BORROW_INDEX_RAY` and `MAX_SUPPLY_INDEX_RAY`, or introduce a market-value ceiling that refuses new exposure before accrual can cross `i128::MAX`. [4](#0-3) [12](#0-11) 

Also consider ordering accrual so repayment-only or withdrawal-only operations can proceed under a capped/saturated valuation instead of rolling back the market. [6](#0-5) 

### Proof of Concept

1. On a configured market with 18 decimals, a high maximum borrow rate, maximum utilization allowed, and caps lifted to the decimal-domain maximum, call `supply(caller, 0, [(hub_asset, 1_000_000_000 * 10^18)])`; retain the returned `account_id`. [13](#0-12) 
2. Supply sufficient collateral and call `borrow(caller, account_id, [(hub_asset, 980_000_000 * 10^18)], None)` to establish 98% utilization. [14](#0-13) 
3. As time passes, call `update_indexes(caller, [hub_asset])`; after the borrow index grows enough, `scaled_to_original(borrowed, borrow_index)` overflows and the call returns `MathOverflow`. [15](#0-14) [16](#0-15) 
4. Subsequent `withdraw(caller, account_id, [(hub_asset, 1)], None)` and `repay(caller, account_id, [(hub_asset, amount)])` calls still fail with `MathOverflow` because they enter the same accrual path before applying their requested operation. [7](#0-6) 

The in-repository reproduction is `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`, which asserts that the overflow occurs below `MAX_BORROW_INDEX_RAY` and that both repayment and withdrawal subsequently revert. [17](#0-16)

### Citations

**File:** common/src/rates/simulate.rs (L60-71)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);

    let new_supply_index = update_supply_index(env, supplied, supply_index, supplier_rewards);
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L26-38)
```rust
/// Steep XLM stress curve: 175 percent max borrow rate, optimal at 75 percent.
fn xlm_curve() -> MarketParamsPreset {
    MarketParamsPreset {
        max_borrow_rate: RAY * 175 / 100,
        base_borrow_rate: RAY / 100,
        slope1: RAY * 4 / 100,
        slope2: RAY * 10 / 100,
        slope3: RAY * 150 / 100,
        mid_utilization: RAY * 50 / 100,
        optimal_utilization: RAY * 75 / 100,
        max_utilization: RAY,
        reserve_factor: 2000,
    }
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L81-95)
```rust
fn lift_caps(t: &LendingTest, asset: &str, decimals: u32) {
    let cap = max_cap_for_decimals(decimals);
    let cfg = t.get_asset_config(asset);
    t.edit_asset_in_spoke_caps(
        asset,
        HARNESS_SPOKE,
        true,
        true,
        cfg.loan_to_value,
        cfg.liquidation_threshold,
        cfg.liquidation_bonus,
        cap,
        cap,
    );
}
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-360)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
fn a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap() {
    let mut t = LendingTest::new()
        .with_market(big("BIG18", 18, xlm_curve()))
        .with_market(col())
        .with_max_utilization_disabled_all_markets()
        .build();
    lift_caps(&t, "BIG18", 18);
    lift_caps(&t, "COL", 7);
    let principal = BILLION * 10i128.pow(18);
    t.supply_raw(BOB, "BIG18", principal);
    let debt = principal / 100 * 98;
    t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
    t.borrow_raw(ALICE, "BIG18", debt);

    let mut years = 0u32;
    let failure = loop {
        years += 1;
        assert!(
            years <= 40,
            "no cliff within 40 years; the bound in docs/reference/formulas.md is wrong"
        );
        t.advance_time(YEAR_SECS);
        if let Err(e) = t.try_update_indexes_for(&["BIG18"]) {
            break e;
        }
    };
    let failed: Result<(), soroban_sdk::Error> = Err(failure);
    assert_contract_error(failed, errors::MATH_OVERFLOW);
    let last = book(&t, "BIG18");
    assert!(
        last.borrow_index < MAX_BORROW_INDEX_RAY,
        "the index cap did not engage before the value overflow"
    );
    // The market is frozen: exits and repayments accrue first and hit the same panic.
    assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
    assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
    std::println!(
        "ray-value cliff reached after {years} years at 98 percent utilization on the XLM curve; last index x{:.1}",
        last.borrow_index as f64 / RAY as f64
    );
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** common/src/rates/index.rs (L13-19)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
}
```

**File:** contracts/pool/src/interest.rs (L20-32)
```rust
pub(crate) fn global_sync(env: &Env, cache: &mut Cache) {
    if !cache.needs_accrual() {
        return;
    }

    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
```

**File:** scripts/permissionless_entrypoints.txt (L69-77)
```text
controller::supply | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may top up an account they do not own, but only for hub assets it already holds a supply position in; a caller that is neither the owner nor an active delegate cannot open a new asset slot, and account_id 0 creates an account owned by the caller.
controller::repay | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may repay any account's debt. Funds are pulled from the caller's own balance and credited from the measured receipt; the target's liabilities can only fall.
controller::liquidate | caller-auth | INV-AUTH-03, INV-LIQ-01, INV-LIQ-02 | Anyone may liquidate an account whose health factor is below one, including the account's own owner; in Credit seize mode the receiving account must be a different account that the liquidator owns or is an active delegate of, and seizure stays coupled to the debt actually repaid.
controller::clean_bad_debt | caller-auth | INV-AUTH-03, INV-LIQ-04 | Anyone may socialize an insolvent account's residual debt, but only once its remaining collateral is at or below the dust threshold; only the owner-gated force_socialize_bad_debt omits the dust cap.
controller::recapitalize | caller-auth | INV-AUTH-03, INV-ACCT-02, INV-ACCT-03 | Anyone may donate their own funds to cover a market's backing shortfall; only the measured receipt up to the shortfall is applied and the excess is refunded to the payer.
controller::update_indexes | caller-auth | INV-AUTH-03, INV-IDX-04 | Keeper maintenance: accrues interest to the current ledger timestamp. Accrual never lowers the borrow or supply index and each chunk's rate is capped at max_borrow_rate, so the caller chooses only the accrual timing and cannot lower anyone's balance.
controller::claim_revenue | caller-auth | INV-AUTH-03, INV-ACCT-06 | Keeper maintenance: sweeps accrued protocol revenue to the governance-configured accumulator. The caller picks the timing, never the recipient.
controller::update_account_threshold | caller-auth | INV-AUTH-03, INV-RISK-01 | Keeper maintenance: restamps cached risk parameters to their currently listed values. Without has_risks it restamps LTV only, which the health factor does not read; with has_risks set it reverts unless the account clears the update health-factor floor, so it cannot be used to push an account into liquidation.
controller::flash_loan | caller-auth | INV-AUTH-03, INV-FLASH-01, INV-FLASH-02 | Anyone may borrow within a single call; the pool verifies principal plus fee is back before returning, and the flash-loan flag blocks monetary reentrancy into position flows.
```

**File:** docs/reference/formulas.md (L432-437)
```markdown
The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```
