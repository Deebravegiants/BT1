### Title
Large RAY-denominated balances permanently freeze a market through index-accrual overflow - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary

A sufficiently large market can make `borrowed * borrow_index` or `supplied * supply_index` exceed `i128::MAX` during routine interest accrual. [1](#0-0)  The multiplication path is not protected by the borrow-index ceiling because the raw debt value is calculated before the capped index is produced. [2](#0-1)  Once that bound is crossed, `update_indexes`, withdrawals, repayments, liquidation, and every other market operation that synchronizes the market revert with `MathOverflow`. [3](#0-2) 

### Finding Description

`Controller::update_indexes` is permissionless and forwards caller-selected `HubAssetKey` values to the pool. [4](#0-3)  Pool accrual loads each market and calls `interest::global_sync`, which applies compounding chunks until the market reaches the current ledger timestamp. [5](#0-4) [6](#0-5) 

Each `accrue_step` first converts scaled debt and supply to RAY-denominated values through `scaled_to_original`. [7](#0-6)  `scaled_to_original` performs a direct `Ray::mul`, so a scaled balance multiplied by a sufficiently grown index exceeds the `i128` domain. [8](#0-7)  The configured borrow-index ceiling only limits the resulting index after `old_index.mul(interest_factor)` succeeds; it does not bound the separate scaled-balance products used for utilization and rewards. [9](#0-8) 

The repository already contains a reproduction where an eighteen-decimal market holding one billion whole tokens at 98% utilization grows beyond the raw-value ceiling before `MAX_BORROW_INDEX_RAY` engages. [10](#0-9)  After the failed accrual, both a one-unit withdrawal and a repayment revert with `MATH_OVERFLOW`, demonstrating that the condition is not confined to the keeper entrypoint. [3](#0-2) 

### Impact Explanation

The affected market becomes permanently inoperable because all pool mutating operations load a synchronized cache before applying their action. [11](#0-10)  Consequently, suppliers cannot withdraw, borrowers cannot repay, liquidators cannot repay debt, revenue cannot be processed, and recapitalization or rate-model replacement still encounters the same accrual panic. [12](#0-11) 

This permanently freezes all user funds and unclaimed yield in that `(hub_id, asset)` book while the overflow persists. [13](#0-12)  The pool continues holding the underlying token balance, but no normal entrypoint can move its accounting past the arithmetic failure. [14](#0-13) 

### Likelihood Explanation

Triggering the state requires a very large normalized balance and sustained interest accrual; it is not instant and depends on the market’s configured caps, decimals, utilization, and interest curve permitting the required book size. [15](#0-14)  However, any signed caller can invoke `Controller::update_indexes(caller, assets)` on the affected market once ledger time has advanced enough to cross the boundary. [4](#0-3) 

The supplied regression establishes the condition with one billion whole eighteen-decimal tokens, 98% utilization, and the steep XLM-style rate curve. [16](#0-15)  Because natural accrual drifts utilization upward when debt compounds faster than supply, the attack does not require continuously maintaining exactly 98% utilization after the position is established. [17](#0-16) 

### Recommendation

Bound the product of scaled balances and indexes, not merely the indexes themselves. Use checked or widened multiplication for `borrowed * borrow_index`, `supplied * supply_index`, `borrowed * new_borrow_index`, and `supplied * new_index`; on overflow, clamp the affected index or transition the market into an explicit recoverable halted-accounting state instead of panicking inside every synchronization. [18](#0-17) 

Also derive supply and borrow caps from the maximum safely representable post-accrual RAY value for the configured decimals and worst-case index ceiling, then reject listings or cap changes that can exceed it. [19](#0-18)  Add a regression asserting that an index at `MAX_BORROW_INDEX_RAY` cannot make utilization, rewards, liquidation, repayment, withdrawal, revenue, or recapitalization arithmetic overflow. [20](#0-19) 

### Proof of Concept

The existing test creates `BIG18`, supplies `1_000_000_000 * 10^18` units, supplies collateral from a second account, and borrows 98% of the BIG18 book. [15](#0-14) 

It then advances ledger time in yearly intervals and calls the permissionless `update_indexes` path until the first accrual returns `MathOverflow`. [21](#0-20)  The stored borrow index remains below `MAX_BORROW_INDEX_RAY`, proving the index cap did not prevent the raw-value overflow. [22](#0-21) 

Finally, both `withdraw(account, [(BIG18, 1)])` and `repay(account, [(BIG18, 1)])` fail with `MATH_OVERFLOW`, confirming permanent denial of normal exits and debt reduction after the boundary is reached. [12](#0-11)

### Citations

**File:** common/src/rates/simulate.rs (L60-66)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);
```

**File:** common/src/rates/simulate.rs (L68-78)
```rust
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

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L8-12)
```rust
//! Cells are chosen under that cliff. Utilization is value-based and debt
//! compounds faster than supply, so an untouched market drifts upward: on the
//! XLM curve a book left at 50 percent utilization crosses the optimal point
//! after about ten years and runs away (the reference puts it at x8650 after
//! twenty). Every cell asserts the reference projection stays under the
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L26-33)
```rust
pub fn calculate_scaled_cap(env: &Env, cap: i128, decimals: u32, index: Ray) -> Ray {
    Ray::from(fp_core::mul_div_floor_saturating(
        env,
        Ray::from_asset(env, cap, decimals).raw(),
        RAY,
        index.raw(),
    ))
}
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

**File:** contracts/pool/src/ops/mod.rs (L42-47)
```rust
/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
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
