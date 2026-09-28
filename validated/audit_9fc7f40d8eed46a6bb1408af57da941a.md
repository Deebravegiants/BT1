### Title
Permanent market freeze when accrued debt value overflows i128 inside `accrue_step` before the borrow-index cap engages - ([File: common/src/rates/simulate.rs])

### Summary
Every state-changing pool entrypoint first runs `interest::global_sync`, which calls `accrue_step`. The step computes `borrowed_original = scaled_to_original(borrowed, borrow_index)`, a `Ray` multiplication that panics with `MathOverflow` on `i128` overflow. On a large market kept at high utilization, the borrow index compounds until `borrowed * borrow_index / RAY` exceeds `i128::MAX` — well before `update_borrow_index`'s `MAX_BORROW_INDEX_RAY` cap can stop accrual. From that point every accrual panics, so `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, and even the permissionless `update_indexes` all revert on that market forever. The protocol's own harness test proves this freeze end-to-end.

### Finding Description
- `contracts/pool/src/interest.rs:20-53` — `global_sync` loops over chunks and calls `accrue_chunk`, which invokes `accrue_step` and commits the new indexes.
- `common/src/rates/simulate.rs:60-66` — `accrue_step` computes `scaled_to_original(env, borrowed, borrow_index)` before the index cap is consulted.
- `common/src/rates/scaling.rs:14-16` — `scaled_to_original` is a raw `Ray::mul` (`scaled * index / RAY`, half-up), which panics with `MathOverflow` (33) when the product exceeds `i128`.
- `contracts/pool/README.md:159-168` — every mutation (`supply`, `borrow`, `withdraw`, `repay`, `seize_positions`, `create_strategy`, `claim_revenue`) runs `Cache::load → interest::global_sync` first, so the panic is on the entry path of all of them.
- `contracts/controller/src/markets.rs:119-125` — `update_indexes` is a permissionless keeper entrypoint (`require_authorized_caller` only authenticates the caller); anyone can trigger the accrual that crosses the cliff.
- The repository's own test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361` demonstrates the exact scenario: a 1-billion-token (18-decimal) market at ~98% utilization on the steep XLM curve panics with `MATH_OVERFLOW` inside accrual while `borrow_index < MAX_BORROW_INDEX_RAY` ("the index cap did not engage before the value overflow"), and the test asserts that subsequent `withdraw` and `repay` fail identically — "the market is frozen: no repay, no withdraw, no liquidation".

### Impact Explanation
Permanent freezing of funds for every participant in the affected `(hub, token)` book: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, bad debt cannot be cleaned, and `recapitalize` (which also syncs) cannot rescue it. Once the cliff is reached the condition is self-perpetuating — the very next accrual always recomputes the same overflowing product, and no governance flag or parameter change reverts it without a code upgrade.

### Likelihood Explanation
Reachable entirely by unprivileged actions: any borrower can draw a market to high utilization, and `update_indexes` is callable by any authenticated address. The requirements are a very large pool (on the order of a billion whole tokens of an 18-decimal asset, or correspondingly less time for larger books), a steep configured rate curve (test uses 175% max APR — a governance-listed parameter), and years of uninterrupted high utilization. Debt compounds faster than supply, so utilization drifts upward on an untouched book even without further attacker action. This matches the Medium severity of CVE-2021-2412: a deterministic complete-DoS crash of a core function requiring attacker-shaped input plus time, but no privileged access.

### Recommendation
Bound the accrual against the value-domain ceiling, not just the index cap:
- In `accrue_step` (`common/src/rates/simulate.rs`), clamp `new_borrow_index` additionally so that `scaled_to_original(borrowed, new_borrow_index)` cannot overflow `i128` — i.e. cap the index at `i128::MAX * RAY / borrowed` (saturating division, like `calculate_scaled_cap` does) — or switch the utilization/debt computation to a saturating `mul_div_floor_saturating` so accrual degrades gracefully instead of trapping.
- At minimum, use saturating math for `borrowed_original`/`supplied_original` so the panic moves off the entry path of every market verb, letting withdrawals and repayments proceed to stop further growth.

### Proof of Concept
Encoded by the repo's own test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`):

```rust
let principal = BILLION * 10i128.pow(18);          // 18-decimal whale market
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;                    // ~98% utilization
t.borrow_raw(ALICE, "BIG18", debt);

loop { t.advance_time(YEAR_SECS);                   // unprivileged: just wait
    if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; } }

// panics with MathOverflow INSIDE accrual, index cap never reached:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

After the cliff, a single permissionless `controller.update_indexes(caller, [hub_asset])` call triggers `global_sync → accrue_step → scaled_to_original`, which panics; the same panic then bricks every subsequent mutation of that market permanently.