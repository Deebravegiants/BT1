### Title
Unbounded market value overflows accrual and permanently freezes the market - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
Interest accrual converts the entire scaled debt book with `scaled_to_original` before applying the borrow-index cap. Once `borrowed * borrow_index / RAY` exceeds `i128::MAX`, every market operation that first synchronizes the market panics with `MathOverflow`, permanently preventing repayment, withdrawal, liquidation, and further index updates. [1](#0-0) [2](#0-1) 

### Finding Description
`accrue_step` first computes `borrowed_original = scaled_to_original(borrowed, borrow_index)` and `supplied_original = scaled_to_original(supplied, supply_index)` to derive utilization. [3](#0-2)  `scaled_to_original` delegates to `Ray::mul`, and the underlying `mul_div_half_up` returns `None` when the exact quotient does not fit `i128`, which is converted into a `MathOverflow` panic. [4](#0-3) [5](#0-4) 

The borrow-index cap is only applied after this total-debt valuation, inside `update_borrow_index`; it therefore cannot prevent the earlier multiplication from exceeding the representable RAY-value domain. [6](#0-5)  The mutating `update_indexes` path calls `global_sync` for each requested market, while user exits and repayments also reach the same path through `load_leg`. [7](#0-6) [8](#0-7) 

An unprivileged user can reach the condition through the public controller paths `supply`, `borrow`, and later `update_indexes`; `repay` is permissionless and `withdraw` is available to the account owner or delegate. [9](#0-8) [10](#0-9) 

### Impact Explanation
This is permanent freezing of funds and protocol insolvency risk: once the market crosses the representable value boundary, suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot reduce the bad debt because all of those operations accrue first. [11](#0-10)  The failure is state-persistent rather than a per-call resource limit: the stale index remains below `MAX_BORROW_INDEX_RAY`, so the next invocation repeats the same overflowing valuation before it can advance or clamp the index. [12](#0-11) 

### Likelihood Explanation
The attack requires an admitted market whose caps and available liquidity permit a book near the RAY-value ceiling, followed by enough accrual at high utilization for the index to cross the threshold. [13](#0-12)  Those requirements impose substantial capital and configuration prerequisites, so the issue is not triggerable on every market; however, the repository's concrete regression test demonstrates that a valid admitted configuration reaches the cliff and that the panic is repeatable. [14](#0-13) 

### Recommendation
Bound market totals against the maximum representable RAY value at supply/borrow entry, not only against token-unit caps. In `accrue_step`, evaluate the new borrow index before multiplying total debt, clamp it to `MAX_BORROW_INDEX_RAY`, and use checked or saturating total-value calculations that preserve an exit path when the value domain is exhausted. The market should remain repayable and withdrawable even if further interest accrual is capped or disabled.

### Proof of Concept
The existing regression test constructs an 18-decimal market using the steep `xlm_curve`, supplies `1_000_000_000 * 10^18` base units, and borrows 98% of that book. [15](#0-14) [13](#0-12)  At approximately a 173× borrow index, `0.98e36 * index / 1e27` approaches `i128::MAX`; the next `update_indexes` call panics in `scaled_to_original` before the index cap can engage. [1](#0-0)  Subsequent `withdraw` and `repay` calls fail with the same `MathOverflow`, demonstrating the permanent freeze. [16](#0-15)

### Citations

**File:** common/src/rates/simulate.rs (L60-67)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

```

**File:** contracts/pool/src/ops/mod.rs (L29-33)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
```

**File:** contracts/pool/src/ops/mod.rs (L42-47)
```rust
/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
}
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** contracts/pool/src/ops/market.rs (L65-72)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
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

**File:** contracts/controller/src/lib.rs (L120-133)
```rust
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }

    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L26-38)
```rust
/// Steep XLM stress curve: 175 percent max borrow rate, optimal at 75 percent.
fn xlm_curve() -> MarketParamsPreset {
    MarketParamsPreset {
        max_borrow_rate: RAY * 175 / 100,
        base_borrow_rate: RAY / 100,
        slope1: RAY * 4 / 100,
        slope2: RAY * 10 / 100,
        slope3: RAY * 150 / 100,
        mid_utilization: RAY * 50 / 100,
        optimal_utilization: RAY * 75 / 100,
        max_utilization: RAY,
        reserve_factor: 2000,
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
