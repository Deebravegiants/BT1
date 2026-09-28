### Title
Accrual-time RAY value overflow permanently freezes an overgrown market — (`common/src/rates/simulate.rs:60`, `common/src/rates/scaling.rs:14`)

### Summary
Analog to CVE-2020-14809 (unauthenticated-adjacent availability loss via a hang/repeatable crash in the server's core processing path): every state-changing pool/controller verb runs interest accrual first, and `accrue_step` computes `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` unconditionally. Once `borrowed * borrow_index` (or `supplied * supply_index`) exceeds the `i128` RAY value ceiling, the multiply-divide panics with `GenericError::MathOverflow`, so the market can never accrue again and every repay/withdraw/liquidate/borrow against it reverts forever — the book is frozen before the documented index ceiling ever engages.

### Finding Description
`accrue_step` (common/src/rates/simulate.rs:51-94) is the single accrual implementation run by the mutating path `contracts/pool/src/interest.rs::global_sync` (lines 20-33, via `accrue_chunk`) and by the view path `simulate_update_indexes`. Its first two statements are

```rust
let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
let supplied_original = scaled_to_original(env, supplied, supply_index);
```

where `scaled_to_original` is `scaled.mul(env, index)` (common/src/rates/scaling.rs:14-16) and `Ray::mul` bottoms out in `mul_div_half_up`, which panics with `GenericError::MathOverflow` when `scaled * index / RAY` leaves `i128` (common/src/math/fp_core.rs:108-118, including the widened `I256` path whose `to_i128()` returns `None`).

The borrow index is capped at `MAX_BORROW_INDEX_RAY` (10^36, i.e., 10^9×RAY) inside `update_borrow_index`, but the *value* product `borrowed * new_borrow_index` in the rewards computation and the unscale at the top of the step have no such cap: `borrowed` can legitimately reach ~`1.7e38` raw RAY (the token-to-RAY input maximum, ~170 billion whole tokens), so an index of only ~170×RAY overflows `i128` — long before the 10^9×RAY index ceiling. The borrow index is monotone and accrual is unavoidable, so once the market crosses this threshold, `global_sync` panics on every subsequent call. The repository's own harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:315-361) demonstrates exactly this: after enough years at 98% utilization on the XLM curve, `update_indexes`, `withdraw`, and `repay` all revert with `MATH_OVERFLOW`, and `last.borrow_index < MAX_BORROW_INDEX_RAY` — "the index cap did not engage before the value overflow."

### Impact Explanation
Permanent freezing of funds, which is an accepted impact class. Once the product `borrowed * borrow_index` exceeds `i128::MAX`:

- `repay` reverts → borrowers cannot deleverage, so the debt (and the panic) persists forever.
- `withdraw` reverts → all suppliers' funds in that market are permanently locked.
- `liquidate` reverts → liquidators cannot clear the position; the account's collateral in other markets may also be effectively stuck if risk evaluation must value this leg.
- `update_indexes` reverts → even the permissionless keeper path cannot advance the market.

Because the panic happens before any index write, there is no on-chain way to recover; the panic is deterministic and repeatable, matching the CVE's "hang or frequently repeatable crash (complete DOS)" class. The docs acknowledge the limit (docs/reference/formulas.md:432-437, docs/explanation/threat-model.md:317-324) but the freeze is a real reachable state, not a documented safe degradation.

### Likelihood Explanation
Reachable by an unprivileged address through `supply` and `borrow` alone, but requires enormous capital and time: the attacker (or organic market growth) must push a market's scaled supply/debt near the ~170-billion-whole-token RAY domain maximum and sustain high utilization so the borrow index compounds ~170× before the market deleverages. Caps (`calculate_scaled_cap`) bound admitted size but can be set at or near the domain maximum, and the ceiling is a function of `borrowed`, not attacker trickery. Medium likelihood: high capital cost and slow compounding, but permissionless and irreversible once triggered — and the same panic can also be reached organically on any very large, long-lived, high-utilization market, with no alarm when approaching the cliff ("No dedicated ceiling alarm is emitted", formulas.md:436-437).

### Recommendation
Make accrual fail-open at the domain boundary instead of trapping:

- In `accrue_step`, compute `borrowed_original`/`supplied_original` with the saturating variant (`mul_div_floor_saturating`) or detect the overflow and clamp the borrow index growth for that step so `borrowed * borrow_index` stays in `i128` — the index ceiling at `MAX_BORROW_INDEX_RAY` should engage (halting further borrower interest) *before* the value product overflows.
- Alternatively, bound `borrowed`/`supplied` admission (caps and `calculate_scaled_borrow`/`calculate_scaled_supply`) so that `scaled * MAX_BORROW_INDEX_RAY` fits `i128`, enforcing the invariant at entry rather than discovering it at accrual.
- Emit an event when an index approaches the effective ceiling so integrators can deleverage before the freeze.

### Proof of Concept
Existing harness test reproduces it end-to-end (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361):

```rust
let principal = BILLION * 10i128.pow(18);          // 1e9 whole 18-decimal tokens
t.supply_raw(BOB, "BIG18", principal);             // unprivileged supply
let debt = principal / 100 * 98;                   // 98% utilization
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);                // unprivileged borrow
// advance time year by year on the XLM curve until accrual fails:
t.try_update_indexes_for(&["BIG18"])               // -> MATH_OVERFLOW
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
assert!(last.borrow_index < MAX_BORROW_INDEX_RAY); // index cap never engaged
```

All subsequent calls that touch the market (`supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `flash_loan`, `update_indexes`) run `global_sync` first and revert identically, permanently.