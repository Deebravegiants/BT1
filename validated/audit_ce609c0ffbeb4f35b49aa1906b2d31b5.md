### Title
RAY-scaled market-value overflow permanently freezes a heavily utilized market - (File: common/src/rates/simulate.rs)

### Summary
`accrue_step` unscalestotal borrowed and supplied shares by multiplying the scaled RAY values by their indexes before it calculates utilization or applies the borrow-index cap. [1](#0-0)  Once either product exceeds the `i128` RAY domain, every subsequent accrual panics before state is updated, leaving the market permanently unable to process repayments, withdrawals, or liquidations. [2](#0-1) 

### Finding Description
`global_sync` executes `accrue_step` for every elapsed compound interval before any market operation proceeds. [3](#0-2)  The first statements in `accrue_step` call `scaled_to_original` for `borrowed * borrow_index` and `supplied * supply_index`. [4](#0-3)  `scaled_to_original` performs an exact RAY multiplication and panics on `i128` overflow rather than saturating the resulting market value or utilization. [5](#0-4)  Although `update_borrow_index` caps the index afterward at `MAX_BORROW_INDEX_RAY`, the vulnerable total-value multiplication happens before that cap and can overflow while the stored index remains below the cap. [6](#0-5) 

Every controller action reaches the pool through `load_leg` or `synced_market`, both of which invoke `global_sync` before performing the operation-specific accounting. [7](#0-6)  Withdrawal accounting loads the synced leg before resolving the withdrawal and burning shares. [8](#0-7)  Repayment accounting likewise loads the synced leg before resolving and burning debt. [9](#0-8)  Borrow-side seizure also synchronizes the market before socializing debt and burning the position. [10](#0-9) 

### Impact Explanation
After the market crosses the representable-value boundary, any call that needs interest accrual reverts and `last_timestamp` remains behind current ledger time, so the same failing interval is retried forever. [2](#0-1)  Suppliers cannot withdraw, borrowers cannot repay, and liquidators or bad-debt cleaners cannot reduce the dangerous balances because all of those paths sync first. [7](#0-6)  The result is permanent freezing of user collateral and supplied funds in the affected pool market rather than merely a temporary utilization denial. [11](#0-10) 

### Likelihood Explanation
An unprivileged account can create the required state through `Controller::supply`, `Controller::borrow`, and the permissionless index-update path, provided the configured asset caps and available token supply admit a sufficiently large book. [12](#0-11)  The repository’s regression scenario demonstrates the reachable sequence with an 18-decimal market holding one billion whole tokens and approximately 98% utilization; sustained accrual reaches the RAY-value ceiling before `MAX_BORROW_INDEX_RAY` engages. [13](#0-12)  This requires an extremely large and highly utilized market, so it is less likely than routine input-validation failures, but the resulting freeze is severe and cannot be repaired by ordinary repayments, withdrawals, liquidations, or cleanup calls. [14](#0-13) 

### Recommendation
Do not require the full scaled-position multiplication to fit `i128` merely to calculate utilization. Compute `borrowed_original / supplied_original` in widened arithmetic or derive a saturated utilization directly from the scaled quantities, and clamp the result to `Ray::ONE` when the value is not representable. The borrow index should then continue advancing to `MAX_BORROW_INDEX_RAY`, after which accrual can become a bounded no-interest state rather than a permanent trap. [6](#0-5)  Position and market unscaling used for actual payment amounts should still reject unrepresentable values where exact accounting is required, but accrual must not make the market unrecoverable before those operations can reduce balances. [15](#0-14)  Add the existing whale-market regression as a mandatory test asserting that `update_indexes`, `repay`, `withdraw`, and liquidation remain executable at the numeric boundary. [16](#0-15) 

### Proof of Concept
1. Create or use a listed 18-decimal market whose supply and borrow caps admit at least one billion whole tokens. [17](#0-16) 
2. Call `Controller::supply` with `account_id = 0`, the market’s `HubAssetKey`, and a `1_000_000_000 * 10^18` base-unit leg. [18](#0-17) 
3. Supply sufficient collateral in another market and call `Controller::borrow` for approximately 98% of the large market’s supplied amount. [19](#0-18) 
4. Advance ledger time and repeatedly invoke the permissionless `update_indexes` path until `accrue_step` panics while unscaling `borrowed * borrow_index` or `supplied * supply_index`. [20](#0-19) 
5. Observe that the stored borrow index is still below `MAX_BORROW_INDEX_RAY`, while subsequent `withdraw` and `repay` calls fail with `MATH_OVERFLOW` because they enter `global_sync` first. [21](#0-20)

### Citations

**File:** common/src/rates/simulate.rs (L51-66)
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L69-80)
```rust
/// Converts a scaled supply `Ray` back to an asset-unit amount, using
/// half-up rounding at `decimals` precision.
pub fn unscale_supply(env: &Env, scaled: Ray, supply_index: Ray, decimals: u32) -> i128 {
    scaled_to_original(env, scaled, supply_index).to_asset(env, decimals)
}

/// Converts a scaled supply `Ray` back to an asset-unit amount, using floor
/// rounding at `decimals` precision.
pub fn unscale_supply_floor(env: &Env, scaled: Ray, supply_index: Ray, decimals: u32) -> i128 {
    scaled
        .mul_floor(env, supply_index)
        .to_asset_floor(env, decimals)
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

**File:** contracts/pool/src/ops/withdraw.rs (L57-67)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
```

**File:** contracts/pool/src/ops/repay.rs (L40-55)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );

    let position = position.checked_sub(env, burned);
    cache.burn_debt(burned);
```

**File:** contracts/pool/src/ops/seize.rs (L18-27)
```rust
pub(crate) fn apply(env: &Env, entry: &PoolSeizeEntry) -> MarketStateSnapshot {
    require_nonneg_amount(env, entry.position.scaled_amount);
    let mut cache = ops::synced_market(env, &entry.hub_asset);
    let position = Ray::from(entry.position.scaled_amount);

    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
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
