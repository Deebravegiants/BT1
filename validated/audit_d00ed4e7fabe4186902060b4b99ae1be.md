### Title
RAY-scaled debt value overflows i128 during accrual, permanently freezing a market - (File: common/src/rates/scaling.rs)

### Summary
CVE-2024-24419 is a buffer overflow reachable by a crafted packet that crashes the decoder — the bug class is "untrusted input drives fixed-width arithmetic past its representable range, turning every subsequent operation into a fatal error." The XOXNO Lending analog is the RAY-value ceiling in the pool's accrual path: once `borrowed * borrow_index` exceeds `i128::MAX`, `scaled_to_original` inside `accrue_step` panics with `MathOverflow`, and because every market verb accrues first via `global_sync`, the market is frozen forever — no repay, withdraw, borrow, seize, or liquidation can ever execute again.

### Finding Description
Accrual runs on every pool mutation through `interest::global_sync`, which chunks elapsed time and calls `accrue_step` [1](#0-0) . `accrue_step` computes utilization by unscaling RAY shares into value: `scaled_to_original(borrowed, borrow_index)` multiplies two RAY-scaled quantities and the intermediate `borrowed * borrow_index` must fit in `i128` [2](#0-1) . `update_borrow_index` multiplies before clamping to `MAX_BORROW_INDEX_RAY`, so the index cap does not protect the value product [3](#0-2) .

A large supplier/borrower can push `borrowed` close to the ceiling: `borrowed` is RAY-scaled, so a market holding ~1e9 whole units of an 18-decimal token is ~1e36 raw, and `i128::MAX` is only ~170× that. On the steep segment of the XLM-style kinked curve (`max_borrow_rate` up to 200% APR), `borrow_index` grows past ~170× within a few years while utilization stays pinned near 98% [4](#0-3) . The next `update_indexes` (permissionless) or any verb panics in `scaled_to_original`, and since `borrow_index` is monotone the panic recurs on every call — the market can never accrue again [5](#0-4) .

### Impact Explanation
Permanent freezing of funds: all supplied tokens, unclaimed yield, and borrower collateral tied to the debt in that market become unrecoverable; liquidation of positions holding this debt also fails, so the debt becomes unbacked bad debt that `clean_bad_debt`/`seize_positions` cannot process. The in-repo test proves `try_update_indexes`, `try_withdraw_raw`, and `try_repay` all revert with `MATH_OVERFLOW` at the cliff [6](#0-5) . Note this boundary is partially acknowledged in INV-IDX-01 ("debt-value overflow can still revert accrual"), but the permanent freeze outcome — rather than a recoverable revert — is the exploitable impact.

### Likelihood Explanation
Requires a whale-scale position in a high-decimal token (18+ decimals) plus sustained near-max utilization on a steep rate curve. On Stellar, high-supply tokens at 18 decimals make ~1e9 whole units plausible; utilization near the kink occurs naturally under borrow demand or can be maintained by the attacker borrowing. No privileged access needed: `supply` and `borrow` are permissionless (caps can be lifted only if governance set permissive caps), and time passage does the rest — any keeper's permissionless `update_indexes` triggers the freeze.

### Recommendation
Saturate rather than panic in the value-unscaling used by accrual: compute `borrowed * borrow_index` via `checked_mul`/widened math and clamp the resulting value (or clamp `borrowed`/`borrow_index` inputs) so accrual degrades gracefully instead of reverting. Alternatively, cap accrued debt value at a constant well below `i128::MAX` (analogous to `MAX_BORROW_INDEX_RAY`) and treat the excess as bad debt, and/or enforce per-market supply/borrow caps that keep `supplied * index` bounded.

### Proof of Concept
```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321
let principal = BILLION * 10i128.pow(18);          // ~1e36 raw shares
t.supply_raw(BOB, "BIG18", principal);
t.borrow_raw(ALICE, "BIG18", principal * 98 / 100); // pin utilization ~98%
loop {
    t.advance_time(YEAR_SECS);
    if t.try_update_indexes_for(&["BIG18"]).is_err() { break; } // MATH_OVERFLOW
}
// Now permanently frozen:
//   try_withdraw_raw(BOB, "BIG18", 1)  -> MATH_OVERFLOW
//   try_repay(ALICE, "BIG18", 1.0)     -> MATH_OVERFLOW
//   liquidate positions w/ BIG18 debt  -> MATH_OVERFLOW (accrual precedes every verb)
```

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

**File:** common/tests/rates/index.rs (L496-517)
```rust
#[test]
fn test_borrow_index_at_the_ceiling_multiplies_without_overflow() {
    let env = Env::default();

    // `update_borrow_index` multiplies before it clamps, so the pre-clamp
    // product at the ceiling times the largest reachable chunk factor is the
    // real overflow site. It must stay inside i128 with room to spare.
    let factor = max_chunk_growth_factor(&env, MAX_BORROW_RATE_RAY);
    let at_ceiling = Ray::from(MAX_BORROW_INDEX_RAY);

    let product = at_ceiling.mul(&env, factor);
    assert!(product.raw() > MAX_BORROW_INDEX_RAY);
    assert!(
        product.raw() < i128::MAX / 20,
        "pre-clamp headroom above the ceiling fell below 20x: {}",
        product.raw()
    );

    assert_eq!(
        update_borrow_index(&env, at_ceiling, factor).raw(),
        MAX_BORROW_INDEX_RAY,
    );
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
