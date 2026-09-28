### Title
Ray-value i128 overflow in accrual permanently freezes a market before `MAX_BORROW_INDEX_RAY` cap engages - ([File: common/src/rates/scaling.rs])

### Summary
The assertion-failure DoS class (CVE-2016-9395: a crafted input reaches an assert that aborts processing) maps onto a permanent panic path in the interest-accrual math. `scaled_to_original` computes `scaled * index` via `Ray::mul`, which panics with `GenericError::MathOverflow` when the product exceeds `i128::MAX`. Because every pool verb accrues first, once a market's scaled debt times its borrow index crosses the `i128` ceiling — which happens strictly before the index reaches the `MAX_BORROW_INDEX_RAY` cap — every subsequent `supply`/`withdraw`/`borrow`/`repay`/`liquidate`/`update_indexes` call on that market reverts forever. Suppliers' funds and unclaimed yield are permanently frozen.

### Finding Description
`update_borrow_index` caps the index at `MAX_BORROW_INDEX_RAY`, but the cap only bounds the index, not the ray-denominated value `borrowed * new_borrow_index` computed downstream via `scaled_to_original` → `Ray::mul` → `mul_div_half_up`/`mul_div_floor`, which panic on overflow (`fp_core.rs` `to_i128`, `mul_div_half_up`). [1](#0-0) [2](#0-1) [3](#0-2) 

The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` reproduces this exactly: a ~10^27-unit (billion-scale, 18-decimal) market at 98% utilization on the XLM rate curve grows the index past ~170x, at which point `try_update_indexes_for` fails with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`. The test then confirms `try_withdraw_raw` and `try_repay` both fail with the same panic — the market is frozen. [4](#0-3) 

No privileged action is required: any unprivileged user can `supply` and `borrow` to build the position and call `update_indexes` to drive accrual; the freeze then affects all users of that market.

### Impact Explanation
Permanent freezing of funds: once the ray-value ceiling is crossed, all exits (withdraw), repayments, liquidations, and interest updates on the affected market revert deterministically. Suppliers cannot recover principal or yield, borrowers cannot repay, and bad debt cannot be liquidated or socialized — the market book is unrecoverable short of a privileged migration path (which itself calls accrue paths).

### Likelihood Explanation
Requires a very large market (ray-scaled debt value near `i128::MAX / index`, i.e. roughly `i128::MAX / RAY` base units — feasible only for high-decimal, high-supply assets) sustained at high utilization long enough for compound growth to multiply the value past the ceiling, before the index cap at `MAX_BORROW_INDEX_RAY` engages. The `supply_cap`/`borrow_cap` ceiling `max_cap_for_decimals` permits values up to `i128::MAX / 10^(27-d)`, so for low-decimal assets caps can admit ray-scaled supplies in the required range. The condition is environmental (scale + time at steep-rate utilization) but requires no privilege, no leaked keys, and no oracle manipulation — matching the Medium severity of the source CVE.

### Recommendation
Make the value computation saturating or cap-aware rather than panicking:
- In `update_borrow_index` / `calculate_supplier_rewards`, compute `new_total_debt` with `mul_div_floor_saturating` or clamp `new_borrow_index` so `borrowed * new_index` stays below `i128::MAX`, e.g. `index_max = min(MAX_BORROW_INDEX_RAY, i128::MAX * RAY / borrowed)`.
- More robustly, enforce the cap inside `Ray::mul` callers on the accrual path (a non-panicking `try_mul`/`saturating` variant for index products), so a market at the ceiling keeps operating at capped index instead of freezing.

### Proof of Concept
The in-repo regression test is a self-contained PoC (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs`):

1. Create market `BIG18` (18 decimals, XLM rate curve) and collateral market `COL`; lift caps.
2. `BOB.supply(BIG18, 1e9 * 10^18)`; `ALICE.supply(COL, ...)`; `ALICE.borrow(BIG18, 0.98 * principal)` — 98% utilization.
3. Advance time and call `controller.update_indexes` yearly. Within the modeled horizon the call fails with `Error(Contract, MATH_OVERFLOW)` while `book("BIG18").borrow_index < MAX_BORROW_INDEX_RAY`.
4. `withdraw(BOB, BIG18, 1)` and `repay(ALICE, BIG18, ...)` both fail identically — all funds permanently locked. [5](#0-4)

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

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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
