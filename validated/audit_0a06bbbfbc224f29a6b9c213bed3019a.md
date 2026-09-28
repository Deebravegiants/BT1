### Title
Unchecked RAY-scaled market-value overflow permanently freezes borrowing, repayment, withdrawal, and liquidation - ([File: contracts/pool/src/cache/scale.rs](contracts/pool/src/cache/scale.rs))

### Summary
`Cache::calculate_utilization` materializes total borrowed and supplied value with `scaled_to_original`, which multiplies RAY-scaled share totals by their indexes and panics when the result exceeds `i128::MAX`. [1](#0-0) [2](#0-1)  Every pool operation loads a synchronized market before applying its state transition, so once accrual reaches this arithmetic boundary, subsequent calls fail before users can reduce the unsafe totals. [3](#0-2)  The repository contains a reproducible scenario in which a billion-unit, 18-decimal market at sustained 98% utilization reaches `MathOverflow` below the borrow-index ceiling, after which repayment and withdrawal continue to fail. [4](#0-3) 

### Finding Description
A permissionless `update_indexes` call invokes the pool's accrual path for attacker-selected market keys. [5](#0-4) [6](#0-5)  Accrual processes elapsed time through `interest::global_sync`, and the shared RAY arithmetic panics with `GenericError::MathOverflow` when a calculated fixed-point result cannot fit in `i128`. [7](#0-6) [8](#0-7) [9](#0-8) 

An attacker with sufficient assets can create the prerequisite market state using only user-reachable operations: call `supply` with `account_id = 0` to create and fund an account, supply collateral, and call `borrow` against that account to establish sustained high utilization. [10](#0-9)  As time passes, the growing borrow index increases the exact debt value until the next accrual calculation overflows. [11](#0-10) [12](#0-11) 

The overflow is self-reinforcing because risk-reducing exits use the same synchronized-market loader before burning debt or supply shares. [3](#0-2)  Therefore, `withdraw`, `repay`, and liquidation paths cannot execute the state changes that would bring the market back below the numeric boundary. [13](#0-12) 

### Impact Explanation
This is a permanent market-level denial of service: suppliers cannot withdraw collateral or supplied assets, borrowers cannot repay, and liquidators cannot execute the accrual-dependent liquidation path for the affected market. [3](#0-2) [14](#0-13)  The last committed accrual timestamp remains behind the ledger time because the panic occurs before the cache commits, so retrying does not progress the market. [7](#0-6) [15](#0-14)  Since user funds remain represented by pool positions while all risk-reducing paths trap, the impact is permanent freezing of user funds absent a privileged contract upgrade or other external remediation. [3](#0-2) 

### Likelihood Explanation
Exploitation requires a listed market whose configured caps and available liquidity permit extremely large aggregate values, sustained high utilization, and enough time for index growth. [16](#0-15)  The deterministic harness reaches the failure with a billion-unit 18-decimal market, 98% utilization, and repeated annual accruals, demonstrating that the state is reachable through ordinary supply, collateralization, borrow, and index-update mechanics rather than privileged storage corruption. [17](#0-16)  Its capital and configuration prerequisites are substantial, which limits practical likelihood, but no authorization beyond the attacker's own token custody and normal controller calls is needed once such a market configuration exists. [10](#0-9) [18](#0-17) 

### Recommendation
Refactor utilization and accrual calculations so they never need to materialize a total value outside the `i128` domain; compute the required ratio with widened arithmetic or an equivalent reduced-ratio implementation, and preserve checked output bounds only where an `i128` result is actually stored or transferred. [1](#0-0) [9](#0-8)  Additionally, add a pre-overflow market guard and regression test that proves `update_indexes`, `repay`, `withdraw`, and liquidation remain executable as scaled totals approach the boundary. [3](#0-2) [13](#0-12) 

### Proof of Concept
1. On an 18-decimal market configured with sufficiently high caps, attacker-controlled BOB supplies `1_000_000_000 * 10^18` base units of the debt asset. [19](#0-18) 
2. Attacker-controlled ALICE supplies sufficient collateral and borrows 98% of that market through `borrow`. [20](#0-19) 
3. Advance ledger time and repeatedly call permissionless `update_indexes(caller, [hub_asset])`; the accrual eventually fails with `GenericError::MathOverflow` while the borrow index remains below its configured ceiling. [18](#0-17) [21](#0-20) 
4. Call `withdraw` for one unit of BOB's supply and `repay` for part of ALICE's debt; both calls load and accrue the market first and revert with the same `MathOverflow`. [3](#0-2) [14](#0-13)

### Citations

**File:** contracts/pool/src/cache/scale.rs (L19-26)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/pool/src/cache/mod.rs (L73-85)
```rust
    /// Persists the full market state and returns a snapshot for events.
    pub(crate) fn commit(&self) -> MarketStateSnapshot {
        let state = PoolStateRaw {
            supplied: self.supplied.raw(),
            borrowed: self.borrowed.raw(),
            revenue: self.revenue.raw(),
            borrow_index: self.borrow_index.raw(),
            supply_index: self.supply_index.raw(),
            last_timestamp: self.last_timestamp,
            cash: self.cash,
        };
        storage::write_state(&self.env, &self.hub_asset, &state);
        self.snapshot()
```
