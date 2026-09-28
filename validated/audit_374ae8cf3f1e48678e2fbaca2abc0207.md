### Title
Accrual value overflow permanently freezes oversized lending market - (File: common/src/rates/simulate.rs)

### Summary
Pool interest accrual converts scaled supply and debt balances to RAY-valued token amounts with `i128` fixed-point multiplication before applying the borrow-index ceiling. Once a market's scaled principal and accrued index produce a value above `i128::MAX`, `accrue_step` panics with `MathOverflow`. Because every market operation accrues first, the affected market can no longer process repayment, withdrawal, liquidation, or further index updates. [1](#0-0) 

### Finding Description
`accrue_step` unconditionally executes `scaled_to_original` for both `borrowed * borrow_index` and `supplied * supply_index`, and only afterward calls `update_borrow_index`, whose `MAX_BORROW_INDEX_RAY` clamp caps the index itself rather than the represented token value. [2](#0-1)  `scaled_to_original` delegates to the non-saturating `Ray::mul`, so a representable scaled balance multiplied by a sufficiently grown index returns no value and aborts the transaction. [3](#0-2)  The mutating path reaches this code through `Cache::load`/`interest::global_sync` from `pool::update_indexes`; the controller's `update_indexes` is callable by any authenticated caller and forwards the market list to the owner-restricted pool call. [4](#0-3) [5](#0-4) [6](#0-5) 

The repository's long-horizon test establishes the reachable state: a one-billion-whole-token, 18-decimal market at 98% utilization reaches `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`, and subsequent withdrawal and repayment attempts fail with the same error. [7](#0-6) 

### Impact Explanation
All user funds held in the affected market are permanently frozen: suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot perform liquidation once accrual itself always panics. This is not merely a temporary fail-closed input check because the stored scaled principal and index cannot be reduced without completing the same accrual that overflows. The indexed test demonstrates that the index ceiling does not prevent this condition and that exit and repayment remain blocked afterward. [8](#0-7) 

### Likelihood Explanation
The condition requires an exceptionally large market and sustained high utilization under a steep permitted rate curve; the tested setup uses one billion whole 18-decimal tokens, roughly 98% utilization, and multiple years of compounding. Those prerequisites make exploitation capital- and maturity-dependent rather than immediate, but every step is reachable through unprivileged `supply`, `borrow`, and `update_indexes` calls once governance has admitted sufficiently high caps and a rate model. [9](#0-8) 

### Recommendation
Bound represented market values, not only indexes. Before scaling or at market-entry/cap enforcement, ensure `supplied * supply_index` and `borrowed * borrow_index` remain below the supported `i128` domain, or make accrual clamp represented debt and supply at a protocol-defined ceiling without aborting all future operations. Add regression coverage that continues to process `repay`, `withdraw`, and `liquidate` at the value boundary rather than only asserting the eventual `MathOverflow`. [2](#0-1) [8](#0-7) 

### Proof of Concept
1. On a market with an 18-decimal token, high cap, and the steep rate model shown by the test, create an account and call controller `supply(caller, 0, spoke_id, [(hub_asset, 1_000_000_000 * 10^18)])`.
2. From a funded collateral account, call `borrow(caller, borrower_account_id, [(hub_asset, 980_000_000 * 10^18)], None)`, leaving utilization near 98%.
3. Let ledger time advance until compounding pushes `borrowed * borrow_index` above `i128::MAX`; the repository test finds this before the configured borrow-index cap.
4. Any caller invokes `update_indexes(caller, [hub_asset])`. The controller forwards to the pool, `accrue` runs `global_sync`, and `accrue_step` panics in `scaled_to_original`.
5. Subsequent `repay`, `withdraw`, `liquidate`, and `update_indexes` calls attempt the same accrual and fail with `MathOverflow`, permanently freezing the market's funds. [10](#0-9)

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

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
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
