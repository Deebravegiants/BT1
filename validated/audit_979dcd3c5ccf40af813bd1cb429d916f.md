### Title
Unbounded index accrual permanently freezes a high-value debt market - (File: `contracts/pool/src/interest.rs`)

### Summary
An attacker-funded market can grow its scaled-debt value until interest accrual overflows `i128` before the configured borrow-index cap is reached. Because every subsequent market operation performs accrual first, the market then rejects withdrawals, repayments, liquidation, revenue claims, and even ordinary interest-model updates. [1](#0-0) [2](#0-1) 

### Finding Description
`Controller::update_indexes(caller, assets)` is permissionless and forwards the requested `Vec<HubAssetKey>` to the pool after caller authorization. [3](#0-2)  The pool’s `update_indexes` calls `ops::market::accrue`, and each accrual runs `global_sync`, which repeatedly invokes `accrue_step` until the stored timestamp reaches the current ledger time. [4](#0-3) [5](#0-4) 

`accrue_step` recalculates borrow and supply indexes from the market’s scaled debt, scaled supply, current indexes, rate model, and elapsed time, then commits those values to the cache. [6](#0-5)  The checked conversion of scaled debt into its original value is not bounded by a debt-value ceiling before multiplying by the borrow index. Consequently, a sufficiently large `borrowed * borrow_index` product can exceed `i128::MAX` while `borrow_index` itself is still below `MAX_BORROW_INDEX_RAY`. [7](#0-6) [8](#0-7) 

The repository’s long-horizon test demonstrates this exact state transition: a billion-unit, 18-decimal market at 98% utilization eventually causes `update_indexes` to panic with `MathOverflow`, while the stored borrow index remains below its configured cap. [9](#0-8)  Afterward, both `withdraw` and `repay` fail with the same `MathOverflow`, confirming that the failed exceptional condition is not confined to the permissionless index-update call. [10](#0-9) 

### Impact Explanation
This is a permanent freezing-of-funds condition for the affected market. Supplier cash, borrower collateral, liquidator access to the debt market, unclaimed protocol revenue, and bad-debt remediation paths all depend on successfully accruing the same market state. [1](#0-0) [10](#0-9) 

The failure also defeats the ordinary administrative recovery path: `upgrade_liquidity_pool_params` invokes `pool_update_indexes` before installing a safer rate model, so it hits the same overflow before the parameters can be changed. [2](#0-1)  Absent a contract upgrade or another out-of-band recovery mechanism, the market remains unable to operate.

### Likelihood Explanation
Likelihood is low to medium because the attacker must create or help create an exceptionally deep market, keep utilization high, and allow enough interest accrual to reach the value ceiling. The demonstrated setup uses a billion-token, 18-decimal market with 98% borrowed and max-utilization checks disabled in the test harness. [11](#0-10) 

Nevertheless, no privileged call is required to trigger the overflow once such a market exists: the final transaction is simply `update_indexes` with the affected `HubAssetKey`, callable by any authorized caller. [3](#0-2)  The exploit does not depend on oracle manipulation, malformed authentication, token misbehavior, or control of a privileged account.

### Recommendation
Bound the debt-value calculation before multiplying scaled shares by the borrow index. In particular:

- Enforce a maximum accrued debt value or maximum `borrowed * borrow_index` product inside the shared `accrue_step` path.
- Clamp `borrow_index` at `MAX_BORROW_INDEX_RAY` before any intermediate value can overflow `i128`.
- Ensure repayment, withdrawal, liquidation, bad-debt cleanup, and recapitalization can still execute after the cap is reached instead of repeatedly attempting an overflowing accrual.
- Add a rate-model recovery path that does not require successful prior accrual of an already-overflowing market.
- Extend the long-horizon regression test so accrual stops deterministically at the index/value cap rather than panicking with `MathOverflow`. [12](#0-11) 

### Proof of Concept
The existing test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` provides a direct executable reproduction. Its public-entrypoint sequence is equivalent to:

```rust
let huge_principal = 1_000_000_000i128 * 10i128.pow(18);
let huge_debt = huge_principal * 98 / 100;

controller.supply(
    attacker,
    account_id,
    spoke_id,
    vec![(debt_asset, huge_principal)],
);

controller.supply(
    attacker,
    account_id,
    spoke_id,
    vec![(collateral_asset, sufficient_collateral)],
);

controller.borrow(
    attacker,
    account_id,
    vec![(debt_asset, huge_debt)],
    Some(attacker),
);

// Repeat as ledger time advances.
controller.update_indexes(attacker, vec![debt_asset]);
```

The harness creates the same shape with `principal = BILLION * 10^18` and `debt = principal * 98 / 100`, advances ledger time, and calls `try_update_indexes_for(&["BIG18"])` until the call returns `MathOverflow`. [13](#0-12)  The resulting `borrow_index` remains below `MAX_BORROW_INDEX_RAY`, proving that the exceptional condition is an unbounded intermediate debt value rather than the intended index cap. [14](#0-13) 

After the overflow, both `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", 1.0)` return `MathOverflow`, demonstrating that user funds can no longer exit and debt can no longer be serviced through the normal entrypoints. [10](#0-9)

### Citations

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

**File:** contracts/controller/src/markets.rs (L94-100)
```rust
    let mut cache = Context::new(env);

    let pool_addr = cache.cached_pool_address();

    pool_update_indexes_call(env, &pool_addr, &vec![env, hub_asset.clone()]);

    pool_update_params_call(env, &pool_addr, hub_asset, params);
```

**File:** contracts/controller/src/markets.rs (L119-124)
```rust
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
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
