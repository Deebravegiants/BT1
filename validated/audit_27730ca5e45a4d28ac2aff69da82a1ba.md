### Title
RAY-scaled debt accrual can overflow `i128` and permanently freeze a market - (File: contracts/pool/src/cache/scale.rs)

### Summary
An unprivileged borrower can leave a very large market at high utilization until its RAY-scaled debt value exceeds `i128`, after which accrual panics with `MathOverflow` instead of reaching the borrow-index cap. [1](#0-0)  The panic is triggered through permissionless `update_indexes`, and subsequent repayments, withdrawals, and liquidations fail because they accrue the market first. [2](#0-1) [3](#0-2) 

### Finding Description
The public controller exposes `supply`, `borrow`, and `update_indexes`, allowing an account to fund collateral, draw most of a debt market, and later invoke accrual. [4](#0-3) [2](#0-1)  The regression test creates an 18-decimal market with a one-billion-token principal and a 98% borrow draw, then advances accrual until `update_indexes` returns `MathOverflow`. [5](#0-4)  The recorded borrow index remains below `MAX_BORROW_INDEX_RAY`, proving that unscaling the existing debt overflows before the index bound can stop growth. [6](#0-5)  Fixed-point multiplication deliberately converts unrepresentable results into `MathOverflow`; once the persisted scaled debt is too large for the current index, every call that recalculates it reaches the same unrecoverable panic. [7](#0-6) 

### Impact Explanation
The market becomes permanently frozen absent code replacement or privileged state repair: suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot perform risk-reducing liquidations. [8](#0-7)  This satisfies permanent freezing of user funds rather than an isolated rejected transaction. [1](#0-0) 

### Likelihood Explanation
Exploitation requires whale-scale liquidity and sustained high utilization under market caps that permit the draw, so ordinary users cannot trigger it with a small malformed input. [9](#0-8)  Nevertheless, all required actions are normal unprivileged protocol operations, and the regression test demonstrates the state transition and resulting freeze concretely. [10](#0-9) 

### Recommendation
Bound the maximum representable `scaled_debt * borrow_index` value before accrual, rather than relying on `MAX_BORROW_INDEX_RAY` alone. [6](#0-5)  Accrual should clamp or checkpoint the index before debt unscaling exceeds `i128`, and provide a recovery path that can persist a bounded index without first reconstructing an overflowing debt value. [7](#0-6) 

### Proof of Concept
The existing regression test demonstrates the complete sequence: fund the debt market, collateralize and borrow 98%, advance accrual, then observe `update_indexes`, withdrawal, and repayment all fail with `MathOverflow`. [10](#0-9) 

```rust
// Simplified from tests/test-harness/tests/controller/
// large_positions_and_long_horizons.rs.
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();

// One attacker-controlled principal can provide both the debt-market liquidity
// and the collateral needed for the borrow.
let principal = BILLION * 10i128.pow(18);
let debt = principal / 100 * 98;

t.supply_raw(ATTACKER, "BIG18", principal);
t.supply_raw(ATTACKER, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ATTACKER, "BIG18", debt);

let failure = loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) {
        break e;
    }
};

assert_contract_error(Err::<(), _>(failure), errors::MATH_OVERFLOW);
assert_contract_error(
    t.try_withdraw_raw(ATTACKER, "BIG18", 1),
    errors::MATH_OVERFLOW,
);
assert_contract_error(
    t.try_repay(ATTACKER, "BIG18", 1.0),
    errors::MATH_OVERFLOW,
);
```

### Citations

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-319)
```rust
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-356)
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
```

**File:** contracts/controller/src/lib.rs (L94-115)
```rust
    fn supply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        assets: Vec<(HubAssetKey, i128)>,
    ) -> u64 {
        positions::process_supply(&env, &caller, account_id, spoke_id, &assets)
    }

    /// Borrows against `account_id`'s collateral, paying `to` or the caller.
    /// Requires owner or delegate authorization and post-borrow solvency.
    #[when_not_paused]
    fn borrow(
        env: Env,
        caller: Address,
        account_id: u64,
        borrows: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) {
        positions::process_borrow(&env, &caller, account_id, &borrows, to);
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

**File:** common/src/math/fp_core.rs (L108-118)
```rust
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
