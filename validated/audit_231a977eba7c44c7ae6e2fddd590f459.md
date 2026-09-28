### Title
Permanent market freeze: unchecked `scaled * index` overflow in accrual traps every pool entrypoint - ([File: common/src/rates/simulate.rs](common/src/rates/simulate.rs))

### Summary
Analogous to CVE-2016-9817 — where a guest-triggerable abort vector crashed the whole Xen host — an unprivileged user can steer a XOXNO Lending market into a state where the mandatory interest-accrual prelude panics with `MathOverflow` on every subsequent call. Because `interest::global_sync` runs first inside every pool mutator, once the panic condition is reached the market is permanently bricked: no `supply`, `borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `claim_revenue`, or `recapitalize` can execute, and all supplier funds in that `(hub_id, asset)` book are frozen forever.

### Finding Description
Every pool entrypoint loads the market `Cache` and calls `interest::global_sync`, which chunks elapsed time and calls `accrue_step` for each window [1](#0-0) . `accrue_step` unconditionally unscales the market's scaled balances at the current indexes:

```rust
let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
let supplied_original = scaled_to_original(env, supplied, supply_index);
``` [2](#0-1)  and `scaled_to_original` is a plain `Ray::mul`, which panics via `panic_with_error!(env, GenericError::MathOverflow)` when `scaled * index / RAY` exceeds `i128` [3](#0-2) . The same pattern exists in `update_supply_index` (`supplied.mul(env, old_index)`) and `calculate_supplier_rewards` (`borrowed.mul(env, new_borrow_index)`) [4](#0-3) .

The design intends `MAX_BORROW_INDEX_RAY` / `MAX_SUPPLY_INDEX_RAY` to cap index growth [5](#0-4) , but the cap is applied to the *index* while the overflow happens on the *value* (`scaled_shares × index`). A market holding a sufficiently large scaled balance crosses the `i128` value ceiling while the index is still far below its cap, so the cap never engages — exactly like the Xen EA-bit abort path reaching a fatal handler before the normal guard could run. The repo's own test proves the freeze and its permanence:

```rust
// The market is frozen: exits and repayments accrue first and hit the same panic.
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
``` [6](#0-5) . Any user can trigger the accrual that crosses the cliff via permissionless `controller::update_indexes` [7](#0-6) , and once crossed there is no recovery path — no admin function skips `global_sync`, and the supply index can only be lowered by `apply_bad_debt_to_supply_index`, which itself is only reachable through a liquidation/cleanup path that accrues first [8](#0-7) .

### Impact Explanation
Permanent freezing of funds and a contract unable to operate: every supplier's deposit in the affected market becomes unrecoverable, borrowers cannot repay, liquidators cannot liquidate, and `clean_bad_debt`/`recapitalize` cannot rescue the book. The panic is not a fail-closed input rejection — it is triggered by the protocol's own mandatory state transition on a market shape that unprivileged `supply`/`borrow` calls created, mirroring the Xen host crash induced by a guest-controlled abort.

### Likelihood Explanation
The setup requires no privilege: an attacker supplies a very large principal (e.g. via an 18-decimal asset with lifted caps) and borrows to sustained high utilization, as the harness test does with `supply_raw`/`borrow_raw` [9](#0-8) . Ordinary market interest then does the rest; `update_indexes` is permissionless so no keeper cooperation is needed, and the cliff is reached in years on the steep curve segment — sooner for larger `supplied × index` products. The barrier is capital (the product must approach `i128::MAX ≈ 1.7e38` in RAY terms), not permission, so this is Medium rather than High.

### Recommendation
Make accrual overflow-safe instead of trapping: saturate or clamp the unscaled value in `accrue_step`/`update_supply_index`/`calculate_supplier_rewards` (e.g. via a saturating `mul_div` as `calculate_scaled_cap` and `protocol_fee_shares` already do [10](#0-9) ), or check `scaled * index` headroom *before* multiplying and clamp the index at the largest value that keeps the unscaled amount within `i128`. A governance- or keeper-reachable escape hatch that resets `last_timestamp` and writes down an overgrown index without running `global_sync` would additionally unbrick any market already at the cliff.

### Proof of Concept
Encoded by `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` [11](#0-10) :

1. List an 18-decimal market (`BIG18`) on the XLM rate curve; supply `1e9 * 1e18` units and borrow ~98% of it from a collateralized account.
2. Let time advance (or call permissionless `update_indexes` as chunks accumulate). `accrue_step` recomputes `scaled_to_original(borrowed, borrow_index)` each chunk; once `borrowed_scaled * borrow_index` leaves `i128`, `Ray::mul` panics `MathOverflow` while `borrow_index < MAX_BORROW_INDEX_RAY` — the cap never engages.
3. Every later `withdraw`, `repay`, `liquidate`, and `update_indexes` call on the market re-enters `global_sync` and panics identically, permanently freezing all supplied funds.

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

**File:** contracts/pool/src/interest.rs (L73-89)
```rust
pub(crate) fn apply_bad_debt_to_supply_index(cache: &mut Cache, bad_debt: Ray) {
    let total_supplied_value = cache.supplied().mul(cache.env(), cache.supply_index());

    if total_supplied_value == Ray::ZERO {
        return;
    }

    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
}
```

**File:** common/src/rates/simulate.rs (L60-61)
```rust
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
```

**File:** common/src/rates/scaling.rs (L14-16)
```rust
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
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

