### Title
Accrual-time `i128` overflow in `scaled_to_original` permanently freezes an entire market — every verb reverts before any exit, repayment, or liquidation — (File: contracts/pool/src/interest.rs)

### Summary
The bug class of CVE-2016-9443 — attacker-reachable input driving the program into an unrecoverable crash — maps onto the pool's interest accrual. Every mutating entrypoint runs `global_sync` first, and `global_sync` → `accrue_step` → `scaled_to_original` multiplies scaled shares by the index in `i128` with no recovery path. Once `borrowed * borrow_index` (or `supplied * supply_index`) exceeds `i128::MAX`, the multiplication panics with `MathOverflow` on every subsequent call, forever. An unprivileged whale can push a market into this state using only `supply`, `borrow`, and time-driven `update_indexes`, permanently freezing all supplier and borrower funds in that market — well before the `MAX_BORROW_INDEX_RAY` cap can clamp growth.

### Finding Description
`global_sync` (`contracts/pool/src/interest.rs:20-33`) chunks elapsed time and calls `accrue_step` (`common/src/rates/simulate.rs:51-94`). The step's first two lines unconditionally unscale the market totals:

```rust
let borrowed_original = scaled_to_original(env, borrowed, borrow_index);   // simulate.rs:60
let supplied_original = scaled_to_original(env, supplied, supply_index);   // simulate.rs:61
```

`scaled_to_original` (`common/src/rates/scaling.rs:14-16`) is `scaled.mul(index)` → `mul_div_half_up`, which panics with `GenericError::MathOverflow` when `scaled * index / RAY` does not fit `i128` (`common/src/math/fp_core.rs:108-118`). The borrow-index ceiling `MAX_BORROW_INDEX_RAY = 10^36` (`common/src/constants/pool.rs:19`) clamps the *index*, but the *product* `borrowed_shares * index` has no ceiling and grows with both market size and accrued index. Since debt compounds while scaled `borrowed` shares stay fixed, the product crosses `i128::MAX` while the index is still far below its cap — the cap never engages.

Every controller verb on that book (`withdraw`, `repay`, `borrow`, `liquidate`, `clean_bad_debt`, `flash_loan`, `claim_revenue`, `update_indexes`) builds a pool `Cache` and accrues first, so all of them hit the same panic. The state is terminal: `last_timestamp` is never advanced (`mark_accrued` at `interest.rs:32` is unreachable), the indexes are never written, and there is no admin or governance path that bypasses accrual.

Admissibility: the cap bound `max_cap_for_decimals` permits up to ~170 billion whole tokens, and utilization can drift upward on its own because debt compounds faster than supply — an attacker only needs to seed the market (`supply` a near-cap amount, `borrow` at high utilization from a collateralized account in a second market) and let time, plus permissionless `update_indexes` calls, do the rest. `docs/reference/formulas.md:432-437` acknowledges value overflow "can occur before the index ceiling," but the accompanying bound table understates how early the cliff arrives: the harness test asserts the cliff is reached *within* the documented domain (caps lifted only to admitted maxima) and notes "the bound in docs/reference/formulas.md is wrong" (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:340`).

### Impact Explanation
Permanent freezing of funds. Once the cliff is crossed, every withdrawal, repayment, liquidation, and bad-debt cleanup on that market reverts with `MathOverflow`. All suppliers' deposits and all borrowers' collateral tied to that book are unrecoverable; liquidations also cannot run, so the position cannot be unwound even as it becomes insolvent. The test at `large_positions_and_long_horizons.rs:321-356` demonstrates exactly this: `try_update_indexes_for`, `try_withdraw_raw`, and `try_repay` all fail with `MATH_OVERFLOW`.

### Likelihood Explanation
Medium. The attack requires a whale-scale deposit approaching the admitted cap (~10^29 raw units at 18 decimals) and sustained high utilization for years of compounding on a steep rate curve — heavy capital and patience, but no privilege, no oracle manipulation, and no cooperation from anyone. Once seeded, any third party can advance the outcome via the permissionless `update_indexes` entrypoint, and ordinary market drift toward high utilization does the rest. The cliff is reachable entirely within admitted caps and configured rate parameters, at indexes far below the 10^36 ceiling.

### Recommendation
Make accrual overflow-safe or recoverable instead of trapping the market permanently:

- In `accrue_step`, use saturating/`try_` variants for `scaled_to_original` on market totals, or short-circuit accrual when `borrowed`/`supplied` would overflow — e.g., clamp the borrow index to `MAX_BORROW_INDEX_RAY` (stopping further interest) before the value multiplication can overflow, since `update_borrow_index` already tolerates the ceiling.
- At minimum, bound scaled totals at entry (`supply`/`borrow`/`flash`/`multiply`) so `scaled * MAX_*_INDEX / RAY` stays within `i128` — i.e., enforce a stricter `max_cap_for_decimals` that accounts for worst-case index growth rather than only the deposit-time conversion limit.
- Add a governance or automatic escape hatch (e.g., an accrual-free forced write-down or index-park operation) so a market that does reach the cliff can be wound down rather than frozen forever.
- Correct the numeric-limits bound in `docs/reference/formulas.md` to reflect the real cliff measured by the harness test.

### Proof of Concept
Existing harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`) reproduces the freeze end-to-end:

1. BOB calls `controller.supply` with `BILLION * 10^18` base units of an 18-decimal market (within the admitted cap after `lift_caps`).
2. ALICE supplies collateral in a second market and calls `controller.borrow` for 98% of the BIG18 pool — high utilization on the steep XLM curve (175% max rate).
3. Anyone advances ledger time; each `controller.update_indexes` call accrues via `global_sync` → `accrue_step`. Within ~a few years `scaled_to_original(borrowed, borrow_index)` overflows `i128` and panics with `MathOverflow`, while `borrow_index < MAX_BORROW_INDEX_RAY` (asserted at line 350-353 — the cap never engages).
4. `withdraw(1)` and `repay(1.0)` both revert with `MATH_OVERFLOW` (lines 355-356). The same panic hits `liquidate`, `clean_bad_debt`, `flash_loan`, and `claim_revenue`, since all of them accrue first. The market, and all funds in it, are permanently frozen.