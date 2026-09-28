### Title
Accrual debt-valuation overflow permanently freezes a large market before the borrow-index cap can engage - (File: common/src/rates/index.rs)

### Summary
CVE-2021-46543 is a crash (SEGV) in Cesanta MJS reachable from user input, yielding denial of service. The analog in XOXNO Lending is a reachable arithmetic panic in the interest-accrual path: once a market's `borrowed * borrow_index` value exceeds `i128::MAX`, `Ray::mul` panics inside `accrue_step`, and because every market entrypoint runs `global_sync` before mutating, the market becomes permanently unresponsive — no `repay`, `withdraw`, `borrow`, `seize_positions`, or `update_indexes` ever completes again, freezing all supplier and borrower funds in that market.

### Finding Description
`global_sync` in `contracts/pool/src/interest.rs` accrues in chunks of `MAX_COMPOUND_DELTA_MS` and calls `accrue_chunk` → `accrue_step`, which internally computes `borrowed.mul(env, new_borrow_index)` and `borrowed.mul(env, old_borrow_index)` in `calculate_supplier_rewards` (`common/src/rates/index.rs:80-86`). `Ray::mul` routes to `mul_div_half_up`, which panics with `GenericError::MathOverflow` when `borrowed * index` does not fit in `i128` (`common/src/math/fp_core.rs:108-118`, `common/src/math/fp.rs:50-52`).

The mitigation `update_borrow_index` caps the index at `MAX_BORROW_INDEX_RAY` (`common/src/rates/index.rs:13-19`), but the cap applies to the *index*, while the overflow happens on the *value* `borrowed * index` computed inside the same step — for a large enough book the value crosses the `i128` ceiling while the index is still far below its cap. The test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates exactly this: after the index grows ~170x, `update_indexes` fails with `MathOverflow`, and subsequent `withdraw` and `repay` calls fail identically because they accrue first — "the market is frozen: exits and repayments accrue first and hit the same panic." [1](#0-0) [2](#0-1) [3](#0-2) 

Once the first accrual overflows, there is no recovery path: `repay`/`borrow`/`withdraw`/`seize_positions`/`claim_revenue`/`update_indexes` all load the `Cache` and call `global_sync` before any debt-burning mutation, so the panic precedes the only operations that could reduce `borrowed`. Debt keeps being owed but can never be repaid; supplied funds can never exit; liquidation is impossible.

### Impact Explanation
Permanent freezing of all funds in the affected `(hub, token)` market — an accepted impact class. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot seize, and `clean_bad_debt`/`recapitalize` (which also touch the market through accrual-backed paths) cannot rescue it. The condition is irreversible once reached.

### Likelihood Explanation
Medium. The trigger requires no privilege — only `supply` and `borrow` plus time — but it needs a whale-scale book (`borrowed` RAY value approaching `i128::MAX`, roughly ≥10^11 whole units at 18 decimals) at sustained near-max utilization over many accrual years so the index grows ~170x before hitting `MAX_BORROW_INDEX_RAY`. It also requires caps configured high enough to admit that principal, which depends on governance parameters rather than a code barrier. On a high-decimal, large-supply asset market with lifted caps this is a real, reachable state rather than a theoretical bound.

### Recommendation
Make accrual debt valuation saturate or clamp instead of panicking: in `calculate_supplier_rewards`, use `mul_div_floor_saturating`/a saturating `Ray::mul` so `new_total_debt` saturates to `i128::MAX` rather than reverting, or engage `MAX_BORROW_INDEX_RAY` on the *value* bound (`borrowed * index` ≤ some ceiling) before the multiply. Alternatively, cap index growth per chunk so the product `borrowed * new_index` provably stays below `i128::MAX` given a documented maximum `borrowed` enforced at `borrow`/`create_market` time.

### Proof of Concept
See `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360`: supply ~10^9 × 10^18 units of an 18-decimal asset, borrow 98% of it on the steep XLM curve, then advance time yearly; `update_indexes` eventually panics with `MathOverflow` inside `scaled_to_original`/debt valuation while `borrow_index < MAX_BORROW_INDEX_RAY`, after which `try_withdraw_raw` and `try_repay` both revert with the same error — the market is permanently frozen. [4](#0-3)

### Citations

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

**File:** contracts/pool/src/interest.rs (L20-33)
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
```

**File:** common/src/rates/index.rs (L80-86)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
```
