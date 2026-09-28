### Title
Debt-value overflow in accrual permanently freezes a high-decimal market - (File: common/src/rates/simulate.rs)

### Summary
The bug class is a crash on adversarially large/crafted input (CVE-2016-7164: crafted tracker response → segfault). The analog is an untyped `i128` overflow panic inside `accrue_step`, which every pool entrypoint runs first via `global_sync`. Once `borrowed × borrow_index` exceeds `i128::MAX`, the market's `update_indexes`/`supply`/`borrow`/`withdraw`/`repay`/`liquidate`/`clean_bad_debt` all revert permanently, freezing every supplier's and borrower's funds in that market. The borrow-index cap (`MAX_BORROW_INDEX_RAY = 1e36`) never engages because the value multiplication overflows before the index reaches the cap, and `require_cap_within_asset_domain` permits caps large enough to reach the cliff.

### Finding Description
`accrue_step` begins by unscaling the market's scaled debt with a half-up multiply:

- `common/src/rates/simulate.rs:60-61`: `borrowed_original = scaled_to_original(env, borrowed, borrow_index)`.
- `scaled_to_original` is `scaled.mul(env, index)` (`common/src/rates/scaling.rs:14-16`), i.e. `half_up(borrowed × index / RAY)` via `mul_div_half_up` in `common/src/math/fp_core.rs`, which panics with `GenericError::MathOverflow` when the quotient does not fit `i128` (the widened `I256` path still calls `.to_i128().unwrap_or_else(panic)`).
- The mutating path `contracts/pool/src/interest.rs:20-33` (`global_sync` → `accrue_chunk` → `accrue_step`) runs at the top of every pool verb, before any state is committed, so the panic bricks the market — there is no way to skip accrual.
- `update_borrow_index` (`common/src/rates/index.rs:13-19`) caps the *index* at `1e36`, but nothing caps the *scaled debt × index* product; `docs/reference/invariants.md` INV-IDX-01 even acknowledges "Debt-value overflow can still revert accrual before that ceiling is reached."
- `require_cap_within_asset_domain` (`common/src/validation.rs:61-70`) only bounds `cap ≤ i128::MAX / 10^(27-decimals)`. For an 18-decimal asset that bound is ~1.7e29 base units, i.e. a scaled supply/debt of ~1.7e38 RAY — already adjacent to `i128::MAX`. A whale supplying and borrowing near a validated cap on a high-decimal market pushes `borrowed` to where even modest index growth (or none, at the extreme cap) overflows the product.

The in-repo harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`) demonstrates exactly this: a whale supplies `BILLION × 10^18` of an 18-decimal asset and borrows 98% of it; after repeated accrual the next `update_indexes` returns `MATH_OVERFLOW`, and subsequent `withdraw` and `repay` attempts fail with the same error while `borrow_index < MAX_BORROW_INDEX_RAY`.

### Impact Explanation
Permanent freezing of funds and a market unable to operate. Once `borrowed × borrow_index ≥ i128::MAX`, every entrypoint that accrues — `update_indexes`, `withdraw`, `repay`, `borrow`, `supply`, `liquidate`, `clean_bad_debt`, `claim_revenue` — panics in `global_sync` before doing work. Suppliers cannot exit, borrowers cannot repay, liquidators cannot clear the position, and the bad-debt/recapitalize paths are equally blocked. The freeze is unrecoverable because no verb can reduce `borrowed` without first running the accrual that panics.

### Likelihood Explanation
Reachable by a single unprivileged address with sufficient capital, using only `supply`, `borrow`, and time/`update_indexes` (permissionless). Requirements: a market on a high-decimal asset (up to 18 decimals is valid) with governance-set caps at or near the `max_cap_for_decimals` bound, and the ability to hold utilization high so the borrow index compounds. The test shows the cliff is hit well before the index cap on a realistic steep curve segment. Likelihood is gated by whale capital and cap configuration rather than by any missing check — the validation bound itself permits the overflowing state — but it does require a large position and sustained accrual, so Medium-High rather than Critical.

### Recommendation
Saturate the debt/supply value computation in accrual instead of panicking: compute `borrowed_original`/`supplied_original` with a saturating `mul_div_*_saturating` (as `calculate_scaled_cap` already does, `common/src/rates/scaling.rs:26-33`), clamping utilization inputs to `i128::MAX` so accrual and the index cap can still engage. Alternatively, enforce a stricter per-market cap so that `cap_ray × MAX_BORROW_INDEX_RAY / RAY` fits `i128` — i.e. tighten `max_cap_for_decimals` to `i128::MAX / 10^(27-d) / (MAX_BORROW_INDEX_RAY / RAY)` — and add a regression test that accrual at the cap and at the index ceiling never reverts.

### Proof of Concept
Existing test: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`.

```rust
let principal = BILLION * 10i128.pow(18);        // 18-decimal asset
t.supply_raw(BOB, "BIG18", principal);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // 98% utilization
// advance years on the steep curve segment; accrual eventually panics:
//   try_update_indexes_for(&["BIG18"]) -> Error(Contract, MATH_OVERFLOW)
// while book.borrow_index < MAX_BORROW_INDEX_RAY.
// After the cliff:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Mechanism: `borrowed` (scaled, RAY) ≈ `0.98 × principal × 10^9` ≈ `9.8e35`; once `borrow_index ≈ 1.7e2 × RAY`, `borrowed × borrow_index / RAY ≈ 1.7e38 = i128::MAX`, and `scaled_to_original` inside `accrue_step` panics on every subsequent accrual, freezing the market.