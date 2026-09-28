### Title
Accrued debt value overflows before the index cap and permanently freezes a market - (File: common/src/rates/scaling.rs)

### Summary
An unprivileged borrower can drive a sufficiently large, high-utilization market into a state where interest accrual panics with `MathOverflow`. Once crossed, every pool mutation performs the same accrual before acting, blocking `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, and `update_indexes` and permanently freezing supplier funds unless the contract is upgraded. [1](#0-0) [2](#0-1) 

### Finding Description
`update_indexes` invokes `ops::market::accrue`, while every market operation loads its cache through `synced_market`, which calls `interest::global_sync` before the operation-specific logic runs. [3](#0-2) [4](#0-3) 

`global_sync` processes elapsed time in bounded chunks, but each chunk calls `accrue_step` using the market’s full scaled debt and current borrow index. [5](#0-4) [6](#0-5) 

`accrue_step` converts scaled debt through `scaled_to_original`, which performs `scaled.mul(index)` in RAY arithmetic. [7](#0-6) 

That multiplication panics with `MathOverflow` when the product cannot fit in `i128`. [8](#0-7) 

The regression test constructs an 18-decimal market with `1_000_000_000 * 10^18` base units supplied and a borrow equal to 98% of that liquidity. [9](#0-8) 

After ledger time advances enough, `update_indexes` fails with `MathOverflow`; the stored borrow index is still below `MAX_BORROW_INDEX_RAY`, proving that the debt-value multiplication overflows before the index bound can engage. [10](#0-9) 

The same test then demonstrates that both `withdraw` and `repay` fail with `MathOverflow`, because they must sync the market before mutating it. [11](#0-10) 

An attacker can reach the trigger through ordinary controller calls: deposit collateral with `supply`, borrow the deep market through `borrow(account_id, [(hub_asset, amount)], to)`, leave the position to accrue, and have anyone call `update_indexes([hub_asset])`. [12](#0-11) [3](#0-2) 

### Impact Explanation
This permanently freezes all supplier funds in the affected market because withdrawals cannot progress past accrual, while borrowers cannot repay and liquidators or bad-debt cleanup cannot recover the position. [1](#0-0) [13](#0-12) 

The failed accrual also prevents the accrual timestamp from being marked complete, so subsequent invocations retry an even larger elapsed interval and hit the same or worse overflow. [14](#0-13) 

### Likelihood Explanation
The attack requires a market whose configured caps and interest model permit enough scaled debt for `scaled_debt * borrow_index` to exceed `i128::MAX`, plus sufficient attacker collateral to establish the borrow. [15](#0-14) [16](#0-15) 

Those are normal market-capacity parameters rather than attacker privileges: the attacker only needs `supply`, `borrow`, and public `update_indexes` access, while existing suppliers provide the victim liquidity. [17](#0-16) [18](#0-17) 

### Recommendation
Cap or saturate the borrow index before multiplying total scaled debt by that index, and perform utilization/debt-value calculations with widened or saturating arithmetic so an oversized market reaches `MAX_BORROW_INDEX_RAY` instead of trapping. [19](#0-18) [7](#0-6) 

Also bound supply and borrow caps by asset decimals and the configured maximum rate so that `scaled_debt * MAX_BORROW_INDEX_RAY` remains representable, and provide a bounded accrual path that commits the clamped index rather than leaving the market permanently unsyncable. [20](#0-19) [5](#0-4) 

### Proof of Concept
The existing regression test creates an 18-decimal `BIG18` market, supplies `1_000_000_000 * 10^18` base units, supplies collateral, and borrows 98% of the `BIG18` liquidity. [9](#0-8) 

It then advances ledger time and repeatedly calls `update_indexes(["BIG18"])` until the call returns contract error `MathOverflow`. [21](#0-20) 

At failure, `borrow_index < MAX_BORROW_INDEX_RAY`, showing that the overflow occurs during debt-value calculation before the intended index cap is reached. [22](#0-21) 

Finally, the test proves the market is unusable by showing that both a supplier `withdraw` of one base unit and a borrower `repay` fail with the same `MathOverflow`. [11](#0-10)

### Citations

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

**File:** contracts/pool/src/lib.rs (L174-179)
```rust
    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
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

