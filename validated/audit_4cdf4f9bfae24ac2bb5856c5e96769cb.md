### Title
Unrecoverable RAY-value overflow can permanently freeze a high-utilization market - (File: common/src/rates/scaling.rs)

### Summary
A sufficiently large market can reach a state where `scaled_shares * index` no longer fits in `i128`. Interest accrual calculates unscaled debt and supply through `scaled_to_original`, which panics with `MathOverflow` when the fixed-point result exceeds the `i128` domain. Because every pool mutation loads the market through `synced_market` and accrues interest before applying the requested operation, one such overflow prevents subsequent supply, borrow, withdraw, repay, liquidation, revenue, and recapitalization operations for that market. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`scaled_to_original` delegates to `Ray::mul`, while the fixed-point implementation intentionally panics when the widened product’s final quotient does not fit in `i128`. The borrow and supply indexes are capped only at `MAX_BORROW_INDEX_RAY` / `MAX_SUPPLY_INDEX_RAY`; those caps do not account for the size of the scaled balance being multiplied. Consequently, an oversized book can cross the smaller effective ceiling `i128::MAX / scaled_balance` before the global index cap is reached. [2](#0-1) [4](#0-3) [5](#0-4) 

The attacker-reachable path is `Controller::supply`, followed by `Controller::borrow`, followed by permissionless `Controller::update_indexes(caller, assets)` after interest has accrued. The controller forwards `update_indexes` to the owner-gated pool function, which loads each market and invokes `global_sync`; `global_sync` repeatedly calls `accrue_step`, where the overflowing unscale occurs before the new state can be committed. [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) [10](#0-9) 

The transaction reverts before `last_timestamp` advances, so the next operation retries accrual from the same stale timestamp over an equal-or-larger interval. `repay`, `withdraw`, `supply`, and `borrow` all enter through `ops::load_leg` / `synced_market`, making the failure persistent rather than a one-call denial of service. [3](#0-2) [11](#0-10) [12](#0-11) [13](#0-12) [14](#0-13) 

### Impact Explanation
This can permanently freeze all user funds and protocol revenue in the affected hub-asset market. Suppliers cannot withdraw, borrowers cannot repay or receive new debt, liquidators cannot settle the affected positions, and recapitalization cannot restore operation because those paths all accrue the poisoned market first. [3](#0-2) [15](#0-14) [16](#0-15) 

### Likelihood Explanation
The attack requires a whale-scale balance and market configuration that admits that balance and sustained high utilization; it is not triggerable from an arbitrary small input. A single funded unprivileged address can nevertheless create a supplier account for the target asset, create a separate collateralized borrower account, draw the target market to high utilization, retain the borrowed assets, and later invoke the permissionless index update once the product crosses the `i128` boundary. Other users may reduce the position before the boundary is reached, but the attacker’s dominant position can make that economically difficult. [6](#0-5) [7](#0-6) 

### Recommendation
Enforce a scale-aware arithmetic invariant whenever supply or debt shares are minted: the stored scaled balances must remain small enough that `scaled * MAX_*_INDEX` fits in `i128`, not merely below the configured token cap. Existing index ceilings should also be reduced or made market-aware where necessary so the maximum reachable index cannot overflow the largest permitted scaled balance, and add a regression test proving that an oversized high-utilization market remains repayable, withdrawable, and liquidatable at the configured ceiling. [17](#0-16) [5](#0-4) [18](#0-17) 

### Proof of Concept
```rust
// A high-decimal target asset T is listed in hub H and spoke S.
// `attacker` is one unauthorized EOA controlling two lending accounts.

let target = HubAssetKey {
    hub_id: H,
    asset: target_token,
};
let collateral = HubAssetKey {
    hub_id: H,
    asset: collateral_token,
};

// For an 18-decimal asset, this is one billion whole tokens.
let supplied = 1_000_000_000i128 * 10i128.pow(18);

// Account 1 supplies most of the target-market liquidity.
let supplier_id = controller.supply(
    attacker,
    0,
    S,
    vec![env, (target.clone(), supplied)],
);

// Account 2 supplies enough independent collateral for a large borrow.
let borrower_id = controller.supply(
    attacker,
    0,
    S,
    vec![env, (collateral, sufficient_collateral)],
);

// Push the target market to sustained high utilization.
let borrowed = supplied * 98 / 100;
controller.borrow(
    attacker,
    borrower_id,
    vec![env, (target.clone(), borrowed)],
    Some(attacker),
);

// After the borrow index has grown enough that
// borrowed_scaled * borrow_index / RAY > i128::MAX:
controller.update_indexes(attacker, vec![env, target.clone()]);
// => GenericError::MathOverflow inside accrue_step / scaled_to_original.

// The committed timestamp never advances, so these subsequently revert
// through the same mandatory accrual:
controller.withdraw(attacker, supplier_id, vec![env, (target.clone(), 1)], None);
controller.repay(attacker, borrower_id, vec![env, (target.clone(), 1)]);
controller.liquidate(liquidator, borrower_id, debt_payments, seize_mode);
```

The decisive state transition is the accrual attempted by `pool.update_indexes`; once it reverts, no state is committed and every later mutation repeats the same overflowing calculation. [19](#0-18) [20](#0-19)

### Citations

**File:** common/src/rates/simulate.rs (L51-71)
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

**File:** contracts/pool/src/interest.rs (L20-53)
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
}
```

**File:** contracts/pool/src/ops/repay.rs (L36-59)
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

    cache.credit_cash(net_repay);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-80)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
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

**File:** contracts/pool/src/ops/withdraw.rs (L111-119)
```rust
fn gate_and_debit(env: &Env, cache: &mut Cache, net_transfer: i128, skip_utilization_check: bool) {
    cache.require_reserves(net_transfer);

    if !skip_utilization_check {
        guards::require_utilization_below_max(env, cache);
    }
    guards::require_supply_for_debt(env, cache);
    cache.debit_cash(net_transfer);
}
```

**File:** contracts/pool/src/ops/supply.rs (L19-40)
```rust
pub(crate) fn apply(
    env: &Env,
    entry: &PoolSupplyEntry,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    guards::require_backed_market(env, &cache);

    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
        amount == 0 || minted.raw() > 0,
        GenericError::SupplyRoundsToZeroShares
    );

    position = position.checked_add(env, minted);
    cache.mint_supply(minted);

    cache.credit_cash(amount);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/borrow.rs (L42-50)
```rust
pub(crate) fn accounting(env: &Env, entry: &PoolBorrowEntry) -> BorrowOutcome {
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    mint_debt(env, &mut cache, &mut position, amount);
    cache.debit_cash(amount);

    let snapshot = cache.commit();
    let mutation = cache.position_mutation(position, amount);
```

**File:** contracts/pool/src/ops/borrow.rs (L63-79)
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
}
```
