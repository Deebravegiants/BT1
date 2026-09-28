### Title
Accrual overflows `i128` and permanently freezes oversized markets - (File: common/src/rates/simulate.rs)

### Summary
Market accrual converts the complete scaled borrow and supply books into RAY-denominated values through `scaled_to_original`, whose result must fit in `i128`. [1](#0-0) [2](#0-1)  A sufficiently large, heavily borrowed market can therefore reach `MathOverflow` before `MAX_BORROW_INDEX_RAY` caps index growth. [3](#0-2) [4](#0-3)  Once this happens, every state-changing path that accrues the market first reverts, including `controller.withdraw`, `controller.repay`, `controller.liquidate`, and permissionless `controller.update_indexes`. [5](#0-4) [6](#0-5) 

### Finding Description
The bug class is the same as the reference issue: integer-range protection validates the intermediate arithmetic but not the economically meaningful result.

`global_sync` splits elapsed time into chunks and calls `accrue_step` for each chunk. [7](#0-6)  Each step first computes `borrowed * borrow_index / RAY` and `supplied * supply_index / RAY` via `scaled_to_original`. [1](#0-0)  `Ray::mul` delegates to `mul_div_half_up`, which uses an `I256` intermediate only when necessary but still panics when the final quotient cannot be represented as `i128`. [8](#0-7) [9](#0-8) 

After utilization and the next borrow index are calculated, `calculate_supplier_rewards` repeats the same representation-bound multiplication on the old and new debt values. [10](#0-9) [11](#0-10)  Consequently, the accrual can fail even though the next borrow index itself remains under `MAX_BORROW_INDEX_RAY`: the capped index is representable, while the debt represented by `borrowed * index` is not. [12](#0-11) 

The repository contains a directed regression proving this state is reachable through ordinary position operations: an 18-decimal asset is supplied at `1e9 * 10^18` base units and 98% of it is borrowed, after which repeated yearly accrual produces `MathOverflow`. [13](#0-12) 

### Impact Explanation
This is permanent freezing of all funds and protocol operations for the affected `(hub, token)` market.

The failure occurs before the requested mutation, so suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and `update_indexes` cannot advance the market timestamp. [5](#0-4) [14](#0-13)  Because the panic happens before `mark_accrued`, retries continue from the same stale state and deterministically fail again. [15](#0-14) 

The market is not merely temporarily congested: its stored shares and indexes already imply a value outside the `i128` result domain used by accrual, so ordinary time progression cannot recover it. [16](#0-15)  All underlying user funds attributed to that market remain trapped unless an out-of-band administrative or upgrade path exists. [4](#0-3) 

### Likelihood Explanation
Likelihood is Medium: exploitation requires a whale-scale token supply, high borrow utilization, configured caps large enough to admit the position, and enough elapsed time at a steep borrow rate.

No privileged action is required to trigger the failure once such a market exists: an attacker can call `supply`, `borrow`, and then permissionless `update_indexes(caller, assets)` as time passes. [17](#0-16) [18](#0-17)  The demonstrated threshold is approximately `borrowed * borrow_index > i128::MAX`; the test reaches it below the borrow-index cap at sustained 98% utilization. [4](#0-3) [19](#0-18) 

### Recommendation
Enforce a market-domain invariant that all stored aggregate values remain representable:

- At supply/borrow/debt-mint boundaries, cap `supplied` and `borrowed` so `scaled * index / RAY <= i128::MAX` at the current index, rather than only bounding the token amount's initial RAY rescale.
- Before accrual computes debt or supply value, cap the effective index at `min(index_cap, floor(i128::MAX * RAY / scaled_book))`, or perform accrual accounting in a representation that does not require total book value to fit `i128`.
- Preserve liveness at the boundary: after the index cap engages, accrual must no-op safely rather than continue to value an already-unrepresentable book.
- Keep `update_indexes`, `repay`, `withdraw`, liquidation, and bad-debt cleanup executable at the cap.
- Add the existing whale-market regression as a permanent end-to-end test and extend it to assert withdrawals, repayments, liquidations, and repeated index updates remain possible at the configured ceiling. [20](#0-19) 

### Proof of Concept
The existing directed test constructs the reachable state through controller-level operations:

```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) {
        assert_contract_error(Err(e), errors::MATH_OVERFLOW);
        break;
    }
}

assert_contract_error(
    t.try_withdraw_raw(BOB, "BIG18", 1),
    errors::MATH_OVERFLOW
);
assert_contract_error(
    t.try_repay(ALICE, "BIG18", 1.0),
    errors::MATH_OVERFLOW
);
```

The test verifies that the panic occurs while `borrow_index < MAX_BORROW_INDEX_RAY`, proving the value multiplication—not the index cap—is the root cause. [21](#0-20)

### Citations

**File:** common/src/rates/simulate.rs (L60-69)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/index.rs (L11-18)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-320)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-361)
```rust
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

**File:** contracts/pool/src/interest.rs (L20-40)
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
```

**File:** common/src/math/fp.rs (L184-193)
```rust
    /// Multiplies two wad values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Wad) -> Wad {
        Wad(fp_core::mul_div_half_up(env, self.0, other.0, WAD))
    }

    /// Multiplies two wad values, rounding the result half up. Returns `None` if
    /// either operand is negative or the result does not fit in `i128`.
    pub fn try_mul(self, env: &Env, other: Wad) -> Option<Wad> {
        fp_core::try_mul_div_half_up(env, self.0, other.0, WAD).map(Wad)
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
