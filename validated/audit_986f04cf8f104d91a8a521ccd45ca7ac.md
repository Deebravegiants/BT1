### Title
Accrual value overflow permanently freezes a high-utilization market before the borrow-index cap can engage - (File: common/src/rates/index.rs)

### Summary
The CVE's bug class is "invalid/extreme state configuration leading to denial of service." The analog in this codebase: the interest-accrual path multiplies scaled shares by the index (`supplied.mul(index)`, `borrowed.mul(index)`) *before* the `MAX_BORROW_INDEX_RAY` clamp can ever fire. On a large market held at high utilization long enough, `borrowed * new_borrow_index` overflows `i128` and panics with `MathOverflow` inside `accrue_step`/`global_sync`. Because every mutating entrypoint accrues first, the entire market freezes: no `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, `recapitalize`, or `update_indexes` can execute. The repository's own harness test demonstrates this deadlock and asserts the documented safety bound is wrong.

### Finding Description
- `interest::global_sync` runs on every market mutation and calls `accrue_step` per chunk (`contracts/pool/src/interest.rs:20-53`).
- Inside `accrue_step`, `calculate_supplier_rewards` computes `borrowed.mul(env, old_borrow_index)` and `borrowed.mul(env, new_borrow_index)` (`common/src/rates/index.rs:80-81`), and `update_supply_index` computes `supplied.mul(env, old_index)` (`common/src/rates/index.rs:34`). `Ray::mul` panics with `MathOverflow` when the RAY-scaled product exceeds `i128` (`common/src/math/fp_core.rs:108-118`).
- The intended bound `MAX_BORROW_INDEX_RAY` is applied only *after* the multiply in `update_borrow_index` (`common/src/rates/index.rs:13-19`), so on a market with ~`10^27`-scale scaled debt (e.g. a billion-unit 18-decimal asset), `borrowed * index` overflows when the index is only ~170× — orders of magnitude below the `1e36` cap. The cap is unreachable.
- Once the product overflows, accrual panics deterministically on every subsequent call. Since accrual precedes every verb, `withdraw` and `repay` revert with `MathOverflow`, so both suppliers and borrowers are permanently locked out; liquidation (which also accrues) cannot run either.
- The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` proves exactly this: after some years at 98% utilization on the XLM curve, `update_indexes` reverts with `MATH_OVERFLOW`, `last.borrow_index < MAX_BORROW_INDEX_RAY`, and `withdraw`/`repay` revert identically (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361`).

### Impact Explanation
Permanent freezing of all user funds in the affected `(hub, asset)` market: suppliers cannot withdraw, borrowers cannot repay, liquidations cannot execute, and `recapitalize`/`clean_bad_debt` cannot unstick it because all of them call `global_sync` first. The market is bricked; only a code upgrade (privileged) could recover it. This is reachable state on a production code path, not a hypothetical overflow — the accrual loop itself creates the poisoned state.

### Likelihood Explanation
A single unprivileged address cannot trigger this instantly; it requires a large market (scaled shares near `i128::MAX / index`) sustained at high utilization for years so the borrow index compounds to ~170×. That needs whale-scale capital plus either an 18-decimal market or governance-set high-rate parameters, and `max_utilization` disabled or set near 100%. Cost and time make it a Medium, but the trigger conditions are entirely permissionless (`supply`, `borrow`, and ledger time), and no privileged action is involved in reaching the cliff.

### Recommendation
Make accrual saturate rather than panic at the value ceiling:
- Use the saturating variant (`mul_div_floor_saturating`-equivalent for `Ray`) or a checked multiply in `calculate_supplier_rewards` and `update_supply_index`, and clamp `new_borrow_index` such that `borrowed * new_borrow_index` stays within `i128` — i.e. enforce the effective cap `i128::MAX / borrowed` (in RAY units) alongside `MAX_BORROW_INDEX_RAY`.
- Alternatively, detect overflow in `accrue_step`, clamp the index to the largest non-overflowing value, and mark the market so rates no longer accrue (rather than reverting), keeping exits reachable.

### Proof of Concept
The codebase already contains the executable proof, `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361`:

```rust
// setup: market "BIG18" (18 decimals), XLM rate curve, max utilization disabled
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);          // ~98% utilization

// advance years; each iteration calls update_indexes
loop {
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; }
}
// => Err(MathOverflow) with last.borrow_index < MAX_BORROW_INDEX_RAY

// market permanently frozen — every verb accrues first and panics:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

The panic originates in `calculate_supplier_rewards` (`common/src/rates/index.rs:80-83`), where `borrowed.mul(env, new_borrow_index)` exceeds `i128` while the index is still far below its `1e36` cap — the cap can never engage, so there is no recovery path short of a contract upgrade.