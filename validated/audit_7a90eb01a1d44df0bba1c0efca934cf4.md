### Title
Permanent market freeze from overflowing debt valuation during permissionless accrual - (File: common/src/rates/simulate.rs)

### Summary
An authenticated but otherwise unprivileged caller can invoke `Controller::update_indexes`, which forwards the selected markets to the pool without additional authorization. [1](#0-0) [2](#0-1) 

The pool accrues the entire elapsed interval before committing the market state, so any arithmetic panic prevents the market from advancing to a usable timestamp. [3](#0-2) [4](#0-3) 

For a sufficiently large admitted debt, `accrue_step` can overflow `i128` while calculating the market’s debt value before the static borrow-index ceiling is reached, permanently freezing withdrawals, repayments and other accrual-dependent operations. [5](#0-4) [6](#0-5) 

### Finding Description
`accrue_step` first multiplies `borrowed` by the current `borrow_index` through `scaled_to_original`, which is an `i128`-backed `Ray::mul`. [7](#0-6) [8](#0-7) [9](#0-8) 

After computing the next borrow index, it repeats the same representability assumption in `calculate_supplier_rewards`, multiplying scaled debt by both the old and new indexes before comparing the resulting values. [10](#0-9) 

`update_borrow_index` caps only the index at `MAX_BORROW_INDEX_RAY`; it does not bound the product `borrowed * borrow_index`, which is the quantity that must fit the RAY-backed `i128` domain. [6](#0-5) 

The direct unprivileged trigger is `update_indexes(caller, assets)` with `assets` containing the vulnerable `HubAssetKey`; ordinary `withdraw`, `repay`, liquidation-related pool calls and other mutations also load an interest-synced market before performing their own accounting. [1](#0-0) [11](#0-10) 

The existing regression test demonstrates that the overflow occurs as `MATH_OVERFLOW`, leaves the stored index below its intended ceiling, and subsequently causes both withdrawal and repayment attempts to fail with the same error. [12](#0-11) 

### Impact Explanation
Once the elapsed accrual reaches the arithmetic boundary, no operation can advance `last_timestamp` because `global_sync` must finish all accrued chunks and return before `Cache::commit` persists the result. [3](#0-2) [4](#0-3) 

Every later call repeats the accrual from the same stored timestamp and reaches the same overflowing product, while even privileged parameter changes cannot rescue the market because `upgrade_liquidity_pool_params` performs index accrual first. [13](#0-12) [14](#0-13) 

The result is permanent freezing of the affected market’s user collateral and unclaimed yield rather than a transient availability failure: suppliers cannot withdraw, borrowers cannot reduce trapped debt, and liquidation or recapitalization cannot safely process the market while its value cannot be represented. [11](#0-10) [15](#0-14) 

### Likelihood Explanation
The condition requires an extremely large, but previously admitted, scaled debt position combined with enough accrued index growth to push `borrowed * index` beyond the RAY-backed `i128` range. [16](#0-15) [9](#0-8) 

The protocol documentation acknowledges that market totals must fit the RAY domain independently of the index ceiling and that accrual-dependent exits can become blocked by value overflow. [17](#0-16) 

The likelihood is limited by the capital required and the need for sustained high utilization, but the triggering transaction itself is permissionless and does not require leaked keys, an invalid parameter, oracle manipulation or privileged access. [18](#0-17) [19](#0-18) 

### Recommendation
Bound the projected total debt value, not merely the borrow index. During each accrual step, compute `borrowed * new_borrow_index` in a wider integer domain such as `I256`, and clamp `new_borrow_index` to `min(MAX_BORROW_INDEX_RAY, floor(i128::MAX * RAY / borrowed))` before any `i128` conversion or market-value subtraction. [6](#0-5) [20](#0-19) 

Alternatively, reject accrual states whose debt value cannot fit `i128` before updating any index, while advancing `last_timestamp` only for safely representable chunks; silently saturating the debt value would misstate obligations and should be avoided. [21](#0-20) [22](#0-21) 

Add a regression test that reaches the value ceiling and verifies that subsequent `update_indexes`, `withdraw`, `repay`, liquidation and recapitalization calls either continue safely under an explicit debt-index cap or fail before state becomes permanently unaccruable. [23](#0-22) 

### Proof of Concept
1. Configure a valid 18-decimal market that admits approximately one billion whole tokens and enough collateral capacity to borrow 98% of that supply. [24](#0-23) 
2. As an unprivileged account owner, call `supply` with the debt asset, supply sufficient collateral, then call `borrow` for the admitted amount. [25](#0-24) 
3. After interest has accumulated at high utilization, call `update_indexes(caller, vec![HubAssetKey { hub_id, asset }])`. [1](#0-0) 
4. The controller forwards the request to `LiquidityPool::update_indexes`, whose accrual loop invokes `accrue_step` until the stored timestamp reaches the current time. [26](#0-25) [27](#0-26) 
5. `accrue_step` evaluates `borrowed * borrow_index` and then `borrowed * new_borrow_index`; when the scaled debt is large enough, one of those products exceeds `i128` and returns `MATH_OVERFLOW` before the intended index cap can take effect. [5](#0-4) [20](#0-19) [6](#0-5) 
6. The repository’s test confirms the resulting behavior: `update_indexes` fails with `MATH_OVERFLOW`, the stored index remains below `MAX_BORROW_INDEX_RAY`, and subsequent `withdraw` and `repay` calls fail with `MATH_OVERFLOW` as well. [12](#0-11)

### Citations

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

**File:** contracts/controller/src/lib.rs (L367-371)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
```

**File:** contracts/controller/src/markets.rs (L87-100)
```rust
/// Accrues indexes under the current model before replacing rate and flash-loan
/// parameters, then emits the new configuration.
pub(crate) fn upgrade_liquidity_pool_params(
    env: &Env,
    hub_asset: &HubAssetKey,
    params: &InterestRateModel,
) {
    let mut cache = Context::new(env);

    let pool_addr = cache.cached_pool_address();

    pool_update_indexes_call(env, &pool_addr, &vec![env, hub_asset.clone()]);

    pool_update_params_call(env, &pool_addr, hub_asset, params);
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

**File:** common/src/rates/simulate.rs (L157-175)
```rust
    let mut remaining = total_delta_ms;
    while remaining > 0 {
        let chunk = remaining.min(MAX_COMPOUND_DELTA_MS);
        let step = accrue_step(
            env,
            &params,
            state.borrowed,
            supplied,
            borrow_index,
            supply_index,
            chunk,
        );

        borrow_index = step.borrow_index;
        supply_index = step.supply_index;
        supplied = supplied.checked_add(env, step.revenue_shares);

        remaining -= chunk;
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

**File:** common/src/rates/index.rs (L73-86)
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

**File:** contracts/pool/src/ops/mod.rs (L29-33)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
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

**File:** docs/reference/formulas.md (L432-437)
```markdown
The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```
