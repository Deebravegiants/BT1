### Title
i128 overflow panic in accrual permanently freezes a whale-scale market before the borrow-index cap engages - (File: common/src/rates/index.rs)

### Summary
The borrow index is capped at `MAX_BORROW_INDEX_RAY` inside `update_borrow_index`, but the accrual step first computes `borrowed * index` products in `calculate_supplier_rewards` (and `scaled_to_original` via utilization) that panic with `MathOverflow` once the scaled ray-value exceeds `i128::MAX`. On a large market at sustained high utilization, the index grows past ~170x and the next `update_indexes` — permissionless — bricks the market: every state-changing entrypoint accrues first, so no repay, withdraw, or liquidation can ever execute again.

### Finding Description
`update_borrow_index` multiplies `old_index * interest_factor` and then clamps to `MAX_BORROW_INDEX_RAY`, so the index itself never overflows [1](#0-0) . However `calculate_supplier_rewards`, invoked each accrual chunk by `accrue_step`, computes `borrowed.mul(env, old_borrow_index)` and `borrowed.mul(env, new_borrow_index)` — `Ray::mul` panics with `GenericError::MathOverflow` when `scaled * index / RAY` exceeds `i128::MAX` [2](#0-1) . `global_sync` unconditionally runs this accrual before any mutation [3](#0-2) , and the in-repo test confirms the market freezes — repay and withdraw both revert with `MATH_OVERFLOW` and "the index cap did not engage before the value overflow" [4](#0-3) .

### Impact Explanation
Permanent freezing of funds. Once `borrowed_scaled * borrow_index` crosses the `i128::MAX` ray-value ceiling, every pool/controller verb (supply, withdraw, repay, borrow, liquidate, clean_bad_debt, claim_revenue) traps inside accrual. Suppliers can never exit, borrowers cannot repay, and liquidators cannot clear the position — the market's entire TVL is frozen with no recovery path, since the cap that was designed to bound growth is unreachable code by the time it would matter.

### Likelihood Explanation
Requires a whale-scale book (the documented scenario uses ~1e9 whole tokens at 18 decimals, i.e. ~1e36 ray supplied) at sustained ~98% utilization on a steep rate curve for several years, or a smaller book correspondingly longer. Each ingredient is reachable by an unprivileged address: `supply`, `borrow`, and the permissionless `update_indexes` that lands the fatal accrual. The attacker does not even need intent — any large organic market drifts into the cliff. The needed capital is large but the trigger transaction itself is a single `update_indexes` call.

### Recommendation
Order the cap before the multiply: clamp inside `calculate_supplier_rewards`/`accrue_step` by comparing `new_borrow_index` against `min(MAX_BORROW_INDEX_RAY, i128::MAX * RAY / borrowed)` before computing `borrowed * index`, or compute total debt via a saturating widening multiply (`I256`) so accrual degrades to capped accounting rather than trapping. Additionally, `update_supply_index` should bound `supplied * old_index` the same way, since `update_supply_index_capped` documents this identical panic domain [5](#0-4) .

### Proof of Concept
Reproduced by the in-repo test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`: list an 18-decimal market on the XLM rate curve, `supply` 1e9 whole tokens, `borrow` ~98% of it against collateral, then call `update_indexes` yearly. Within a few years `try_update_indexes_for(["BIG18"])` fails with `MATH_OVERFLOW`, `borrow_index < MAX_BORROW_INDEX_RAY`, and both `withdraw` and `repay` fail with the same error [6](#0-5) .

### Citations

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

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-356)
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
```

**File:** certora/common/spec/rates_rules.rs (L316-320)
```rust
/// Residual hidden bound: `update_supply_index` computes
/// `supplied.mul(old_index)`, which panics with `MathOverflow` once
/// `supplied * old_index / RAY` leaves `i128`. Sunbeam treats that panic as
/// `assume(false)`, so the trap, not an assume, prunes the upper corner of the
/// `supplied x old_index` box. The assertion is proved on the rest.
```
