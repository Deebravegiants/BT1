### Title
Permanent market freeze: `borrowed * borrow_index` overflows `i128` in accrual before the index cap engages, bricking all pool operations — (File: common/src/rates/index.rs)

### Summary

Analogous to the `TensorByteSize` `CHECK`-failure class — attacker-reachable state that makes a bounded arithmetic precondition fail and aborts every subsequent call — XOXNO Lending's accrual path computes `borrowed (scaled, RAY) * borrow_index (RAY)` in `i128` fixed point. When a market's scaled debt is large enough that the *debt value* exceeds `i128::MAX` before `borrow_index` reaches its `MAX_BORROW_INDEX_RAY` (10³⁶) cap, `Ray::mul` panics with `GenericError::MathOverflow` inside `accrue_step`/`global_sync`. Since every pool mutation accrues first (`Cache::load` → `interest::global_sync`), the market is permanently frozen: no repay, no withdraw, no liquidation, no `update_indexes`. The codebase's own test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` proves the freeze and demonstrates `try_withdraw_raw` and `try_repay` both reverting.

### Finding Description

`accrue_step` in `common/src/rates/simulate.rs` computes valuations of the full scaled debt every compounding step:

```text
borrowed_original = scaled_to_original(borrowed, borrow_index)   // simulate.rs:60
new_borrow_index  = update_borrow_index(borrow_index, factor)    // simulate.rs:66
calculate_supplier_rewards: borrowed.mul(new_borrow_index)       // index.rs:80-81
```

`scaled_to_original` (`common/src/rates/scaling.rs:14-16`) is `scaled.mul(env, index)`, i.e. `x * y / RAY` via `mul_div_half_up` (`common/src/math/fp_core.rs:108-118`). The I256 fallback only saves the intermediate product; the *result* must still fit `i128`, otherwise it panics with `MathOverflow`. So accrual aborts as soon as

```text
borrowed_scaled_raw * borrow_index_raw / RAY > i128::MAX  (~1.7e38)
```

`update_borrow_index` (`common/src/rates/index.rs:13-19`) caps the index at `MAX_BORROW_INDEX_RAY` *after* multiplying — but the debt-value overflow happens at index values far below the cap when `borrowed_scaled` is large, so the cap never saves the market. The same panic occurs in `update_supply_index` (`index.rs:34`), `supply_index_reward_shortfall` (`index.rs:60-63`), and `apply_bad_debt_to_supply_index` (`contracts/pool/src/interest.rs:74`) since all multiply `supplied * index` or `borrowed * index` in `i128`.

Every pool entrypoint runs `interest::global_sync` (`contracts/pool/src/interest.rs:20-33`) before mutating — confirmed by the pool README flow `Cache::load → interest::global_sync → mutate → guards` — so once the product overflows, **every** subsequent call to that market reverts, including `clean_bad_debt`, `recapitalize`, and liquidations routed through the controller.

### Impact Explanation

Permanent freezing of funds and protocol insolvency:

- All suppliers' deposits in the affected market are permanently locked — `withdraw` reverts in accrual before any burn.
- Borrowers cannot repay; liquidators cannot liquidate underwater positions; the position-NFT-backed collateral is stranded.
- The freeze is irreversible: `borrow_index` is monotone non-decreasing and `borrowed` cannot be reduced (repay itself accrues first), so the overflowing product can never come back into range. No admin function bypasses `global_sync` for an existing market.
- Indirect contagion: controller risk views that call `cached_market_index`/`simulate_update_indexes` for the frozen market also revert, degrading evaluation of any account holding that hub asset.

### Likelihood Explanation

Reachable by a single unprivileged address through `supply` + `borrow` (or just by waiting on an existing large, high-utilization market), but with meaningful prerequisites, which caps severity at Medium:

- Requires a market whose *scaled* debt is huge — the repo's own proof uses ~10⁹ whole tokens of an 18-decimal asset (scaled raw ≈ 10³⁶). Feasible only for high-supply assets (meme tokens) or markets with lifted caps (`lift_caps` / `with_max_utilization_disabled_all_markets` in the test reflect cap-free or very high-cap configurations).
- Requires sustained high utilization at a steep curve segment so the index grows ~170×; the test reaches the cliff within a bounded number of years of ledger time. An attacker cannot force it instantly, but nothing prevents it: utilization near the kink at `MAX_BORROW_RATE_RAY` (2 RAY annual) grows the index up to e² per one-year chunk (`MAX_COMPOUND_DELTA_MS`).
- No privileged action, parameter change, or oracle manipulation is needed — ordinary `supply`/`borrow` calls plus elapsed ledger time suffice. `docs/reference/invariants.md` (INV-IDX-01) acknowledges "debt-value overflow can still revert accrual before that ceiling," and the test comment notes the documented bound "is wrong," indicating a defect rather than an accepted design choice.

### Recommendation

- In `accrue_step`, compute the debt-value delta via a saturating/widened path: keep `old_total_debt`/`new_total_debt` as `I256` (or saturate at `i128::MAX`) and only narrow after the subtraction, so interest up to the index cap stays representable.
- Alternatively, cap `borrowed` growth or clamp `update_borrow_index`'s *effective* index to `min(index, i128::MAX * RAY / borrowed_scaled)` — i.e. enforce a **debt-value ceiling** alongside the index ceiling, so accrual saturates (stops charging interest) instead of panicking.
- Ensure at least one escape path (`repay`/`liquidate`/`clean_bad_debt`) can operate with accrual skipped or saturated, so frozen markets remain unwindable.
- Add a supply/borrow cap check that bounds `scaled * MAX_BORROW_INDEX_RAY / RAY ≤ i128::MAX` at listing or cap-update time (`require_cap_within_asset_domain`-style validation in `common/src/validation.rs`).

### Proof of Concept

The scenario is already encoded in `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs::a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`:

```rust
let principal = BILLION * 10i128.pow(18);          // ~1e9 whole tokens, 18 dp
t.supply_raw(BOB, "BIG18", principal);
let debt = principal / 100 * 98;                   // 98% utilization
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);

// advance ledger time in 1-year steps at the steep curve segment
loop {
    t.advance_time(YEAR_SECS);
    if t.try_update_indexes_for(&["BIG18"]).is_err() { break; }
}
// → Error(Contract, MathOverflow): index ~170x, below MAX_BORROW_INDEX_RAY
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

Manual trace: with `borrowed_scaled ≈ 9.8e26 * RAY`-scale raw and `borrow_index` grown past ~170 RAY, `borrowed.mul(new_borrow_index)` in `calculate_supplier_rewards` (`index.rs:81`) produces `> i128::MAX`, the `I256::to_i128()` conversion returns `None`, and `mul_div_half_up` panics `MathOverflow`. Because `borrow_index` is monotone and `borrowed` cannot be burned without a successful accrual, the condition is permanent.