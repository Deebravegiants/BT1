### Title
Unchecked RAY share-index multiplication permanently freezes a saturated debt market - (File: common/src/rates/scaling.rs)

### Summary
`Controller::update_indexes(caller, assets)` is a permissionless, caller-authorized path that forwards the selected markets to the pool. [1](#0-0) [2](#0-1)  Each pool mutation first loads an interest-synced market cache, and `global_sync` performs every elapsed-time accrual before the requested operation. [3](#0-2) [4](#0-3)  The accrual converts scaled debt and supply to value with `scaled.mul(index)` before applying the index ceiling, and the fixed-point multiplication traps with `MathOverflow` when the result exceeds `i128`. [5](#0-4) [6](#0-5) [7](#0-6) 

### Finding Description
`accrue_step` evaluates `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` before calculating utilization or updating the borrow index. [8](#0-7)  `scaled_to_original` performs an unchecked-from-the-caller-perspective `scaled * index` fixed-point multiplication, whose result must fit in `i128`. [6](#0-5) [9](#0-8)  Although `update_borrow_index` clamps the index to `MAX_BORROW_INDEX_RAY`, that clamp occurs only after the vulnerable product has already been evaluated during the next accrual, and the configured ceiling is far above the point where a sufficiently large scaled position can overflow. [10](#0-9) [11](#0-10) 

Once `borrowed * borrow_index` or `supplied * supply_index` exceeds `i128::MAX`, the panic occurs inside `accrue_step`, before `cache.mark_accrued()` is reached. [12](#0-11) [5](#0-4)  Pool `supply`, `borrow`, `withdraw`, `repay`, and explicit `update_indexes` all route through the synced-market path, so they repeat the same trap before performing their operation. [13](#0-12) [14](#0-13) [15](#0-14) [16](#0-15) [17](#0-16) 

### Impact Explanation
All supplier funds and collectible debt in the affected market become inaccessible because deposits, withdrawals, repayments, liquidations, bad-debt settlement, revenue claims, and index refresh require the same accrual to complete first. [18](#0-17) [3](#0-2)  Because `last_timestamp` is only marked after all accrual chunks finish, the overflow leaves the stale accrual state in place and causes every later operation to fail identically. [4](#0-3)  This is a permanent freezing of user funds and protocol receivables absent a code change or another privileged recovery mechanism. [3](#0-2) [12](#0-11) 

### Likelihood Explanation
An unprivileged account can create the required state through ordinary `supply` and `borrow` calls, then drive accrual through `update_indexes(caller, assets)`, which only authorizes the supplied caller and assigns no privileged role. [1](#0-0) [19](#0-18)  The attack requires a very large outstanding scaled position and enough index growth for the product to exceed the `i128` domain, so market caps, token supply, collateral requirements, utilization, and prior accrual history constrain feasibility. [6](#0-5) [9](#0-8)  These preconditions make the issue materially less practical than a small crafted transaction, but once the state exists the denial is deterministic and affects every user of that market. [12](#0-11) [3](#0-2) 

### Recommendation
Do not materialize `scaled * index` in `i128` during accrual or utilization checks: carry the products as `I256`, compute utilization from a rational comparison, or maintain explicit market-wide bounds such as `scaled <= i128::MAX / index` before permitting position growth. [20](#0-19) [21](#0-20)  Add a checked pre-accrual domain guard that produces a recoverable market state rather than repeatedly trapping in `global_sync`, and enforce the bound in `supply`, `borrow`, strategy debt creation, and index accrual. [3](#0-2) [22](#0-21) 

### Proof of Concept
1. In a spoke where the debt market is borrowable, call `supply(caller, account_id, spoke_id, payments)` with enough collateral to support a very large position. [13](#0-12) 
2. Call `borrow(caller, account_id, payments, recipient = None)` for a large amount of the selected debt asset, leaving a large nonzero `borrowed` scaled-share total. [14](#0-13) 
3. Repeatedly invoke `update_indexes(caller, [hub_asset])`, or allow another user’s market operation to perform accrual, until `borrowed * borrow_index` exceeds `i128::MAX`. [1](#0-0) [8](#0-7) [9](#0-8) 
4. Submit `repay(caller, account_id, payments)`, `withdraw(caller, account_id, payments, recipient = None)`, a liquidation, bad-debt cleanup, or another `update_indexes` call for that market. [23](#0-22) [17](#0-16) 
5. Each call reaches `synced_market`, enters `global_sync`, and traps in `scaled_to_original` before `mark_accrued`, so the same failure repeats indefinitely. [3](#0-2) [4](#0-3) [6](#0-5)

### Citations

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
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

**File:** contracts/pool/src/ops/mod.rs (L1-5)
```rust
//! Market mutation operations invoked from the pool's public interface.
//!
//! Each submodule implements one logical action (supply, borrow, …). Shared
//! helpers here load an interest-synced [`Cache`], run multi-leg batches, and
//! emit market state events after each batch.
```

**File:** contracts/pool/src/ops/mod.rs (L29-33)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
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

**File:** contracts/pool/src/interest.rs (L39-52)
```rust
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
```

**File:** common/src/rates/simulate.rs (L60-67)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp_core.rs (L14-20)
```rust
/// Widens `x`, `y`, and `d` to `I256` for overflow-safe intermediate arithmetic.
fn to_i256_operands(env: &Env, x: i128, y: i128, d: i128) -> (I256, I256, I256) {
    (
        I256::from_i128(env, x),
        I256::from_i128(env, y),
        I256::from_i128(env, d),
    )
```

**File:** common/src/math/fp_core.rs (L108-118)
```rust
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

**File:** common/src/math/fp_core.rs (L131-143)
```rust
    if let Some(biased) = x
        .checked_mul(y)
        .and_then(|product| product.checked_add(half))
    {
        return Some(biased / d);
    }

    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    x256.mul(&y256)
        .add(&I256::from_i128(env, half))
        .div(&d256)
        .to_i128()
}
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

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** contracts/pool/src/lib.rs (L128-132)
```rust
    /// Accrues, mints scaled supply shares and credits cash per entry. The
    /// controller transfers the tokens in before this call. Owner-only.
    #[only_owner]
    fn supply(env: Env, entries: Vec<PoolSupplyEntry>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, ops::supply::apply)
```

**File:** contracts/pool/src/lib.rs (L139-145)
```rust
    #[only_owner]
    fn borrow(
        env: Env,
        receiver: Address,
        entries: Vec<PoolBorrowEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
```

**File:** contracts/pool/src/lib.rs (L153-171)
```rust
    #[only_owner]
    fn withdraw(
        env: Env,
        receiver: Address,
        is_liquidation: bool,
        entries: Vec<PoolWithdrawEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::withdraw::apply(env, &receiver, is_liquidation, entry)
        })
    }

    /// Burns scaled debt up to the repay amount, credits cash with the net
    /// repay and refunds overpayment to `payer`. Owner-only.
    #[only_owner]
    fn repay(env: Env, payer: Address, actions: Vec<PoolAction>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, actions, |env, action| {
            ops::repay::apply(env, &payer, action)
        })
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
