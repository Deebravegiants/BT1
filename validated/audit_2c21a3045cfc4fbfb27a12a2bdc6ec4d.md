### Title
Sustained high-utilization accrual overflows the RAY value domain and permanently freezes the market - ([File: contracts/pool/src/cache/scale.rs])

### Summary

Like CVE-2018-7286 (an authenticated user crashes the service), a single unprivileged borrower can drive a market into a state where every subsequent call panics with `MathOverflow`, permanently freezing the market. The mechanism is the fixed-point value ceiling: total debt is stored as `borrowed * borrow_index` in RAY, and once the borrow index grows enough that `scaled_to_original` overflows `i128`, every entrypoint that accrues — which is all of them — reverts. The index cap `MAX_BORROW_INDEX_RAY` does not prevent this because the *value* (`scaled * index`) overflows before the *index* cap is reached. This is demonstrated end-to-end by the repo's own test [1](#0-0) .

### Finding Description

`Cache::calculate_utilization` unscales totals via `scaled_to_original(&env, self.borrowed, self.borrow_index)`, which calls `Ray::mul` → `fp_core::mul_div_half_up` → panics `GenericError::MathOverflow` when the product does not fit `i128` [2](#0-1) [3](#0-2) . RAY is 1e27 on `i128`, so scaled totals are capped at ~`i128::MAX / 1e27` ≈ 170 billion whole-token value; a whale supply principal near that ceiling with ~98% utilization means accrued interest compounds the debt value past the representable domain after a few years at a steep rate curve [4](#0-3) .

Every state-changing verb first calls `global_sync`, which calls `accrue_chunk`/`accrue_step` over `cache.borrowed()`/`cache.supplied()`, and utilization reads hit the same `scaled_to_original` overflow [5](#0-4) . The borrow-index ceiling check compares only the index, so `borrow_index < MAX_BORROW_INDEX_RAY` still holds when the panic fires — the cap cannot save the market [6](#0-5) .

### Impact Explanation

Once triggered, `update_indexes`, `supply`, `withdraw`, `borrow`, `repay`, `liquidate`, `clean_bad_debt`, and `recapitalize` all revert with `MathOverflow` on this market — permanently. Supplier principal and accrued yield in that pool are unrecoverable; borrowers cannot repay. This is permanent freezing of user funds and a contract unable to operate, both accepted impact classes. Severity: Medium — the condition requires a very large market and sustained extreme utilization, but once reached there is no recovery path (no governance verb can bypass accrual to socialize or recapitalize, since `recapitalize` also accrues first).

### Likelihood Explanation

An attacker needs a market whose total supplied scaled value is a substantial fraction of `i128::MAX / RAY` (~170B whole tokens) — reachable for low-price 18-decimal assets or for any asset where governance sets high caps — then borrow to high utilization (caps on borrow limit only entry size, not post-accrual growth) and wait for compounding at high utilization rates. The in-repo test achieves the freeze with a 1-billion-unit 18-decimal market at 98% utilization on the XLM-style curve within decades of ledger time; the attacker can accelerate this by supplying most of the pool themselves and repeatedly max-borrowing to keep utilization pinned high. No privileged action, oracle manipulation, or leaked keys are required — only `supply`/`borrow` and elapsed time.

### Recommendation

Make the accrual path overflow-tolerant instead of fail-closed: in `accrue_step` and `Cache::calculate_utilization`, use `mul_div_floor_saturating` (already available in `fp_core` and used by `calculate_scaled_cap`) for `borrowed * borrow_index` / `supplied * supply_index`, or clamp scaled debt growth at the RAY value ceiling and route the unbacked excess through `apply_bad_debt_to_supply_index` / `clean_bad_debt`. At minimum, allow `clean_bad_debt`/`recapitalize`/`withdraw` to skip or bound accrual when the debt value is at the ceiling so user funds remain exitable.

### Proof of Concept

Reproduced by the repo's own test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`:

1. Whale supplies ~10²⁷ raw units of an 18-decimal asset; another user supplies collateral and borrows ~98% of it (`borrow` at high utilization on the XLM curve).
2. Advance ledger time in yearly steps calling `update_indexes`; `accrue_step` compounds `borrowed * borrow_index` until `scaled_to_original` panics `MathOverflow` (error #33).
3. Subsequently `withdraw` and `repay` both revert with `MathOverflow` because every verb accrues first — the market is permanently frozen with `borrow_index < MAX_BORROW_INDEX_RAY` [7](#0-6) [8](#0-7) [9](#0-8) .

### Citations

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-362)
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

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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
