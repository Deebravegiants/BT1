### Title

RAY debt valuation overflow permanently freezes a high-utilization market - (File: common/src/rates/scaling.rs)

### Summary

A large debt position can make `borrowed * borrow_index` exceed `i128::MAX` before `MAX_BORROW_INDEX_RAY` is reached. The next permissionless `Controller::update_indexes` call panics during accrual, leaving the market's `last_timestamp` stale so every subsequent supply, borrow, withdrawal, repayment, liquidation, bad-debt cleanup, or strategy touching that market repeats the same accrual and reverts. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description

The RAY representation multiplies token base units by `10^(27 - decimals)`. For an 18-decimal asset, one billion whole tokens already occupies approximately `1e36` scaled value, so a debt index around 170 times `RAY` makes the RAY-denominated debt value exceed the `i128` range. `scaled_to_original` delegates to `Ray::mul`, which widens intermediate products but panics when the quotient cannot fit back into `i128`. [1](#0-0) [4](#0-3) [5](#0-4) 

Every pool mutation loads the market and runs `global_sync` before its operation-specific logic. `global_sync` calls `accrue_step` with the stored `borrowed` amount and `borrow_index`; `calculate_supplier_rewards` then evaluates both `borrowed * old_borrow_index` and `borrowed * new_borrow_index`. Once the scaled debt crosses the representable-value boundary, either debt valuation panics with `MathOverflow` before the borrow index cap can stop growth. [3](#0-2) [6](#0-5) [7](#0-6) [8](#0-7) 

The repository already contains a reproduction for this boundary. It creates a billion-token 18-decimal market, supplies the full amount, borrows 98%, advances the ledger until `update_indexes` returns `MATH_OVERFLOW`, and demonstrates that withdrawal and repayment then fail for the same reason. [9](#0-8) [10](#0-9) 

### Impact Explanation

This is permanent freezing of user funds. Suppliers cannot withdraw principal or yield, borrowers cannot repay, liquidators cannot clear positions, and any controller or strategy path that causes the pool to accrue the affected market reverts. The first overflow does not commit a new timestamp, so the condition is self-perpetuating rather than a temporary failed transaction. [11](#0-10) [3](#0-2) [10](#0-9) 

### Likelihood Explanation

An unprivileged caller can trigger the terminal accrual through `Controller::update_indexes(caller, assets)` after the ledger advances far enough. Establishing the required state needs a very large configured position and sustained high utilization: the account supplies the high-decimal asset, borrows nearly all of it, and leaves the debt outstanding while the configured rate curve compounds. [2](#0-1) [12](#0-11) 

The feasibility depends on deployed token supply, spoke caps, utilization limits, and the configured interest-rate model. It is not guaranteed for every market, but `MAX_BORROW_INDEX_RAY` does not prevent the failure because total debt valuation can overflow before that index cap engages. [8](#0-7) [13](#0-12) 

### Recommendation

Bound the total scaled exposure before it can produce an unrepresentable debt value. In particular:

- Reject supply or borrow entries when the resulting `scaled * index` ceiling exceeds a safe fraction of `i128::MAX`.
- Enforce per-market scaled supply and debt limits in addition to token-unit spoke caps.
- Make accrual clamp or otherwise handle an index/delta that would push debt value over the representable RAY domain instead of reverting unconditionally.
- Add invariant tests proving that every admitted `borrowed` amount can be multiplied by `MAX_BORROW_INDEX_RAY` without overflow.

### Proof of Concept

1. Configure or use an 18-decimal hub asset whose market permits approximately one billion whole tokens and very high utilization.
2. Call `Controller::supply` to deposit `1_000_000_000 * 10^18` base units.
3. Call `Controller::borrow` for 98% of the supplied asset using separate collateral that satisfies the account risk checks.
4. Advance the ledger while the configured borrow-rate curve compounds the debt index.
5. Call `Controller::update_indexes(caller, vec![HubAssetKey { hub_id, asset }])`.
6. The call reaches `global_sync` → `accrue_step` → debt valuation and panics with `GenericError::MathOverflow` once `borrowed * borrow_index` exceeds `i128::MAX`. [6](#0-5) [1](#0-0) 
7. Subsequent calls to `withdraw` and `repay` fail with the same error because both load the stale market and attempt accrual before processing the requested action. [10](#0-9)

### Citations

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/pool/src/interest.rs (L20-32)
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
```

**File:** contracts/pool/src/interest.rs (L39-52)
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

**File:** common/src/math/fp_core.rs (L138-143)
```rust
    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    x256.mul(&y256)
        .add(&I256::from_i128(env, half))
        .div(&d256)
        .to_i128()
}
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

**File:** common/src/rates/index.rs (L73-88)
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

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);

    (supplier_rewards, protocol_fee)
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-333)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L343-356)
```rust
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

**File:** contracts/pool/src/cache/mod.rs (L133-146)
```rust
    /// Milliseconds between last accrual and the stamped current time.
    pub(crate) fn elapsed_ms(&self) -> u64 {
        self.current_timestamp.saturating_sub(self.last_timestamp)
    }

    /// `true` when interest should be compounded before further mutations.
    pub(crate) fn needs_accrual(&self) -> bool {
        self.elapsed_ms() > 0
    }

    /// Marks the market as fully accrued through `current_timestamp`.
    pub(crate) fn mark_accrued(&mut self) {
        self.last_timestamp = self.current_timestamp;
    }
```
