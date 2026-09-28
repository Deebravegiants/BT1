### Title
Permanent market freeze: RAY-value overflow in accrual triggers before the `MAX_BORROW_INDEX_RAY` cap - (File: common/src/rates/index.rs)

### Summary
Every state-changing verb accrues interest first (`global_sync` → `accrue_chunk` → `accrue_step`). Accrual computes the RAY-scaled total debt via `borrowed.mul(env, new_borrow_index)` in `calculate_supplier_rewards` (common/src/rates/index.rs:80-81), which panics with `MathOverflow` once `borrowed_shares * borrow_index / RAY` exceeds `i128::MAX`. Although `update_borrow_index` caps the index at `MAX_BORROW_INDEX_RAY` (index.rs:13-19), on a whale-scale market the RAY-value ceiling (`i128::MAX`) is reached while the index is still far below the cap — so the cap never engages. Once this state is reached, every subsequent accrual panics, permanently freezing the market: no `supply`, `withdraw`, `repay`, `borrow`, `liquidate`, `clean_bad_debt`, or `flash_loan` can execute for that asset, because all of them call `global_sync` first (contracts/pool/src/interest.rs:20-33).

### Finding Description
The memory-corruption class of CVE-2017-13784 (attacker-influenced state drives arithmetic into an out-of-bounds/crash condition) maps onto Soroban as unchecked-domain `i128` arithmetic. In `common/src/rates/index.rs`:

```rust
let old_total_debt = borrowed.mul(env, old_borrow_index);   // line 80
let new_total_debt = borrowed.mul(env, new_borrow_index);   // line 81
```

`Ray::mul` goes through `fp_core::mul_div_half_up`, which is overflow-safe for the intermediate product (I256 widening) but still panics when the *result* does not fit `i128`. The same applies to `update_supply_index` (index.rs:34, `supplied.mul(env, old_index)`) and `apply_bad_debt_to_supply_index` (contracts/pool/src/interest.rs:74). The borrow index is capped, but the cap compares `new_index.raw() > MAX_BORROW_INDEX_RAY` — it does not bound `borrowed * index`. For a market with `borrowed` scaled shares near the supply cap on an 18-decimal asset, the value product overflows at roughly `i128::MAX / borrowed` ≈ an index of ~170×, reached by sustained compound accrual on the steep segment of the rate curve long before `MAX_BORROW_INDEX_RAY`.

The protocol's own test demonstrates the freeze end-to-end: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-360) supplies 1e27 units of an 18-decimal asset, borrows 98% of it, advances time, and observes `MATH_OVERFLOW` from `update_indexes`, `withdraw`, and `repay`, with `borrow_index < MAX_BORROW_INDEX_RAY` — the index cap never engaged.

### Impact Explanation
Permanent freezing of funds. Once `borrowed * borrow_index` crosses `i128::MAX`, every entrypoint that accrues — `update_indexes`, `withdraw`, `repay`, `borrow`, `liquidate`, `clean_bad_debt`, `recapitalize`, `flash_loan`, `flash_position` — panics before touching balances. All supplier funds in that market (which can include other users' deposits, not just the attacker's) are unrecoverable; the debt can never be repaid, liquidated, or socialized. The freeze is permanent because accrual is monotonic in time: there is no transaction that reduces `borrowed` or the index without first accruing.

### Likelihood Explanation
An unprivileged attacker needs to (a) supply a very large principal to an 18-decimal market (the test uses ~1e9 whole tokens with caps lifted via `lift_caps`, i.e., at the market's own configured cap), and (b) borrow it to ~98% utilization so the index rides the steep segment of the curve. Accrual to the ~170× index takes on the order of years of ledger time, so this is a slow-burn griefing/insolvency path rather than an instant exploit; however it requires no privilege, no oracle manipulation, and no cooperation — just capital and time. Alternatively, any organic whale market left at high utilization drifts into the same cliff, making it an ambient protocol-insolvency condition. Severity: High impact, moderate likelihood → High/Medium.

### Recommendation
Bound the value product, not just the index:

- In `update_borrow_index` / `accrue_step`, cap the index at `min(MAX_BORROW_INDEX_RAY, i128::MAX * RAY / borrowed)` so `borrowed.mul(index)` can never overflow; equivalently compute the index ceiling dynamically from current scaled debt and supply.
- Alternatively, switch total-debt/supply-value computations to a saturating path (`mul_div_floor_saturating`, already used for `grown` in `update_supply_index` line 41 and `protocol_fee_shares` line 95) so accrual degrades gracefully instead of panicking — a saturated index still permits withdraw/repay/liquidate.
- Enforce supply/borrow caps such that `max_scaled * MAX_BORROW_INDEX_RAY / RAY <= i128::MAX` at listing time, so the value ceiling is unreachable by construction.

### Proof of Concept
The harness test is a working PoC (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360):

```rust
let principal = BILLION * 10i128.pow(18);          // whale supply on 18-dec asset
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;                   // 98% utilization
t.borrow_raw(ALICE, "BIG18", debt);
loop { t.advance_time(YEAR_SECS);
       if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e } }
// -> MathOverflow; then:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Both calls fail inside `global_sync` → `accrue_step` → `calculate_supplier_rewards` before any balance is touched, confirming every supplier's funds in the market are permanently locked while `borrow_index < MAX_BORROW_INDEX_RAY`.