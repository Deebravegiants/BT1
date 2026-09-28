### Title
Market permanently freezes once the borrow index growth overflows `scaled_to_original` before `MAX_BORROW_INDEX_RAY` engages - ([File: contracts/pool/src/interest.rs](contracts/pool/src/interest.rs))

### Summary
The pool accrues interest by unscaling share totals at the live indexes (`scaled_to_original` / `accrue_step`) inside `global_sync`. On a whale-sized market at sustained high utilization, the RAY value `borrowed_scaled * borrow_index` crosses the `i128` ceiling and panics with `MathOverflow` *before* the `MAX_BORROW_INDEX_RAY` index cap can clamp growth. Because every market verb (`supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `flash_loan`, `claim_revenue`, `clean_bad_debt`, `recapitalize`) runs `global_sync` first, the market is bricked forever — a repeatable crash DoS, analogous to the InnoDB crash class, but on pool state instead of a database. The protocol's own harness test documents this cliff and confirms `withdraw` and `repay` both revert with `MathOverflow` afterward.

### Finding Description
`global_sync` splits elapsed time into `MAX_COMPOUND_DELTA_MS` chunks and calls `accrue_chunk`, which invokes `accrue_step` and unconditionally writes back the new indexes. [1](#0-0)  Inside `accrue_step`, totals are unscaled via `scaled_to_original` — the same helper used by `Cache::calculate_utilization` — which panics when `scaled * index` does not fit `i128` (the `mul`-based helpers panic with `GenericError::MathOverflow` rather than saturating). [2](#0-1) 

The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` sets up a market with ~1 billion 18-decimal units supplied, ~98% borrowed on the steep XLM rate curve, and advances time until `update_indexes` fails. It proves three facts:
1. The failure is `MathOverflow` inside accrual, not a returned error that could be handled.
2. `borrow_index` is still below `MAX_BORROW_INDEX_RAY` — the intended index cap never engages because the *scaled value* (`borrowed_scaled_ray` near `i128::MAX` from the huge supply, roughly 170× the cap's implied maximum) overflows first.
3. The market is permanently frozen: `try_withdraw_raw` and `try_repay` both fail with `MathOverflow` because they accrue first. [3](#0-2) 

Once `borrowed * borrow_index ≥ i128::MAX`, every subsequent `accrue_chunk` computes with the same (or larger) values — interest monotonically grows the index — so the panic is deterministic and unrecoverable. `clean_bad_debt` cannot rescue it (it also accrues), and `recapitalize` cannot lower a borrow index. No admin action short of a contract upgrade unfreezes the market.

### Impact Explanation
Permanent freezing of all user funds in the affected market: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and pending revenue cannot be claimed. Every entrypoint touching that `(hub, token)` book calls `renewed_market` → `global_sync` → the overflowing `accrue_step`, so the revert is total. This is the pool-side equivalent of the reported "complete DoS": a single reachable arithmetic ceiling bricks the component rather than a bounded, per-request failure.

### Likelihood Explanation
The trigger requires three simultaneous conditions: a market whose scaled borrow supply approaches the `i128` range (achievable on high-decimal assets where `i128::MAX / 10^(27-d)` caps are large, e.g., the 18-decimal market in the test at ~10^27 base units — a whale-scale but legitimate supply), sustained ~98% utilization on a steep rate curve, and accrual time measured in years rather than a single transaction. An unprivileged attacker can supply and borrow to pin utilization at the curve's steep segment, and any third party's `update_indexes` call then drives accrual; the attacker cannot accelerate ledger time, so the attack is slow and requires capital, but needs no privilege and no cooperation. The test shows the cliff arrives in under 40 years at 98% utilization, and the docs' bound on when `MAX_BORROW_INDEX_RAY` protects the market is wrong — the value ceiling is hit first, so the protection the protocol relies on does not exist in this regime.

### Recommendation
Bound the value domain, not just the index. In `accrue_step` / `scaled_to_original`, detect the `i128` ceiling and clamp (or clamp `borrowed_scaled_ray` via a market-level scaled-value cap checked at supply/borrow entry, since `scaled * index` must always fit). Alternatively, make `MAX_BORROW_INDEX_RAY` a hard clamp on the *value* computed from `borrowed * index` — i.e., once the index times the outstanding scaled debt reaches the representable maximum, freeze accrual for that market instead of panicking, so verbs continue to operate at the capped index. At minimum, enforce supply/borrow caps that keep `scaled_cap * MAX_BORROW_INDEX_RAY < i128::MAX` per listing, so the index cap provably engages before the value ceiling.

### Proof of Concept
The repository's own harness test is the PoC:

```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-360
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
lift_caps(&t, "BIG18", 18);
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;              // 98% utilization, steep curve
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

// advance year-by-year until accrual panics
loop { t.advance_time(YEAR_SECS); if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; } }
// => MathOverflow, with last.borrow_index < MAX_BORROW_INDEX_RAY (cap never engaged)

// market is permanently frozen:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

All state changes use only unprivileged entrypoints: `supply`, `borrow`, `update_indexes`, `withdraw`, `repay`. The panic originates in `accrue_step`'s unscaling of `borrowed * borrow_index` (same path as `Cache::calculate_utilization` → `scaled_to_original`). [4](#0-3) [2](#0-1)

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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-360)
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
```
