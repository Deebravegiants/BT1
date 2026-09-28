### Title
Borrow-index accrual overflow in `scaled_to_original` permanently freezes a market — all repay, withdraw, and liquidation paths panic - (File: `common/src/rates/scaling.rs`)

### Summary
The CVE class is an integer overflow that corrupts downstream computation. In XOXNO Lending, the same class maps onto the `i128` ceiling of the fixed-point engine: every state-changing entrypoint accrues interest first via `global_sync`, and accrual (and utilization) compute `shares * index` through `scaled_to_original`/`mul_div_half_up`, which panics with `MathOverflow` when the RAY-scaled value no longer fits `i128`. A whale-scale market sustained at high utilization reaches that ceiling before `MAX_BORROW_INDEX_RAY` ever engages, at which point the market is permanently frozen: every subsequent `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, and `update_indexes` reverts in the same overflow. The codebase's own test harness documents and reproduces this failure mode.

### Finding Description
`scaled_to_original` in `common/src/rates/scaling.rs:14` computes `scaled.mul(index)` — a `mul_div_half_up(x, index, RAY)` that returns the exact product in `i128` and panics `MathOverflow` when `scaled * index / RAY > i128::MAX` (`common/src/math/fp_core.rs:108-118`). Two places consume it on the hot path:

- `Cache::calculate_utilization` (`contracts/pool/src/cache/scale.rs:19-27`) unscale total `borrowed` and `supplied` shares to RAY values on every guarded operation.
- `accrue_step` via `interest.rs::accrue_chunk` (`contracts/pool/src/interest.rs:39-53`), invoked by `global_sync` at the top of every verb; `global_sync` runs before the borrow-index cap can halt growth.

Because a large supplied/borrowed book multiplies a large `scaled` share count, the value ceiling is hit long before `borrow_index` approaches `MAX_BORROW_INDEX_RAY`: the harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-360`) supplies ~1e27 units of an 18-decimal asset, borrows 98% of it, advances time at the XLM curve's steep segment, and observes `MATH_OVERFLOW` on `update_indexes` while `borrow_index < MAX_BORROW_INDEX_RAY`. After that, `withdraw` and `repay` revert identically since they accrue first.

### Impact Explanation
Permanent freezing of funds and protocol insolvency: once the panic threshold is crossed, no entrypoint that touches the market can succeed — suppliers cannot withdraw, borrowers cannot repay (so positions can never be liquidated or closed), and `update_indexes` itself bricks. The state is unrecoverable without an upgrade because accrual is monotonic in the index.

### Likelihood Explanation
Requires a whale-scale position (~1e27 base units of an 18-decimal asset) and sustained near-max utilization for multiple years on a steep rate curve. A single attacker cannot force this quickly, but they can deliberately construct the preconditions — supply the whale position themselves, borrow ~98%, and let `max_utilization` be disabled or loose — after which time alone triggers the freeze and locks every other supplier's funds. Medium likelihood, critical impact.

### Recommendation
Clamp or saturate inside `accrue_step`/`scaled_to_original` for aggregate unscale operations: cap `borrow_index` growth *before* multiplying (enforced inside the same step rather than after), and/or compute utilization and bad-debt totals with a saturating `mul_div` so accrual and guards degrade to a bounded value instead of panicking. Alternatively bound `scaled * index / RAY` by enforcing a supply cap in scaled-share terms at `calculate_scaled_supply`, guaranteeing `scaled` stays below `i128::MAX * RAY / MAX_BORROW_INDEX_RAY`.

### Proof of Concept
The repository's own test at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-360` is the PoC: supply `BILLION * 10^18` of an 18-decimal asset, borrow 98% of it against a large `COL` position, disable `max_utilization`, then advance a year at a time; `try_update_indexes_for(&["BIG18"])` eventually returns `MATH_OVERFLOW` with `borrow_index < MAX_BORROW_INDEX_RAY`, and subsequent `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", ...)` panic with the same error — demonstrating permanent, unrecoverable market freeze reachable by an unprivileged address.