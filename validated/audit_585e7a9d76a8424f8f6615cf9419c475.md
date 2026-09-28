### Title
Permanent market freeze: `borrowed × borrow_index` overflows `i128` before the index cap engages, bricking repay/withdraw/liquidate — ([File: common/src/rates/index.rs](common/src/rates/index.rs))

### Summary
`accrue_step` computes accrued interest as `borrowed.mul(new_index) − borrowed.mul(old_index)`. `Ray::mul` is `x * y / RAY` that widens to `I256` only for the intermediate product; the *result* must still fit `i128`. For a market whose total debt value (`borrowed × index / RAY`) approaches `i128::MAX`, the subtraction's operands panic with `MathOverflow` — and this panic fires before `update_borrow_index`'s `MAX_BORROW_INDEX_RAY` cap can halt index growth. Since `global_sync` accrues on every mutating verb, the market freezes permanently. The protocol's own test harness demonstrates this exact cliff.

### Finding Description
Every pool mutator runs `global_sync` → `accrue_chunk` → `accrue_step`, which calls `calculate_supplier_rewards`, where `borrowed.mul(env, new_borrow_index)` and `borrowed.mul(env, old_borrow_index)` panic with `MathOverflow` when the RAY-denominated total debt value exceeds `i128::MAX` (~1.7e38, i.e. ~1.7e11 RAY-scaled value units — about 170 billion tokens at 18 decimals). [1](#0-0)  The borrow index is only capped *after* this multiplication, at `MAX_BORROW_INDEX_RAY`, so large books hit the value ceiling first — index growth never stops, it just becomes unreachable. [2](#0-1)  An unprivileged attacker can seed the condition entirely with in-scope verbs: `supply` a whale-scale position in an 18-decimal asset, `borrow` ~98% of it against collateral in another market, then drive accrual via the permissionless `update_indexes`. The repo's own test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` proves the outcome: after the cliff, `try_update_indexes_for`, `try_withdraw_raw`, and `try_repay` all revert with `MATH_OVERFLOW`, and `borrow_index < MAX_BORROW_INDEX_RAY` confirms the cap never engaged. [3](#0-2)  `compound_interest` already widens the exponent to `I256` but truncates the scaled rate back into `i128` for the Taylor terms, so there is no second unbounded-multiplication defense upstream. [4](#0-3) 

### Impact Explanation
Permanent freezing of funds for an entire market book: once the debt RAY-value crosses the ceiling, every verb on that market — `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `flash_loan`, `supply`, `borrow` — reverts in accrual before touching state. Suppliers' deposits, the bad-debt/recapitalization path, and unclaimed protocol revenue on that book are all unreachable. `update_indexes` is permissionless, so the final push over the cliff needs no privilege.

### Likelihood Explanation
Requires a genuinely whale-scale market (≳1e11 whole-token debt value at 18 decimals, or proportionally less at lower index multipliers) sustained at high utilization for multiple years — the test reaches the cliff inside 40 years at 98% utilization on the steep XLM curve. The attacker must lock enormous capital as supplier liquidity, but any user can trigger the fatal accrual once the book drifts near the bound, and no governance action can rescue it since rescue verbs also accrue first. Capital and time requirements make this Medium rather than High.

### Recommendation
Enforce a debt/supply *value* ceiling independent of the index cap: in `accrue_step`, clamp `borrow_index` growth so `borrowed × new_index / RAY` cannot exceed a safe bound (e.g. `i128::MAX / 4`), or short-circuit accrual when `borrowed > i128::MAX / index`. A cheaper partial fix is ordering `update_borrow_index` such that the product overflow saturates to `MAX_BORROW_INDEX_RAY` instead of panicking, plus a `require_*` guard at `supply`/`borrow` bounding `scaled × index` so the cliff is never approachable through normal deposits.

### Proof of Concept
1. Attacker supplies `10^9 × 10^18` base units of an 18-decimal asset via `supply`; supplies collateral in a second market and calls `borrow` for ~98% of it (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:329-333`).
2. Time advances (or `update_indexes` is called repeatedly); borrow index compounds while `borrowed × index / RAY` grows toward `i128::MAX`.
3. The first accrual where `borrowed.mul(new_borrow_index)` exceeds `i128::MAX` panics in `calculate_supplier_rewards` (index.rs:80-83) with `MathOverflow` — verified at `:343-348`.
4. `borrow_index` is still below `MAX_BORROW_INDEX_RAY` (`:350-353`), and subsequent `withdraw`/`repay`/`update_indexes` all revert (`:355-356`): the market is permanently frozen.

### Citations

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

**File:** common/src/rates/index.rs (L80-83)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
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

**File:** common/src/rates/compound.rs (L36-48)
```rust
    let x = Ray::from({
        let r = I256::from_i128(env, rate.raw());
        let d = I256::from_i128(env, delta_ms as i128);
        r.mul(&d)
            .to_i128()
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
    });

    let mut sum = Ray::ONE.checked_add(env, x);
    let mut pow = x;
    for divisor in [2, 6, 24, 120, 720, 5_040, 40_320] {
        pow = pow.mul(env, x);
        sum = sum.checked_add(env, pow.div_by_int(env, divisor));
```
