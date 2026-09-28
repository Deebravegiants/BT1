### Title
Accrual `borrowed × borrow_index` `i128` overflow panics before the borrow-index cap can engage, permanently freezing a whale market - (File: common/src/rates/index.rs)

### Summary
The bug class is an integer overflow in a size computation causing denial of service (libxml2 `xmlBuildQName` overflow → stack overflow). The analog in XOXNO Lending is an `i128` overflow in the *value* computation `scaled_borrowed × borrow_index` during interest accrual. `update_borrow_index` caps the index at `MAX_BORROW_INDEX_RAY`, but `calculate_supplier_rewards` multiplies the full RAY-scaled share supply by the new index *before* that cap protects anything — when the product exceeds `i128::MAX`, `Ray::mul` panics with `MathOverflow`. Because every pool verb runs `global_sync` (accrual) first, one panic permanently freezes the market: no supply, withdraw, borrow, repay, liquidate, flash, or bad-debt cleanup can ever execute again. This is proven by the repository's own harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361`), which shows withdraw and repay reverting with `MATH_OVERFLOW` forever while `borrow_index < MAX_BORROW_INDEX_RAY` — i.e. the documented cap never engaged.

### Finding Description
Accrual path:

1. `global_sync` (`contracts/pool/src/interest.rs:20-33`) chunks elapsed time and calls `accrue_chunk` → `accrue_step`.
2. `accrue_step` calls `update_borrow_index` (`common/src/rates/index.rs:13-19`), which clamps the *index* at `MAX_BORROW_INDEX_RAY`.
3. It then calls `calculate_supplier_rewards` (`common/src/rates/index.rs:73-89`), which computes `new_total_debt = borrowed.mul(env, new_borrow_index)` — a checked `i128`/`I256` `mul_div` that panics with `GenericError::MathOverflow` when `borrowed_shares × index / RAY` does not fit `i128` (`common/src/math/fp_core.rs:148-159`, `to_i128` conversion).

Shares are RAY-scaled (`amount × 10^(27 − decimals)`), so on an 18-decimal market a supply of ~10^9 whole tokens already produces ~10^36 RAY shares; an index of ~100–170× RAY makes the product exceed `i128::MAX ≈ 1.7e38`. The index cap bounds the index, not the product, so the overflow happens strictly before the cap could stop growth — confirmed by the harness assertion `last.borrow_index < MAX_BORROW_INDEX_RAY` at the freeze point.

Note that `update_supply_index` (`common/src/rates/index.rs:34`) has the same exposure via `supplied.mul(env, old_index)`, and `apply_bad_debt_to_supply_index` (`contracts/pool/src/interest.rs:74`) via `cache.supplied().mul(supply_index)` — but the borrow-side panic is the one that triggers first in normal accrual.

Reachable entrypoints (unprivileged): `supply`/`borrow` to build the position, then `update_indexes` (permissionless) or any subsequent `withdraw`/`repay`/`liquidate`/`flash_loan` — all accrue first and hit the same panic.

### Impact Explanation
Permanent freezing of funds. Once the panic condition is reached, every state-changing entrypoint on that market reverts, so all suppliers' deposits, all borrowers' collateral backing, and all unclaimed revenue are frozen forever; the pool contract cannot operate. Unlike a transient revert, no future call can unwind it because the overflow lives in accrual itself, which precedes every verb.

### Likelihood Explanation
Requires an extreme but reachable state: a very large share base (whale-scale supply, easiest on high-decimal assets where the RAY multiplier is small) combined with sustained near-max utilization so the borrow index compounds toward ~100×+ RAY. The harness reaches the cliff in well under 40 years at 98% utilization on the steep curve segment. An attacker cannot accelerate time, so this is a slow-burn, market-scale condition rather than a single-transaction exploit — Medium severity at most. It is not a "fail-closed DoS" in the rejected sense: the revert is irreversible and locks real user funds, not just the attacker's call.

### Recommendation
Bound the *value* domain, not just the index:
- In `calculate_supplier_rewards` and `update_supply_index`, compute totals with `mul_div_floor_saturating` (or clamp `borrowed`/`supplied` share totals at listing time to `i128::MAX / MAX_BORROW_INDEX_RAY × RAY`) so accrual degrades gracefully instead of panicking.
- Enforce a `total_shares` cap per market via `require_cap_within_asset_domain`-style validation so `shares × MAX_*_INDEX` always fits `i128`.
- Update `docs/reference/formulas.md`: the documented bound is wrong (the harness test asserts this), so the published safety limit understates the real cliff.

### Proof of Concept
Reproduced by `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`:

```rust
let principal = BILLION * 10i128.pow(18);          // whale supply, 18 decimals
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;                   // ~98% utilization
t.borrow_raw(ALICE, "BIG18", debt);
// advance time in 1-year steps until accrual panics
if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; }
assert_contract_error(failed, errors::MATH_OVERFLOW);
assert!(last.borrow_index < MAX_BORROW_INDEX_RAY); // cap never engaged
// market is now permanently frozen:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Root cause: `new_total_debt = borrowed.mul(env, new_borrow_index)` in `common/src/rates/index.rs:81` panics on `i128` overflow; the index clamp at lines 15-17 bounds the index, not the product, so the overflow fires first and, since `global_sync` precedes every verb (`contracts/pool/src/interest.rs:20-33`), the market is unrecoverable.