### Title
Accrual arithmetic overflows i128 before the borrow-index cap engages, permanently freezing a whale-scale market - (File: common/src/rates/index.rs)

### Summary
The CVE-2017-18237 bug class is a crash (invalid pointer dereference) on unvalidated input inside a conversion helper. The analog on XOXNO Lending is an unconditional arithmetic trap inside index accrual: `calculate_supplier_rewards` multiplies the scaled debt by the new borrow index in `i128`-bounded RAY arithmetic and panics with `MathOverflow` when `borrowed * new_borrow_index / RAY` exceeds `i128::MAX`. Because every state-changing verb accrues first via `global_sync`, once `scaled_debt × borrow_index` crosses the i128 ceiling, every call on that market — `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `update_indexes` — reverts forever. The `MAX_BORROW_INDEX_RAY` cap in `update_borrow_index` is applied to the index, not the value, so it cannot prevent the trap.

### Finding Description
`update_borrow_index` caps the borrow index at `MAX_BORROW_INDEX_RAY` (≈170×) after multiplication, so the index itself is bounded. But `calculate_supplier_rewards` then computes `new_total_debt = borrowed.mul(env, new_borrow_index)` where `borrowed` is the *scaled* debt in RAY terms — a quantity proportional to principal size × 1e27. On a large market (e.g., an 18-decimal token with ~1e9 tokens supplied, scaled ≈ 1e45 RAY) at sustained high utilization, `new_total_debt` overflows `i128` long before the index approaches the cap. `Ray::mul` routes through `mul_div_half_up`, which panics with `GenericError::MathOverflow` when the widened `I256` result does not fit `i128`.

`global_sync` (contracts/pool/src/interest.rs:20-33) runs this accrual at the top of every mutating operation, and `simulate_update_indexes_body` runs the same `accrue_step` on the read path used by the controller's risk/liquidation views. There is no try/catch, no clamping of the debt value, and no path that skips accrual once `last_timestamp < now`. The panic is therefore a persistent, state-dependent trap — the market is bricked, not just one transaction.

The repository's own harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-362) demonstrates exactly this: after enough years at 98% utilization on the XLM curve, `update_indexes` fails with `MATH_OVERFLOW`, `last.borrow_index < MAX_BORROW_INDEX_RAY` (cap never engaged), and both `withdraw` and `repay` fail with the same error.

### Impact Explanation
Permanent freezing of funds / protocol insolvency for the affected market. All supplier principal and borrower collateral routed through that market becomes unrecoverable: withdrawals, repayments, liquidations, and bad-debt cleanup all accrue first and hit the same panic. A single unprivileged address can set up the precondition with `controller.supply`/`controller.borrow` (whale principal at high utilization); the trap then arms itself through ordinary time-based accrual, and any user — including the attacker's victims — triggers it on their next interaction. Unlike a fail-closed input check, the failure is permanent and affects third parties' funds, not just the caller's transaction.

### Likelihood Explanation
Medium. Exploitability requires (a) a market whose scaled supply is large enough that `borrowed × ~170× index` exceeds `i128::MAX` (achievable on high-decimal or high-cap listings; the harness reaches it at ~1e9 × 1e18 scale with caps lifted), and (b) sustained high utilization over a long accrual horizon so the borrow index compounds toward the cliff. No privileged action is needed — `supply`, `borrow`, and `update_indexes` are permissionless. The cost is capital and time, not access. Once the cliff is crossed, there is no recovery path in-contract; only a code upgrade (rejected as out of scope) could unbrick the market.

### Recommendation
Bound the accrual arithmetic on the *value* side, not just the index. In `accrue_step`/`calculate_supplier_rewards`, compute the debt delta with saturating or try-variants (`try_mul_div_half_up` / `mul_div_floor_saturating`) and clamp `new_total_debt` so that accrual continues (or cleanly caps the index at the point the representable value saturates) instead of panicking. Alternatively, enforce the cap early: if `borrowed.mul(new_index)` would overflow, clamp `new_index` to `i128::MAX * RAY / borrowed` and the already-defined `MAX_BORROW_INDEX_RAY`, whichever is lower, and treat residual interest as unbooked rather than trapping. The fix must be applied symmetrically in `simulate_update_indexes_body` so the liquidation view path cannot panic where the mutating path would have succeeded.

### Proof of Concept
Conceptual walkthrough (the repo's own test at tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361 is an executable version):

1. Attacker supplies `10^9` units of an 18-decimal token to market `BIG18` (scaled supply ≈ 1e45) and, using `COL` collateral on a second account, borrows 98% of it.
2. Time passes (ordinary ledger advancement; anyone can call the permissionless `Controller::update_indexes` at contracts/controller/src/lib.rs:370, though the trap also fires on any verb).
3. `global_sync` → `accrue_step` → `calculate_supplier_rewards` computes `borrowed.mul(new_borrow_index)`: ~1e45 × ~170e27 / 1e27 ≈ 1.7e74 > i128::MAX → `MathOverflow` panic, aborting before `last_timestamp` is stamped.
4. Because the panic precedes `cache.mark_accrued()`, every subsequent call re-runs the identical overflowing step. `withdraw`, `repay`, and `liquidate` on `BIG18` revert permanently; supplier funds are frozen forever.

Key code:
- `common/src/rates/index.rs:73-88` — `calculate_supplier_rewards` unbounded `borrowed.mul(new_borrow_index)`.
- `common/src/rates/index.rs:13-19` — `update_borrow_index` caps the index, not the product.
- `contracts/pool/src/interest.rs:20-33` — `global_sync` runs accrual unconditionally on every verb.
- `common/src/math/fp_core.rs:108-118` — `mul_div_half_up` panics `MathOverflow` on i128 overflow of the widened result.