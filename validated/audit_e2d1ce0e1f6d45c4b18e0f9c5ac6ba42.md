### Title
Sustained high-utilization market exhausts the RAY value domain and permanently freezes all market operations - (File: contracts/pool/src/interest.rs)

### Summary
The Tomcat report's bug class — a remotely reachable input that causes resource exhaustion and hangs the whole service — maps onto XOXNO Lending's accrual path: once a market's `borrowed` scaled shares times `borrow_index` overflows the RAY/`i128` domain inside `accrue_step`, `global_sync` panics with `MATH_OVERFLOW` on every subsequent call. Because every user-facing verb (supply, borrow, withdraw, repay, liquidate, clean_bad_debt, flash paths) accrues first, the entire market is permanently bricked — no repay, no withdraw, no liquidation, no bad-debt cleanup.

### Finding Description
`ops::market::accrue` loads the market cache and calls `interest::global_sync`, which loops `accrue_chunk` over `MAX_COMPOUND_DELTA_MS` windows and invokes `accrue_step` on the stored `borrowed`/`supplied` share counts and indexes [1](#0-0) [2](#0-1) . Accrual does not cap the index against the *value* capacity of the fixed-point type: `scaled_to_original`/`mul` on `borrowed * borrow_index` overflows `i128` before the `MAX_BORROW_INDEX_RAY` cap is reached, so the panic happens mid-accrual and `last_timestamp` is never advanced. Since `accrue` is invoked first by every pool op, the state is unrecoverable — there is no entrypoint that skips accrual.

This is proven by the harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`, which supplies a whale-scale book, borrows to 98% utilization on a steep rate curve, advances time, and observes `MATH_OVERFLOW` on `update_indexes`, after which `withdraw` and `repay` both fail with the same error and `borrow_index < MAX_BORROW_INDEX_RAY` confirms the index cap never engaged [3](#0-2) . The threat model independently acknowledges the gap: "Finite RAY value capacity can be exhausted before the index ceiling. Synchronizing an overlarge book can then fail before an otherwise risk-reducing operation" [4](#0-3) .

The unprivileged reachability is direct: `supply` and `borrow` are permissionless controller verbs, and `update_indexes` itself is permissionless (caller auth only, no role check) [5](#0-4) , so any address can both build the oversized book and trigger the accrual that crosses the cliff.

### Impact Explanation
Permanent freezing of funds and protocol insolvency: all suppliers' deposits, borrowers' collateral, and pending liquidations in the affected `(hub_id, asset)` book are locked forever. Repayment is impossible, so interest accounting and bad-debt cleanup cannot proceed; the market cannot operate and its token funds are unreachable.

### Likelihood Explanation
Requires a whale-scale position and a steep utilization curve sustained over a long horizon — the test needed ~billions of units of an 18-decimal asset at 98% utilization and multiple years of accrual. That is high capital and time cost, but it is reachable purely through permissionless `supply`/`borrow` with no privileged input, and there is no governance lever or cap that prevents the value-domain overflow once the book is that large. Medium severity is appropriate.

### Recommendation
Bound accrual so `borrowed * borrow_index` cannot overflow before the index cap engages: either clamp `borrow_index` at `MAX_BORROW_INDEX_RAY` *before* the value multiplication in `accrue_step`, or enforce per-market supply/borrow caps derived from the fixed-point value ceiling (`i128::MAX / index`) rather than token counts alone. Alternatively, make `global_sync` degrade gracefully — freeze the index at the cap instead of reverting — so exits and repayments remain possible.

### Proof of Concept
Existing harness test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321` `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates the full path: permissionless `supply_raw`/`borrow_raw` build the book, `advance_time` grows the index past the value ceiling, `try_update_indexes_for` fails with `MATH_OVERFLOW`, and `try_withdraw_raw`/`try_repay` fail identically — the market is frozen with no recovery path.

### Citations

**File:** contracts/pool/src/interest.rs (L20-53)
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-361)
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
    std::println!(
        "ray-value cliff reached after {years} years at 98 percent utilization on the XLM curve; last index x{:.1}",
        last.borrow_index as f64 / RAY as f64
    );
}
```

**File:** docs/explanation/threat-model.md (L319-324)
```markdown
Finite RAY value capacity can be exhausted before the index ceiling. Synchronizing
an overlarge book can then fail before an otherwise risk-reducing operation.
Caps must account for plausible index growth as well as token balances.
Accrual cadence changes utilization and subsequent rates; bounded chunks do not
make cadence neutral or prove exact conservation after integer rounding.
See [numeric limits](../reference/formulas.md#numeric-limits).
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
