### Title
Interest accrual overflows the RAY debt value and permanently freezes a large market - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary

A sufficiently large borrowed book can exceed the `i128` RAY-value domain before the configured borrow-index ceiling is reached. The next permissionless `update_indexes` call then panics inside `scaled_to_original`; because every pool mutation accrues interest before repayment, withdrawal, liquidation, or rate-model replacement, the market can no longer process any state-changing operation. [1](#0-0) [2](#0-1) 

### Finding Description

`accrue_step` unconditionally converts the stored scaled debt and supply into RAY-denominated values by calling `scaled_to_original` before calculating utilization, the borrow rate, and the next indexes. [1](#0-0)  `scaled_to_original` calls `Ray::mul`, which delegates to `mul_div_half_up`. [3](#0-2) [4](#0-3) 

`mul_div_half_up` widens the intermediate multiplication to `I256`, but panics with `MathOverflow` when the resulting quotient does not fit in `i128`. [5](#0-4)  The borrow index is capped only after calculating the candidate index, and no corresponding bound enforces `borrowed * borrow_index <= i128::MAX` for every index up to `MAX_BORROW_INDEX_RAY`. [6](#0-5) 

An unprivileged caller can create an account and supply assets through `Controller::supply(caller, account_id, spoke_id, assets)`, borrow through `Controller::borrow(caller, account_id, borrows, to)`, and later invoke `Controller::update_indexes(caller, assets)` for the affected `HubAssetKey`. [7](#0-6) [8](#0-7)  The controller forwards `update_indexes` to the pool, and the pool calls `global_sync` for each requested market. [9](#0-8) [10](#0-9) 

Once the book is large enough, ordinary index growth makes the initial `borrowed * borrow_index` value overflow before the index ceiling engages. [11](#0-10)  The checked panic rolls back the accrual, leaving `last_timestamp` and the indexes unchanged, so the same boundary is encountered on every subsequent call. [12](#0-11) [13](#0-12) 

### Impact Explanation

This permanently freezes the affected market under the deployed arithmetic model: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot seize collateral, and `update_indexes` cannot advance state. [14](#0-13)  The frozen state also prevents governance from changing the market's rate model through the normal path because `replace_rate_model` accrues under the old model before writing new parameters. [15](#0-14) 

All cash and outstanding claims in that market remain locked even though borrowers and suppliers may be solvent and willing to transact. [16](#0-15) [17](#0-16)  The resulting impact is permanent freezing of user funds and a market unable to operate without a privileged contract upgrade or other out-of-protocol remediation. [18](#0-17) 

### Likelihood Explanation

Triggering the condition requires a very large market and sustained high utilization rather than a small one-transaction input. [19](#0-18)  The admitted token domain nevertheless permits the required scale: for 18 decimals, the maximum cap is approximately 170 billion whole tokens, while a 1-billion-token deposit uses approximately `1e36` scaled RAY units. [20](#0-19) [11](#0-10) 

A single attacker with sufficient collateral and token inventory can establish the state with ordinary `supply` and `borrow` calls, after which anyone can trigger the first failing accrual through permissionless `update_indexes`. [7](#0-6) [8](#0-7)  The repository's stress test demonstrates that a 1-billion-token, 18-decimal market at 98% utilization reaches this boundary within the tested horizon while `borrow_index` remains below `MAX_BORROW_INDEX_RAY`. [21](#0-20) 

Likelihood is constrained by the capital requirement, market cap configuration, and the need for interest to accumulate without enough repayment or withdrawal to keep the scaled value below the boundary. [22](#0-21) 

### Recommendation

Enforce a forward-looking scaled-debt and scaled-supply bound at mint time so `scaled * MAX_*_INDEX_RAY / RAY` remains representable for the full configured index domain. [6](#0-5) [23](#0-22)  Alternatively, rework accrual to perform utilization and debt/supply totals in a wider representation such as `I256`, with explicit bounds before any value is narrowed to `i128`. [24](#0-23) 

Any remediation should also provide a recovery path that can lower the rate model or otherwise reduce future accrual without first multiplying the already-overflowing stored book by its current index. [15](#0-14)  The bound should be tested at both `MAX_BORROW_INDEX_RAY` and the value-overflow boundary rather than only against the token amount admitted by `max_cap_for_decimals`. [20](#0-19) 

### Proof of Concept

The existing stress test creates an 18-decimal market, supplies `1_000_000_000 * 10^18` base units, supplies separate collateral, and borrows 98% of the large market's principal. [25](#0-24)  It then advances ledger time yearly and invokes the permissionless index-update path until `update_indexes` returns `MathOverflow` while the borrow index is still below `MAX_BORROW_INDEX_RAY`. [26](#0-25) 

The transaction-level sequence is:

```rust
// 1. Create or use an account in a spoke whose caps admit the position.
controller.supply(
    attacker,
    0,
    spoke_id,
    vec![(collateral_key, sufficient_collateral)],
);

// 2. Supply enough of the vulnerable asset to place its scaled RAY value
// close to the i128 RAY-value ceiling divided by a reachable index.
controller.supply(
    attacker,
    account_id,
    spoke_id,
    vec![(debt_asset_key, 1_000_000_000 * 10i128.pow(18))],
);

// 3. Borrow at sustained high utilization.
controller.borrow(
    attacker,
    account_id,
    vec![(debt_asset_key, 980_000_000 * 10i128.pow(18))],
    Some(attacker),
);

// 4. After enough index growth, anyone calls:
controller.update_indexes(attacker, vec![debt_asset_key]);
// -> MathOverflow inside scaled_to_original
```

After that call crosses the boundary, both `withdraw(attacker, account_id, vec![(debt_asset_key, 1)], None)` and `repay(attacker, account_id, vec![(debt_asset_key, amount)])` fail with `MathOverflow` because their pool legs call `global_sync` before mutating positions. [27](#0-26) [2](#0-1)

### Citations

**File:** common/src/rates/simulate.rs (L51-66)
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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/math/fp_core.rs (L104-140)
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

/// Computes `x * y / d` rounded half up. Returns `None` if `x < 0`, `y < 0`, `d <= 0`, or the
/// result does not fit in `i128`.
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
```

**File:** common/src/rates/index.rs (L11-19)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
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

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
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

**File:** contracts/pool/src/ops/market.rs (L60-72)
```rust
/// Accrues interest for each market in `hub_assets` and emits one state event
/// per market.
///
/// Always commits state so same-ledger simulation records the write footprint
/// needed if time advances before transaction inclusion.
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

**File:** contracts/pool/src/ops/borrow.rs (L38-49)
```rust
/// Runs borrow accounting without transferring tokens.
///
/// Updates the user's scaled debt position by `entry.action.amount` in asset
/// units, debits market cash, and commits state.
pub(crate) fn accounting(env: &Env, entry: &PoolBorrowEntry) -> BorrowOutcome {
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    mint_debt(env, &mut cache, &mut position, amount);
    cache.debit_cash(amount);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/repay.rs (L36-55)
```rust
/// Accrues interest, resolves the repay amount into burned debt shares and
/// overpayment, burns the shares, and credits the net repay to cash without
/// transferring the overpayment refund. Panics if a positive net repay would
/// burn zero scaled shares.
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );

    let position = position.checked_sub(env, burned);
    cache.burn_debt(burned);
```

**File:** contracts/pool/src/lib.rs (L119-126)
```rust
    /// Upgrades the contract WASM to `new_wasm_hash`, extending instance TTL
    /// first. Restricted to the owner.
    #[only_owner]
    fn upgrade(env: Env, new_wasm_hash: BytesN<32>) {
        renew_instance(&env);
        env.deployer()
            .update_current_contract(ContractExecutable::Wasm(new_wasm_hash));
    }
```

**File:** common/src/validation.rs (L41-69)
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
```
