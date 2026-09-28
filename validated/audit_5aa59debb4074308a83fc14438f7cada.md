### Title
`i128` overflow in accrued market valuation permanently freezes all market operations - (File: common/src/rates/simulate.rs)

### Summary

A sufficiently large market can reach a state where `borrowed * borrow_index` or `supplied * supply_index` no longer fits in `i128`. Interest accrual performs these products before applying the borrow/supply index ceilings, so the operation panics with `MathOverflow` instead of clamping the index. Because every pool mutation loads the market through `synced_market`, the overflow permanently prevents withdrawal, repayment, liquidation, bad-debt cleanup, recapitalization, and further index updates for that market. [1](#0-0) [2](#0-1) 

### Finding Description

`accrue_step` converts the scaled borrow and supply books to their accrued values before calculating utilization and updating the indexes:

```rust
let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
let supplied_original = scaled_to_original(env, supplied, supply_index);
```

`scaled_to_original` calls `Ray::mul`, which delegates to `mul_div_half_up`; that function panics with `GenericError::MathOverflow` when the result does not fit in `i128`. The configured `MAX_BORROW_INDEX_RAY` is only applied afterward inside `update_borrow_index`, and `MAX_SUPPLY_INDEX_RAY` is only applied inside `update_supply_index`. Neither ceiling prevents the prior scaled-value multiplication from overflowing. [3](#0-2) [4](#0-3) [5](#0-4) 

This state is reachable through ordinary unprivileged controller calls. An attacker can create an account with `supply(caller, 0, spoke_id, assets)`, add collateral, and draw a very large borrow through `borrow(caller, account_id, borrows, to)`, subject to the configured caps. Caps may reach `max_cap_for_decimals`; for an 18-decimal asset this permits roughly 170 billion whole tokens, while only about 1 billion whole tokens produces a raw RAY book of `1e36`. Since the `i128` value ceiling is approximately `1.70e38`, index growth of about 170x is sufficient to make the accrued book unrepresentable well before the `1e36` index ceiling engages. [6](#0-5) [7](#0-6) [8](#0-7) 

Once such an index has been committed, any later touch of the market loads a `Cache` and calls `global_sync` before executing the requested operation. The first step again multiplies the stored scaled totals by the stored indexes and panics. Consequently, even actions that should reduce risk cannot execute: `repay`, `withdraw`, `liquidate`, `clean_bad_debt`, `recapitalize`, and controller-driven `update_indexes` all reach a pool path that accrues first. The owner-only `update_params` path likewise accrues under the old model before replacing it. [9](#0-8) [10](#0-9) [11](#0-10) 

The repository contains a dedicated regression that demonstrates this cliff: after constructing a one-billion-token, 18-decimal market and borrowing 98% of it, repeated index updates eventually fail with `MATH_OVERFLOW`; subsequent `withdraw` and `repay` attempts fail with the same error while the borrow index remains below `MAX_BORROW_INDEX_RAY`. [12](#0-11) [13](#0-12) 

### Impact Explanation

All users' supply and debt in the affected market become permanently frozen. Suppliers cannot withdraw, borrowers cannot repay, liquidators cannot reduce unsafe positions, and cleanup or recapitalization cannot run because each path performs the overflowing accrual before applying its state change. The panic also prevents rate-model replacement because `update_params` accrues under the old model first, leaving contract upgrade as the only plausible recovery path. [2](#0-1) [10](#0-9) 

### Likelihood Explanation

The attack requires no privileged role, oracle manipulation, leaked key, token semantics, or off-chain component. It does require a high-decimal market admitted with a very large cap, substantial attacker capital, and enough elapsed accrual for the scaled book value to cross the `i128` boundary. Those requirements reduce practical likelihood, but the resulting failure is deterministic and cannot be undone by ordinary user or administrative market operations once reached. This maps the CVE's denial-of-service class to a market-freezing condition reachable solely through public `supply`, `borrow`, and index-accrual paths.

### Recommendation

Constrain accrued values before unscaling rather than relying only on index ceilings. In particular:

- Before each accrual step, compute safe index bounds such as `i128::MAX / borrowed.raw()` and `i128::MAX / supplied.raw()`, and clamp or handle accrual before `borrowed * borrow_index` or `supplied * supply_index` overflows.
- Prefer widened intermediate arithmetic for market-value products, with an explicit saturation or safe index-splitting policy rather than a panic.
- Enforce a maximum stored RAY book value in addition to maximum token caps, so admitted supply/borrow caps cannot approach the representable-value cliff.
- Add a non-accruing emergency path for reducing debt or withdrawing only against already committed values, or make governance able to bound/disable further accrual without first invoking the overflowing multiplication.
- Extend the existing cliff regression to cover `liquidate`, `clean_bad_debt`, `recapitalize`, `flash_loan`, and `update_params`, and to assert that the market remains recoverable below the index ceiling.

### Proof of Concept

The checked-in scenario at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356` is a direct proof:

1. Configure an 18-decimal `BIG18` market with the steep rate curve and lift its spoke caps to `max_cap_for_decimals(18)`.
2. Call `supply` for the liquidity account with `assets = [(BIG18, 1_000_000_000 * 10^18)]`.
3. Supply sufficient `COL` collateral and call `borrow` with `borrows = [(BIG18, 980_000_000 * 10^18)]`.
4. Advance ledger time and repeatedly call controller `update_indexes` for `BIG18`.
5. The accrual eventually fails with `MATH_OVERFLOW` inside `scaled_to_original`, while `borrow_index < MAX_BORROW_INDEX_RAY`.
6. Calls to `withdraw` and `repay` then fail with the same `MATH_OVERFLOW`, demonstrating that the market cannot be exited or repaired through ordinary operations. [14](#0-13)

### Citations

**File:** common/src/rates/simulate.rs (L51-70)
```rust
pub fn accrue_step(
    env: &Env,
    params: &MarketParams,
    borrowed: Ray,
    supplied: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    delta_ms: u64,
) -> AccrualStep {
    let borrowed_original = scaled_to_original(env, borrowed, borrow_index);
    let supplied_original = scaled_to_original(env, supplied, supply_index);
    let util = utilization(env, borrowed_original, supplied_original);
    let borrow_rate = calculate_borrow_rate(env, util, params);
    let interest_factor = compound_interest(env, borrow_rate, delta_ms);

    let new_borrow_index = update_borrow_index(env, borrow_index, interest_factor);

    let (supplier_rewards, protocol_fee) =
        calculate_supplier_rewards(env, params, borrowed, new_borrow_index, borrow_index);

```

**File:** contracts/pool/src/ops/mod.rs (L29-46)
```rust
/// Loads a market cache and accrues interest through the current ledger time.
pub(crate) fn synced_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    let mut cache = Cache::load(env, hub_asset);
    interest::global_sync(env, &mut cache);
    cache
}

/// Renews instance TTL, then loads and accrues the market.
pub(crate) fn renewed_market(env: &Env, hub_asset: &HubAssetKey) -> Cache {
    renew_instance(env);
    synced_market(env, hub_asset)
}

/// Validates `action.amount ≥ 0`, syncs the market, and returns (cache, scaled position).
pub(crate) fn load_leg(env: &Env, action: &PoolAction) -> (Cache, Ray) {
    require_nonneg_amount(env, action.amount);
    let cache = synced_market(env, &action.hub_asset);
    (cache, Ray::from(action.position.scaled_amount))
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/math/fp.rs (L49-56)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }

    /// Divides this value by `other`, rounding the result half up.
    pub fn div(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, RAY, other.0))
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

**File:** contracts/controller/src/lib.rs (L90-115)
```rust
    /// Supplies `assets` as collateral and returns the account id; `account_id = 0`
    /// creates an account in `spoke_id`. Third parties may only top up existing
    /// supply positions; owners and delegates may add assets.
    #[when_not_paused]
    fn supply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        assets: Vec<(HubAssetKey, i128)>,
    ) -> u64 {
        positions::process_supply(&env, &caller, account_id, spoke_id, &assets)
    }

    /// Borrows against `account_id`'s collateral, paying `to` or the caller.
    /// Requires owner or delegate authorization and post-borrow solvency.
    #[when_not_paused]
    fn borrow(
        env: Env,
        caller: Address,
        account_id: u64,
        borrows: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) {
        positions::process_borrow(&env, &caller, account_id, &borrows, to);
    }
```

**File:** common/src/validation.rs (L41-56)
```rust
/// Returns the largest cap, in asset base units, whose ray-scaled form still
/// fits in `i128`.
///
/// Returns 0 when `asset_decimals > RAY_DECIMALS`, since the ray form is not
/// representable in that case. Enforced by
/// [`require_cap_within_asset_domain`], so stored caps can never overflow the
/// asset→ray rescale.
pub fn max_cap_for_decimals(asset_decimals: u32) -> i128 {
    let Some(exp) = RAY_DECIMALS.checked_sub(asset_decimals) else {
        return 0;
    };
    let upscale = 10i128
        .checked_pow(exp)
        .expect("10^(RAY_DECIMALS - asset_decimals) fits i128 for asset_decimals <= RAY_DECIMALS");
    i128::MAX / upscale
}
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** contracts/pool/src/ops/market.rs (L50-57)
```rust
/// Accrues interest under the old model, commits it, then replaces the interest
/// and flash-loan parameters and validates them against the stored decimals.
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
    events::emit_market_params(env, hub_asset.hub_id, hub_asset.asset, params);
```

**File:** contracts/pool/src/ops/market.rs (L60-72)
```rust
/// Accrues interest for each market in `hub_assets` and emits one state event
/// per market.
///
/// Always commits state so same-ledger simulation records the write footprint
/// needed if time advances before transaction inclusion.
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
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
