### Title
Unchecked borrow-index growth overflows `i128` before `MAX_BORROW_INDEX_RAY` cap engages, permanently freezing the market - ([File: common/src/rates/index.rs](common/src/rates/index.rs))

### Summary
CVE-2018-17407 is a buffer overflow: an unbounded attacker-influenced size value overflows a fixed-size container. The analog in XOXNO Lending is the millisecond-chunked borrow-index accrual in `update_borrow_index`/`scaled_to_original`: the RAY index value `debt * index` can overflow `i128` and panic with `MathOverflow` *before* the `MAX_BORROW_INDEX_RAY` cap is applied. Because every pool verb (supply, borrow, withdraw, repay, liquidate, `update_indexes`, `claim_revenue`) accrues interest first, a single panicking accrual permanently bricks the market: no repayment, no withdrawal, no liquidation can ever execute again.

### Finding Description
Interest accrual computes the new borrow index by multiplying the outstanding scaled debt by the accrued index factor. The index cap `MAX_BORROW_INDEX_RAY` is checked on the *result*, but the intermediate product `supplied/borrowed * old_index` is evaluated in `i128` (widened `I256` mul-div in `fp_core` still panics when the final quotient leaves `i128`). On a large market at sustained high utilization on a steep interest-rate curve, the accrued `index * debt` product crosses the `i128` RAY-value ceiling while the index itself is still below `MAX_BORROW_INDEX_RAY`. The repository's own harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` proves this: `try_update_indexes_for`, `try_withdraw_raw`, and `try_repay` all fail with `MATH_OVERFLOW`, and the comment states "the bound in docs/reference/formulas.md is wrong" — i.e., the documented index cap does not protect the market.

An unprivileged attacker can drive a market into this state: supply a very large position, supply collateral in a second market, borrow to ~98% utilization, and let millisecond-chunked accrual grow the index. After the cliff is crossed, every call that touches the market reverts permanently — deposited supplier funds and borrower collateral are frozen forever, and bad debt cannot be cleaned because `clean_bad_debt`/liquidation also accrues first.

### Impact Explanation
Permanent freezing of all user funds in the affected market: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and governance cannot `recapitalize` because accrual panics before any of that logic runs. This is protocol-level insolvency-by-freeze rather than a temporary DoS.

### Likelihood Explanation
Requires a whale-scale position (the PoC uses a 1e9 * 10^18-unit market at 98% utilization on the steepest curve segment) and sustained accrual over many years, so capital cost is high. However, it is fully reachable by unprivileged entrypoints (`supply`, `borrow`, `update_indexes`), is deterministic once the position exists, and is already encoded as a demonstrated behavior in the test suite. Severity: Medium (high impact, high capital/time precondition).

### Recommendation
Evaluate the index cap *before* the widening multiply that can overflow — e.g., clamp the accrued index increment so `new_index <= MAX_BORROW_INDEX_RAY` and derive the interest amount from the clamped delta, instead of computing `debt * index` at full precision. Alternatively, perform the accrual in `I256` end-to-end and saturate at the cap rather than panicking, so that a saturated market stays operable (repay/withdraw/liquidate) instead of bricking.

### Proof of Concept
From `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs` (lines ~320-360):

```rust
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);
// advance year-by-year; accrual eventually panics with MathOverflow
assert_contract_error(t.try_update_indexes_for(&["BIG18"]), MATH_OVERFLOW);
// market is permanently frozen:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), MATH_OVERFLOW);
assert!(last.borrow_index < MAX_BORROW_INDEX_RAY); // cap never engaged
```

The overflow occurs inside `scaled_to_original`/`update_borrow_index` during accrual in `contracts/pool/src/cache/scale.rs` (RAY index unscale path), which every controller/pool entrypoint calls before mutating the book — see the `mul_div` overflow path in `common/src/math/fp_core.rs` and the index growth assertion in `certora/common/spec/rates_rules.rs` noting `supplied.mul(old_index)` panics once the product leaves `i128`.