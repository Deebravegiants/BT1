### Title
Unbounded RAY-value accrual permanently freezes an oversized market - (File: contracts/pool/src/interest.rs)

### Summary
An attacker can place a market in a state where the next accrual overflows `i128` before `MAX_BORROW_INDEX_RAY` caps index growth. [1](#0-0)  Because every market operation loads the market and calls `interest::global_sync`, the overflow repeats for maintenance, repayment, withdrawal, and liquidation paths. [2](#0-1)  The result is a permanently unusable market containing user funds. [3](#0-2) 

### Finding Description
`Controller::update_indexes` is permissionless and forwards the selected markets to `pool_update_indexes_call`. [4](#0-3)  The pool synchronization loop processes elapsed time in bounded chunks and calls `accrue_step` for each chunk. [5](#0-4)  That accrual converts scaled balances using fixed-point arithmetic; for a sufficiently large supplied/borrowed book, the RAY value can exceed `i128::MAX` while the stored borrow index remains below its configured ceiling. [6](#0-5) 

Repay and withdraw both call `ops::load_leg`, which loads and synchronizes the market before processing the requested action. [7](#0-6) [8](#0-7)  Once the overflow boundary is crossed, even a minimal repayment or withdrawal aborts with `MathOverflow`, so neither borrowers nor suppliers can reduce the balances that caused the failure. [9](#0-8) 

### Impact Explanation
All funds represented by the affected market can be frozen permanently. [1](#0-0)  Suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot execute a cleanup path that first synchronizes the same book. [10](#0-9)  The failure is especially harmful because the index ceiling does not prevent it: the market hits the finite RAY-value domain before `MAX_BORROW_INDEX_RAY` is reached. [11](#0-10) 

### Likelihood Explanation
Triggering the condition requires an exceptionally large market, sufficient token liquidity, sustained high utilization, and configuration that admits the required balances. [12](#0-11)  The required operations themselves are unprivileged: one address can own separate accounts that supply the debt asset, supply collateral, borrow the debt asset, and then call `update_indexes`. [4](#0-3)  After crossing the boundary, the attacker cannot cheaply reverse the state either, because the same overflow blocks repayment. [9](#0-8) 

### Recommendation
Add a pre-accrual capacity check that computes the maximum representable scaled balance or RAY value before mutating indexes, and reject new supply/borrow growth that could cross that boundary. [13](#0-12)  Accrual should also clamp safely at an explicit protocol terminal state rather than panic, allowing at minimum debt repayment and collateral liquidation to proceed. [2](#0-1) 

### Proof of Concept
1. Attacker-owned account A calls `supply(caller=A, account_id=0, spoke_id=S, assets=[(BIG, principal)])` with approximately `1_000_000_000 * 10^18` base units. [14](#0-13) 
2. Attacker-owned account B supplies enough collateral and calls `borrow(caller=A, account_id=B, borrows=[(BIG, principal * 98 / 100)])`. [15](#0-14) 
3. The attacker repeatedly calls `update_indexes(caller=A, assets=[BIG])` as ledger time advances until `accrue_step` returns `MathOverflow`; the stored borrow index is still below `MAX_BORROW_INDEX_RAY`. [16](#0-15) 
4. A subsequent `withdraw` for even one base unit and a `repay` both revert with `MathOverflow` because they synchronize the same market before mutating it. [10](#0-9) [9](#0-8)

### Citations

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-320)
```rust
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L342-356)
```rust
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

**File:** contracts/pool/src/ops/repay.rs (L40-45)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
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
