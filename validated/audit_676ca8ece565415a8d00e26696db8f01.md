### Title
Arithmetic overflow during mandatory interest accrual freezes all market funds - (File: common/src/rates/simulate.rs)

### Summary
A large, high-utilization market can reach a state where `borrowed * borrow_index` or `supplied * supply_index` exceeds the `i128` RAY-value domain before the configured index ceiling is reached, after which every market operation that accrues interest reverts and the market cannot advance its timestamp. [1](#0-0) [2](#0-1) 

### Finding Description
`Controller::update_indexes` is callable by any authenticated address and accepts arbitrary listed `HubAssetKey` values. [3](#0-2)  The controller forwards those assets to `pool_update_indexes`, and the pool runs `interest::global_sync` before committing market state. [4](#0-3) [5](#0-4) 

Each accrual chunk computes aggregate debt and supply by calling `scaled_to_original`, which multiplies the scaled share amount by its index. [1](#0-0) [6](#0-5)  The global index bound is independent of the amount of outstanding scaled shares, so a sufficiently large market reaches the aggregate-value overflow boundary before the index reaches its maximum. [7](#0-6) [8](#0-7) 

If `scaled_to_original` panics inside `accrue_step`, `mark_accrued` is never reached, so `last_timestamp` remains old and every later accrual starts from the same stale checkpoint with an even larger elapsed interval. [9](#0-8)  Both repayment and withdrawal load a market leg only after interest accrual, so the same panic blocks exits and debt reduction rather than merely blocking keeper maintenance. [10](#0-9) [11](#0-10) 

An unprivileged attacker can create one account that supplies the volatile market asset and another account that supplies collateral and borrows that asset through `Controller::supply` and `Controller::borrow`, provided the existing listed caps, oracle values, utilization limits, and solvency gates permit the required size. [12](#0-11)  Once enough ledger time has elapsed, the attacker calls `Controller::update_indexes(caller, vec![debt_asset])`; the transaction reverts inside aggregate-value scaling, and the market enters a permanently failing accrual state absent privileged code intervention. [3](#0-2) [13](#0-12) [2](#0-1) 

### Impact Explanation
This permanently freezes the affected market's pool funds for ordinary users: suppliers cannot withdraw, borrowers cannot repay or be cleanly processed, and liquidations that must load the same market also fail at mandatory accrual. [11](#0-10) [10](#0-9) [9](#0-8)  The loss is not limited to the attacker's position because `borrowed` and `supplied` are market-wide aggregates, so one oversized market state can freeze every user's claims in that asset. [1](#0-0) 

### Likelihood Explanation
The attack requires an existing market whose caps and risk parameters admit enough aggregate value for `scaled_amount * index / RAY` to leave the `i128` domain, plus sustained borrowing at a positive interest rate. [12](#0-11) [6](#0-5) [14](#0-13)  It is therefore not reachable in every deployment, but all prerequisite actions use normal permissionless supply, borrow, and index-update paths when such a market configuration exists. [15](#0-14) [3](#0-2) 

### Recommendation
Compute aggregate debt and supply through a checked widened type during accrual and enforce a market-size-dependent index ceiling such as `min(MAX_BORROW_INDEX_RAY, i128::MAX / borrowed)` and `min(MAX_SUPPLY_INDEX_RAY, i128::MAX / supplied)` before performing `scaled_to_original`. [16](#0-15) [6](#0-5)  If the ceiling is reached, clamp the index and still mark accrual complete so repayments and withdrawals remain executable, while separately enforcing entry caps that prevent admitted supply and debt from reaching the arithmetic domain boundary. [2](#0-1) [17](#0-16) 

### Proof of Concept
1. Attacker-controlled lender account calls `Controller::supply(attacker_lender, 0, spoke_id, vec![(debt_asset, N)])`, where `N` is within the listed supply cap but large enough that market-wide scaled supply is near the representability boundary. [18](#0-17) 
2. Attacker-controlled borrower account calls `Controller::supply(attacker_borrower, 0, spoke_id, vec![(collateral_asset, C)])` with enough listed collateral to satisfy the health-factor and minimum-collateral checks. [18](#0-17) 
3. The borrower calls `Controller::borrow(attacker_borrower, borrower_account_id, vec![(debt_asset, D)], None)`, selecting the largest `D` admitted by utilization and solvency. [19](#0-18) 
4. After interest-bearing time passes, any address calls `Controller::update_indexes(attacker, vec![debt_asset])`; `accrue_step` evaluates `borrowed * borrow_index`, overflows, and rolls back before `mark_accrued` can update `last_timestamp`. [3](#0-2) [13](#0-12) [2](#0-1) 
5. Subsequent `repay` or `withdraw` calls repeat the same failing accrual before their share burns and transfers, leaving the market's token funds inaccessible. [10](#0-9) [11](#0-10)

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

**File:** contracts/pool/src/ops/market.rs (L35-43)
```rust
        &PoolStateRaw {
            supplied: 0,
            borrowed: 0,
            revenue: 0,
            borrow_index: RAY,
            supply_index: RAY,
            last_timestamp: time::now_ms(env),
            cash: 0,
        },
```

**File:** contracts/pool/src/ops/market.rs (L65-71)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L18-32)
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
```

**File:** contracts/pool/src/ops/repay.rs (L22-31)
```rust
/// Accrues interest, burns the position's debt shares, credits the net repay to cash,
/// commits the market state, and transfers any overpayment back to the payer.
/// The returned mutation's `actual_amount` is the net repay, excluding overpayment.
pub(crate) fn apply(
    env: &Env,
    payer: &Address,
    action: &PoolAction,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let outcome = accounting(env, action);

```

**File:** contracts/pool/src/ops/withdraw.rs (L25-36)
```rust
/// Accrues interest, burns supply shares, debits cash, and transfers the net
/// proceeds to `receiver`.
///
/// Mutation `actual_amount` is the **gross** withdrawal; `net_transfer` is what
/// leaves the pool after any liquidation fee.
pub(crate) fn apply(
    env: &Env,
    receiver: &Address,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let outcome = accounting(env, is_liquidation, entry);
```
