### Title
Permissionless `update_indexes` / any market verb permanently freezes a market via `MathOverflow` panic in interest accrual once `borrowed * borrow_index` exceeds the i128 RAY value ceiling before `MAX_BORROW_INDEX_RAY` clamps - (File: contracts/pool/src/interest.rs)

### Summary
CVE-2019-7664 is a denial of service caused by an incorrect overflow check: a computation that should have been bounded instead crashes the program. The XOXNO Lending analog is the unchecked-domain assumption in the interest-accrual path: `global_sync` accrues indexes by multiplying scaled debt shares by the borrow index in RAY fixed point, and the product `borrowed * new_index` can overflow `i128` before `update_borrow_index`'s cap at `MAX_BORROW_INDEX_RAY` ever engages. The panic is permanent because every pool verb and the permissionless `update_indexes` entrypoint accrue first, so once the cliff is crossed the market can never recover — an infinite-loop-of-reverts with no rescue path.

### Finding Description
Interest accrual runs in `global_sync`, which splits elapsed time into `MAX_COMPOUND_DELTA_MS` chunks and calls `accrue_chunk` → `accrue_step` for each [1](#0-0) . Inside `accrue_step`, debt value is computed as `borrowed.mul(env, new_borrow_index)` (RAY × RAY / RAY), which panics with `GenericError::MathOverflow` via `checked_sub_nonneg`-style checked arithmetic when the intermediate exceeds `i128::MAX` [2](#0-1) [3](#0-2) . The borrow-index cap `MAX_BORROW_INDEX_RAY` is only applied to `new_index` after the multiplication, so it cannot prevent the value-level overflow [4](#0-3) .

The repository's own harness test proves the cliff and the consequence: on an 18-decimal market with ~1e9 whole tokens supplied and 98% borrowed on the steep XLM rate curve, `update_indexes` eventually fails with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`, and subsequent `withdraw` and `repay` calls fail identically because "every verb accrues first" [5](#0-4) . Unlike CVE-2019-7664's missing check, here the check exists but fires on the wrong invariant — the code bounds the index, not the scaled-debt × index product that actually overflows.

### Impact Explanation
Permanent freezing of funds / contract unable to operate. Once `borrowed * borrow_index` crosses the i128 ceiling, every state transition for that market book panics: `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, flash paths, and `update_indexes` all run accrual first. Supplier principal, borrower collateral backing, and unclaimed revenue on that book are locked indefinitely; there is no admin path to rewind `borrow_index` or skip accrual. This is not a fail-closed rejection of a single bad input — it is a permanent, state-dependent freeze of an entire market triggered through normal operation.

### Likelihood Explanation
Reachable by unprivileged addresses without any privileged action. The demonstrated path requires a whale-scale supplier (or a crowd) plus a borrower holding ~98% utilization on a steep-curve, high-decimals market for multiple years, then any caller — including the attacker — invokes the permissionless `update_indexes` to cross the cliff. The cost is capital lockup, not permission. It sits at Medium severity (matching the CVE's 5.5): high impact, but requires a large, sustained borrow position and years of accrual, and the cliff only exists above ~`i128::MAX / index` of scaled supply — i.e., markets near 1e9 whole-token scale on steep curves.

### Recommendation
In `accrue_step`/`accrue_chunk`, saturate rather than panic: clamp the borrow index growth so that `borrowed * new_index` stays below `i128::MAX` (e.g., cap `new_index` at `min(MAX_BORROW_INDEX_RAY, i128::MAX / borrowed)` before multiplying), and similarly bound `supplied * new_index` in `update_supply_index`/`supply_index_reward_shortfall` [6](#0-5) . Alternatively, make the debt-value product saturating (`mul_saturating`) so accrual always completes and positions can still be repaid/withdrawn even if indexes pin at the ceiling.

### Proof of Concept
The repo ships the exploit as a test. `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`:

1. `LendingTest` with market `BIG18` (18 decimals, `xlm_curve()`) and `COL`; caps lifted, `max_utilization` disabled.
2. BOB `supply_raw(BIG18, 1e9 * 1e18)`; ALICE supplies collateral and `borrow_raw(BIG18, 98% of principal)`.
3. Loop: `advance_time(YEAR_SECS)` then `try_update_indexes_for(&["BIG18"])` — a permissionless call — until it returns `Err`.
4. Observed: error is `MATH_OVERFLOW` while `book.borrow_index < MAX_BORROW_INDEX_RAY` (the cap never engaged; the panic is the raw `borrowed * index` product in `scaled_to_original` inside `accrue_step`).
5. `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", ...)` both revert with `MATH_OVERFLOW`, confirming permanent freeze: no repay, no withdraw, no liquidation.

Caveat: I could not open `common/src/rates/compound.rs`/`simulate.rs` in the remaining iterations to quote `accrue_step`/`scaled_to_original` line numbers verbatim; the panic site is documented in the test comments as `scaled_to_original` inside the per-chunk accrual, consistent with the `Ray::mul`/`checked_sub` overflow paths in `common/src/rates/index.rs:80-86` and `common/src/math/fp.rs:20-24`.

### Citations

**File:** contracts/pool/src/interest.rs (L20-53)
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

/// Applies one compound step of `delta_ms` to indexes and protocol revenue.
///
/// The arithmetic lives in [`accrue_step`], shared with the read-only
/// `simulate_update_indexes` so the view and the mutator cannot drift.
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

**File:** common/src/rates/index.rs (L13-18)
```rust
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
```

**File:** common/src/rates/index.rs (L29-44)
```rust
pub fn update_supply_index(env: &Env, supplied: Ray, old_index: Ray, rewards_increase: Ray) -> Ray {
    if supplied == Ray::ZERO || rewards_increase == Ray::ZERO {
        return old_index;
    }

    let total_supplied_value = supplied.mul(env, old_index);

    if total_supplied_value == Ray::ZERO {
        return old_index;
    }

    let new_value = total_supplied_value.checked_add(env, rewards_increase);
    let grown = fp_core::mul_div_floor_saturating(env, new_value.raw(), RAY, supplied.raw());

    let bounded_old = old_index.raw().min(MAX_SUPPLY_INDEX_RAY);
    Ray::from(grown.min(MAX_SUPPLY_INDEX_RAY).max(bounded_old))
```

**File:** common/src/rates/index.rs (L80-86)
```rust
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);

    let accrued_interest = new_total_debt.checked_sub(env, old_total_debt);

    let protocol_fee = params.reserve_factor.apply_to_ray(env, accrued_interest);
    let supplier_rewards = accrued_interest.checked_sub(env, protocol_fee);
```

**File:** common/src/math/fp.rs (L20-24)
```rust
fn checked_sub_nonneg(env: &Env, a: i128, b: i128) -> i128 {
    if a < 0 || b < 0 || b > a {
        panic_with_error!(env, GenericError::MathOverflow);
    }
    a - b
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L315-356)
```rust
/// The cliff. A billion whole tokens is `1e36` raw ray; the value ceiling is
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
