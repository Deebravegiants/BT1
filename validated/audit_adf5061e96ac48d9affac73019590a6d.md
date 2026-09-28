### Title
Accrual `MathOverflow` panic permanently freezes a saturated market — withdraw, repay, and liquidation all revert — ([File: contracts/pool/src/cache/scale.rs](contracts/pool/src/cache/scale.rs))

### Summary
The analog of CVE-2017-2893's "crafted input → unhandled fault → service halt" maps onto XOXNO Lending's accrual path: when a market's `borrow_index` grows past the point where `scaled * index` still fits in `i128`, `scaled_to_original` (via `common::rates`) panics with `GenericError::MathOverflow`. Because every pool verb accrues first, the panic bricks the entire market: `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `flash_loan`, and `update_indexes` all revert identically for every caller, permanently freezing all supplied funds in that market.

### Finding Description
Interest accrual multiplies scaled share amounts by the live RAY index. `Cache::unscale_borrow`, `unscale_supply`, and `scaled_to_original` (`contracts/pool/src/cache/scale.rs:23`, `scale.rs:50-87`) delegate to `common::rates` helpers that compute `scaled.mul(index)` in `i128`. The comment in `certora/common/spec/rates_rules.rs:316-320` confirms `update_supply_index` computes `supplied.mul(old_index)` which "panics with `MathOverflow` once `supplied * old_index / RAY` leaves `i128`."

The index cap (`MAX_BORROW_INDEX_RAY` / `MAX_SUPPLY_INDEX_RAY`) was intended to bound this, but the harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`) demonstrates the value-overflow cliff is reached *before* the index cap engages: the last recorded `borrow_index` is still below the cap when the panic occurs, and the test explicitly asserts `t.try_withdraw_raw(BOB, "BIG18", 1)` and `t.try_repay(...)` both revert with `MATH_OVERFLOW` — "the market is frozen: no repay, no withdraw, no liquidation."

The trigger is fully unprivileged: an attacker (or honest whale) supplies a very large principal on a high-decimals market and borrows near 98% utilization; sustained accrual (millisecond-chunked, so it compounds continuously) drives `borrowed * borrow_index` past `i128::MAX`. No privileged call is required.

### Impact Explanation
Permanent freezing of funds and a contract unable to operate for that market. Once the overflow corner is reached there is no recovery path: `clean_bad_debt` and `recapitalize` also accrue first, and the index cap cannot retroactively engage because accrual itself is what panics. All supplier principal and borrower collateral routed through that market's book is bricked, and liquidators cannot rescue bad debt — so it also propagates to protocol insolvency if the market carries undercollateralized positions.

### Likelihood Explanation
Medium-low. The trigger requires (a) a market whose configured supply cap and decimals admit a very large `supplied * index` product (the test needed ~`10^36`-scale principal on an 18-decimal asset with caps lifted), and (b) enough accrual time at steep utilization to push the index up ~170× (years at the XLM curve's steep segment in the test). Real-world caps may bound this below the cliff for 7-decimal stablecoin markets, but caps are governance configuration — nothing in the contract enforces that `cap * max_index` stays within `i128`, so any high-decimals listing or lifted-cap market is exposed, and once crossed the state is irreversible.

### Recommendation
- In `common::rates::update_borrow_index`/`update_supply_index`, clamp the index to `MAX_BORROW_INDEX_RAY`/`MAX_SUPPLY_INDEX_RAY` **before** the `scaled * index` unscale, or perform accrual unscaling through the `I256`-widened path (`common/src/math/fp_core.rs:14-21`) and saturate the result rather than panicking.
- Enforce at listing/config time that `max_cap_for_decimals(decimals) * MAX_INDEX` cannot overflow `i128`, so caps provably stay under the cliff.
- Optionally make `withdraw`/`repay` full-close paths skip accrual when the computed delta would overflow, preserving an escape hatch.

### Proof of Concept
Covered by the existing harness test `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-361`: supply `BILLION * 10^18` of an 18-decimal asset, borrow ~98%, advance ledger time repeatedly until `try_update_indexes` fails with `MATH_OVERFLOW`; thereafter `try_withdraw_raw` and `try_repay` both fail with `MATH_OVERFLOW`, and `borrow_index < MAX_BORROW_INDEX_RAY` proves the cap never engaged.

Uncertainty note: I could not fully verify whether production `supply`/`borrow` entrypoints enforce a cap check that provably keeps `supplied * index` inside `i128` for all listed markets; the finding assumes caps can be configured high enough, which the test's `lift_caps` path demonstrates is not an invariant enforced by the contracts themselves.