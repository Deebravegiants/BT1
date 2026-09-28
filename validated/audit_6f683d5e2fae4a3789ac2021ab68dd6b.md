### Title
RAY-value overflow in `scaled_to_original` permanently freezes a saturated market before the borrow-index cap engages — (File: common/src/rates/scaling.rs)

### Summary
`scaled_to_original` unscales a scaled RAY share balance by `Ray::mul`, which panics with `MathOverflow` whenever `scaled * index / RAY` exceeds `i128::MAX` (≈1.7e38). Because the borrow index is only capped at `MAX_BORROW_INDEX_RAY = 1e36` (a 1e9× ceiling) while the product `borrowed_scaled * borrow_index` hits `i128::MAX` far earlier on a large book, an accrual step panics before the cap can engage. Every mutating verb on the market — `withdraw`, `repay`, `borrow`, `supply`, `liquidate`, `clean_bad_debt`, `update_indexes`, `recapitalize`, `claim_revenue` — syncs/accrues the market first, so once the debt value crosses the RAY-domain ceiling the entire market is permanently bricked: suppliers cannot withdraw and borrowers cannot repay. [1](#0-0) [2](#0-1) 

### Finding Description
The accrual pipeline computes current debt and supply values via `scaled_to_original` (`scaled.mul(env, index)` → `fp_core::mul_div_half_up`), which widens to `I256` but returns `None`/panics when the *result* does not fit `i128` [3](#0-2) . `accrue_step` calls it for `borrowed` and `supplied` at the top of every chunk [4](#0-3) , and `update_borrow_index` clamps the *index* to `1e36`, not the *value* [5](#0-4) . The docs concede the gap: "Value overflow can occur before the index ceiling and block repayment/withdrawal because those operations accrue first" [6](#0-5) .

Reachability is entirely unprivileged: `supply` admits up to ≈170 billion whole tokens at 18 decimals (`i128::MAX / 10^(27−d)`, the admitted cap maximum), and `borrow` up to the liquidity. A single attacker supplying ~1e9 units of an 18-decimal asset and borrowing ~98% creates `borrowed_scaled ≈ 9.8e35` RAY; the borrow index then only needs ~170× growth — reachable at the XLM-curve steep segment / near the 200% APR `MAX_BORROW_RATE_RAY` — before `borrowed * index` overflows. The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates exactly this: accrual panics with `MATH_OVERFLOW`, `borrow_index < MAX_BORROW_INDEX_RAY` (cap never engages), and subsequent `withdraw`/`repay` revert identically [7](#0-6) .

Because every pool entry point calls `ops::synced_market`/accrue first (e.g. `seize::apply` [8](#0-7) ), there is no escape verb: liquidation and `clean_bad_debt` also sync the market and hit the same panic.

### Impact Explanation
Permanent freezing of all funds in the affected market plus protocol insolvency: suppliers' claims are unwithdrawable, outstanding debt can never be repaid or liquidated, and `recapitalize` (which also syncs) cannot repair the book. All supplier principal in that market is locked forever.

### Likelihood Explanation
Requires whale-scale capital (up to the ~170B-token admitted cap) on a high-decimals market and sustained high utilization so the borrow index compounds to the value-overflow threshold (index ≈ `i128::MAX / borrowed_scaled`) — on the order of ~170× growth, i.e. several years at maximum curve rates. Once the debt exists, however, no governance or user action can prevent the cliff other than repaying before it, and after it is crossed the freeze is irreversible. The attacker's own capital is at stake during accrual, lowering practical likelihood; hence Medium–High rather than Critical.

### Recommendation
Saturate rather than panic in `scaled_to_original` when used for *market totals* in accrual (e.g. a `mul_floor_saturating` variant for `borrowed`/`supplied` valuation inside `accrue_step`/`synced_market`), or clamp `borrowed`/`supplied` scaled totals and per-position unscaling to `i128::MAX` and route repayment/withdrawal through saturating valuation so exits remain possible past the cliff. Alternatively enforce caps so `cap_ray * MAX_BORROW_INDEX_RAY ≤ i128::MAX` at listing, shrinking admitted caps far below the current ~170B-token bound.

### Proof of Concept
See `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs::a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` [9](#0-8) : supply `1e9` BIG18 (18 decimals), borrow 98% of it against COL collateral, advance time yearly; `try_update_indexes_for(["BIG18"])`, `try_withdraw_raw`, and `try_repay` all fail with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, leaving the market permanently frozen.

### Citations

**File:** common/src/rates/scaling.rs (L14-16)
```rust
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

**File:** common/src/math/fp_core.rs (L122-143)
```rust
pub fn try_mul_div_half_up(env: &Env, x: i128, y: i128, d: i128) -> Option<i128> {
    if x < 0 || y < 0 || d <= 0 {
        return None;
    }
    let half = d / 2;

    // Fast path: the biased product fits `i128`, so the whole computation is
    // native. `x * y + half` is non-negative here, so `/` is the floor the
    // widened path would produce.
    if let Some(biased) = x
        .checked_mul(y)
        .and_then(|product| product.checked_add(half))
    {
        return Some(biased / d);
    }

    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    x256.mul(&y256)
        .add(&I256::from_i128(env, half))
        .div(&d256)
        .to_i128()
}
```

**File:** common/src/rates/simulate.rs (L60-64)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);
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

**File:** docs/reference/formulas.md (L432-437)
```markdown
The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
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

**File:** contracts/pool/src/ops/seize.rs (L18-27)
```rust
pub(crate) fn apply(env: &Env, entry: &PoolSeizeEntry) -> MarketStateSnapshot {
    require_nonneg_amount(env, entry.position.scaled_amount);
    let mut cache = ops::synced_market(env, &entry.hub_asset);
    let position = Ray::from(entry.position.scaled_amount);

    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
```
