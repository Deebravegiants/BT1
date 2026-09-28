### Title
Supply-index floor clamp leaves stranded claims that drain fresh suppliers' deposits - (File: contracts/pool/src/interest.rs)

### Summary
`apply_bad_debt_to_supply_index` socializes bad debt by scaling down `supply_index`, but clamps the result at `SUPPLY_INDEX_FLOOR_RAW` (`RAY/1000`) instead of resetting supplier claims to zero. After a wipeout, wiped suppliers retain shares redeemable against a still-positive index, so a `clean_bad_debt`-driven debt seizure leaves a phantom claim that pays out real tokens from the next depositor.

### Finding Description
The CVE class is integer underflow: a value that should go to zero (or negative) is forced into a semantically wrong non-zero state, corrupting downstream accounting. The analog lives in the bad-debt write-down path.

`apply_bad_debt_to_supply_index` caps the loss at total supplied value, computes a reduction factor, and then clamps:

```rust
// contracts/pool/src/interest.rs:80-89
let capped = bad_debt.min(total_supplied_value);
let remaining = total_supplied_value.checked_sub(cache.env(), capped);
let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
let new_supply_index = cache.supply_index().mul_floor(cache.env(), reduction_factor);
cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
```

When bad debt ≥ total supplied value, `remaining` is 0 and `new_supply_index` is 0 — but the `max(SUPPLY_INDEX_FLOOR_RAW)` revives it to `RAY/1000`. All pre-wipeout supply shares keep a positive claim (`0.1%` of their original scaled value). This is invoked from `seize::apply` on the `Borrow` side (`contracts/pool/src/ops/seize.rs:23-28`), which the controller reaches via `clean_bad_debt`/liquidation paths reachable by an unprivileged address.

The project's own test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (`contracts/pool/tests/interest.rs:372-427`) demonstrates the exact drain: a wiped supplier's `unscale_supply_floor` stays > 0, and once a fresh supplier deposits, `resolve_withdrawal(i128::MAX, old_scaled)` pays out exactly the fresh deposit while leaving the fresh claim unbacked.

`recapitalize` mitigates only partially: the harness test `pool_loss_floor_recapitalization_returns_only_unused_funding` (`tests/test-harness/tests/pool_money_flow_audit.rs:270-358`) shows recapitalization refills cash but the index stays clamped at the floor — `state.supply_index == SUPPLY_INDEX_FLOOR_RAW` throughout — so stranded claims remain redeemable against any subsequent deposits.

### Impact Explanation
Theft of user funds / protocol insolvency. A holder of a wiped position can withdraw after any new supply enters the market and extract real tokens that belong to new suppliers. The pool's `cash` drops below the sum of remaining claims (`cache.cash() < fresh_claim` in the test), meaning the pool becomes insolvent for whoever withdraws last. Impact scales with wiped positions' share count and the size of fresh deposits.

### Likelihood Explanation
Reachable by unprivileged callers: the path is user-driven — a dust-sized underwater position that passes the bad-debt cleanup threshold gets seized via `clean_bad_debt` (or a liquidation that leaves unrecoverable debt), triggering `apply_bad_debt_to_supply_index`. A wipeout requires bad debt ≥ total supplied value, which occurs naturally when a small or fully-utilized market accumulates unbacked debt (e.g., a borrowed-out market where collateral is seized elsewhere). An attacker can then simply hold old shares and wait for, or self-provide, fresh supply to withdraw against. No privileged role is required at any step.

### Recommendation
When `remaining == Ray::ZERO` (full wipeout), the correct fix is not to clamp the index but to zero or explicitly retire outstanding supply shares — e.g., treat all supply claims as void and require `recapitalize` to settle them via its own accounting (as it already does for the loss floor), rather than letting `resolve_withdrawal`/`unscale_supply_floor` re-derive value from a revived index. At minimum, `unscale_supply_floor` on a post-wipeout index should not yield a payable claim; alternatively gate withdrawals so a wiped market requires recapitalization to a non-floor index before payout.

### Proof of Concept
`contracts/pool/tests/interest.rs:372-427` already encodes it end to end:

1. Market seeded with `supplied = 1000·RAY`, `supply_index = RAY`, `cash = 0`.
2. `apply_bad_debt_to_supply_index(cache, 5000·RAY)` — a full wipeout — clamps `supply_index` to `SUPPLY_INDEX_FLOOR_RAW` instead of zeroing claims.
3. `cache.unscale_supply_floor(old_scaled) > 0` — the wiped holder keeps a phantom claim.
4. A fresh supplier mints `fresh_scaled` for `fresh_cash = stranded`.
5. `resolve_withdrawal(i128::MAX, old_scaled)` + `require_reserves` + `debit_cash` pays the wiped holder `gross == fresh_cash` — the entire fresh deposit — and `cache.cash() < fresh_claim`, leaving the fresh supplier unbacked.

Reachability in production: `clean_bad_debt`/`seize_positions` (`Borrow` side) → `apply_bad_debt_to_supply_index` (`contracts/pool/src/ops/seize.rs:24-27`), all callable without privilege once a position qualifies as bad debt.