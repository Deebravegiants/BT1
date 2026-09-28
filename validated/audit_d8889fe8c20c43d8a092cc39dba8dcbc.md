### Title
Unprivileged market freeze via RAY-value overflow inside interest accrual before the borrow-index cap engages — (File: contracts/pool/src/interest.rs)

### Summary
Analog of CVE-2016-9392 (assertion failure in `calcstepsizes` reachable by a crafted input): in XOXNO Lending, every mutating entrypoint first runs `global_sync` accrual, and inside `accrue_step`/`calculate_supplier_rewards` the computation `borrowed * new_borrow_index` overflows the fixed-point domain and panics (`MathOverflow`) **before** the `MAX_BORROW_INDEX_RAY` cap in `update_borrow_index` can clamp the index. Once a market's scaled debt times index crosses the RAY ceiling, every subsequent accrual panics, permanently freezing all supplier and borrower funds in that market.

### Finding Description
`global_sync` in `contracts/pool/src/interest.rs:20-33` runs before every pool op and loops `accrue_chunk` over the elapsed time. Each chunk calls `accrue_step` (common/src/rates), which computes old and new total debt via `borrowed.mul(env, index)` in `calculate_supplier_rewards` (`common/src/rates/index.rs:73-80`). That multiply is the same `scaled_to_original`-domain product that panics on values above the i128/I256 RAY ceiling — the exact class of unchecked intermediate the JasPer bug exercised.

The borrow index itself is capped at `MAX_BORROW_INDEX_RAY` by `update_borrow_index` (`common/src/rates/index.rs:13-19`), but the panic fires *while computing debt value at the new index* — so the cap never engages when `borrowed_scaled` is large enough that `borrowed × index` overflows first. The repository's own harness proves this:

`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361` (`a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`): a billion-scale market at ~98% utilization on a steep rate curve hits `MATH_OVERFLOW` inside `try_update_indexes_for`, with `borrow_index < MAX_BORROW_INDEX_RAY` — explicitly asserting "the index cap did not engage before the value overflow." The test then confirms the freeze: `try_withdraw_raw` and `try_repay` both revert with `MATH_OVERFLOW` because "every verb accrues first" (`large_positions_and_long_horizons.rs:354-356`).

This is permanent, not transient: `global_sync` unconditionally accrues on entry, so no repay, withdraw, liquidate, `clean_bad_debt`, or `update_indexes` can ever succeed again on that book. Unlike the guarded `*RoundsToZeroShares` reverts (which reject only the offending call), this panic bricks the market for all users.

### Impact Explanation
Permanent freezing of funds — all suppliers and borrowers in the affected (hub, token) book lose access to their balances forever. An attacker with large capital can deliberately manufacture the state: supply and borrow a whale-scale position to pin utilization near 100% on a steep interest curve, then simply let time pass (or nudge it with `update_indexes`, an unprivileged entrypoint) until the accrual crosses the RAY ceiling. Every other user's funds in that book are frozen with no recovery path — `recapitalize` and bad-debt paths also accrue first.

### Likelihood Explanation
Reachable entirely by unprivileged addresses via `supply`, `borrow`, and `update_indexes`; requires whale-scale liquidity and sustained high utilization on a high-rate curve (the harness demonstrates it concretely). No privileged action, oracle manipulation, or timing race is needed — the condition is purely arithmetic. The cost to the attacker is interest paid while holding utilization high, but the griefing ratio is high since all suppliers in the book are frozen. Medium severity: high impact, but requires substantial capital and extreme sustained utilization.

### Recommendation
- Order the operations so the index cap is applied to `new_borrow_index` **before** computing `borrowed * new_index` in `calculate_supplier_rewards`/`accrue_step`, and clamp the product itself (e.g., `mul_floor_saturating` or saturating the computed interest) rather than letting it panic.
- Alternatively, add an explicit early check in `accrue_chunk`: if `borrowed_scaled × index` would overflow, clamp debt value at the ceiling and cap the index, so the market degrades gracefully (index pinned at cap, interest stops accruing) instead of freezing.
- At minimum, allow `update_indexes`/accrual to succeed past the cliff so withdrawals and repayments remain possible.

### Proof of Concept
The repository already contains the working demonstration:

```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;                 // ~98% utilization
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);
// advance years; try_update_indexes_for eventually fails:
assert_contract_error(failed, errors::MATH_OVERFLOW);
assert!(last.borrow_index < MAX_BORROW_INDEX_RAY); // cap never engaged
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Manual trace: `controller.update_indexes` / any verb → pool op → `Cache` load → `global_sync` (`interest.rs:20`) → `accrue_chunk` → `accrue_step` → `calculate_supplier_rewards` → `borrowed.mul(env, new_borrow_index)` (`rates/index.rs:80`) → product exceeds RAY ceiling → `panic_with_error!(MathOverflow)` → call reverts, state unchanged, and every future call repeats the same panic.