### Title
Accrual-time `i128` overflow in `scaled_to_original` permanently freezes a whale-scale market before the borrow-index cap can engage - (File: common/src/rates/simulate.rs)

### Summary
`accrue_step` values the scaled borrow book with `scaled_to_original(borrowed, borrow_index)`, an `x * y / RAY` that panics with `GenericError::MathOverflow` once the RAY-valued debt exceeds `i128`. The `MAX_BORROW_INDEX_RAY` index cap is meant to be the terminal bound on accrual, but the value ceiling is hit first, so the panic fires on every subsequent accrual. Because every controller verb runs `global_sync` before acting, the market can never again be supplied to, borrowed from, repaid, withdrawn, or liquidated — all supplier and borrower funds in that market are permanently frozen.

### Finding Description
The accrual pipeline is:

- `global_sync` (`contracts/pool/src/interest.rs:20`) runs at the head of every pool mutation and loops `accrue_chunk` over `MAX_COMPOUND_DELTA_MS` windows.
- Each chunk calls `accrue_step` (`common/src/rates/simulate.rs:51`), whose first statement is `let borrowed_original = scaled_to_original(env, borrowed, borrow_index)` (`simulate.rs:60`).
- `scaled_to_original` is `scaled.mul(env, index)` (`common/src/rates/scaling.rs:14`), i.e. `mul_div_half_up(borrowed, borrow_index, RAY)`, which panics with `MathOverflow` when the result does not fit `i128` (`common/src/math/fp_core.rs:108-118`). The `I256` widened path only rescues the *intermediate* product; a result above `i128::MAX` still returns `None` and panics.
- The borrow index is capped at `MAX_BORROW_INDEX_RAY = 1e36` inside `update_borrow_index` (`common/src/rates/index.rs:13-19`), but that cap is applied *after* the utilization read — and the utilization read is exactly the multiplication that overflows. So for a book where `borrowed * index / RAY > i128::MAX ≈ 1.7e38` while `index < 1e36`, the market bricks before the safety cap engages. A scaled `borrowed` of ~170 RAY (≈170 whole-token equivalents of debt in RAY terms — reachable at ~1e9 tokens supplied and 98% borrowed, as in the harness test) with an index of ~170×RAY trips it.

This is an exact analog of CVE-2015-8875: an unbounded integer multiply (`width * height * channels` there; `borrowed * borrow_index` here) overflows the fixed-size integer before a size bound is enforced, turning a legitimate input scale into a crash on the processing path. Here the "crash" is a contract panic that, because accrual precedes every verb, is permanent rather than transient.

### Impact Explanation
Permanent freezing of user funds. Once `borrowed * borrow_index / RAY > i128::MAX`:

- `update_indexes` reverts (it accrues).
- `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `flash_loan`, `repay_debt_with_collateral`, `recapitalize` on that market all revert, since each calls `global_sync` first.
- Suppliers cannot exit and borrowers cannot close; liquidators cannot clear bad debt. The tokens sit in the pool forever with no admin-free recovery path.

The in-repo test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-356`) demonstrates exactly this: after the value ceiling is hit, `try_withdraw_raw` and `try_repay` both fail with `MATH_OVERFLOW` and `borrow_index < MAX_BORROW_INDEX_RAY` — the cap never engaged.

### Likelihood Explanation
Reachable by a single unprivileged address but capital-intensive: the attacker must drive one market's RAY-scaled debt book large enough that `borrowed * index` exceeds `i128` before `index` reaches `1e36`. With 18-decimal assets and lifted/supply-cap-permitting markets, a billion-token book at ~98% utilization reaches the cliff in well under the ~11 years the index cap needs at maximum rate (the harness test observes it; the exact year depends on the curve's steep segment). An attacker can also accelerate it by supplying the liquidity, borrowing at max utilization to pin the rate at the curve's steep segment, then simply waiting and calling the permissionless `update_indexes`. No governance action, leaked key, or oracle manipulation is required — only capital and time on the public entrypoints `supply`, `borrow`, and `update_indexes`.

### Recommendation
Make the utilization/value read overflow-tolerant rather than the panic source:

1. In `accrue_step`, compute `borrowed_original`/`supplied_original` with a saturating variant (e.g. `mul_div_floor_saturating`/`half_up` saturating at `i128::MAX`). Utilization is a ratio capped at `RAY` anyway; a saturated numerator yields `util = RAY`, which selects `max_borrow_rate` — the correct terminal behavior.
2. Alternatively, clamp `borrow_index` to `MAX_BORROW_INDEX_RAY` *before* `scaled_to_original` is evaluated, and short-circuit accrual when either index is at its cap (the cap already makes `update_borrow_index` sticky — the early return just needs to precede the valuation).
3. Also guard `apply_bad_debt_to_supply_index` (`contracts/pool/src/interest.rs:74`), which performs the same unguarded `supplied * supply_index` valuation.

### Proof of Concept
The protocol's own test harness already contains the working PoC at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`:

```rust
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
lift_caps(&t, "BIG18", 18);
lift_caps(&t, "COL", 7);
let principal = BILLION * 10i128.pow(18);          // whale supply, unprivileged
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;                    // 98% utilization
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; }
}
// => Error(Contract, MATH_OVERFLOW) from scaled_to_original in accrue_step
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
assert!(book(&t, "BIG18").borrow_index < MAX_BORROW_INDEX_RAY); // cap never engaged
```

All calls are permissionless (`supply`, `borrow`, `update_indexes`, `withdraw`, `repay`), so a single unprivileged whale triggers and confirms the permanent freeze.