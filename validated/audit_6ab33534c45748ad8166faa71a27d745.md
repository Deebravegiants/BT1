### Title
Unpriceable dust collateral blocks liquidation and bad-debt cleanup - ([File: contracts/controller/src/positions/supply.rs](contracts/controller/src/positions/supply.rs))

### Summary
An indebted account owner can permissionlessly add a new collateral position while that asset’s oracle price is unavailable. The supply path does not require a fresh price for the incoming asset, while liquidation and bad-debt cleanup later price every collateral leg. A dust-sized position can therefore make the whole account temporarily unliquidatable and uncleanable until the feed recovers. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`supply` authenticates the caller, loads or creates the account, checks entry gates, transfers the measured amount, and creates the supply position without requiring a usable oracle price for the deposited asset. [1](#0-0) [4](#0-3) 

For an existing account controlled by the caller, adding a new listed asset is permitted; the existing-asset restriction applies only to third parties. [5](#0-4) 

Risk valuation then loads prices for all supply positions and dereferences each cached price while calculating collateral and health factor. [2](#0-1)  The context loads missing token prices through the price aggregator before `cached_price` returns them. [6](#0-5) [7](#0-6) 

Liquidation builds a risk-sensitive plan before moving repayment or collateral, so one missing or stale collateral price reverts the entire liquidation. [8](#0-7)  Permissionless bad-debt cleanup enters the same account valuation path, so the poisoned leg also prevents cleanup while the feed is unavailable. [9](#0-8) [10](#0-9) 

### Impact Explanation
A borrower can keep collateral and borrowed funds economically frozen by inserting a dust-sized collateral leg whose price feed is unavailable. [11](#0-10)  Once the account falls below the liquidation threshold, every liquidation attempt reverts with `PriceFeedStale` rather than seizing the account’s healthy collateral. [12](#0-11)  Bad-debt cleanup is also blocked by the same stale leg, leaving debt outstanding while collateral seizure and socialization are unavailable. [10](#0-9)  The freeze is temporary: the same liquidation succeeds once the poisoned asset’s feed becomes fresh. [13](#0-12) 

### Likelihood Explanation
The attacker only needs an owned or delegated indebted account, an unused supply-position slot, and a dust amount of a listed collateral asset whose oracle is currently stale or unavailable. [1](#0-0)  The harness demonstrates this sequence with an existing borrower adding `0.001` WBTC while its feed is stale. [14](#0-13)  A comparable account without the poisoned leg remains liquidatable under the same market crash, showing that the added leg rather than ordinary unhealthy-account processing causes the revert. [15](#0-14)  Exploitation depends on a listed feed being unavailable, but the attacker can wait for that public condition and add the leg permissionlessly. [14](#0-13) 

### Recommendation
Require a fresh, valid price for each incoming collateral asset before creating or increasing a supply position, and enforce a minimum USD value for new collateral legs so economically irrelevant positions cannot impose account-wide oracle dependencies. [4](#0-3)  Alternatively, liquidation and bad-debt cleanup could exclude supply legs below a conservative valuation floor before requiring their prices, while ensuring that excluded collateral cannot retain material value. [2](#0-1)  Regression coverage should keep both `liquidate` and `clean_bad_debt` reachable after an account adds a dust leg during an oracle outage. [16](#0-15) 

### Proof of Concept
1. Alice supplies USDC and borrows ETH, while Bob creates an otherwise identical control account. [17](#0-16) 
2. Advance time and set WBTC’s only price observation one hour in the past so that it is stale. [18](#0-17) 
3. Alice calls `supply(caller=ALICE, account_id=alice_id, spoke_id, assets=[(hub_id, WBTC), 0.001])`; the call succeeds and creates a nonzero WBTC supply position despite the stale price. [11](#0-10) 
4. Reduce USDC’s price so both accounts become unhealthy; Bob’s unpoisoned account can still be liquidated. [19](#0-18) 
5. Calling `liquidate(liquidator=LIQUIDATOR, account_id=alice_id, debt_payments=[(hub_id, ETH), 1.0], seize_mode=Transfer)` reverts with `PriceFeedStale`, and `clean_bad_debt(caller, alice_id)` reverts the same way. [20](#0-19) 
6. Updating WBTC to a fresh price makes the identical liquidation succeed and reduce Alice’s ETH debt. [13](#0-12)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L38-63)
```rust
/// Supplies collateral, creating an account when `account_id` is zero.
/// Third parties may only add to existing supply positions. Returns the account id.
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

**File:** contracts/controller/src/positions/supply.rs (L76-96)
```rust
/// Restricts third parties to existing supply positions. New accounts are
/// exempt because the caller becomes their owner.
fn require_third_party_existing_supply(
    env: &Env,
    account_id: u64,
    resolved_account_id: u64,
    caller: &Address,
    account: &Account,
    aggregated: &AggregatedPayments,
) {
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
    }
```

**File:** contracts/controller/src/positions/supply.rs (L107-134)
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
```

**File:** contracts/controller/src/risk/totals.rs (L76-97)
```rust
pub(crate) fn calculate_ltv_collateral_wad(
    env: &Env,
    cache: &mut Context,
    supply_positions: &Map<HubAssetKey, AccountPositionRaw>,
) -> Wad {
    cache.load_markets(&supply_positions.keys());

    let mut ltv = Wad::ZERO;
    for (hub_asset, position) in iter_typed_positions(supply_positions) {
        let feed = cache.cached_price(&hub_asset.asset);
        let market_index = cache.cached_market_index(&hub_asset);

        let value = position_value_floor(
            env,
            position.scaled_amount,
            market_index.supply_index,
            feed.price,
        );

        let effective_ltv = position.loan_to_value.min(position.liquidation_threshold);
        ltv = ltv.checked_add(env, effective_ltv.apply_to_wad_floor(env, value));
    }
```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L10-18)
```rust
    t.set_oracle_single_spot("WBTC");

    t.supply(ALICE, "USDC", 10_000.0);
    t.borrow(ALICE, "ETH", 3.0);
    t.supply(BOB, "USDC", 10_000.0);
    t.borrow(BOB, "ETH", 3.0);

    let pre = t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0);
    test_harness::assert_contract_error(pre, errors::HEALTH_FACTOR_TOO_HIGH);
```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L20-58)
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
```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L60-69)
```rust
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

**File:** contracts/controller/src/context.rs (L141-159)
```rust
    /// Fetches missing prices in one aggregator call; retains cached prices.
    pub(crate) fn fetch_prices(&mut self, assets: &Vec<Address>) {
        let missing = collect_uncached_keys(&self.env, assets, &self.token_prices);
        if missing.is_empty() {
            return;
        }
        let fetched = external::price_aggregator::fetch_prices(&self.env, &missing);
        for (asset, feed) in fetched.iter() {
            self.token_prices.set(asset, feed);
        }
    }

    /// Returns a previously loaded price; fails if the cache has no entry.
    pub(crate) fn cached_price(&mut self, asset: &Address) -> PriceFeed {
        let raw = self
            .token_prices
            .get(asset.clone())
            .unwrap_or_else(|| panic_with_error!(&self.env, OracleError::OracleNotConfigured));
        (&raw).into()
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L36-59)
```rust
pub(crate) fn process_liquidation(
    env: &Env,
    liquidator: &Address,
    account_id: u64,
    debt_payments: &Vec<HubPayment>,
    seize_mode: SeizeMode,
) -> u64 {
    liquidator.require_auth();
    validation::require_not_flash_loaning(env);

    let mut account = storage::get_account(env, account_id);

    let mut cache = Context::new(env);

    require_non_empty_payments(env, debt_payments);

    // Reject an unusable receiver before moving tokens.
    let mut receiver = resolve_seize_receiver(
        env, liquidator, account_id, &account, seize_mode, &mut cache,
    );

    // Share payment normalization and positivity checks with the estimate view.
    let liquidation_plan = plan::build_liquidation_plan(env, &account, debt_payments, &mut cache);
    let offered = liquidation_plan
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-214)
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
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L36-46)
```rust
    let liq = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    test_harness::assert_contract_error(liq, errors::PRICE_FEED_STALE);

    let clean = t.try_clean_bad_debt_by_id(borrower_id);
    test_harness::assert_contract_error(clean, errors::PRICE_FEED_STALE);

    t.set_price("WBTC", usd(60_000));
    let recovered = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    assert!(
        recovered.is_ok(),
        "once WBTC is fresh, the identical liquidation must succeed: {recovered:?}"
```
