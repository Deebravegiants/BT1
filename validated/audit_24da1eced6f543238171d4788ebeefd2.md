### Title
Permanent market freeze: `accrue_step` computes unscaled debt before the borrow-index cap can engage, overflowing `i128` and bricking every verb on a whale market - ([File: common/src/rates/simulate.rs])

### Summary
`update_borrow_index` is designed to cap the borrow index at `MAX_BORROW_INDEX_RAY` so that growth is bounded. However, each accrual chunk first calls `scaled_to_original(borrowed, borrow_index)` inside `accrue_step` to compute utilization, and `scaled_to_original` panics on `i128` overflow. On a large-supply market at sustained high utilization, the borrow index can grow past the point where `borrowed × borrow_index` exceeds `i128::MAX` *before* the index ever reaches its cap. Since every state-changing pool verb accrues first, the whole market permanently freezes — no repay, no withdraw, no liquidation, no `update_indexes`. The codebase's own test documents this cliff (`a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`).

### Finding Description
The accrual loop in `global_sync` iterates chunks of at most `MAX_COMPOUND_DELTA_MS` and calls `accrue_step` for each [1](#0-0) . `accrue_step` computes utilization from `scaled_to_original(env, borrowed, borrow_index)`, which is `scaled.mul(env, index)` — an `i128` checked multiplication that panics on overflow [2](#0-1) [3](#0-2) . The cap in `update_borrow_index` only clamps the *new* index returned, and only *after* the utilization math already ran — it never protects the multiplication itself [4](#0-3) .

The harness test proves the failure mode concretely: a 1-billion-whole-token market at 18 decimals (raw debt ≈ 1e36 ray-scaled) on the XLM curve at 98% utilization overflows inside `scaled_to_original` once the index passes ~170×, well below `MAX_BORROW_INDEX_RAY`, and the panic propagates out of `update_indexes`, `withdraw`, and `repay` alike [5](#0-4) .

Reachability by an unprivileged address: `supply`/`borrow` are permissionless. An attacker (or syndicate of accounts, since per-account position limits bound count, not size) can push a high-decimals listed asset to near-max utilization and keep it there by repaying-withdrawing other collateral and re-borrowing, or simply by opening a max-sized borrow and refusing repayment — liquidations cannot restore utilization once the cliff is hit because `liquidate` accrues first too. Caps bound per-market size but listings can set high caps and 18-decimal assets multiply raw values by `10^18`, so the ray-value ceiling is reachable well below `i128::MAX` headroom.

### Impact Explanation
Permanent freezing of funds. Once `borrowed × borrow_index` crosses the `i128` ceiling, every entrypoint on that pool — `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `recapitalize`, `flash_loan`, `flash_position`, `update_indexes` — panics inside `global_sync` before doing any work. All supplier deposits and borrower collateral routed through that market are frozen forever; there is no admin unwind because even governance-invoked paths accrue first. This is the same impact class as the Xen PoD bug: mishandled arithmetic in an error/growth path produces an unrecoverable hang rather than a bounded failure.

### Likelihood Explanation
Medium. Triggering requires a high-decimal market with a large cap and sustained ~98% utilization for multiple years at the steep slope, which is a real but extreme configuration — mitigated by the fact that (a) utilization this high normally triggers `max_utilization` entry gates, and (b) the index still needs years of compounding to reach the cliff. However, no mechanism exists to reverse it once reached, and an attacker controlling the marginal borrow can keep utilization pinned while honest users' exits remain open only until the cliff.

### Recommendation
- In `accrue_step`, clamp `borrow_index`/`supply_index` to their caps *before* calling `scaled_to_original`, or use a saturating `mul_div` for the utilization computation so utilization saturates at `RAY` instead of trapping.
- Alternatively, make `scaled_to_original` saturation-aware in the accrual path only (it must keep panicking for user-facing unscale calls), or early-exit `accrue_step` once `borrow_index == MAX_BORROW_INDEX_RAY` with zero additional interest, so capped markets stay operable.
- Add a regression test asserting `withdraw`/`repay` still succeed after the index reaches its cap on a whale market.

### Proof of Concept
The in-repo test at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs` lines 321-360 is a working PoC:

```rust
let mut t = LendingTest::new()
    .with_market(big("BIG18", 18, xlm_curve()))
    .with_market(col())
    .with_max_utilization_disabled_all_markets()
    .build();
lift_caps(&t, "BIG18", 18);
t.supply_raw(BOB, "BIG18", BILLION * 10i128.pow(18));   // unprivileged supply
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", BILLION * 10i128.pow(18) / 100 * 98); // unprivileged borrow @98% util

// advance ledger time year by year via update_indexes
// eventually: try_update_indexes_for -> MATH_OVERFLOW inside scaled_to_original
// then permanently:
//   try_withdraw_raw(BOB, "BIG18", 1) -> MATH_OVERFLOW
//   try_repay(ALICE, "BIG18", 1.0)    -> MATH_OVERFLOW
```

Every subsequent call on the market panics during `global_sync`, permanently freezing supplier principal and collateral.

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

**File:** common/src/rates/simulate.rs (L60-64)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);
```

**File:** common/src/rates/scaling.rs (L13-16)
```rust
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-360)
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
    std::println!(
        "ray-value cliff reached after {years} years at 98 percent utilization on the XLM curve; last index x{:.1}",
        last.borrow_index as f64 / RAY as f64
    );
```
