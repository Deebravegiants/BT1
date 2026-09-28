### Title
Permanent market freeze via debt-value overflow in interest accrual — (File: contracts/pool/src/interest.rs)

### Summary
The CVE class is a crash triggered by a crafted input reaching an unchecked arithmetic path. The analog in XOXNO Lending: `interest::global_sync` runs unconditionally at the head of every pool verb, and once a market's accrued debt value no longer fits `i128`, the checked arithmetic in `accrue_step`/`scaled_to_original` panics with `MathOverflow` on every subsequent call — `update_indexes`, `repay`, `withdraw`, `borrow`, `seize_positions`, `recapitalize`, and liquidation all included. The `MAX_BORROW_INDEX_RAY` index cap is never reached because the value multiplication overflows first, so the freeze is permanent and no recovery path exists inside the market.

### Finding Description
Every pool entrypoint calls `Cache::load` then `interest::global_sync`, which chunks elapsed time and calls `accrue_chunk` → `accrue_step` for each window [1](#0-0) . Inside accrual and utilization computation, scaled shares are converted to value via `scaled_to_original`, which multiplies shares by the index as RAY fixed-point [2](#0-1) . When `borrowed_shares * borrow_index` exceeds `i128` (~1.7e38, while scaled debt is denominated in 27-decimal RAY space), the checked multiply panics. The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates this concretely: a ~1e30-unit market at 98% utilization on the XLM curve overflows inside `scaled_to_original` before the index cap `MAX_BORROW_INDEX_RAY` engages, and afterwards `try_withdraw_raw` and `try_repay` both revert with `MathOverflow` — the market is permanently frozen [3](#0-2) . The documented invariant `INV-IDX-01` concedes the cap does not bound representable values: "Debt-value overflow can still revert accrual before that ceiling is reached" [4](#0-3) .

Reachability by an unprivileged address: a whale supplies a very large amount of an 18-decimal asset (caps and the max-utilization gate bound, but do not prevent, large positions), an account borrows near the utilization ceiling, and anyone — including the attacker or any third party — calls the permissionless `update_indexes` / any verb after sufficient accrual time to push the debt value past the RAY ceiling. No governance action is required; the only prerequisites are scale and time.

### Impact Explanation
Permanent freezing of funds: once the panic threshold is crossed, no supplier can withdraw, no borrower can repay, no liquidator can seize, and governance cannot `recapitalize` or `clean_bad_debt` — every path accrues first and hits the same panic. All underlying tokens in that market are irrecoverable, an accepted "theft/permanent freezing of funds" impact class. The freeze is irreversible short of an upgrade because `last_timestamp` can never advance past a failing accrual.

### Likelihood Explanation
Low-to-moderate. It requires a whale-scale position (≈10³⁰ raw units of a high-decimal asset), sustained ~98% utilization, and roughly a decade of accrual on a steep rate curve before the cliff — the test bounds it under 40 years. Supply caps and the max-utilization gate (which blocks new borrows but not accrual) slow but do not eliminate the setup, and `update_indexes` is callable by anyone to advance accrual. Severity is Medium: real but demanding attacker cost and long horizon.

### Recommendation
Enforce the invariant the index cap was intended to provide: in `accrue_chunk` (or inside `accrue_step`), clamp the effective accrual so `borrowed * borrow_index` stays representable — e.g., derive a per-market `max_borrow_index = i128::MAX / borrowed_shares` floor and cap `step.borrow_index` at it, mirroring how `MAX_BORROW_INDEX_RAY` already caps the index itself. Alternatively, bound market supply/borrow caps and `asset_decimals` at listing so `shares × MAX_BORROW_INDEX_RAY` cannot overflow `i128` for any permitted market configuration, and add a harness test asserting the cap engages before `scaled_to_original` overflows.

### Proof of Concept
See `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-360`, which already exercises the path: supply `BILLION * 10^18` of an 18-decimal asset, borrow 98%, advance `YEAR_SECS` in a loop calling `update_indexes`; within 40 iterations `try_update_indexes_for` fails with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, and subsequent `try_withdraw_raw` and `try_repay` panic identically — suppliers' principal is locked forever [5](#0-4) .

### Citations

**File:** contracts/pool/src/interest.rs (L20-33)
```rust
pub(crate) fn global_sync(env: &Env, cache: &mut Cache) {
    if !cache.needs_accrual() {
        return;
    }

    let mut remaining = cache.elapsed_ms();
    while let Some(nonzero) = NonZeroU64::new(remaining) {
        let chunk = nonzero.get().min(MAX_COMPOUND_DELTA_MS);
        accrue_chunk(env, cache, chunk);
        remaining = remaining.saturating_sub(chunk);
    }

    cache.mark_accrued();
}
```

**File:** contracts/pool/src/cache/scale.rs (L19-27)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
    }
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-356)
```rust
/// `i128::MAX`, 170 times that. At the XLM curve's steep segment the index
/// grows past 170x in a few years, and the next accrual panics inside
/// `scaled_to_original`. Every verb accrues first, so the market freezes:
/// no repay, no withdraw, no liquidation. The index cap never engages.
#[test]
fn a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap() {
    let mut t = LendingTest::new()
        .with_market(big("BIG18", 18, xlm_curve()))
        .with_market(col())
        .with_max_utilization_disabled_all_markets()
        .build();
    lift_caps(&t, "BIG18", 18);
    lift_caps(&t, "COL", 7);
    let principal = BILLION * 10i128.pow(18);
    t.supply_raw(BOB, "BIG18", principal);
    let debt = principal / 100 * 98;
    t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
    t.borrow_raw(ALICE, "BIG18", debt);

    let mut years = 0u32;
    let failure = loop {
        years += 1;
        assert!(
            years <= 40,
            "no cliff within 40 years; the bound in docs/reference/formulas.md is wrong"
        );
        t.advance_time(YEAR_SECS);
        if let Err(e) = t.try_update_indexes_for(&["BIG18"]) {
            break e;
        }
    };
    let failed: Result<(), soroban_sdk::Error> = Err(failure);
    assert_contract_error(failed, errors::MATH_OVERFLOW);
    let last = book(&t, "BIG18");
    assert!(
        last.borrow_index < MAX_BORROW_INDEX_RAY,
        "the index cap did not engage before the value overflow"
    );
    // The market is frozen: exits and repayments accrue first and hit the same panic.
    assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
    assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

**File:** docs/reference/invariants.md (L229-236)
```markdown
### INV-IDX-01 — Borrow index is monotone and bounded

Both indexes start at one RAY. Successful accrual with validated rate parameters
cannot lower the borrow index and caps it at the protocol constant 10^36 raw
RAY. At the ceiling, further accrual produces no borrower interest.

Debt-value overflow can still revert accrual before that ceiling is reached.
Bounded indexes do not guarantee representable position or market values.
```
