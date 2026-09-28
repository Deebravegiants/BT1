### Title
Sustained accrual overflows `i128` in `scaled_to_original` before the index cap engages, permanently freezing the market - ([File: common/src/rates/index.rs])

### Summary
The pool accrues interest via `accrue_step` → `calculate_supplier_rewards`, which computes `borrowed.mul(env, new_borrow_index)` — a raw `i128` product of scaled debt (RAY units) times the borrow index. `update_borrow_index` clamps the *index* at `MAX_BORROW_INDEX_RAY` (≈10⁹·RAY), but that clamp only bounds the multiplier, not the product: `scaled_debt × new_index` overflows `i128::MAX` long before the cap is reached when total debt is whale-scale. The multiplication panics inside `Ray::mul` (`scaled_to_original` in `common/src/rates/scaling.rs:14`), and because `interest::global_sync` runs at the head of every market verb (`Cache::load` → accrue → mutate → commit), the panic bricks the market entirely.

### Finding Description
Two unchecked products exist on the accrual path:

- `calculate_supplier_rewards` at `common/src/rates/index.rs:80-81`: `borrowed.mul(env, old_borrow_index)` and `borrowed.mul(env, new_borrow_index)`. `Ray::mul` computes `a*b/RAY` in `i128`; with `borrowed` ≈ i128::MAX/170 in scaled units and the index grown past ~170×RAY, the intermediate `a*b` exceeds `i128::MAX` and panics with `MathOverflow`.
- `update_supply_index` at `common/src/rates/index.rs:34`: `supplied.mul(env, old_index)` has the same exposure for whale-scale supply.

The index ceilings (`MAX_BORROW_INDEX_RAY` / `MAX_SUPPLY_INDEX_RAY` in `common/src/constants/pool.rs:19-23`) clamp the index value only — they give no protection to the value product. `MAX_COMPOUND_DELTA_MS` chunking in `global_sync` (`contracts/pool/src/interest.rs:20-33`) limits per-step rate growth but does not shrink `borrowed`, so a later chunk panics identically.

Once `borrowed × borrow_index` crosses the `i128` ceiling, every call that loads the market — `withdraw`, `repay`, `borrow`, `supply`, `update_indexes`, liquidation-driven `repay`/`seize_positions`, `claim_revenue`, `recapitalize` — accrues first and panics. There is no recovery path: indexes are monotone (`borrow_index` only grows), accrual cannot be skipped, and nothing writes the index back down.

### Impact Explanation
Permanent freezing of funds and complete market DoS — the direct analog of the CVE's "hang or frequently repeatable crash (complete DOS)" plus unauthorized state effect (accrual continuing to move debt while exits are impossible). All suppliers' deposits, all borrowers' collateral backing, and all accrued revenue in that `(hub, asset)` market become unreachable forever. Borrowers cannot repay (so even honest borrowers' positions drift into bad-debt territory in accounting terms), liquidators cannot clear the market, and the protocol cannot socialize or recapitalize it — every cleanup path accrues first and hits the same panic. The in-repo harness test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-360` demonstrates exactly this: `update_indexes`, `withdraw`, and `repay` all revert with `MathOverflow`, and the index cap never engages.

### Likelihood Explanation
Reachable by a single unprivileged address using only public entrypoints: `supply` a whale-scale position in an 18-decimal market, `borrow` near the utilization cap, then let interest compound (or keep calling `update_indexes` as time passes). The harness reaches the cliff with principal ≈ 10⁹·10¹⁸ and ~98% utilization on the steepest listed curve segment within a few years — below the 40-year bound documented in `docs/reference/formulas.md`. The barrier is capital scale and sustained high utilization rather than privilege or timing precision, which caps severity at Medium, but no admin action, oracle manipulation, or third-party behavior is required.

### Recommendation
Compute accrued interest without forming the overflowing product. In `calculate_supplier_rewards` (`common/src/rates/index.rs:80-81`), compute `accrued_interest` as `borrowed.mul(env, new_index − old_index)` (or equivalently `borrowed * (new−old) / RAY` via `mul_div`), which keeps the intermediate proportional to the *delta* rather than the absolute debt value, and only then add it to `old_total_debt` if the absolute total is truly needed. Alternatively use a widened/saturating `mul_div` for these products and clamp `accrued_interest` instead of trapping. The same treatment applies to `update_supply_index`'s `supplied.mul(env, old_index)` at `common/src/rates/index.rs:34`. A fallback that treats an overflowing accrual as "accrue nothing, keep indexes" would convert a permanent freeze into a rate-saturation event.

### Proof of Concept
From `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-360` (unprivileged calls only):

```rust
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);              // whale supply
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // ~98% utilization

loop {                                              // pure time passage
    t.advance_time(YEAR_SECS);
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; }
}
// All three now panic with MathOverflow — market permanently frozen:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
assert!(book(&t, "BIG18").borrow_index < MAX_BORROW_INDEX_RAY); // cap never engaged
```

Call chain per verb: entrypoint → `Cache::load` → `interest::global_sync` (`contracts/pool/src/interest.rs:20`) → `accrue_step` → `calculate_supplier_rewards` (`common/src/rates/index.rs:80`) → `Ray::mul` → `scaled_to_original` (`common/src/rates/scaling.rs:14`) → `MathOverflow` panic, reverting the whole call before any state mutation or token movement.