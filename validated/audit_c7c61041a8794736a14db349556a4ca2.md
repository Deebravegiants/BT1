### Title
RAY-denominated debt valuation overflow permanently freezes an active market - (File: common/src/rates/index.rs)

### Summary

Interest accrual calculates old and new market-wide debt as `borrowed.mul(index)`. Once the total scaled debt times the borrow index no longer fits in `i128`, `Ray::mul` panics with `GenericError::MathOverflow` instead of saturating or capping the index. Because every market mutation accrues first, a public `update_indexes` call can cross that boundary and subsequently leave repayment, withdrawal, liquidation, index updates, and rate-model changes unusable for the market.

### Finding Description

`calculate_supplier_rewards` multiplies the market’s total scaled debt by both the old and new borrow indexes before checking or clamping them to `MAX_BORROW_INDEX_RAY`. [1](#0-0)  The multiplication delegates to `mul_div_half_up`, which returns `MathOverflow` when the rounded RAY value cannot fit in `i128`. [2](#0-1) [3](#0-2) 

The permissionless controller entrypoint `update_indexes(caller, assets)` forwards the attacker-selected hub asset to `markets::update_indexes`. [4](#0-3)  Pool `update_indexes` calls `ops::market::accrue`, and `global_sync` feeds the stored scaled debt and current indexes into `accrue_step`. [5](#0-4) [6](#0-5) 

The regression test demonstrates that the borrow index can remain below `MAX_BORROW_INDEX_RAY` while the next accrual fails in this valuation step; afterward, even a one-unit withdrawal and a minimal repayment fail with `MATH_OVERFLOW`. [7](#0-6) 

### Impact Explanation

All user funds represented by the affected market’s supply shares become permanently inaccessible, and borrowers cannot repay or be liquidated through the normal entrypoints. `clean_bad_debt`, `recapitalize`, `claim_revenue`, and rate-model replacement also cannot provide a recovery path when they must perform the same accrual before mutating state. The protocol therefore has a permanently frozen market even though its index remains below the configured index ceiling.

### Likelihood Explanation

The trigger requires a very large, highly utilized market whose total RAY-valued debt approaches the `i128` boundary, so this is not reachable with ordinary small balances. It does not require privileged state, malformed configuration, oracle manipulation, or a transaction atomicity edge: ordinary supply and borrow positions create the state, and any unprivileged caller can invoke `update_indexes` once accrued interest pushes the valuation across the boundary. The existing harness constructs exactly such a market and reaches the failure solely through public operations.

### Recommendation

Compute accrual on bounded or saturated debt values before emitting the new index. In particular:

- Determine `MAX_BORROW_INDEX_RAY` before evaluating `borrowed * new_borrow_index`.
- Use saturating `I256`-backed valuation for the old/new totals, or explicitly cap the computed debt value at the largest representable amount.
- Ensure accrual marks the market synchronized at the index ceiling instead of trapping.
- Add a regression path asserting that repayment, withdrawal, liquidation, and `update_indexes` remain executable when the index cap is reached.
- Consider reducing effective borrow/share caps so `scaled_debt * MAX_BORROW_INDEX_RAY / RAY` is guaranteed to fit in `i128`.

### Proof of Concept

A concrete regression already exists in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs`:

1. Create a high-decimal market and a collateral market.
2. Supply `BILLION * 10^18` units to the debt market.
3. Borrow 98% of that supply.
4. Advance the ledger and repeatedly call the permissionless controller method:
   ```rust
   update_indexes(caller, vec![BIG18_HUB_ASSET])
   ```
5. Once `borrowed * new_borrow_index / RAY` exceeds `i128::MAX`, `accrue_step` reverts with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`.
6. Subsequent calls such as:
   ```rust
   withdraw(caller, supplier_account, vec![(BIG18_HUB_ASSET, 1)], to)
   repay(caller, borrower_account, vec![(BIG18_HUB_ASSET, ONE_TOKEN)])
   update_indexes(caller, vec![BIG18_HUB_ASSET])
   ```
   all fail before reaching their operation-specific logic because each path attempts accrual first. [8](#0-7)

### Citations

**File:** common/src/rates/index.rs (L73-83)
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
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/math/fp_core.rs (L104-118)
```rust
/// Computes `x * y / d` rounded half up. Requires `x >= 0`, `y >= 0`, and `d > 0`; a
/// `debug_assert` checks this in debug builds. Panics with `GenericError::DivisionByZero` if
/// `d == 0`, and with `GenericError::MathOverflow` if any other precondition is violated or if
/// the result does not fit in `i128`.
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
```

**File:** contracts/pool/src/lib.rs (L174-180)
```rust
    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
    }
```

**File:** contracts/pool/src/interest.rs (L20-52)
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
