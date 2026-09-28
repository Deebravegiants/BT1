### Title
i128 overflow in accrual's `scaled_to_original` permanently freezes a large high-utilization market before the borrow-index cap can engage - (common/src/rates/simulate.rs)

### Summary
The pool's interest-accrual step unscales `borrowed` and `supplied` shares to original RAY value via `scaled_to_original` (`Ray::mul`, which panics on `i128` overflow) *before* clamping the borrow index at `MAX_BORROW_INDEX_RAY` (`1e36`). For a sufficiently large market, `scaled × index` overflows `i128` while `borrow_index` is still far below the cap, so `accrue_step` panics with `GenericError::MathOverflow`. Since `interest::global_sync` runs at the head of every pool mutation (`Cache::load` → accrue → mutate), every user-reachable verb on that market — supply, withdraw, repay, liquidate, seize, recapitalize — reverts forever. The index cap that was designed to stop growth at `1e36` never engages, because the overflow happens in the unscale used to compute utilization, not in `update_borrow_index`.

### Finding Description
- `common/src/rates/simulate.rs:60-62`: `accrue_step` calls `scaled_to_original(env, borrowed, borrow_index)` and `scaled_to_original(env, supplied, supply_index)` unconditionally at the top of each chunk.
- `common/src/rates/scaling.rs:14-16`: `scaled_to_original` is `scaled.mul(env, index)`; `Ray::mul` panics (`GenericError::MathOverflow`) when `scaled * index / RAY` exceeds `i128::MAX`. In RAY terms, the product overflows when `scaled × index ≳ i128::MAX` — i.e. `scaled ≳ 1.7e11` RAY-valued units at `index = RAY`, and proportionally less as the index grows.
- `common/src/rates/index.rs:13-19`: `update_borrow_index` clamps the *index* at `MAX_BORROW_INDEX_RAY = 1e36` (≈1e9×), but the overflow bound on `scaled` shrinks as `1/index`, so with `scaled ~ 1e12` (e.g., ~10¹¹ whole tokens — a whale-sized 18-decimal market that lifted spoke caps can hold, as the harness test constructs), the unscale overflows when the index is only ~170×, roughly 8 orders of magnitude below the cap.
- `contracts/pool/src/interest.rs:20-33`: `global_sync` runs `accrue_chunk` in ≤1-year chunks; a single panicking `accrue_step` aborts the whole transaction, so the panic is permanent — there is no path that skips accrual on a market that needs it.

The repository's own harness test pins this exact failure: `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361`) supplies `10⁹ × 10¹⁸` units of an 18-decimal asset, borrows 98% of it, advances years, and observes `MathOverflow` from `update_indexes`, after which `withdraw` and `repay` also revert with `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`.

### Impact Explanation
Permanent freezing of funds and a contract unable to operate. Once the market's `scaled × index` crosses `i128::MAX`:
- Suppliers cannot withdraw any amount (`withdraw` accrues first and panics).
- Borrowers cannot repay, so their collateral in other markets is permanently locked — and can never be released even by liquidation.
- Liquidators cannot liquidate; bad debt cannot be cleaned or socialized; `recapitalize` (which also accrues) cannot rescue the market.
- All cash held by that market in the physical pool is stranded.

Only time passage is needed after the attacker/user establishes the position — no privileged action required.

### Likelihood Explanation
Reachable by an unprivileged address, but demanding: it requires a market large enough that `scaled_debt × borrow_index` exceeds `1.7e38` RAY², which means whale-scale positions (on the order of `i128::MAX / (index × RAY)` whole tokens) sustained at high utilization for years, with spoke caps lifted by governance. Spoke supply/borrow caps and `require_cap_within_asset_domain` are the intended mitigations, but they are per-market config values that governance can set arbitrarily high, and nothing in the listing validation bounds `cap × MAX_BORROW_INDEX_RAY` against the `i128` domain. This is a Medium-severity reachable-assertion class bug, matching the CVE's "crafted input → assertion → DoS" shape: here the "crafted input" is ordinary large supply/borrow plus elapsed time, and the assertion is the `i128` overflow panic inside shared accrual math.

### Recommendation
Make accrual saturate instead of panicking on the value product:
- In `accrue_step`, compute `borrowed_original`/`supplied_original` with a saturating multiply (e.g., `mul_div_floor_saturating` or `mul_div_ceil_saturating` in `fp_core`) so utilization saturates at ≥ 100% and `update_borrow_index` can pin the index at `MAX_BORROW_INDEX_RAY` cleanly.
- Ensure `update_supply_index`'s `total_supplied_value` (`supplied.mul(old_index)`) and `supply_index_reward_shortfall` use the same saturating/tolerant path, since they multiply the same oversized operands.
- Alternatively, bound state at entry: validate in `supply`/`borrow` that `scaled × MAX_BORROW_INDEX_RAY` and `scaled × MAX_SUPPLY_INDEX_RAY` fit `i128`, so no position can ever carry the market into the overflow region.

### Proof of Concept
The in-repo test demonstrates it end-to-end (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`):

```rust
let principal = BILLION * 10i128.pow(18);        // 1e27 units, 18-dec asset
t.supply_raw(BOB, "BIG18", principal);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98); // 98% utilization
// advance years; each accrual grows borrow_index past ~170x
// → update_indexes panics with MathOverflow inside scaled_to_original,
//   while borrow_index is still < MAX_BORROW_INDEX_RAY.
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Unprivileged entrypoint path: `supply` + `borrow` (controller, with `require_auth` on the caller's own funds) create the oversized scaled balances; thereafter any caller's `update_indexes(market)`, or any `withdraw`/`repay`/`liquidate` touching the market, hits `Cache::load` → `global_sync` → `accrue_chunk` → `accrue_step` → `scaled_to_original` → `MathOverflow`, permanently.