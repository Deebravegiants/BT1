### Title
RAY-domain aggregate-value overflow permanently freezes a saturated lending market - (File: common/src/rates/simulate.rs)

### Summary
Interest accrual panics when the product of aggregate scaled debt or supply and its index no longer fits in `i128`, even though both indexes remain below their configured `1e36` ceiling. Once a sufficiently large, highly utilized market crosses that boundary, every mutation that accrues interest—including repayment, withdrawal, liquidation, and explicit index updates—reverts, permanently freezing the market. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`accrue_step` begins by unscaling the complete aggregate debt and supply via `scaled_to_original`, before it calculates utilization, the next borrow index, or accrued rewards. [4](#0-3)  `scaled_to_original` delegates to `Ray::mul`, which calls the checked `mul_div_half_up` implementation and panics with `MathOverflow` when the resulting RAY value exceeds `i128`. [5](#0-4) [6](#0-5) [7](#0-6) 

The borrow-index ceiling is applied only to the index itself, not to the aggregate value represented by `borrowed * borrow_index`. [8](#0-7)  Consequently, a market can remain below `MAX_BORROW_INDEX_RAY` while its aggregate debt value is already outside the representable domain. [9](#0-8) 

All pool mutations route through `synced_market` or `renewed_market`, both of which call `interest::global_sync` before performing the requested operation. [3](#0-2)  `global_sync` calls `accrue_chunk`, which executes the vulnerable `accrue_step` for every elapsed chunk. [10](#0-9)  The public controller exposes `supply`, `borrow`, `withdraw`, `repay`, and `liquidate` entrypoints that ultimately reach those synchronized pool operations. [11](#0-10) 

### Impact Explanation
Once `borrowed * borrow_index / RAY` or `supplied * supply_index / RAY` exceeds `i128::MAX`, subsequent accrual always panics before any operation-specific logic runs. [12](#0-11)  Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate the account, and permissionless index synchronization cannot commit a new accrual state. [13](#0-12) [14](#0-13)  This permanently freezes user funds and leaves the affected market unable to operate absent a contract upgrade or administrative intervention. [3](#0-2) 

The repository’s long-horizon test demonstrates this precise failure: a one-billion-token, 18-decimal market at 98% utilization eventually fails `update_indexes` with `MathOverflow`, while the stored borrow index remains below `MAX_BORROW_INDEX_RAY`; subsequent withdrawal and repayment attempts fail with the same error. [15](#0-14) 

### Likelihood Explanation
An unprivileged borrower can reach the condition on any sufficiently large listed market by borrowing close to its available liquidity, subject only to ordinary collateral, cap, utilization, and liquidity checks. [16](#0-15)  For an 18-decimal market, a 98% borrow of one billion whole tokens produces approximately `0.98e36` scaled debt shares; the aggregate debt exceeds `i128::MAX` when the borrow index reaches roughly 174 times its initial value. [17](#0-16) [18](#0-17) 

The attack requires whale-scale liquidity and sustained interest accrual rather than a single immediate transaction, but no privileged action is needed to trigger the eventual panic through `update_indexes` or any normal market mutation. [14](#0-13) [19](#0-18)  Because the failed multiplication is part of mandatory pre-operation accrual, the condition is self-sustaining after it is reached. [3](#0-2) 

### Recommendation
Make accrual domain-aware before unscaling aggregate shares. Compute the greatest safe borrow index and supply index for the current aggregate scaled balances using widened `I256` arithmetic, clamp `new_borrow_index` and `new_supply_index` to those limits as well as the existing `1e36` ceilings, and derive rewards and shortfalls only from representable values. [20](#0-19) [21](#0-20) 

At minimum, replace the initial aggregate unscaling in `accrue_step` with an overflow-safe path that caps index growth before `scaled_to_original` can panic, while preserving solvency rounding in favor of suppliers and the protocol. [22](#0-21)  Add a production regression equivalent to `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`, asserting that `update_indexes`, `repay`, `withdraw`, and liquidation remain executable when the configured index ceiling is reached. [15](#0-14) 

### Proof of Concept
Assume an admitted 18-decimal asset `A` under hub `H`, with caps permitting one billion whole tokens and an active supply of that amount.

```text
HubAssetKey market = { hub_id: H, asset: A };
u64 account_id = /* attacker account */;

// Existing market liquidity, represented by a supplier deposit.
Controller.supply(
    caller = supplier,
    account_id = supplier_account,
    spoke_id = spoke,
    assets = [(market, 1_000_000_000 * 10^18)]
);

// The attacker supplies sufficient collateral in another listed asset,
// then borrows 98% of market A.
Controller.borrow(
    caller = attacker,
    account_id = account_id,
    borrows = [(market, 980_000_000 * 10^18)],
    to = Some(attacker)
);

// Time advances until borrow_index > ~1.7376e29.
Controller.update_indexes([market]);          // MathOverflow
Controller.repay(attacker, account_id,
                 [(market, 1)]);              // MathOverflow
Controller.withdraw(supplier, supplier_account,
                    [(market, 1)], None);     // MathOverflow
Controller.liquidate(liquidator, account_id,
                     [(market, 1)], SeizeMode::Transfer); // MathOverflow
```

The pool stores the 98% borrow as approximately `0.98e36` scaled debt shares, so `borrowed * borrow_index / RAY` exceeds `i128::MAX` before the borrow index approaches its `1e36` cap. [9](#0-8)  The included test establishes the resulting `MathOverflow` on index update, withdrawal, and repayment while proving that the index cap did not engage. [23](#0-22)

### Citations

**File:** common/src/rates/simulate.rs (L60-72)
```rust
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L52-56)
```rust
/// Converts an asset-unit `amount` to a scaled borrow `Ray` using ceiling
/// rounding relative to `borrow_index`.
pub fn calculate_scaled_borrow(env: &Env, amount: i128, decimals: u32, borrow_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, borrow_index)
}
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

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
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

**File:** contracts/controller/src/lib.rs (L90-158)
```rust
    /// Supplies `assets` as collateral and returns the account id; `account_id = 0`
    /// creates an account in `spoke_id`. Third parties may only top up existing
    /// supply positions; owners and delegates may add assets.
    #[when_not_paused]
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

    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
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
    }

    /// Repays debt and seizes collateral at a health-factor-based bonus.
    /// Permissionless, including self-liquidation; requires liquidator authorization.
    /// Residual bad debt is socialized only at or below the collateral dust cap.
    ///
    /// `Transfer` pays pool cash and returns `0`. `Credit(id)` moves net supply
    /// shares to a different, authorized Normal-mode account on the same spoke;
    /// `Credit(0)` creates one. Credit mode needs no free collateral liquidity
    /// and returns the receiving account id.
    fn liquidate(
        env: Env,
        liquidator: Address,
        account_id: u64,
        debt_payments: Vec<(HubAssetKey, i128)>,
        seize_mode: SeizeMode,
    ) -> u64 {
        positions::liquidation::process_liquidation(
            &env,
            &liquidator,
            account_id,
            &debt_payments,
            seize_mode,
        )
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
