### Title
RAY-value overflow in accrual permanently freezes a large market — `borrowed * borrow_index` exceeds `i128` before the index cap engages - (File: `common/src/rates/scaling.rs`)

### Summary
Analogous to the Thrift compact-protocol integer overflow, this protocol's own fixed-point pipeline has an overflow cliff: the RAY-scaled debt valuation `borrowed_scaled * borrow_index` panics with `GenericError::MathOverflow` once the product exceeds `i128::MAX`. Because every state-mutating entrypoint runs `global_sync` → `accrue_step` → `scaled_to_original` first, crossing this boundary permanently bricks the market: `repay`, `withdraw`, `liquidate`, `borrow`, `supply`, `clean_bad_debt`, `flash_loan`, and even `update_indexes` all revert. The `MAX_BORROW_INDEX_RAY` cap does not prevent it — the panic happens in the value multiplication, not the index.

### Finding Description
`scaled_to_original` is a bare `scaled.mul(index)` ( [1](#0-0) ), which routes to `mul_div_half_up`; when `x * y + d/2` doesn't fit `i128` it widens to `I256` but then `to_i128()` returns `None` and panics with `MathOverflow` if the *result* doesn't fit `i128` ( [2](#0-1) ). In accrual, `accrue_step` calls `scaled_to_original(borrowed, borrow_index)` ( [3](#0-2) ) and `calculate_supplier_rewards` multiplies `borrowed` by the new index inside `calculate_supplier_rewards`/`accrue_step`. `update_borrow_index` multiplies before clamping ( [4](#0-3) ), so an index near the cap times a large `borrowed` scaled value overflows regardless of the cap.

`global_sync` runs this on every cache-touching operation and there is no fallback ( [5](#0-4) ). The project's own regression test proves the freeze: at ~1 billion whole tokens of an 18-decimal asset at ~98% utilization on a steep rate curve, `update_indexes` starts reverting with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, after which `withdraw` and `repay` also revert with the same error — "no repay, no withdraw, no liquidation" ( [6](#0-5) ).

### Impact Explanation
Permanent freezing of funds. Once `borrowed_scaled * index / RAY` exceeds `i128::MAX` (≈1.7e38 ray units — a pool holding on the order of 10^17–10^18 raw units of an 18-decimal token at index ~10–170), the market cannot be unwound by anyone: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and bad debt cannot be cleaned, because each of those paths accrues first and hits the same panic. There is no index rollback and no accrual-free escape entrypoint. This is not a fail-closed DoS on a single call — it is a terminal state for the market.

### Likelihood Explanation
Reaching the cliff requires a very large market (`borrowed` RAY value near `i128::MAX / index`) and sustained high utilization over many accrual chunks, as the test shows — dozens of year-chunks at 98% utilization on the steep XLM curve segment. It also requires supply/borrow caps that admit the scale; caps are validated against the asset domain but the test had to lift default caps to reach the boundary, so realization depends on a high-decimal market being listed with very large caps. An unprivileged user can drive the trajectory entirely with `supply`, `borrow`, and `update_indexes`; no privileged call is needed once caps admit the size. Medium–low likelihood, but the impact is total and unrecoverable.

### Recommendation
Add a saturating or capped path for accrual-time valuations so a single overflow can't brick the market: e.g., use `mul_div_floor_saturating` inside `accrue_step`'s `scaled_to_original`/`calculate_supplier_rewards` calls, or clamp `borrowed`'s effective valuation to `i128::MAX` and let the index cap (and `MAX_BORROW_INDEX_RAY`) bound growth instead of panicking. Alternatively, enforce at listing/config time that `supply_cap_ray * MAX_BORROW_INDEX_RAY` stays inside `i128`, and add an accrual-free emergency repay/withdraw path that operates on stored indexes so markets can always be unwound.

### Proof of Concept
Reproduced by the existing test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` ( [7](#0-6) ):

1. List an 18-decimal market; an unprivileged user supplies `1e9 * 10^18` units, another supplies collateral and borrows ~98% of it.
2. Advance time year-by-year calling `update_indexes`. Each call runs `global_sync` → `accrue_step`; the borrow index compounds at the steep-curve rate.
3. After enough chunks, `scaled_to_original(borrowed, new_borrow_index)` returns `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY` — the index cap never engages.
4. All subsequent `repay(ALICE, BIG18, …)`, `withdraw(BOB, BIG18, …)`, `liquidate`, and `update_indexes` calls revert with `MATH_OVERFLOW`. Funds are permanently frozen.

Uncertainty: whether production cap validation (`require_cap_within_asset_domain`) plus realistic admin caps would always prevent reaching the cliff could not be fully verified in this pass; the test required `lift_caps`, so exploitability depends on a listed market permitting a scale near the domain ceiling.

### Citations

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp_core.rs (L138-143)
```rust
    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    x256.mul(&y256)
        .add(&I256::from_i128(env, half))
        .div(&d256)
        .to_i128()
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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-361)
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
}
```
