### Title
Scaled-debt overflow during accrual permanently freezes a market - (File: `common/src/rates/index.rs`)

### Summary

A sufficiently large market can reach a state where `borrowed_scaled_ray * borrow_index` exceeds `i128::MAX` before the borrow index reaches its configured ceiling. The next accrual panics while calculating total debt, causing every controller operation that synchronizes the market—including `withdraw`, `repay`, `liquidate`, `borrow`, `clean_bad_debt`, and `update_indexes`—to revert permanently. [1](#0-0) 

### Finding Description

Pool markets store debt as RAY-scaled shares and multiply those shares by the current borrow index during accrual. `update_borrow_index` caps the index only after computing the new index, and `calculate_supplier_rewards` subsequently multiplies the scaled debt by both the old and new indexes without bounding their product. [2](#0-1) [3](#0-2) 

The borrow-index ceiling is `10^36` raw RAY, equivalent to one billion times the initial index, but the total RAY-denominated debt value is still bounded by `i128::MAX`. A large scaled-debt principal can therefore overflow the value calculation long before the index cap protects it. [4](#0-3) 

Market accrual is mandatory: `global_sync` runs every elapsed-time chunk and calls `accrue_step`, while `update_indexes` invokes the pool’s market-accrual path. [5](#0-4) [6](#0-5) [7](#0-6) 

An unprivileged user can create this condition through ordinary `supply` and `borrow` calls if the listed market’s caps admit a sufficiently large position. The attacker supplies a very large amount of the debt asset, supplies enough collateral on the same account, and borrows a high-utilization share of that liquidity. After interest growth makes `borrowed_scaled_ray * new_borrow_index` exceed `i128::MAX`, any later `update_indexes` call commits the market to a permanently failing accrual path. [8](#0-7) [9](#0-8) 

### Impact Explanation

This permanently freezes all user funds associated with the affected market. Suppliers cannot withdraw because withdrawal synchronizes the market first; borrowers cannot repay; liquidators cannot reduce risk; and bad-debt cleanup cannot proceed. The test harness demonstrates that after the overflow condition is reached, both `withdraw` and `repay` fail with `MathOverflow`, while the stored borrow index remains below `MAX_BORROW_INDEX_RAY`. [10](#0-9) 

Because the panic occurs before the relevant operation commits, there is no ordinary user-level recovery path. A governance upgrade may be the only remediation, but existing funds remain frozen until such an upgrade is deployed. [11](#0-10) 

### Likelihood Explanation

The attack requires no privileged call, malformed encoding, oracle manipulation, reentrancy, or external-contract dishonesty. It does require an unusually large token position and a market whose configured supply and borrow caps permit that position; caps are validated only to remain within the asset’s RAY domain, not to keep `scaled_shares * future_index` below `i128::MAX`. [12](#0-11) 

The economic cost is substantial because the attacker must provide both the borrowed liquidity and sufficient collateral. Nevertheless, the attack also freezes unrelated suppliers’ funds once the market reaches the overflow boundary, so the impact extends beyond the attacker’s own position. [13](#0-12) 

### Recommendation

Bound market totals by the future value domain, not merely by the current asset-domain cap. In particular:

- Derive supply and borrow caps from `i128::MAX / MAX_BORROW_INDEX_RAY` and `i128::MAX / MAX_SUPPLY_INDEX_RAY`, accounting for asset-decimal scaling.
- Check `borrowed_scaled_ray * MAX_BORROW_INDEX_RAY` and `supplied_scaled_ray * MAX_SUPPLY_INDEX_RAY` before admitting new shares.
- Alternatively, change accrual arithmetic to use saturating or widened total-debt and total-supply calculations, ensuring overflow cannot permanently block repayment, withdrawal, liquidation, or cleanup.
- Add an invariant test asserting that every admitted scaled principal can be multiplied by the configured index ceiling without overflowing.

### Proof of Concept

The following is the user-reachable flow represented by the existing harness test:

```rust
let debt_asset = HubAssetKey {
    hub_id,
    asset: big_18_decimal_token,
};

let collateral_asset = HubAssetKey {
    hub_id,
    asset: collateral_token,
};

// One attacker-owned account can create both positions.
let account_id = controller.supply(
    attacker,
    0,
    spoke_id,
    vec![
        (debt_asset, 1_000_000_000 * 10i128.pow(18)),
        (collateral_asset, sufficient_collateral),
    ],
);

controller.borrow(
    attacker,
    account_id,
    vec![(debt_asset, 980_000_000 * 10i128.pow(18))],
    None,
);

// Advance ledger time until index growth pushes:
// borrowed_scaled_ray * new_borrow_index > i128::MAX.
controller.update_indexes(attacker, vec![debt_asset]);
```

The repository’s executable scenario uses `supply`, `borrow`, and repeated `update_indexes` calls to reach `MathOverflow`; afterward, a one-unit withdrawal and a repayment both fail with the same error. [14](#0-13)

### Citations

**File:** common/src/rates/index.rs (L11-19)
```rust
/// Applies `interest_factor` to `old_index` to produce the new borrow index,
/// capped at `MAX_BORROW_INDEX_RAY`.
pub fn update_borrow_index(env: &Env, old_index: Ray, interest_factor: Ray) -> Ray {
    let new_index = old_index.mul(env, interest_factor);
    if new_index.raw() > MAX_BORROW_INDEX_RAY {
        return Ray::from(MAX_BORROW_INDEX_RAY);
    }
    new_index
}
```

**File:** common/src/rates/index.rs (L73-88)
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
```

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** contracts/pool/src/interest.rs (L16-33)
```rust
/// Accrues borrow/supply indexes from `last_timestamp` to the cache's current time.
///
/// No-op when no time has elapsed. Splits long gaps into max-sized compound
/// windows, then sets `last_timestamp` to `current_timestamp`.
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

**File:** contracts/pool/src/interest.rs (L35-53)
```rust
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

**File:** contracts/pool/src/lib.rs (L174-180)
```rust
    /// Accrues interest for each market in `hub_assets` through the current
    /// ledger time. Commits state even with no elapsed time to reserve the write
    /// footprint, and emits its market state event. Restricted to the owner.
    #[only_owner]
    fn update_indexes(env: Env, hub_assets: Vec<HubAssetKey>) {
        ops::market::accrue(&env, hub_assets);
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

**File:** contracts/controller/src/markets.rs (L118-125)
```rust
/// Accrues indexes for each hub asset. Requires caller authorization and no flash loan.
pub(crate) fn update_indexes(env: &Env, caller: Address, assets: Vec<HubAssetKey>) {
    validation::require_authorized_caller(env, &caller);

    let mut cache = Context::new(env);
    let pool_addr = cache.cached_pool_address();
    pool_update_indexes_call(env, &pool_addr, &assets);
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

**File:** common/src/validation.rs (L41-70)
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

/// Panics with `CollateralError::AssetDecimalsTooHigh` if `asset_decimals`
/// exceeds `RAY_DECIMALS`, or with `CollateralError::InvalidBorrowParams` if
/// `cap` exceeds the value returned by `max_cap_for_decimals`.
pub fn require_cap_within_asset_domain(env: &Env, cap: i128, asset_decimals: u32) {
    if RAY_DECIMALS.checked_sub(asset_decimals).is_none() {
        panic_with_error!(env, CollateralError::AssetDecimalsTooHigh);
    }
    assert_with_error!(
        env,
        cap <= max_cap_for_decimals(asset_decimals),
        CollateralError::InvalidBorrowParams
    );
}
```
