### Title
Whale-scale supply plus near-full borrow drives the market's RAY-domain debt value past `i128`, permanently bricking every entrypoint via an accrual-time overflow panic - (File: common/src/rates/scaling.rs)

### Summary
Analog of CVE-2020-18976 (crafted input reaching an unchecked arithmetic path that crashes the process): in XOXNO Lending the reachable crash is the fixed-point value overflow inside interest accrual. Every state-changing pool verb runs `global_sync` first, so once a market's accrued debt value exceeds the RAY/`i128` domain, `scaled_to_original` / `mul_div` panics with `MathOverflow` on *every* subsequent call — supply, borrow, withdraw, repay, liquidate, `update_indexes`, `clean_bad_debt` — permanently. An unprivileged attacker can steer a market toward this cliff by supplying near the per-decimals domain cap and borrowing to sustained high utilization.

### Finding Description
The pool accrues interest through `global_sync`/`accrue_chunk` in `contracts/pool/src/interest.rs:20-53`, which calls `accrue_step` and must unscale `cache.borrowed()`/`cache.supplied()` by the indexes. Unscaling goes through `scaled_to_original` (`common/src/rates/scaling.rs:14-16`) → `Ray::mul` → `fp_core::mul_div_half_up`, which panics with `GenericError::MathOverflow` when `scaled * index` no longer fits `i128` (`common/src/math/fp_core.rs:108-118`).

The borrow index is capped at `10^36` (`MAX_BORROW_INDEX_RAY`), but that cap does not bound the *value* domain: with a large enough scaled supply (up to `max_cap_for_decimals(d)` ≈ 170 billion whole tokens for 18 decimals), `scaled × index` overflows `i128` well before the index ceiling engages. The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates exactly this: after sufficient accrual time `try_update_indexes_for`, `try_withdraw_raw`, and `try_repay` all fail with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-360`). `docs/reference/formulas.md:434-437` acknowledges the gap: "Value overflow can occur before the index ceiling and block repayment/withdrawal because those operations accrue first." Because `global_sync` runs at the top of every mutation (`contracts/pool/README.md:159-168`), the panic is unconditional — there is no path that skips accrual, and no `clean_bad_debt`/`recapitalize` escape, since those accrue first too.

### Impact Explanation
Permanent freezing of funds: once the market crosses the overflow point, no supplier can withdraw, no borrower can repay, no liquidator can liquidate, and bad-debt cleanup cannot run. All user deposits and outstanding debt in that market are frozen forever; the panic reverts atomically, so even partial exits are impossible. This matches the "permanent freezing of funds" impact class.

### Likelihood Explanation
The precondition is a single unprivileged address (or a few) executing `supply` of up to ~170×10⁹ whole tokens of a high-decimals asset (which requires real capital but is within the admitted cap domain — `lift_caps`/governance caps up to `max_cap_for_decimals`) plus `borrow` to ~98% utilization on a steep rate curve. After that, only the passage of time is needed; no further attacker action, oracle manipulation, or privileged call is required. Any user can also grief an existing large market this way once organic growth approaches the domain. The cost is large but the attack requires no privilege and the freeze is irreversible, consistent with Medium severity like the source CVE.

### Recommendation
Bound the *value* domain, not just the index: in `accrue_step`/`global_sync`, cap or clamp accrued totals so `borrowed_scaled × borrow_index` and `supplied_scaled × supply_index` stay within `i128` (e.g., stop accruing when the unscaled value approaches `i128::MAX`, analogous to the existing `MAX_BORROW_INDEX_RAY` index ceiling), and/or enforce tighter admission caps in `require_cap_within_asset_domain` (`common/src/validation.rs`) so `max_cap × MAX_INDEX` cannot overflow the RAY value domain. At minimum, give `clean_bad_debt`/write-down paths an accrual-free recovery route so a frozen market can be unwound.

### Proof of Concept
```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321
let principal = BILLION * 10i128.pow(18);          // ~1e27 units of an 18-dec asset
t.supply_raw(BOB, "BIG18", principal);             // unprivileged supply at domain cap
let debt = principal / 100 * 98;                   // ~98% utilization
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);                // unprivileged borrow

// advance ledger time; each year accrues via global_sync → accrue_step
loop {
    t.advance_time(YEAR_SECS);
    if t.try_update_indexes_for(&["BIG18"]).is_err() { break; }  // panics MathOverflow
}
// market is now permanently frozen: accrual precedes every verb
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
// borrow_index never reached MAX_BORROW_INDEX_RAY — the index cap cannot save it
```

Relevant code: `global_sync`/`accrue_chunk` at `contracts/pool/src/interest.rs:20-53`, `scaled_to_original` at `common/src/rates/scaling.rs:14-16`, panicking `mul_div_half_up` at `common/src/math/fp_core.rs:108-118`, and the demonstrating test at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-360`.

Caveat: the value-domain limit is documented in `docs/reference/formulas.md:421-437`, which a reviewer could read as a "documented ADR choice." It is included here because the docs describe an *arithmetic limit* (no enforcement, no recovery path, permanent freeze) rather than an accepted design decision, and because an unprivileged address can push a real market across it.