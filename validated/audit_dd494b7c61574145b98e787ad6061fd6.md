### Title
RAY share-value overflow in interest accrual permanently freezes an oversized market - (File: common/src/rates/simulate.rs)

### Summary
A sufficiently large `(hub_id, asset)` market can push `scaled_to_original(borrowed, borrow_index)` or `scaled_to_original(supplied, supply_index)` past `i128::MAX` before `MAX_BORROW_INDEX_RAY` is reached. Every user-facing verb that touches the market accrues first, so once this boundary is crossed, `withdraw`, `repay`, `liquidate`, `borrow`, `supply`, `recapitalize`, and `update_indexes` all revert with `MathOverflow`, permanently freezing user funds and debt in that market.

### Finding Description
`Controller::update_indexes` is reachable by an ordinary authenticated caller and forwards the requested `Vec<HubAssetKey>` to the pool. [1](#0-0)  The pool owner entrypoint iterates the assets, loads each market, runs `interest::global_sync`, and commits the result. [2](#0-1)  `global_sync` chunks elapsed time into periods of at most `MAX_COMPOUND_DELTA_MS` and calls `accrue_chunk` for each chunk. [3](#0-2) 

The vulnerable step is `accrue_step`, which computes `borrowed_original` and `supplied_original` with `scaled_to_original` before it updates either index. [4](#0-3)  `scaled_to_original` is a plain `scaled.mul(env, index)` RAY multiplication, so a scaled share count times index whose exact value exceeds `i128::MAX` panics. [5](#0-4)  The checked multiplication path behind that operation converts overflow into `GenericError::MathOverflow` rather than clamping the value. [6](#0-5) 

The borrow-index cap does not prevent this state: `update_borrow_index` caps only the index after multiplying `old_index * interest_factor`, and it does not bound `borrowed * borrow_index`. [7](#0-6)  The in-repo adversarial test demonstrates the exact condition: an 18-decimal market with `1e9 * 1e18` supplied and 98% borrowed reaches `MATH_OVERFLOW` on a later `update_indexes`, while `borrow_index < MAX_BORROW_INDEX_RAY`. [8](#0-7)  The same test confirms the market is then frozen for `withdraw` and `repay`. [9](#0-8) 

### Impact Explanation
This is a permanent freezing of user funds and a protocol-insolvency-adjacent stall. Once `scaled * index` crosses the representable RAY total, every path that must accrue the market fails atomically, including exits and debt reduction. Suppliers cannot withdraw, borrowers cannot repay or be liquidated through the market path, and recapitalization cannot restore operation because it still routes through market accounting. The failure is not a fail-closed liquidity guard: the market still holds cash and positions, but accounting can no longer be evaluated.

### Likelihood Explanation
The trigger requires an extremely large market balance relative to `i128` RAY units and enough elapsed accrual to raise the index before the value ceiling is crossed. An unprivileged user can create the necessary condition only if the listed asset supports enough decimals/supply and the attacker can fund the supply leg and collateral for a very large borrow. The required scale is far above ordinary markets, which lowers practical likelihood, but the test shows the state is reachable under legal supply/borrow calls and does not require privileged access, oracle manipulation, or malformed input beyond large amounts.

### Recommendation
Bound the **value domain**, not just the index domain. During accrual, compute utilization and debt totals with saturating or wide (`I256`) arithmetic, or explicitly cap scaled share totals so `scaled * index` cannot exceed `i128::MAX`. Enforce a maximum scaled supply/debt per market at `supply`/`borrow`/`create_strategy` time based on `MAX_SUPPLY_INDEX_RAY`/`MAX_BORROW_INDEX_RAY`, and add an emergency path that can settle or write down positions without first running the panicking `scaled_to_original` conversion.

### Proof of Concept
Using the harness pattern in `large_positions_and_long_horizons.rs`:

1. List an 18-decimal asset with a steep rate curve and disable the max-utilization cap for the test market.
2. `supply(BOB, BIG18, 1_000_000_000 * 10^18)`.
3. Supply collateral to `ALICE` and `borrow(ALICE, BIG18, 98% of supplied)`.
4. Advance ledger time in one-year chunks while calling unprivileged `controller.update_indexes(caller, [HubAssetKey { hub_id, asset: BIG18 }])`.
5. When the accrued RAY debt value crosses `i128::MAX`, `update_indexes` reverts with `MATH_OVERFLOW` while the stored borrow index is still below `MAX_BORROW_INDEX_RAY`.
6. Subsequent `withdraw(BOB, BIG18, 1)` and `repay(ALICE, BIG18, …)` revert for the same reason because they accrue first.

### Citations

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

**File:** common/src/rates/simulate.rs (L60-66)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-352)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L354-356)
```rust
    // The market is frozen: exits and repayments accrue first and hit the same panic.
    assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
    assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```
