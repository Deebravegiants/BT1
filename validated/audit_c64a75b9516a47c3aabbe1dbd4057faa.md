### Title

Accrual-time `i128` overflow permanently freezes an overgrown debt market - (File: contracts/pool/src/interest.rs)

### Summary

A market whose scaled debt multiplied by the borrow index exceeds the `i128` range cannot complete interest accrual because `scaled_to_original` panics on overflow. Since `update_indexes`, `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, and every other pool mutation all run accrual first, the market becomes permanently unusable and its funds cannot be recovered. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description

`Controller::update_indexes` is callable by any authorized address and forwards the supplied `HubAssetKey` list to `pool_update_indexes_call`. [4](#0-3)  The pool's `update_indexes` entrypoint calls `ops::market::accrue`, which invokes `interest::global_sync` before committing state. [5](#0-4) [6](#0-5) 

`global_sync` calls `accrue_chunk`, which passes the stored scaled borrow total into `accrue_step`. [7](#0-6) [8](#0-7)  Utilization and debt-value calculations unscale debt through `scaled_to_original`, which computes `scaled * index / RAY` through `Ray::mul`. [9](#0-8) [2](#0-1) 

`Ray::mul` delegates to `mul_div_half_up`, which widens the intermediate product to `I256` but still requires the final quotient to fit `i128`. [10](#0-9) [11](#0-10)  If the post-accrual debt value exceeds `i128::MAX`, the conversion returns `None` and is converted into `GenericError::MathOverflow`; the transaction then reverts before `cache.mark_accrued()` or `cache.commit()` can execute. [12](#0-11) [13](#0-12) 

The stale `last_timestamp` remains in storage, so every later call calculates a still-elapsed interval and reaches the same overflow again. [1](#0-0)  `withdraw` reaches this through `ops::load_leg`, `repay` reaches it through the same helper, and every other mutation uses `synced_market` or `load_leg`, leaving no ordinary state transition that can reduce debt, realize bad debt, or bypass accrual. [14](#0-13) [15](#0-14) [3](#0-2) 

### Impact Explanation

This is a permanent market-level denial of service: suppliers cannot withdraw the affected asset, borrowers cannot repay it, liquidators cannot seize collateral or socialize bad debt, and even `recapitalize` and `claim_revenue` cannot reach the market because they sync first. [3](#0-2) [16](#0-15) 

The condition is not bounded by the configured borrow-index ceiling, because the representable debt value `borrowed_scaled * borrow_index / RAY` can exceed `i128::MAX` while the index itself is still below the protocol ceiling. [2](#0-1) [17](#0-16) 

### Likelihood Explanation

The bug requires an already-admitted market to accumulate enough scaled debt and enough index growth that their unscaled value exceeds `i128::MAX`. [2](#0-1) [11](#0-10) 

For an eighteen-decimal market, one billion whole tokens is already `1e36` in RAY representation, and a 98% utilization debt book overflows once the borrow index reaches roughly 170×, far below the protocol index ceiling. [18](#0-17) [19](#0-18) 

Once ledger time has advanced enough for this condition, a single unprivileged caller only needs to invoke `controller.update_indexes(caller, vec![hub_asset])`, after which the state cannot advance past the failed accrual. [4](#0-3) [6](#0-5) 

### Recommendation

Compute utilization and accrual intermediates in `I256`, or calculate the utilization ratio without materializing `borrowed * borrow_index` in `i128`. [9](#0-8) [12](#0-11) 

Cap the next borrow index at the largest value for which the current scaled debt remains representable, then commit `last_timestamp` so repayment, withdrawal, liquidation, and bad-debt cleanup remain callable while further interest accrual is disabled or safely clamped. [1](#0-0) [8](#0-7) 

Also enforce borrow and supply caps against worst-case future index growth, not only the current index, and add a regression proving that `repay`, `withdraw`, and `liquidate` remain executable after the market reaches its representability bound. [20](#0-19) [17](#0-16) 

### Proof of Concept

1. On an admitted eighteen-decimal market whose caps allow the exposure, an account supplies approximately `1_000_000_000 * 10^18` base units through `controller.supply(caller, account_id, spoke_id, vec![(hub_asset, amount)])`. [21](#0-20) [22](#0-21) 

2. A sufficiently collateralized borrower takes roughly 98% of that liquidity through `controller.borrow(caller, account_id, vec![(hub_asset, debt)], to)`. [23](#0-22) [24](#0-23) 

3. After enough ledger time has elapsed for `borrowed_scaled * borrow_index / RAY` to exceed `i128::MAX`, an unprivileged caller invokes `controller.update_indexes(caller, vec![hub_asset])`. [4](#0-3) [2](#0-1) 

4. The call reaches `global_sync`, panics with `MathOverflow`, and leaves `last_timestamp` unchanged. [1](#0-0) [12](#0-11) 

5. Subsequent `withdraw`, `repay`, `liquidate`, and `clean_bad_debt` transactions reach `synced_market` and fail with the same error before their state changes can execute. [3](#0-2) [14](#0-13) [15](#0-14)

### Citations

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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L18-33)
```rust
/// Converts an asset-unit `cap` to a scaled `Ray` value, rounding down.
///
/// The division saturates at `i128::MAX` instead of panicking, so the cap check
/// fails open rather than trapping an entry path. The asset-to-RAY
/// rescale still panics on overflow; listings validate caps with
/// [`crate::validation::require_cap_within_asset_domain`]. Position accounting
/// uses [`calculate_scaled_supply`] and [`calculate_scaled_borrow`], which panic
/// on overflow.
pub fn calculate_scaled_cap(env: &Env, cap: i128, decimals: u32, index: Ray) -> Ray {
    Ray::from(fp_core::mul_div_floor_saturating(
        env,
        Ray::from_asset(env, cap, decimals).raw(),
        RAY,
        index.raw(),
    ))
}
```

**File:** contracts/pool/src/ops/mod.rs (L29-47)
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
}
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

**File:** contracts/controller/src/markets.rs (L140-164)
```rust
/// Transfers funds to the pool, credits the measured receipt up to the backing
/// shortfall, and refunds unused funds. Returns credited cash; rejects flash loans.
pub(crate) fn recapitalize(
    env: &Env,
    payer: Address,
    hub_asset: HubAssetKey,
    amount: i128,
) -> i128 {
    validation::require_authorized_caller(env, &payer);
    require_positive_amount(env, amount);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    // Prefund the pool and credit only its measured receipt.
    let received = payments::transfer_amount_measured(
        env,
        &hub_asset.asset,
        &payer,
        &pool_addr,
        amount,
        GenericError::AmountMustBePositive,
    );

    pool_recapitalize_call(env, &pool_addr, &hub_asset, &payer, received).actual_amount
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

**File:** contracts/pool/src/cache/scale.rs (L19-27)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
    }
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
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

**File:** contracts/pool/src/ops/repay.rs (L40-45)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
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

**File:** contracts/controller/src/lib.rs (L90-102)
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
```

**File:** contracts/controller/src/lib.rs (L104-115)
```rust
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
