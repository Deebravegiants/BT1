### Title
i128 overflow in accrual `scaled_to_original` permanently freezes a whale-scale market before the borrow-index cap can engage - (File: common/src/rates/simulate.rs)

### Summary
Every market mutator (`supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `flash_loan`, `claim_revenue`, `update_indexes`, etc.) begins with `interest::global_sync`, which calls `accrue_step` per chunk. `accrue_step` computes `borrowed_original = scaled_to_original(env, borrowed, borrow_index)` — i.e. `borrowed_scaled * borrow_index / RAY` — *before* the borrow index is grown and clamped at `MAX_BORROW_INDEX_RAY` in `update_borrow_index` (common/src/rates/index.rs:13-19). Because scaled shares are token units × 10^(27−decimals), a market holding on the order of a billion whole tokens of debt reaches `borrowed_scaled * borrow_index > i128::MAX` while the index is still far below the cap. `mul` then panics with `GenericError::MathOverflow`, the accrual aborts, and since every verb accrues first, the market is permanently bricked — no withdrawal, repayment, or liquidation can ever execute.

### Finding Description
- `contracts/pool/src/interest.rs:20-33` (`global_sync`) runs `accrue_chunk` → `accrue_step` on every mutation of an existing market.
- `common/src/rates/simulate.rs:60-61`: `scaled_to_original(env, borrowed, borrow_index)` and the same for `supplied` are evaluated to compute utilization, unconditionally, before index update.
- `common/src/rates/scaling.rs:14-16`: `scaled_to_original` is `scaled.mul(env, index)`, which resolves via `mul_div_half_up`/`mul_ratio` paths that panic on `MathOverflow` when the quotient exceeds `i128::MAX` (common/src/math/fp_core.rs:104-118).
- The cap in `update_borrow_index` (index.rs:13-19) only bounds the *index* (≤ ~10^9·RAY), not the *product* `borrowed_scaled × index`. For an 18-decimal asset, `borrowed_scaled ≈ debt_units × 10^9`; with ~10^27 token units of debt (10^9 whole tokens), the product overflows once the index reaches only ~170×, long before the 10^9× cap. The repo's own test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361) confirms `MATH_OVERFLOW` on `update_indexes`, `withdraw`, and `repay`, and notes "the index cap did not engage before the value overflow" — contradicting the bound claimed in docs/reference/formulas.md.
- The same overflow domain applies to `supplied * supply_index` (simulate.rs:61), which is reached even earlier since supply ≥ debt in a solvent market.

### Impact Explanation
Permanent freezing of funds. Once the scaled-value product crosses `i128::MAX`, every entrypoint on that market reverts at the accrual step. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, `clean_bad_debt`/`recapitalize` cannot run — none of them can skip `global_sync`. All tokens custodied in the pool for that market (all spokes' supplies over the shared physical balance) are locked forever. This is not a fail-closed guard: it is an unbounded arithmetic trap on the only code path that can unfreeze it.

### Likelihood Explanation
Medium-low but reachable by unprivileged actions. An attacker (or organic market state) needs a market whose scaled debt or supply is within a few orders of magnitude of the overflow point: for low-decimal tokens (e.g., 6–8 decimals, where the 10^(27−d) multiplier is 10^19–10^21) the threshold in whole tokens is far lower than for 18-decimal assets — a high-decimals-scaled market like USDC-sized stables reaches the cliff with materially smaller unit counts than the test's 10^9-token 18-decimal example. Attacker-controlled actions are simply `supply` + `borrow` at high utilization plus letting time pass; no admin, oracle, or timing manipulation is required. The steep segment of the interest curve accelerates index growth, and nothing in the borrow flow prevents accumulating the position other than caps — which are rescale-saturated admin parameters that can be set high for a large market (`calculate_scaled_cap` fails open, scaling.rs:26-33). Cost is capital-heavy, so likelihood is bounded, but the freeze is also reachable non-adversarially, at which point there is no recovery path at all.

### Recommendation
Make the value computations in `accrue_step` saturating or clamped rather than panicking:
- Use `mul_div_floor_saturating` (already in `fp_core`) for `borrowed_original`/`supplied_original` in `accrue_step`, since they feed only utilization and the reward split — saturating to `i128::MAX` preserves ordering (utilization ≈ 100%+) without trapping.
- Clamp `borrowed_scaled * index` growth directly: apply `update_borrow_index`'s cap based on `min(index_cap, i128::MAX / borrowed_scaled)` so the index is always capped at the largest value that keeps `scaled_to_original` representable — analogous to the existing `protocol_fee_shares` headroom cap (index.rs:94-99).
- Alternatively, pre-scale down: if `borrowed` exceeds a bound, compute utilization on a reduced-precision quotient (`mul_div_floor` on already-divided operands) so accrual survives any market size.
- Add a regression test asserting `update_indexes`/`withdraw`/`repay` still succeed at the overflow boundary for both low- and high-decimal assets, and fix the formulas.md bound.

### Proof of Concept
Mirrors the existing harness test (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361), which already fails today:

1. Admin lists market `BIG18` (18 decimals, XLM-style curve) and `COL`; unprivileged actors then act.
2. `BOB` calls `supply(BIG18, 10^9 × 10^18)`; `ALICE` supplies `COL` collateral and calls `borrow(BIG18, 0.98 × supply)` — both ordinary unprivileged entrypoints, caps lifted/lenient.
3. Time advances at ~98% utilization; on the steep curve the borrow index compounds toward ~170×.
4. `ALICE` (or anyone) calls `update_indexes` / `repay` / `withdraw(1)`. `global_sync` → `accrue_step` → `scaled_to_original(borrowed, borrow_index)`: `borrowed_scaled (≈10^36) × index (≈1.7×10^29) / 10^27 > i128::MAX` → `MathOverflow` panic.
5. `borrow_index` is still ≪ `MAX_BORROW_INDEX_RAY` (10^36), so the cap never saved it. All subsequent calls on the market revert identically; the pool's tokens are permanently locked.