**File:** common/src/rates/scaling.rs (L12-15)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
```

**File:** common/src/rates/scaling.rs (L18-32)
```rust
/// Converts an asset-unit `cap` to a scaled `Ray` value, rounding down.
///
/// The division saturates at `i128::MAX` instead of panicking, so the cap check
/// fails open rather than trapping an entry path. The asset-to-RAY
/// rescale still panics on overflow; listings validate caps with
/// [`crate::validation::require_cap_within_asset_domain`]. Position accounting
/// uses [`calculate_scaled_supply`] and [`calculate_scaled_borrow`], which panic
/// on overflow.
pub fn calculate_scaled_cap(env: &Env, cap: i128, decimals: u32, index: Ray) -> Ray {
    Ray::from(fp_core::mul_div_floor_saturating(
        env,
        Ray::from_asset(env, cap, decimals).raw(),
        RAY,
        index.raw(),
    ))
```

**File:** common/src/math/fp_core.rs (L104-118)
```rust
/// Computes `x * y / d` rounded half up. Requires `x >= 0`, `y >= 0`, and `d > 0`; a
/// `debug_assert` checks this in debug builds. Panics with `GenericError::DivisionByZero` if
/// `d == 0`, and with `GenericError::MathOverflow` if any other precondition is violated or if
/// the result does not fit in `i128`.
pub fn mul_div_half_up(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    // The zero check runs first so debug and release builds agree on a zero
    // divisor: both surface `DivisionByZero` rather than tripping the assert.
    require_nonzero_divisor(env, d);
    debug_assert!(
        x >= 0 && y >= 0 && d > 0,
        "mul_div_half_up: non-negative x, y and positive d"
    );
    try_mul_div_half_up(env, x, y, d)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

**File:** contracts/controller/src/positions/debt.rs (L33-66)
```rust
pub(crate) fn process_borrow(
    env: &Env,
    caller: &Address,
    account_id: u64,
    borrows: &Vec<HubPayment>,
    to: Option<Address>,
) {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_positive_payments(env, borrows);

    validate_position_entry_gates(
        env,
        &account,
        &aggregated,
        &mut cache,
        AccountPositionType::Borrow,
    );
    settle_borrow(env, &mut account, &recipient, &aggregated, &mut cache);

    let restamped = enforce_post_pool_solvency(env, &mut cache, &mut account);
    let sides = if restamped {
        PositionSides::Both
    } else {
        PositionSides::Debt
    };
    finalize_position_flow(env, account_id, &account, &mut cache, sides, false);
}
```

**File:** contracts/controller/src/positions/debt.rs (L93-122)
```rust
/// Borrows the aggregated amounts to `recipient` and merges the debt results.
fn settle_borrow(
    env: &Env,
    account: &mut Account,
    recipient: &Address,
    aggregated: &AggregatedPayments,
    cache: &mut Context,
) {
    let pool_addr = cache.cached_pool_address();
    let mut entries: Vec<PoolBorrowEntry> = Vec::new(env);
    for (hub_asset, amount) in aggregated.iter() {
        let position = account.get_or_create_debt_position(&hub_asset);
        entries.push_back(PoolBorrowEntry {
            action: make_pool_action(&position, amount, hub_asset.clone()),
        });
    }
    let results = pool_borrow_call(env, &pool_addr, recipient, &entries);
    for_each_leg(env, &entries, &results, |entry, result| {
        merge_debt_leg(
            env,
            account,
            events::PositionAction::Borrow,
            &entry.action.hub_asset,
            LegDirection::Entry {
                asset_decimals: result.asset_decimals,
            },
            &LegOutcome::from(&result),
            cache,
        );
    });
```

**File:** contracts/pool/src/ops/seize.rs (L20-28)
```rust
    let mut cache = ops::synced_market(env, &entry.hub_asset);
    let position = Ray::from(entry.position.scaled_amount);

    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
```

**File:** contracts/controller/src/spoke_usage.rs (L100-115)
```rust
    /// Buffers a scaled increase from stored usage, or zero for a missing row.
    /// Rejects totals above the cap converted at the supplied index.
    pub(crate) fn apply_entry(
        &mut self,
        side: UsageSide,
        hub_asset: &HubAssetKey,
        delta_scaled: Ray,
        cap: i128,
        index: Ray,
        decimals: u32,
    ) {
        let mut usage = self.load_usage_row(hub_asset).unwrap_or_default();
        let next = enforce_spoke_cap(&self.env, side, &usage, delta_scaled, cap, index, decimals);
        side.set_scaled(&mut usage, next.raw());
        self.usage.set(hub_asset.clone(), usage);
    }
```

**File:** contracts/controller/src/spoke_usage.rs (L142-156)
```rust
/// Adds scaled usage and enforces the asset-unit cap converted to RAY
/// with `index` and `decimals`.
fn enforce_spoke_cap(
    env: &Env,
    side: UsageSide,
    usage: &SpokeUsageRaw,
    delta_scaled: Ray,
    cap: i128,
    index: Ray,
    decimals: u32,
) -> Ray {
    let cap_scaled = calculate_scaled_cap(env, cap, decimals, index);
    let next_scaled = Ray::from(side.scaled(usage)).checked_add(env, delta_scaled);
    assert_with_error!(env, next_scaled <= cap_scaled, side.cap_error());
    next_scaled
```
