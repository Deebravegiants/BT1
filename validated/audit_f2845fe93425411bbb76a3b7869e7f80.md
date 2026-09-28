### Title
i128 overflow in borrow-debt accrual permanently freezes a saturated high-utilization market — ([File: common/src/rates/index.rs])

### Summary

CVE-2016-9426 is an integer-overflow-to-DoS/code-exec bug: an intermediate product (`rows * cols` in `renderTable`) overflows before allocation, corrupting downstream logic. The analog in XOXNO Lending is the `borrowed × borrow_index` value computation inside index accrual: `calculate_supplier_rewards` multiplies total scaled debt by the new borrow index in `i128`, and once that product exceeds `i128::MAX` the call panics with `GenericError::MathOverflow`. Every user-facing pool verb runs `global_sync` (accrual) first, so once a market crosses this value ceiling, `update_indexes`, `repay`, `withdraw`, `borrow`, `supply`, `liquidate`, `clean_bad_debt`, and all controller strategies permanently revert on that market — user funds are frozen forever. The `MAX_BORROW_INDEX_RAY` cap does not protect: the overflow is in the *value* product, not the index, and is reached before the index cap when total debt is large.

### Finding Description

Accrual runs on every mutation. `global_sync` in `contracts/pool/src/interest.rs:20-33` calls `accrue_step` (`common/src/rates/simulate.rs`), which calls `update_borrow_index` (`common/src/rates/index.rs:13-19`) and then `calculate_supplier_rewards` (`common/src/rates/index.rs:73-89`). The latter computes:

```rust
let old_total_debt = borrowed.mul(env, old_borrow_index);
let new_total_debt = borrowed.mul(env, new_borrow_index);
```

`Ray::mul` is `mul_div_half_up(x, y, RAY)`, which widens to `I256` only for the *intermediate* product — the final result must still fit `i128` or `try_mul_div_half_up` returns `None` and `mul_div_half_up` panics with `MathOverflow` (`common/src/math/fp_core.rs:108-118`). `borrowed` is the market's total scaled debt (RAY shares); with large `borrowed`, `borrowed × new_index / RAY` exceeds `i128::MAX ≈ 1.7e38` while `new_index` is still far below `MAX_BORROW_INDEX_RAY = 1e36`. `docs/reference/formulas.md:434-437` concedes this: "Value overflow can occur before the index ceiling and block repayment/withdrawal because those operations accrue first. No dedicated ceiling alarm is emitted."

The caps do not prevent an attacker from sizing the market into this regime. A cap is admitted up to `i128::MAX / 10^(27-d)` token units ≈ 170 billion whole tokens (`formulas.md:429`), and `calculate_scaled_cap` *saturates* rather than rejects on the scaled conversion (`scaling.rs:26-33`), so the scaled-usage comparison fails open. The pool's own harness test proves the end state: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361` seeds a 1e9-token market at 98% utilization, advances years, and observes `MATH_OVERFLOW` from `update_indexes`, after which `withdraw` and `repay` both fail with the same panic while `borrow_index < MAX_BORROW_INDEX_RAY` — "The market is frozen: exits and repayments accrue first and hit the same panic."

Reachability for a single unprivileged address: `controller.supply(token, amount)` up to the admitted cap, `controller.borrow` near full utilization using a second supplied asset as collateral, then either wait for accrual at the steep end of the interest curve or periodically call `pool.update_indexes` (permissionless) so each chunk accrues. Once `scaled_debt × borrow_index / RAY > i128::MAX`, no further accrual-bearing call on that market can succeed, including `clean_bad_debt` and `recapitalize`, which also sync first.

### Impact Explanation

Permanent freezing of all supplier and collateral funds in the affected market (and bad debt that can never be liquidated or written down), plus protocol insolvency on the borrower's remaining debt — an accepted "permanent freezing of funds / protocol insolvency" impact. Unlike a transient fail-closed revert, this trap is unrecoverable: there is no privileged escape hatch in the panic path, and no non-accruing entrypoint exists to unwind positions.

### Likelihood Explanation

High on any market whose admitted cap approaches the representable-balance ceiling and whose rate curve produces high sustained utilization (the XLM-family curve reaches the cliff in ~a few years per the harness test; faster at 175%+ APR segments). The attacker needs capital up to the market cap, but the bug requires no privileged role, no oracle manipulation, and only standard `supply`/`borrow`/`update_indexes` calls. The attacker's own deposit is also frozen, so this is a griefing/insolvency vector rather than theft — economically motivated when the attacker is short the market or holds the debt side to force socialization deadlock.

### Recommendation

Cap total scaled debt so that `borrowed × MAX_BORROW_INDEX_RAY / RAY` can never overflow `i128` — i.e. enforce `scaled_borrowed ≤ i128::MAX / MAX_BORROW_INDEX_RAY` (≈ 1.7e11 RAY-scaled units) at borrow mint time in `calculate_scaled_borrow`/cap admission, rather than relying on the index ceiling. Alternatively, clamp the accrual in `calculate_supplier_rewards`/`update_borrow_index` so that once the value product would overflow, the borrow index is pinned at `MAX_BORROW_INDEX_RAY` and interest accrual is skipped (the cap semantics already imply zero further accrual), keeping `repay`/`withdraw`/`liquidate` operable. A documented "cliff" is not a mitigation since no verb can execute past it.

### Proof of Concept

```rust
// Mirrors tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
lift_caps(&t, "BIG18", 18);          // admit cap up to ~i128::MAX / 10^(27-18) tokens
lift_caps(&t, "COL", 7);

let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);          // attacker-sized supply
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // 98% utilization

loop {
    t.advance_time(YEAR_SECS);
    if t.try_update_indexes_for(&["BIG18"]).is_err() { break; }
}
// borrowed * borrow_index / RAY > i128::MAX while borrow_index < MAX_BORROW_INDEX_RAY.
// From here on, ALL of these revert with MathOverflow forever:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
// liquidate / clean_bad_debt / recapitalize / borrow / supply revert identically,
// because global_sync -> accrue_step -> calculate_supplier_rewards panics first.
```