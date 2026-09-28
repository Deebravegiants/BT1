### Title
Ray-value `i128` overflow in interest accrual permanently freezes a whale market (no repay, withdraw, or liquidation) - ([File: common/src/rates/scaling.rs])

### Summary
Analogous to CVE-2022-0608 (integer overflow leading to corruption), the pool's fixed-point engine overflows `i128` when unscal­ing `scaled_shares * index` inside `accrue_step`. Because every mutating entrypoint runs `global_sync` first, once a market's borrowed or supplied ray-value crosses `i128::MAX`, the trap bricks the market forever: suppliers cannot withdraw, borrowers cannot repay, and liquidators cannot liquidate. This is proven by an in-repo test.

### Finding Description
`accrue_step` begins by unscaling both book totals:

```rust
// common/src/rates/simulate.rs:60-61
let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
let supplied_original = scaled_to_original(env, supplied, supply_index);
```

`scaled_to_original` is `Ray::mul` → `fp_core::mul_div_half_up(env, scaled, index, RAY)`, which raises `GenericError::MathOverflow` when the result does not fit `i128` (`common/src/rates/scaling.rs:14-16`, `docs/reference/formulas.md` "Unrepresentable results raise `MathOverflow`"). The borrow index is capped at `MAX_BORROW_INDEX_RAY = 10^36`, but that cap does not bound `borrowed * borrow_index`: a market holding ~1e11 whole tokens of debt hits `i128::MAX` when the index is only ~170x — far below the 10^9x cap.

`global_sync` in `contracts/pool/src/interest.rs:20-33` runs `accrue_chunk` → `accrue_step` at the top of every pool mutation (`supply`, `withdraw`, `borrow`, `repay`, `liquidate`, `clean_bad_debt`, `flash_loan`, `update_indexes`, etc.). After the overflow point, every one of these calls panics in `scaled_to_original`, so no state transition on that market can ever execute again.

The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360`) demonstrates exactly this: a 1e9-whole-token market at ~98% utilization on a steep rate curve traps `MATH_OVERFLOW`, then `try_withdraw_raw` and `try_repay` both fail with the same error, with `borrow_index < MAX_BORROW_INDEX_RAY` (the cap never engaged).

### Impact Explanation
Permanent freezing of user funds and protocol insolvency on the affected market: all supplied tokens are locked in the pool contract forever, all debt becomes uncollectable, liquidations are impossible, and `clean_bad_debt`/`recapitalize` cannot run because they accrue first. A single unprivileged attacker can be the one to push the market over the cliff — supply a large amount (permissible up to the admitted cap, which can be as high as `i128::MAX / 10^(27-d)`), borrow against separate collateral to keep utilization high, then simply let time pass and call the permissionless `update_indexes`. Unlike a temporary fail-closed DoS, the panic is state-determined: every future call re-traps on the same multiplication, so the freeze is irreversible.

### Likelihood Explanation
Reaching the cliff requires a market whose debt ray-value approaches `i128::MAX` (~170 billion whole tokens), i.e., a very large cap and whale-scale capital or many years of high-utilization compounding — the steep-curve test crosses it within 40 years. These are arithmetic limits, not typical sizes, so likelihood is low on small markets; however, no protocol mechanism prevents it: the index cap engages too late, caps only gate entry (exits still trap), and any whale-scale market with a steep `slope3` curve drifts toward the cliff autonomously since utilization drifts upward as debt compounds faster than supply.

### Recommendation
Bound the product, not just the index: in `accrue_step`/`update_borrow_index`, clamp accrual when `borrowed * borrow_index / RAY` or `supplied * supply_index / RAY` would exceed `i128::MAX` — e.g., freeze index growth (as the `MAX_BORROW_INDEX_RAY` cap already does) instead of letting `scaled_to_original` trap, or compute utilization and rewards through the existing `I256` widened path (`mul_div_*` already widens internally; the panic comes from the `i128` result bound, so a saturating or widened-valuation variant is needed). Additionally, when admitting a cap, derive the maximum safe scaled total from `i128::MAX / MAX_BORROW_INDEX_RAY` rather than the raw token-to-RAY maximum, so an admitted market can never reach the cliff before the index cap.

### Proof of Concept
Existing in-repo PoC: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360`. Conceptually:

1. On a market with an 18-decimal asset and a steep borrow curve (e.g., the test's `xlm_curve()`, max 175% APR), attacker-supplied liquidity plus a 98%-utilization borrow creates `borrowed * borrow_index` approaching `i128::MAX`.
2. Advance time (anyone can call `pool.update_indexes` / controller `update_indexes`); accrual eventually makes `scaled_to_original(env, borrowed, borrow_index)` panic with `MathOverflow` at `common/src/rates/scaling.rs:15` via `fp_core::mul_div_half_up`, while `borrow_index < MAX_BORROW_INDEX_RAY`.
3. Thereafter `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, and `supply` all re-enter `global_sync` → `accrue_step` and trap identically, permanently locking all supplied funds in that market's pool.