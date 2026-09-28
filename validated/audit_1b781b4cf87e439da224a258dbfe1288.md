### Title
A stale or reverting feed on any dust-sized collateral leg bricks `liquidate` and `clean_bad_debt`, trapping bad debt - (File: contracts/controller/src/external/price_aggregator.rs)

### Summary
The controller values every position through a strict, all-or-nothing aggregator read. `Context::fetch_prices` loads prices for *all* of an account's supply and borrow assets via `PriceAggregatorClient::prices` (the hard path), and the aggregator's `engine::force` panics on any unusable outcome — staleness, sanity-band violation, dual-leg deviation, missing feed, or a provider revert. Because `liquidate` and `clean_bad_debt` both price the entire position set, a single economically irrelevant dust collateral leg whose oracle feed is stale makes the whole account unliquidatable *and* un-cleanable, the exact bad-debt class of the IronBank finding. This is proven by the in-repo regression test `audit_liquidate_and_clean_bricked_by_unpriceable_dust_leg`.

### Finding Description
- `external::price_aggregator::fetch_prices` calls the aggregator's `prices` entrypoint and panics with `OracleNotConfigured` if any requested key is absent; there is no fallback or partial result path. [1](#0-0) 
- `Context::fetch_prices` caches whatever the hard fetch returns; `cached_price` then panics on any miss, so every position the risk engine iterates must resolve. [2](#0-1) 
- On the aggregator side, `engine::resolve` → `compute_hard` → `force` panics for market-condition failures (stale, deviation, sanity band, `NoLastPrice`), not just config errors. [3](#0-2) 
- The harness test shows the concrete shape: WBTC's Reflector feed is set 3,600 s stale; `supply(borrower, "WBTC", 0.001)` still succeeds and persists a non-zero supply leg; after USDC halves and the account goes underwater, `try_liquidate` reverts with `PRICE_FEED_STALE` and `try_clean_bad_debt_by_id` reverts identically. [4](#0-3) 
- A second test confirms the twin account with fresh feeds liquidates normally, isolating the stale dust leg as the blocker. [5](#0-4) 

### Impact Explanation
An underwater account cannot be liquidated and its bad debt cannot be written off via `clean_bad_debt`, because both paths strictly value every leg. The blocker needs no price manipulation: oracle staleness is exogenous (a missed heartbeat, a Reflector/RedStone outage, an Aquarius pool dropping below `min_pool_value_wad`). During a crash — exactly when liquidations matter most — collateral value keeps decaying while the revert persists, destroying liquidation incentive and forcing the protocol toward insolvency. Unlike the IronBank case, even the debt-cleanup escape hatch shares the same failure mode.

### Likelihood Explanation
Any unprivileged borrower can hold a dust supply position in any listed asset; supply deliberately does not require the supplied asset's feed to be fresh. One stale feed out of N configured markets poisons the account. Staleness budgets can be as low as 60 s (`MIN_PRICE_STALE_SECONDS`), so transient provider gaps routinely cross the threshold. Caveat: `docs/reference/invariants.md` INV-ORACLE-01 states required valuations "fail closed, including liquidation," which may be argued as a documented design choice — however, the invariant speaks of *required* prices, and a 0.001-unit dust leg of an unrelated collateral is arguably not required to value the debt being closed or cleaned; the existing `audit_*` tests also suggest the team treats the dust-leg variant as a live concern rather than settled design.

### Recommendation
- In the liquidation path, value only the legs actually needed (debt assets being repaid plus collateral legs being seized), or treat a strict-price failure on a non-seized leg as zero-value for that leg instead of aborting.
- Let `clean_bad_debt` operate on debt legs alone — writing down the borrow index does not require collateral valuation.
- Alternatively, have `liquidate` consume `quotes` (`fetch_prices_status`, which already degrades to `PriceStatus::unusable` per key) and explicitly reject only failures on legs in the pro-rata seize set.

### Proof of Concept
```rust
// tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs
t.set_oracle_single_spot("WBTC");
t.supply(LIQUIDATOR, "USDC", 50_000.0);
t.supply(borrower, "USDC", 10_000.0);
t.borrow(borrower, "ETH", 3.0);

// Make WBTC's feed stale (now - 3_600) and plant a dust leg — supply succeeds.
t.mock_reflector_client().set_price_at(&wbtc, &usd(60_000), &(now - 3_600));
assert!(t.try_supply(borrower, "WBTC", 0.001).is_ok());

// Crash USDC so the borrower is underwater.
t.set_price("USDC", usd_cents(50));

// Both liquidation and bad-debt cleanup revert with PRICE_FEED_STALE.
assert_contract_error(t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0), PRICE_FEED_STALE);
assert_contract_error(t.try_clean_bad_debt_by_id(borrower_id), PRICE_FEED_STALE);
```

### Citations

**File:** contracts/controller/src/external/price_aggregator.rs (L18-28)
```rust
pub(crate) fn fetch_prices(env: &Env, assets: &Vec<Address>) -> Map<Address, PriceFeedRaw> {
    let aggregator = storage::get_price_aggregator(env);
    let keyed = PriceAggregatorClient::new(env, &aggregator).prices(&token_keys(env, assets));
    let mut out = Map::new(env);
    for asset in assets.iter() {
        match keyed.get(PriceKey::Token(asset.clone())) {
            Some(feed) => out.set(asset, feed),
            None => panic_with_error!(env, OracleError::OracleNotConfigured),
        }
    }
    out
```

**File:** contracts/controller/src/context.rs (L141-160)
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
    }
```

**File:** contracts/price-aggregator/src/engine.rs (L181-189)
```rust
pub(crate) fn force(env: &Env, outcome: &Outcome, oracle: Option<&AssetOracle>) -> PriceFeedRaw {
    if let Some(err) = outcome.failure(oracle) {
        panic_with_error!(env, err);
    }
    let Some(oracle) = oracle else {
        panic_with_error!(env, OracleError::OracleNotConfigured)
    };
    outcome.to_feed(oracle.asset_decimals)
}
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L26-41)
```rust
    let plant = t.try_supply(borrower, "WBTC", 0.001);
    assert!(
        plant.is_ok(),
        "supply must accept the fragile leg with a stale feed: {plant:?}"
    );

    t.set_price("USDC", usd_cents(50));

    let borrower_id = t.resolve_account_id(borrower);

    let liq = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    test_harness::assert_contract_error(liq, errors::PRICE_FEED_STALE);

    let clean = t.try_clean_bad_debt_by_id(borrower_id);
    test_harness::assert_contract_error(clean, errors::PRICE_FEED_STALE);

```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L39-58)
```rust
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
