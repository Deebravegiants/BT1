### Unbounded RAY debt valuation overflows before the borrow-index cap, permanently freezing a market - (File: common/src/rates/index.rs)

### Summary

Interest accrual computes total debt and total supply as `scaled_shares * index`, but the resulting RAY value must still fit in `i128`. [1](#0-0)  Although the borrow index is capped at `1e12` in RAY units, that cap is checked only after index multiplication and does not bound the separate `borrowed * borrow_index` valuation. [2](#0-1) [3](#0-2) 

Consequently, a sufficiently large market at sustained high utilization can cross the `i128` RAY-value ceiling while the index remains far below its configured cap. Every later market mutation first accrues interest, so the first overflowing accrual permanently prevents repayment, withdrawal, liquidation, bad-debt processing, revenue claims, and even parameter updates for that market. [4](#0-3) [5](#0-4) 

### Finding Description

`Controller::update_indexes` is callable by any authorized external caller and forwards a chosen `Vec<HubAssetKey>` to the pool. [6](#0-5)  The pool's `update_indexes` loads each market and calls `interest::global_sync`. [7](#0-6) [8](#0-7) 

`global_sync` compounds elapsed milliseconds in bounded chunks, but each chunk still calls `accrue_step` with the unbounded scaled debt and current index. [9](#0-8)  The shared index logic multiplies scaled debt by both old and new borrow indexes using `Ray::mul`, which panics when the quotient cannot be represented as `i128`. [10](#0-9) [11](#0-10) 

The cap prevents the index itself from exceeding `MAX_BORROW_INDEX_RAY`, but no check rejects or saturates when `borrowed * index / RAY` exceeds `i128::MAX` before that cap is reached. [12](#0-11)  Supply-side accrual has the same structural issue through `supplied * supply_index`, and its cap likewise does not prevent the intermediate value from exceeding `i128`. [13](#0-12) 

Because all pool operation legs load an interest-synced cache, a market whose next accrual overflows cannot be rescued through normal operations. [14](#0-13)  The existing harness demonstrates this state with an 18-decimal market holding one billion whole tokens at 98% utilization on a steep rate curve: `update_indexes`, `withdraw`, and `repay` all revert with `MathOverflow`, while the committed borrow index remains below `MAX_BORROW_INDEX_RAY`. [15](#0-14) 

### Impact Explanation

The market permanently freezes once the next accrual cannot fit in `i128`. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and permissionless bad-debt cleanup cannot execute because those paths accrue the same market first. [14](#0-13)  Governance replacement of the rate model is not a recovery path because `replace_rate_model` deliberately accrues under the old model before writing new parameters. [5](#0-4) 

The result is permanent freezing of all funds represented by the affected `(hub_id, asset)` book and a protocol book whose recorded debt, supply, revenue, and cash can no longer be safely settled. This is a distinct numeric-boundary failure rather than a resource-limit or ordinary fail-closed rejection: a valid sequence of user deposits, borrowing, and permissionless accrual leaves committed state that no later transaction can process. [16](#0-15) 

### Likelihood Explanation

An unprivileged participant can establish the preconditions by supplying a very large amount of an allowed high-decimal asset and borrowing enough of it through their own sufficiently collateralized account. The protocol's configured asset cap permits up to the largest base-unit amount whose RAY representation fits `i128`; it does not reserve headroom for later multiplication by the borrow index. [17](#0-16) 

The attack is capital-intensive and requires enough time at high utilization for the index to multiply the initial RAY value beyond `i128::MAX`. It is therefore less immediate than a single-transaction exploit, but it requires no privileged action, oracle manipulation, leaked key, malicious token, or external service. Once ordinary market operation crosses the boundary, `Controller::update_indexes` can finalize the frozen state permissionlessly. [6](#0-5) 

### Recommendation

Bound the RAY-denominated value calculations, not merely the index. Before accrual, calculate whether `borrowed * new_borrow_index / RAY` and `supplied * new_supply_index / RAY` fit in `i128`; handle an overflow deterministically instead of trapping. [1](#0-0) 

Prefer clamping the relevant index to `min(index_cap, i128::MAX / scaled_amount)` for nonzero scaled amounts, then accruing only to the highest representable boundary. Protocol fee conversion already uses saturation and explicit headroom accounting and provides a useful pattern for avoiding uncontrolled share or value overflow. [18](#0-17)  Alternatively, move valuation arithmetic to a wider returned type throughout accrual and downstream accounting, although that requires broader changes because persisted share/index values remain `i128`.

### Proof of Concept

1. Configure or use a listed 18-decimal market whose caps allow at least `1_000_000_000 * 10^18` base units and whose rate model reaches a high borrow rate at high utilization. The harness's `xlm_curve` uses a 175% maximum rate and 75% optimal utilization. [19](#0-18) 
2. Attacker-controlled supplier account calls `Controller::supply` with `amount = 1_000_000_000 * 10^18` for the target `HubAssetKey`.
3. A separate attacker-controlled account supplies sufficient collateral and calls `Controller::borrow` for 98% of the target market's supply.
4. Leave the position untouched while utilization remains high. Each permissionless `Controller::update_indexes(caller, vec![target])` accrues the book to the current timestamp. [6](#0-5) 
5. When `borrowed_scaled_ray * borrow_index / RAY` no longer fits `i128`, `Ray::mul` returns an overflow through `try_mul_div_half_up` and converts it to `MathOverflow`. [20](#0-19) [11](#0-10) 
6. Thereafter, `Controller::withdraw`, `Controller::repay`, `Controller::liquidate`, `Controller::clean_bad_debt`, and `Controller::update_indexes` for that market all fail before reaching their operation-specific logic because each pool leg calls `synced_market` first. [14](#0-13) 

The repository's harness reproduces the exact cliff and confirms that the last stored index remains below `MAX_BORROW_INDEX_RAY`, while subsequent withdrawal and repayment attempts return `MathOverflow`. [21](#0-20)

### Citations

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

**File:** common/src/rates/index.rs (L29-41)
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

**File:** common/src/rates/index.rs (L91-99)
```rust
/// Converts a Ray-denominated `fee` into scaled supply-index shares
/// (`fee / supply_index`), floor-rounded and saturating on overflow. Caps the
/// result so that adding it to `supplied` cannot overflow `i128::MAX`.
pub fn protocol_fee_shares(env: &Env, fee: Ray, supply_index: Ray, supplied: Ray) -> Ray {
    let raw = fp_core::mul_div_floor_saturating(env, fee.raw(), RAY, supply_index.raw());

    let headroom = i128::MAX.saturating_sub(supplied.raw());
    Ray::from(raw.min(headroom))
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

**File:** contracts/pool/src/ops/mod.rs (L29-45)
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

**File:** contracts/pool/src/interest.rs (L20-30)
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

**File:** contracts/pool/src/cache/mod.rs (L25-41)
```rust
/// Mutable snapshot of one market for the duration of a mutation or view.
///
/// Constructed from persistent storage, updated by ops/interest, then written
/// back via [`Cache::commit`]. Does not hold a storage lock; callers must not
/// interleave commits for the same market without reloading.
pub(crate) struct Cache {
    env: Env,
    hub_asset: HubAssetKey,
    params: MarketParams,
    last_timestamp: u64,
    current_timestamp: u64,
    supplied: Ray,
    borrowed: Ray,
    revenue: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    cash: i128,
```

**File:** common/src/validation.rs (L41-56)
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
```

**File:** common/src/math/fp.rs (L80-86)
```rust
    pub fn mul_ceil(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_ceil(env, self.0, other.0, RAY))
    }

    /// Multiplies this value by `numerator / denominator`, rounding the result up.
    pub fn mul_ratio_ceil(self, env: &Env, numerator: i128, denominator: i128) -> Ray {
        Ray(fp_core::mul_div_ceil(env, self.0, numerator, denominator))
```
