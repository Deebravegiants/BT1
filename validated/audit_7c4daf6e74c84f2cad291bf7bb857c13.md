### Title
Unpriceable dust collateral blocks liquidation and bad-debt cleanup, shielding borrower defaults - ([File: contracts/controller/src/risk/totals.rs](contracts/controller/src/risk/totals.rs))

### Summary
A borrower can add a minimal supply position in a listed asset while that asset’s oracle is stale or otherwise unusable, because `supply` performs listing, flag, and measured-deposit checks without resolving the asset price. The deposited leg then becomes part of `account.supply_positions`, while `liquidate` and `clean_bad_debt` both evaluate every supply and debt leg through `calculate_account_risk_totals`, which bulk-loads all corresponding prices. One failed price causes the entire operation to revert, temporarily or permanently blocking liquidation and cleanup of an otherwise eligible account. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`process_deposit` iterates attacker-selected `assets`, requires only that each `(hub_id, asset)` is listed, transfers the measured amount to the pool, and creates or updates the supply position. It does not call `cached_price`, `fetch_prices`, or another strict price-validation path for the new leg. [1](#0-0) 

The vulnerable path is reachable through the public `supply(caller, account_id, spoke_id, assets)` flow implemented by `process_supply`, which authorizes the caller and then invokes `process_deposit`. For the borrower’s own account, including a newly created account, there is no requirement that the collateral be valuable or priceable at deposit time. [4](#0-3) 

`liquidate(liquidator, account_id, debt_payments, seize_mode)` calls `build_liquidation_plan` before moving repayment tokens. [5](#0-4) [6](#0-5)  That planner calls `calculate_account_risk_totals` over the complete supply and borrow maps, not merely the supplied collateral selected by the liquidator. [7](#0-6) 

`calculate_account_risk_totals_body` calls `cache.load_markets` on the concatenated supply and borrow keys, then iterates every supply position and reads `cache.cached_price(&hub_asset.asset)`. [2](#0-1)  `load_markets` converts those keys to unique token addresses and calls `fetch_prices`, which forwards every required token to the strict `PriceAggregator.prices` endpoint. [8](#0-7) [9](#0-8)  The aggregator resolves each key through `engine::resolve`, and `force` panics on staleness, unsafe deviation, invalid price, missing oracle, or sanity-bound failure. [10](#0-9) [11](#0-10) [12](#0-11) 

The same all-position strict pricing is repeated by permissionless `clean_bad_debt(caller, account_id)`, which calls `socialize_bad_debt`, computes `calculate_account_risk_totals`, and only then decides whether debt exceeds collateral and whether the collateral is below the dust cap. [13](#0-12) [14](#0-13)  Therefore even an insolvent account that should be cleaned up cannot be processed while one dust collateral leg has an unusable price.

### Impact Explanation
This enables a borrower to freeze liquidation and bad-debt cleanup by spending only enough of a listed asset to create a nonzero collateral position. Once the account becomes underwater, liquidators cannot repay its debt through either `SeizeMode::Transfer` or `SeizeMode::Credit`, because both modes share `build_liquidation_plan` and its all-position risk calculation. If the account later becomes insolvent, permissionless `clean_bad_debt` also fails before the socialization gate because it needs prices for every position. [7](#0-6) [15](#0-14) 

The direct consequence is temporary freezing of liquidation and cleanup for as long as the poisoned asset’s price remains unavailable. If that feed never becomes usable, the account’s debt and remaining collateral remain locked in the account and the bad debt cannot be socialized through the permissionless path. During the delay, interest continues accruing and collateral values can deteriorate further, converting an otherwise recoverable underwater position into protocol insolvency borne by suppliers. The borrower has a concrete economic incentive to deploy this shield before or while its collateral declines. [16](#0-15) [17](#0-16) 

### Likelihood Explanation
The attack requires only a listed asset whose strict price is currently unavailable, plus a minimal supply deposit by the borrower. No privileged role, leaked key, malicious token, malicious venue, or governance action is required. The borrower controls both the timing and the selected `HubAssetKey` passed to `supply`, while liquidators cannot omit that leg because the planner always prices the full position set. [4](#0-3) [18](#0-17) [19](#0-18) 

The repository’s own regression test demonstrates the reachable sequence: configure WBTC with a single spot feed, let that feed become stale, successfully `supply` a WBTC dust leg, make the account underwater through the other collateral, and observe both `liquidate` and `clean_bad_debt` fail with `PRICE_FEED_STALE`; refreshing WBTC makes the identical liquidation succeed. [20](#0-19) [21](#0-20) 

### Recommendation
Do not let an arbitrarily supplied, economically insignificant collateral leg poison the entire risk calculation. Possible remediations include:

- Require a strict, usable price when creating a new supply position, while still allowing top-ups to an existing position under the existing third-party rules.
- Alternatively, value an unpriceable dust leg as zero for liquidation and cleanup, with a conservative bound or explicit exclusion rule that cannot hide material collateral.
- Add a liquidation/cleanup fallback that prices only economically material collateral or supports bounded “unpriced collateral treated as zero” semantics.
- Apply the same treatment consistently to liquidation estimates, `liquidate`, `clean_bad_debt`, withdrawal solvency checks, and any strategy path that recalculates account risk.
- Add regression coverage proving that a stale minimal collateral leg cannot prevent liquidation or dust-gated bad-debt cleanup after it was admitted by `supply`.

### Proof of Concept
1. Configure a listed collateral asset, for example WBTC, with a single-source oracle so there is no second leg that can keep the aggregate usable.
2. Attacker supplies substantial USDC and borrows ETH, leaving a healthy account.
3. Attacker lets WBTC’s observation become stale, or selects an asset whose configured strict source is otherwise unusable.
4. Attacker calls `supply(attacker, account_id, spoke_id, [(HubAssetKey { hub_id, asset: WBTC }, dust_amount)])`. `process_supply` authenticates the attacker, `process_deposit` checks the listing and transfers the measured WBTC amount to the pool, and a nonzero WBTC supply position is created without resolving its price. [1](#0-0) 
5. USDC subsequently falls enough that the account’s health factor is below one.
6. Any liquidator calls `liquidate(liquidator, account_id, [(HubAssetKey { hub_id, asset: ETH }, repay_amount)], SeizeMode::Transfer)` or `SeizeMode::Credit(_)`. Before repayment, `build_liquidation_plan` calls `calculate_account_risk_totals`; that loads the WBTC price together with all other supply and debt prices. [7](#0-6) [2](#0-1) 
7. `Context::fetch_prices` calls the aggregator’s strict `prices` method for every token. WBTC resolution returns or panics with `PriceFeedStale`, causing the entire liquidation transaction to revert before debt repayment or collateral seizure. [9](#0-8) [12](#0-11) 
8. If the account becomes insolvent, any caller invoking `clean_bad_debt(caller, account_id)` reaches the same `calculate_account_risk_totals` call before the dust-cap and insolvency checks, so cleanup also reverts on the poisoned WBTC leg. [22](#0-21) 
9. The account cannot be liquidated or cleaned while the leg’s price remains unavailable. Once the feed becomes fresh, the identical liquidation succeeds, demonstrating that the dust leg—not insufficient collateral, debt selection, seize mode, or liquidation eligibility—is the blocker. [23](#0-22)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L40-63)
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
```

**File:** contracts/controller/src/positions/supply.rs (L107-128)
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
```

**File:** contracts/controller/src/risk/totals.rs (L27-37)
```rust
    let mut assets = Vec::new(env);
    for key in account.supply_positions.keys().iter() {
        push_unique_address(&mut assets, key.asset);
    }
    for key in account.borrow_positions.keys().iter() {
        push_unique_address(&mut assets, key.asset);
    }
    for asset in extras.iter() {
        push_unique_address(&mut assets, asset.clone());
    }
    assets
```

**File:** contracts/controller/src/risk/totals.rs (L163-180)
```rust
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
```

**File:** contracts/controller/src/risk/totals.rs (L201-207)
```rust
    let total_debt = sum_debt_usd_loaded(env, cache, borrow_positions, position_value_ceil);

    let health_factor = if total_debt == Wad::ZERO {
        Wad::from(i128::MAX)
    } else {
        weighted_collateral.div_floor_saturating(env, total_debt)
    };
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L52-66)
```rust
    // Reject an unusable receiver before moving tokens.
    let mut receiver = resolve_seize_receiver(
        env, liquidator, account_id, &account, seize_mode, &mut cache,
    );

    // Share payment normalization and positivity checks with the estimate view.
    let liquidation_plan = plan::build_liquidation_plan(env, &account, debt_payments, &mut cache);
    let offered = liquidation_plan
        .repayment
        .full_close
        .then(|| payments::aggregate_positive_payments(env, debt_payments));

    let result = liquidation_plan.into_result();

    require_non_empty_payments(env, &result.repaid);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L211-237)
```rust
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

**File:** contracts/controller/src/lib.rs (L144-150)
```rust
    fn liquidate(
        env: Env,
        liquidator: Address,
        account_id: u64,
        debt_payments: Vec<(HubAssetKey, i128)>,
        seize_mode: SeizeMode,
    ) -> u64 {
```

**File:** contracts/controller/src/lib.rs (L160-164)
```rust
    /// Socializes insolvent debt into the supply index and removes the account
    /// when remaining collateral is at or below the dust cap. Permissionless;
    /// requires caller authorization.
    fn clean_bad_debt(env: Env, caller: Address, account_id: u64) {
        positions::liquidation::process_clean_bad_debt(&env, &caller, account_id);
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

**File:** contracts/controller/src/context.rs (L70-74)
```rust
    pub(crate) fn load_markets(&mut self, hub_assets: &Vec<HubAssetKey>) {
        let assets = unique_hub_tokens(&self.env, hub_assets);
        self.fetch_prices(&assets);
        self.fetch_market_indexes(hub_assets);
    }
```

**File:** contracts/controller/src/external/price_aggregator.rs (L18-25)
```rust
pub(crate) fn fetch_prices(env: &Env, assets: &Vec<Address>) -> Map<Address, PriceFeedRaw> {
    let aggregator = storage::get_price_aggregator(env);
    let keyed = PriceAggregatorClient::new(env, &aggregator).prices(&token_keys(env, assets));
    let mut out = Map::new(env);
    for asset in assets.iter() {
        match keyed.get(PriceKey::Token(asset.clone())) {
            Some(feed) => out.set(asset, feed),
            None => panic_with_error!(env, OracleError::OracleNotConfigured),
```

**File:** contracts/price-aggregator/src/lib.rs (L69-77)
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
```

**File:** contracts/price-aggregator/src/engine.rs (L122-147)
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
```

**File:** contracts/price-aggregator/src/engine.rs (L181-188)
```rust
pub(crate) fn force(env: &Env, outcome: &Outcome, oracle: Option<&AssetOracle>) -> PriceFeedRaw {
    if let Some(err) = outcome.failure(oracle) {
        panic_with_error!(env, err);
    }
    let Some(oracle) = oracle else {
        panic_with_error!(env, OracleError::OracleNotConfigured)
    };
    outcome.to_feed(oracle.asset_decimals)
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

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L20-31)
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
```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L49-69)
```rust
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
    assert!(
        t.borrow_balance(ALICE, "ETH") < 3.0,
        "post-recovery liquidation must reduce ALICE's debt"
    );
```
