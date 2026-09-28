### Title
Unprivileged accrual triggers `i128` RAY-value overflow in `scaled_to_original` before the index cap engages, permanently freezing every market verb - (File: common/src/rates/index.rs)

### Summary
The bug class in the report is a crafted input driving a computation into a fatal overflow, producing a denial of service. The XOXNO Lending analog: an unprivileged user can create a market state (very large supplied principal at sustained high utilization on a steep rate curve) where the borrow index growth eventually makes `borrowed * borrow_index` overflow `i128` inside `scaled_to_original`/`Ray::mul`. Because every controller verb calls `global_sync` first, the first panic bricks the market permanently: no repay, no withdraw, no liquidation, no `clean_bad_debt`. The `MAX_BORROW_INDEX_RAY` cap never engages because the panic happens on the *value* (`scaled * index`) before the index itself reaches the cap.

### Finding Description
- `update_borrow_index` caps the new index at `MAX_BORROW_INDEX_RAY` (common/src/rates/index.rs:13-19), so the index is bounded — but nothing bounds `scaled_to_original(borrowed, borrow_index)` = `borrowed.mul(borrow_index)`.
- `Ray::mul` resolves to `mul_div_*` in `common::math::fp_core`, which widens to `I256` and then `to_i128` panics with `GenericError::MathOverflow` when the product exceeds `i128` (common/src/math/fp_core.rs:300-303). `scaled_to_original` and `calculate_utilization` call it unchecked (contracts/pool/src/cache/scale.rs:19-27).
- Accrual runs unconditionally at the head of every operation: `global_sync` loops chunks into `accrue_chunk` → `accrue_step` → `update_borrow_index` / `calculate_supplier_rewards`, all of which compute `borrowed.mul(index)` (contracts/pool/src/interest.rs:20-53, common/src/rates/index.rs:80-81).
- The existing harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361) demonstrates exactly this: a ~1e27-token, 18-decimal market at 98% utilization on the XLM curve overflows within ~40 years of compounding; the test asserts `borrow_index < MAX_BORROW_INDEX_RAY` at failure (cap never engaged) and that `withdraw` and `repay` both revert with `MATH_OVERFLOW`.

### Impact Explanation
Permanent freezing of funds, market-wide. Once the accrual overflows, `global_sync` panics before any state change, so all subsequent `supply`/`withdraw`/`borrow`/`repay`/`liquidate`/`clean_bad_debt`/`flash_*` calls on that (hub, token) book revert. Suppliers cannot exit, borrowers cannot repay, liquidators cannot clear positions, and bad-debt cleanup (`apply_bad_debt_to_supply_index`, contracts/pool/src/interest.rs:73-89) is unreachable. The panic is deterministic and unrecoverable — there is no admin path that skips accrual, so the freeze is not temporary.

### Likelihood Explanation
An unprivileged address reaches this purely through `supply`, `borrow`, and permissionless `update_indexes` — no privileges required. However, it demands whale-scale capital in a single market (the test uses ~1 billion × 10^18 base units, i.e. an 18-decimal asset with effectively unlimited cap lifted) and years of sustained near-max utilization on a curve with a high `max_borrow_rate`. For realistic listed assets with smaller token supplies, enforced supply/borrow caps, and active liquidations keeping utilization off the cliff, the overflow horizon moves far out or becomes unreachable. Severity: Medium — catastrophic impact gated by extreme capital/time requirements; it also partially self-defends since the attacker’s own supplied principal is frozen.

### Recommendation
Make accrual saturating rather than panicking:
- In `calculate_supplier_rewards` / `calculate_utilization` / `scaled_to_original`, use a saturating variant (`mul_div_floor_saturating` already exists in `fp_core`) or clamp `borrowed`/`supplied` scaled totals so `scaled * index` can never exceed `i128::MAX`.
- Alternatively, enforce the `MAX_BORROW_INDEX_RAY` cap by checking the *value* product (`borrowed * index`) rather than the index alone, and freeze accrual (keep `last_timestamp` advancing) once the ceiling is hit, so verbs continue to work.
- Enforce per-market supply caps in asset terms that guarantee `max_supply_scaled * MAX_BORROW_INDEX_RAY < i128::MAX` at market registration time.

### Proof of Concept
Encoded by the existing test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`:

```rust
// BIG18: 18-decimal market on the steep XLM curve, caps lifted.
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);            // unprivileged supply
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // 98% utilization
loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; } // permissionless accrual
}
// e == GenericError::MathOverflow, book("BIG18").borrow_index < MAX_BORROW_INDEX_RAY
// Both revert forever:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Root cause chain: `update_indexes` → `global_sync` (`contracts/pool/src/interest.rs:20`) → `accrue_step` → `calculate_supplier_rewards` (`common/src/rates/index.rs:80-83`) → `Ray::mul` → `to_i128` panic (`common/src/math/fp_core.rs:300-303`).

Caveat: I was limited in iterations and did not verify whether asset-registration code enforces a supply cap that would make `scaled * MAX_BORROW_INDEX_RAY` unconditionally fit `i128` for all admissible markets; if such an invariant is enforced at listing time, the reachable surface shrinks to markets whose caps were set above the bound (a configuration risk rather than code bug).