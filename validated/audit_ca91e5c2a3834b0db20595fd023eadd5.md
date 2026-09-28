### Title
Debt-index accrual overflows `i128` and permanently freezes a whale market - ([File: common/src/rates/index.rs](common/src/rates/index.rs))

### Summary
A sufficiently large market at sustained high utilization can make `borrowed * new_borrow_index` exceed the `i128` RAY domain before the borrow-index ceiling is reached. Because every mutation accrues interest before changing state, the resulting `MathOverflow` blocks withdrawals, repayments, and liquidations for the affected market.

### Finding Description
`global_sync` unconditionally runs `accrue_step` for elapsed time before any market operation proceeds. [1](#0-0) [2](#0-1)  During accrual, `calculate_supplier_rewards` multiplies the full scaled debt by both the old and new borrow indexes to derive accrued interest. [3](#0-2)  Fixed-point multiplication returns a typed `MathOverflow` when the exact result cannot fit in `i128`. [4](#0-3) 

The borrow index is capped at `MAX_BORROW_INDEX_RAY`, but that cap is applied only after `old_index.mul(interest_factor)` and does not bound the market value represented by `borrowed * index`. [5](#0-4)  The test scenario documents a 98%-utilized 18-decimal market with one billion whole tokens whose next accrual fails before the index cap, after which withdrawal and repayment fail with the same error. [6](#0-5) 

### Impact Explanation
Once the debt value crosses the representable RAY boundary, no mutation touching that market can complete because every mutation loads the market through `synced_market`, which invokes `interest::global_sync` first. [2](#0-1)  Suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot liquidate; the regression test explicitly demonstrates `MathOverflow` for withdrawal and repayment after the cliff. [7](#0-6)  Even `replace_rate_model` accrues under the old model before writing replacement parameters, so changing the rate model does not bypass the overflow. [8](#0-7)  This is permanent freezing of user funds.

### Likelihood Explanation
An unprivileged caller can create the precondition by supplying a large listed asset and having another account borrow most of it, within the protocol’s documented cap domain and utilization bounds. [9](#0-8)  Any address can then trigger `update_indexes`, while the pool’s owner-gated `update_indexes` entrypoint directly calls market accrual. [10](#0-9) [11](#0-10)  The attack requires an exceptionally large, highly utilized market and sustained accrual, so the practical likelihood is medium rather than high. [12](#0-11) 

### Recommendation
Handle the borrow-value ceiling explicitly before accrual. When `borrowed * new_borrow_index` would exceed `i128::MAX`, clamp the borrow index to the largest index whose debt value remains representable, or split accounting into a representation that does not overflow. Apply the same explicit saturation policy to `old_total_debt` and `new_total_debt` in `calculate_supplier_rewards`, and add a regression test showing that `withdraw`, `repay`, and `liquidate` remain usable after reaching the value boundary.

### Proof of Concept
1. Configure an 18-decimal market and collateral market, then supply `1_000_000_000 * 10^18` base units of the debt asset.
2. Supply sufficient collateral from a borrower account and borrow 98% of the debt asset.
3. Advance ledger time and invoke permissionless `update_indexes` until the next accrual would make `borrowed * new_borrow_index` exceed `i128::MAX`.
4. The call aborts in `calculate_supplier_rewards` with `MathOverflow` while computing `new_total_debt`. [3](#0-2) 
5. Subsequent `withdraw` and `repay` calls abort during their mandatory pre-operation accrual, leaving supplier and borrower funds frozen. [2](#0-1) [7](#0-6)

### Citations

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

**File:** contracts/pool/src/ops/mod.rs (L29-33)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
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

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
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

**File:** contracts/pool/src/ops/market.rs (L50-57)
```rust
/// Accrues interest under the old model, commits it, then replaces the interest
/// and flash-loan parameters and validates them against the stored decimals.
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
    events::emit_market_params(env, hub_asset.hub_id, hub_asset.asset, params);
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
