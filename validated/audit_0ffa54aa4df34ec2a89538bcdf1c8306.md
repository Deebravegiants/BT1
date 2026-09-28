### Title
Sustained high-utilization accrual overflows the RAY value ceiling in `scaled_to_original`, permanently freezing the market and all supplier funds - (File: contracts/pool/src/cache/scale.rs)

### Summary
CVE-2017-13685 is a crash-on-crafted-input bug: a specific input drives `dump_callback` into an unrecoverable abort (EXC_BAD_ACCESS), denying service. The XOXNO Lending analog is a reachable arithmetic overflow inside index accrual: once a market's scaled borrow value approaches the `i128`/RAY value ceiling, `scaled_to_original` panics with `MathOverflow` on every accrual. Because every user-facing verb (`supply`, `withdraw`, `repay`, `borrow`, `liquidate`, `claim_revenue`) accrues the market index first, the panic permanently bricks the market — suppliers can never withdraw and borrowers can never repay.

### Finding Description
Interest accrual converts scaled debt to native units via `scaled_to_original` in `common/src/rates/scaling.rs` and `contracts/pool/src/cache/scale.rs`. The multiplication `scaled * index` can exceed `i128::MAX` even though the borrow index itself stays below `MAX_BORROW_INDEX_RAY`, so the index cap in `common/src/constants/pool.rs` never engages before the value overflow.

The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360) drives an 18-decimal market holding ~1e9 whole tokens at ~98% utilization on the steep XLM rate curve, calling the permissionless `update_indexes` entrypoint repeatedly. Within the test's bound the accrual panics with `GenericError::MathOverflow`, and afterward `try_withdraw_raw` and `try_repay` both fail with the same `MathOverflow` — "the market is frozen: exits and repayments accrue first and hit the same panic." The test also notes the safety bound documented in `docs/reference/formulas.md` does not hold, so this is not a documented/accepted parameter choice.

Every step is reachable by a single unprivileged address: `supply` and `borrow` build the position (spoke caps can be configured high, and the test lifts them via the same unprivileged listing config), and `update_indexes` is callable by anyone to advance accrual. No privileged call is required at any step.

### Impact Explanation
Permanent freezing of funds / contract unable to operate for the affected market: once the accrual panics, all mutations that touch the market revert forever. Supplier principal, borrower exit paths, liquidations, and revenue claims for that market are unreachable; tokens custodied in the pool for that market's book cannot leave. This maps directly to the CVE's class — an input-driven crash that permanently denies service — but with durable on-chain state corruption rather than a process restart.

### Likelihood Explanation
Likelihood is low but nonzero, consistent with Medium. It requires an unusually large market (order ~1e9 units of an 18-decimal asset at ~98% utilization) sustained on a steep rate curve for an extended horizon (tens of years at the tested curve segment, less under more aggressive configured rate models). No off-chain cooperation, oracle manipulation, or privilege is needed; an attacker funding the supply/borrow legs can trigger it purely through `supply`, `borrow`, and `update_indexes`. The deterministic arithmetic guarantees the freeze once the value ceiling is crossed, and there is no recovery path short of a Wasm upgrade.

### Recommendation
Bound the accrual math, not just the index:
- In `scaled_to_original`/accrual, clamp or saturate the scaled-to-native conversion and/or cap the accrual step so `scaled * index` cannot overflow `i128`; alternatively enforce `MAX_BORROW_INDEX_RAY` at a value low enough that the conversion is provably safe for the maximum possible scaled total.
- Prefer `checked_mul`-based saturating accrual that stops index growth at the ceiling instead of panicking, so the market degrades (interest stops accruing) rather than bricks.
- Add a regression test asserting withdraw/repay still succeed after the index reaches its cap.

### Proof of Concept
From `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356` (condensed):

```rust
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);              // unprivileged supply
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // ~98% utilization
loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; } // anyone can call
}
// -> MathOverflow while borrow_index < MAX_BORROW_INDEX_RAY
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

After the overflow, every market-touching verb reverts permanently; supplier and borrower funds are frozen.