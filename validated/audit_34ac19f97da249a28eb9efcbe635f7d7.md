### Title
i128 overflow in `scaled_to_original` during accrual permanently freezes a high-utilization market before the borrow-index cap engages - (File: common/src/rates/simulate.rs)

### Summary
The ClamAV bug class is "integer overflow → DoS" (an unbounded loop reached via an overflowed length). The XOXNO analog is an i128 overflow in debt valuation inside the chunked accrual loop: `accrue_step` multiplies `borrowed` (RAY-scaled debt shares) by `borrow_index` before `update_borrow_index` can clamp the index to `MAX_BORROW_INDEX_RAY`. On a large, high-utilization market the product `borrowed * index` exceeds `i128::MAX` while the index is still far below its cap, and `Ray::mul` panics with `MathOverflow`. Since `global_sync` runs before every state transition in the pool, the market can never progress again — no repay, withdraw, liquidate, or bad-debt cleanup. The repository's own harness test proves the freeze end-to-end.

### Finding Description
`contracts/pool/src/interest.rs::global_sync` loops `accrue_chunk` over `MAX_COMPOUND_DELTA_MS` windows, each calling `accrue_step` in `common/src/rates/simulate.rs` [1](#0-0) . The first arithmetic in `accrue_step` is `scaled_to_original(env, borrowed, borrow_index)`, i.e. `borrowed.mul(env, index)`, which uses the panicking `mul` — it widens to `I256` for the intermediate but still panics when the final quotient doesn't fit `i128` [2](#0-1) [3](#0-2) .

The borrow index is only clamped *after* the multiply inside `update_borrow_index` — the pre-clamp product is what overflows, and debt valuation is a separate multiply that overflows earlier still [4](#0-3) . Concretely: `borrowed` is RAY-scaled, so a book of ~`1e36` RAY-raw debt (e.g., 1e9 whole tokens at 18 decimals, or proportionally less at higher decimals' caps) overflows when the borrow index passes ~`i128::MAX / 1e36 ≈ 1.7e38 / 1e36 ≈ 170x` — an index of ~`1.7e29`, far below `MAX_BORROW_INDEX_RAY = 1e36`. On a steep rate curve (the test uses 175% max borrow rate), sustained high utilization reaches that index in a few years of accrual [5](#0-4) .

Once the panic point is crossed, every call that touches the market calls `global_sync` first (supply, withdraw, borrow, repay, liquidate, clean_bad_debt, update_indexes, claim_revenue all accrue first), so every subsequent transaction on that market reverts with `MathOverflow` — verified in the test at lines 343-356 [6](#0-5) .

### Impact Explanation
Permanent freezing of funds for that entire (hub, token) market: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and bad debt cannot be cleaned. There is no index-cap fallback — `update_borrow_index`'s `MAX_BORROW_INDEX_RAY` clamp exists exactly to stop runaway accrual, but the debt-valuation multiply overflows *before* the index reaches the cap, so the intended safety bound never engages [7](#0-6) . The freeze is unrecoverable because the panic occurs inside the accrual prelude common to all paths; there is no escape verb that skips accrual.

### Likelihood Explanation
An unprivileged actor can push a market toward the cliff with ordinary `supply`/`borrow` volume plus elapsed time at high utilization; `update_indexes` (permissionless accrual trigger) is the entrypoint that first trips the panic once the boundary is crossed [8](#0-7) . It requires a whale-scale book and a steep `max_borrow_rate` config — the harness used 1e9 whole tokens at 175% max rate and hit the cliff in "a few years" of simulated accrual — so the likelihood is conditional on governance listing high-decimals assets with aggressive curves and large caps, not on any privileged or off-chain action. No attacker can accelerate index growth beyond the rate curve, so this is Medium, not High.

### Recommendation
Make debt/supply valuation saturating or widened rather than panicking inside the accrual path: e.g., in `accrue_step`, compute `borrowed * borrow_index` via a saturating mul (like `mul_div_floor_saturating` used by `update_supply_index` and `protocol_fee_shares` [9](#0-8) ), and short-circuit accrual when `borrow_index == MAX_BORROW_INDEX_RAY` before any debt valuation multiply. Alternatively, clamp the borrow index at the *start* of `accrue_step` so the valuation multiply always operates on the bounded index, and add a runtime invariant asserting `borrowed * MAX_BORROW_INDEX_RAY < i128::MAX` at listing/cap configuration (extending `require_cap_within_asset_domain`) so a configured cap can never reach the cliff.

### Proof of Concept
The repo ships the PoC: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs::a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` [10](#0-9) .

1. List `BIG18` (18 decimals) on the 175%-max-rate XLM curve with lifted caps; supply 1e9 whole tokens; another account supplies collateral and borrows ~98% of the book.
2. Advance time year-by-year, calling permissionless `update_indexes` each year (`t.try_update_indexes_for(&["BIG18"])`).
3. At the year where `borrowed * borrow_index > i128::MAX`, `update_indexes` returns `MathOverflow` — while `borrow_index < MAX_BORROW_INDEX_RAY`, proving the cap never engaged.
4. From that point on, `withdraw` of even 1 unit and `repay` of 1.0 token both revert with `MathOverflow`, since every verb accrues first — the market is frozen permanently.

### Citations

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

**File:** common/src/rates/simulate.rs (L60-66)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);
```

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L41-44)
```rust
    let grown = fp_core::mul_div_floor_saturating(env, new_value.raw(), RAY, supplied.raw());

    let bounded_old = old_index.raw().min(MAX_SUPPLY_INDEX_RAY);
    Ray::from(grown.min(MAX_SUPPLY_INDEX_RAY).max(bounded_old))
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
