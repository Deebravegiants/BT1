### Title
Interest accrual overflows i128 on scaled-debt value before the borrow-index cap engages, permanently freezing the market - ([File: common/src/rates/index.rs](common/src/rates/index.rs))

### Summary
`accrue_step` → `calculate_supplier_rewards` computes `borrowed * new_borrow_index` in `i128` before the `MAX_BORROW_INDEX_RAY` clamp can protect anything. On a large market at sustained high utilization the borrow index grows fast enough that the debt-value product overflows `i128` while the index itself is still far below the cap. Accrual panics, and because every pool/controller verb accrues first, the market is permanently bricked: no repay, no withdraw, no liquidation, no `update_indexes`. The live regression test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361` demonstrates exactly this and notes the documented bound in `docs/reference/formulas.md` is wrong.

### Finding Description
`update_borrow_index` caps the new index at `MAX_BORROW_INDEX_RAY` (common/src/rates/index.rs:13-19), but `calculate_supplier_rewards` then multiplies the scaled borrow total by that index to get total debt value:

- `let old_total_debt = borrowed.mul(env, old_borrow_index);` (index.rs:80)
- `let new_total_debt = borrowed.mul(env, new_borrow_index);` (index.rs:81)

`Ray::mul` is a checked fixed-point multiply; `borrowed` (scaled shares) times `borrow_index` (RAY-scaled) overflows `i128` when scaled principal is roughly `i128::MAX / index ≈ 1e11` RAY-units at a ~170x index — a value the cap `MAX_BORROW_INDEX_RAY` does not prevent because the index is still below it. The panic propagates out of `accrue_chunk` (contracts/pool/src/interest.rs:39-53) called by `global_sync` (interest.rs:20-33), which runs at the top of every market transition via `synced_market`/`load_leg`/`run_batch` (contracts/pool/src/ops/mod.rs:30-73). Once the index crosses the cliff, there is no path that skips accrual, so the freeze is unrecoverable.

An unprivileged borrower drives the market there: `borrow` at near-max utilization on the steep segment of the rate curve (e.g. the XLM curve in the test) compounds the index, and any later call — `update_indexes`, `repay`, `withdraw`, `liquidate` — panics once the value ceiling is crossed. `max_utilization` must be uncapped or near 1.0, which is a supported configuration (`with_max_utilization_disabled_all_markets` in the test).

### Impact Explanation
Permanent freezing of funds. Once the overflow is hit, every supplier's principal and every borrower's collateral in that market is locked forever: `withdraw`, `repay`, `liquidate`, and `clean_bad_debt` all call `global_sync` first and all revert. The test confirms: `t.try_withdraw_raw(BOB, "BIG18", 1)` and `t.try_repay(...)` both fail with `MATH_OVERFLOW`, and `borrow_index < MAX_BORROW_INDEX_RAY` proves the cap never engaged.

### Likelihood Explanation
Requires an extreme but reachable state: ~98% utilization sustained for a period of years on a large market (the test uses ~10^9 whole units of an 18-decimal asset and finds the cliff within 40 years). Not exploitable on demand; it is a latent accounting ceiling that a whale borrower can steer the market toward, and once crossed it cannot be undone. Medium.

### Recommendation
Order the cap before the value math and bound the product, not just the index:
- In `accrue_step`, clamp `new_borrow_index` to `min(MAX_BORROW_INDEX_RAY, i128::MAX / borrowed.raw() * RAY)` so `borrowed * new_index` cannot overflow, or compute `accrued_interest` via a saturating `mul_div` that caps debt value at `i128::MAX`.
- Alternatively, when the index would exceed the value ceiling, pin `new_borrow_index` so that `new_total_debt == i128::MAX` and stop accruing rather than panicking — keeping the market operable for repay/withdraw.
- Fix the bound documented in `docs/reference/formulas.md`, which the test shows understates the cliff.

### Proof of Concept
Reproduced by the existing harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361):

1. Create markets `BIG18` (18 decimals, XLM rate curve) and `COL`, with utilization caps disabled.
2. `supply(BOB, BIG18, 1e9 * 10^18)`; `supply(ALICE, COL, large)`; `borrow(ALICE, BIG18, 98% of supply)`.
3. Advance time in 1-year steps calling `update_indexes` on `BIG18`.
4. Within 40 years `update_indexes` reverts with `MathOverflow`; `borrow_index` is still below `MAX_BORROW_INDEX_RAY`, and subsequent `withdraw`/`repay` calls on the market all revert with `MathOverflow` — the market is frozen.