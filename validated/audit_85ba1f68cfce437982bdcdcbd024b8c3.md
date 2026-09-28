### Title
Interest accrual can permanently freeze an oversized market before the borrow-index cap engages - ([File: contracts/pool/src/interest.rs]) [1](#0-0) 

### Summary
A sufficiently large borrowed position can make `scaled_debt × borrow_index` overflow `i128` before `borrow_index` reaches `MAX_BORROW_INDEX_RAY`. Because every pool operation synchronizes interest before mutating state, the first overflow makes subsequent repayments, withdrawals, liquidations, recapitalizations, and index updates fail, permanently freezing the affected market’s funds. [2](#0-1) [3](#0-2) [4](#0-3) 

### Finding Description
The controller exposes the relevant path through `supply(caller, account_id, spoke_id, assets)`, `borrow(caller, account_id, borrows, to)`, `repay(caller, account_id, payments)`, `withdraw(caller, account_id, withdrawals, to)`, and `liquidate(liquidator, account_id, debt_payments, seize_mode)`. [5](#0-4) 

All pool operations load the market through `ops::load_leg`, which calls `synced_market`, which unconditionally calls `interest::global_sync` before the operation-specific logic runs. [6](#0-5)  `global_sync` calls `accrue_chunk` for every elapsed accrual window, and `accrue_chunk` invokes `accrue_step` with the stored scaled debt and indexes. [7](#0-6) 

`accrue_step` must compute the old and new total debt with `borrowed.mul(old_borrow_index)` and `borrowed.mul(new_borrow_index)`. [3](#0-2)  The borrow-index guard caps only the index after multiplication, not the total-debt value represented by `scaled_debt × index`. [8](#0-7)  Consequently, a large enough scaled-debt position can overflow the `Ray` value while `borrow_index` is still below `MAX_BORROW_INDEX_RAY`. [9](#0-8) [10](#0-9) 

The existing regression test demonstrates the reachable state by supplying `BILLION * 10^18` units and borrowing 98% of it, then repeatedly accruing until `update_indexes` fails with `MATH_OVERFLOW`. [11](#0-10)  The same test confirms that the stored index remains below the configured cap and that both `withdraw` and `repay` subsequently fail with the same overflow. [12](#0-11) 

### Impact Explanation
This is a permanent market-level denial of service and freezing of user funds. Suppliers cannot withdraw because withdrawal first calls `ops::load_leg` and accrues interest. [13](#0-12)  Borrowers and third-party payers cannot reduce the debt because repayment also resolves the position only after `ops::load_leg` synchronizes the market. [14](#0-13)  Liquidation, bad-debt cleanup, and recapitalization cannot bypass the same synchronization boundary because they operate through pool market mutations. [6](#0-5) 

Once the state reaches the overflow condition, additional elapsed time does not recover it: the stored debt remains oversized and the next accrual repeats the overflowing multiplication. [1](#0-0)  The impact therefore matches the report’s denial-of-service bug class while producing the more severe on-chain effect of permanently frozen pool funds.

### Likelihood Explanation
The attack is permissionless and can be constructed by one address that controls enough collateral and market liquidity: first submit `supply(caller, account_id, spoke_id, [(debt_asset, principal)])`, then submit `borrow(caller, account_id, [(debt_asset, debt)], Some(receiver))`, and later trigger accrual through `update_indexes`, `repay`, `withdraw`, or `liquidate`. [15](#0-14) 

The practical barrier is substantial because the market’s supply cap, token supply, collateral requirement, utilization policy, and interest-rate model must permit a scaled-debt position large enough for the value multiplication to exceed `i128::MAX`. [16](#0-15) [9](#0-8)  The regression test had to lift market caps and use a billion-token 18-decimal market, so this is not generally reachable under conservative caps, but it is reachable by an unprivileged actor whenever configuration admits the required position size. [17](#0-16)  The appropriate severity is Medium because the impact is irreversible for the affected market, while the capital and configuration requirements constrain exploitability.

### Recommendation
Cap the represented debt value, not merely `borrow_index`. Before accepting or accruing debt, check `scaled_borrowed * new_borrow_index` with checked arithmetic and clamp or reject the new index at the largest value that keeps the represented total debt within `i128::MAX`. [8](#0-7) [3](#0-2) 

Apply the same value-headroom bound to supply-side calculations such as `supplied * old_index` and `total_supplied_value + rewards_increase`, which also perform `Ray` multiplication and checked addition during accrual. [18](#0-17)  Governance market validation and mutable caps should additionally enforce the resulting maximum safe asset amount so users cannot create a position whose future index growth can cross the representable-value boundary. [19](#0-18) 

### Proof of Concept
1. Create or select a market whose configured supply/borrow caps admit `principal = BILLION * 10^18` token units. [20](#0-19) 
2. Call controller `supply(caller, account_id, spoke_id, [(debt_asset, principal)])` to seed the market. [21](#0-20) 
3. Supply sufficient collateral and call `borrow(caller, account_id, [(debt_asset, principal * 98 / 100)], Some(receiver))`. [22](#0-21) [23](#0-22) 
4. Advance ledger time and call controller `update_indexes` for the affected `HubAssetKey`; accrual eventually returns `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`. [24](#0-23) 
5. Attempt `withdraw(caller, account_id, [(debt_asset, 1)], to)` and `repay(caller, account_id, [(debt_asset, amount)])`; both fail with `MATH_OVERFLOW` because they execute `global_sync` before repayment or withdrawal accounting. [6](#0-5) [25](#0-24)

### Citations

**File:** contracts/pool/src/interest.rs (L20-52)
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

**File:** common/src/rates/index.rs (L73-86)
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

**File:** contracts/controller/src/lib.rs (L100-158)
```rust
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
    ) -> u64 {
        positions::liquidation::process_liquidation(
            &env,
            &liquidator,
            account_id,
            &debt_payments,
            seize_mode,
        )
    }
```

**File:** common/src/rates/scaling.rs (L12-16)
```rust
/// Converts a scaled `Ray` amount to its original (unscaled) value by
/// multiplying by `index`, rounding half up.
pub fn scaled_to_original(env: &Env, scaled: Ray, index: Ray) -> Ray {
    scaled.mul(env, index)
}
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

**File:** common/src/constants/pool.rs (L18-23)
```rust
/// Ceiling the borrow index is clamped to after growth, in raw ray units.
pub const MAX_BORROW_INDEX_RAY: i128 = 1_000_000_000_000_000_000_000_000_000_000_000_000;

/// Ceiling the supply index is clamped to after growth, in raw ray units.
/// Equal to [`MAX_BORROW_INDEX_RAY`].
pub const MAX_SUPPLY_INDEX_RAY: i128 = MAX_BORROW_INDEX_RAY;
```

**File:** contracts/pool/src/ops/withdraw.rs (L53-64)
```rust
/// Runs withdraw accounting without transferring tokens.
///
/// Resolves full or partial close, burns shares, optionally withholds the
/// liquidation fee, and gates the final state before debiting cash.
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

```

**File:** contracts/pool/src/ops/repay.rs (L36-47)
```rust
/// Accrues interest, resolves the repay amount into burned debt shares and
/// overpayment, burns the shares, and credits the net repay to cash without
/// transferring the overpayment refund. Panics if a positive net repay would
/// burn zero scaled shares.
pub(crate) fn accounting(env: &Env, action: &PoolAction) -> RepayOutcome {
    let (mut cache, position) = ops::load_leg(env, action);
    let amount = action.amount;

    let (burned, overpayment) = cache.resolve_repay(amount, position);
    let net_repay = amount
        .checked_sub(overpayment)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
```

**File:** contracts/pool/src/ops/borrow.rs (L58-79)
```rust
/// Mints scaled debt for `amount` of underlying and enforces max utilization.
///
/// Requires positive amount, sufficient cash reserves, and that the draw
/// leaves the liquidation buffer intact. Panics if the scaled mint rounds to
/// zero shares.
pub(crate) fn mint_debt(env: &Env, cache: &mut Cache, position: &mut Ray, amount: i128) {
    require_positive_amount(env, amount);
    cache.require_reserves(amount);
    guards::require_liquidation_buffer(env, cache, amount);

    let minted = cache.calculate_scaled_borrow(amount);

    assert_with_error!(
        env,
        minted.raw() > 0,
        GenericError::BorrowRoundsToZeroShares
    );

    *position = position.checked_add(env, minted);
    cache.mint_debt(minted);
    guards::require_utilization_below_max(env, cache);
}
```
