### Title
Unprivileged borrower can permanently freeze a market by driving RAY-scaled debt value past the `i128` ceiling during accrual - ([File: contracts/pool/src/interest.rs])

### Summary
CVE-2014-0236 is a crash-from-malformed-input bug: a single attacker-controlled field (zero `root_storage`) reaches an unchecked dereference and kills the process. The on-chain analog in XOXNO Lending is a single unprivileged `borrow`/`update_indexes` call pushing `borrowed * borrow_index` past the representable RAY range inside accrual, which panics in `scaled_to_original`. Because every market verb accrues first, the panic bricks the market permanently.

### Finding Description
`interest::global_sync` runs before every market mutation (`Cache::load` → `accrue_chunk` → `accrue_step` at `contracts/pool/src/interest.rs:20-53`). Accrual computes the RAY-scaled debt value via `mul_div`/`scaled_to_original` on `borrowed * borrow_index`. `update_borrow_index` caps the index at `MAX_BORROW_INDEX_RAY` (`common/src/rates/index.rs:13-19`), but nothing caps the **product** `borrowed * index`. On a large, high-utilization market the value overflows `i128`/`I256`-to-`i128` before the index cap engages, and `mul_div_half_up` panics with `MathOverflow` (`common/src/math/fp_core.rs:108-118`).

The in-tree harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`) demonstrates exactly this: after the cliff, `update_indexes`, `withdraw`, and `repay` all revert with `MATH_OVERFLOW`, and the index cap never engages (`borrow_index < MAX_BORROW_INDEX_RAY`).

### Impact Explanation
Permanent freezing of funds and effective market insolvency. Once the debt-value product exceeds the representable range, accrual panics unconditionally, so no `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, or `claim_revenue` on that market can ever succeed — suppliers' deposits and any liquidation-accessible collateral are locked forever. Unlike the CVE's restartable process crash, a Soroban panic persists in state.

### Likelihood Explanation
Reachable by a single unprivileged address through `controller.borrow` and `pool.update_indexes`/`controller.update_indexes` alone — no privilege, no bad parameter, no oracle manipulation. The cost is capital-scale: it requires a very large supplied book (the test uses ~10^27 base units of an 18-decimal asset) sustained at high utilization for multiple years on a steep rate curve. Given real XLM-market sizes this is an edge condition rather than an imminent attack, matching Medium severity.

### Recommendation
Bound the accrual input rather than only the index: in `accrue_step`/`update_borrow_index`, clamp or saturate when `borrowed * borrow_index` approaches the `i128` RAY ceiling (e.g., cap the index at `min(MAX_BORROW_INDEX_RAY, i128::MAX / borrowed_raw)` computed per market), or treat the overflow as a terminal index cap instead of panicking, so exits and liquidations remain executable. At minimum, add an explicit guard in `global_sync` that skips further index growth once the value product saturates.

### Proof of Concept
Existing test: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`. Conceptually:

1. `supply_raw(BOB, "BIG18", 1e9 * 1e18)` — unprivileged `controller.supply`.
2. `supply_raw(ALICE, "COL", ...)`; `borrow_raw(ALICE, "BIG18", 98% of supply)` — unprivileged `controller.borrow`.
3. Advance ledger time ~yearly; call `update_indexes` (permissionless) until `accrue_step` panics with `MathOverflow`.
4. Subsequent `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", ...)` revert with `MATH_OVERFLOW` — funds permanently frozen.