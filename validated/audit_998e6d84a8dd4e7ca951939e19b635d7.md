### Title
Permanent market freeze from RAY debt-value overflow before borrow-index cap - ([File: contracts/pool/src/interest.rs](contracts/pool/src/interest.rs))

### Summary
An unprivileged user can create a sufficiently large, highly utilized borrow market and eventually make every state-changing operation on that market panic with `MathOverflow` before `MAX_BORROW_INDEX_RAY` can cap accrual. [1](#0-0)  Once the panic condition is reached, `update_indexes`, `withdraw`, and `repay` all fail because each path first invokes `interest::global_sync`. [2](#0-1) [3](#0-2) 

### Finding Description
The pool stores supply and debt as RAY-scaled shares and converts them back to value by `scaled_to_original`, which performs a checked `scaled * index` multiplication. [4](#0-3)  During accrual, `accrue_step` receives the market's scaled `borrowed`, `supplied`, borrow index, and supply index; supplier reward accounting multiplies `borrowed` by both the old and new borrow indexes. [5](#0-4) [6](#0-5)  Although `update_borrow_index` caps the index at `MAX_BORROW_INDEX_RAY`, that cap is applied only after the multiplication produces `new_index`; it does not prevent the subsequent total-debt value calculation from exceeding `i128::MAX`. [7](#0-6) [8](#0-7) 

Every pool operation leg loads a synced market through `synced_market`, which calls `interest::global_sync` before executing the operation. [9](#0-8)  Explicit index synchronization also calls `global_sync` for each requested market. [3](#0-2)  Therefore, once `borrowed * new_borrow_index` exceeds the finite RAY value domain, all controller-reachable operations that touch the affected market—supply, borrow, withdraw, repay, liquidation legs, flash operations, and index updates—fail atomically before their state transition can run. [10](#0-9) [2](#0-1) 

The existing adversarial regression test constructs a large 18-decimal market, supplies a large collateral position, borrows to 98% utilization, advances ledger time, and observes `MathOverflow` while the borrow index remains below `MAX_BORROW_INDEX_RAY`. [11](#0-10)  The same test confirms that subsequent withdrawal and repayment attempts hit the same overflow. [12](#0-11) 

### Impact Explanation
This permanently freezes every user’s funds in the affected market: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot execute repayment legs involving that market, and `update_indexes` cannot recover the market because it performs the same failing accrual. [2](#0-1) [3](#0-2) [12](#0-11)  The resulting state is a market-level denial of service and permanent freezing of funds rather than a transient revert tied to a bad caller input. [13](#0-12) 

### Likelihood Explanation
The condition requires an exceptionally large market and sustained high utilization long enough for debt value to cross the `i128` RAY-value boundary before the index cap is reached. [14](#0-13)  The triggering sequence is nevertheless built from public, permissionless controller actions—`supply` creates collateral positions, `borrow` creates the debt position, and `update_indexes` or any later market operation triggers the fatal accrual. [15](#0-14) [3](#0-2)  The substantial capital and accrual horizon reduce practical likelihood, making the finding Medium rather than High. [16](#0-15) 

### Recommendation
Bound the market’s scaled debt and total RAY-denominated debt value before accrual can overflow, rather than relying only on `MAX_BORROW_INDEX_RAY` after index multiplication. [7](#0-6)  In particular, cap or reject borrow growth when `borrowed` is already near `i128::MAX / MAX_BORROW_INDEX_RAY`, or make reward accounting use a saturating/short-circuiting calculation once the borrow index reaches its maximum. [6](#0-5)  Add an invariant test that every post-overflow-condition public verb either remains executable under the capped index or is rejected before accrual without corrupting market state. [12](#0-11) 

### Proof of Concept
The repository already contains a deterministic reproduction in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. [17](#0-16) 

1. Create a high-decimal market and an ordinary collateral market, then lift both markets’ caps. [18](#0-17) 
2. Supply a very large amount of the debt asset and collateral through `supply`, then borrow approximately 98% of the debt market through `borrow`. [19](#0-18) 
3. Advance ledger time in yearly increments and call `update_indexes` for the debt market until it fails with `MathOverflow`. [20](#0-19) 
4. Observe that the stored borrow index remains below `MAX_BORROW_INDEX_RAY`, proving the index cap did not prevent the debt-value overflow. [21](#0-20) 
5. Attempt `withdraw` or `repay`; both fail with the same `MathOverflow` because each operation first synchronizes the market. [9](#0-8) [12](#0-11)

### Citations

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-356)
```rust
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** contracts/pool/src/interest.rs (L39-53)
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

**File:** contracts/pool/src/lib.rs (L131-179)
```rust
    fn supply(env: Env, entries: Vec<PoolSupplyEntry>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, ops::supply::apply)
    }

    /// Batch-borrows assets and transfers them to `receiver`: accrues
    /// interest, mints scaled debt, debits cash, and enforces max
    /// utilization after each mint. Restricted to the owner; returns one
    /// [`PoolPositionMutation`] per entry.
    #[only_owner]
    fn borrow(
        env: Env,
        receiver: Address,
        entries: Vec<PoolBorrowEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::borrow::apply(env, &receiver, entry)
        })
    }

    /// Burns supply shares and transfers the underlying to `receiver`.
    /// `is_liquidation` skips the max-utilization check and may withhold a
    /// protocol fee. Owner-only; `actual_amount` is gross of that fee.
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
    }

    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
```

**File:** contracts/controller/src/lib.rs (L90-114)
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
```
