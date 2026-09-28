### Title
RAY-value overflow in accrual permanently bricks a market before the borrow-index cap can engage - (File: common/src/rates/index.rs / common/src/rates/scaling.rs)

### Summary
CVE-2024-52919 is a remote-crash/DoS class bug (Bitcoin Core node killed by malformed input). The XOXNO Lending analog is a permanent liveness kill of an entire market: accrual computes `borrowed_scaled * borrow_index` and `supplied * supply_index` in `i128` via `Ray::mul`, and at high debt scale times a high index this product overflows `i128::MAX` *before* `update_borrow_index`'s `MAX_BORROW_INDEX_RAY` cap can engage. Since `interest::global_sync` runs at the top of every mutating entrypoint, once the market crosses the cliff every verb — repay, withdraw, liquidate, supply — panics with `MathOverflow` forever.

### Finding Description
Every pool mutation loads the cache and calls `interest::global_sync` → `accrue_chunk` → `accrue_step`, which evaluates `scaled_to_original(borrowed, borrow_index)` and `scaled_to_original(supplied, supply_index)` to derive utilization (`contracts/pool/src/cache/scale.rs:23-24`, `contracts/pool/src/interest.rs:39-53`). `Ray::mul` panics with `GenericError::MathOverflow` on `i128` overflow (`common/src/math/fp.rs:13-25`, via `calculate_supplier_rewards` at `common/src/rates/index.rs:80-83` and `update_supply_index` at `common/src/rates/index.rs:34`).

The intended guard is `MAX_BORROW_INDEX_RAY` in `update_borrow_index` (`common/src/rates/index.rs:13-19`), but it caps the *index*, not the *value* `borrowed_scaled * borrow_index`. For a sufficiently large book (debt principal scaled to RAY ≈ >10³⁶ units), the product overflows while `borrow_index` is still well below the cap — the codebase's own regression test proves this and asserts the cap never engaged: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:316-360` ("the index cap did not engage before the value overflow"; "The market is frozen: exits and repayments accrue first and hit the same panic").

Reachable by a single unprivileged address:

1. `supply(hub, BIG18_asset, huge_amount)` — create a whale-scale market (supply caps are per-asset configuration and the attacker can use the deepest market or spread across hubs).
2. Deposit collateral and `borrow` to ~98% utilization on a curve whose steep segment compounds fast (the test uses the XLM curve shape).
3. Let time advance — `update_indexes` is callable by anyone, and accrual also happens implicitly inside every other user's op.
4. At the cliff, the next accrual panics; because `borrow_index`/`supply_index` only move through this panicking path, no transaction can ever succeed on the market again.

### Impact Explanation
Permanent freezing of all funds in the affected market: suppliers cannot withdraw, borrowers cannot repay (repay accrues first and panics), liquidations fail, and bad-debt cleanup (`clean_bad_debt` → seize → `apply_bad_debt_to_supply_index`) cannot run because it too syncs indexes. All supplied tokens in the book are permanently locked in the pool contract. This satisfies the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Requires a market whose RAY-scaled debt principal approaches `i128::MAX / borrow_index` — i.e., an extremely large book (billions of 18-decimal units) sustained at high utilization for years, or a smaller book pushed further by compounding. Not triggerable on demand, but the overflow threshold is finite, accrual is permissionless, and the cliff is silent: the market functions normally until one transaction crosses the boundary and permanently bricks it. Severity Medium (permanent freeze, conditional on market scale).

### Recommendation
Bound the *product*, not just the index: in `accrue_step`/`calculate_supplier_rewards`/`update_supply_index`, compute `scaled * index` via the existing `I256`/`mul_div`-style widened path (or `checked_mul` with a saturation/clamp), or cap `borrow_index`/`supply_index` dynamically at `i128::MAX / max(scaled)` so accrual clamps instead of panicking. Alternatively enforce a per-market cap on `supplied`/`borrowed` scaled shares derived from the index ceiling, so the reachable domain can never overflow.

### Proof of Concept
The shipped regression test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360`) is a direct PoC: supply `BILLION * 10^18` of an 18-decimal asset, borrow 98% of it, advance time year-by-year; `update_indexes` eventually returns `MathOverflow` (33) with `borrow_index < MAX_BORROW_INDEX_RAY`, after which `withdraw` and `repay` both fail with `MathOverflow` — permanent freeze. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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

**File:** common/src/rates/index.rs (L73-89)
```rust
pub fn calculate_supplier_rewards(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    new_borrow_index: Ray,
    old_borrow_index: Ray,
) -> (Ray, Ray) {
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);

    (supplier_rewards, protocol_fee)
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
