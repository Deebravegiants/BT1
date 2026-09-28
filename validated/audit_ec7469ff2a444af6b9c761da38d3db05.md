### Title
RAY-value overflow in accrual permanently freezes a market before the index cap engages - (File: common/src/rates/index.rs)

### Summary
Every state-changing entrypoint on a market first runs `global_sync` → `accrue_chunk` → `accrue_step`, which calls `calculate_supplier_rewards`. That function computes `borrowed.mul(new_borrow_index)` and `borrowed.mul(old_borrow_index)` in `i128` and panics with `GenericError::MathOverflow` when the product leaves the domain. Because the panic happens inside accrual, which every verb (`supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `flash_loan`, `update_indexes`, `claim_revenue`, `recapitalize`) executes first, the entire market freezes permanently: no repayment, no withdrawal, no liquidation, no bad-debt cleanup. The borrow-index ceiling (`MAX_BORROW_INDEX_RAY = 1e36`) does not protect against this — the debt *value* overflows `i128` long before the index reaches its cap, so the clamp in `update_borrow_index` never engages.

### Finding Description
`calculate_supplier_rewards` multiplies the scaled borrowed share total by both indexes and subtracts (common/src/rates/index.rs:80-83):

```rust
let old_total_debt = borrowed.mul(env, old_borrow_index);
let new_total_debt = borrowed.mul(env, new_borrow_index);
let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);
```

`Ray::mul` is `x * y / RAY` half-up; it widens to `I256` only for the *intermediate* product — the *result* must still fit `i128` (~1.7e38). With scaled `borrowed` near the admitted cap (`~i128::MAX / 10^(27-d)` asset units → ~1.7e38 RAY for an 18-decimal token), the representable debt value is exhausted once the borrow index grows past ~1x–170x depending on size, i.e. `borrowed * index / RAY > i128::MAX`. The same overflow class exists in `update_supply_index` at `supplied.mul(old_index)` (index.rs:34) and in `supply_index_reward_shortfall` (index.rs:60-63).

This is the exact analog of the Crab `normalizationFactor` revert: a monotonically growing accumulator crosses an arithmetic boundary at a corner of (size × time), and the revert is on a path every operation must traverse, so the contract is blocked rather than merely rejecting one bad input. The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360) demonstrates the freeze end-to-end: `update_indexes`, `withdraw`, and `repay` all return `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`.

### Impact Explanation
Permanent freezing of user funds and protocol insolvency on the affected market. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate (so positions going underwater cannot be closed), and `clean_bad_debt`/`recapitalize` also accrue first and revert — there is no administrative escape since the panic precedes any state write. All supplied tokens and unclaimed yield/revenue in that `(hub, token)` book are frozen indefinitely.

### Likelihood Explanation
No privileged action is required to create the precondition: any unprivileged address can `supply` up to the market cap and `borrow` up to utilization. After that, only the passage of time is needed — utilization drifts upward because debt compounds faster than supply, and on steep curves the index reaches the cliff. Constraints that temper likelihood: the market must be very large (order of billions of whole tokens at 18 decimals, within the ~170B admission cap), utilization must stay high for an extended period, and no one may successfully call `update_indexes` often enough to matter (calling it does not help — accrual itself is what panics once the product overflows, and earlier accruals do not reduce `borrowed`). Mitigating note: docs/reference/formulas.md:432-437 acknowledges this as an arithmetic limit ("Value overflow can occur before the index ceiling and block repayment/withdrawal"), which weakens novelty but does not remove the impact path.

### Recommendation
Compute accrued interest incrementally instead of by differencing two total-debt products: `accrued = borrowed * (new_index - old_index) / RAY`, which keeps the product small since `new_index - old_index` is bounded by one chunk's factor (`≤ ~8×RAY`). Alternatively, widen the debt-value computation through `I256` and clamp, or detect the overflow in `accrue_step` and pin the index at the last representable value rather than panicking, so exits and liquidations remain possible. Add an Echidna/proptest invariant that every verb stays callable for all `(borrowed, index)` in the admitted domain.

### Proof of Concept
1. List an 18-decimal market with a steep curve (e.g. `max_borrow_rate = 1.75×RAY`, `optimal_utilization = 75%`) and high caps; disable or set `max_utilization = RAY`.
2. Whale supplies ~1e9 whole tokens (`supply`); borrower supplies collateral in a second market and borrows ~98% of the book (`borrow`).
3. Advance ledger time. Each `update_indexes` grows `borrow_index` via `update_borrow_index`.
4. At the step where `borrowed * new_borrow_index / RAY > i128::MAX`, `Ray::mul` panics with `MathOverflow` inside `calculate_supplier_rewards` — the borrow index is still far below `MAX_BORROW_INDEX_RAY`.
5. From then on `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `flash_loan`, `claim_revenue`, `recapitalize`, and `update_indexes` all revert at the same point, permanently. The committed test at tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360 is a ready-made PoC.