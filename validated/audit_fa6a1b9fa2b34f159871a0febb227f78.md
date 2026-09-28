### Title
Accrual RAY-value overflow bricks a market before the borrow-index cap engages, permanently freezing all supplier and borrower funds - (File: common/src/rates/index.rs)

### Summary
The PDF2JSON null-deref bug class maps onto Soroban as an unchecked-arithmetic panic in a shared, accrual-first code path. In XOXNO Lending, every pool verb (`supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `update_indexes`) accrues interest before touching user state. Interest accrual multiplies the stored scaled debt by the borrow index in RAY precision (`scaled_to_original`), and that product can exceed `i128::MAX` well before the `MAX_BORROW_INDEX_RAY` index cap is reached. Once the book crosses that cliff, accrual panics with `MathOverflow` on every subsequent call, permanently. The protocol's own harness test demonstrates this: after crossing the cliff, `update_indexes`, `withdraw`, and `repay` all fail with `MathOverflow`, and the test comment states the market is frozen — "no repay, no withdraw, no liquidation". [1](#0-0) 

### Finding Description
Ray-scaled values are `scaled_amount * index` products held in `i128`. The supply/borrow index is capped at `MAX_BORROW_INDEX_RAY`, but the cap is checked on the index, not on the index-times-principal product. For a market with very large principal (high-decimals asset at high utilization on a steep rate curve), `scaled_to_original(scaled_amount, index)` overflows `i128` while `index < MAX_BORROW_INDEX_RAY` — the test observes the panic at an index of ~170x against a principal of `1e9 * 1e18`. Because accrual runs first inside `update_indexes` and every position mutation, the panic is not a per-call revert a user can avoid: the stored index only moves forward through accrual, and accrual itself is what panics. There is no admin-less or privileged escape path in scope; `recapitalize` and `clean_bad_debt` also accrue first. The result is the null-deref analog's real shape here: a single arithmetic deref of an out-of-range value crashing the shared path rather than one caller's request.



### Impact Explanation
Permanent freezing of funds. Once the product `scaled_debt * borrow_index` exceeds `i128::MAX`, every entrypoint on that hub/spoke market reverts at accrual: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and `claim_revenue`/`recapitalize` fail. All token balances held by the pool book for that market are frozen indefinitely. The test explicitly asserts `withdraw` and `repay` both fail with `MathOverflow` after the cliff. [2](#0-1) 

### Likelihood Explanation
Reachable entirely by unprivileged `supply`/`borrow` calls, but requires extreme conditions: a whale-scale position (the test uses ~`1e27` native units of an 18-decimal asset at 98% utilization) and sustained accrual on the steep segment of the interest curve — the test measured the cliff arriving in under ~40 years, with no earlier bound. Supply/borrow caps must be lifted or set very high (the test calls `lift_caps`). This is not a parameter the attacker controls; it needs a genuinely large market on a steep curve, so the practical likelihood is low but nonzero, and once triggered it is irreversible by anyone. Medium at best given the capital and time prerequisites; the freeze itself is unconditional once state crosses the threshold.

### Recommendation
Bound the overflowed quantity, not just the index. In `common/src/rates/index.rs` accrual, compute the accrued RAY value with a saturating or wide (256-bit) multiply before committing, or clamp accrual when `scaled_amount * index` would exceed `i128::MAX` and freeze interest growth at the ceiling instead of panicking. Alternatively enforce a per-market invariant `scaled_debt <= i128::MAX / MAX_BORROW_INDEX_RAY` at borrow/supply entry, so the cap on principal is derived from the index cap and the panic state is unreachable.

### Proof of Concept
The repo already contains the reproduction: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` supplies `1e9 * 1e18` of an 18-decimal asset, borrows 98%, and advances time until `try_update_indexes_for(&["BIG18"])` returns `MathOverflow` with `borrow_index < MAX_BORROW_INDEX_RAY`; subsequent `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(...)` also fail with `MathOverflow`. [3](#0-2) 

Note on scope: I verified the panic site via the harness test and the general accrual-first design, but did not read the full body of `common/src/rates/index.rs`/`scale.rs` line-by-line; the exact line of the overflowing multiply inside `scaled_to_original`/accrual should be confirmed before patching.

### Citations

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
