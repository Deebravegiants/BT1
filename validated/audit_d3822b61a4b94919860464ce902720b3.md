### Title
Accrual arithmetic overflow permanently freezes a market — `MathOverflow` panic in `scaled_to_original`/`accrue_step` bricks all operations on that market - ([File: common/src/rates/index.rs](common/src/rates/index.rs))

### Summary
Analogous to CVE-2018-20217 (a reachable assertion that crashes the KDC on a crafted request), the pool's permissionless interest-accrual path contains a reachable `i128` overflow panic. Once a market's scaled debt value `borrowed * borrow_index / RAY` approaches the `i128` ceiling, `accrue_step` panics with `GenericError::MathOverflow` (`#33`) inside `Ray::mul`/`scaled_to_original`. Because every market-mutating entrypoint runs `global_sync` → `accrue_chunk` first, the panic bricks the entire market: no supply, withdraw, borrow, repay, liquidation, bad-debt cleanup, or revenue claim can ever execute again. All supplier funds and borrower collateral routed through that market are permanently frozen.

### Finding Description
- `contracts/pool/src/interest.rs:39-53` — `accrue_chunk` calls `accrue_step`, which computes `borrowed.mul(env, old_borrow_index)` / `new_total_debt` etc. in `common/src/rates/index.rs:80-86` (`calculate_supplier_rewards`). These use panicking `Ray::mul`, which internally is `mul_div_half_up` — it panics with `MathOverflow` when `x * y / d` does not fit `i128` (`common/src/math/fp_core.rs:104-118`).
- The index cap `MAX_BORROW_INDEX_RAY` does not engage first: `update_borrow_index` caps the *index*, but the debt *value* (`borrowed × index`) overflows before the cap is reached for large books. This is proven by the repository's own harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-362`), which demonstrates that after the cliff is reached, `try_withdraw_raw` and `try_repay` both fail with `MATH_OVERFLOW` and the borrow index is still below `MAX_BORROW_INDEX_RAY`.
- `update_indexes` is permissionless (the fuzz harness notes "update_indexes is permissionless, so the caller chooses how a span is partitioned into accruals", `tests/fuzz/fuzz_targets/rates_and_index.rs:375-378`), so any unprivileged address advances accrual and can push the market across the cliff.
- Reachability by an unprivileged attacker: supply a large position (caps are configurable and the harness test lifts them), borrow to ~98% utilization (`borrow` is permissionless subject to collateral, and `max_utilization` up to `< RAY` is allowed per `guards.rs:19-34`), then repeatedly call `update_indexes`. Each call advances accrual by the real elapsed ledger time; at sustained high utilization the borrow index compounds until the value multiplication overflows, at which point the panic becomes permanent and unrecoverable — there is no code path that lowers `borrowed` or `borrow_index` without first accruing.
- `docs/reference/invariants.md` INV-IDX-01 acknowledges the shape ("Debt-value overflow can still revert accrual before that ceiling is reached") but treats it as a bound, not the resulting permanent freeze of all market funds.

### Impact Explanation
Permanent freezing of funds: once `borrowed * borrow_index` crosses the `i128` representable domain, every entrypoint on that market reverts in `global_sync` before any state change or escape hatch can run. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, governance `recapitalize`/`clean_bad_debt` paths that touch the market accrue first and revert too. All tokens held by the pool for that market are locked forever — the accepted "permanent freezing of funds / contract unable to operate" impact class.

### Likelihood Explanation
Medium. The trigger requires a large book (billions of a high-decimal asset, e.g. an 18-decimal asset where `supply caps` are lifted or sized generously) and sustained high utilization so the borrow index compounds toward the value ceiling — real ledger time must elapse, so it cannot be done atomically. However, no privileged action is needed: an attacker with sufficient capital controls supply size, utilization (via their own borrow), and the accrual trigger (`update_indexes` is permissionless). The protocol's own test suite confirms the cliff is reachable and that the index cap does not prevent it.

### Recommendation
- In `accrue_step`/`calculate_supplier_rewards` and `update_supply_index`, use saturating (`mul_div_floor_saturating`) or widened `I256` arithmetic for debt/supply value computations, and clamp accrual (e.g., stop growing `borrow_index` once the value domain is exhausted) instead of panicking — mirroring how `update_supply_index` already uses `mul_div_floor_saturating` at `common/src/rates/index.rs:41` while `calculate_supplier_rewards` uses panicking `mul`.
- Add a per-market circuit breaker: when `borrowed.mul(index)` approaches `i128::MAX`, freeze *accrual only* and let repay/withdraw/liquidate proceed against the last accrued indexes, so funds remain exitable.
- Enforce caps so `supply_cap × MAX_BORROW_INDEX_RAY / RAY < i128::MAX` per market decimals, validating at listing/`update_indexes` parameter changes.

### Proof of Concept
The repository ships the exploit as a regression test — `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`:

```rust
// supply ~1e27 raw of an 18-dec asset, borrow 98%, then advance time
// until try_update_indexes_for("BIG18") fails:
assert_contract_error(failed, errors::MATH_OVERFLOW);
assert!(last.borrow_index < MAX_BORROW_INDEX_RAY); // cap never engaged
// market permanently frozen:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

An unprivileged attacker reproduces this on a live deployment by: (1) supplying a large amount of a high-decimal, high-rate-curve market; (2) borrowing near `max_utilization` against their own collateral on a separate market; (3) calling `update_indexes(market)` periodically as ledger time accrues until `accrue_step` panics; (4) the market is thereafter bricked for all users — every subsequent call reverts in `global_sync` before reaching any recovery path.