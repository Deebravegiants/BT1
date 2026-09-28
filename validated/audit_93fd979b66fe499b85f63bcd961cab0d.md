### Title
RAY value overflow during interest accrual permanently freezes a market - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
`accrue_step` converts total scaled debt and supply back into RAY-denominated values before calculating utilization, and both conversions delegate to `scaled_to_original` / `Ray::mul`. [1](#0-0) [2](#0-1)  Once `scaled * index` exceeds `i128::MAX`, the conversion panics with `MathOverflow` before the market timestamp or indexes are committed, so every subsequent accrual attempt repeats the same failure. [3](#0-2) 

### Finding Description
The permissionless controller entrypoint `update_indexes(caller, assets)` forwards attacker-selected `HubAssetKey` values to the pool’s `update_indexes`, which calls `ops::market::accrue`. [4](#0-3) [5](#0-4)  `ops::market::accrue` loads each market and invokes `interest::global_sync`, and `global_sync` calls `accrue_step` for each elapsed chunk. [6](#0-5) [7](#0-6)  The vulnerable boundary is the product of a market’s stored scaled shares and its current index, not the index cap itself: `update_borrow_index` only clamps the index after multiplication, while `accrue_step` has already evaluated `borrowed * borrow_index` and `supplied * supply_index`. [8](#0-7) [9](#0-8) 

All ordinary market legs use `load_leg`, which calls `synced_market`, which calls `global_sync` before the requested operation. [10](#0-9)  Consequently, after the stored share/index product crosses the representable range, `supply`, `borrow`, `withdraw`, `repay`, liquidation legs, flash operations, revenue claims, and even `update_params` cannot execute on that market. [11](#0-10) [12](#0-11) [13](#0-12) 

### Impact Explanation
This is permanent freezing of user funds and market functionality: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and governance cannot change the market’s rate model because `replace_rate_model` accrues through the same overflowing path first. [13](#0-12)  The repository’s stress test demonstrates the failure state by driving a one-billion-token, 18-decimal market to sustained high utilization, after which `update_indexes`, `withdraw`, and `repay` all return `MathOverflow`. [14](#0-13) 

### Likelihood Explanation
Likelihood is medium because exploitation requires an extremely large listed market and enough elapsed time for index growth to make the stored scaled value exceed `i128::MAX`. [15](#0-14)  The sequence is still reachable through normal `supply` and `borrow` calls, and the final trigger can be submitted by any address through `controller::update_indexes`. [16](#0-15) [4](#0-3)  Protocol documentation already acknowledges that bounded indexes do not guarantee representable market values and that the overflow blocks repayment and withdrawal, indicating the issue is a real domain boundary rather than merely a malformed-input revert. [17](#0-16) 

### Recommendation
Enforce a market-wide representable-value invariant before accepting new supply or debt, ensuring both `supplied * MAX_SUPPLY_INDEX_RAY / RAY` and `borrowed * MAX_BORROW_INDEX_RAY / RAY` remain below `i128::MAX`. [18](#0-17)  Prefer saturating accrual at the last representable index or adding a non-accruing emergency parameter path so an already-affected market can be recovered without requiring a contract upgrade. [13](#0-12)  Market entry checks should compute worst-case share/index products rather than relying only on token-unit caps, because the overflow threshold falls as indexes grow. [19](#0-18) 

### Proof of Concept
1. Configure an 18-decimal market with a supply/borrow cap admitting at least one billion whole tokens and a steep interest-rate curve. [20](#0-19) 
2. Supply `1_000_000_000 * 10^18` base units and borrow a large fraction of the market, leaving the position untouched while the borrow index compounds. [21](#0-20) 
3. Call `controller.update_indexes(caller, [hub_asset])`; accrual reaches `scaled_to_original(borrowed, borrow_index)` or the corresponding supply conversion and reverts once the product exceeds `i128::MAX`. [9](#0-8) [6](#0-5) 
4. Retry `update_indexes`, `withdraw`, or `repay`; each operation calls `global_sync` before applying its own accounting, so all revert with `MathOverflow` and the market remains frozen. [10](#0-9) [22](#0-21)

### Citations

**File:** common/src/rates/simulate.rs (L60-71)
```rust
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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
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

**File:** contracts/pool/src/ops/market.rs (L50-56)
```rust
/// Accrues interest under the old model, commits it, then replaces the interest
/// and flash-loan parameters and validates them against the stored decimals.
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
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

**File:** common/src/rates/index.rs (L13-18)
```rust
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

**File:** contracts/pool/src/ops/repay.rs (L40-45)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
```

**File:** contracts/pool/src/ops/withdraw.rs (L62-65)
```rust
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
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

**File:** contracts/pool/src/cache/scale.rs (L19-27)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
    }
```
