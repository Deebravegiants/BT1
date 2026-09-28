### Title
Borrowers can plant collateral with a stale price and temporarily block liquidation and bad-debt cleanup - (contracts/controller/src/positions/supply.rs)

### Summary
Medium. An account owner can add a new collateral asset while its oracle feed is already stale because `supply` admits the position without loading a valid price for it. Every subsequent risk calculation loads prices for all supply and debt assets, so the dust leg makes `liquidate`, `clean_bad_debt`, and debt-collateralized `withdraw` revert until the feed becomes fresh.

### Finding Description
`supply` requires caller authorization and loads or creates the account, but an owner or delegate is exempt from the requirement that each supplied asset already exists in the account’s supply positions. [1](#0-0) [2](#0-1) 

`process_deposit` checks entry gates, transfers the measured amount to the pool, and creates the supply position without fetching a `PriceFeed` for the supplied asset. [3](#0-2) 

The later `merge_supply_leg` path calls `refresh_supply_risk_params`, but the liquidation-parameter gate only calculates health when the new tuple favors a liquidator and the account has debt. [4](#0-3) [5](#0-4) 

For a newly created position, the stored tuple already comes from `effective_config`, so `favors_liquidator` is false and no price-bearing health calculation is required before the position is persisted. [6](#0-5) [7](#0-6) 

By contrast, `calculate_account_risk_totals` unconditionally loads markets for every supply and debt key. [8](#0-7) 

`liquidate` calls that function before checking `health_factor < 1`, so a stale price on any collateral leg aborts liquidation before the health check can run. [9](#0-8) 

### Impact Explanation
A borrower can wait until their position is unhealthy—or nearly unhealthy—and then add a dust amount of a listed collateral whose feed is stale. The added position can have negligible economic value and still poison every account-wide valuation because all supply keys are loaded, not just the collateral being seized or withdrawn. [10](#0-9) 

While the feed remains stale, liquidators cannot repay the debt and seize collateral, and `clean_bad_debt` cannot socialize residual debt. The borrower also cannot withdraw the poisoned leg while debt remains because the post-withdrawal gate evaluates the complete portfolio. [11](#0-10) 

This temporarily freezes liquidation and cleanup for the account while interest continues accruing, increasing the eventual supplier loss or bad-debt write-down. The protocol impact is greater than the dust collateral’s value because the leg disables resolution of unrelated debt and collateral markets.

### Likelihood Explanation
The attack needs an owner-controlled account with debt and a listed collateral asset whose oracle is already stale. No privileged role, leaked key, upgrade, malicious token, or third-party supply is required: the owner calls `supply` directly, and the third-party position restriction does not apply to owners or delegates. [2](#0-1) 

The condition is externally bounded because liquidation becomes available again once the price feed is fresh. That makes this a temporary-freeze and insolvency-delay issue rather than a permanent freeze, consistent with Medium severity. [12](#0-11) 

### Recommendation
Require a fresh, valid price for every newly supplied collateral leg before creating or persisting the position. In `process_deposit`, call `cache.load_markets` or otherwise fetch `cached_price(hub_asset.asset)` for each supplied `HubAssetKey`, even when the liquidation tuple does not change and no health-factor gate runs.

An alternative is to admit economically unpriced collateral only after marking it ineligible, but that would require a larger state change; validating price freshness at admission is the narrower fix.

### Proof of Concept
The repository already contains a matching integration proof in `tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs`.

1. Alice supplies 10,000 USDC and borrows 3 ETH; liquidation correctly rejects the still-healthy account. [13](#0-12) 
2. WBTC’s price is deliberately set one hour in the past. [14](#0-13) 
3. Alice calls `supply` with `0.001` WBTC. The call succeeds even though the WBTC feed is stale. [15](#0-14) 
4. USDC is then repriced downward to make the account unhealthy. [16](#0-15) 
5. Both `liquidate` and `clean_bad_debt` revert with `PRICE_FEED_STALE`. [17](#0-16) 
6. Refreshing WBTC makes the identical liquidation succeed, proving that the stale dust leg—not insufficient health or liquidity—blocked resolution. [18](#0-17)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L47-63)
```rust
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

**File:** contracts/controller/src/positions/supply.rs (L86-95)
```rust
    if account_id != 0
        && !account::is_owner_or_delegate(env, resolved_account_id, caller, &account.owner)
    {
        for (hub_asset, _) in aggregated.iter() {
            assert_with_error!(
                env,
                account.supply_positions.contains_key(hub_asset.clone()),
                GenericError::NotAuthorized
            );
        }
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

**File:** contracts/controller/src/positions/supply.rs (L283-296)
```rust
    let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, hub_asset);

    let mut position = account.get_or_create_supply_position(hub_asset, &asset_config);
    let old_scaled = position.scaled_amount;

    refresh_supply_risk_params(
        env,
        cache,
        account,
        hub_asset,
        &mut position,
        &asset_config,
        RiskRefreshScope::FullTuple,
    );
```

**File:** contracts/controller/src/positions/supply.rs (L314-323)
```rust
    cache.put_market_index(hub_asset, &outcome.market_index);
    cache.record_supply_position_update(
        events::PositionAction::Supply,
        hub_asset,
        outcome.market_index.supply_index,
        action.amount,
        &position,
    );

    update_or_remove_supply_position(account, hub_asset, &position);
```

**File:** contracts/controller/src/risk/params.rs (L76-87)
```rust
    if favors_liquidator(position, effective_config)
        && !account.debt_free()
        && !clears_min_hf(
            env,
            cache,
            account,
            hub_asset,
            position,
            effective_config.liquidation_threshold,
        )
    {
        return;
```

**File:** contracts/controller/src/risk/params.rs (L95-99)
```rust
/// Detects a lower threshold or fee, or a higher bonus, than the stored tuple.
fn favors_liquidator(position: &AccountPosition, effective_config: &AssetConfig) -> bool {
    effective_config.liquidation_threshold.raw() < position.liquidation_threshold.raw()
        || effective_config.liquidation_bonus.raw() > position.liquidation_bonus.raw()
        || effective_config.liquidation_fees.raw() < position.liquidation_fees.raw()
```

**File:** contracts/controller/src/risk/totals.rs (L157-173)
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

**File:** contracts/controller/src/risk/validation.rs (L34-40)
```rust
    let totals = risk::calculate_account_risk_totals(
        env,
        cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L13-18)
```rust
    let borrower = test_harness::ALICE;
    t.supply(borrower, "USDC", 10_000.0);
    t.borrow(borrower, "ETH", 3.0);

    let fresh = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    test_harness::assert_contract_error(fresh, errors::HEALTH_FACTOR_TOO_HIGH);
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L20-24)
```rust
    t.advance_time(5_000);
    let now = t.env.ledger().timestamp();
    let wbtc = t.resolve_asset("WBTC");
    t.mock_reflector_client()
        .set_price_at(&wbtc, &usd(60_000), &(now - 3_600));
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L26-30)
```rust
    let plant = t.try_supply(borrower, "WBTC", 0.001);
    assert!(
        plant.is_ok(),
        "supply must accept the fragile leg with a stale feed: {plant:?}"
    );
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L32-34)
```rust
    t.set_price("USDC", usd_cents(50));

    let borrower_id = t.resolve_account_id(borrower);
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L36-40)
```rust
    let liq = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    test_harness::assert_contract_error(liq, errors::PRICE_FEED_STALE);

    let clean = t.try_clean_bad_debt_by_id(borrower_id);
    test_harness::assert_contract_error(clean, errors::PRICE_FEED_STALE);
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L42-51)
```rust
    t.set_price("WBTC", usd(60_000));
    let recovered = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    assert!(
        recovered.is_ok(),
        "once WBTC is fresh, the identical liquidation must succeed: {recovered:?}"
    );
    assert!(
        t.borrow_balance(borrower, "ETH") < 3.0,
        "post-recovery liquidation must reduce the borrower's debt"
    );
```
