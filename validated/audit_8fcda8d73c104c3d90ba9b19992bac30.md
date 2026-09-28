### Title
Unbounded RAY-scaled balances can overflow accrual and permanently freeze a market - ([File: common/src/rates/index.rs])

### Summary
A sufficiently large market can reach a state where `borrowed × borrow_index` or `supplied × supply_index` no longer fits in `i128`, causing every subsequent accrual to revert with `MathOverflow`. Because all exit, repayment, liquidation, and forced-accrual paths synchronize interest before mutating the market, the overflow permanently blocks access to the market’s funds. [1](#0-0) [2](#0-1) 

### Finding Description
`Controller::supply` and `Controller::borrow` allow an unprivileged account to establish very large scaled supply and debt balances, while the permissionless `Controller::update_indexes` entrypoint forwards a selected `HubAssetKey` to the pool for forced accrual. [3](#0-2) [4](#0-3) 

Pool operations call `synced_market`, which invokes `interest::global_sync`; `global_sync` processes all elapsed time in chunks through `accrue_step`. [5](#0-4) [6](#0-5) 

Inside `accrue_step`, `scaled_to_original` evaluates scaled balances against the current indexes, and `calculate_supplier_rewards` separately evaluates debt at the old and new borrow indexes. [1](#0-0) [7](#0-6) 

`scaled_to_original` delegates to `Ray::mul`, whose underlying `mul_div_half_up` computes `x × y / RAY` and panics with `GenericError::MathOverflow` when the quotient cannot fit in `i128`. [8](#0-7) [9](#0-8) 

The borrow index is capped only after multiplying `old_index` by the next interest factor, so the index cap does not bound the already-stored scaled balance against value overflow. [10](#0-9) 

### Impact Explanation
Once `borrowed × borrow_index / RAY` or `supplied × supply_index / RAY` exceeds `i128::MAX`, any transaction that touches the market fails before it can change balances or commit a later accrual timestamp. [11](#0-10) [12](#0-11) 

The same failure blocks withdrawals, repayments, liquidations, forced index updates, and rate-model replacement because those paths all load an interest-synced market or explicitly accrue before committing state. [2](#0-1) [13](#0-12) 

Consequently, supplier principal and yield, borrower collateral, and any pool cash owed to users can become permanently inaccessible rather than merely temporarily delayed.

### Likelihood Explanation
Reaching the condition requires a very large market balance and enough index growth for the RAY-valued total to exceed the signed `i128` range, so it is not triggerable in an ordinary small market. [14](#0-13) 

However, the state can be produced through normal `supply` and `borrow` calls using assets and collateral controlled by the attacker, and any authorized caller can later trigger the fatal accrual through `update_indexes`. [3](#0-2) [4](#0-3) 

Asset caps and utilization limits reduce exposure only when their configured values keep every possible accrued market value below the `i128` boundary; they do not provide a protocol-level invariant that stored scaled balances remain safe through the configured index ceilings.

### Recommendation
Enforce market-size bounds against the maximum reachable index, not merely the current index, before admitting supply or debt. For example, entry validation should ensure that `scaled_supply × MAX_SUPPLY_INDEX_RAY / RAY` and `scaled_debt × MAX_BORROW_INDEX_RAY / RAY` remain below `i128::MAX` with a safety margin covering intermediate interest calculations. [10](#0-9) [15](#0-14) 

Do not repair this by silently saturating debt or supply valuations during accrual, because that would understate obligations or claims and can transfer losses between users. Existing markets need a migration or governance-controlled exposure reduction path whose caps are calculated from the worst-case index domain.

### Proof of Concept
The following sequence uses one unprivileged caller controlling two accounts and assumes an 18-decimal borrow asset, an accepted collateral asset, caps permissive enough for the positions, and ledger time advanced until the accrued value crosses `i128::MAX`:

```rust
let debt_asset = HubAssetKey { hub_id, asset: big_token };
let collateral_asset = HubAssetKey { hub_id, asset: collateral_token };

let principal: i128 = 1_000_000_000 * 10_i128.pow(18);
let debt: i128 = principal * 98 / 100;

// Fund the target market from attacker-owned account A.
let supplier_id = controller.supply(
    attacker.clone(),
    0,
    spoke_id,
    vec![&env, (debt_asset.clone(), principal)],
);

// Fund attacker-owned account B with sufficient collateral.
let borrower_id = controller.supply(
    attacker.clone(),
    0,
    spoke_id,
    vec![&env, (collateral_asset.clone(), sufficient_collateral)],
);

// Borrow almost all available liquidity.
controller.borrow(
    attacker.clone(),
    borrower_id,
    vec![&env, (debt_asset.clone(), debt)],
    Some(attacker.clone()),
);

// After enough elapsed ledger time, any caller forces accrual.
controller.update_indexes(
    attacker.clone(),
    vec![&env, debt_asset.clone()],
);
```

At the overflow boundary, `update_indexes` reverts while evaluating `borrowed_original` or `new_total_debt`, leaving the previous timestamp and balances unchanged. [1](#0-0) [7](#0-6) 

Subsequent calls equivalent to the following also revert because each pool operation performs `global_sync` before withdrawal or repayment logic runs:

```rust
controller.withdraw(
    attacker.clone(),
    supplier_id,
    vec![&env, (debt_asset.clone(), 0)],
    Some(attacker.clone()),
);

controller.repay(
    attacker.clone(),
    borrower_id,
    vec![&env, (debt_asset.clone(), 1)],
);
```

### Citations

**File:** common/src/rates/simulate.rs (L60-71)
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

**File:** contracts/controller/src/lib.rs (L94-115)
```rust
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

**File:** common/src/rates/index.rs (L80-86)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/pool/src/ops/market.rs (L50-71)
```rust
/// Accrues interest under the old model, commits it, then replaces the interest
/// and flash-loan parameters and validates them against the stored decimals.
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
    events::emit_market_params(env, hub_asset.hub_id, hub_asset.asset, params);
}

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
```
