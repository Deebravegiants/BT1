### Title
Sustained high-utilization whale market overflows RAY fixed-point during accrual, permanently freezing the market - (File: common/src/rates/index.rs)

### Summary
The pool's accrual path multiplies `scaled * index` in RAY (1e27) fixed point and panics with `MathOverflow` on `i128` overflow before the `MAX_BORROW_INDEX_RAY` / `MAX_SUPPLY_INDEX_RAY` caps can clamp the index. Since every state-changing entrypoint accrues first (`Cache::load` → `interest::global_sync`), once a market crosses this arithmetic cliff it can never be touched again: `supply`, `borrow`, `withdraw`, `repay`, `net_settle`, `seize_positions`, `recapitalize`, `claim_revenue`, and even `update_indexes` all revert permanently. The bug class is a crash/DoS from unchecked-order arithmetic — directly analogous to CVE-2020-2930's repeatable crash.

### Finding Description
`interest::global_sync` in `contracts/pool/src/interest.rs:20-33` runs `accrue_step` on every market mutation. Inside `common/src/rates/index.rs`:

- `update_supply_index` computes `supplied.mul(env, old_index)` at line 34 and `new_total_debt = borrowed.mul(env, new_borrow_index)` inside `calculate_supplier_rewards` at line 81.
- `Ray::mul` uses checked `i128` arithmetic that panics with `GenericError::MathOverflow` (`common/src/math/fp.rs:12-24`).
- The index cap `MAX_BORROW_INDEX_RAY` (~1e12 RAY, `common/src/constants/pool.rs:19`) is only applied *after* growth inside `update_borrow_index` (lines 13-19) — it does not protect the `scaled × index` products, which overflow `i128` (~1.7e38) when `scaled ~ borrowed ≈ 1e26` raw and the index passes ~170× RAY.

Root cause is the multiplication order and domain: `scaled` is `amount × RAY` (27 extra decimals), so even modest token amounts with high decimals produce enormous raw values, and the index only needs ~170× growth — reachable on the steep segment of a two-slope rate curve at sustained ~98% utilization — to push `scaled × index` past `i128::MAX`. The in-repo test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361` demonstrates exactly this: `update_indexes`, `withdraw`, and `repay` all fail with `MATH_OVERFLOW`, and the comment confirms "the index cap never engages" and "every verb accrues first, so the market freezes: no repay, no withdraw, no liquidation."

### Impact Explanation
Permanent freezing of all funds in the affected `(hub, token)` market: suppliers cannot withdraw, borrowers cannot repay, liquidations and bad-debt cleanup (`seize_positions`, `recapitalize`) cannot run, and revenue is unclaimable — every path reverts in accrual before reaching its own logic. This is permanent freezing of user funds and protocol insolvency for that market's book, satisfying the acceptance criteria.

### Likelihood Explanation
Triggering requires (a) a listed market with high-decimals or large supply so `scaled` is large, (b) sustained near-max utilization on the steep rate segment long enough for the index to grow ~170×, and (c) no successful accrual checkpoint before the overflow threshold — the chunked accrual (`MAX_COMPOUND_DELTA_MS`) makes each step's growth bounded, but the *product* `borrowed × index` grows monotonically, so once crossed, every subsequent call fails. A single unprivileged attacker can drive this by supplying the whale principal and borrowing ~98% of it via `controller::supply`/`borrow`; thereafter only the passage of ledger time is needed. The capital requirement is high but is the attacker's own position at risk, and the freeze is irreversible once reached — consistent with a Medium severity.

### Recommendation
Reorder or bound the arithmetic in `common/src/rates/index.rs` and `common/src/rates/accrue_step` so the index caps engage before any `scaled × index` product can overflow: e.g., early-clamp the index when `new_index > min(MAX_BORROW_INDEX_RAY, i128::MAX / scaled)` before computing `borrowed.mul(new_index)`, or compute accrued interest as `borrowed × (new_index − old_index)` with a pre-checked delta, and use saturating (`mul_div_floor_saturating`-style) products in `calculate_supplier_rewards` and `update_supply_index`. Alternatively cap the borrow index at a per-market bound derived from `i128::MAX / supplied` at accrual time so the value ceiling can never be hit before the cap.

### Proof of Concept
1. List (or use) a market with an 18-decimal asset and a steep high-utilization rate curve; disable/avoid the max-utilization guard via legitimate sustained borrowing.
2. Unprivileged attacker calls `controller::supply` with `principal = 1e9 × 10^18` units, then `controller::borrow` for ~98% of it (backed by collateral in another market).
3. Advance ledger time; call `update_indexes` (permissionless-facing via controller flow). Within the documented horizon the accrual step panics inside `scaled_to_original`/`Ray::mul` with `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`.
4. Thereafter `withdraw`, `repay`, `liquidate`, `clean_bad_debt`/`seize_positions`, `recapitalize`, and `claim_revenue` on that market all revert permanently with `MathOverflow` in `interest::global_sync` — total freeze. Demonstrated verbatim by `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`.