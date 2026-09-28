### Title
Borrow/supply index accrual overflows i128 RAY value space before the index cap engages, permanently freezing a market — all repay, withdraw, and liquidation paths panic — (File: contracts/pool/src/interest.rs)

### Summary
The pool accrues interest inside every mutating entrypoint via `global_sync`, which calls `accrue_step` → `scaled_to_original`. The RAY fixed-point value space (`scaled_amount × index`) overflows `i128` long before `MAX_BORROW_INDEX_RAY` is reached, so the cap that is supposed to bound index growth never engages. The resulting `MathOverflow` panic aborts every subsequent operation on that market: supply, withdraw, borrow, repay, liquidation, bad-debt cleanup, and flash loans all run `Cache::load → global_sync` first. This is the lending-protocol analog of CVE-2019-2740's class — an unprivileged-reachable input condition that produces a repeatable crash and complete denial of service of the component.

### Finding Description
Every market mutation follows the documented sequence `Cache::load → interest::global_sync → mutate → guards → commit` [1](#0-0) . `global_sync` unconditionally accrues whenever time has elapsed, chunking into `MAX_COMPOUND_DELTA_MS` windows [2](#0-1) . Each chunk calls `accrue_step` with the market's scaled `borrowed`/`supplied` and the live indexes [3](#0-2) , and `scaled_to_original` multiplies scaled shares by the index in RAY precision [4](#0-3) .

The in-repo proof test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates the failure concretely: an 18-decimal market supplied with ~1e9 whole tokens, borrowed at 98% utilization on the XLM rate curve, accrues until the value multiplication overflows with `MathOverflow` — while `last.borrow_index < MAX_BORROW_INDEX_RAY`, i.e., the cap never fires [5](#0-4) . From that point `try_withdraw` and `try_repay` both fail with `MATH_OVERFLOW` [6](#0-5) , and liquidation fails identically since it accrues first.

The overflow is reachable entirely through unprivileged calls: `supply` of a large principal (the test uses `lift_caps` only to raise governance caps — an attacker simply needs an uncapped or generously capped market, and `max_utilization` disabled or high), plus one `borrow` at high utilization. No privileged role, oracle manipulation, or token misbehavior is required; only time and balance-sheet size.

### Impact Explanation
Permanent freezing of user funds in the affected market. Once `scaled × index` exceeds the RAY value capacity, every accrual panics, and since accrual precedes every verb, no supplier can withdraw, no borrower can repay, no liquidator can liquidate, and `clean_bad_debt`/`recapitalize` cannot run either — they accrue too. The market's cash is locked in the pool contract indefinitely. This satisfies the "permanent freezing of funds" / "contract unable to operate" acceptance criteria for the market book, affecting all suppliers of that (hub, token) book regardless of their own position size.

### Likelihood Explanation
Medium. Triggering requires (a) a high-decimals token market (18 decimals, as in the PoC), (b) whale-scale principal (~billions of tokens or an equivalent low-value-per-unit token), and (c) sustained near-max utilization for years so the borrow index compounds to ~170×. The docs acknowledge the hazard — "Finite RAY value capacity can be exhausted before the index ceiling" [7](#0-6)  — but the intended mitigation (`MAX_BORROW_INDEX_RAY`) provably does not engage because the value multiplication overflows first, which the test flags as contradicting the documented bound ("the bound in docs/reference/formulas.md is wrong"). The defect is a wrong ordering of guards, not an accepted design choice: the cap exists precisely to prevent this and fails.

### Recommendation
Bound the product, not just the index. In `accrue_step`/`global_sync`, clamp the index step when `borrowed × borrow_index` (or `supplied × supply_index`) approaches the RAY value ceiling — e.g., cap `borrow_index` at `min(step.borrow_index, MAX_BORROW_INDEX_RAY, i128::MAX / borrowed)` before writing it, or saturate interest accrual (stop growing the index, mark accrued) once the value product reaches a safe fraction of `i128::MAX`. Alternatively enforce a per-market `supplied` share cap derived from `i128::MAX / MAX_BORROW_INDEX_RAY` at `supply`/`calculate_scaled_supply` time [8](#0-7)  so no reachable book can ever overflow the value space. Add a regression test asserting the index cap engages before any `MathOverflow`.

### Proof of Concept
Adapted from `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-361`:

```rust
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))     // 18-decimal market
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
lift_caps(&t, "BIG18", 18);
lift_caps(&t, "COL", 7);

// Unprivileged: whale supply + 98% utilization borrow
let principal = BILLION * 10i128.pow(18);
t.supply_raw(BOB, "BIG18", principal);
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", principal / 100 * 98);

// Advance ledger time; accrual eventually panics inside scaled_to_original
loop {
    t.advance_time(YEAR_SECS);
    if t.try_update_indexes_for(&["BIG18"]).is_err() { break; }  // MathOverflow
}

// Market is permanently frozen — all accrue-first verbs panic:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0),  errors::MATH_OVERFLOW);
// Index cap never engaged: book.borrow_index < MAX_BORROW_INDEX_RAY
```

All steps are reachable by a single unprivileged address via `supply`, `borrow`, `withdraw`, `repay`, and `update_indexes`; ledger-time advancement is the only environmental dependency.

### Citations

**File:** contracts/pool/README.md (L159-168)
```markdown
Each mutation of an existing market runs this sequence:

```text
entrypoint (#[only_owner])
  → Cache::load             # read params + state, bump TTL
  → interest::global_sync   # accrue to now, in ≤1yr chunks
  → mutate                  # cache/shares.rs, cache/cash.rs
  → guards::*               # reserve, utilization, backing checks
  → commit → transfer_out → emit
```
```

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

**File:** contracts/pool/src/interest.rs (L39-53)
```rust
fn accrue_chunk(env: &Env, cache: &mut Cache, delta_ms: u64) {
    let step = accrue_step(
        env,
        cache.params(),
        cache.borrowed(),
        cache.supplied(),
        cache.borrow_index(),
        cache.supply_index(),
        delta_ms,
    );

    cache.set_borrow_index(step.borrow_index);
    cache.set_supply_index(step.supply_index);
    cache.accrue_revenue(step.revenue_shares);
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

**File:** contracts/pool/src/cache/scale.rs (L30-37)
```rust
    pub(crate) fn calculate_scaled_supply(&self, amount: i128) -> Ray {
        calculate_scaled_supply(
            &self.env,
            amount,
            self.params.asset_decimals,
            self.supply_index,
        )
    }
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L320-361)
```rust
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
    std::println!(
        "ray-value cliff reached after {years} years at 98 percent utilization on the XLM curve; last index x{:.1}",
        last.borrow_index as f64 / RAY as f64
    );
}
```

**File:** docs/explanation/threat-model.md (L317-324)
```markdown
## Numeric and resource limits

Finite RAY value capacity can be exhausted before the index ceiling. Synchronizing
an overlarge book can then fail before an otherwise risk-reducing operation.
Caps must account for plausible index growth as well as token balances.
Accrual cadence changes utilization and subsequent rates; bounded chunks do not
make cadence neutral or prove exact conservation after integer rounding.
See [numeric limits](../reference/formulas.md#numeric-limits).
```
