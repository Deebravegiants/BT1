### Title
Accrual math-overflow permanently freezes a saturated market, trapping all supplier and borrower funds - (File: contracts/pool/src/interest.rs)

### Summary
The hapi advisory is a denial-of-service class: a request handler throws on adversarial input and kills the service. The analog in XOXNO Lending is worse than a per-request throw: `global_sync` accrual runs before every pool mutation, and when `borrowed * borrow_index` overflows `i128` inside `scaled_to_original`/`accrue_step`, the accrual panics with `MathOverflow`. Because the panic happens before any mutation, every verb on that market — `withdraw`, `repay`, `borrow`, `liquidate`, `flash_loan` — reverts identically and forever, permanently freezing all supplier funds.

### Finding Description
Every market mutation in the pool runs `Cache::load` → `interest::global_sync` before touching state, and `global_sync` loops `accrue_chunk` over the elapsed interval [1](#0-0) . Each chunk recomputes debt value via scaled-to-original conversion; when the borrow index has grown enough that `borrowed * borrow_index / RAY` exceeds `i128`, the fixed-point helpers panic with `GenericError::MathOverflow` [2](#0-1) . The `MAX_BORROW_INDEX_RAY` cap does not protect this path — the value product overflows before the index reaches its cap on a large book at high utilization, so the cap never engages [3](#0-2) .

The harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` demonstrates the end state: after enough years at ~98% utilization on a steep rate curve, `update_indexes` reverts with `MATH_OVERFLOW`, and subsequently `withdraw` and `repay` fail with the same error — the market is bricked with no recovery path, since even bad-debt cleanup and liquidation accrue first [4](#0-3) .

### Impact Explanation
Permanent freezing of funds. Once the index/debt product crosses the `i128` boundary mid-accrual, no entrypoint on that market can execute: suppliers cannot withdraw, borrowers cannot repay (including willing repayers trying to fix it), liquidators cannot liquidate, and `clean_bad_debt`/`recapitalize` hit the same pre-mutation accrual panic. All cash held by the physical pool for that `(hub, asset)` book is stranded. Because hub/spoke books share one physical token balance, the frozen market's cash is unrecoverable by any in-scope unprivileged or privileged flow.

### Likelihood Explanation
An unprivileged attacker supplies a very large amount and borrows near `max_utilization`, then simply waits — no further action is needed. Permissionless `update_indexes` lets anyone advance accrual, but time alone does it. Requirements: a market whose `supply_cap`/`borrow_cap` admit a book large enough that `debt * index` can exceed `i128::MAX` (caps are validated only against the asset→ray domain, not the value product), a steep `InterestRateModel` so utilization drives `max_borrow_rate`, and sustained high utilization so the index compounds toward the cliff. The in-repo test reaches the cliff on an 18-decimal billion-scale market at 98% utilization; nothing a borrower or supplier can do afterward un-bricks it. Cost is capital lockup for the attacker's own supply, which is itself frozen — so this is a griefing/DoS-by-accumulation rather than profit-motivated, matching the advisory's DoS class. Severity: Medium (severe impact, requires large book plus prolonged high utilization and a governance-set cap/curve that permits it).

### Recommendation
Bound accrual inputs before the multiplication rather than letting `scaled_to_original` panic: clamp the computed debt value to `i128::MAX` (or saturate the borrow index at the largest value keeping `borrowed * index / RAY` representable, below `MAX_BORROW_INDEX_RAY`), so accrual completes and exits stay open. Alternatively, validate at `create_market`/`update_params` that `supply_cap` scaled-to-value at `MAX_BORROW_INDEX_RAY` stays within `i128`, and let `repay`/`clean_bad_debt` skip or tolerate the accrual panic so debt can be burned down to a representable level.

### Proof of Concept
The scenario is exercised by the existing harness test: deploy markets `BIG18` (18 decimals, XLM-style steep curve) and `COL` with caps lifted, supply `principal = 1e9 * 10^18` BIG18 from BOB, borrow 98% of it from ALICE, then advance ledger time year-by-year calling `update_indexes`. Accrual eventually panics with `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`, and afterward `withdraw` and `repay` both revert with `MathOverflow` — permanent freeze [5](#0-4) .

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

**File:** common/src/math/fp.rs (L13-16)
```rust
fn checked_add_raw(env: &Env, a: i128, b: i128) -> i128 {
    a.checked_add(b)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

**File:** common/src/rates/index.rs (L13-19)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
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
