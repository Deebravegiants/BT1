### Title
i128 overflow in RAY-denominated accrual permanently freezes a high-utilization market — (`common/src/rates/scaling.rs`)

### Summary
The integer-overflow bug class of CVE-2021-39714 maps onto XOXNO Lending as an `i128` overflow in `scaled_to_original` during interest accrual. When `borrowed * borrow_index` no longer fits in `i128`, `accrue_step` panics with `MathOverflow`. Every state-changing entrypoint accrues first, so once the product crosses the ceiling the market is frozen forever — no repay, withdraw, liquidate, or `clean_bad_debt` can execute, and the `MAX_BORROW_INDEX_RAY` clamp does not protect it because the multiplication happens before the clamp.

### Finding Description
`global_sync` in `contracts/pool/src/interest.rs` runs before every pool operation and calls `accrue_step`, which computes `scaled_to_original(env, borrowed, borrow_index)` (`common/src/rates/simulate.rs:60`). `scaled_to_original` is `scaled.mul(env, index)` — a `mul_div_half_up` that panics with `GenericError::MathOverflow` when `borrowed * borrow_index / RAY` exceeds `i128::MAX` (`common/src/rates/fp_core.rs:108-118`). The overflow domain is real: scaled debt can reach ~`1.7e38` RAY (the token-to-RAY cap, `docs/reference/formulas.md`), and `borrow_index` grows toward `MAX_BORROW_INDEX_RAY = 10^36`; the product overflows before the index ceiling engages, as proven by the harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356`, which shows `try_update_indexes_for`, `try_withdraw_raw`, and `try_repay` all failing with `MATH_OVERFLOW`.

### Impact Explanation
Permanent freezing of funds: all supplier deposits and all collateral backing borrows in that market become unrecoverable, and borrowers can never repay, so liquidations are impossible too. Any unprivileged user can trigger the terminal panic via the permissionless `update_indexes` entrypoint once the market's `borrowed * borrow_index` product crosses `i128::MAX`; there is no recovery path since every verb accrues first.

### Likelihood Explanation
Requires a very large market (~170 billion token supply domain per `docs/reference/formulas.md`) at sustained high utilization over multiple years of accrual — the harness test reaches the cliff inside 40 years at 98% utilization on a steep curve. Not exploitable at will, but the failure mode is a hard protocol invariant violation with total loss for that market, so severity is High with low likelihood → Medium-High.

### Recommendation
Clamp or saturate the accrued value: cap `borrowed` growth, evaluate `scaled_to_original` through the saturating `mul_div_floor_saturating` for utilization, and — most importantly — clamp `new_borrow_index` to `MAX_BORROW_INDEX_RAY` in `update_borrow_index` *before* computing debt valuations in `calculate_supplier_rewards`/`accrue_step`, so accrual becomes a monotone no-op at the cap instead of panicking. Add a pre-accrual early return in `accrue_step` when the index is already at the ceiling.

### Proof of Concept
See `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356`: supply `1e9 * 10^18` units, borrow 98% of it, advance time year-by-year; `update_indexes` panics with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, after which `withdraw` and `repay` panic identically — permanent freeze.