### Title
A permissionless index update can permanently freeze an oversized market when accrual overflows the RAY value domain - (File: contracts/pool/src/interest.rs)

### Summary
`Controller::update_indexes` is permissionless and forwards a caller-selected market list to the pool, where `accrue` runs `global_sync` before committing state. [1](#0-0) [2](#0-1)  Each accrual step unscales aggregate borrowed and supplied shares through `scaled_to_original`, which performs checked RAY multiplication and panics when the resulting value exceeds `i128::MAX`. [3](#0-2) [4](#0-3) [5](#0-4)  Once the product of a market's scaled book and index approaches the `i128` ceiling, the next permissionless accrual panics before `last_timestamp` is updated, making every later accrual-first operation on that market revert. [6](#0-5) [7](#0-6) 

### Finding Description
The vulnerable path is `Controller::update_indexes(caller, assets)` → `pool_update_indexes_call` → `LiquidityPool::update_indexes` → `ops::market::accrue` → `Cache::load` → `interest::global_sync` → `accrue_step`. [8](#0-7) [9](#0-8) [2](#0-1)  `accrue_step` unconditionally evaluates `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` before calculating utilization and the next interest factor. [10](#0-9)  These helpers multiply two RAY-scaled `i128` values with checked fixed-point arithmetic, so a sufficiently large scaled book multiplied by a sufficiently grown index raises `MathOverflow` rather than saturating or clamping. [11](#0-10) [5](#0-4) 

The failure persists because `global_sync` calls `accrue_chunk` in a loop and only calls `mark_accrued` after all chunks complete. [12](#0-11)  A panic therefore reverts the whole invocation without advancing `last_timestamp`, so the next call starts from the same oversized interval and reaches the same overflowing conversion. [13](#0-12)  This affects more than the keeper method because all ordinary pool mutation legs load through `synced_market`, which invokes `global_sync` before the operation. [7](#0-6)  Repayment and withdrawal both enter through `load_leg`, so borrowers cannot repay and suppliers cannot withdraw from the affected market after the cliff is reached. [14](#0-13) [15](#0-14) 

The codebase already contains a production regression demonstrating this boundary: an 18-decimal market with a billion whole tokens at sustained 98% utilization eventually fails `update_indexes` with `MATH_OVERFLOW` below the index cap, after which both withdrawal and repayment fail with the same error. [16](#0-15) 

### Impact Explanation
An attacker who can cause or identify a listed market near this numeric boundary can submit `update_indexes(caller, [HubAssetKey { hub_id, asset }])` and permanently freeze that market's state transition. [1](#0-0) [2](#0-1)  Because each failed accrual rolls back before `mark_accrued`, the condition is not cleared by retries or by choosing another mutating entrypoint. [12](#0-11) [13](#0-12)  The resulting impact is permanent freezing of supplier principal and yield, inability to repay or reduce debt, and inability to execute market mutations needed by liquidation and bad-debt resolution. [7](#0-6) [17](#0-16) 

### Likelihood Explanation
The trigger does not require privileged execution: `update_indexes` only authorizes the caller and accepts the target market list from that caller. [1](#0-0)  It does require an extreme pre-existing market state, because `scaled * index` must approach `i128::MAX`; the included proof uses a billion whole 18-decimal tokens, 98% utilization, and multiple years of high-rate accrual. [18](#0-17)  Market caps constrain whether a realistic asset can reach that state, since stored caps are bounded by the asset's RAY-domain capacity rather than a safety margin for later index multiplication. [19](#0-18)  The issue is therefore most plausible for high-decimal, very-large-supply assets after sustained utilization or unusually long accrual gaps, but once reached a single permissionless call can activate the permanent failure. [20](#0-19) 

### Recommendation
Add an explicit numeric invariant that the maximum permitted scaled supply and debt remain safely below `i128::MAX / max_index` for every supported index and asset-decimal configuration, rather than bounding caps only by the initial asset-to-RAY conversion. [21](#0-20)  During accrual, detect an impending unscale overflow before calling `scaled_to_original` and clamp or fail in a recoverable way that still permits repayments, liquidations, bad-debt processing, and owner intervention. [10](#0-9)  At minimum, cap market utilization, totals, and index growth jointly so `borrowed * borrow_index` and `supplied * supply_index` cannot exceed the RAY value domain before the declared index cap engages. [22](#0-21) 

### Proof of Concept
The repository's regression test constructs a billion-whole-token, 18-decimal market, supplies the full principal, borrows 98%, repeatedly advances one year, and invokes permissionless index updates until `MathOverflow` occurs. [23](#0-22)  It then verifies that the stored borrow index is still below `MAX_BORROW_INDEX_RAY`, so the configured index ceiling did not prevent the earlier value overflow. [24](#0-23)  Finally, the test demonstrates market freeze by showing that both a one-unit supplier withdrawal and a borrower repayment revert with `MATH_OVERFLOW`. [25](#0-24)

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

**File:** common/src/rates/simulate.rs (L51-64)
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
```

**File:** common/src/rates/simulate.rs (L157-175)
```rust
    let mut remaining = total_delta_ms;
    while remaining > 0 {
        let chunk = remaining.min(MAX_COMPOUND_DELTA_MS);
        let step = accrue_step(
            env,
            &params,
            state.borrowed,
            supplied,
            borrow_index,
            supply_index,
            chunk,
        );

        borrow_index = step.borrow_index;
        supply_index = step.supply_index;
        supplied = supplied.checked_add(env, step.revenue_shares);

        remaining -= chunk;
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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
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

**File:** contracts/pool/src/interest.rs (L39-53)
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
}
```

**File:** contracts/pool/src/ops/mod.rs (L29-34)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
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

**File:** contracts/pool/src/cache/mod.rs (L133-145)
```rust
    /// Milliseconds between last accrual and the stamped current time.
    pub(crate) fn elapsed_ms(&self) -> u64 {
        self.current_timestamp.saturating_sub(self.last_timestamp)
    }

    /// `true` when interest should be compounded before further mutations.
    pub(crate) fn needs_accrual(&self) -> bool {
        self.elapsed_ms() > 0
    }

    /// Marks the market as fully accrued through `current_timestamp`.
    pub(crate) fn mark_accrued(&mut self) {
        self.last_timestamp = self.current_timestamp;
```

**File:** contracts/pool/src/ops/repay.rs (L40-45)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
```

**File:** contracts/pool/src/ops/withdraw.rs (L62-69)
```rust
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
    let net_transfer = withhold_liquidation_fee(
        env,
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

**File:** common/src/validation.rs (L41-70)
```rust
/// Returns the largest cap, in asset base units, whose ray-scaled form still
/// fits in `i128`.
///
/// Returns 0 when `asset_decimals > RAY_DECIMALS`, since the ray form is not
/// representable in that case. Enforced by
/// [`require_cap_within_asset_domain`], so stored caps can never overflow the
/// asset→ray rescale.
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
}
```
