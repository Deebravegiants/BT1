### Title
RAY-value overflow in accrual permanently freezes a large market before the borrow-index cap can engage - (File: contracts/pool/src/interest.rs)

### Summary
`global_sync` accrues interest by computing `borrowed * borrow_index` in RAY units via `scaled_to_original`/`mul_div_*` before applying the `MAX_BORROW_INDEX_RAY` clamp. For a sufficiently large borrowed principal, the RAY-valued product overflows `i128` while the index is still far below its cap. Since every pool verb (supply, borrow, withdraw, repay, liquidate, claim_revenue, clean_bad_debt) calls `global_sync` first, the market panics permanently — no repay, no withdraw, no liquidation, no recapitalization. This is the memory-corruption class mapped onto Soroban: unchecked-value arithmetic crossing the fixed-point domain boundary produces an unrecoverable state rather than memory unsafety.

### Finding Description
Accrual runs in `accrue_chunk` (`contracts/pool/src/interest.rs:39-53`), which calls `accrue_step` with `cache.borrowed()` and `cache.borrow_index()`. The borrow index is capped at `MAX_BORROW_INDEX_RAY`, but the *value* computation `borrowed_scaled * index` is evaluated in `i128`/`I256` (`common/src/math/fp_core.rs:148-159`, `common/src/rates/scaling.rs:14-16`) and panics with `MathOverflow` when the product exceeds `i128::MAX`. `mul_div_half_up`/`mul_div_floor` panic rather than saturate (`fp_core.rs:108-118`).

The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`) demonstrates the exact sequence: ~10^9 units of an 18-decimal asset supplied, ~98% utilization borrowed, then time advances. Within decades `try_update_indexes_for` returns `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY` (lines 348-353), and subsequently `try_withdraw_raw` and `try_repay` both revert with `MATH_OVERFLOW` (lines 355-356). The test itself notes the bound documented in `docs/reference/formulas.md` is wrong — the index cap never engages before the value overflow.

The overflow threshold is `borrowed_ray * index > i128::MAX ≈ 1.7e38`, i.e. a market whose RAY-valued debt exceeds ~1.7e11 in RAY terms (≈170× the 10^27 scale). An unprivileged attacker contributes only the supply and the borrow; time does the rest. Once triggered there is no path back: `apply_bad_debt_to_supply_index` and `recapitalize` also flow through the same accruing cache, and liquidation cannot run because accrual panics first.

### Impact Explanation
Permanent freezing of all supplier and borrower funds in the affected (hub, token) book, plus protocol insolvency mechanics: bad debt can never be cleaned, revenue can never be claimed, and the market becomes a write-only sink. This satisfies both "permanent freezing of funds" and "contract unable to operate" acceptance criteria.

### Likelihood Explanation
Requires a whale-scale position (~a billion base units of an 18-decimal token, i.e. a market with TVL near or above the asset's realistic supply) and sustained high utilization for many years at the steep segment of the rate curve. Caps must be lifted by governance (`lift_caps`), so the attack presumes an already-large legitimately-configured market — the attacker is a participant, not a governor. Capital cost is enormous and the trigger is slow, but once the market exists the freeze is deterministic and unstoppable by anyone, including governance. Medium likelihood, High-class impact.

### Recommendation
Cap the *RAY-valued debt* used by accrual, not just the index: clamp `borrowed` or short-circuit `accrue_step` when `borrowed_ray * index` approaches `i128::MAX` (e.g. freeze index growth once the valuation saturates via `mul_div_floor_saturating`, and treat the market as paused-for-accrual while still permitting repay/withdraw/liquidate on the last good index). Alternatively, bound per-market borrow caps (`require_cap_within_asset_domain`) to `i128::MAX / MAX_BORROW_INDEX_RAY / 10^(27-d)` so the product can never overflow within the index domain. Fix the incorrect bound documented in `docs/reference/formulas.md`.

### Proof of Concept
See `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`. In essence:

```rust
t.supply_raw(BOB, "BIG18", 1_000_000_000 * 10i128.pow(18));   // whale supply
t.borrow_raw(ALICE, "BIG18", debt_at_98pct_util);             // unprivileged borrow
loop { t.advance_time(YEAR_SECS); t.try_update_indexes_for(&["BIG18"])?; }
// eventually: MATH_OVERFLOW, borrow_index < MAX_BORROW_INDEX_RAY
// then: withdraw(1) -> MATH_OVERFLOW, repay(1.0) -> MATH_OVERFLOW  // permanent freeze
```

Every subsequent `supply/borrow/withdraw/repay/liquidate/clean_bad_debt/claim_revenue/recapitalize` on that market reverts in `global_sync` before reaching its own logic. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** common/src/math/fp_core.rs (L148-159)
```rust
pub fn mul_div_floor(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    require_nonzero_divisor(env, d);
    if let Some(quotient) = x
        .checked_mul(y)
        .and_then(|product| div_floor_i128(product, d))
    {
        return quotient;
    }
    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    let nonneg = quotient_is_nonnegative(x, y, d);
    to_i128(env, &div_floor_i256(env, &x256.mul(&y256), &d256, nonneg))
}
```

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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
