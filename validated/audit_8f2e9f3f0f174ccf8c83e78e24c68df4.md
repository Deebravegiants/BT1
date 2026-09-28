### Title
Unbounded `borrowed × borrow_index` product permanently freezes a market via `MathOverflow` panic in accrual - (File: common/src/rates/index.rs)

### Summary
The GPAC integer-overflow bug class maps to XOXNO Lending's share/index arithmetic. All RAY-valued products (`supplied × supply_index`, `borrowed × borrow_index`) are computed through `mul_div_half_up`/`Ray::mul`, which panic with `GenericError::MathOverflow` when the exact result leaves `i128` (the `I256` widened path returns `None` past `i128`, converted to a panic). [1](#0-0)  Because every state-changing entrypoint runs `global_sync` → `accrue_step` before touching user balances, the first accrual that pushes `borrowed × borrow_index` past `i128::MAX` bricks the market: supply, borrow, withdraw, repay, liquidate, `clean_bad_debt`, `recapitalize`, and `update_indexes` all revert forever. [2](#0-1) 

### Finding Description
`calculate_supplier_rewards` multiplies `borrowed.mul(env, old_borrow_index)` and `borrowed.mul(env, new_borrow_index)` directly, with no saturation or early clamp. [3](#0-2)  The `MAX_BORROW_INDEX_RAY` cap only limits the index itself; it does not bound the product. [4](#0-3)  For a high-decimals market with large scaled debt, the RAY-domain debt value reaches `i128::MAX` (~1.7e38 RAY, ≈170 billion whole tokens of value) while `borrow_index` is still far below its `1e36` ceiling, so the cap never protects the multiplication. The protocol's own harness demonstrates the freeze: after sustained high utilization on an 18-decimals market, `try_update_indexes_for`, `try_withdraw_raw`, and `try_repay` all revert with `MATH_OVERFLOW`, and the comment states "the market is frozen: no repay, no withdraw, no liquidation. The index cap never engages." [5](#0-4) 

An unprivileged attacker reachable path: supply large collateral, borrow to maximum LTV on a high-decimals market (e.g., 18 decimals, near `max_cap_for_decimals`), then repeatedly call `update_indexes` — or simply wait for any third-party interaction — until compounding pushes the debt-value product over `i128::MAX`. Every supplier's and borrower's funds in that market, including other users' deposits, are then unrecoverable.

### Impact Explanation
Permanent freezing of all user funds in the affected market. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate, and `clean_bad_debt`/`recapitalize` cannot run because they all accrue first. Note this limit is disclosed in `docs/reference/formulas.md` as an arithmetic bound, but the disclosed consequence — a one-way, unrecoverable freeze of third-party deposits triggered by ordinary accrual — is a concrete loss of user funds, not merely a documented parameter choice. [6](#0-5) 

### Likelihood Explanation
Requires the market's scaled debt value to approach `~1.7e38` RAY — on the order of 170 billion whole tokens at index ~1, or proportionally less as the index grows — so the direct attack demands either whale-scale capital or a token whose supply supports such a position. Once a large position exists, however, no attacker action is needed: ordinary compounding at high utilization crosses the bound deterministically before the index cap, and the freeze is irreversible with no rescue path. Medium likelihood, high impact when reached.

### Recommendation
In `accrue_step`/`calculate_supplier_rewards`, clamp the effective borrow index used for accrual so that `borrowed × new_borrow_index` saturates at the largest representable value instead of panicking — e.g., compute `new_borrow_index = min(computed_index, i128::MAX / borrowed * RAY-adjusted bound)` and treat further accrual as zero, mirroring the existing `MAX_BORROW_INDEX_RAY` cap semantics. [7](#0-6)  Apply the same bound to `supplied × supply_index` in `update_supply_index` and `supply_index_reward_shortfall`. [8](#0-7) 

### Proof of Concept
The repository's own test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` is the PoC: an 18-decimals market with a `BILLION * 10^18` supply and 98% borrowed reaches `MathOverflow` inside `scaled_to_original`/`calculate_supplier_rewards` within 40 simulated years of `update_indexes` calls; afterward `withdraw` and `repay` revert with the same error while `borrow_index < MAX_BORROW_INDEX_RAY`. [9](#0-8)

### Citations

**File:** common/src/math/fp_core.rs (L108-118)
```rust
pub fn mul_div_half_up(env: &Env, x: i128, y: i128, d: i128) -> i128 {
    // The zero check runs first so debug and release builds agree on a zero
    // divisor: both surface `DivisionByZero` rather than tripping the assert.
    require_nonzero_divisor(env, d);
    debug_assert!(
        x >= 0 && y >= 0 && d > 0,
        "mul_div_half_up: non-negative x, y and positive d"
    );
    try_mul_div_half_up(env, x, y, d)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow))
}
```

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

**File:** common/src/rates/index.rs (L29-45)
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
}
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

**File:** docs/reference/formulas.md (L432-437)
```markdown
The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```
