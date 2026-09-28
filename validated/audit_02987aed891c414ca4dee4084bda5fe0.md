### Title
RAY-value overflow during interest accrual permanently freezes a large market - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
`accrue_step` converts aggregate scaled debt and supply back to RAY-denominated value before calculating utilization, rates, and rewards. [1](#0-0)  The conversion uses `scaled_to_original`, which delegates to `Ray::mul` and therefore panics when the representable result exceeds `i128`. [2](#0-1) [3](#0-2)  Because every pool mutation syncs the market before mutating it, crossing this value boundary prevents ordinary exits, repayments, liquidations, and explicit keeper accrual from completing. [4](#0-3) 

### Finding Description
The intended borrow-index ceiling does not protect the protocol from overflowing the separate `borrowed * borrow_index` and `supplied * supply_index` products: `update_borrow_index` caps only the index after multiplication, while `calculate_supplier_rewards` subsequently multiplies aggregate shares by both indexes. [5](#0-4) [6](#0-5)  Even earlier in the same accrual step, `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` can overflow before a new index is calculated. [7](#0-6)  The permissionless controller entrypoint `update_indexes(caller, assets)` forwards the selected `(hub_id, asset)` books to pool accrual, and the pool commits each synchronized market. [8](#0-7) [9](#0-8) 

### Impact Explanation
Once aggregate market value no longer fits the RAY domain, `MathOverflow` is raised inside the mandatory pre-mutation accrual and the transaction rolls back. [4](#0-3) [10](#0-9)  This permanently freezes supplier principal and yield in the affected market, blocks borrower repayment, and prevents liquidation or bad-debt processing that must first load the same market. [11](#0-10) [12](#0-11)  The in-tree regression test demonstrates that `update_indexes`, `withdraw`, and `repay` all fail with `MATH_OVERFLOW` while the borrow index remains below `MAX_BORROW_INDEX_RAY`. [13](#0-12) 

### Likelihood Explanation
The condition requires a very large admitted market together with sustained high utilization so index growth pushes a `scaled * index` value past `i128::MAX`; caps and utilization policy determine how practical that state is. [14](#0-13)  No privileged action is needed to trigger the failure once such a market exists: any authenticated caller may call `update_indexes`, and any affected user can trigger the same failure through `withdraw` or `repay`. [15](#0-14) [16](#0-15)  This is therefore a conditional High-impact availability and solvency failure rather than an immediately exploitable theft primitive. [17](#0-16) 

### Recommendation
Bound the protocol by total RAY-valued market size rather than only by token amount and index ceilings. [18](#0-17)  Admission and entry checks should ensure `supplied * MAX_SUPPLY_INDEX_RAY` and `borrowed * MAX_BORROW_INDEX_RAY` remain representable, and accrual should safely clamp or isolate an overflowing market before every recovery path becomes unusable. [5](#0-4) [19](#0-18) 

### Proof of Concept
The repository already contains a deterministic reproduction in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`. [20](#0-19) 

1. Create an 18-decimal market using the steep XLM curve and lift its caps. [21](#0-20) 
2. Supply `1_000_000_000 * 10^18` base units and borrow 98% of it against sufficient collateral. [22](#0-21) 
3. Advance ledger time and repeatedly call `update_indexes(caller, vec![HubAssetKey { hub_id, asset }])` until accrual returns `MathOverflow`. [23](#0-22) 
4. Verify that the stored borrow index is still below `MAX_BORROW_INDEX_RAY`, then observe that both `withdraw` and `repay` fail with the same overflow because they accrue before their respective mutations. [24](#0-23)

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

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp.rs (L12-15)
```rust
/// Adds two raw values, panicking with `GenericError::MathOverflow` on overflow.
fn checked_add_raw(env: &Env, a: i128, b: i128) -> i128 {
    a.checked_add(b)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
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

**File:** common/src/rates/index.rs (L73-83)
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

**File:** contracts/pool/src/ops/repay.rs (L36-45)
```rust
/// Accrues interest, resolves the repay amount into burned debt shares and
/// overpayment, burns the shares, and credits the net repay to cash without
/// transferring the overpayment refund. Panics if a positive net repay would
/// burn zero scaled shares.
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
```

**File:** contracts/pool/src/ops/withdraw.rs (L53-65)
```rust
/// Runs withdraw accounting without transferring tokens.
///
/// Resolves full or partial close, burns shares, optionally withholds the
/// liquidation fee, and gates the final state before debiting cash.
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-333)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L335-356)
```rust
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
