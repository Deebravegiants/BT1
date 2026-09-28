### Title
Unchecked `i128` debt-value overflow permanently freezes all operations in a large accrued market - ([File: common/src/rates/simulate.rs])

### Summary
Interest accrual converts aggregate scaled debt and supply into RAY-denominated values using `i128` arithmetic before applying the borrow-index ceiling. Once `borrowed * borrow_index` or `supplied * supply_index` exceeds `i128::MAX`, accrual panics with `MathOverflow`; because every state-changing market path accrues first, the affected market can no longer process repayments, withdrawals, liquidations, flash operations, revenue claims, or later index updates. [1](#0-0) 

### Finding Description
`accrue_step` first computes `borrowed_original` and `supplied_original` through `scaled_to_original`, which multiplies scaled RAY shares by their index. [2](#0-1)  `scaled_to_original` delegates directly to `Ray::mul`, while the comments in the scaling layer explicitly note that position accounting panics on overflow. [3](#0-2)  The same accrual then calculates old and new aggregate debt with `borrowed.mul(old_borrow_index)` and `borrowed.mul(new_borrow_index)`. [4](#0-3) 

Although `update_borrow_index` caps the resulting index at `MAX_BORROW_INDEX_RAY`, the cap is applied only after the multiplication succeeds, so an oversized aggregate position can overflow before the index bound protects the system. [5](#0-4)  `global_sync` executes this step for every elapsed-time chunk before any mutation is processed. [6](#0-5) 

An unprivileged account can create the prerequisite state through normal `supply` and `borrow` calls where governance caps, available collateral, and token supply permit a sufficiently large market. Any account can then trigger the failure through the permissionless `update_indexes` entrypoint, which forwards the selected `HubAssetKey` to the pool. [7](#0-6)  The controller implementation only authorizes the caller and calls `pool_update_indexes`; it does not recover from the accrual panic. [8](#0-7) 

The codebase already contains a regression scenario demonstrating the exact cliff: a one-billion-token, 18-decimal market at sustained high utilization overflows before the borrow-index cap engages, and subsequent withdrawal and repayment attempts both fail with `MathOverflow`. [9](#0-8) 

### Impact Explanation
This is permanent freezing of funds and can also create protocol insolvency because debtors cannot repay, suppliers cannot withdraw, and liquidators cannot unwind risk in the affected market. [9](#0-8)  The freeze is not limited to the account that created the large position: the pool stores aggregate `borrowed`, `supplied`, and index state per market, and `accrue_step` multiplies those aggregates before processing any individual action. [1](#0-0) 

Withdrawal is blocked because `ops::load_leg` loads the market leg before share burning and cash debit, and that load runs the accrual path. [10](#0-9)  Repayment is blocked for the same reason before debt shares can be burned or cash credited. [11](#0-10)  The failure state is persistent because elapsed time cannot be reduced, the oversized aggregate position cannot be reduced by repayment or withdrawal, and `update_indexes` itself cannot complete. [6](#0-5) 

### Likelihood Explanation
The attack requires an unusually large listed market, sufficient token liquidity, high borrow utilization, and enough elapsed time for the index to multiply the aggregate position beyond `i128::MAX`. [12](#0-11)  The in-repo stress test demonstrates that the condition is reachable under configured market parameters and ordinary `supply`/`borrow` semantics, with the failure asserted after advancing ledger time. [13](#0-12)  No privileged action is required at trigger time because `update_indexes` is permissionless and only requires caller authorization. [8](#0-7) 

### Recommendation
Use widened checked arithmetic for aggregate debt and supply valuation during accrual, and clamp or safely split the computation when the `i128` RAY value exceeds the representable domain. At minimum, `accrue_step` should detect the value ceiling before multiplication and transition the market into a recoverable bounded state instead of leaving every future accrual guaranteed to panic. [14](#0-13)  Apply the same widened representation inside `calculate_supplier_rewards`, since both `old_total_debt` and `new_total_debt` can independently overflow even when the index itself remains below `MAX_BORROW_INDEX_RAY`. [15](#0-14) 

### Proof of Concept
1. Configure a listed asset with high decimals and a large admitted supply/borrow cap, then supply `principal` base units through `controller.supply`. [16](#0-15) 
2. Supply sufficient collateral in another listed asset and borrow approximately `principal * 98 / 100` through `controller.borrow`, producing a very large aggregate scaled debt at high utilization. [17](#0-16) 
3. Advance ledger time until the borrow index has grown enough that `borrowed_scaled * borrow_index` or `supplied_scaled * supply_index` exceeds `i128::MAX`. [14](#0-13) 
4. Call `controller.update_indexes(caller, vec![hub_asset])`; the pool’s accrual panics with `MathOverflow` before the borrow-index cap is applied. [7](#0-6) 
5. Subsequent `withdraw`, `repay`, liquidation-related settlement, and further `update_indexes` calls for that `hub_asset` all fail on the same accrual multiplication, leaving user collateral and debt locked. [18](#0-17)

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

**File:** common/src/rates/scaling.rs (L12-25)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}

/// Converts an asset-unit `cap` to a scaled `Ray` value, rounding down.
///
/// The division saturates at `i128::MAX` instead of panicking, so the cap check
/// fails open rather than trapping an entry path. The asset-to-RAY
/// rescale still panics on overflow; listings validate caps with
/// [`crate::validation::require_cap_within_asset_domain`]. Position accounting
/// uses [`calculate_scaled_supply`] and [`calculate_scaled_borrow`], which panic
/// on overflow.
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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
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

**File:** contracts/pool/src/ops/withdraw.rs (L57-81)
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
    let net_transfer = withhold_liquidation_fee(
        env,
        &mut cache,
        gross_amount,
        is_liquidation,
        entry.protocol_fee,
    );

    // A footprint-only close must not add a utilization gate to same-market
    // net settlement: it burns no shares and moves no cash.
    let empty_close = position.raw() == 0 && entry.action.amount == i128::MAX;
    gate_and_debit(env, &mut cache, net_transfer, is_liquidation || empty_close);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/repay.rs (L40-60)
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

    cache.credit_cash(net_repay);

    let snapshot = cache.commit();
    let mutation = cache.position_mutation(position, net_repay);
```
