### Title
Debt-value `i128` overflow in interest accrual permanently freezes a whale-scale market before the borrow-index cap engages — (`contracts/pool/src/interest.rs` / `common/src/rates/index.rs`)

### Summary
The bug class of CVE-2018-11724 is "attacker-influenced input drives an unchecked arithmetic/memory bound into a crash that takes down the whole system." The Soroban analog lives in the pool's accrual path: `calculate_supplier_rewards` computes `borrowed * new_borrow_index` in `i128` (widened to `I256` only for the product, but the *result* must still fit `i128`). When `borrowed` shares times the index exceeds `i128::MAX` — which happens at a lower index than `MAX_BORROW_INDEX_RAY` for a sufficiently large market — `Ray::mul` → `mul_div_half_up` → `I256::to_i128()` returns `None` and the contract panics with `GenericError::MathOverflow`. Every pool mutation accrues first, so the entire market freezes permanently.

### Finding Description
`common/src/rates/index.rs::calculate_supplier_rewards` (lines 80–83) computes:

```rust
let old_total_debt = borrowed.mul(env, old_borrow_index);
let new_total_debt = borrowed.mul(env, new_borrow_index);
```

`Ray::mul` calls `fp_core::mul_div_half_up`, which falls back to `I256` for the intermediate product but converts the quotient back with `.to_i128()` — returning `None` once the result exceeds `i128::MAX`, which `mul_div_half_up` turns into a panic (`common/src/math/fp_core.rs:116-143`). The same `borrowed * index` valuation happens in `scaled_to_original` during utilization recomputation inside chunked accrual.

The borrow index is capped at `MAX_BORROW_INDEX_RAY` in `update_borrow_index` (`common/src/rates/index.rs:13-19`), but the value ceiling `borrowed * index <= i128::MAX` binds *first* whenever `borrowed` (RAY-scaled shares) is large: the index cap is `10^36` while `i128::MAX / borrowed` can be far below it. The repository's own test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-362`) proves this: after the panic, `last.borrow_index < MAX_BORROW_INDEX_RAY`, and both `try_withdraw_raw` and `try_repay` revert with `MATH_OVERFLOW` because every verb accrues first.

An unprivileged attacker reaches this through the normal entrypoints: `controller.supply` a whale-scale position in a high-decimals market (caps can be lifted only by governance, but on an uncapped/high-cap market — e.g. XLM-like main token — the attacker supplies the full cap), then `controller.borrow` at maximum utilization. From that point the freeze requires no further attacker action: anyone's call to `update_indexes`, `supply`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, or `claim_revenue` panics once `borrowed * borrow_index` crosses `i128::MAX`, before the index ever reaches its cap. Crucially, even honest `repay`/`liquidate` calls that would shrink the debt are blocked, since accrual precedes the mutation.

### Impact Explanation
Permanent freezing of all funds in the affected market — suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and revenue cannot be claimed. Because debt cannot be reduced once the panic threshold is crossed, the market is unrecoverable and the bad debt cannot even be cleaned. This maps to the accepted impact "permanent freezing of funds."

### Likelihood Explanation
Likelihood is low in capital terms: the attacker must supply on the order of billions of whole tokens at high utilization, and the index must compound past `i128::MAX / borrowed` (the test shows the cliff within ~tens of years at 98% utilization on a steep curve, faster at steeper rates). No privileged access, timing, or oracle manipulation is needed — only capital and patience — and there is no in-protocol mitigation: the index cap exists but is unreachable before the value ceiling. Severity: Medium (real permanent-freeze impact, but requires whale-scale capital and long accrual, and the cliff is already exercised by the protocol's own test suite).

### Recommendation
Bound the debt valuation below the index cap: enforce `borrowed * borrow_index <= i128::MAX` as an explicit invariant — e.g. cap `total_debt` shares at market creation/`update_indexes` relative to the current index (`max_scaled_debt = i128::MAX / borrow_index`), or process accrual in a saturating/decomposed form (split `borrowed` into chunks and sum `checked` partial debts). Alternatively, make `repay`/`liquidate`/`clean_bad_debt` accrue against a clamped index so debt-reducing verbs remain callable after the ceiling is reached, leaving only index growth frozen instead of the whole market.

### Proof of Concept
The repo already contains an executable PoC: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-362`. It:

1. Supplies `10^9 * 10^18` units of an 18-decimal asset and `3e16` units of collateral.
2. Borrows 98% of supplied via `borrow_raw` (unprivileged `controller.borrow` path).
3. Advances time in 1-year chunks calling `update_indexes` until it reverts with `MATH_OVERFLOW`, asserting `borrow_index < MAX_BORROW_INDEX_RAY` (cap never engaged).
4. Asserts `withdraw` and `repay` both revert with `MATH_OVERFLOW` — market permanently frozen.

An attacker reproduces this on-chain with only `controller.supply`, `controller.borrow`, and the passage of ledger time; no privileged role is involved at any step.