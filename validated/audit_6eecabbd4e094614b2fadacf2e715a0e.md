### Title
Permanent market freeze: accrual `scaled_to_original` overflow panics before the borrow-index cap can engage - (File: common/src/rates/scaling.rs via contracts/pool/src/interest.rs)

### Summary
The bug class of CVE-2023-21873 is a crash/hang denial of service. The analog in XOXNO Lending is a permanent, unrecoverable freeze of an entire market: once scaled debt × borrow index exceeds the `i128` RAY-value domain, every verb on that market panics inside `scaled_to_original` during mandatory upfront accrual. An unprivileged whale can drive a market into this state by supplying enormous principal and holding utilization near the steep end of the interest curve; the configured `MAX_BORROW_INDEX_RAY` cap never engages because the panic fires on the value multiplication, not on the index bound.

### Finding Description
Every pool operation accrues interest first. `global_sync` (contracts/pool/src/interest.rs:20-33) chunks elapsed time and calls `accrue_chunk` → `accrue_step` (common rates), which recomputes utilization through `scaled_to_original(borrowed, borrow_index)` — the same helper `Cache::calculate_utilization` calls at contracts/pool/src/cache/scale.rs:23-26. `scaled_to_original` multiplies a RAY-scaled share count by a RAY index and reverts with `MATH_OVERFLOW` when the product exceeds `i128::MAX`.

Because scaled debt can carry ~1e9 × 10^18 asset units (see the harness test at tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361), the value ceiling is ~170× below the index ceiling `MAX_BORROW_INDEX_RAY`. On a steep curve segment at ~98% sustained utilization the borrow index grows past 170× while still far under the cap, at which point accrual panics. The test demonstrates the consequence directly: after the cliff, `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", 1.0)` both revert with `errors::MATH_OVERFLOW` (lines 354-356), and the stored `borrow_index` is below `MAX_BORROW_INDEX_RAY` (lines 350-353), confirming the cap is dead code for this failure mode.

Since accrual is unconditional in `global_sync` before any supply/withdraw/borrow/repay/liquidate/clean_bad_debt/flash/recapitalize logic, there is no reachable path that skips the panicking multiplication — the market is permanently bricked, not merely delayed.

### Impact Explanation
Permanent freezing of funds: every supplier's tokens in that market are locked forever (withdraw, repay, liquidation, and cleanup all hit the same panic during accrual). This satisfies the "permanent freezing of funds" / "contract unable to operate" acceptance criteria.

### Likelihood Explanation
Reachable by a single unprivileged address via ordinary `supply`/`borrow`, but with real preconditions: it needs whale-scale capital (order 10^27 base units of an 18-decimal asset — feasible only for high-supply tokens), lifted or generous supply/borrow caps, and sustained near-max utilization over many years of index growth. Governance could mitigate via caps at listing time (the threat model instructs cap reviewers to account for index growth, docs/explanation/threat-model.md:317-324), but nothing in code prevents it post-listing. Overall likelihood is low, matching Medium severity.

### Recommendation
Make `scaled_to_original`/accrual saturate rather than panic, or clamp accrual when `borrowed * borrow_index` approaches the RAY value domain — e.g., enforce `MAX_BORROW_INDEX_RAY` as a clamp applied before value multiplication (set index to cap and continue), or add a debt-ceiling invariant checked at borrow time so `scaled_debt × index` cannot reach `i128::MAX`. At minimum, allow emergency exit paths (withdraw/repay) that skip accrual once the index is frozen at its cap.

### Proof of Concept
Existing in-repo reproduction: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` at tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361. It supplies `BILLION * 10^18` units of an 18-decimal asset, borrows 98% of it, advances time in yearly steps, and observes `update_indexes` fail with `MATH_OVERFLOW`; subsequent minimal `withdraw` and `repay` calls panic with the same error while `borrow_index < MAX_BORROW_INDEX_RAY`. [1](#0-0) [2](#0-1) [3](#0-2) 

Uncertainty note: whether this is dismissed as a "documented ADR choice" is a judgment call — docs/explanation/threat-model.md:317-324 acknowledges finite RAY value capacity as a cap-setting consideration, but the code path still produces an unrecoverable freeze with no owner workaround, and the in-repo test frames it as a genuine cliff rather than intended behavior.

### Citations

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
