### Title
Overflowing index-scaled market totals permanently freeze a borrowed market - (File: common/src/rates/index.rs)

### Summary
A sufficiently large market with sustained high utilization can overflow `i128` while interest accrual multiplies scaled balances by their RAY index. Because the panic occurs inside `global_sync` before state mutation or index capping, every later operation that accrues the market fails, leaving supplied funds, collateral, and debt permanently stuck absent a privileged upgrade or migration.

### Finding Description
`contracts/pool/src/interest.rs:20-33` requires each market mutation to complete `global_sync` before proceeding. Each accrual chunk calls `accrue_step` and only then writes the returned indexes. [1](#0-0) 

The rate engine computes total debt as `borrowed * borrow_index`, including both old and new totals, using fallible RAY multiplication. [2](#0-1) 

Although `update_borrow_index` caps the index at `MAX_BORROW_INDEX_RAY`, the cap is applied only after `old_index.mul(interest_factor)` and does not bound `borrowed * new_index`, which can exceed `i128::MAX` first. [3](#0-2) 

The same scaled-total multiplication is used when unscaling supply and borrow balances, so withdrawal and repayment paths also overflow rather than degrade gracefully. [4](#0-3) [5](#0-4) 

The in-repository regression test demonstrates the reachable condition: a one-billion-token, 18-decimal market at 98% utilization eventually makes `update_indexes` return `MathOverflow`, and subsequent `withdraw` and `repay` calls return the same error. [6](#0-5) 

### Impact Explanation
Once the scaled-total value crosses the `i128` ceiling, the accrual transaction aborts before `mark_accrued` runs, so the market cannot advance past the overflowing chunk. [7](#0-6) 

All suppliers’ pool funds and the borrower’s collateral become unusable: withdrawals and liquidation-market exits accrue first, while debt repayment also accrues first and reverts. This is permanent freezing of user funds rather than a temporary fail-closed price or liquidity condition.

### Likelihood Explanation
An unprivileged borrower can create the condition through `controller::supply`, `controller::borrow`, and periodic permissionless `controller::update_indexes` calls. The exploit requires a very large underlying market, high debt utilization, a rate configuration that compounds the index substantially, and enough elapsed ledger time; no privileged call, malformed authorization, or third-party contract behavior is required.

The proof case uses `supply` to create the target liquidity market, `supply` on a collateral market and `borrow` for approximately 98% of the target liquidity, then repeated `update_indexes` calls to advance accrual until the multiplication overflows. [8](#0-7) 

### Recommendation
Perform all index-scaled market totals in a wider representation, such as `I256`, before reducing to `i128`; alternatively cap or split scaled balances so `borrowed * index` and `supplied * index` cannot overflow. Bound `borrowed` before applying `interest_factor`, rather than relying only on `MAX_BORROW_INDEX_RAY`. Add a recovery-safe accrual path that clamps an overflowing aggregate and still advances `last_timestamp`, and extend the regression test to assert that repay, withdraw, liquidation, and bad-debt cleanup remain callable at the largest supported market domain.

### Proof of Concept
The repository already contains an executable reproduction:

- File: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs`
- Test: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`

Relevant sequence:

```rust
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

t.advance_time(YEAR_SECS);
t.try_update_indexes_for(&["BIG18"])
```

The test observes `MathOverflow`, confirms `borrow_index < MAX_BORROW_INDEX_RAY`, and then confirms both withdrawal and repayment fail with the same error. [9](#0-8)

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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L80-86)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L89-95)
```rust
/// Converts a scaled borrow `Ray` back to an asset-unit amount, using
/// ceiling rounding at `decimals` precision.
pub fn unscale_borrow_ceil(env: &Env, scaled: Ray, borrow_index: Ray, decimals: u32) -> i128 {
    scaled
        .mul_ceil(env, borrow_index)
        .to_asset_ceil(env, decimals)
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
