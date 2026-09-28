### Title
RAY-scaled market value can overflow before the index cap and permanently freeze a market - ([File: common/src/rates/simulate.rs])

### Summary
Pool mutations synchronize interest before changing state, and synchronization materializes RAY-scaled supply and debt through `scaled_to_original`. [1](#0-0) [2](#0-1)  A sufficiently large admitted book can therefore exceed the `i128` value domain through index growth even though `update_borrow_index` still clamps the index itself. [3](#0-2) 

### Finding Description
`accrue_step` first converts scaled borrow and supply balances into their RAY asset values, then compounds the borrow index and calculates new total debt. [4](#0-3)  The old and new debt calculations are `Ray` multiplications, while the underlying fixed-point arithmetic rejects unrepresentable `i128` results with `MathOverflow`. [5](#0-4) [6](#0-5) 

The borrow index cap is applied only after multiplying the previous index by the interest factor, and it does not bound `borrowed * index / RAY`. [3](#0-2)  Consequently, a market can remain below `MAX_BORROW_INDEX_RAY` while its scaled debt value has crossed the arithmetic limit needed for the next accrual step. [5](#0-4) 

`Controller::supply`, `Controller::borrow`, and `Controller::repay` are reachable by ordinary users or delegates and ultimately call the corresponding pool operations. [7](#0-6) [8](#0-7)  Every pool leg that uses the shared market helpers accrues before executing, so once the next accrual cannot be represented, repayments, withdrawals, liquidations, recapitalization, and `update_indexes` all revert before any recovery action can commit. [1](#0-0) [9](#0-8) 

### Impact Explanation
This permanently freezes all funds in the affected market and prevents debt repayment or liquidation, because time cannot move backward and every recovery path performs accrual first. [1](#0-0)  Even `update_params` cannot reduce the rate to rescue the market because it accrues and commits under the old model before replacing it. [10](#0-9) 

### Likelihood Explanation
Triggering the condition requires a market whose configured caps and utilization admit a scaled balance near the `i128` RAY domain and enough index growth to push its value over the limit. [11](#0-10)  This is economically demanding, but it requires only ordinary unprivileged supply and borrow transactions, no privileged call, malformed token, or external dependency. [7](#0-6) 

### Recommendation
Derive supply and borrow caps from the maximum index-adjusted value, not merely from whether the original token amount fits the RAY domain. [12](#0-11)  Alternatively, represent intermediate market totals with a wider integer type or apply explicit saturation/index clamping before `scaled_to_original` and `calculate_supplier_rewards` can revert. [4](#0-3) [5](#0-4) 

### Proof of Concept
1. On a market whose caps and `max_utilization` permit the position, call:

```rust
supply(caller, 0, spoke_id, vec![(debt_key, supply_cap_amount)]);
supply(caller, account_id, spoke_id, vec![(collateral_key, required_collateral)]);
borrow(caller, account_id, vec![(debt_key, near_supply_cap_amount)], Some(caller));
```

These calls use the public controller supply and borrow entrypoints. [7](#0-6) 

2. Let interest accrue until `borrowed_scaled * borrow_index / RAY` is just below `i128::MAX`; at that point the next nonzero index increase makes `new_total_debt` unrepresentable. [5](#0-4) 

3. Call `update_indexes(vec![debt_key])`; `pool_update_indexes_call` invokes the pool accrual entrypoint, which calls `global_sync` and reverts inside the accrual calculation. [13](#0-12) [9](#0-8) 

4. Subsequent `withdraw`, `repay`, liquidation seizure, or recapitalization attempts hit the same pre-mutation accrual and cannot rescue the market. [1](#0-0)

### Citations

**File:** contracts/pool/src/ops/mod.rs (L29-33)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
```

**File:** common/src/rates/simulate.rs (L60-69)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);
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

**File:** common/src/math/fp_core.rs (L145-158)
```rust
/// Computes `floor(x * y / d)`, rounding toward negative infinity for a negative quotient.
/// Panics with `GenericError::DivisionByZero` if `d == 0`, or with
/// `GenericError::MathOverflow` if the result does not fit in `i128`.
pub fn mul_div_floor(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    require_nonzero_divisor(env, d);
    if let Some(quotient) = x
        .checked_mul(y)
        .and_then(|product| div_floor_i128(product, d))
    {
        return quotient;
    }
    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    let nonneg = quotient_is_nonnegative(x, y, d);
    to_i128(env, &div_floor_i256(env, &x256.mul(&y256), &d256, nonneg))
```

**File:** contracts/controller/src/lib.rs (L94-114)
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
```

**File:** contracts/controller/src/lib.rs (L130-134)
```rust
    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
    }
```

**File:** contracts/pool/src/ops/market.rs (L50-56)
```rust
/// Accrues interest under the old model, commits it, then replaces the interest
/// and flash-loan parameters and validates them against the stored decimals.
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
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

**File:** common/src/validation.rs (L41-55)
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
```

**File:** contracts/controller/src/external/pool.rs (L109-115)
```rust
/// Accrues and persists market indexes through the current ledger time.
pub(crate) fn pool_update_indexes_call(
    env: &Env,
    pool_addr: &Address,
    hub_assets: &Vec<HubAssetKey>,
) {
    LiquidityPoolClient::new(env, pool_addr).update_indexes(hub_assets)
```
