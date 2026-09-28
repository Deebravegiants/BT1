### Title
Interest accrual overflows scaled Ray balances and freezes a high-utilization market - (File: common/src/rates/simulate.rs)

### Summary
The pool computes accrued utilization by multiplying stored scaled balances by their RAY indexes before applying the borrow-index cap. For a sufficiently large market, `scaled * index` exceeds `i128::MAX` while the index remains far below `MAX_BORROW_INDEX_RAY`, causing every subsequent state-changing operation on that market to revert. [1](#0-0) [2](#0-1) 

### Finding Description
`accrue_step` first reconstructs `borrowed_original` and `supplied_original` through `scaled_to_original`, which is simply `scaled.mul(index)` and therefore panics on `i128` overflow. [3](#0-2) [4](#0-3)  It then multiplies the unchanged scaled debt by both the new and old borrow indexes in `calculate_supplier_rewards`, creating another overflow point. [5](#0-4) 

The borrow-index cap is applied only after `old_index * interest_factor`, and it bounds the index at approximately `10^9`, not the resulting token value. [6](#0-5)  Consequently, a market can reach the value ceiling long before the index ceiling. [2](#0-1) 

`Controller::update_indexes(caller, assets)` is permissionless and forwards the selected hub assets to the pool. [7](#0-6)  The pool's `update_indexes` and every ordinary market mutation load the cache and run `global_sync` before processing the requested operation. [8](#0-7) [9](#0-8) 

### Impact Explanation
Once the scaled balance times the live index overflows, the market can no longer accrue, so repayments, withdrawals, borrows, liquidations, revenue claims, and subsequent keeper calls against that market all revert before reaching their operation-specific logic. [9](#0-8)  This freezes supplier principal and yield and prevents borrowers or liquidators from reducing the debt that caused the condition. [10](#0-9) 

The repository already contains a live regression demonstrating this condition: a one-billion-token, 18-decimal market at 98% utilization eventually returns `MathOverflow` from `update_indexes`, and both withdrawal and repayment then fail with the same error while the borrow index is still below its cap. [11](#0-10) [12](#0-11) 

### Likelihood Explanation
The trigger is an existing high-decimal market whose aggregate scaled debt or supply approaches `i128::MAX / current_index`, followed by sustained utilization long enough for index growth to cross that ratio. [1](#0-0)  An unprivileged caller only has to submit `update_indexes(caller, [hub_asset])` after enough time has elapsed; the controller requires ordinary caller authorization but no privileged role. [13](#0-12) 

The capital requirement is substantial and depends on the asset's decimals, configured caps, liquidity, and interest-rate curve, so this is not a zero-cost or immediate attack. [14](#0-13)  Nevertheless, the demonstrated configuration uses otherwise ordinary `supply`, `borrow`, and `update_indexes` flows, and the resulting failure is persistent rather than an isolated bad input. [15](#0-14) 

### Recommendation
Bound market size by the maximum representable scaled value at the configured index ceiling, not only by token-unit caps, and enforce that bound before minting supply or debt. [16](#0-15)  Accrual should also use widened or saturating scaled-value calculations, and capped indexes must be applied before any arithmetic that can overflow. [6](#0-5) 

Repayment, withdrawal, liquidation, bad-debt cleanup, and recapitalization should retain a bounded path when accrued value reaches the ceiling—for example by capping the index/value first or bypassing further reward distribution—so debt reduction and user exits cannot become permanently unreachable. [9](#0-8) 

### Proof of Concept
For an asset with decimals `d`, a native supply of `P` produces approximately `P * 10^(27-d)` scaled supply shares. Borrowing `U` of that value produces approximately `U * P * 10^(27-d)` scaled debt shares. [16](#0-15)  Accrual overflows when `borrowed_scaled * borrow_index / RAY > i128::MAX`; for `d = 18`, `P = 1_000_000_000`, and `U = 98%`, the debt is about `9.8e35` scaled units and the crossing index is only about `170 * RAY`, far below the `10^9 * RAY` index cap. [2](#0-1) 

Using the repository's test scenario, an unprivileged account can:

1. Supply `1_000_000_000` units of an 18-decimal asset through `Controller::supply`.
2. Supply sufficient collateral and borrow `980_000_000` units through `Controller::borrow`.
3. Leave the market at high utilization while the steep interest curve compounds.
4. Call `Controller::update_indexes(caller, [hub_asset])`.

The test performs those operations with `principal = 1e9 * 10^18` and `debt = 98%` of principal. [17](#0-16)  After repeated yearly accrual, `update_indexes` returns `MathOverflow`, the stored borrow index remains below `MAX_BORROW_INDEX_RAY`, and both `withdraw` and `repay` fail with `MathOverflow`. [18](#0-17)

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

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L35-56)
```rust
/// Converts an asset-unit `amount` to a scaled supply `Ray` using floor
/// rounding relative to `supply_index`.
pub fn calculate_scaled_supply(env: &Env, amount: i128, decimals: u32, supply_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_floor(env, supply_index)
}

/// Converts an asset-unit `amount` to a scaled supply `Ray` using ceiling
/// rounding relative to `supply_index`.
pub fn calculate_scaled_supply_ceil(
    env: &Env,
    amount: i128,
    decimals: u32,
    supply_index: Ray,
) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, supply_index)
}

/// Converts an asset-unit `amount` to a scaled borrow `Ray` using ceiling
/// rounding relative to `borrow_index`.
pub fn calculate_scaled_borrow(env: &Env, amount: i128, decimals: u32, borrow_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, borrow_index)
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

**File:** common/src/rates/index.rs (L73-86)
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

**File:** contracts/pool/src/ops/mod.rs (L29-39)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
}

/// Renews instance TTL, then loads and accrues the market.
pub(crate) fn renewed_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    renew_instance(env);
    synced_market(env, hub_asset)
```

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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-319)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
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
