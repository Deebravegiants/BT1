### Title
Accrual-time `i128` value overflow permanently freezes a market before the borrow-index cap engages - (File: common/src/rates/scaling.rs)

### Summary
The bug class suggested by CVE-2017-2396 (memory corruption → crash/DoS) maps onto Soroban as unchecked numeric-domain overflow in the accrual path. In this codebase, a whale-scale market at sustained high utilization reaches the RAY value ceiling inside `scaled_to_original` *before* the borrow index reaches `MAX_BORROW_INDEX_RAY`. Since every mutating verb accrues first, the market then reverts on every call forever: suppliers cannot withdraw, borrowers cannot repay, liquidators cannot liquidate. An unprivileged attacker can drive the market into this state through ordinary `supply`/`borrow` calls.

### Finding Description
Interest accrual values positions as `scaled_shares × index` in RAY via `scaled_to_original` → `Ray::mul` → `mul_div_*`, which panics with `GenericError::MathOverflow` when the product exceeds `i128` even though the widened `I256` path is exact — the *result* still must fit `i128`. [1](#0-0)  `accrue_step` computes `borrowed_original = scaled_to_original(borrowed, borrow_index)` on every chunk [2](#0-1) , and `global_sync` runs before every pool mutation [3](#0-2) . The documented bounds admit token-to-RAY inputs up to ~170 billion whole tokens and a borrow-index ceiling of `10^36`, but the value ceiling `borrowed × index < i128::MAX` is reached first at high utilization on a steep curve, so the index cap never clamps growth. [4](#0-3) 

### Impact Explanation
Permanent freezing of funds and protocol insolvency for the affected market. Once `borrowed × borrow_index` exceeds `i128::MAX`, `accrue_chunk` panics inside every `supply`/`withdraw`/`borrow`/`repay`/`net_settle`/`seize_positions`/`flash`/`claim_revenue` path for that market, because all of them sync the market first. The harness test confirms `withdraw` and `repay` both revert with `MATH_OVERFLOW` and that the index cap did not engage [5](#0-4) . All supplier principal in that market is permanently locked, and outstanding debt becomes uncollectible and unsocializable (`clean_bad_debt` → `seize_positions` → `synced_market` also accrues). [6](#0-5) 

### Likelihood Explanation
The trigger requires an unprivileged caller to supply a very large position (approaching the admitted cap domain, ~170 billion whole-token scale for an 18-decimal asset) and borrow ~98% of it, then wait for compound growth. Caps can be governance-set high and `max_utilization` is a separate optional gate the attacker does not control, but nothing in the accrual path bounds `borrowed × index`; the test demonstrates the cliff is reached in a few years at the XLM-curve steep segment without exceeding any configured cap or the borrow-index ceiling. Likelihood is constrained by the capital required, but the attack uses only `controller::supply` and `controller::borrow` with attacker-owned funds and a borrowed position the attacker can abandon. [7](#0-6) 

### Recommendation
Bound the accrual inputs, not just the indexes: either cap `borrowed` (scaled debt shares) at listing/update time so `borrowed × MAX_BORROW_INDEX_RAY` fits `i128`, or make `accrue_step` clamp the borrow index to the largest value that keeps `scaled_to_original` representable before applying `MAX_BORROW_INDEX_RAY`. A fail-safe alternative is to make `global_sync` treat `MathOverflow` in the value computation as "index pinned at ceiling" rather than reverting, so exits and repayments remain possible. Validation of caps should use `require_cap_within_asset_domain` against the *maximum reachable* index, not the current one. [8](#0-7) 

### Proof of Concept
Reproduced by the existing harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap`:

1. Attacker calls `controller::supply(caller, 0, spoke, [(hub_BIG18, 1e9 × 10^18 units)])` — a large but admitted supply.
2. From a second collateralized account, `controller::borrow` draws 98% of the BIG18 liquidity, driving utilization onto the steep curve segment.
3. Time advances; each `pool::update_indexes` (callable permissionlessly through the controller) runs `global_sync` → `accrue_step` → `scaled_to_original(borrowed, new_index)`.
4. When `borrowed × new_index > i128::MAX`, `mul_div` panics `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY`, so the index cap never engages.
5. Thereafter every verb reverts: the test asserts `try_withdraw_raw(BOB, "BIG18", 1)` and `try_repay(ALICE, "BIG18", 1.0)` both fail with `errors::MATH_OVERFLOW`, and liquidation/bad-debt paths fail identically since they sync the same market. [9](#0-8)

### Citations

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L18-32)
```rust
/// Converts an asset-unit `cap` to a scaled `Ray` value, rounding down.
///
/// The division saturates at `i128::MAX` instead of panicking, so the cap check
/// fails open rather than trapping an entry path. The asset-to-RAY
/// rescale still panics on overflow; listings validate caps with
/// [`crate::validation::require_cap_within_asset_domain`]. Position accounting
/// uses [`calculate_scaled_supply`] and [`calculate_scaled_borrow`], which panic
/// on overflow.
pub fn calculate_scaled_cap(env: &Env, cap: i128, decimals: u32, index: Ray) -> Ray {
    Ray::from(fp_core::mul_div_floor_saturating(
        env,
        Ray::from_asset(env, cap, decimals).raw(),
        RAY,
        index.raw(),
    ))
```

**File:** common/src/rates/simulate.rs (L60-66)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);
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

**File:** docs/reference/formulas.md (L425-437)
```markdown
| Asset decimals 0..=18 | Exact token-to-RAY upscaling. Below 3: collateral only, no flash loans, no liquidation fee, its account's only supply position, at least 2 whole units while in debt |
| Both indexes initially RAY; ceiling 10^36 | 10^9 times initial index; protocol constants |
| Supply-index floor 10^24 | At most 1,000 times the shares minted at index one for the same deposit |
| Borrow APR maximum 2 RAY | 200% annual rate; not a bound on balance growth alone |
| Token-to-RAY input maximum `i128::MAX / 10^(27-d)` | About 170.14 billion whole tokens, before other limits |
| Deposit conversion at the supply-index floor | About 170.14 million whole tokens before scaled-share overflow |

The token-to-RAY maximum is also the admitted cap maximum. Accrued position
values and market totals must independently fit the RAY domain; valid caps and
bounded indexes do not guarantee that future accrual fits. Value overflow can
occur before the index ceiling and block repayment/withdrawal because those
operations accrue first. At the borrow-index ceiling, further accrual produces
no borrower interest. No dedicated ceiling alarm is emitted.
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L327-360)
```rust
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

**File:** contracts/pool/src/ops/seize.rs (L20-27)
```rust
    let mut cache = ops::synced_market(env, &entry.hub_asset);
    let position = Ray::from(entry.position.scaled_amount);

    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
```
