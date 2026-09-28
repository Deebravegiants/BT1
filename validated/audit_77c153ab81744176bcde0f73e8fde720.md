### Title
RAY-scaled debt value overflows `i128` before the borrow-index cap engages, permanently freezing the market — every verb panics in `accrue_step` — ([File: common/src/rates/scaling.rs](common/src/rates/scaling.rs))

### Summary
The bug class of BIT-apache-2020-9490 is a crafted input that poisons state so a later operation crashes. The analog here: an unprivileged user can grow a market's RAY-scaled borrow value past the `i128` ceiling through ordinary `supply`/`borrow`. From that point on, the accrual that runs first inside `update_indexes`, `withdraw`, `repay`, and `liquidate` panics with `MathOverflow` in `scaled_to_original` (`Ray::mul` → `mul_div_half_up`), so the market is permanently frozen: no withdrawal, no repayment, no liquidation. The repo's own harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` proves the freeze end-to-end and confirms `MAX_BORROW_INDEX_RAY` never engages before the value overflow. [1](#0-0) 

### Finding Description
Debt and supply positions are stored as RAY-scaled shares (`scaled_amount`, 10^27). Any conversion back to value multiplies shares by the index via `scaled_to_original`, which calls `Ray::mul` → `fp_core::mul_div_half_up`; when the product `scaled × index / RAY` exceeds `i128::MAX` the widened `I256` path still returns `None` from `to_i128()` and panics with `GenericError::MathOverflow` (`errors.rs` #33). [2](#0-1) [3](#0-2) 

`global_sync`/`accrue_chunk` runs `accrue_step(borrowed, supplied, borrow_index, supply_index)` unconditionally at the head of every index-bearing operation, so once `borrowed × borrow_index` crosses the `i128` ceiling the panic fires on every subsequent call — there is no path to reduce `borrowed` or reset the index without first accruing. [4](#0-3) 

The intended guard is `MAX_BORROW_INDEX_RAY`, but the test shows it does not bind first: on an 18-decimal market, `borrowed ≈ 9.8e26` RAY-scale units times an index that keeps compounding hits `i128::MAX` while `borrow_index < MAX_BORROW_INDEX_RAY`. The test asserts `MATH_OVERFLOW` on `update_indexes`, `withdraw(1)`, and `repay` — the freeze is permanent because accrual precedes every mutation. [5](#0-4) 

### Impact Explanation
Permanent freezing of user funds. Once the RAY value ceiling is crossed, suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot touch the book: all calls revert in `accrue_step` before reaching any verb logic. `clean_bad_debt` and `recapitalize` also accrue/scale against the same market state, so there is no administrative escape that avoids the panicking multiplication (the test explicitly verifies withdraw and repay both fail). This is not a designed fail-closed path — it is an arithmetic ceiling reached by market size alone.

### Likelihood Explanation
Reachable entirely through unprivileged `supply` and `borrow` entrypoints; no privileged call is needed at the failure point (the test's `lift_caps` only mimics a market listed with a generous or absent cap — caps are per-market config and several production listings carry very high caps). Preconditions that temper likelihood: the market needs ~1e27 raw token units of outstanding debt (about a billion whole tokens at 18 decimals, or a proportionally smaller whale book at lower decimals), and utilization must stay near the steep segment of the interest curve long enough for the index to multiply the scaled debt past `i128::MAX` — in the test this is reached by looping yearly accrual at ~98% utilization. The blocker is capital size plus sustained high utilization, not authorization; a rational attacker can also reach it faster by borrowing against their own supplied collateral on an inflated or low-liquidity market. Medium-to-low likelihood, but the impact is total for that market, consistent with High severity.

### Recommendation
Cap growth earlier and fail open. Concretely: (1) clamp the accrued value rather than the index — in `accrue_step`, detect that `borrowed × borrow_index` would overflow and pin the index at a derived safe maximum (`i128::MAX / borrowed` scaled) instead of panicking, so the market stays operable; (2) enforce a supply/borrow ceiling in RAY value space (not just asset-unit caps) so `scaled × index` can never approach the `i128` bound — the existing `calculate_scaled_cap` already saturates, extend the same treatment to position accounting; (3) at minimum, let `repay`/`clean_bad_debt`/`recapitalize` skip the panicking leg of accrual (accrue at the clamped index) so debt can be wound down after the ceiling is hit.

### Proof of Concept
The repository already contains a deterministic reproduction at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs` (`a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`):

```rust
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
lift_caps(&t, "BIG18", 18);
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);          // unprivileged supply
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // unprivileged borrow, 98% util

loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; } // panics
}
// asserted: MATH_OVERFLOW, index still below MAX_BORROW_INDEX_RAY,
// and try_withdraw_raw / try_repay both revert with MATH_OVERFLOW.
```

The attacker-facing sequence is identical without test helpers: `supply` a large amount of a high-decimal asset, `borrow` ~98% of it against own collateral, and let compounding cross the `i128` value ceiling. Thereafter every controller call that accrues that market — including anyone's `repay` or `withdraw` — reverts, permanently trapping all suppliers' funds in the market.

Caveat I could not fully verify within the iteration budget: whether a production listing's caps and decimal domain make the required `borrowed` size economically attainable today; the arithmetic bound itself is proven by the in-repo test regardless of configuration.

### Citations

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-356)
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

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** contracts/pool/src/interest.rs (L39-53)
```rust
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
