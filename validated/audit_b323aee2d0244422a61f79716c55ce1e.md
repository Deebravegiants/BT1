### Title
Unpriced dust collateral can freeze liquidation and bad-debt cleanup - (File: contracts/controller/src/risk/totals.rs)

### Summary

`supply` admits a positive collateral leg without resolving that asset's strict price, but every later account valuation iterates over all stored supply positions and strictly resolves every price. A borrower can therefore add a dust position in an asset whose oracle is stale; while it remains stale, `liquidate`, permissionless `clean_bad_debt`, and any debt-preserving withdrawal that leaves that leg revert with `PriceFeedStale`.

### Finding Description

`Controller::supply` reaches `process_supply`, which checks authorization/entry conditions, transfers measured assets into the pool, and merges supply shares without running the full account risk calculation. [1](#0-0)  The supplied leg's risk refresh only prices the full account when a liquidation-favoring tuple change triggers `clears_min_hf`; otherwise the new stale-priced position can be recorded without its strict price being consumed. [2](#0-1) 

Once stored, the leg is a required valuation input: `calculate_account_risk_totals` loads every supply key, calls `cached_price` for each leg, and sums its value. [3](#0-2)  Liquidation calls that shared calculation before checking `HF < 1`; cleanup calls it before checking the dust gate. [4](#0-3) [5](#0-4)  The aggregator hard path rejects a stale outcome with `PriceFeedStale`. [6](#0-5) 

### Impact Explanation

An underwater account's collateral is temporarily frozen from liquidation, and residual bad debt cannot be socially cleaned while the injected leg's feed remains invalid. The borrower's own withdrawal paths are also affected whenever debt remains and the poisoned leg remains part of the account. This delays loss realization and liquidation proceeds; recovery depends on the oracle becoming valid again or the owner fully removing the poisoned leg, neither of which a liquidator controls.

The regression test demonstrates the complete primitive: a stale WBTC supply succeeds, the scaled position persists, then `liquidate`, `clean_bad_debt`, and a partial WBTC withdrawal all revert with `PriceFeedStale`; after WBTC refreshes, the identical liquidation succeeds. [7](#0-6) 

### Likelihood Explanation

The attacker needs only an owned or delegated borrowing account and `supply(caller, account_id, spoke_id, [(hub_asset, positive_amount)])`. Third parties cannot plant a new asset slot because non-owner supply is restricted to assets already held, so this is primarily a self-protection/griefing path rather than arbitrary victim poisoning. [8](#0-7)  It becomes exploitable whenever any listed collateral's configured oracle is stale or otherwise unusable; Aquarius LP collateral can also become unavailable through its configured pool-value floor. [9](#0-8) 

### Recommendation

Do not let economically negligible supply positions become required hard-valuation inputs. Prefer one of:

- strictly resolve the newly supplied asset's price before persisting a new supply leg; or
- omit below-threshold dust legs from HF/dust valuation after proving the leg cannot exceed a fixed USD threshold; or
- provide a permissionless non-price-valued removal path for a dust leg, such as crediting its shares as protocol revenue or quarantining it, so liquidation and cleanup can proceed.

Any solution must preserve conservative collateral valuation and prevent attackers from hiding material collateral from liquidation.

### Proof of Concept

1. Open or control an account holding substantial collateral and debt.
2. Let a listed collateral asset's feed become stale.
3. Call `supply` for that stale asset with a small positive amount. The deposit is measured and merged without strict valuation of the new leg.
4. Move another collateral price downward until the account is liquidatable.
5. Call `liquidate` or `clean_bad_debt`. Both build risk totals over the entire supply map, encounter the stale leg, and revert with `PriceFeedStale`.
6. A debt-preserving partial withdrawal of the poisoned leg also reverts because post-pool solvency still prices the remaining position.
7. Refresh the stale feed and repeat liquidation; the same call succeeds.

This sequence is implemented by `audit_supply_setup_blocks_liquidation_via_stale_dust_leg`. [10](#0-9)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L40-72)
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
```

**File:** contracts/controller/src/positions/supply.rs (L76-97)
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
}
```

**File:** contracts/controller/src/risk/params.rs (L66-93)
```rust
/// Refreshes the liquidation threshold, bonus, and fees together. With debt,
/// changes favoring liquidators require hypothetical health factor >= 1.05.
pub(crate) fn apply_gated_liquidation_params(
    env: &Env,
    cache: &mut Context,
    account: &Account,
    hub_asset: &HubAssetKey,
    position: &mut AccountPosition,
    effective_config: &AssetConfig,
) {
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
    }

    position.liquidation_threshold = effective_config.liquidation_threshold;
    position.liquidation_bonus = effective_config.liquidation_bonus;
    position.liquidation_fees = effective_config.liquidation_fees;
}
```

**File:** contracts/controller/src/risk/totals.rs (L157-180)
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

**File:** contracts/controller/src/positions/liquidation/mod.rs (L212-237)
```rust
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

**File:** contracts/price-aggregator/src/engine.rs (L126-148)
```rust
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

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L4-69)
```rust
fn audit_supply_setup_blocks_liquidation_via_stale_dust_leg() {
    let mut t = LendingTest::new()
        .three_asset_usdc_eth_wbtc()
        .with_dust_disabled_all_markets()
        .build();

    t.set_oracle_single_spot("WBTC");

    t.supply(ALICE, "USDC", 10_000.0);
    t.borrow(ALICE, "ETH", 3.0);
    t.supply(BOB, "USDC", 10_000.0);
    t.borrow(BOB, "ETH", 3.0);

    let pre = t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0);
    test_harness::assert_contract_error(pre, errors::HEALTH_FACTOR_TOO_HIGH);

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

**File:** docs/explanation/threat-model.md (L364-365)
```markdown
| DoS.1 | Price outage blocks valuation-dependent actions, including liquidation; fail-closed availability cost. Supply needs no price, so an indebted borrower can add a dust leg of any listed collateral and choose which feed outage shields the account. For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization. |
| DoS.2 | Selected paused debt or no_seize collateral blocks liquidation; distinct flag policies matter. |
```
