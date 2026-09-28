### Title
Permanent market freeze: i128 ray-value overflow in `scaled_to_original` during accrual bricks every verb on a whale-scale market - (File: common/src/rates/simulate.rs)

### Summary
The GPAC bug class is "crafted input → unhandled panic → denial of service". The lending analog: interest accrual unscale `borrowed * borrow_index` (and `supplied * supply_index`) through `scaled_to_original`, which panics with `GenericError::MathOverflow` when the unscaled value exceeds `i128::MAX`. The borrow-index ceiling `MAX_BORROW_INDEX_RAY` (1e36) is far too high to protect this multiplication: a market holding ~1e36 raw ray of scaled debt hits the i128 value ceiling when the index is still ~170x below the cap. Since every user-facing verb accrues the market first, the panic permanently freezes repay, withdraw, borrow, supply, and liquidation on that market. This is already demonstrated by the protocol's own horizon test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:315-356).

### Finding Description
`accrue_step` in `common/src/rates/simulate.rs:60-61` computes:
```
let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
let supplied_original = scaled_to_original(env, supplied, supply_index);
```
`scaled_to_original` is `scaled.mul(env, index)` (common/src/rates/scaling.rs:14-16), which computes `scaled * index / RAY` widened to `I256` and converts back via `to_i128`, panicking with `MathOverflow` when the result does not fit (common/src/math/fp_core.rs:300-303).

The protective clamp `MAX_BORROW_INDEX_RAY` in `update_borrow_index` only bounds the *index*; it does nothing for `scaled * index`. With a scaled book of ~1e36 raw ray (e.g. ~1 billion whole units of an 18-decimal token), the value product reaches `i128::MAX` at an index of only ~170, while the cap sits at 1e36/RAY = 1e9. The test confirms `last.borrow_index < MAX_BORROW_INDEX_RAY` at the moment of failure — "the index cap did not engage before the value overflow" (test line 350-353).

Because accrual runs at the top of every flow, once a single accrual step overflows, no subsequent call on that market can succeed: `update_indexes` itself, `repay`, `withdraw`, `liquidate`, `supply`, `borrow`, `recapitalize`, `clean_bad_debt` — all panic on the same multiplication. The test explicitly asserts `try_withdraw_raw` and `try_repay` revert with `MATH_OVERFLOW` (lines 354-356).

Attack path for a single unprivileged address:
1. `supply(caller, 0, spoke_id, [(key, very_large_amount)])` to build the scaled book — third-party top-ups are allowed on any account.
2. `borrow` to hold utilization on the steep curve segment (rate up to `MAX_BORROW_RATE_RAY` = 200% APR), keeping the index compounding.
3. `update_indexes` (permissionless) periodically to keep accrual running; alternatively let passive time advance and let anyone's next call trigger the fatal step.

Nothing in the flow bounds `scaled` or the product `scaled * index`; `calculate_scaled_cap` fails open on caps and listing-time cap validation is a governance parameter, not an invariant.

### Impact Explanation
Permanent freezing of funds: once the market's `scaled * index` crosses `i128::MAX`, every exit verb panics on accrual, so suppliers' principal and borrowers' collateral on that market are frozen forever, and liquidations cannot proceed even to socialize losses — protocol insolvency follows for any underwater debt on the frozen book.

### Likelihood Explanation
The path is permissionless but capital-heavy and time-dependent: it requires a very large scaled book (billions of whole units at high decimals) plus sustained high utilization over multiple compounding years at a steep curve segment. The harness test reaches the cliff within 40 simulated years at 98% utilization after lifting caps, and a whale or attacker funding the supply can drive the book directly rather than waiting for organic growth. Because caps are governance parameters, nothing structural prevents a large-cap market from drifting into the cliff. Severity Medium: high-impact permanent freeze, but demanding preconditions.

### Recommendation
- Make the unscale saturating or pre-check `scaled` against `i128::MAX * RAY / index` in `scaled_to_original`, returning `Ray::from(i128::MAX)` so accrual degrades (index cap engages, debt keeps its ceiling value) instead of panicking.
- Alternatively, tighten `MAX_BORROW_INDEX_RAY`/`MAX_SUPPLY_INDEX_RAY` per-market so that `market_scaled * cap` provably stays under `i128::MAX`, and enforce `scaled <= i128::MAX * RAY / MAX_INDEX` at deposit time in `process_deposit`/`mint_debt`.
- Enforce supply/borrow caps as hard storage bounds (not just listing-time validation) that keep `scaled` under the overflow threshold for any permitted index.

### Proof of Concept
Already encoded in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356`:

```rust
let principal = BILLION * 10i128.pow(18);          // 1e36 raw ray book
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;                   // ~98% utilization
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

loop {
    t.advance_time(YEAR_SECS);                     // permissionless accrual steps
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; }
}
// -> MathOverflow inside scaled_to_original during accrue_step
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

The index at failure is below `MAX_BORROW_INDEX_RAY`, proving the value ceiling — not the index cap — is the binding constraint, and the freeze is permanent because every subsequent verb re-triggers the same overflow in `accrue_step`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** common/src/rates/simulate.rs (L51-64)
```rust
pub fn accrue_step(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    supplied: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    delta_ms: u64,
) -> AccrualStep {
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp_core.rs (L298-303)
```rust
/// Converts an `I256` to `i128`, panicking with `GenericError::MathOverflow` if it does not
/// fit.
fn to_i128(env: &Env, val: &I256) -> i128 {
    val.to_i128()
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-356)
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
