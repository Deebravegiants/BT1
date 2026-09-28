### Title
Ray-scaled market-value overflow permanently freezes a large borrowed market - ([File: common/src/rates/scaling.rs])

### Summary

**Severity: Medium.** An unprivileged account can create a sufficiently large collateralized debt position so that a later accrual computes a RAY-denominated market value outside `i128`, causing `scaled_to_original` to panic with `MathOverflow` rather than clamping or preserving the previous index. [1](#0-0) [2](#0-1) [3](#0-2) 

The overflow is reachable through the permissionless `Controller::update_indexes(caller, assets)` path, which delegates to `markets::update_indexes`, then to the pool's owner-only `update_indexes` call. [4](#0-3) [5](#0-4) 

Once the stored scaled totals and index make `scaled * index / RAY` exceed `i128::MAX`, every operation that performs `interest::global_sync` first encounters the same panic, so withdrawals, repayments, liquidations, and later index updates cannot make progress. [6](#0-5) [7](#0-6) [8](#0-7) 

### Finding Description

`scaled_to_original` computes `scaled.mul(index)`, where `Ray::mul` evaluates `scaled * index / RAY` and panics when the resulting value cannot be represented as an `i128`. [1](#0-0) [2](#0-1) [9](#0-8) 

During utilization and accrual accounting, the pool converts both `borrowed` and `supplied` scaled shares through this path using the live indexes held in `Cache`. [10](#0-9) [11](#0-10) 

The same value multiplication occurs when interest is split, because `calculate_supplier_rewards` computes the old and new total debt by multiplying `borrowed` by the old and new borrow indexes. [12](#0-11) 

`update_borrow_index` caps the index only after multiplying the old index by the interest factor, so the cap does not prevent an overflow in the separately computed market value. [13](#0-12) 

The protocol documentation explicitly recognizes this arithmetic boundary: valid caps and bounded indexes do not guarantee that accrued values fit the RAY domain, and value overflow can block repayment and withdrawal because those operations accrue first. [14](#0-13) 

### Impact Explanation

The affected market becomes permanently unable to accrue past the overflowing state because a failed transaction rolls back the index update while the next attempt evaluates an even larger accrued value. [7](#0-6) [15](#0-14) 

Supplier funds are frozen because `Controller::withdraw` reaches the pool withdrawal path, whose synchronized-market mutation accrues before resolving the withdrawal. [16](#0-15) [17](#0-16) 

Debt cannot be repaid through `Controller::repay`, even by a third party, because the repayment path also accrues before burning debt shares. [18](#0-17) [19](#0-18) 

The regression test demonstrates the concrete impact by showing a market whose next accrual returns `MathOverflow`, followed by failed withdrawal and repayment attempts. [8](#0-7) 

### Likelihood Explanation

The attack requires a market large enough for the product of scaled debt or supply and its index to exceed `i128::MAX`; the documented upper bound is roughly 170.14 billion whole-token input units, with a lower effective ceiling for accrued market value. [20](#0-19) 

The regression test uses a one-billion-token, 18-decimal market with approximately 98% utilization to reach the value ceiling before the configured borrow-index cap. [21](#0-20) 

A single unprivileged caller can establish the required state through `Controller::supply(caller, 0, spoke_id, assets)` to create an account and deposit both the debt-market liquidity and separate collateral, followed by `Controller::borrow(caller, account_id, borrows, None)` to borrow the large position. [22](#0-21) 

After ledger time advances, the same caller—or any other unprivileged authorized caller—can invoke `Controller::update_indexes(caller, [hub_asset])` to force the failing accrual. [4](#0-3) [6](#0-5) 

The requirement for very large token balances and sufficient collateral makes exploitation economically difficult, but no governance action, leaked key, malicious oracle, or privileged contract call is required after an oversized market exists. [22](#0-21) [4](#0-3) 

### Recommendation

Handle unrepresentable accrued market values explicitly instead of allowing the shared `scaled * index` conversion to panic inside global synchronization. [1](#0-0) [7](#0-6) 

The accrual path should clamp or split the value calculation before `borrowed * index` or `supplied * index` exceeds the domain, while preserving conservative rounding for borrower liabilities and supplier claims. [12](#0-11) [10](#0-9) 

Alternatively, enforce a protocol-level invariant that `scaled * index / RAY <= i128::MAX` for both totals before accepting additional supply or debt that could later violate it. [23](#0-22) [24](#0-23) 

Any recovery path should also avoid recalculating the overflowing accrued total in `repay`, `withdraw`, `liquidate`, and `clean_bad_debt`, so the market cannot be bricked by a state that only the normal accrual path cannot represent. [25](#0-24) [26](#0-25) 

### Proof of Concept

1. Use `Controller::supply` with `account_id = 0`, a valid `spoke_id`, and `assets = [(collateral_asset, collateral_amount), (debt_asset, debt_liquidity)]`; the test fixture uses `BIG18` for the debt market and a separate collateral market, with `BIG18` liquidity of `1_000_000_000 * 10^18`. [27](#0-26) [28](#0-27) 
2. Call `Controller::borrow(caller, account_id, [(BIG18_key, debt_amount)], None)`, where `debt_amount` is approximately 98% of the supplied `BIG18` liquidity and the collateral is sufficient for post-borrow solvency. [29](#0-28) [30](#0-29) 
3. Advance ledger time under sustained high utilization and repeatedly call `Controller::update_indexes(caller, [BIG18_key])` until the stored scaled debt multiplied by its accrued borrow index no longer fits `i128`. [4](#0-3) [31](#0-30) 
4. The next call fails with `GenericError::MathOverflow` before `MAX_BORROW_INDEX_RAY` can clamp the borrow index. [3](#0-2) [32](#0-31) 
5. Subsequent `withdraw` and `repay` calls revert with the same `MathOverflow` because both paths synchronize interest before resolving the user action. [33](#0-32) [34](#0-33)

### Citations

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
```

**File:** common/src/rates/scaling.rs (L35-55)
```rust
/// Converts an asset-unit `amount` to a scaled supply `Ray` using floor
/// rounding relative to `supply_index`.
pub fn calculate_scaled_supply(env: &Env, amount: i128, decimals: u32, supply_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_floor(env, supply_index)
}

/// Converts an asset-unit `amount` to a scaled supply `Ray` using ceiling
/// rounding relative to `supply_index`.
pub fn calculate_scaled_supply_ceil(
    env: &Env,
    amount: i128,
    decimals: u32,
    supply_index: Ray,
) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, supply_index)
}

/// Converts an asset-unit `amount` to a scaled borrow `Ray` using ceiling
/// rounding relative to `borrow_index`.
pub fn calculate_scaled_borrow(env: &Env, amount: i128, decimals: u32, borrow_index: Ray) -> Ray {
    Ray::from_asset(env, amount, decimals).div_ceil(env, borrow_index)
```

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** common/src/math/fp_core.rs (L104-143)
```rust
/// Computes `x * y / d` rounded half up. Requires `x >= 0`, `y >= 0`, and `d > 0`; a
/// `debug_assert` checks this in debug builds. Panics with `GenericError::DivisionByZero` if
/// `d == 0`, and with `GenericError::MathOverflow` if any other precondition is violated or if
/// the result does not fit in `i128`.
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

/// Computes `x * y / d` rounded half up. Returns `None` if `x < 0`, `y < 0`, `d <= 0`, or the
/// result does not fit in `i128`.
pub fn try_mul_div_half_up(env: &Env, x: i128, y: i128, d: i128) -> Option<i128> {
    if x < 0 || y < 0 || d <= 0 {
        return None;
    }
    let half = d / 2;

    // Fast path: the biased product fits `i128`, so the whole computation is
    // native. `x * y + half` is non-negative here, so `/` is the floor the
    // widened path would produce.
    if let Some(biased) = x
        .checked_mul(y)
        .and_then(|product| product.checked_add(half))
    {
        return Some(biased / d);
    }

    let (x256, y256, d256) = to_i256_operands(env, x, y, d);
    x256.mul(&y256)
        .add(&I256::from_i128(env, half))
        .div(&d256)
        .to_i128()
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

**File:** contracts/controller/src/lib.rs (L117-149)
```rust
    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }

    /// Repays `account_id`'s debt using measured payments from the caller.
    /// Anyone may repay; excess payments are refunded to the caller.
    fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>) {
        positions::process_repay(&env, &caller, account_id, &payments);
    }

    /// Repays debt and seizes collateral at a health-factor-based bonus.
    /// Permissionless, including self-liquidation; requires liquidator authorization.
    /// Residual bad debt is socialized only at or below the collateral dust cap.
    ///
    /// `Transfer` pays pool cash and returns `0`. `Credit(id)` moves net supply
    /// shares to a different, authorized Normal-mode account on the same spoke;
    /// `Credit(0)` creates one. Credit mode needs no free collateral liquidity
    /// and returns the receiving account id.
    fn liquidate(
        env: Env,
        liquidator: Address,
        account_id: u64,
        debt_payments: Vec<(HubAssetKey, i128)>,
        seize_mode: SeizeMode,
```

**File:** contracts/controller/src/lib.rs (L160-165)
```rust
    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
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

**File:** contracts/pool/src/lib.rs (L150-171)
```rust
    /// Burns supply shares and transfers the underlying to `receiver`.
    /// `is_liquidation` skips the max-utilization check and may withhold a
    /// protocol fee. Owner-only; `actual_amount` is gross of that fee.
    #[only_owner]
    fn withdraw(
        env: Env,
        receiver: Address,
        is_liquidation: bool,
        entries: Vec<PoolWithdrawEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::withdraw::apply(env, &receiver, is_liquidation, entry)
        })
    }

    /// Burns scaled debt up to the repay amount, credits cash with the net
    /// repay and refunds overpayment to `payer`. Owner-only.
    #[only_owner]
    fn repay(env: Env, payer: Address, actions: Vec<PoolAction>) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, actions, |env, action| {
            ops::repay::apply(env, &payer, action)
        })
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

**File:** contracts/pool/src/ops/market.rs (L65-72)
```rust
pub(crate) fn accrue(env: &Env, hub_assets: Vec<HubAssetKey>) {
    renew_instance(env);

    for hub_asset in hub_assets.iter() {
        let mut cache = Cache::load(env, &hub_asset);
        interest::global_sync(env, &mut cache);
        events::emit_market_state(env, cache.commit());
    }
```

**File:** contracts/pool/src/interest.rs (L20-32)
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

**File:** contracts/pool/src/cache/scale.rs (L19-26)
```rust
    pub(crate) fn calculate_utilization(&self) -> Ray {
        if self.supplied == Ray::ZERO {
            return Ray::ZERO;
        }
        let total_borrowed = scaled_to_original(&self.env, self.borrowed, self.borrow_index);
        let total_supplied = scaled_to_original(&self.env, self.supplied, self.supply_index);

        utilization(&self.env, total_borrowed, total_supplied)
```

**File:** contracts/pool/src/cache/mod.rs (L30-41)
```rust
pub(crate) struct Cache {
    env: Env,
    hub_asset: HubAssetKey,
    params: MarketParams,
    last_timestamp: u64,
    current_timestamp: u64,
    supplied: Ray,
    borrowed: Ray,
    revenue: Ray,
    borrow_index: Ray,
    supply_index: Ray,
    cash: i128,
```

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

**File:** docs/reference/formulas.md (L423-437)
```markdown
| Bound | Consequence |
|---|---|
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
