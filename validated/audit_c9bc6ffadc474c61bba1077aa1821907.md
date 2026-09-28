### Title
Unbounded RAY index multiplication permanently freezes a high-utilization market - (File: common/src/rates/simulate.rs)

### Summary
Interest accrual converts aggregate scaled debt and supply to original RAY values before calculating utilization, and the `i128` result can overflow before the configured borrow-index ceiling is reached. Since every pool mutation synchronizes the market before acting, this permanently prevents repayment, withdrawal, liquidation, and further index updates for that market. [1](#0-0) [2](#0-1) 

### Finding Description
`Controller::supply(caller, account_id, spoke_id, assets)` lets an unprivileged address create and fund accounts, while `Controller::borrow(caller, account_id, borrows, to)` lets that account owner borrow up to the configured risk limits. [3](#0-2)  The controller forwards the borrow legs to `LiquidityPool::borrow(receiver, entries)`, which mints scaled debt and debits cash. [4](#0-3) [5](#0-4) 

On every subsequent operation leg, `ops::load_leg` calls `synced_market`, which loads state and invokes `interest::global_sync`. [2](#0-1)  `global_sync` passes the stored scaled `borrowed`, scaled `supplied`, and both indexes into `accrue_step`. [6](#0-5)  `accrue_step` first computes `borrowed * borrow_index` and `supplied * supply_index` through `scaled_to_original`, and `Ray::mul` panics with `MathOverflow` when the product does not fit in `i128`. [7](#0-6) [8](#0-7) 

The overflow is not confined to a view or an optional trigger: `repay`, `withdraw`, `borrow`, `supply`, liquidation withdrawal, and `update_indexes` all require the same accrual-first load, so none can complete once the multiplication exceeds the `i128` domain. [9](#0-8) [10](#0-9) [11](#0-10) 

### Impact Explanation
All supplier funds and all borrower collateral exposed through the affected market become permanently frozen. Borrowers cannot repay, suppliers cannot withdraw, liquidators cannot clear unhealthy positions, and the owner-only pool operations that must first accrue the market cannot recover it through `update_indexes` or a rate-model change. [2](#0-1) [12](#0-11) 

The repository’s own regression coverage demonstrates the reachable end state: after sustained high utilization, `update_indexes`, withdrawal, and repayment all fail with `MATH_OVERFLOW`, while the stored borrow index remains below `MAX_BORROW_INDEX_RAY`. [13](#0-12) 

### Likelihood Explanation
The attacker path is permissionless but capital-intensive: supply a very large amount of the debt asset, supply sufficient collateral, and borrow enough of the market to keep utilization on the steep part of its configured rate curve. `Controller::supply` and `Controller::borrow` are externally reachable and require no administrative role. [3](#0-2) 

The attack requires a market whose admitted caps, liquidity, collateral value, and utilization configuration permit the scaled balances to reach the arithmetic ceiling, then enough ledger time for index growth. Once that state exists, any unprivileged caller can trigger the permanent freeze with `Controller::update_indexes(caller, vec![hub_asset])`, because the pool implementation unconditionally runs `global_sync` before committing the market. [11](#0-10)  The demonstrated test fixture uses a billion-unit 18-decimal market at 98% utilization, so likelihood is constrained by asset supply and configured caps rather than by permissions. [14](#0-13) 

### Recommendation
Prevent aggregate `scaled * index` values from crossing the representable domain before time accrues. At minimum, perform the accrual valuation in a wider type and define a deterministic saturation or bounded-accrual path, while ensuring position-level exits remain computable after the bound is reached. Entry validation should also reject a scaled balance that cannot be safely represented at the configured index ceiling, rather than relying on future `MathOverflow` failures. [1](#0-0) [15](#0-14) 

A recovery path should also be added or preserved so that repayment and withdrawal do not require a valuation that has already crossed the arithmetic boundary; the current common `synced_market` precondition makes every remediation path hit the same panic first. [2](#0-1) 

### Proof of Concept
1. Using one unprivileged address, call `Controller::supply(caller, 0, spoke_id, vec![(debt_hub_asset, principal)])` to create a liquidity account, then call `Controller::supply(caller, 0, spoke_id, vec![(collateral_hub_asset, collateral)])` to create a borrowing account.
2. Call `Controller::borrow(caller, collateral_account_id, vec![(debt_hub_asset, debt)], Some(caller))`, where `debt` keeps the debt market at sustained high utilization and satisfies the collateral risk check. [16](#0-15) 
3. Advance ledger time while the position remains outstanding.
4. Call `Controller::update_indexes(caller, vec![debt_hub_asset])`.
5. The pool reaches `accrue_step`, evaluates `scaled_to_original(borrowed, borrow_index)` or `scaled_to_original(supplied, supply_index)`, and panics with `GenericError::MathOverflow` before committing a new `last_timestamp`. [7](#0-6) 
6. Subsequent `Controller::repay`, `Controller::withdraw`, `Controller::liquidate`, and `Controller::update_indexes` calls repeat the same accrual-first path and fail identically. [2](#0-1)

### Citations

**File:** common/src/rates/simulate.rs (L51-69)
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

**File:** contracts/controller/src/external/pool.rs (L30-38)
```rust
/// Mints scaled debt and transfers borrowed assets to `receiver`.
pub(crate) fn pool_borrow_call(
    env: &Env,
    pool_addr: &Address,
    receiver: &Address,
    entries: &Vec<PoolBorrowEntry>,
) -> Vec<PoolPositionMutation> {
    LiquidityPoolClient::new(env, pool_addr).borrow(receiver, entries)
}
```

**File:** contracts/pool/src/ops/borrow.rs (L42-79)
```rust
pub(crate) fn accounting(env: &Env, entry: &PoolBorrowEntry) -> BorrowOutcome {
    let (mut cache, mut position) = ops::load_leg(env, &entry.action);
    let amount = entry.action.amount;

    mint_debt(env, &mut cache, &mut position, amount);
    cache.debit_cash(amount);

    let snapshot = cache.commit();
    let mutation = cache.position_mutation(position, amount);
    BorrowOutcome {
        cache,
        mutation,
        snapshot,
    }
}

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

**File:** common/src/math/fp.rs (L49-52)
```rust
    /// Multiplies two ray values, rounding the result half up.
    pub fn mul(self, env: &Env, other: Ray) -> Ray {
        Ray(fp_core::mul_div_half_up(env, self.0, other.0, RAY))
    }
```

**File:** contracts/pool/src/ops/repay.rs (L40-57)
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
```

**File:** contracts/pool/src/ops/withdraw.rs (L57-81)
```rust
pub(crate) fn accounting(
    env: &Env,
    is_liquidation: bool,
    entry: &PoolWithdrawEntry,
) -> WithdrawOutcome {
    require_nonneg_amount(env, entry.protocol_fee);
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
    let net_transfer = withhold_liquidation_fee(
        env,
        &mut cache,
        gross_amount,
        is_liquidation,
        entry.protocol_fee,
    );

    // A footprint-only close must not add a utilization gate to same-market
    // net settlement: it burns no shares and moves no cash.
    let empty_close = position.raw() == 0 && entry.action.amount == i128::MAX;
    gate_and_debit(env, &mut cache, net_transfer, is_liquidation || empty_close);

    let snapshot = cache.commit();
```

**File:** contracts/pool/src/ops/market.rs (L50-72)
```rust
/// Accrues interest under the old model, commits it, then replaces the interest
/// and flash-loan parameters and validates them against the stored decimals.
pub(crate) fn replace_rate_model(env: &Env, hub_asset: HubAssetKey, model: InterestRateModel) {
    ops::renewed_market(env, &hub_asset).commit();

    let params = storage::write_rate_model(env, &hub_asset, &model);
    params.verify(env);
    events::emit_market_params(env, hub_asset.hub_id, hub_asset.asset, params);
}

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

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L321-333)
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
```

**File:** tests/test-harness/tests/controller/large_positions_and_long_horizons.rs (L335-356)
```rust
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

**File:** contracts/controller/src/positions/debt.rs (L33-65)
```rust
pub(crate) fn process_borrow(
    env: &Env,
    caller: &Address,
    account_id: u64,
    borrows: &Vec<HubPayment>,
    to: Option<Address>,
) {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_positive_payments(env, borrows);

    validate_position_entry_gates(
        env,
        &account,
        &aggregated,
        &mut cache,
        AccountPositionType::Borrow,
    );
    settle_borrow(env, &mut account, &recipient, &aggregated, &mut cache);

    let restamped = enforce_post_pool_solvency(env, &mut cache, &mut account);
    let sides = if restamped {
        PositionSides::Both
    } else {
        PositionSides::Debt
    };
    finalize_position_flow(env, account_id, &account, &mut cache, sides, false);
```
