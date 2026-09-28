### Title
Unchecked scaled-debt multiplication can permanently freeze a market - ([File: common/src/rates/index.rs])

### Summary

`Controller::update_indexes` is permissionless and forwards attacker-selected `HubAssetKey` values to the pool's accrual path. [1](#0-0) [2](#0-1)  Accrual evaluates the market's scaled debt multiplied by both the old and new borrow indexes; a sufficiently large scaled debt can overflow `i128` even when the borrow-index cap itself has not been reached. [3](#0-2) [4](#0-3) 

Because every affected pool leg performs interest synchronization before mutating state, the panic repeats on later calls and permanently blocks repayment, withdrawal, liquidation, and other operations for that market under the deployed code. [5](#0-4) 

### Finding Description

The controller exposes `supply`, `borrow`, `repay`, `withdraw`, and permissionless `update_indexes` entrypoints. [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) [1](#0-0) 

`Controller::update_indexes` authenticates only the caller, loads the pool address, and invokes pool accrual. [10](#0-9)  The pool loads the committed market and calls `global_sync`, which invokes `accrue_step` with the stored scaled `borrowed`, `supplied`, `borrow_index`, and `supply_index`. [2](#0-1) [3](#0-2) [11](#0-10) 

The borrow-index cap only bounds the index value returned by `update_borrow_index`. [12](#0-11)  The subsequent reward calculation still multiplies the unbounded stored `borrowed` share total by both indexes, so a book whose scaled debt is near the `i128` ceiling can overflow while calculating `new_total_debt` before the index cap protects the operation. [13](#0-12) 

Once `borrowed * new_borrow_index` exceeds `i128::MAX`, `Ray::mul` traps and the transaction rolls back before `last_timestamp` is committed. [14](#0-13) [15](#0-14)  Subsequent calls start from the same stale timestamp and retry the same or an even larger accrual, so the overflow is permanent rather than a one-call rejection. [16](#0-15) [5](#0-4) 

### Impact Explanation

This permanently freezes funds and normal market operation: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot process the debt, and permissionless index updates cannot recover the market. [17](#0-16) [18](#0-17)  Even replacing the interest-rate model normally cannot rescue the book because `replace_rate_model` synchronizes and therefore hits the same overflow before writing safer parameters. [19](#0-18) 

The freeze is isolated to the affected `(hub_id, asset)` book, but every asset already supplied to that book can remain inaccessible absent a contract upgrade or other out-of-band recovery. [20](#0-19) [5](#0-4) 

### Likelihood Explanation

A single unprivileged address can create separate lender and borrower accounts, supply the debt asset from one account, supply collateral to the other, borrow up to the market's configured limits, and maintain solvency until accrual reaches the overflowing product. [21](#0-20) [22](#0-21) 

The attack requires a listed asset whose decimals, supply cap, actual token liquidity, and admitted interest model permit a scaled debt large enough that `scaled_debt * borrow_index` can exceed `i128::MAX`. [23](#0-22) [4](#0-3)  It therefore has substantial capital and market-configuration prerequisites, but the final trigger is a permissionless `update_indexes` call and the resulting denial of service is persistent. [1](#0-0) [5](#0-4) 

### Recommendation

Enforce a share-space ceiling in addition to asset-unit caps: require `borrowed <= i128::MAX / MAX_BORROW_INDEX_RAY` and `supplied <= i128::MAX / MAX_SUPPLY_INDEX_RAY` on market creation and before every mint. [12](#0-11) [5](#0-4) 

Alternatively, perform accrual's debt and supply valuation in a wider type such as `I256` and saturate or clamp the represented value so the index cap can be committed safely, though explicit share-space bounds are the stronger invariant. [24](#0-23) [25](#0-24) 

### Proof of Concept

Let `DEBT` be a listed market whose configured cap admits enough nominal units for `scaled_borrowed * borrow_index / RAY` to exceed `i128::MAX`, and let `COL` be sufficient listed collateral.

```text
lender = supply(
    attacker,
    account_id = 0,
    spoke_id,
    assets = [(DEBT, principal)]
)

borrower = supply(
    attacker,
    account_id = 0,
    spoke_id,
    assets = [(COL, collateral)]
)

borrow(
    attacker,
    account_id = borrower,
    borrows = [(DEBT, borrow_amount)],
    to = None
)
```

The attacker keeps `borrower` solvent, lets interest accrue, then submits:

```text
update_indexes(attacker, assets = [DEBT])
```

Once the accrued `new_borrow_index` makes `borrowed * new_borrow_index` overflow, `update_indexes` reverts during `global_sync` before committing `last_timestamp`. [15](#0-14) [4](#0-3) 

The following calls then repeatedly fail in the same pre-mutation accrual:

```text
repay(attacker, borrower, [(DEBT, 1)])
withdraw(attacker, lender, [(DEBT, 1)], None)
update_indexes(attacker, [DEBT])
```

`repay` and `withdraw` both enter through `load_leg`, which synchronizes the market before resolving shares or cash. [18](#0-17) [17](#0-16) [26](#0-25)

### Citations

**File:** contracts/controller/src/lib.rs (L90-101)
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
```

**File:** contracts/controller/src/lib.rs (L104-114)
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
```

**File:** contracts/controller/src/lib.rs (L117-121)
```rust
    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
    fn withdraw(
        env: Env,
```

**File:** contracts/controller/src/lib.rs (L130-133)
```rust
    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
```

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
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

**File:** contracts/pool/src/ops/market.rs (L68-71)
```rust
    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
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

**File:** contracts/pool/src/interest.rs (L40-44)
```rust
    let step = accrue_step(
        env,
        cache.params(),
        cache.borrowed(),
        cache.supplied(),
```

**File:** contracts/pool/src/interest.rs (L45-48)
```rust
        cache.borrow_index(),
        cache.supply_index(),
        delta_ms,
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

**File:** contracts/pool/src/ops/mod.rs (L42-46)
```rust
/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
```

**File:** contracts/controller/src/markets.rs (L118-124)
```rust
/// Accrues indexes for each hub asset. Requires caller authorization and no flash loan.
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
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

**File:** contracts/pool/src/cache/mod.rs (L49-70)
```rust
    pub(crate) fn load(env: &Env, hub_asset: &HubAssetKey) -> Self {
        let raw_params = storage::read_params(env, hub_asset);
        let raw_state = storage::read_state(env, hub_asset);
        storage::renew_market(env, hub_asset);

        let state = PoolState::from(&raw_state);
        let params = MarketParams::from(&raw_params);
        let time = time::now_ms(env);

        Self {
            env: env.clone(),
            hub_asset: hub_asset.clone(),
            params,
            last_timestamp: state.last_timestamp,
            current_timestamp: time,
            supplied: state.supplied,
            borrowed: state.borrowed,
            revenue: state.revenue,
            borrow_index: state.borrow_index,
            supply_index: state.supply_index,
            cash: state.cash,
        }
```

**File:** contracts/pool/src/cache/mod.rs (L133-141)
```rust
    /// Milliseconds between last accrual and the stamped current time.
    pub(crate) fn elapsed_ms(&self) -> u64 {
        self.current_timestamp.saturating_sub(self.last_timestamp)
    }

    /// `true` when interest should be compounded before further mutations.
    pub(crate) fn needs_accrual(&self) -> bool {
        self.elapsed_ms() > 0
    }
```

**File:** contracts/pool/src/ops/withdraw.rs (L62-65)
```rust
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
```

**File:** contracts/pool/src/ops/repay.rs (L40-44)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
```

**File:** common/src/rates/compound.rs (L36-42)
```rust
    let x = Ray::from({
        let r = I256::from_i128(env, rate.raw());
        let d = I256::from_i128(env, delta_ms as i128);
        r.mul(&d)
            .to_i128()
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
    });
```
