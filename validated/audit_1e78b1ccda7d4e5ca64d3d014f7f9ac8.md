### Title
Permissionless accrual panics on i128 value overflow before the borrow-index cap engages, permanently freezing the market - (File: common/src/rates/simulate.rs)

### Summary
The JerryScript bug is an assertion reachable by unprivileged input (a crash class). The analog in XOXNO Lending is a reachable `MathOverflow` panic inside the interest-accrual step: `accrue_step` unscales market totals via `scaled_to_original`, a plain `Ray::mul` that panics on i128 overflow, before the `MAX_BORROW_INDEX_RAY` clamp in `update_borrow_index` can run. Any address can trigger it through `update_indexes`, and once the market's scaled totals times index exceed `i128::MAX`, every verb that accrues first — `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `flash_loan`, `claim_revenue` — reverts on the same panic. The market's funds are permanently frozen; the index ceiling designed to bound growth never engages.

### Finding Description
`accrue_step` computes utilization by un-scaling both legs first: `scaled_to_original(env, borrowed, borrow_index)` and `scaled_to_original(env, supplied, supply_index)` at `common/src/rates/simulate.rs:60-61`. `scaled_to_original` is just `scaled.mul(env, index)` at `common/src/rates/scaling.rs:14-16`, which panics with `GenericError::MathOverflow` on overflow — there is no saturation like `calculate_scaled_cap` uses. The index clamp in `update_borrow_index` (`common/src/rates/index.rs:13-19`) runs only *after* those multiplications, so a market whose `borrowed * borrow_index` or `supplied * supply_index` exceeds `i128::MAX` (≈1.7e38) traps before the 1e36 index cap can stop growth. A billion-whole-token market is ~1e36 ray, so the index only needs to grow past ~170x — far below the 1e9x index cap — before every accrual panics. `docs/reference/formulas.md:432-437` concedes "valid caps and bounded indexes do not guarantee that future accrual fits," but the shipped bound it states is wrong per the test comment at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:338-340`, and the failure mode — a hard panic that blocks repayment and liquidation — is not a graceful degradation.

### Impact Explanation
Permanent freezing of funds and protocol insolvency for the affected market. The regression test proves the end state: after the cliff, `withdraw` and `repay` both revert with `MATH_OVERFLOW` (`large_positions_and_long_horizons.rs:354-356`). Since liquidation also accrues first, underwater debt cannot be liquidated, bad debt cannot be cleaned or socialized, suppliers cannot exit, and the treasury cannot claim revenue. There is no admin escape hatch either — `recapitalize` and governance operations touching that market run the same accrual.

### Likelihood Explanation
Reaching the cliff requires a whale-scale position (the test uses 10^9 whole tokens of an 18-decimal asset, `BILLION * 10i128.pow(18)`) and sustained near-cap utilization on the steep curve segment for multiple years (`large_positions_and_long_horizons.rs:321-346`). That is expensive and slow, not a one-shot attack, and it requires a listed market with lifted/near-saturated caps. However, every step is fully unprivileged (`supply`, `borrow`, `update_indexes`), the state is monotone so the freeze cannot be reversed once crossed, and an attacker can deliberately hold utilization high to accelerate it while earning yield. Severity lands at Medium given the extreme economic cost and long horizon versus a permanent, unrecoverable freeze.

### Recommendation
Saturate rather than panic in the accrual path: use `mul_div_floor_saturating` (as `calculate_scaled_cap` already does) for the un-scaling in `accrue_step`, or apply the `MAX_BORROW_INDEX_RAY` / `MAX_SUPPLY_INDEX_RAY` clamps to the *stored* index before un-scaling so the cap actually engages ahead of the value ceiling. Alternatively, add a guard at borrow/supply entry that rejects positions whose worst-case accrued value (scaled amount × index cap) cannot fit `i128`, and emit an alarm as indexes approach the value ceiling so keepers can deleverage the market.

### Proof of Concept
The repository's own regression test demonstrates it end-to-end (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`):

```rust
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
lift_caps(&t, "BIG18", 18);
t.supply_raw(BOB, "BIG18", BILLION * 10i128.pow(18));        // unprivileged supply
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98);          // 98% utilization

loop {                                                       // unprivileged update_indexes
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; }
}
// -> Error(Contract, MATH_OVERFLOW) inside scaled_to_original, index < MAX_BORROW_INDEX_RAY
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

The panic originates at `common/src/rates/simulate.rs:60-61` via `scaled_to_original` (`common/src/rates/scaling.rs:14-16`), before `update_borrow_index`'s cap at `common/src/rates/index.rs:13-19` can run.

Caveat: this is a documented arithmetic limit per `docs/reference/formulas.md:432-437`, which the scan rules flag for rejection — however the doc's stated bound is itself wrong (the test asserts "the bound in docs/reference/formulas.md is wrong") and the designed index ceiling fails to engage, so the panic reaching before the intended safeguard is a genuine defect rather than a deliberate design trade-off.