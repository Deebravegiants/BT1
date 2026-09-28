### Title
Unbounded debt valuation overflows `i128` before the borrow-index cap and permanently freezes a market - (`common/src/rates/index.rs`)

### Summary
Market debt is stored as scaled `Ray` shares and every accrual converts those shares back into a RAY-denominated debt value by computing `borrowed * borrow_index / RAY`. [1](#0-0)  The product is calculated in `i128`/`I256` but the quotient must fit `i128`; once `borrowed * borrow_index / RAY > i128::MAX`, `calculate_supplier_rewards` panics before the protocol’s `MAX_BORROW_INDEX_RAY` cap can stop growth. [2](#0-1) [3](#0-2)  Every state-changing money path synchronizes interest before doing its operation, so the same panic blocks repayments, withdrawals, borrowing, liquidation, bad-debt processing, and revenue claims for that market. [4](#0-3) 

### Finding Description
`accrue_step` calls `scaled_to_original(borrowed, borrow_index)` to compute utilization, updates `borrow_index`, and then calls `calculate_supplier_rewards`, which multiplies the unchanged scaled-debt amount by the new index. [5](#0-4)  `update_borrow_index` only clamps the index after the multiplication, and `calculate_supplier_rewards` separately multiplies the debt by both the old and new indexes without a representable-value bound. [6](#0-5) [7](#0-6)  The multiplication can therefore overflow even though `new_borrow_index` remains below `MAX_BORROW_INDEX_RAY`; the index bound is an index bound, not a bound on `borrowed * index`. [3](#0-2) [8](#0-7) 

The vulnerable flow is externally reachable through `Controller::update_indexes(caller, assets)`, which is permissionless and only requires caller authorization. [9](#0-8)  Supply, withdraw, repay, borrow, and other pool legs call `load_leg`, which invokes `synced_market` and `interest::global_sync` before the requested operation. [4](#0-3)  `global_sync` applies `accrue_step` to every elapsed chunk, so once the next chunk would make the debt value unrepresentable, all operations that first accrue that market revert with `MathOverflow`. [10](#0-9) 

This is not merely an edge case in an invalid entry: the repository’s own extreme-position test constructs an 18-decimal market, deposits `BILLION * 10^18` base units, borrows 98% of it, and advances time until `update_indexes` returns `MathOverflow`. [11](#0-10)  The test confirms the borrow index is still below `MAX_BORROW_INDEX_RAY`, proving that the configured index ceiling does not prevent the overflow. [12](#0-11) 

### Impact Explanation
The affected market becomes permanently unable to accrue and therefore unable to operate its normal money paths. [13](#0-12) [4](#0-3)  Suppliers cannot withdraw because `withdraw` calls `load_leg` and accrues before resolving or paying the withdrawal. [14](#0-13)  Borrowers cannot repay because `repay` similarly calls `load_leg` before burning debt shares or crediting cash. [15](#0-14)  The repository’s regression test explicitly verifies that both withdrawal and repayment revert with `MathOverflow` after the cliff is reached. [16](#0-15) 

Because liquidation paths also use the pool’s synchronized position operations, underwater accounts cannot be liquidated normally after the accrual overflow, which can leave the market permanently insolvent as oracle prices continue changing externally. [4](#0-3) [17](#0-16)  This satisfies permanent freezing of user funds and can further produce protocol insolvency.

### Likelihood Explanation
No privileged role is required to trigger the final overflow: any caller can submit `update_indexes(caller, [hub_asset])` after enough time has elapsed. [9](#0-8)  The preconditions are an exceptionally large RAY-scaled debt balance and enough accrued index growth for the debt value to exceed `i128::MAX`; the repository test reaches that condition with a one-billion-whole-token 18-decimal market at approximately 98% utilization. [11](#0-10) 

The attack or failure can emerge organically in a sufficiently large, high-utilization market rather than requiring a malformed parameter or leaked key. [13](#0-12)  Its likelihood is limited by the large token amount and sustained borrow utilization needed before the representable debt ceiling is reached, so it is less likely in ordinary-sized markets but catastrophic in markets admitted with very large caps and high-decimal assets. [18](#0-17) [11](#0-10) 

### Recommendation
Treat the RAY debt value `borrowed * borrow_index / RAY` as the quantity that must remain representable, not merely the index itself. [7](#0-6) 

At market/listing or cap-update time, enforce:

```text
borrow_cap_scaled * MAX_BORROW_INDEX_RAY / RAY <= i128::MAX
```

or equivalently derive a market-specific maximum borrow index:

```text
max_safe_index = floor(i128::MAX * RAY / borrow_cap_scaled)
```

and require `max_safe_index >= MAX_BORROW_INDEX_RAY` before admitting that cap. [18](#0-17) [3](#0-2)  Borrow entry should then reject any scaled-debt total that would violate the market’s safe representable-value bound. [19](#0-18) 

For existing markets already near the limit, add a recovery path that can cap or socialize the index/value transition without panicking before normal exits are blocked; simply widening the intermediate product to `I256` is insufficient because the resulting debt value itself does not fit `i128`. [8](#0-7) [20](#0-19) 

### Proof of Concept
1. Configure or use a listed 18-decimal market with caps large enough to accept approximately `1_000_000_000 * 10^18` base units, matching the repository’s `BIG18` scenario. [21](#0-20) 
2. An unprivileged supplier calls `supply` for `principal = 1_000_000_000 * 10^18`, creating approximately `9.9e35` scaled supply shares at the initial index. [22](#0-21) [23](#0-22) 
3. An unprivileged borrower with sufficient collateral calls `borrow` for approximately `0.98 * principal`, creating scaled debt around `9.8e35`. [24](#0-23) 
4. Let time advance while utilization stays high, then call permissionless `update_indexes(caller, [BIG18_hub_asset])`. [9](#0-8) 
5. `global_sync` invokes `accrue_step`, and `calculate_supplier_rewards` evaluates `borrowed * new_borrow_index / RAY`; at roughly a 170x index the quotient exceeds `i128::MAX` and panics with `MathOverflow`. [25](#0-24) [8](#0-7) 
6. The stored `borrow_index` remains below `MAX_BORROW_INDEX_RAY`, so the index cap has not protected the market. [12](#0-11) 
7. Subsequent `withdraw` and `repay` calls both enter `load_leg`, attempt the same accrual first, and revert with `MathOverflow`, freezing supplier cash and preventing debt closure. [4](#0-3) [16](#0-15)

### Citations

**File:** common/src/rates/simulate.rs (L51-71)
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

    let new_supply_index = update_supply_index(env, supplied, supply_index, supplier_rewards);
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

**File:** contracts/pool/src/ops/mod.rs (L29-47)
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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-348)
```rust
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L349-353)
```rust
    let last = book(&t, "BIG18");
    assert!(
        last.borrow_index < MAX_BORROW_INDEX_RAY,
        "the index cap did not engage before the value overflow"
    );
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L354-356)
```rust
    // The market is frozen: exits and repayments accrue first and hit the same panic.
    assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
    assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-65)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
```

**File:** contracts/pool/src/ops/repay.rs (L40-59)
```rust
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        net_repay == 0 || burned.raw() > 0,
        GenericError::RepayRoundsToZeroShares
    );

    let position = position.checked_sub(env, burned);
    cache.burn_debt(burned);

    cache.credit_cash(net_repay);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/lib.rs (L224-230)
```rust
    /// Seizes positions during liquidation or bad-debt cleanup. Borrow-side
    /// entries socialize bad debt onto the supply index and burn the debt;
    /// deposit-side entries reclassify supply shares as protocol revenue.
    /// Restricted to the owner.
    #[only_owner]
    fn seize_positions(env: Env, entries: Vec<PoolSeizeEntry>) {
        ops::run_batch(&env, entries, |e, entry| ((), ops::seize::apply(e, entry)));
```

**File:** common/src/rates/scaling.rs (L18-33)
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
}
```

**File:** contracts/pool/src/cache/scale.rs (L39-47)
```rust
    /// Converts an asset borrow into scaled debt shares (ceil at the borrow index).
    pub(crate) fn calculate_scaled_borrow(&self, amount: i128) -> Ray {
        calculate_scaled_borrow(
            &self.env,
            amount,
            self.params.asset_decimals,
            self.borrow_index,
        )
    }
```

**File:** common/src/math/fp_core.rs (L108-143)
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

**File:** contracts/pool/src/ops/supply.rs (L19-41)
```rust
pub(crate) fn apply(
    env: &Env,
    entry: &PoolSupplyEntry,
) -> (PoolPositionMutation, MarketStateSnapshot) {
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    guards::require_backed_market(env, &cache);

    let minted = cache.calculate_scaled_supply(amount);
    assert_with_error!(
        env,
        amount == 0 || minted.raw() > 0,
        GenericError::SupplyRoundsToZeroShares
    );

    position = position.checked_add(env, minted);
    cache.mint_supply(minted);

    cache.credit_cash(amount);

    let snapshot = cache.commit();
    (cache.position_mutation(position, amount), snapshot)
```
