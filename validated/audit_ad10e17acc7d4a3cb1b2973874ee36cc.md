### Title
i128 RAY-value overflow during accrual permanently freezes a whale market before the borrow-index cap engages - (File: contracts/pool/src/cache/scale.rs)

### Summary
The analog of the reported buffer-overflow class (unbounded growth past a fixed storage boundary, crashing the engine) is an `i128` overflow in the pool's scaled-share arithmetic: `scaled_to_original(borrowed, borrow_index)` multiplies scaled debt shares by the borrow index as `i128` RAY math. The borrow index is capped at `MAX_BORROW_INDEX_RAY`, but on a large-decimal market the product `borrowed_scaled * index` hits the `i128::MAX` ceiling long before the index cap engages. Since interest accrual runs at the head of every pool verb, once this boundary is crossed every operation on that market reverts forever.

### Finding Description
`Cache::calculate_utilization` and the accrual path unscales scaled share counts via `scaled_to_original`, which performs `Ray` multiplication in `i128` (`common/src/math/fp.rs` wraps raw ops in checked arithmetic that panics with `GenericError::MathOverflow`). [1](#0-0) 

The borrow index grows each accrual chunk via `update_borrow_index`, which clamps the *index* at `MAX_BORROW_INDEX_RAY`. [2](#0-1)  However, the protective cap operates on the index, not on the value product `borrowed_scaled * index`. For a market with a large token supply (e.g. an 18-decimal asset with a billion-scale deposit), scaled debt is enormous, so `borrowed_scaled * borrow_index` overflows `i128` while `borrow_index` is still far below `MAX_BORROW_INDEX_RAY`. [3](#0-2) 

`global_sync` is invoked before any pool operation, and each chunk calls `accrue_step`, which internally computes `scaled_to_original` on the totals. The overflow therefore poisons the market at accrual time: `supply`, `withdraw`, `borrow`, `repay`, `liquidate`, `clean_bad_debt`, `update_indexes`, and `claim_revenue` all hit the same deterministic `MathOverflow` panic. [4](#0-3) 

The harness test demonstrates this concretely: a 18-decimal market at ~98% utilization on the steep XLM rate curve fails `try_update_indexes_for` with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, and subsequent `withdraw` and `repay` attempts fail identically. [5](#0-4) 

### Impact Explanation
Permanent freezing of funds on the affected market. Suppliers cannot withdraw, borrowers cannot repay (their collateral is locked and can never be liquidated or released), and liquidators cannot touch underwater positions. The panic is a deterministic arithmetic overflow, not a transient revert — no sequence of unprivileged or admin calls routes around it because accrual precedes every code path and `recapitalize`/`clean_bad_debt` also accrue first. The market's real token balance sits in the pool contract unclaimable.

### Likelihood Explanation
Requires a whale-scale position (billions of units on a high-decimals asset) and sustained high utilization so compound interest pushes `borrowed * index` to `i128::MAX` before the index reaches its cap. Both legs are reachable by a single unprivileged address: `controller.supply` to build the deposit and `controller.borrow` to hold utilization near the steep segment of the rate curve. After that, growth is purely passive compounding — no further attacker action, privileged call, or oracle manipulation is needed. It is capital-intensive and configuration-dependent (needs a live market whose caps permit the position size), which keeps this at Medium rather than High.

### Recommendation
- In `accrue_step`/`scaled_to_original`, detect the would-be overflow and clamp the *value* (or equivalently clamp `borrow_index` to `i128::MAX / borrowed_scaled` when `borrowed_scaled > 0`) instead of panicking, so the market degrades to a capped index rather than a permanent halt.
- Add a precondition check in `Cache::calculate_utilization` and the unscale helpers that returns a saturated value (`i128::MAX`) for the utilization/total-debt computation rather than aborting the transaction.
- As a defense-in-depth, enforce a market-level bound on `borrowed_scaled * MAX_BORROW_INDEX_RAY ≤ i128::MAX` when caps or market decimals are configured, and add a harness regression asserting the index cap engages before the value ceiling on extreme-decimal markets.

### Proof of Concept
1. On an 18-decimal market, attacker calls `controller.supply(..., amount = 1e9 * 10^18)` from a second funded account and supplies sufficient collateral to `controller.borrow` ~98% of it.
2. Time passes; each `update_indexes` call compounds `borrow_index` via `accrue_chunk`.
3. `borrowed_scaled * borrow_index` eventually exceeds `i128::MAX` inside `scaled_to_original` while `borrow_index < MAX_BORROW_INDEX_RAY`; `update_indexes` reverts with `MathOverflow` (error #33).
4. `withdraw`, `repay`, `liquidate`, and `clean_bad_debt` on that market revert identically forever — the harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` reproduces exactly this (fails at `scaled_to_original`, index cap never engages, exits and repayments panic). [6](#0-5)

### Citations

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

**File:** common/src/rates/index.rs (L13-19)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
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
