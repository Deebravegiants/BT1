### Title
RAY-scaled interest valuation overflows before the borrow-index cap, permanently freezing a market - (File: common/src/rates/scaling.rs)

### Summary
Interest accrual converts scaled debt and supply back into RAY-denominated values before applying the borrow-index cap. When `scaled_amount * index / RAY` exceeds `i128::MAX`, the checked fixed-point multiplication panics with `MathOverflow`, making every operation that first synchronizes the market revert. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`Controller::update_indexes(caller, assets)` is permissionless, requires only caller authorization, and forwards the selected `HubAssetKey` values to the pool’s accrual entrypoint. [4](#0-3) [5](#0-4)  Each pool operation loads a `Cache` and calls `interest::global_sync`, while `global_sync` runs `accrue_step` over elapsed-time chunks. [6](#0-5) [7](#0-6) 

At the start of each step, `accrue_step` calls `scaled_to_original` for both `borrowed` and `supplied`; that helper performs `Ray::mul`, which evaluates `x * y / RAY`. [1](#0-0) [8](#0-7)  The intermediate product is widened to `I256`, but the final result must still fit in `i128`; otherwise `try_mul_div_half_up` returns `None` and `mul_div_half_up` panics with `GenericError::MathOverflow`. [9](#0-8) [3](#0-2) 

This panic occurs before `update_borrow_index` can clamp the newly grown index to `MAX_BORROW_INDEX_RAY`. [10](#0-9)  The repository’s regression test demonstrates the concrete cliff: after sufficient index growth, `update_indexes` fails, the stored index remains below its cap, and both withdrawal and repayment revert with `MATH_OVERFLOW`. [11](#0-10) [12](#0-11) 

### Impact Explanation
Once either the scaled supply value or scaled debt value exceeds the representable `i128` range, accrual cannot complete and therefore cannot persist a new timestamp. [13](#0-12)  Because every mutating market leg synchronizes before acting, suppliers cannot withdraw, borrowers cannot repay, and liquidation or cleanup paths that require synchronization also revert. [6](#0-5) [14](#0-13)  This is a permanent freezing of user funds in the affected market rather than a temporary failure that can be resolved by retrying. [11](#0-10) 

### Likelihood Explanation
The condition requires an unusually large market whose scaled principal multiplied by its grown index exceeds `i128::MAX`, so the likelihood depends on asset decimals, total market size, utilization, and accrued index growth. A single unprivileged address can nevertheless create the condition using its own funds through `supply` and `borrow`, then trigger the failure through permissionless `update_indexes`; no privileged action is required at the triggering step. [15](#0-14) [16](#0-15) [4](#0-3)  The existing test constructs a reachable high-utilization whale market and confirms that the value ceiling is reached before the index ceiling. [17](#0-16) [18](#0-17) 

### Recommendation
Enforce a market-level scaled-balance bound that guarantees `scaled * MAX_INDEX / RAY <= i128::MAX`, or rework accrual valuation and reward calculation to retain `I256` intermediates without requiring each valuation to fit in `i128`. If a hard bound is chosen, apply it consistently to supply minting, debt minting, revenue-share accrual, liquidation share movements, and direct market-cap accounting so the overflow state can never be entered. The index cap should also be checked before performing multiplications whose result can exceed `i128`, rather than only after `update_borrow_index`. [10](#0-9) [19](#0-18) 

### Proof of Concept
1. As one unprivileged caller, create a supply account with a very large position in an 18-decimal market, for example `supply(caller, 0, spoke_id, [(BIG18, 1_000_000_000 * 10^18)])`.
2. Using the same caller, create or use a second account with sufficient collateral and execute `borrow(caller, collateral_account_id, [(BIG18, 980_000_000 * 10^18)], None)`, producing approximately `9.8e35` scaled debt shares. [20](#0-19) 
3. Allow the market index to grow until `scaled_debt * borrow_index / RAY > i128::MAX`; for that position, this corresponds to roughly a 174× index multiplier, still below the configured index ceiling. [11](#0-10) 
4. Call `update_indexes(caller, [BIG18])`; the call reaches pool accrual and panics in `scaled_to_original` before the index cap can engage. [5](#0-4) [2](#0-1) [18](#0-17) 
5. Subsequent `withdraw` and `repay` attempts revert with `MathOverflow`, leaving the market’s supplied and borrowed funds frozen. [14](#0-13)

### Citations

**File:** common/src/rates/simulate.rs (L60-64)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp_core.rs (L116-118)
```rust
    try_mul_div_half_up(env, x, y, d)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

**File:** common/src/math/fp_core.rs (L138-142)
```rust
    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    x256.mul(&y256)
        .add(&I256::from_i128(env, half))
        .div(&d256)
        .to_i128()
```

**File:** contracts/controller/src/lib.rs (L94-101)
```rust
    fn supply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        assets: Vec<(HubAssetKey, i128)>,
    ) -> u64 {
        positions::process_supply(&env, &caller, account_id, spoke_id, &assets)
```

**File:** contracts/controller/src/lib.rs (L107-115)
```rust
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

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
```

**File:** contracts/controller/src/markets.rs (L120-124)
```rust
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
```

**File:** contracts/pool/src/ops/mod.rs (L29-33)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
```

**File:** contracts/pool/src/interest.rs (L25-29)
```rust
    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/rates/index.rs (L13-17)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
```

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-319)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-333)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L349-356)
```rust
    let last = book(&t, "BIG18");
    assert!(
        last.borrow_index < MAX_BORROW_INDEX_RAY,
        "the index cap did not engage before the value overflow"
    );
    // The market is frozen: exits and repayments accrue first and hit the same panic.
    assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
    assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```
