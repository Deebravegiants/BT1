### Accrued RAY debt value can overflow `i128` and permanently freeze a market - (File: common/src/rates/simulate.rs)

### Summary

`accrue_step` converts the market-wide scaled debt and supply shares back to RAY-denominated values before calculating utilization, using `scaled.mul(index)` [1](#0-0) . That multiplication is `i128`-bounded, while the borrow-index ceiling only applies after the index has grown [2](#0-1) . Consequently, a sufficiently large market can reach a state in which `borrowed * borrow_index / RAY` overflows before `borrow_index` reaches `MAX_BORROW_INDEX_RAY`, causing every operation that accrues the market to panic with `MathOverflow` [3](#0-2) .

### Finding Description

Every market mutation loads the market through `ops::load_leg`, which calls `synced_market`, and `synced_market` unconditionally invokes `interest::global_sync` [4](#0-3) . `global_sync` runs `accrue_step` for each elapsed chunk, and `accrue_step` first computes `borrowed_original = scaled_to_original(borrowed, borrow_index)` and `supplied_original = scaled_to_original(supplied, supply_index)` [5](#0-4) [1](#0-0) . `scaled_to_original` is a checked `Ray::mul`, so once either scaled balance times its index exceeds `i128::MAX` after division by `RAY`, accrual reverts [6](#0-5) .

This is reachable with a validated rate curve: `InterestRateModel::verify` accepts any `max_borrow_rate <= MAX_BORROW_RATE_RAY`, and `MAX_BORROW_RATE_RAY` is 200% APR [7](#0-6) [8](#0-7) . The repository's own regression test constructs a valid 18-decimal market at 98% utilization under a 175% maximum-rate curve, advances time, and observes `MathOverflow` from `update_indexes` before the borrow-index cap engages [9](#0-8) .

Once that boundary is crossed, the state cannot be advanced or repaired through ordinary market operations. `update_indexes` calls `global_sync` directly [10](#0-9) ; `repay` and `withdraw` call `load_leg`, which accrues first [11](#0-10) [12](#0-11) ; and even `update_params` accrues under the old model before replacing it [13](#0-12) . The test confirms that attempted withdrawals and repayments revert with the same `MathOverflow` [14](#0-13) .

### Impact Explanation

Suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot execute the pool repayment or collateral-withdrawal legs for the affected `(hub_id, asset)` market, so user funds can be permanently frozen [15](#0-14) . Because the failed accrual occurs before the market mutation and before the model can be changed, the panic repeats on every later attempt rather than advancing `last_timestamp` to a recoverable state [4](#0-3) [13](#0-12) .

### Likelihood Explanation

The attacker does not need a privileged rate-setting function: an unprivileged account can call `supply(caller, account_id, spoke_id, assets)` and then `borrow(caller, account_id, borrows, to)` with a large position, while any caller can later invoke `update_indexes(caller, assets)` to trigger accrual [16](#0-15) [17](#0-16) . The exploit requires a very large market and sustained high utilization over time; the included proof uses one billion 18-decimal tokens supplied and 98% borrowed, both allowed by the tested cap configuration [18](#0-17) . Severity is nevertheless permanent freezing of user funds, and the repository test demonstrates that the index ceiling does not prevent the value overflow [19](#0-18) .

### Recommendation

Ensure that accrual cannot make the aggregate debt or supply value unrepresentable. In particular, either calculate `borrowed * borrow_index` and `supplied * supply_index` through widened `I256` arithmetic, or dynamically cap index growth at the largest index for which both current market totals remain inside `i128`. A defensive check should occur in `accrue_step` before `scaled_to_original`, and borrowing or supplying should reject a scaled total whose value cannot be represented at `MAX_BORROW_INDEX_RAY` and `MAX_SUPPLY_INDEX_RAY` respectively [20](#0-19) . Add a regression test asserting that the market remains repayable, withdrawable, liquidatable, and parameter-updatable at the maximum admitted aggregate balances and index ceilings [14](#0-13) .

### Proof of Concept

The repository already contains an executable scenario in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` [21](#0-20) .

1. Configure an 18-decimal market using the test's valid XLM curve: `max_borrow_rate = 175%`, `optimal_utilization = 75%`, and `max_utilization = 100%` [22](#0-21) .
2. Raise the market caps to `max_cap_for_decimals(18)`, which admits balances whose asset-to-RAY representation fits `i128` [23](#0-22) [24](#0-23) .
3. Execute `controller.supply(BOB, 0, spoke_id, [(BIG18, 1_000_000_000 * 10^18)])`.
4. Execute `controller.supply(ALICE, 0, spoke_id, [(COL, sufficient_collateral)])`, followed by `controller.borrow(ALICE, account_id, [(BIG18, 98% of supplied)], None)`; the test uses `principal / 100 * 98` [25](#0-24) .
5. Leave the position untouched until compounding pushes `borrowed * borrow_index / RAY` beyond `i128::MAX`; any caller can trigger the transition with `controller.update_indexes(caller, [BIG18])` [17](#0-16) .
6. The call reaches `accrue_step`, where `scaled_to_original(borrowed, borrow_index)` panics with `MathOverflow`; because the whole transaction reverts, no usable partial accrual is committed [20](#0-19) .
7. Subsequent `withdraw` and `repay` attempts fail for the same reason, as demonstrated by the assertions in the regression test [14](#0-13) .

### Citations

**File:** common/src/rates/simulate.rs (L51-69)
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

**File:** common/src/constants/pool.rs (L11-19)
```rust
/// Upper bound accepted for a pool's configured maximum borrow rate, in raw ray units.
pub const MAX_BORROW_RATE_RAY: i128 = 2 * RAY;

/// Share of supplied value, in BPS, that pool cash must still cover after any
/// debt mint, borrows and strategy openings alike (INV-ACCT-07).
pub const LIQUIDATION_BUFFER_BPS: i128 = 200;

/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;
```

**File:** contracts/pool/src/ops/mod.rs (L29-46)
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
}

/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/types/pool.rs (L167-195)
```rust
impl InterestRateModel {
    /// Validates that the rate curve is well-formed: a non-negative base rate, non-decreasing
    /// slopes up through the max borrow rate, a max rate within bounds and above the base
    /// rate, a utilization breakpoint sequence that is strictly increasing through
    /// `optimal_utilization` and non-decreasing to `max_utilization`
    /// (`0 < mid < optimal < RAY`, `optimal <= max <= RAY`), a reserve factor below 100%, and
    /// a flashloan fee within the configured maximum. Panics if any of these checks fails.
    pub fn verify(&self, env: &Env) {
        assert_with_error!(
            env,
            self.base_borrow_rate >= 0,
            CollateralError::BaseRateNegative
        );
        if self.slope1 < self.base_borrow_rate
            || self.slope2 < self.slope1
            || self.slope3 < self.slope2
            || self.max_borrow_rate < self.slope3
        {
            panic_with_error!(env, CollateralError::SlopeNonMonotonic);
        }
        assert_with_error!(
            env,
            self.max_borrow_rate > self.base_borrow_rate,
            CollateralError::MaxRateBelowBase
        );
        assert_with_error!(
            env,
            self.max_borrow_rate <= MAX_BORROW_RATE_RAY,
            CollateralError::MaxBorrowRateTooHigh
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L81-95)
```rust
fn lift_caps(t: &LendingTest, asset: &str, decimals: u32) {
    let cap = max_cap_for_decimals(decimals);
    let cfg = t.get_asset_config(asset);
    t.edit_asset_in_spoke_caps(
        asset,
        HARNESS_SPOKE,
        true,
        true,
        cfg.loan_to_value,
        cfg.liquidation_threshold,
        cfg.liquidation_bonus,
        cap,
        cap,
    );
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

**File:** contracts/pool/src/ops/repay.rs (L40-45)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-65)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
```

**File:** common/src/validation.rs (L48-69)
```rust
pub fn max_cap_for_decimals(asset_decimals: u32) -> i128 {
    let Some(exp) = RAY_DECIMALS.checked_sub(asset_decimals) else {
        return 0;
    };
    let upscale = 10i128
        .checked_pow(exp)
        .expect("10^(RAY_DECIMALS - asset_decimals) fits i128 for asset_decimals <= RAY_DECIMALS");
    i128::MAX / upscale
}

/// Panics with `CollateralError::AssetDecimalsTooHigh` if `asset_decimals`
/// exceeds `RAY_DECIMALS`, or with `CollateralError::InvalidBorrowParams` if
/// `cap` exceeds the value returned by `max_cap_for_decimals`.
pub fn require_cap_within_asset_domain(env: &Env, cap: i128, asset_decimals: u32) {
    if RAY_DECIMALS.checked_sub(asset_decimals).is_none() {
        panic_with_error!(env, CollateralError::AssetDecimalsTooHigh);
    }
    assert_with_error!(
        env,
        cap <= max_cap_for_decimals(asset_decimals),
        CollateralError::InvalidBorrowParams
    );
```
