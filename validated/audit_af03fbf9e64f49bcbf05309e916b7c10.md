### Title
Whale-scale market permanently freezes when accrued index growth overflows `scaled_to_original` before the index cap can engage - (File: contracts/pool/src/interest.rs)

### Summary
Every state-changing pool verb accrues interest first via `global_sync` → `accrue_chunk` → `accrue_step`. Inside accrual, utilization is computed as `scaled_to_original(scaled, index)`, i.e. `scaled_ray * index_ray / RAY` (`contracts/pool/src/cache/scale.rs:19-27`, `common/src/rates/scaling.rs:14-16`). On a very large market at sustained high utilization, the RAY-scaled position value times the grown index exceeds the `i128` result domain, and `mul`/`mul_div_*` panics with `GenericError::MathOverflow` (`common/src/math/fp.rs:50-52`, `common/src/math/fp_core.rs`). The panic occurs during utilization computation *before* the borrow index is capped at `MAX_BORROW_INDEX_RAY`, so the cap never engages and the market is permanently wedged: no repay, withdraw, liquidation, or further `update_indexes` can execute.

### Finding Description
`Cache::calculate_utilization` computes `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` (`contracts/pool/src/cache/scale.rs:19-27`). `scaled_to_original` is `scaled.mul(env, index)` = `mul_div_half_up(scaled_raw, index_raw, RAY)` (`common/src/rates/scaling.rs:14-16`, `common/src/math/fp.rs:50-52`). The `I256`-widened intermediate is exact, but the *result* must fit `i128`; when `scaled_value_ray × index` exceeds `i128::MAX` the function panics with `MathOverflow`.

`global_sync` runs unconditionally at the head of every accrual-requiring operation (`contracts/pool/src/interest.rs:20-33`). Because utilization is evaluated inside `accrue_step` before `set_borrow_index`/`set_supply_index` write the (capped) indexes (`contracts/pool/src/interest.rs:39-53`), a single failing chunk poisons all subsequent accruals — `mark_accrued` is never reached and `last_timestamp` is never advanced, so the overflow re-triggers on every later call.

The repository's own harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-362`) demonstrates exactly this:

- 18-decimal market, ~1 billion whole-token principal supplied, ~98% borrowed
- after enough years at high utilization on the XLM curve, `update_indexes` fails with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`
- subsequent `withdraw` and `repay` also revert with `MATH_OVERFLOW` because they accrue first

The test comment itself notes "the index cap never engages" and "the market is frozen: no repay, no withdraw, no liquidation." The bound documented in `docs/reference/formulas.md` (numeric limits) is acknowledged in the test as incorrect.

### Impact Explanation
Permanent freezing of funds for the affected (hub, token) book: all suppliers' claims become unwithdrawable, borrowers cannot repay or be liquidated, and the pool balance is stranded. This is a market-wide, irreversible availability failure of user funds, reachable entirely through unprivileged entrypoints (`supply`, `borrow`, then time).

### Likelihood Explanation
The attack is permissionless but capital-intensive: the caller must supply on the order of billions of whole units of a high-decimal asset and hold ~98% utilization long enough for the index to grow the scaled value past the `i128` ceiling (tens of years at the demonstrated curve, less at higher-utilization curves). The attacker's own principal is also frozen, making it a costly griefing/insolvency-adjacent attack rather than profitable theft. The arithmetic bound is also partially documented, so this is a residual-risk class issue rather than a novel design flaw. Medium.

### Recommendation
Cap the *value* side before the multiply overflows: in `accrue_step`/utilization, clamp `borrow_index` (and accrual growth) so that `scaled × index` stays within the `i128` result domain, or compute utilization in a saturating form like `calculate_scaled_cap` (`common/src/rates/scaling.rs:26-33`) so the rate engine degrades gracefully instead of panicking. Alternatively enforce `borrow_index ≤ MAX_BORROW_INDEX_RAY` as a precondition checked before `scaled_to_original` is invoked, and fix the incorrect bound stated in `docs/reference/formulas.md#numeric-limits`.

### Proof of Concept
See `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-362` — an existing end-to-end reproduction: `supply_raw(BOB, "BIG18", 1e9 * 1e18)`, `borrow_raw(ALICE, "BIG18", 98% of principal)`, advance time until `try_update_indexes_for` returns `MATH_OVERFLOW`, then observe `try_withdraw_raw` and `try_repay` both fail with the same error.