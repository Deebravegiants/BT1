### Title
RAY-value i128 overflow in accrual permanently freezes a whale market before the borrow-index cap engages - (File: common/src/rates/simulate.rs)

### Summary
Like the Dulwich `apply_delta` overflow, the bug class is an arithmetic overflow on attacker-influenceable magnitudes. Here, `accrue_step` computes `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` at the top of every accrual chunk (`common/src/rates/simulate.rs:60-61`). `scaled_to_original` is `scaled.mul(env, index)` → `mul_div_half_up`, which panics with `MathOverflow` when the RAY-scaled value exceeds `i128::MAX` (`common/src/math/fp_core.rs:108-118`, `common/src/rates/scaling.rs:14-16`). A market holding ~1e9 whole 18-decimal tokens (`1e36` RAY units) reaches that ceiling once the borrow index grows ~170x — which the borrow-index cap `MAX_BORROW_INDEX_RAY = 1e36` cannot prevent because the overflow happens on `borrowed * index`, not on the index itself. The repo's own stress test confirms: after the panic, every verb accrues first via `interest::global_sync`, so `update_indexes`, `withdraw`, and `repay` all revert with `MathOverflow` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:315-361`, `contracts/pool/src/interest.rs:20-53`).

### Finding Description
`interest::global_sync` runs `accrue_chunk` → `accrue_step` before every pool mutation (`contracts/pool/src/interest.rs:20-53`; flow documented in `contracts/pool/README.md` "each mutation ... → interest::global_sync → mutate"). The first two lines of `accrue_step` unscale the market's aggregate share totals: [1](#0-0) 

Both calls multiply a RAY share quantity by a RAY index. For an 18-decimal asset, one billion whole tokens is `1e36` RAY; `i128::MAX ≈ 1.7e38`, so the product overflows once `borrow_index ≳ 170·RAY`. `mul_div_half_up` widens to `I256` and then panics via `to_i128`/`MathOverflow` when the result does not fit (`common/src/math/fp_core.rs:138-143`, `:300-303`). The `update_borrow_index` cap at `MAX_BORROW_INDEX_RAY` (1e36, i.e., a 1e9x multiplier) is ordered too late: the value multiplication happens before the cap can be reached, as the test asserts (`borrow_index < MAX_BORROW_INDEX_RAY` when the cliff hits, `large_positions_and_long_horizons.rs:350-353`).

An unprivileged attacker can drive a market into this state using only in-scope entrypoints:
- `controller.supply` / `controller.borrow` — permissionless; supply caps are configurable per spoke and the harness lifts them via ordinary config edits (`lift_caps`, lines 81-95); `with_max_utilization_disabled` corresponds to `max_utilization = RAY`, a value inside the domain `MarketParams` accepts.
- `pool.update_indexes` — explicitly permissionless (`tests/fuzz/fuzz_targets/rates_and_index.rs:375` "update_indexes is permissionless"), so anyone can force the accrual step that panics. Time does the rest: utilization drifts upward because debt compounds faster than supply, pushing the curve onto its steep `slope3` segment (test header, lines 8-13).

There is no recovery path once the panic occurs: `repay`, `withdraw`, `liquidate`/`seize_positions`, `clean_bad_debt`, `recapitalize`, and `claim_revenue` all route through `Cache::load` + `global_sync`, which panics before any state change.

### Impact Explanation
Permanent freezing of funds. All supplier principal and yield, all borrower collateral backing the frozen debt, and all unclaimed protocol revenue in the market are locked permanently — the contract cannot be operated for that market because every mutation reverts in accrual. The test proves `withdraw` and `repay` both revert with `MATH_OVERFLOW` after the cliff (lines 354-356). Even a borrower willing to repay in full cannot do so, so the bad debt cannot be unwound and liquidation is impossible. This is a protocol-level insolvency/freeze outcome, not a per-transaction DoS.

### Likelihood Explanation
Medium. Exploitation requires a whale-scale deposit (≈1e9 whole tokens of an 18-decimal asset, or proportionally large scaled totals at other decimals) plus sustained high utilization on a steep rate curve for multiple years — the harness reaches the cliff in under ~10-40 years at 98% utilization on the 175%-max XLM curve, and utilization drifts up on its own since debt compounds faster than supply (lines 8-13). No privileged action is needed to create the book once caps permit it, but the capital and horizon requirements are substantial, and caps on real listings may keep scaled totals below the ceiling for most assets. Note the neighboring matrix cells (lines 287-305) show the cliff is binary: the same markets that accrue fine at 95% utilization for 2 years hit the wall at 98% for a few years.

### Recommendation
Make accrual fail-safe instead of panicking on the value product:
- In `accrue_step`, compute `borrowed_original`/`supplied_original` with a saturating or capped helper (e.g., clamp to `i128::MAX` or to a value-domain bound) before the `I256 → i128` conversion, so utilization pins at ~100% rather than reverting.
- Alternatively, cap the borrow/supply index at a level derived from `i128::MAX / supplied` at market creation or in `update_borrow_index`, so the cap engages before the product overflows — the current `MAX_BORROW_INDEX_RAY = 1e36` cap is book-agnostic and arrives too late.
- At minimum, provide an escape path (e.g., a `repay`/`withdraw` mode that skips accrual or accrues with a clamped index) so positions are not permanently bricked once the threshold is crossed.

### Proof of Concept
The repository contains a direct, executable PoC: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361` (`a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`). It:

1. Creates market `BIG18` (18 decimals, `xlm_curve` with 175% max rate, `max_utilization = RAY`) and `COL` collateral; lifts supply/borrow caps to `max_cap_for_decimals` (lines 327-328).
2. BOB supplies `1e9 * 1e18` BIG18 (`supply_raw`, line 330) — raw value `1e36` RAY.
3. ALICE supplies COL collateral and borrows 98% of the BIG18 book (lines 332-333).
4. Advances time one year per loop calling `update_indexes` (permissionless) until it reverts with `MATH_OVERFLOW` (lines 336-348); asserts the revert happens *below* `MAX_BORROW_INDEX_RAY` (lines 350-353) — i.e., in `scaled_to_original` inside `accrue_step`, before the index cap.
5. Asserts the market is bricked: `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", ...)` both revert with `MATH_OVERFLOW` (lines 354-356).

All calls used (`supply`, `borrow`, `update_indexes`, `withdraw`, `repay`) are unprivileged entrypoints; only the harness's cap-lift helper touches config, which merely sets caps to the protocol's own per-decimals maximum.

### Citations

**File:** common/src/rates/simulate.rs (L60-64)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);
```
