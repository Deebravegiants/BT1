### Title
Interest accrual overflow panics every subsequent market verb, permanently freezing all supplier funds in a high-decimal whale market - (File: contracts/pool/src/cache/scale.rs)

### Summary
The bug class in CVE-2019-25014 is a user-reachable runtime panic that turns into a persistent denial of service. The analog in XOXNO Lending is the RAY-value ceiling in pool accrual: once a market's RAY-denominated book value grows large enough, the next index update panics inside `scaled_to_original` with `MathOverflow` before the borrow-index cap can engage. Because every permissionless and user verb (`supply`, `withdraw`, `repay`, `borrow`, `liquidate`, `clean_bad_debt`, `update_indexes`) accrues the market first, the panic bricks the entire market: no exits, no repayments, no liquidations, forever.

### Finding Description
Accrual converts scaled RAY balances back to asset values via `scaled_to_original` (a `mul_div` over RAY). The math layer in `common/src/math/fp_core.rs` panics with `GenericError::MathOverflow` whenever the unscaled value cannot be represented in `i128` [1](#0-0) . There is a documented index cap (`MAX_BORROW_INDEX_RAY`), but the value overflow trips first: the index grows toward ~170x while the product `scaled * index / RAY` already exceeds `i128::MAX`, so the protective cap never engages [2](#0-1) .

The repository's own harness proves this end to end: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` builds an 18-decimal market with a billion-unit supply at ~98% utilization on the XLM rate curve, advances time, and observes `update_indexes` revert with `MATH_OVERFLOW`. After that point both `withdraw` and `repay` revert with the same error, since they accrue first [3](#0-2) . The test comment states the market is frozen — "no repay, no withdraw, no liquidation" — and that the bound asserted in `docs/reference/formulas.md` is wrong, i.e., the safety bound claimed in the documentation does not actually protect this path.

### Impact Explanation
Permanent freezing of user funds and protocol insolvency on the affected market. All suppliers' principal and accrued yield become unrecoverable because `withdraw` panics on every attempt; borrowers cannot `repay`, so their collateral in other legs cannot be released through normal flows; liquidations and `clean_bad_debt` also panic, so positions decay into unresolvable bad debt. Only governance intervention (e.g., an upgrade or parameter change that alters the accrual path) could recover the market, and nothing in the unprivileged surface can.

### Likelihood Explanation
Medium. It requires an extreme but reachable configuration: a high-decimal asset, whale-scale balances, and sustained near-max utilization over a long horizon (the harness reaches the cliff within the test's 40-year bound). Every step uses permissionless entrypoints — `supply`, `borrow`, `update_indexes` — and governance-admitted market parameters; no privileged or leaked-key precondition is needed beyond an aggressively parameterized market existing. The threat model already acknowledges "bounded indexes and chunks coexist with cadence and value-overflow risks" [4](#0-3) , indicating the risk is known but unmitigated in code.

### Recommendation
Guard the accrual unscaling with the checked `try_mul_div_*`/`saturating` variants instead of the panicking `mul_div` path: when `scaled * index / RAY` would overflow, either engage the index cap by clamping the index before unscaling, or fail the accrual into a partial-accrual mode that still permits repayments and withdrawals. Additionally, enforce the claimed bound from `docs/reference/formulas.md` at market creation (reject decimal/balance-domain combinations whose RAY ceiling is reachable within the cap) and add a regression test asserting repay/withdraw still succeed at the boundary.

### Proof of Concept
The in-repo test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs` is the executable PoC [5](#0-4) :

1. Create a market for an 18-decimal asset with the XLM rate curve and no max-utilization clamp; create a second collateral market.
2. `supply` ~10^9 whole units of the high-decimal asset (permissionless).
3. `supply` collateral on a second account and `borrow` ~98% of the whale market (permissionless).
4. Advance ledger time in yearly steps calling `update_indexes` until it reverts with `Error(Contract, MathOverflow)` — observed before `MAX_BORROW_INDEX_RAY` engages.
5. From then on, `withdraw(1 unit)` and `repay` both revert with `MATH_OVERFLOW` because they accrue first; the market is permanently bricked for every user.

### Citations

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

**File:** docs/explanation/threat-model.md (L352-352)
```markdown
| Tamper.6 | Accrual manipulation/extremes; bounded indexes and chunks coexist with cadence and value-overflow risks. |
```
