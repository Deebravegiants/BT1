### Title
RAY market-value overflow permanently freezes large lending markets - (File: common/src/rates/simulate.rs)

### Summary
`accrue_step` converts aggregate scaled debt and supply back into RAY-denominated values by computing `scaled * index / RAY`; once that quotient exceeds `i128::MAX`, `Ray::mul` panics with `MathOverflow`. [1](#0-0) [2](#0-1) [3](#0-2) 

Because `global_sync` marks the market accrued only after all chunks complete, the panic leaves `last_timestamp` unchanged and every subsequent synced operation repeats the same overflowing calculation. [4](#0-3) [5](#0-4) 

### Finding Description
The permissionless controller entrypoint `update_indexes(caller, assets)` accepts ordinary caller authorization and forwards the requested `Vec<HubAssetKey>` to the pool. [6](#0-5) [7](#0-6) 

For each requested market, `ops::market::accrue` loads the cache, invokes `interest::global_sync`, and only then commits the state. [8](#0-7) 

`accrue_step` evaluates `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` before updating either index. [1](#0-0) 

`scaled_to_original` delegates to `Ray::mul`, which uses `mul_div_half_up`; that helper panics with `MathOverflow` when the exact quotient cannot fit into `i128`. [2](#0-1) [9](#0-8) 

The same market-value overflow can also occur later in the step when accrued debt is computed as `borrowed * new_borrow_index / RAY` and `borrowed * old_borrow_index / RAY`. [10](#0-9) 

The configured borrow-index ceiling is `10^36`, but a debt book of approximately `0.98e36` scaled units overflows once the index exceeds roughly `1.735e29` raw RAY—about `173.5` times the initial index and far below the configured ceiling. [11](#0-10) [12](#0-11) 

### Impact Explanation
Once the market crosses the value ceiling, `update_indexes` cannot commit a later timestamp, so the overflow is deterministic on every future accrual attempt. [4](#0-3) 

Supply, borrow, withdraw, repay, liquidation, strategy, and flash paths load an interest-synced market through `synced_market` or `load_leg`, so they all reach the same panic before mutating or settling the market. [13](#0-12) 

Consequently, suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot execute liquidation withdrawals or repayments through the normal controller paths; funds already held by the pool remain frozen absent a privileged recovery or upgrade. [14](#0-13) [15](#0-14) [16](#0-15) 

This is a protocol-wide market freeze rather than a single-position failure because the overflowing multiplication uses aggregate `supplied` and `borrowed` totals shared by every position in the market. [17](#0-16) 

### Likelihood Explanation
A single unprivileged caller can fund a supply account, fund collateral on a second market or account, borrow most of the large market, and later call `update_indexes(caller, vec![hub_asset])` with their own authorization. [18](#0-17) [6](#0-5) 

The checked-in scenario supplies `1e27` base units of an 18-decimal asset and borrows 98% of it, demonstrating that the admitted accounting domain permits the scaled-debt total needed to reach the cliff. [19](#0-18) 

The likelihood is constrained by the substantial token liquidity and collateral required, but no privileged parameter change, leaked key, oracle manipulation, or third-party cooperation is required once suitable listed markets and caps exist. [7](#0-6) [11](#0-10) 

### Recommendation
Enforce a worst-case scaled-share ceiling at debt and supply minting, not merely an asset-unit input cap, so that `scaled * MAX_*_INDEX / RAY` remains representable for the configured index ceiling. [20](#0-19) [21](#0-20) 

For the current `10^36` index ceiling, the raw scaled-share bound is approximately `i128::MAX / 10^9`; market usage should be rejected before `supplied` or `borrowed` can exceed that bound. [11](#0-10) 

Alternatively, make accrual explicitly saturate or close out interest at a market-specific index ceiling derived from the current scaled totals before performing the overflowing multiplication; silently proceeding to the current fixed index ceiling does not prevent the earlier valuation panic. [22](#0-21) [23](#0-22) 

Add the existing whale-market scenario as a release-blocking regression test and extend it to assert that minting is rejected before the unrecoverable state is reached. [24](#0-23) 

### Proof of Concept
The repository’s harness already demonstrates the vulnerable sequence: configure a large 18-decimal market, deposit `1e27` units, supply collateral in a second market, borrow `98e25` units, advance ledger time, then invoke index updates until `scaled_to_original` overflows. [24](#0-23) [25](#0-24) 

```rust
let principal = 1_000_000_000i128 * 10i128.pow(18);
t.supply_raw(attacker_supply_account, "BIG18", principal);
t.supply_raw(attacker_borrow_account, "COL", required_collateral);
t.borrow_raw(attacker_borrow_account, "BIG18", principal * 98 / 100);

// After index growth makes borrowed * borrow_index / RAY exceed i128::MAX:
assert_contract_error(
    t.try_update_indexes_for(&["BIG18"]),
    errors::MATH_OVERFLOW,
);
assert_contract_error(
    t.try_withdraw_raw(attacker_supply_account, "BIG18", 1),
    errors::MATH_OVERFLOW,
);
assert_contract_error(
    t.try_repay(attacker_borrow_account, "BIG18", 1),
    errors::MATH_OVERFLOW,
);
```

The test explicitly identifies the overflow as occurring before the borrow-index cap and confirms that withdrawal and repayment fail with `MATH_OVERFLOW` after the cliff is reached. [26](#0-25)

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

**File:** common/src/rates/scaling.rs (L12-15)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** contracts/pool/src/interest.rs (L25-32)
```rust
    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
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

**File:** common/src/math/fp_core.rs (L104-117)
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

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-319)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-333)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L335-344)
```rust
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L347-356)
```rust
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

**File:** contracts/pool/src/ops/withdraw.rs (L61-80)
```rust
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
    let net_transfer = withhold_liquidation_fee(
        env,
        &mut cache,
        gross_amount,
        is_liquidation,
        entry.protocol_fee,
    );

    // A footprint-only close must not add a utilization gate to same-market
    // net settlement: it burns no shares and moves no cash.
    let empty_close = position.raw() == 0 && entry.action.amount == i128::MAX;
    gate_and_debit(env, &mut cache, net_transfer, is_liquidation || empty_close);

```

**File:** contracts/pool/src/ops/repay.rs (L40-57)
```rust
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

    cache.credit_cash(net_repay);
```

**File:** contracts/pool/src/ops/supply.rs (L28-36)
```rust
    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
        amount == 0 || minted.raw() > 0,
        GenericError::SupplyRoundsToZeroShares
    );

    position = position.checked_add(env, minted);
    cache.mint_supply(minted);
```

**File:** contracts/pool/src/ops/borrow.rs (L63-78)
```rust
pub(crate) fn mint_debt(env: &Env, cache: &mut Cache, position: &mut Ray, amount: i128) {
    require_positive_amount(env, amount);
    cache.require_reserves(amount);
    guards::require_liquidation_buffer(env, cache, amount);

    let minted = cache.calculate_scaled_borrow(amount);

    assert_with_error!(
        env,
        minted.raw() > 0,
        GenericError::BorrowRoundsToZeroShares
    );

    *position = position.checked_add(env, minted);
    cache.mint_debt(minted);
    guards::require_utilization_below_max(env, cache);
```
