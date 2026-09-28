### Title
Accrued RAY market-value overflow permanently freezes withdrawals and repayments - (File: common/src/rates/simulate.rs)

### Summary
A sufficiently large market can cross the `i128` RAY-value domain through ordinary interest accrual before reaching the configured borrow-index ceiling. Once that happens, `accrue_step` panics while multiplying scaled balances by the stored index, and every operation that first synchronizes the market— including `update_indexes`, `withdraw`, and `repay`—reverts, leaving user funds permanently locked absent an upgrade. [1](#0-0) [2](#0-1) 

### Finding Description
Pool positions are stored as RAY-scaled shares and converted back to RAY-denominated asset value using `scaled_to_original`, which delegates to `Ray::mul` and `mul_div_half_up`. [3](#0-2) [4](#0-3)  `mul_div_half_up` raises `MathOverflow` when the representable result exceeds `i128`, rather than clamping the market index or preserving an exit path. [5](#0-4) 

Accrual unconditionally computes both `borrowed * borrow_index` and `supplied * supply_index` before deriving utilization, interest, and the new indexes. [6](#0-5)  `update_borrow_index` separately computes the uncapped product before applying `MAX_BORROW_INDEX_RAY`, so the nominal index ceiling does not prevent an intermediate or market-value overflow. [7](#0-6) 

For an 18-decimal asset, one billion whole tokens are `10^27` base units and become approximately `10^36` RAY-scaled shares; an index near `170.14 * RAY` makes `scaled * index / RAY` exceed `i128::MAX`. [8](#0-7)  The repository’s own regression test demonstrates that this value ceiling is reached before `MAX_BORROW_INDEX_RAY` and that subsequent withdrawal and repayment calls both fail with `MATH_OVERFLOW`. [9](#0-8) 

The externally reachable path is `Controller::supply` to fund the market and collateral, `Controller::borrow` to establish high utilization, and the permissionless `Controller::update_indexes` to trigger accrual. [10](#0-9) [11](#0-10)  The controller forwards accrual to the pool, whose `update_indexes` implementation loads the stored market and calls `global_sync`. [12](#0-11) [13](#0-12) 

### Impact Explanation
This causes permanent freezing of funds for every participant in the affected market: suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot force an exit because those paths first attempt the same overflowing accrual. [14](#0-13) [15](#0-14)  The failed transaction does not advance `last_timestamp` or commit a lower index, so later calls repeat the same multiplication from the already-overflowed stored state. [13](#0-12) [16](#0-15)  Even replacing the rate model accrues under the old state before updating parameters, making a non-upgrade administrative rescue unavailable. [17](#0-16) 

### Likelihood Explanation
The attack requires a market whose configured caps and actual liquidity admit very large balances, plus enough time for interest to grow the index beyond the market-specific `i128 / scaled_shares` threshold. [18](#0-17) [19](#0-18)  No privileged action is needed at trigger time because `update_indexes` is permissionless and merely requires caller authorization. [11](#0-10)  The required whale-scale liquidity and accrual-dependent trigger make this a Medium rather than an easily repeatable low-cost denial of service. [20](#0-19) 

### Recommendation
Enforce a dynamic scaled-balance ceiling derived from the maximum representable index, such as `scaled * MAX_INDEX / RAY <= i128::MAX`, on supply and borrow entry in addition to the existing asset-unit caps. [21](#0-20)  Update index calculations should compare the next index to both the configured cap and `floor(i128::MAX * RAY / scaled_amount)` using an `I256` or division-first check, rather than forming an overflowing product before clamping. [7](#0-6)  Accrual should clamp the stored index at that dynamic ceiling or provide a checked safe-exit mode for repayment, withdrawal, liquidation, and recapitalization so crossing the value domain cannot permanently brick the market. [22](#0-21) 

### Proof of Concept
Using the repository’s stress configuration, list or configure a borrowable 18-decimal asset with a steep rate curve and caps at `max_cap_for_decimals(18)`, together with sufficient collateral-market capacity. [23](#0-22) [19](#0-18) 

Call `Controller::supply(caller, 0, spoke_id, [(BIG18, 1_000_000_000 * 10^18), (COL, 30_000_000_000 * 10^7)])`; the same authorized caller can then call `Controller::borrow(caller, account_id, [(BIG18, 980_000_000 * 10^18)], to)`. [10](#0-9) [24](#0-23) 

After the borrow index crosses roughly `170 * RAY`, call `Controller::update_indexes(caller, [BIG18])`; the call reaches `accrue_step` and panics with `MathOverflow` while unscaling the scaled balance. [11](#0-10) [1](#0-0)  Subsequent `withdraw` and `repay` calls revert with the same error before burning shares or transferring funds, as demonstrated by the checked-in test assertions. [9](#0-8)

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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/math/fp_core.rs (L145-159)
```rust
/// Computes `floor(x * y / d)`, rounding toward negative infinity for a negative quotient.
/// Panics with `GenericError::DivisionByZero` if `d == 0`, or with
/// `GenericError::MathOverflow` if the result does not fit in `i128`.
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

**File:** contracts/controller/src/lib.rs (L90-115)
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

**File:** contracts/controller/src/external/pool.rs (L109-116)
```rust
/// Accrues and persists market indexes through the current ledger time.
pub(crate) fn pool_update_indexes_call(
    env: &Env,
    pool_addr: &Address,
    hub_assets: &Vec<HubAssetKey>,
) {
    LiquidityPoolClient::new(env, pool_addr).update_indexes(hub_assets)
}
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

**File:** common/src/validation.rs (L375-417)
```rust

```

**File:** docs/reference/formulas.md (L423-437)
```markdown
| Bound | Consequence |
|---|---|
| Asset decimals 0..=18 | Exact token-to-RAY upscaling. Below 3: collateral only, no flash loans, no liquidation fee, its account's only supply position, at least 2 whole units while in debt |
| Both indexes initially RAY; ceiling 10^36 | 10^9 times initial index; protocol constants |
| Supply-index floor 10^24 | At most 1,000 times the shares minted at index one for the same deposit |
| Borrow APR maximum 2 RAY | 200% annual rate; not a bound on balance growth alone |
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |

The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```
