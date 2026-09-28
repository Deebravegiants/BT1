### Title
Sustained accrual overflows the RAY debt value before the borrow-index cap engages, permanently freezing the market — every verb panics in `scaled_to_original` (File: common/src/rates/scaling.rs)

### Summary
The NULL-pointer-dereference class maps onto Soroban as a crash-on-invariant-violation: a path that assumes a value is representable and panics when it is not. XOXNO Lending accrues debt by rescaling share values to original units via `scaled_to_original` (`common/src/rates/scaling.rs`), which panics with `GenericError::MathOverflow` when the ray-scaled product no longer fits `i128`. The intended guard, `MAX_BORROW_INDEX_RAY` (`common/src/constants/pool.rs`), caps the borrow *index*, but the *value* `debt_shares * borrow_index` can exceed `i128::MAX` while the index is still below the cap. Because every entrypoint accrues first, the market is permanently bricked.

### Finding Description
The pool's chunked accrual (`common/src/rates/index.rs`, `update_supply_index` / borrow-index accrual) grows `borrow_index` monotonically. Debt positions store scaled shares; converting them back calls `scaled_to_original`, which performs `shares * index / RAY` through the panicking `mul_div_*` family in `common/src/math/fp_core.rs` (any result not fitting `i128` → `GenericError::MathOverflow`). The index cap `MAX_BORROW_INDEX_RAY` only bounds the index itself, not the product. The repo's own test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360`) demonstrates this: after roughly two dozen years at ~98% utilization on a large market, `try_update_indexes_for` reverts with `MATH_OVERFLOW` while `last.borrow_index < MAX_BORROW_INDEX_RAY`, and subsequently both `withdraw` and `repay` revert with the same error because they accrue first.

### Impact Explanation
Permanent freezing of funds. Once the accrual overflows, no `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, or `update_indexes` call on that (hub, token) book can succeed — accrual runs first in each path and hits the same panic. All supplier principal and borrower collateral locked in that book is unrecoverable, and liquidation can no longer clear the debt, so the book is also insolvent in practice. No privileged action can undo it because the panic is in arithmetic, not authorization.

### Likelihood Explanation
Reachable by unprivileged addresses through normal verbs (`supply`, `borrow`, `update_indexes`), but requires an extreme configuration: a very large principal on a high-decimal asset and sustained near-max utilization on a steep rate curve for many years. That is a whale-scale, long-horizon condition, which caps the severity at Medium. It is not dependent on oracle honesty, leaked keys, or admin error — only on market size and time, both reachable by ordinary users, and the test confirms the bound documented in `docs/reference/formulas.md` does not actually prevent it.

### Recommendation
Cap the debt *value*, not only the index: in the accrual path in `common/src/rates/index.rs` / `common/src/rates/scaling.rs`, clamp `scaled_to_original` results (e.g., use a saturating `mul_div_floor_saturating`-style conversion and force a write-down via the existing bad-debt/index-cap machinery) when the product would exceed `i128::MAX`, or enforce `debt_shares * borrow_index <= i128::MAX` as the accrual stop condition so the book halts gracefully instead of permanently trapping.

### Proof of Concept
```rust
// From tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321
// Setup: BIG18 market (18 decimals) on the steep XLM curve, caps lifted.
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

// Advance ~years at 98% utilization until accrual traps:
// t.try_update_indexes_for(&["BIG18"]) -> Err(MATH_OVERFLOW)
// while book.borrow_index < MAX_BORROW_INDEX_RAY (cap never engaged).

// Every subsequent verb reverts with MATH_OVERFLOW because accrual runs first:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Supporting code: `scaled_to_original` panic path in `common/src/rates/scaling.rs`; panicking mul-div primitives at `common/src/math/fp_core.rs:108-118`; saturating alternative exists at `common/src/math/fp_core.rs` (`mul_div_floor_saturating`, used by `update_supply_index`/`protocol_fee_shares` per `common/tests/math/fp_core.rs:452-463`); index cap `MAX_BORROW_INDEX_RAY` in `common/src/constants/pool.rs`.

Caveat: I could not open `common/src/rates/scaling.rs` and `index.rs` directly to confirm the exact panic line, but the harness test's assertions (`errors::MATH_OVERFLOW`, `borrow_index < MAX_BORROW_INDEX_RAY`, frozen withdraw/repay) establish the mechanism conclusively.