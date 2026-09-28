### Title
Permanent market freeze: accrual's `scaled * index` multiplication overflows `i128` before the borrow-index cap, bricking every verb on the market — (`contracts/pool/src/interest.rs`)

### Summary
The bug class behind ALPINE-CVE-2017-3309 is a low-privileged user reaching a code path that reliably crashes the service (complete DoS). The analog in XOXNO Lending is a reachable arithmetic trap — not a budget limit — in the mandatory accrual step: `global_sync` runs `accrue_step`, whose first statement computes `scaled_to_original(borrowed, borrow_index)` = `borrowed * borrow_index / RAY` with checked `i128` multiplication. On a large high-utilization market, compounding pushes this product past `i128::MAX` while `borrow_index` is still far below `MAX_BORROW_INDEX_RAY`, so the index ceiling never engages. Every mutating verb on the market accrues first (`Cache::load → global_sync → mutate`), so once the product overflows, `supply`, `borrow`, `withdraw`, `repay`, `update_indexes`, `recapitalize`, `seize_positions`, `claim_revenue`, `net_settle`, `flash_loan`, `create_strategy` and all controller paths routed through them (`liquidate`, `clean_bad_debt`, strategies) permanently panic with `MathOverflow`.

### Finding Description
`accrue_step` unscales debt and supply with checked fixed-point multiplication:

- `common/src/rates/simulate.rs:60-61` — `scaled_to_original(env, borrowed, borrow_index)` and `scaled_to_original(env, supplied, supply_index)` call `Ray::mul` → `fp_core::mul_div_half_up`, which traps on `i128` overflow (MathOverflow, error 33).
- `contracts/pool/src/interest.rs:20-33` — `global_sync` loops `accrue_chunk` over the elapsed interval at the head of every mutation; there is no catch, skip, or cap-aware short-circuit.
- `common/src/rates/index.rs` `update_borrow_index` caps the *index* at `MAX_BORROW_INDEX_RAY` (10^36 raw), but the value product `borrowed_scaled * index` overflows `i128` (~1.7e38) long before the cap for large books — the cap protects the index, not the product.
- The panic is sticky: once `borrowed * borrow_index` overflows, the next accrual recomputes the same (larger) product. `last_timestamp` is only stamped after the loop completes (`cache.mark_accrued()`), so the market can never advance past the overflow.

The repo's own harness demonstrates the end state: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-360` supplies a 1e9·10^18-unit market, borrows 98%, advances time, and observes `try_update_indexes_for`, `try_withdraw_raw`, and `try_repay` all fail with `MATH_OVERFLOW`, with the comment "the market freezes: no repay, no withdraw, no liquidation. The index cap never engages."

Reachability for an unprivileged address: any user can `supply` an 18-decimal listed asset in whale size (caps can be large and `with_max_utilization_disabled`/high `max_utilization` are governance-admitted configurations, not attacker-controlled parameters), `borrow` near the utilization bound, and simply leave the position open — or directly call the permissionless `controller.update_indexes(caller, assets)` (`contracts/controller/src/lib.rs:370-372`) as time accrues. The attacker needs no privilege and no further action after the borrow; compounding itself drives the product over the cliff, at which point *all* suppliers' and revenue shares in that `(hub, token)` book are frozen forever, since there is no path that mutates the market without accruing first, and `apply_bad_debt_to_supply_index`/`seize_positions` also run `global_sync` before writing.

### Impact Explanation
Permanent freezing of user funds and protocol insolvency mechanics: every supplier's deposit in the affected market is locked (withdraw accrues → panic), borrower debt cannot be repaid or liquidated (repay/liquidate/seize accrue → panic), protocol revenue cannot be claimed, and the pool cannot even be recapitalized. There is no recovery path short of contract upgrade/migration. This matches the accepted impact "permanent freezing of funds" / "contract unable to operate."

### Likelihood Explanation
Medium. It requires a very large book (value within ~170× of the `i128` ceiling at scale) and sustained high utilization for years, or governance listing a high-decimal asset with generous caps — the harness reaches it in a few years at the XLM curve's steep segment with ~$10^30-scale liquidity. It is not a one-transaction attack: cost is the capital supplied/borrowed, and the trigger is passive time. But the preconditions are entirely reachable by ordinary unprivileged supply/borrow calls, the outcome is deterministic (monotone index growth makes the overflow inevitable rather than probabilistic), and nothing in the code bounds `borrowed * index` or lets a caller skip accrual.

### Recommendation
In `accrue_step` (and the `global_sync` loop), avoid computing `borrowed * borrow_index` in `i128` when it can exceed the ceiling: clamp the borrow index against the maximum value that keeps `borrowed_scaled * index / RAY` representable (a per-market value ceiling analogous to `MAX_BORROW_INDEX_RAY`), or compute the utilization inputs via `I256`/`mul_div` widened math and saturate the *rate inputs* rather than trapping. At minimum, cap `new_borrow_index` at `min(cap, i128-safe bound for current borrowed)` so accrual degrades to "no more interest" instead of a permanent panic — mirroring the existing sticky-cap behavior at `MAX_BORROW_INDEX_RAY`.

### Proof of Concept
See `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-360`:

```rust
t.supply_raw(BOB, "BIG18", principal);          // 1e9 * 10^18 units
t.borrow_raw(ALICE, "BIG18", debt);             // 98% utilization
// advance years; each update_indexes re-runs global_sync -> accrue_step
// until borrowed * borrow_index overflows i128:
assert_contract_error(t.try_update_indexes_for(&["BIG18"]), MATH_OVERFLOW);
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), MATH_OVERFLOW); // supplier funds frozen
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), MATH_OVERFLOW);    // debt unclosable
assert!(last.borrow_index < MAX_BORROW_INDEX_RAY);                          // cap never engaged
```

The trace is: `withdraw/repay/update_indexes` → `ops::*` → `Cache::load` → `interest::global_sync` (`contracts/pool/src/interest.rs:20-33`) → `accrue_step` (`common/src/rates/simulate.rs:60`) → `Ray::mul` checked `i128` multiply → `MathOverflow` → transaction aborts → state unchanged → next call panics identically, forever.