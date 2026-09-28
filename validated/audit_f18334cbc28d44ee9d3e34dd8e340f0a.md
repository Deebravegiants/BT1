### Title
Debt-value overflow in interest accrual permanently freezes a market — no repay, withdraw, or liquidation possible - (File: common/src/rates/index.rs)

### Summary
An unprivileged user can drive a hub market into a state where every entrypoint panics with `MathOverflow`, permanently freezing all supplied and borrowed funds. Analogous to CVE-2024-30253 (untrusted input causes a crash → loss of availability), here a user-created book state (large `borrowed` scaled shares growing via `borrow_index`) makes the accrual arithmetic exceed `i128`, and since accrual runs at the head of every market mutation, the market is bricked forever. The bug is already demonstrated by an in-repo test.

### Finding Description
Every pool mutation loads the market and runs `global_sync` first (`contracts/pool/README.md` documents `Cache::load → interest::global_sync → mutate`). `global_sync` calls `accrue_step`, which computes `new_total_debt = borrowed.mul(env, new_borrow_index)` in `calculate_supplier_rewards` (`common/src/rates/index.rs:80-81`). `Ray::mul` is a half-up `mul_div` whose product must fit `i128`; `scaled_to_original` likewise panics on unrepresentable results (`common/src/rates/scaling.rs:14-16`).

`borrowed` scaled shares are attacker-controlled: an unprivileged `supply`/`borrow` on the controller mints debt shares at ceiling rounding. `borrow_index` grows monotonically and is only capped at `MAX_BORROW_INDEX_RAY` (10^36 raw). For a market with an 18-decimal asset and ~10^9 whole tokens of debt (debt value ~10^36 ray), the product `borrowed * borrow_index` overflows `i128` (~1.7e38) once the index exceeds ~170× — reachable at sustained ~98% utilization on the steep segment of the configured curve, well before the index cap engages.

Once the product overflows, `update_indexes`, `withdraw`, `repay`, `borrow`, `net_settle`, `seize_positions` (used by `liquidate`), `recapitalize`, and `claim_revenue` all panic on accrual. Nothing in the code path resets or bounds `borrowed` before the multiply, so the panic is permanent.

### Impact Explanation
Permanent freezing of user funds and market-wide denial of service on the affected (hub, token) book: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate or clean bad debt, and `recapitalize`/`update_indexes` fail. Since hub markets share one physical pool balance, all suppliers of that asset lose access to their deposits.

### Likelihood Explanation
Requires a whale-scale position (~10^9 whole tokens for an 18-decimal asset, less for lower-decimal... actually the cliff is at ray-value `i128::MAX`, so ~10^11 whole tokens at 7 decimals) plus sustained high utilization for several years — but it requires no privilege and no oracle manipulation, only ordinary `supply`/`borrow` calls and time. The repo's own harness test reaches the cliff within 40 simulated years at 98% utilization on the XLM curve.

### Recommendation
Bound the accrual multiply rather than panicking: in `accrue_step`/`calculate_supplier_rewards` (`common/src/rates/index.rs:80-83`), clamp `new_borrow_index` such that `borrowed * new_borrow_index` stays representable (i.e., apply the `MAX_BORROW_INDEX_RAY` cap *before* the debt multiply, or early-exit the step when `borrowed * index` would overflow and pin the index at its cap). Alternatively, saturate `scaled_to_original` in the accrual path so `MathOverflow` cannot brick every subsequent market verb.

### Proof of Concept
The repository already contains an executable PoC: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs::a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (lines 315-361). It supplies 10^9 18-decimal tokens, borrows 98% of it under the `xlm_curve`, advances time year-by-year calling `update_indexes`, and observes:

- `try_update_indexes_for(["BIG18"])` → `Error(Contract, #33)` (`MATH_OVERFLOW`) while `borrow_index < MAX_BORROW_INDEX_RAY` (the cap never engaged);
- subsequent `try_withdraw_raw` and `try_repay` both panic with `MATH_OVERFLOW` — exits and repayments accrue first and hit the same panic.

Steps: `supply(caller, account, spoke, [(hub_asset(BIG18), 1e27 units)])` → `borrow(...)` at ~98% utilization → wait / advance ledger time → `update_indexes` panics in `global_sync → accrue_step → borrowed.mul(new_borrow_index)` → the market is frozen permanently.