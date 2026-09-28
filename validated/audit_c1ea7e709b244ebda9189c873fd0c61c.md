### Title
Saturating a market's scaled RAY value permanently freezes the market — borrow, repay, withdraw and liquidate all revert in accrual - (File: common/src/rates/simulate.rs)

### Summary
The bug class of CVE-2006-7254 — an unhandled input condition leaves a resource permanently unusable — maps onto the lending pool's index accrual. Every state-changing verb accrues interest first, and the first step of accrual computes `scaled_to_original(borrowed, borrow_index)`, a plain `i128` RAY multiplication that panics on overflow. A single unprivileged account can push `borrowed * borrow_index` over `i128::MAX` by borrowing near the per-market cap, after which every subsequent call that touches the market reverts with `MathOverflow`. The market is frozen permanently: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and `update_indexes` itself cannot recover because it is the function that panics.

### Finding Description
`accrue_step` in `common/src/rates/simulate.rs:60` unscales the scaled borrow total at the current borrow index with `scaled_to_original`, which is `scaled.mul(env, index)` — a checked `i128` mul_div that panics on overflow (`common/src/rates/scaling.rs:14-16`). The borrow index ceiling is `MAX_BORROW_INDEX_RAY = 10^36` (i.e., `1e9` × initial index), but the RAY value domain overflows `i128` (~`1.7e38`) long before that ceiling is reached, as the protocol's own documentation acknowledges: "Value overflow can occur before the index ceiling and block repayment/withdrawal because those operations accrue first" (`docs/reference/formulas.md:434-437`).

The reachable path: an attacker supplies tokens up to a market's configured cap and calls `borrow` to take the scaled `borrowed` total to a large fraction of `i128::MAX`. Token-to-RAY upscaling admits up to ~`170 billion` whole tokens (`docs/reference/formulas.md:429`), so `borrowed` scaled ≈ `1.6e38` is admissible whenever governance has lifted caps toward the domain maximum. At a `borrow_index` even marginally above `1 RAY` (reached by any interest accrual), `scaled_to_original` overflows. The harness reproduces this cliff: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` shows `try_update_indexes_for`, `try_withdraw_raw`, and `try_repay` all reverting with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361`).

Once `borrowed * index > i128::MAX`, there is no fallback path: `accrue_step` has no saturating branch or error return, every controller verb (`withdraw`, `repay`, `borrow`, `liquidate`, `clean_bad_debt`, `flash_loan`, `supply`) runs accrual first, and there is no owner-only index repair — `recapitalize` restores cash shortfalls but does not roll back the index or reduce scaled `borrowed`. The freeze is therefore permanent, not transient.

### Impact Explanation
Permanent freezing of all supplier funds in the affected market. Every supplier's tokens are locked in the pool with no withdrawal path, borrower collateral backing the debt is likewise frozen, and the market can never accrue, liquidate, or socialize bad debt again. This is the "permanent freezing of funds" / "contract unable to operate" acceptance class, reachable by an unprivileged address through ordinary `supply`/`borrow`/`update_indexes` calls.

### Likelihood Explanation
Likelihood is moderate rather than high because the attack demands whale-scale capital: the scaled borrow total must approach `i128::MAX` in RAY terms, which requires caps set near the domain maximum (~170 billion whole tokens) and the attacker must actually fund the borrow demand and the collateral. However, on a genuinely large listed market (the test uses 1 billion whole tokens as a plausible cell, not a contrived one), normal usage plus a few years of compounding at steep utilization reaches the same cliff without any attacker — the overflow is a function of book size and time, not attacker privilege. An attacker with sufficient capital can trigger it deliberately by borrowing near the cap so that the next accrual overflows immediately rather than after years. No privileged role, oracle manipulation, or third-party cooperation is required.

### Recommendation
Make accrual overflow-safe instead of panic-propagating:

- In `accrue_step` (`common/src/rates/simulate.rs:60-61`), compute `borrowed_original` / `supplied_original` with a saturating mul_div (the pattern already used by `calculate_scaled_cap` via `mul_div_floor_saturating` in `common/src/rates/scaling.rs:26-33`), clamping the unscaled value at `i128::MAX` rather than panicking. Utilization saturates at `RAY` and rate/index updates remain computable, keeping repay/withdraw/liquidate callable.
- Alternatively, cap the *scaled RAY value* a market may hold — enforce `scaled_borrowed * MAX_BORROW_INDEX_RAY / RAY <= i128::MAX` (and the analogous supply bound) at `supply`/`borrow` entry, so accrual can never overflow within the index's own lifetime; the documented bound in `docs/reference/formulas.md:432-437` explicitly notes that valid caps do not currently guarantee this.
- Ensure at least one verb remains executable on a saturated market (e.g., allow `repay` and `withdraw` to proceed on the last-good index when accrual overflows), so the failure mode degrades to "no further interest" instead of a permanent freeze.

### Proof of Concept
The repository's own harness test demonstrates the freeze end-to-end (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`):

```rust
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
lift_caps(&t, "BIG18", 18);
lift_caps(&t, "COL", 7);
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);              // whale supply, permissionless
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // 98% utilization

// advance time; accrual eventually panics inside scaled_to_original
let failure = loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; }
};
assert_contract_error(Err::<(), _>(failure), errors::MATH_OVERFLOW);

// market permanently frozen — every verb accrues first and hits the same panic
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Key properties: only unprivileged entrypoints (`supply`, `borrow`, `update_indexes`, `withdraw`, `repay`) are used; the panic occurs at `borrow_index < MAX_BORROW_INDEX_RAY`, so the index cap never engages and no recovery path exists; and no pause, flag, or governance action is involved. An attacker can compress the multi-year timeline to a single transaction by sizing the borrow so `borrowed * (RAY + ε)` already exceeds `i128::MAX`, making the very next accrual overflow.