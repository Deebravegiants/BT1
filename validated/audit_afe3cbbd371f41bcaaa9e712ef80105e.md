### Title
A stale price on any dust collateral leg permanently blocks liquidation and bad-debt cleanup for the whole account - (File: contracts/controller/src/risk/totals.rs)

### Summary
An unprivileged borrower can add a small listed collateral position while its oracle is stale; `supply` accepts the position, but liquidation and `clean_bad_debt` later attempt to price every supply and debt position in one batch and revert on the stale leg. [1](#0-0) [2](#0-1) 

### Finding Description
`Controller::supply` authenticates the caller, measures the token transfer, and creates the supply position without requiring the asset's price to resolve. [3](#0-2) [4](#0-3) 

`calculate_account_risk_totals` unconditionally calls `cache.load_markets` for the union of all supply and debt keys, and `Context::load_markets` requests prices for every distinct asset in one aggregator call. [5](#0-4) [6](#0-5) 

The aggregator's `prices` entry point panics if any requested key cannot resolve, and `Outcome::failure` converts a stale observation into `OracleError::PriceFeedStale`. [7](#0-6) [8](#0-7) 

`build_liquidation_plan` calls this all-position risk calculation before checking health factor, so one unpriceable dust leg aborts liquidation before any repayment or seizure can occur. [9](#0-8) 

`clean_bad_debt` has the same all-position valuation dependency through `socialize_bad_debt`, so the emergency path cannot remove the poisoned account either. [10](#0-9) 

### Impact Explanation
A borrower can temporarily freeze liquidation and permissionless bad-debt cleanup on an underwater account by keeping one listed collateral leg unpriceable. [11](#0-10) 

While the feed remains unavailable, debt and interest can continue accruing even though liquidators cannot seize the still-priceable collateral, leaving suppliers exposed to growing protocol insolvency. [9](#0-8) [12](#0-11) 

The poisoned leg also prevents the borrower from withdrawing even a different priced collateral leg because post-withdrawal solvency again evaluates the whole account. [13](#0-12) [14](#0-13) 

### Likelihood Explanation
The attacker needs only an authorized account, an existing debt position, and a positive amount of a listed collateral whose configured source is currently stale. [3](#0-2) [15](#0-14) 

The existing regression test demonstrates the full path: WBTC's timestamp is moved outside its staleness window, a `0.001` WBTC supply succeeds, both liquidation and cleanup revert with `PRICE_FEED_STALE`, and the same liquidation succeeds after the feed is refreshed. [16](#0-15) 

Likelihood is conditional on an oracle outage rather than solely attacker-controlled for a plain feed, but an Aquarius LP collateral can also become unpriceable when pool value falls below `min_pool_value_wad`, which a sufficiently large liquidity provider can induce through normal withdrawals. [17](#0-16) 

### Recommendation
Do not make account-level liquidation and cleanup depend on resolving every collateral leg in one strict batch. [18](#0-17) 

Use `quotes`/per-leg status so an unusable supply leg can be isolated or conservatively valued for the action being performed, while still allowing repayment and seizure of priceable collateral. [19](#0-18) 

Alternatively, let liquidation explicitly select priceable collateral legs and reject seizure of unpriceable legs, and provide a cleanup path that cannot be blocked solely by an oracle error on dust collateral. [20](#0-19) [21](#0-20) 

### Proof of Concept
1. Create or use an account with priced collateral and debt, then wait for one listed collateral asset's configured feed timestamp to become older than its staleness bound. [15](#0-14) 
2. Call `Controller::supply(caller, account_id, spoke_id, vec![(HubAssetKey { hub_id, asset: stale_asset }, 1)])`; the supply path accepts and persists the new leg because it does not fetch the stale price. [1](#0-0) 
3. Move the account below HF 1 through interest or a market move, then call `liquidate(liquidator, account_id, vec![(debt_key, amount)], SeizeMode::Transfer)`. [22](#0-21) 
4. The plan calls `calculate_account_risk_totals`, which calls `prices` for all account assets, and the stale leg causes the whole transaction to panic before liquidation. [9](#0-8) [7](#0-6) 
5. Call `clean_bad_debt(caller, account_id)`; it reaches the same strict valuation and reverts before `execute_bad_debt_cleanup`. [23](#0-22) 
6. This sequence is implemented by `audit_supply_setup_blocks_liquidation_via_stale_dust_leg`, which observes `PRICE_FEED_STALE` for liquidation, cleanup, and withdrawal. [24](#0-23)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L40-73)
```rust
pub(crate) fn process_supply(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    assets: &Vec<HubPayment>,
) -> u64 {
    validation::require_authorized_caller(env, caller);
    let aggregated = payments::aggregate_positive_payments(env, assets);
    let mut cache = Context::new(env);

    let (acct_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        PositionMode::Normal,
        account::AccountGuard::Supply,
        &mut cache,
    );

    require_third_party_existing_supply(env, account_id, acct_id, caller, &account, &aggregated);

    process_deposit(env, caller, &mut account, &aggregated, &mut cache);

    finalize_position_flow(
        env,
        acct_id,
        &account,
        &mut cache,
        PositionSides::Supply,
        false,
    );
    acct_id
```

**File:** contracts/controller/src/positions/supply.rs (L107-135)
```rust
    validate_position_entry_gates(
        env,
        account,
        aggregated,
        cache,
        AccountPositionType::Deposit,
    );
    let pool_addr = cache.cached_pool_address();
    let mut entries: Vec<PoolSupplyEntry> = Vec::new(env);
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
    }

    let results = pool_supply_call(env, &pool_addr, &entries);
    for_each_leg(env, &entries, &results, |entry, result| {
        merge_supply_leg(env, account, &entry.action, &result, cache);
    });
```

**File:** contracts/controller/src/positions/supply.rs (L157-168)
```rust
    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
    let _ = enforce_post_pool_solvency(env, &mut cache, &mut account);

    finalize_position_flow(
        env,
        account_id,
        &account,
        &mut cache,
        PositionSides::Supply,
        true,
    );
    paid
```

**File:** contracts/controller/src/risk/totals.rs (L157-201)
```rust
fn calculate_account_risk_totals_body(
    env: &Env,
    cache: &mut Context,
    supply_positions: &Map<HubAssetKey, AccountPositionRaw>,
    borrow_positions: &Map<HubAssetKey, DebtPositionRaw>,
) -> AccountRiskTotals {
    cache.load_markets(&portfolio_hub_keys(
        supply_positions.keys(),
        &borrow_positions.keys(),
    ));

    let mut total_collateral = Wad::ZERO;
    let mut ltv_collateral = Wad::ZERO;
    let mut weighted_collateral = Wad::ZERO;
    for (hub_asset, position) in iter_typed_positions(supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let value = position_value(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );
        let gate_value = position_value_floor(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

        total_collateral = total_collateral.checked_add(env, value);
        // A gated threshold can stay below refreshed LTV; clamp the borrow limit to it.
        let effective_ltv = position.loan_to_value.min(position.liquidation_threshold);
        ltv_collateral =
            ltv_collateral.checked_add(env, effective_ltv.apply_to_wad_floor(env, gate_value));
        weighted_collateral = weighted_collateral.checked_add(
            env,
            position
                .liquidation_threshold
                .apply_to_wad_floor(env, gate_value),
        );
    }

    let total_debt = sum_debt_usd_loaded(env, cache, borrow_positions, position_value_ceil);
```

**File:** contracts/controller/src/lib.rs (L90-102)
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
```

**File:** contracts/controller/src/lib.rs (L144-158)
```rust
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

**File:** contracts/controller/src/context.rs (L68-74)
```rust
    /// Loads missing prices by token address and missing indexes by hub-asset key.
    /// Already cached values are retained.
    pub(crate) fn load_markets(&mut self, hub_assets: &Vec<HubAssetKey>) {
        let assets = unique_hub_tokens(&self.env, hub_assets);
        self.fetch_prices(&assets);
        self.fetch_market_indexes(hub_assets);
    }
```

**File:** contracts/price-aggregator/src/lib.rs (L69-78)
```rust
    /// Resolves and returns the price feed for each of `keys`, panicking if
    /// any key fails to resolve to a usable price.
    fn prices(env: Env, keys: Vec<PriceKey>) -> Map<PriceKey, PriceFeedRaw> {
        let mut out = Map::new(&env);
        let mut session = warmed_session(&env, &keys);
        for key in keys.iter() {
            out.set(key.clone(), engine::resolve(&mut session, &key, 0));
        }
        out
    }
```

**File:** contracts/price-aggregator/src/lib.rs (L80-89)
```rust
    /// Resolves and returns the `PriceStatus` for each of `keys`, without
    /// panicking on individually unusable prices.
    fn quotes(env: Env, keys: Vec<PriceKey>) -> Map<PriceKey, PriceStatus> {
        let mut out = Map::new(&env);
        let mut session = warmed_session(&env, &keys);
        for key in keys.iter() {
            out.set(key.clone(), engine::resolve_status(&mut session, &key, 0));
        }
        out
    }
```

**File:** contracts/price-aggregator/src/engine.rs (L122-148)
```rust
    /// Returns the error that makes this outcome unusable against `oracle`, if
    /// any. Checks, in order: an error already carried on the outcome, a missing
    /// oracle, staleness, deviation, a non-positive price, and the oracle's
    /// sanity price bounds. Returns `None` when none of these apply.
    fn failure(&self, oracle: Option<&AssetOracle>) -> Option<OracleError> {
        if let Some(err) = self.err {
            return Some(err);
        }
        let Some(oracle) = oracle else {
            return Some(OracleError::OracleNotConfigured);
        };
        if self.stale {
            return Some(OracleError::PriceFeedStale);
        }
        if self.deviation {
            return Some(OracleError::UnsafePriceNotAllowed);
        }
        if self.price_wad <= 0 {
            return Some(OracleError::InvalidPrice);
        }
        if self.price_wad < oracle.min_sanity_price_wad
            || self.price_wad > oracle.max_sanity_price_wad
        {
            return Some(OracleError::SanityBoundViolated);
        }
        None
    }
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L34-44)
```rust
    let totals = risk::calculate_account_risk_totals(
        env,
        cache,
        &account.supply_positions,
        &account.borrow_positions,
    );
    assert_with_error!(
        env,
        totals.health_factor < Wad::ONE,
        CollateralError::HealthFactorTooHigh
    );
```

**File:** contracts/controller/src/positions/liquidation/plan.rs (L81-89)
```rust
    for entry in seized_collaterals.iter() {
        enforce_spoke_asset_flags(
            env,
            cache,
            account.spoke_id,
            &entry.hub_asset,
            FreezePolicy::SeizureLeg,
        );
    }
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-237)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
}

/// Admission condition for bad-debt socialization.
#[derive(Clone, Copy, PartialEq)]
enum BadDebtGate {
    /// Permissionless: insolvent *and* collateral at or below the dust threshold.
    DustCapped,
    /// Owner-only: insolvent alone, with no cap on the collateral left behind.
    InsolventOnly,
}

/// Requires open debt and the selected insolvency gate, then cleans up the account.
fn socialize_bad_debt(env: &Env, account_id: u64, gate: BadDebtGate) {
    let mut cache = Context::new(env);
    let account = storage::get_account(env, account_id);

    assert_with_error!(
        env,
        !account.borrow_positions.is_empty(),
        CollateralError::DebtPositionNotFound
    );

    let totals = risk::calculate_account_risk_totals(
        env,
        &mut cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);

    bad_debt::execute_bad_debt_cleanup(env, &mut cache, account_id, &account, &totals);
```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L20-65)
```rust
    t.advance_time(5_000);
    let now = t.env.ledger().timestamp();
    let wbtc = t.resolve_asset("WBTC");
    t.mock_reflector_client()
        .set_price_at(&wbtc, &usd(60_000), &(now - 3_600));

    let plant = t.try_supply(ALICE, "WBTC", 0.001);
    assert!(
        plant.is_ok(),
        "supply must accept the leg even though WBTC's feed is stale: {plant:?}"
    );
    t.assert_position_exists(ALICE, "WBTC", PositionType::Supply);
    assert!(
        t.supply_balance_raw(ALICE, "WBTC") > 0,
        "poisoned WBTC leg must persist with a non-zero scaled share"
    );

    t.set_price("USDC", usd_cents(50));

    assert!(
        t.can_be_liquidated(BOB),
        "twin account must be underwater so the crash — not the leg — drives HF<1"
    );
    t.liquidate(LIQUIDATOR, BOB, "ETH", 1.0);
    assert!(
        t.borrow_balance(BOB, "ETH") < 3.0,
        "twin liquidation must succeed with fresh feeds"
    );

    let alice_id = t.resolve_account_id(ALICE);

    let liq = t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0);
    test_harness::assert_contract_error(liq, errors::PRICE_FEED_STALE);

    let clean = t.try_clean_bad_debt_by_id(alice_id);
    test_harness::assert_contract_error(clean, errors::PRICE_FEED_STALE);

    let wd = t.try_withdraw(ALICE, "WBTC", 0.0001);
    test_harness::assert_contract_error(wd, errors::PRICE_FEED_STALE);

    t.set_price("WBTC", usd(60_000));
    let recovered = t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0);
    assert!(
        recovered.is_ok(),
        "once WBTC is fresh again, the identical liquidation must succeed: {recovered:?}"
    );
```

**File:** common/src/oracle/observation.rs (L53-57)
```rust
/// Returns whether `feed_ts` is older than `max_stale` seconds relative to
/// `now_secs`. Returns `false` when `feed_ts` is at or after `now_secs`.
pub fn is_stale(now_secs: u64, feed_ts: u64, max_stale: u64) -> bool {
    now_secs > feed_ts && (now_secs - feed_ts) > max_stale
}
```

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L115-122)
```rust
    let share_unit = 10i128
        .checked_pow(share_decimals)
        .ok_or(OracleError::InvalidPrice)?;
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
    }
```

**File:** contracts/controller/src/positions/liquidation/bad_debt.rs (L21-49)
```rust
    let mut entries: Vec<PoolSeizeEntry> = Vec::new(env);
    for (hub_asset, position) in iter_typed_positions(&account.supply_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Supply,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Deposit,
            position: (&position).into(),
        });
    }
    for (hub_asset, position) in iter_debt_positions(&account.borrow_positions) {
        cache.apply_spoke_exit(
            account.spoke_id,
            UsageSide::Borrow,
            &hub_asset,
            position.scaled_amount,
        );
        entries.push_back(PoolSeizeEntry {
            hub_asset,
            side: AccountPositionType::Borrow,
            position: (&position).into(),
        });
    }
    let pool_addr = cache.cached_pool_address();
    pool_seize_positions_call(env, &pool_addr, &entries);
```
