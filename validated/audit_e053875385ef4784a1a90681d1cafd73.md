### Title
Unpriceable dust collateral leg permanently shields an underwater account from liquidation and bad-debt cleanup - (File: contracts/controller/src/positions/liquidation/plan.rs)

### Summary
The NodeGoat CVE-2021-4247 class — attacker-controlled input steering the protocol into a denial-of-service state — maps onto XOXNO Lending's health-factor valuation path. `build_liquidation_plan` computes `calculate_account_risk_totals` over **every** supply position of the target account before checking HF < 1 [1](#0-0) . The totals loop resolves a strict price for each collateral leg via `cache.cached_price(&hub_asset.asset)` [2](#0-1) , and missing cached prices fail closed per INV-ORACLE-03 [3](#0-2) . The `supply` entrypoint, however, does not require a valid price to add a collateral leg. A borrower can therefore plant a dust-sized leg of any listed collateral whose price feed is — or can be made — unavailable, and the account becomes unliquidatable and uncleanable for as long as that leg is unpriceable. The repo pins this behavior in `audit_supply_stale_shield` and `audit_liquidate_and_clean_bricked_by_unpriceable_dust_leg` [4](#0-3) , and documents it as threat DoS.1 [5](#0-4) .

### Finding Description
- Root cause: supply admission does not price the new leg, while every downstream risk operation (liquidate, clean_bad_debt, withdraw-with-debt, full threshold refresh) requires strict prices for **all** of the account's supply legs. One unpriceable leg poisons the entire valuation — the strict read raises (e.g., `PriceFeedStale` 206, `NoLastPrice` 210, `InsufficientAquariusLiquidity` 235) inside `calculate_account_risk_totals`, before the HF check or the repayment/seizure plan runs [2](#0-1) .
- Reachable path (single unprivileged address):
  1. Attacker opens an account, supplies collateral A, borrows asset B via `Controller::borrow`.
  2. Attacker calls `Controller::supply` with a dust amount of a fragile collateral C (accepted even while C's feed is already stale — pinned by the harness test [6](#0-5) ).
  3. Attacker waits for C's feed to lapse, or actively induces the outage: for a listed Aquarius LP collateral, `aquarius::read` returns `InsufficientAquariusLiquidity` whenever pool value falls below `min_pool_value_wad` [7](#0-6) , a threshold reachable by ordinary liquidity withdrawal (`own trades on Aquarius` is in scope).
  4. Every `liquidate` call against the account now reverts in the price read, before `HealthFactorTooHigh` can even be evaluated; `clean_bad_debt` and `update_account_threshold` fail the same way [8](#0-7) .
- The mainnet config lists real Aquarius LP collateral markets with `min_pool_value_wad` floors (e.g., `AQUAUSDC_LP`, `XAUMUSDC_LP`) [9](#0-8) , so the self-induced variant is deployable, not hypothetical.

### Impact Explanation
While the shield is up, the attacker's debt accrues interest but cannot be liquidated, and if the account goes insolvent `clean_bad_debt` also reverts, so the protocol cannot socialize the loss — the bad debt is permanently frozen on the book and the supply-index write-down path is unreachable. That is "permanent freezing of funds / protocol insolvency progression" under the stated impact list. If the attacker controls the LP liquidity, they can raise and lower the shield at will (remove liquidity to block liquidation during a crash, restore it after repositioning), converting a transient market move into realized bad debt borne by suppliers.

### Likelihood Explanation
Cost is one dust supply transaction plus, in the LP variant, temporary liquidity withdrawal from a pool the attacker may already LP in. No privileged role, no leaked key, no oracle dishonesty is needed — the fail-closed behavior of `aquarius::read` and strict `cached_price` does the work. The only precondition is a listed collateral whose price can lapse (any feed can go stale) or whose LP floor can be crossed (any LP collateral). Existing monitoring (`LendingLpPoolValueNearFloor`) treats this as a warning scenario rather than a mitigation [10](#0-9) .

### Recommendation
Make risk valuation robust to a single unpriceable leg, or make leg admission prove priceability:
- Price the new leg at `supply` time when the account carries debt (reject supply of an unpriceable asset into an indebted account), or
- In `calculate_account_risk_totals`, treat a collateral leg with an unusable price as zero-valued collateral rather than aborting — conservative for the account (its HF drops, making liquidation easier, not harder) while keeping liquidation/cleanup reachable. This must be paired with seizure handling for that leg (skip or transfer-at-zero) since the pro-rata seizure plan also needs leg prices.
- Alternatively, add a permissionless `remove_unpriceable_leg` / forced-seizure path for legs whose oracle returns a hard error, bounded so it cannot strip a priced leg.

### Proof of Concept
The repo's own harness test demonstrates the flow end to end (`tests/test-harness/tests/controller/audit_supply_stale_shield.rs`):

```rust
t.supply(ALICE, "USDC", 10_000.0);
t.borrow(ALICE, "ETH", 3.0);
// WBTC feed is stale (timestamp now - 3600)
let plant = t.try_supply(ALICE, "WBTC", 0.001);   // succeeds despite stale feed
t.set_price("USDC", usd_cents(50));               // account goes underwater
let liq = t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0);
// -> Error(Contract, PRICE_FEED_STALE)  — liquidation bricked
let clean = t.try_clean_bad_debt_by_id(alice_id);
// -> Error(Contract, PRICE_FEED_STALE)  — bad-debt cleanup bricked too
``` [11](#0-10) 

A twin account without the dust leg liquidates normally under identical prices, isolating the leg — not the crash — as the cause [12](#0-11) . For the actively-induced variant, substitute an Aquarius LP collateral and withdraw pool liquidity below `min_pool_value_wad`; `aquarius::read` then returns `InsufficientAquariusLiquidity` on every valuation [13](#0-12) .

### Citations

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

**File:** contracts/controller/src/risk/totals.rs (L84-97)
```rust
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

**File:** docs/reference/invariants.md (L320-328)
```markdown
### INV-ORACLE-03 — A context retains fetched prices

A controller context retains each fetched asset price and requests only missing
assets on subsequent fetches. Missing cached prices fail closed. Aggregator
sessions also cache resolved keys.

These caches preserve repeated valuations within their context. They do not
provide identical observation timestamps across sources or a transaction-wide
snapshot shared by independent contexts.
```

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L3-58)
```rust
#[test]
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
```

**File:** docs/explanation/threat-model.md (L364-365)
```markdown
| DoS.1 | Price outage blocks valuation-dependent actions, including liquidation; fail-closed availability cost. Supply needs no price, so an indebted borrower can add a dust leg of any listed collateral and choose which feed outage shields the account. For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization. |
| DoS.2 | Selected paused debt or no_seize collateral blocks liquidation; distinct flag policies matter. |
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

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L36-41)
```rust
    let liq = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    test_harness::assert_contract_error(liq, errors::PRICE_FEED_STALE);

    let clean = t.try_clean_bad_debt_by_id(borrower_id);
    test_harness::assert_contract_error(clean, errors::PRICE_FEED_STALE);

```

**File:** configs/mainnet/markets.json (L1628-1644)
```json
        "sources": [
          {
            "AquariusLp": {
              "pool": "CA6GAFOJCW4MGQQBUCQUSA3CLIH25G4SNKB2JHYKZCVWZTNW5VXMSC4O",
              "token_a": "CAUIKL3IYGMERDRUN6YSCLWVAKIFG5Q4YJHUKM4S4NJZQIA3BAS6OJPK",
              "token_b": "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75",
              "key_a": {
                "Token": "CAUIKL3IYGMERDRUN6YSCLWVAKIFG5Q4YJHUKM4S4NJZQIA3BAS6OJPK"
              },
              "key_b": {
                "Token": "CCW67TSZV3SSS2HXMBQ5JFGCKJNXKZM7UQUWUZPUTHXSTZLEO7SJMI75"
              },
              "reserve_a_decimals": 7,
              "reserve_b_decimals": 7,
              "min_pool_value_wad": "200000000000000000000000"
            }
          }
```

**File:** services/lending-exporter/ops/alerts.yml (L42-48)
```yaml
      - alert: LendingLpPoolValueNearFloor
        expr: (lending_oracle_price_usd * lending_oracle_lp_total_shares) / lending_oracle_lp_pool_floor_usd < 1.25 and lending_oracle_lp_pool_floor_usd > 0
        for: 10m
        labels: { severity: warning }
        annotations:
          summary: "Aquarius pool behind {{ $labels.symbol }} ({{ $labels.network }}) is within 25% of its value floor"
          description: "Pool value is {{ $value | humanize }}x the min_pool_value floor. Under 1.0x the LP price is rejected and accounts holding this leg become unliquidatable. Review the floor, the listing's collateral flag, and the spoke borrow caps."
```
