### Title
RAY-value overflow in accrual permanently freezes a saturated market - (File: common/src/rates/simulate.rs)

### Summary
`accrue_step` recomputes total supplied/borrowed value with `scaled_to_original` (`scaled.mul(env, index)`), which panics with `GenericError::MathOverflow` when `scaled * index` exceeds `i128::MAX`. The borrow-index ceiling (`MAX_BORROW_INDEX_RAY` = 10³⁶, only 10⁹× the initial index) does not prevent this: for a market whose scaled supply is ~170× larger than the cap implies, the value product overflows before the index cap engages. Because every state-changing entry point runs `global_sync` first, once the market crosses the cliff, `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `recapitalize`, and `update_indexes` all revert permanently — the panic is in accrual, not in the verb itself.

### Finding Description
The bug class of the reference CVE — a counter growing past its safe domain and corrupting subsequent operations — maps onto the index/value arithmetic here:

- `contracts/pool/src/interest.rs:39-53` `accrue_chunk` → `common/src/rates/simulate.rs:60-61` calls `scaled_to_original(env, borrowed, borrow_index)` and `scaled_to_original(env, supplied, supply_index)`.
- `common/src/rates/scaling.rs:14-16` `scaled_to_original` is `scaled.mul(env, index)` → `fp_core::mul_div_half_up`, which widens to `I256` for the intermediate product but panics via `to_i128()` when `scaled * index / RAY` does not fit in `i128` (`common/src/rates/compound.rs:40-42` shows the same panic pattern).
- `common/src/rates/index.rs:80-81` `calculate_supplier_rewards` performs `borrowed.mul(env, new_borrow_index)` on the *post-growth* index — the overflow site that fires first, before any clamp in `update_borrow_index` can help (the index ceiling caps the index, not the product).

The harness proves reachability and permanence: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360` drives a 1e9-whole-token market at 98% utilization on the steep XLM curve; `update_indexes` fails with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, and afterwards `withdraw` and `repay` fail identically.

Reachability for an unprivileged attacker: the admitted cap maximum is `i128::MAX / 10^(27-d)` ≈ 170 billion whole tokens (`docs/reference/formulas.md:429`), and a supply position at/near the cap combined with sustained high borrow utilization pushes `borrowed * borrow_index` past `i128::MAX` after years of accrual — no privileged action needed, only capital plus time, and `update_indexes` is permissionless so anyone triggers the freeze once the cliff is crossed.

### Impact Explanation
Permanent freezing of funds: once `borrowed * new_borrow_index` overflows `i128`, every verb accrues first and panics inside `calculate_supplier_rewards`/`scaled_to_original`. Suppliers cannot withdraw, borrowers cannot repay (their collateral is locked too), and liquidations cannot execute. The freeze is permanent because the borrow index is monotone and `last_timestamp` only moves forward — there is no path that reduces the product. This is "permanent freezing of funds," an accepted impact class.

### Likelihood Explanation
Requires a market admitted with a cap near the domain maximum and a whale-sized supply book plus sustained high utilization; the steep-curve cell in the harness reaches the cliff in a small number of years. On high-decimal, high-supply tokens listed with generous caps this is reachable without privilege, but it demands substantial capital and time, so likelihood is Medium-Low. Note also that `docs/reference/formulas.md:434-437` acknowledges "value overflow can occur before the index ceiling and block repayment/withdrawal" — if this disclosure makes it a documented accepted limit, severity should be downgraded, but the impact remains a permanent freeze rather than a graceful fail-closed state.

### Recommendation
Guard the multiplication in `accrue_step`/`calculate_supplier_rewards` so the accrual saturates instead of trapping: clamp `borrow_index` to the largest value for which `borrowed * index` fits `i128` (compute the bound via `I256` and compare before `to_i128`), mirroring the existing `MAX_BORROW_INDEX_RAY` clamp in `update_borrow_index` (common/src/rates/index.rs:13-19). Alternatively, admit caps low enough that `cap * MAX_BORROW_INDEX_RAY / RAY` always fits `i128` at listing time in `require_cap_within_asset_domain`.

### Proof of Concept
See `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360` — `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`: supply 1e9 BIG18 tokens, borrow 98% of it, advance time; `try_update_indexes_for(["BIG18"])` returns `MATH_OVERFLOW` with `borrow_index < MAX_BORROW_INDEX_RAY`, and subsequent `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", 1.0)` both return `MATH_OVERFLOW`.