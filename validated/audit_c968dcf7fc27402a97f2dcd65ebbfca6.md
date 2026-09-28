### Title
RAY-value overflow in interest accrual permanently freezes a large, heavily-borrowed market before the borrow-index cap engages - ([File: common/src/rates/index.rs])

### Summary
The CVE bug class is a crash/DoS triggered by an invalid value reaching a dereference. The Soroban analog is a permanent, market-wide freeze: interest accrual panics on `i128` overflow while computing total debt value, and because every controller verb accrues first, the entire market becomes uncallable.

### Finding Description
`global_sync` runs at the head of every pool operation and calls `accrue_chunk`, which delegates to `accrue_step`. Inside `accrue_step`, `calculate_supplier_rewards` computes `borrowed.mul(env, new_borrow_index)` — i.e., `scaled_to_original(borrowed, borrow_index)` — as a raw `i128` product of two RAY values divided by RAY. This product overflows `i128` when the total debt's RAY value exceeds `i128::MAX` (~1.7e38). The `MAX_BORROW_INDEX_RAY` cap (`1e36` raw, i.e., index ≤ 1e9×) is applied inside `update_borrow_index` to the *index* only; it does not bound `borrowed * index`, which depends on debt size. The in-repo test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates the exact sequence: with a ~$1B-scale 18-decimal market borrowed to 98% utilization on a steep rate curve, the debt's RAY value crosses `i128::MAX` while `borrow_index < MAX_BORROW_INDEX_RAY`, the accrual panics with `MathOverflow`, and subsequent `withdraw` and `repay` calls revert identically. Since `scaled_to_original`/`Ray::mul` panic via `panic_with_error!`, there is no recovery path — the panic is state-persistent.

### Impact Explanation
Permanent freezing of funds: once the debt's RAY value exceeds `i128::MAX`, every entrypoint that touches the market — `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `update_indexes`, `claim_revenue`, `recapitalize` — traps in accrual before reaching its own logic. Suppliers cannot exit, borrowers cannot repay, liquidators cannot liquidate, and bad debt cannot be cleaned. The market's funds are locked in the contract indefinitely (TTL extension and upgrades aside, which are out of scope).

### Likelihood Explanation
Reachable by unprivileged addresses using only `supply` + `borrow`: an attacker supplies a large 18-decimal token market, a second party (or the same wallet with collateral) borrows to ~98% utilization, and then anyone — including the attacker — lets interest compound. The trigger requires whale-scale capital and sustained high utilization over an extended accrual horizon (the test reaches the cliff via repeated yearly `advance_time`), so likelihood is moderate rather than high; but the cap that was designed to prevent index unboundedness (`MAX_BORROW_INDEX_RAY`) provably does not prevent this overflow, since the overflow is in the debt *value*, not the index.

### Recommendation
Bound the product, not just the index. Options: (a) enforce a protocol-wide maximum on the RAY-denominated total debt per market (`borrowed.mul(borrow_index) <= i128::MAX` headroom) checked at `borrow`/`flash_position` time; (b) tighten `MAX_BORROW_INDEX_RAY` dynamically against live `borrowed` so `borrowed * MAX_BORROW_INDEX_RAY / RAY` stays in `i128`; or (c) make accrual saturate (cap `new_total_debt` at `i128::MAX` / treat accrual as complete) rather than panic, so the market remains operable at the cliff.

### Proof of Concept
`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs` already encodes the exploit end-to-end:
1. `lift_caps` removes supply/borrow caps; `supply_raw(BOB, "BIG18", 10^9 * 10^18)` seeds the market.
2. `borrow_raw(ALICE, "BIG18", 98% of principal)` drives utilization into the curve's steep segment.
3. Loop `advance_time(YEAR_SECS)`; within the tested horizon `try_update_indexes_for(&["BIG18"])` returns `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`.
4. `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", 1.0)` both revert with `MATH_OVERFLOW` — the market is permanently frozen.

Relevant code: `contracts/pool/src/interest.rs` (`global_sync`, `accrue_chunk`), `common/src/rates/index.rs` (`update_borrow_index` caps only the index; `calculate_supplier_rewards` panics on `borrowed.mul(new_borrow_index)`), `common/src/rates/scaling.rs` (`scaled_to_original`), `common/src/constants/pool.rs` (`MAX_BORROW_INDEX_RAY`).