**File:** common/src/rates/index.rs (L34-81)
```rust
    let total_supplied_value = supplied.mul(env, old_index);

    if total_supplied_value == Ray::ZERO {
        return old_index;
    }

    let new_value = total_supplied_value.checked_add(env, rewards_increase);
    let grown = fp_core::mul_div_floor_saturating(env, new_value.raw(), RAY, supplied.raw());

    let bounded_old = old_index.raw().min(MAX_SUPPLY_INDEX_RAY);
    Ray::from(grown.min(MAX_SUPPLY_INDEX_RAY).max(bounded_old))
}

/// Computes the portion of `rewards_increase` not reflected by the change in
/// supplied value implied by moving from `old_index` to `new_index` over
/// `supplied` (i.e. `supplied * new_index - supplied * old_index`).
///
/// Panics if `new_index` implies less supplied value than `old_index`, or if
/// the distributed value exceeds `rewards_increase`.
pub fn supply_index_reward_shortfall(
    env: &Env,
    supplied: Ray,
    old_index: Ray,
    new_index: Ray,
    rewards_increase: Ray,
) -> Ray {
    let distributed = supplied
        .mul(env, new_index)
        .checked_sub(env, supplied.mul(env, old_index));
    rewards_increase.checked_sub(env, distributed)
}

/// Splits the interest accrued on `borrowed` debt between `old_borrow_index`
/// and `new_borrow_index` into supplier rewards and protocol fee, per
/// `params.reserve_factor`. Returns `(supplier_rewards, protocol_fee)`.
///
/// Panics if `new_borrow_index` implies less total debt than
/// `old_borrow_index`, or if the rounded protocol fee exceeds the accrued
/// interest.
pub fn calculate_supplier_rewards(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    new_borrow_index: Ray,
    old_borrow_index: Ray,
) -> (Ray, Ray) {
    let old_total_debt = borrowed.mul(env, old_borrow_index);
    let new_total_debt = borrowed.mul(env, new_borrow_index);
```

**File:** common/src/rates/index.rs (L94-99)
```rust
pub fn protocol_fee_shares(env: &Env, fee: Ray, supply_index: Ray, supplied: Ray) -> Ray {
    let raw = fp_core::mul_div_floor_saturating(env, fee.raw(), RAY, supply_index.raw());

    let headroom = i128::MAX.saturating_sub(supplied.raw());
    Ray::from(raw.min(headroom))
}
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L316-361)
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
}
```

**File:** contracts/controller/src/lib.rs (L367-372)
```rust
    /// Accrues pool borrow and supply indexes for `assets`. Permissionless;
    /// requires caller authorization.
    #[when_not_paused]
    fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>) {
        markets::update_indexes(&env, caller, assets);
    }
```
