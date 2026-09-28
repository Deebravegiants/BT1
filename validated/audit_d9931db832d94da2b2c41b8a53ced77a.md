### Title
RAY-value `i128` overflow in interest accrual permanently freezes a market before the borrow-index cap engages - ([File: common/src/rates/scaling.rs](common/src/rates/scaling.rs))

### Summary
The CVE class is an integer overflow in size/value computation. The analog in XOXNO Lending is the RAY asset-value product `scaled × index` inside accrual: `scaled_to_original` calls `Ray::mul`, which panics with `GenericError::MathOverflow` when `borrowed × borrow_index / RAY` exceeds `i128` [1](#0-0) . Because every state-changing verb runs `global_sync` (which calls `accrue_step`) before doing its own work, once a market's borrowed RAY value crosses the `i128` ceiling the market can never accrue again and every entrypoint reverts [2](#0-1) . The `MAX_BORROW_INDEX_RAY` cap does not protect against this: the value product overflows at a borrowed amount roughly `i128::MAX / index` long before the index itself reaches `10^36` [3](#0-2) .

### Finding Description
`accrue_step` recomputes utilization and indexes each chunk by unscaling `borrowed` and `supplied` through `scaled_to_original` [4](#0-3) . `Ray::mul` is `mul_div_half_up` over `i128`/`I256`, which panics with `MathOverflow` when the result does not fit `i128` [5](#0-4) . A RAY asset value saturates `i128` at roughly `1.7e11` whole tokens; the protocol's own bounds documentation anticipated the index cap protecting the domain, but the harness test proves the value product overflows first: on an 18-decimal market a whale supplier plus a borrower at ~98% utilization drives `borrowed × borrow_index` past `i128::MAX` while `borrow_index < MAX_BORROW_INDEX_RAY` [6](#0-5) . From that point `withdraw`, `repay`, `borrow`, `liquidate`, `clean_bad_debt` and `update_indexes` all trap inside `global_sync` → `accrue_step` → `scaled_to_original`, since accrual precedes every op [7](#0-6) .

### Impact Explanation
Permanent freezing of funds: all suppliers' deposits in that market become unwithdrawable, borrowers cannot repay, liquidations cannot run, and `recapitalize`/`clean_bad_debt` also accrue first, so there is no recovery path. The panic is not a transient fail-closed guard; the overflow is deterministic on stored state (`borrowed` shares and `borrow_index` only grow), so every subsequent call reverts forever [8](#0-7) .

### Likelihood Explanation
Reachable by unprivileged addresses using only `supply` and `borrow`: a whale supplies a very large amount of a high-decimals asset, a borrower takes ~98% utilization, and sustained high borrow interest compounds the RAY value of `borrowed` until `scaled_to_original` overflows. The test exercises exactly this via `supply_raw`/`borrow_raw` plus `advance_time`, and shows the panic arrives while the index cap remains unengaged [9](#0-8) . Cost is dominated by the whale principal on an 18-decimal asset; supply/borrow caps bound it per listing, but `lift_caps`-style configurations (caps set high relative to `i128` RAY domain) leave the path open, and cap checks themselves saturate rather than bound the RAY product [10](#0-9) .

### Recommendation
Cap accrual inputs rather than the index alone: before unscaling, clamp the RAY value domain (e.g., enforce `supplied`/`borrowed` share caps such that `shares × MAX_BORROW_INDEX_RAY / RAY ≤ i128::MAX` at listing/validation, alongside `require_cap_within_asset_domain`), or make `accrue_step` saturate `borrow_index` at `MAX_BORROW_INDEX_RAY` without computing the overflowing value product. At minimum, add a checked fast-path in `global_sync` that detects `borrowed × borrow_index` overflow and clamps `borrow_index` to the cap instead of panicking, so exits and repayments remain possible. Validate with the existing harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` [11](#0-10) .

### Proof of Concept
The repository already contains an executable PoC at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`:

```text
1. List BIG18 (18 decimals) on the steep XLM rate curve; lift caps.
2. BOB supplies 1e9 × 10^18 base units of BIG18.
3. ALICE supplies COL collateral and borrows ~98% of the BIG18 pool.
4. advance_time(YEAR_SECS) repeatedly, calling update_indexes each year.
5. After a few years, update_indexes reverts with MATH_OVERFLOW inside
   accrue_step -> scaled_to_original(borrowed, borrow_index),
   while book.borrow_index < MAX_BORROW_INDEX_RAY.
6. try_withdraw_raw(BOB, "BIG18", 1) and try_repay(ALICE, "BIG18", 1.0)
   both revert with MATH_OVERFLOW — the market is permanently frozen.
```

Root cause: `Cache::calculate_utilization` and `accrue_step` unscale `borrowed`/`supplied` via `scaled_to_original` (`contracts/pool/src/cache/scale.rs:23-24`, `common/src/rates/scaling.rs:14-16`), whose `Ray::mul` panics on `i128` overflow (`common/src/math/fp_core.rs:108-118`), and `global_sync` runs this before every verb (`contracts/pool/src/interest.rs:20-33`).

### Citations

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L26-32)
```rust
pub fn calculate_scaled_cap(env: &Env, cap: i128, decimals: u32, index: Ray) -> Ray {
    Ray::from(fp_core::mul_div_floor_saturating(
        env,
        Ray::from_asset(env, cap, decimals).raw(),
        RAY,
        index.raw(),
    ))
```

**File:** contracts/pool/src/interest.rs (L20-33)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-360)
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
