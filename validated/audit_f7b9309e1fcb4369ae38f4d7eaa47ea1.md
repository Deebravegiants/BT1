### Title
i128 overflow in scaled-to-original accrual permanently freezes an over-sized market - (File: common/src/rates/scaling.rs)

### Summary
Analogous to CVE-2016-5095 (integer overflow during a value amplification), XOXNO Lending's RAY-scaled accounting lets a single unprivileged user push a market's total scaled value past the `i128` ceiling. Every state-changing entrypoint accrues interest first via `global_sync` → `accrue_step` → `scaled_to_original` (`scaled.mul(env, index)` → `fp_core::mul_div_half_up`), which panics with `GenericError::MathOverflow` once `supplied * supply_index / RAY` or `borrowed * borrow_index / RAY` exceeds `i128::MAX`. The panic is permanent: no path reduces `borrowed`/`supplied` before accrual, so `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `update_indexes`, and every controller verb on that market revert forever. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`accrue_step` (shared by the mutator `global_sync` in `contracts/pool/src/interest.rs` and the view) computes total debt and total supplied value by unscaling `borrowed` and `supplied` at the live indexes inside `Cache::calculate_utilization` and `calculate_supplier_rewards`. These are `Ray::mul` calls routed to `mul_div_half_up`, which falls back to `I256` for the product but then panics via `to_i128` when the quotient itself exceeds `i128::MAX`. [4](#0-3) [5](#0-4) [6](#0-5) 

The protocol's own cap validation admits caps up to `max_cap_for_decimals = i128::MAX / 10^(27-decimals)` — about 170 billion whole tokens at 18 decimals — but the RAY-domain value of `supplied * index` or `borrowed * index` can exceed `i128` far below the index cap (`MAX_BORROW_INDEX_RAY = 10^36`, i.e. only 10^9 × RAY) once the market is large. Documentation concedes this: "valid caps and bounded indexes do not guarantee that future accrual fits. Value overflow can occur before the index ceiling and block repayment/withdrawal because those operations accrue first." [7](#0-6) [8](#0-7) 

The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates exactly this cliff: after ~years of accrual at 98% utilization on the XLM curve, `update_indexes` fails with `MATH_OVERFLOW` and subsequent `withdraw` and `repay` calls fail with the same error, with `borrow_index < MAX_BORROW_INDEX_RAY` (the index clamp never engages because the value overflows first). [9](#0-8) 

### Impact Explanation
Permanent freezing of all funds in the affected market: suppliers can never withdraw, borrowers can never repay, liquidators can never seize, and protocol revenue/revenue-share redemption is dead — every controller verb and `update_indexes` routes through `global_sync`, which panics before any bookkeeping runs. The attacker's own collateral is sacrificed, but every other supplier's deposit on the market is locked forever. This satisfies "permanent freezing of funds" and "contract unable to operate" for that market.

### Likelihood Explanation
Requires a market whose cap is admitted near `max_cap_for_decimals` and a high-decimals token with sufficient circulating supply for an attacker (or organic whale activity) to reach ~170 billion whole tokens supplied, plus sustained high utilization (attacker-controlled via their own collateralized borrow) over a long horizon. The cap is within the protocol's own validated domain rather than a misconfiguration, but the capital requirement and multi-year accrual window make exploitation expensive and slow; organic occurrence is more plausible than deliberate attack. Likelihood low-to-medium; impact is permanent and total for that market — overall Medium.

### Recommendation
- In `accrue_step`/`calculate_utilization`, replace panicking `Ray::mul` on `borrowed`/`supplied` with a saturating variant (e.g. `mul_div_*_saturating` or an `I256`-preserving path) so utilization/interest computations degrade gracefully near the ceiling instead of reverting.
- Add a hard guard at deposit/borrow entry: after computing scaled deltas, check that `supplied * supply_index` and `borrowed * borrow_index` fit in `i128` (use `try_mul_div_half_up` / `mul_floor` with an `Option` check) and revert new supply/borrows that would push the market into the un-accrueable region — analogous to how `protocol_fee_shares` already caps minted revenue shares at `i128::MAX − supplied`. [10](#0-9) 
- Tighten `require_cap_within_asset_domain` to bound caps by a value-headroom limit (`i128::MAX / (index ceiling)`) rather than only the rescale domain.

### Proof of Concept
Reproduced by the existing harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs`):

