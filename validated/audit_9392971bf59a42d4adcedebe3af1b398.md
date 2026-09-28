### Title
Missing revenue accumulator initialization freezes protocol revenue claims - (File: contracts/controller/src/markets.rs)

### Summary
The controller constructor configures the owner, position limits, minimum borrow collateral, and app version, but does not initialize `ControllerKey::Accumulator`. [1](#0-0)   
`claim_revenue` therefore rejects every call with `NoAccumulator` before it can invoke the pool’s revenue-claim operation. [2](#0-1) 

### Finding Description
`claim_revenue` is callable by any authorizing caller and iterates through the supplied hub assets. [3](#0-2)   
For each asset, `claim_revenue_for_asset` reads the optional accumulator from instance storage and panics with `OracleError::NoAccumulator` when it is absent. [4](#0-3)   
Because this check occurs before `pool_claim_revenue_call`, the transaction never reaches the pool code that would burn claimable revenue shares and pay out cash. [2](#0-1) [5](#0-4) 

### Impact Explanation
All protocol revenue accrued after deployment remains locked in the pool until governance configures an accumulator. [6](#0-5)   
This temporarily freezes unclaimed yield because neither a permissionless caller nor the revenue beneficiary can move the accrued funds while `ControllerKey::Accumulator` is unset. [7](#0-6) 

### Likelihood Explanation
The vulnerable state is reachable through ordinary deployment ordering: the constructor does not require an accumulator, while the controller can later be unpaused and begin operating without one. [1](#0-0)   
Although `set_accumulator` exists, it is an owner-only configuration action rather than a constructor requirement or protocol invariant. [8](#0-7) 

### Recommendation
Require the accumulator address in the controller constructor and initialize `ControllerKey::Accumulator` atomically with the rest of the controller configuration. [1](#0-0)   
Alternatively, prevent unpausing while `try_get_accumulator` returns `None` so revenue cannot accrue behind an unusable claim path. [7](#0-6) 

### Proof of Concept
1. Deploy the controller with `__constructor(admin)`; the function stores the owner and other defaults but no `Accumulator` value. [1](#0-0) 
2. Configure the pool and markets, unpause the controller, and execute ordinary `supply`, `borrow`, and `update_indexes` calls so protocol revenue shares accrue. [5](#0-4) 
3. Any caller invokes `Controller::claim_revenue(caller, assets)` for an asset containing claimable revenue. [9](#0-8) 
4. `claim_revenue_for_asset` reads no accumulator and panics with `NoAccumulator` before calling the pool. [4](#0-3) 
5. The accrued revenue remains in the pool and cannot be forwarded until governance separately executes `set_accumulator`. [8](#0-7)

### Citations

**File:** contracts/controller/src/governance.rs (L14-32)
```rust
pub(crate) fn init(env: &Env, admin: &Address) {
    ownable::set_owner(env, admin);
    ownable::emit_ownership_transfer_completed(env, admin);

    config::registry::set_position_limits(
        env,
        PositionLimits {
            max_supply_positions: POSITION_LIMIT_MAX,
            max_borrow_positions: POSITION_LIMIT_MAX,
        },
    );

    config::registry::set_min_borrow_collateral_usd(env, DEFAULT_MIN_BORROW_COLLATERAL_USD_WAD);

    env.storage()
        .instance()
        .set(&ControllerKey::AppVersion, &INITIAL_APP_VERSION);

    pausable::pause(env);
```

**File:** contracts/controller/src/markets.rs (L127-135)
```rust
/// Claims and forwards revenue to the accumulator in input order. Returns
/// measured controller receipts; requires caller authorization and no flash loan.
pub(crate) fn claim_revenue(env: &Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128> {
    validation::require_authorized_caller(env, &caller);
    let mut results = Vec::new(env);
    let mut cache = Context::new(env);
    for hub_asset in assets {
        let amount = claim_revenue_for_asset(env, &caller, &hub_asset, &mut cache);
        results.push_back(amount);
```

**File:** contracts/controller/src/markets.rs (L168-184)
```rust
fn claim_revenue_for_asset(
    env: &Env,
    caller: &Address,
    hub_asset: &HubAssetKey,
    cache: &mut Context,
) -> i128 {
    let accumulator = storage::try_get_accumulator(env)
        .unwrap_or_else(|| panic_with_error!(env, OracleError::NoAccumulator));

    let pool_addr = cache.cached_pool_address();

    // Measure custody receipts before forwarding inexact-delivery tokens (INV-ACCT-03).
    let controller = env.current_contract_address();
    let asset = &hub_asset.asset;
    let before = token::Client::new(env, asset).balance(&controller);

    let _ = pool_claim_revenue_call(env, &pool_addr, hub_asset);
```

**File:** contracts/pool/src/ops/revenue.rs (L19-30)
```rust
/// Claims all currently claimable revenue and pays it to the Ownable owner.
/// Emits a market state snapshot in all cases. If nothing is claimable, returns
/// a mutation with `actual_amount` zero and performs no transfer.
pub(crate) fn apply(env: &Env, hub_asset: HubAssetKey) -> PoolAmountMutation {
    let outcome = accounting(env, hub_asset);

    if outcome.mutation.actual_amount != 0 {
        let owner = ownable::get_owner(env)
            .unwrap_or_else(|| panic_with_error!(env, GenericError::OwnerNotSet));
        outcome
            .cache
            .transfer_out(&owner, outcome.mutation.actual_amount);
```

**File:** contracts/pool/src/ops/revenue.rs (L39-47)
```rust
pub(crate) fn accounting(env: &Env, hub_asset: HubAssetKey) -> RevenueOutcome {
    let mut cache = ops::renewed_market(env, &hub_asset);

    let net_transfer = cache.burn_claimable_revenue();

    guards::require_utilization_below_max(env, &cache);
    guards::require_supply_for_debt(env, &cache);
    cache.debit_cash(net_transfer);

```

**File:** contracts/controller/src/storage/protocol.rs (L74-83)
```rust
/// Returns the instance accumulator address, or `None` when unset.
pub(crate) fn try_get_accumulator(env: &Env) -> Option<Address> {
    env.storage().instance().get(&ControllerKey::Accumulator)
}

/// Stores the accumulator address in instance storage.
pub(crate) fn set_accumulator(env: &Env, addr: &Address) {
    env.storage()
        .instance()
        .set(&ControllerKey::Accumulator, addr);
```

**File:** contracts/controller/src/config/registry.rs (L30-34)
```rust
/// Stores the revenue accumulator and emits its address.
pub(crate) fn set_accumulator(env: &Env, addr: Address) {
    storage::set_accumulator(env, &addr);
    UpdateAccumulatorEvent { accumulator: addr }.publish(env);
}
```
