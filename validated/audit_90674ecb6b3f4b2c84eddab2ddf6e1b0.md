### Title
Overflow in borrow-value accrual permanently freezes a market - ([File: common/src/rates/simulate.rs])

### Summary
`accrue_step` evaluates `borrowed * borrow_index` before applying the configured borrow-index ceiling. Once total scaled debt grows beyond the `i128::MAX` RAY-value ceiling, every subsequent accrual panics with `MathOverflow`, freezing repayment, withdrawal, liquidation, and further index updates for that market. The bundled regression test demonstrates this with a large 18-decimal market at sustained high utilization. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
The accrual path first converts scaled borrow shares into their RAY-denominated original value using `scaled_to_original`. [4](#0-3)  That helper calls `Ray::mul`, which panics when the exact result cannot fit in `i128`. [2](#0-1) [5](#0-4) 

The borrow-index cap is applied only inside `update_borrow_index`, after the vulnerable borrow-value multiplication has already executed. [6](#0-5)  Because accrual is recomputed from the same stored scaled debt and nondecreasing index, the overflow is persistent: the next accrual reaches the same multiplication again and fails again. [7](#0-6) [8](#0-7) 

An unprivileged caller can reach the failing operation through `update_indexes`; the controller forwards the requested market list to the pool after caller authorization. [9](#0-8)  The project’s own regression test creates a one-billion-token 18-decimal market, supplies the full amount, borrows 98% of it, advances time, and observes `MathOverflow` before `MAX_BORROW_INDEX_RAY` is reached. [10](#0-9) 

### Impact Explanation
This causes permanent freezing of all funds represented by the affected market book. Once the product overflows, suppliers cannot withdraw and borrowers or third parties cannot repay; the test explicitly verifies that both one-unit withdrawal and one-unit repayment hit `MathOverflow`. [8](#0-7) 

The failure also prevents liquidation of the underwater position because liquidation paths accrue indexes first, so collateral backing the debt cannot be recovered through the normal protocol flow. [11](#0-10)  Absent an administrative recovery path such as an upgrade or pause, the market remains bricked and all its supplier/debt accounting is inaccessible. [1](#0-0) 

### Likelihood Explanation
Triggering the condition requires a very large position and sustained high utilization, so it is capital-intensive rather than a routine small-transaction exploit. [12](#0-11)  The documented fixture admits the necessary shape: one billion whole tokens at 18 decimals and 98% utilization. [13](#0-12) 

The test only requires ordinary public actions—supply, borrow, passage of time, and `update_indexes`—and shows failure within the exercised horizon while the index remains below its intended cap. [14](#0-13)  Because the index cap does not prevent the earlier RAY-value overflow, normal protocol bounds do not stop the condition. [15](#0-14) [16](#0-15) 

### Recommendation
Bound the product `borrowed * borrow_index`, rather than only the index, before accrual proceeds. A practical approach is to cap or decompose debt growth based on `i128::MAX / borrow_index` so `scaled_to_original` cannot receive an overflowing operand. [2](#0-1) [6](#0-5) 

The same domain check should be applied consistently to `supplied * supply_index` and to later calculations in `calculate_supplier_rewards`, `update_supply_index`, and `supply_index_reward_shortfall`, which perform additional index-scaled products during each step. [17](#0-16) [18](#0-17)  Add a regression test asserting that the debt-value ceiling is reached without panicking and that exits remain executable afterward. [19](#0-18) 

### Proof of Concept
The existing test demonstrates the exploit path:

```rust
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

From `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-333`. [13](#0-12) 

Advancing time and invoking index accrual eventually fails with `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`. [14](#0-13)  Subsequent `withdraw` and `repay` calls also fail with the same error, proving the market and its funds are frozen rather than merely rejecting one large operation. [20](#0-19)

### Citations

**File:** common/src/rates/simulate.rs (L51-87)
```rust
pub fn accrue_step(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    supplied: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    delta_ms: u64,
) -> AccrualStep {
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);

    let new_supply_index = update_supply_index(env, supplied, supply_index, supplier_rewards);
    let supplier_shortfall = supply_index_reward_shortfall(
        env,
        supplied,
        supply_index,
        new_supply_index,
        supplier_rewards,
    );

    let protocol_reward = protocol_fee.checked_add(env, supplier_shortfall);
    // Shares are valued at the new supply index, which the caller stores for
    // this step.
    let revenue_shares = if protocol_reward == Ray::ZERO {
        Ray::ZERO
    } else {
        protocol_fee_shares(env, protocol_reward, new_supply_index, supplied)
    };
```

**File:** common/src/rates/simulate.rs (L136-174)
```rust
pub(crate) fn simulate_update_indexes_body(
    env: &Env,
    current_timestamp: u64,
    sync: &PoolSyncData,
) -> MarketIndex {
    let state = PoolState::from(&sync.state);
    let total_delta_ms = current_timestamp.saturating_sub(state.last_timestamp);

    if total_delta_ms == 0 {
        return MarketIndex {
            supply_index: state.supply_index,
            borrow_index: state.borrow_index,
        };
    }

    let params = MarketParams::from(&sync.params);

    let mut supplied = state.supplied;
    let mut borrow_index = state.borrow_index;
    let mut supply_index = state.supply_index;

    let mut remaining = total_delta_ms;
    while remaining > 0 {
        let chunk = remaining.min(MAX_COMPOUND_DELTA_MS);
        let step = accrue_step(
            env,
            &params,
            state.borrowed,
            supplied,
            borrow_index,
            supply_index,
            chunk,
        );

        borrow_index = step.borrow_index;
        supply_index = step.supply_index;
        supplied = supplied.checked_add(env, step.revenue_shares);

        remaining -= chunk;
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/rates/index.rs (L11-19)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
}
```

**File:** common/src/rates/index.rs (L29-44)
```rust
pub fn update_supply_index(env: &Env, supplied: Ray, old_index: Ray, rewards_increase: Ray) -> Ray {
    if supplied == Ray::ZERO || rewards_increase == Ray::ZERO {
        return old_index;
    }

    let total_supplied_value = supplied.mul(env, old_index);

    if total_supplied_value == Ray::ZERO {
        return old_index;
    }

    let new_value = total_supplied_value.checked_add(env, rewards_increase);
    let grown = fp_core::mul_div_floor_saturating(env, new_value.raw(), RAY, supplied.raw());

    let bounded_old = old_index.raw().min(MAX_SUPPLY_INDEX_RAY);
    Ray::from(grown.min(MAX_SUPPLY_INDEX_RAY).max(bounded_old))
```

**File:** contracts/controller/src/markets.rs (L118-125)
```rust
/// Accrues indexes for each hub asset. Requires caller authorization and no flash loan.
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
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