1. List `BIG18` (18 decimals, XLM curve, `max_borrow_rate` 175%) with caps lifted to `max_cap_for_decimals(18)` — admitted by `require_cap_within_asset_domain`. [11](#0-10) 
2. Unprivileged BOB calls `supply` with `1e9 * 10^18` units; ALICE supplies `COL` collateral and calls `borrow` for 98% of the pool. [12](#0-11) 
3. Advance ledger time year-by-year; eventually `update_indexes` returns `MATH_OVERFLOW` with `borrow_index < MAX_BORROW_INDEX_RAY`. [13](#0-12) 
4. `withdraw(BOB, "BIG18", 1)` and `repay(ALICE, "BIG18", 1)` both revert with `MATH_OVERFLOW` — the market is permanently frozen. [14](#0-13)

### Citations

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp_core.rs (L108-118)
```rust
pub fn mul_div_half_up(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    // The zero check runs first so debug and release builds agree on a zero
    // divisor: both surface `DivisionByZero` rather than tripping the assert.
    require_nonzero_divisor(env, d);
    debug_assert!(
        x >= 0 && y >= 0 && d > 0,
        "mul_div_half_up: non-negative x, y and positive d"
    );
    try_mul_div_half_up(env, x, y, d)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

**File:** common/src/math/fp_core.rs (L298-303)
```rust
/// Converts an `I256` to `i128`, panicking with `GenericError::MathOverflow` if it does not
/// fit.
fn to_i128(env: &Env, val: &I256) -> i128 {
    val.to_i128()
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

**File:** contracts/pool/src/interest.rs (L20-53)
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
}

/// Applies one compound step of `delta_ms` to indexes and protocol revenue.
///
/// The arithmetic lives in [`accrue_step`], shared with the read-only
/// `simulate_update_indexes` so the view and the mutator cannot drift.
fn accrue_chunk(env: &Env, cache: &mut Cache, delta_ms: u64) {
    let step = accrue_step(
        env,
        cache.params(),
        cache.borrowed(),
        cache.supplied(),
        cache.borrow_index(),
        cache.supply_index(),
        delta_ms,
    );

    cache.set_borrow_index(step.borrow_index);
    cache.set_supply_index(step.supply_index);
    cache.accrue_revenue(step.revenue_shares);
}
```

**File:** contracts/pool/src/cache/scale.rs (L19-27)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
    }
```

**File:** common/src/rates/index.rs (L73-89)
```rust
pub fn calculate_supplier_rewards(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    new_borrow_index: Ray,
    old_borrow_index: Ray,
) -> (Ray, Ray) {
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);

    (supplier_rewards, protocol_fee)
}
```

**File:** common/src/rates/index.rs (L94-99)
```rust
pub fn protocol_fee_shares(env: &Env, fee: Ray, supply_index: Ray, supplied: Ray) -> Ray {
    let raw = fp_core::mul_div_floor_saturating(env, fee.raw(), RAY, supply_index.raw());

    let headroom = i128::MAX.saturating_sub(supplied.raw());
    Ray::from(raw.min(headroom))
}
```

**File:** common/src/validation.rs (L48-70)
```rust
pub fn max_cap_for_decimals(asset_decimals: u32) -> i128 {
    let Some(exp) = RAY_DECIMALS.checked_sub(asset_decimals) else {
        return 0;
    };
    let upscale = 10i128
        .checked_pow(exp)
        .expect("10^(RAY_DECIMALS - asset_decimals) fits i128 for asset_decimals <= RAY_DECIMALS");
    i128::MAX / upscale
}

/// Panics with `CollateralError::AssetDecimalsTooHigh` if `asset_decimals`
/// exceeds `RAY_DECIMALS`, or with `CollateralError::InvalidBorrowParams` if
/// `cap` exceeds the value returned by `max_cap_for_decimals`.
pub fn require_cap_within_asset_domain(env: &Env, cap: i128, asset_decimals: u32) {
    if RAY_DECIMALS.checked_sub(asset_decimals).is_none() {
        panic_with_error!(env, CollateralError::AssetDecimalsTooHigh);
    }
    assert_with_error!(
        env,
        cap <= max_cap_for_decimals(asset_decimals),
        CollateralError::InvalidBorrowParams
    );
}
```

**File:** docs/reference/formulas.md (L426-437)
```markdown
| Both indexes initially RAY; ceiling 10^36 | 10^9 times initial index; protocol constants |
| Supply-index floor 10^24 | At most 1,000 times the shares minted at index one for the same deposit |
| Borrow APR maximum 2 RAY | 200% annual rate; not a bound on balance growth alone |
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |

The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-361)
```rust
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
}
```
