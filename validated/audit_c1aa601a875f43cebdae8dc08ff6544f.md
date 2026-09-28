### Title
Unbounded scaled-debt valuation can permanently freeze an entire market before the borrow-index cap - (File: `common/src/rates/index.rs`)

### Summary
The interest-accrual path multiplies total scaled debt by the next borrow index without enforcing that the resulting RAY-denominated debt value fits in `i128`. A sufficiently large market at sustained positive utilization can therefore reach a state where every accrual reverts with `MathOverflow`, even though the configured `MAX_BORROW_INDEX_RAY` has not been reached. Because all user and liquidation paths accrue before mutating the market, this permanently blocks repayment, withdrawal, liquidation, bad-debt cleanup, recapitalization, and parameter changes. [1](#0-0) 

### Finding Description
`accrue_step` first converts `borrowed * borrow_index` and `supplied * supply_index` to compute utilization, then calculates a new borrow index and calls `calculate_supplier_rewards`. [2](#0-1)  `calculate_supplier_rewards` multiplies the scaled debt by both the old and new indexes through `Ray::mul`, which panics with `MathOverflow` if the resulting RAY value does not fit `i128`. [3](#0-2)  The configured index ceiling only caps `new_borrow_index`; it does not cap the product `borrowed * new_borrow_index`, so an oversized book can cross the representable debt-value ceiling before the index ceiling engages. [4](#0-3) 

Every pool mutation that touches an existing market reaches `synced_market`, which calls `interest::global_sync` before the operation-specific accounting. [5](#0-4)  `global_sync` invokes `accrue_step` for each elapsed-time chunk, so once the multiplication overflows there is no pool-level path that can advance or bypass accrual. [6](#0-5)  `update_params` also accrues under the old model before replacing it, and `recapitalize`, repayment, withdrawal, liquidation seizure, and revenue processing all load the same synced market path. [7](#0-6) 

An unprivileged user can create the required book through the public `supply` and `borrow` controller entrypoints, subject to the market's configured caps, collateral availability, and utilization rules. [8](#0-7)  After enough time passes, anyone can trigger the state transition through `controller::update_indexes`, which forwards to the pool's owner-gated `update_indexes` and invokes `ops::market::accrue` for each selected market. [9](#0-8) [10](#0-9) 

### Impact Explanation
Once `borrowed * new_borrow_index` or `borrowed * old_borrow_index` exceeds `i128::MAX`, accrual aborts before state is committed. The market then cannot repay debt, withdraw supplied funds, liquidate unhealthy accounts, socialize bad debt, recapitalize, or change its rate model, permanently freezing supplier principal and outstanding debt in that market. [5](#0-4) [11](#0-10) 

The existing harness reproduces this permanent freeze: after several years of high utilization on an oversized 18-decimal market, `update_indexes` fails with `MathOverflow`, and subsequent `withdraw` and `repay` calls fail for the same reason while `borrow_index` remains below `MAX_BORROW_INDEX_RAY`. [12](#0-11) 

### Likelihood Explanation
The attack requires a very large market and sustained utilization, so it is not triggerable at ordinary balances or solely through a low-cost transaction. However, it does not require privileged access after deployment: an attacker can use ordinary `supply` and `borrow` calls to build exposure within the admitted cap domain, then permissionless `update_indexes` or any subsequent user operation triggers the overflow. The repository's own boundary documentation acknowledges that caps and bounded indexes do not guarantee accrued market totals remain representable. [13](#0-12) 

### Recommendation
Enforce a market-size bound against the worst-case index product before admitting scaled supply or debt, rather than relying only on token-unit caps. For example, reject `borrow` and `supply` when `scaled_amount` exceeds the amount that remains representable at the configured index ceiling and relevant decimal scaling. Additionally, make accrual clamp `new_borrow_index` at `floor(i128::MAX / borrowed)` instead of allowing `calculate_supplier_rewards` to panic; apply the equivalent representability check to `supplied * supply_index`. This preserves an operable market when the arithmetic ceiling is reached instead of bricking it. [14](#0-13) [3](#0-2) 

### Proof of Concept
1. Create or select an 18-decimal market whose caps admit approximately `10^27` base units, equivalent to one billion whole tokens.
2. Call `controller::supply(caller=attacker, account_id=0, spoke_id=S, assets=[(debt_hub_asset, 1_000_000_000 * 10^18)])`.
3. Supply sufficient collateral in another listed market through `controller::supply`, then call `controller::borrow(caller=attacker, account_id=A, borrows=[(debt_hub_asset, 980_000_000 * 10^18)], to=None)`.
4. Leave the position at sustained high utilization until the next index makes `borrowed * borrow_index` exceed `i128::MAX`.
5. Call `controller::update_indexes(caller=anyone, hub_assets=[debt_hub_asset])`.
6. The call reaches `pool::update_indexes -> ops::market::accrue -> global_sync -> accrue_step -> calculate_supplier_rewards` and reverts in `borrowed.mul(new_borrow_index)` with `MathOverflow`.
7. Repeat `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `recapitalize`, and `update_indexes`; each path accrues first and hits the same overflow before any recovery logic can execute. [15](#0-14)

### Citations

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

**File:** common/src/rates/simulate.rs (L51-69)
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

**File:** contracts/pool/src/interest.rs (L20-52)
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
}

/// Applies one compound step of `delta_ms` to indexes and protocol revenue.
///
/// The arithmetic lives in [`accrue_step`], shared with the read-only
/// `simulate_update_indexes` so the view and the mutator cannot drift.
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

**File:** contracts/controller/src/external/pool.rs (L109-116)
```rust
/// Accrues and persists market indexes through the current ledger time.
pub(crate) fn pool_update_indexes_call(
    env: &Env,
    pool_addr: &Address,
    hub_assets: &Vec<HubAssetKey>,
) {
    LiquidityPoolClient::new(env, pool_addr).update_indexes(hub_assets)
}
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

**File:** docs/reference/formulas.md (L432-437)
```markdown
The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```
