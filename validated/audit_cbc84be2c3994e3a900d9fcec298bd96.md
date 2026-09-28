### Title
RAY-scaled market value overflows before the index cap, permanently freezing the market - (File: common/src/rates/simulate.rs)

### Summary
`accrue_step` computes aggregate borrowed and supplied values with fallible `i128` fixed-point multiplication before applying the borrow-index ceiling. On a sufficiently large, highly utilized market, the aggregate value crosses `i128::MAX` while the stored index remains below `MAX_BORROW_INDEX_RAY`, causing every operation that first runs `global_sync` to revert with `MathOverflow`.

### Finding Description
`accrue_step` first unscales `borrowed` and `supplied` through `scaled_to_original`, which is implemented as `scaled.mul(index)`. [1](#0-0) [2](#0-1)  `Ray::mul` delegates to checked `mul_div_half_up`, so a representable index combined with a sufficiently large scaled balance produces `GenericError::MathOverflow` instead of a bounded accrual result. [3](#0-2) 

The nominal borrow-index ceiling is applied only when updating the index, and does not bound the aggregate `borrowed * index` or `supplied * index` values used earlier and later in the accrual calculation. [4](#0-3) [5](#0-4)  Consequently, the protocol can reach a state where `borrow_index < MAX_BORROW_INDEX_RAY`, yet no further accrual step can complete. [6](#0-5) 

The public `Controller::update_indexes(caller, assets)` path requires only the caller's authorization and forwards the selected `HubAssetKey` list to `pool.update_indexes`. [7](#0-6)  The pool then runs `interest::global_sync` for each requested market. [8](#0-7)  Other market verbs use the same synchronization step through `ops::load_leg`, including withdrawal and repayment. [9](#0-8) [10](#0-9) [11](#0-10) 

### Impact Explanation
Once the aggregate RAY value exceeds the `i128` domain, all state transitions that accrue first revert, preventing suppliers from withdrawing, borrowers from repaying, and liquidators or cleanup paths from operating on the affected market. [12](#0-11) [13](#0-12)  This constitutes permanent freezing of user funds under the deployed accounting implementation, even though the configured static index ceiling was never reached. [6](#0-5) 

### Likelihood Explanation
The condition requires a very large scaled balance, sustained high utilization, and enough elapsed time for the index to grow until `scaled * index / RAY` exceeds `i128::MAX`. The in-repository reproduction uses an 18-decimal market with one billion whole tokens supplied, 98% utilization, lifted caps, disabled maximum utilization, and yearly calls to `update_indexes`. [14](#0-13)  These requirements make the issue less likely than an ordinary liquidation or rounding bug, but the triggering actions—supplying, borrowing, and calling the caller-authenticated `update_indexes`—are reachable by unprivileged users once such a market configuration exists. [7](#0-6) 

### Recommendation
Bound indexes by the market's scaled balance, not only by the static `MAX_*_INDEX_RAY` constants. For each accrual step, compute a safe dynamic ceiling such that `scaled * index / RAY <= i128::MAX`, using widened arithmetic for the ceiling calculation itself, and clamp both borrow and supply index growth before calling `scaled_to_original`, `calculate_supplier_rewards`, or `update_supply_index`. Alternatively, refactor aggregate-value calculations to use a wider representation and only convert position-sized results back to `i128` after proving they fit; silently saturating aggregate value is not safe because it would corrupt utilization and interest accounting. [15](#0-14) [16](#0-15) 

### Proof of Concept
The repository already contains a deterministic regression-style test:

1. Create an 18-decimal market using `xlm_curve`, a collateral market, lifted caps, and disabled maximum utilization.
2. Supply `1_000_000_000 * 10^18` base units of the debt asset and enough collateral to borrow `98%` of it.
3. Advance ledger time in one-year intervals and call `update_indexes` for the market's `HubAssetKey`.
4. Within the asserted bound, `update_indexes` fails with `MathOverflow` while the stored borrow index remains below `MAX_BORROW_INDEX_RAY`.
5. Subsequent calls to `withdraw` for one base unit and `repay` for one whole token fail with the same `MathOverflow`, demonstrating that the market is frozen. [17](#0-16)

### Citations

**File:** common/src/rates/simulate.rs (L60-80)
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
    let supplier_shortfall = supply_index_reward_shortfall(
        env,
        supplied,
        supply_index,
        new_supply_index,
        supplier_rewards,
    );

    let protocol_reward = protocol_fee.checked_add(env, supplier_shortfall);
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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L73-88)
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

    (supplier_rewards, protocol_fee)
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-320)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-356)
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
