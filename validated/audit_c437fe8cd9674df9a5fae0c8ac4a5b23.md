### Title
RAY-scaled debt/supply value overflows `i128` during interest accrual, permanently freezing all market operations - (File: contracts/pool/src/interest.rs)

### Summary
`global_sync` accrues interest on every mutating entrypoint by computing the RAY-scaled value `total_shares * index` via `scaled_to_original` → `Ray::mul` → `mul_div_half_up`. When `total_shares * borrow_index` exceeds `i128::MAX`, the widened `I256` quotient still does not fit `i128`, so `to_i128` panics with `GenericError::MathOverflow`. Once a market's total borrowed or supplied value crosses this ceiling, every subsequent accrual panics, and since all controller verbs (supply, borrow, withdraw, repay, liquidate, clean_bad_debt) accrue first, the market is frozen permanently — there is no path that reduces the stored share totals without first running the panicking accrual.

### Finding Description
The CVE's class is an unchecked arithmetic overflow reachable from attacker-influenced input causing a crash/DoS. In XOXNO Lending the analog is the RAY value ceiling in the accrual path:

- `interest.rs::accrue_chunk` calls `accrue_step(env, params, borrowed_shares, supplied_shares, borrow_index, supply_index, delta_ms)`, which internally values the books via `scaled_to_original(shares, index)` (`common/src/rates/scaling.rs:14`).
- `scaled_to_original` is `scaled.mul(env, index)` → `mul_div_half_up` (`common/src/math/fp_core.rs`), which returns the exact quotient in `i128` and panics `MathOverflow` when `shares * index / RAY ≥ i128::MAX` (i.e. the asset's RAY-scaled book value exceeds ~1.7e38).
- A position on an 18-decimal market holding ~10^9 whole tokens is `1e36` raw ray; the value ceiling is ~170x that, so once the borrow index grows past ~170 RAY the multiplication overflows. The protocol's own regression test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356) demonstrates exactly this: after sustained ~98% utilization, `try_update_indexes`, `try_withdraw`, and `try_repay` all revert with `MATH_OVERFLOW`, and the stored `borrow_index` is still below `MAX_BORROW_INDEX_RAY`, so the intended index cap never engages.
- `global_sync` runs at the top of every state-changing op; the panic occurs before any share mutation, so no verb can reduce `borrowed`/`supplied` below the overflow threshold. Governance `recapitalize` also accrues first and cannot unstick it.

### Impact Explanation
Permanent freezing of funds: once `total_borrowed_shares * borrow_index / RAY` (or the supply twin) exceeds `i128::MAX`, every operation on that market reverts forever. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot seize, and `clean_bad_debt`/`recapitalize` cannot run because accrual precedes them. All user funds held in that market's physical pool balance are locked for the lifetime of the contract.

### Likelihood Explanation
Medium. Triggering requires (a) a market whose total position value is within ~1/170 of `i128::MAX` — reachable on high-decimal listings (18 decimals) with whale-scale supply, as the harness test constructs — and (b) sustained high utilization so the borrow index grows ~170x before the `MAX_BORROW_INDEX_RAY` cap (which the test shows does not fire first) can stop growth. An unprivileged borrower driving utilization to the curve's steep segment accelerates index growth; the overflow is then hit by any subsequent `update_indexes`, `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, or direct-transfer-triggered accrual. No privileged role is required at trigger time; any caller can submit the accrual.

### Recommendation
Enforce the value ceiling before the index cap inside `accrue_step`: when `scaled_to_original` of total borrowed or supplied would overflow, clamp the index to `min(computed_index, i128::MAX / shares * RAY)` (or stop accruing that market rather than panicking), or cap accrued shares/index so `shares * index ≤ i128::MAX` is an invariant. Alternatively make `scaled_to_original` on the aggregate totals saturate (like `calculate_scaled_cap` does via `mul_div_floor_saturating`) so accrual degrades gracefully instead of trapping, and add a regression that a market at the ceiling still exits.

### Proof of Concept
The existing harness test is a working PoC (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356):

```rust
let principal = BILLION * 10i128.pow(18);       // 1e9 whole 18-decimal tokens
t.supply_raw(BOB, "BIG18", principal);
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // ~98% utilization
// advance ~years at the XLM curve's steep segment, then:
// t.try_update_indexes_for(&["BIG18"]) -> Err(MATH_OVERFLOW)
// t.try_withdraw_raw(BOB, "BIG18", 1)  -> Err(MATH_OVERFLOW)
// t.try_repay(ALICE, "BIG18", 1.0)     -> Err(MATH_OVERFLOW)
// borrow_index < MAX_BORROW_INDEX_RAY — the cap never engaged; market frozen.
```

Citations: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/pool/src/interest.rs (L39-48)
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
```

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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
