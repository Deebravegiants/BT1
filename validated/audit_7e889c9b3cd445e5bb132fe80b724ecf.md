### Title
Unpriceable dust collateral lets a borrower temporarily block liquidation and bad-debt cleanup - (File: contracts/controller/src/risk/totals.rs)

### Summary
An indebted account can add a minimal amount of any listed collateral, including an Aquarius LP token, because `supply` performs token and position accounting without first requiring that collateral's price to be usable. Subsequent liquidation, withdrawal while debt remains, permissionless `clean_bad_debt`, and forced socialization all value every supply leg through strict oracle reads, so one failing collateral price aborts the entire operation. If the borrower or an aligned liquidity provider can push the referenced Aquarius pool below its configured `min_pool_value_wad`, the dust LP leg becomes a temporary liquidation shield while interest accrues or collateral prices deteriorate.

### Finding Description
`process_supply` authenticates the caller, resolves the account, applies third-party restrictions, and calls `process_deposit`; the deposit path checks listing and position-entry gates, transfers the measured tokens, and merges the returned pool shares, but it does not require a currently valid oracle price for the supplied collateral. [1](#0-0) [2](#0-1) 

Once such a position exists, `calculate_account_risk_totals_body` loads all market data and then calls `cache.cached_price` for every supply position, regardless of how economically insignificant that position is. [3](#0-2)  `liquidate` builds its plan from those account positions, and `clean_bad_debt` computes the same risk totals before applying either cleanup gate. [4](#0-3) [5](#0-4) 

For an Aquarius LP leg, the price provider derives the share price from live pool reserves and rejects the read when the resulting total pool value is below `min_pool_value_wad`. [6](#0-5)  The existing regression test demonstrates the pattern: an already indebted borrower supplies `0.001` WBTC while that feed is stale, after which both liquidation and `clean_bad_debt` revert with `PriceFeedStale`; refreshing the feed makes the same liquidation succeed. [7](#0-6) 

### Impact Explanation
This is a temporary freeze of liquidation and debt-cleanup paths for the targeted account. The borrower already controls the account and can add the shielding collateral through `supply`; if the selected collateral is an Aquarius LP share whose pool the borrower or another liquidity provider can drain below the configured value floor, the borrower can also trigger the outage without privileged lending access.

During the outage, liquidators cannot repay and seize collateral, `clean_bad_debt` cannot socialize eligible debt, and even forced socialization still needs every required price. Debt continues accruing while timely liquidation is blocked, so the delay can turn a recoverable position into a larger supplier loss or protocol insolvency. The shield is temporary rather than permanent: restoration of a valid feed or sufficient pool liquidity unblocks the affected paths, and the borrower can remove the leg only subject to the same priced withdrawal gates.

### Likelihood Explanation
Likelihood is market- and configuration-dependent. The borrower must already have an indebted account, must be able to acquire at least a dust amount of a listed collateral whose price can be made invalid, and must benefit from delaying liquidation. Aquarius LP collateral provides the clearest trigger when a single liquidity provider can withdraw enough value to cross `min_pool_value_wad`; ordinary feed staleness can produce the same temporary shield without requiring manipulation.

The position size does not have to be economically meaningful because the controller requires a usable price for every collateral leg, not just the legs being seized. The attacker's cost is therefore bounded by the dust collateral and any cost of causing the external price outage, while the benefit is control over liquidation timing for the full debt position.

### Recommendation
Do not let an irrelevant or dust-valued collateral leg make the entire account unpriceable. Possible mitigations include:

- Require a valid price for each new supply asset before opening the position, while still allowing top-ups of already-held assets or explicitly accepting that top-ups can refresh the same risk.
- Add a liquidation/cleanup path that can ignore or seize collateral legs below a tightly defined value floor without making an unpriceable leg contribute zero to collateral.
- For Aquarius LP sources, avoid treating transient `InsufficientAquariusLiquidity` as a reason to block all liquidation, or provide a governance/timelocked fallback valuation and emergency delisting path.
- At minimum, enforce a minimum first-supply amount for oracle-dependent collateral so a user cannot attach an economically irrelevant leg solely as a liquidation shield.

### Proof of Concept
The repository already contains an executable regression-style PoC in `tests/test-harness/tests/controller/audit_supply_stale_shield.rs`:

1. Alice supplies USDC and borrows ETH while healthy; an early liquidation attempt correctly reverts with `HealthFactorTooHigh`. [8](#0-7) 
2. WBTC's oracle observation is made stale, and Alice calls `supply(ALICE, account_id, spoke_id, [(WBTC, 0.001)])`; the new supply slot succeeds despite the unusable price. [9](#0-8) 
3. Alice's primary USDC collateral is crashed so the account becomes liquidatable; a twin account without the WBTC leg is liquidated successfully. [10](#0-9) 
4. `liquidate(LIQUIDATOR, alice_id, [(ETH, 1.0)], Transfer)` and `clean_bad_debt(alice_id)` both revert with `PriceFeedStale`. [11](#0-10) 
5. After WBTC receives a fresh price, the identical liquidation succeeds and reduces Alice's ETH debt. [12](#0-11) 

The Aquarius variant replaces the stale WBTC feed with a listed LP share whose underlying pool value is withdrawn below `min_pool_value_wad`, causing `InsufficientAquariusLiquidity` and the same strict-valuation abort.

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

**File:** contracts/controller/src/positions/liquidation/mod.rs (L46-58)
```rust
    let mut account = storage::get_account(env, account_id);

    let mut cache = Context::new(env);

    require_non_empty_payments(env, debt_payments);

    // Reject an unusable receiver before moving tokens.
    let mut receiver = resolve_seize_receiver(
        env, liquidator, account_id, &account, seize_mode, &mut cache,
    );

    // Share payment normalization and positivity checks with the estimate view.
    let liquidation_plan = plan::build_liquidation_plan(env, &account, debt_payments, &mut cache);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L222-237)
```rust
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

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L88-121)
```rust
    let price_a = engine::resolve_nested(session, &lp.key_a, depth + 1)?;
    let price_b = engine::resolve_nested(session, &lp.key_b, depth + 1)?;
    let (reserve_a, reserve_b) =
        aquarius_pool_reserves_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
    let total_shares =
        aquarius_total_shares_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;

    let leg_a = LpLeg {
        reserve: reserve_a,
        decimals: lp.reserve_a_decimals,
        price_wad: price_a.price_wad,
    };
    let leg_b = LpLeg {
        reserve: reserve_b,
        decimals: lp.reserve_b_decimals,
        price_wad: price_b.price_wad,
    };
    let supply = LpSupply {
        total_shares,
        decimals: share_decimals,
    };
    let price_wad = if stable {
        let amp = aquarius_amp_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
        fair_stable_lp_price_wad(&env, &leg_a, &leg_b, &supply, amp)?
    } else {
        fair_lp_price_wad(&env, &leg_a, &leg_b, &supply)?
    };
    let share_unit = 10i128
        .checked_pow(share_decimals)
        .ok_or(OracleError::InvalidPrice)?;
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L12-18)
```rust
    t.supply(ALICE, "USDC", 10_000.0);
    t.borrow(ALICE, "ETH", 3.0);
    t.supply(BOB, "USDC", 10_000.0);
    t.borrow(BOB, "ETH", 3.0);

    let pre = t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0);
    test_harness::assert_contract_error(pre, errors::HEALTH_FACTOR_TOO_HIGH);
```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L20-69)
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
    assert!(
        t.borrow_balance(ALICE, "ETH") < 3.0,
        "post-recovery liquidation must reduce ALICE's debt"
    );
```
