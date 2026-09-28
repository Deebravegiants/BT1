### Title
Dust collateral leg on an attacker-drained Aquarius LP feed bricks `liquidate` and `clean_bad_debt`, shielding bad debt - (File: contracts/controller/src/risk/totals.rs)

### Summary

`calculate_account_risk_totals` values **every** supply leg of an account, and each leg calls `cached_price`, which panics when that asset's feed fails [1](#0-0) . Both `liquidate` (via `build_liquidation_plan`) and the permissionless `clean_bad_debt` (via `socialize_bad_debt`) compute these totals before doing anything else [2](#0-1) [3](#0-2) . Supply requires no valid price — `process_deposit` only checks entry flags, caps, and measured receipts [4](#0-3) . A borrower can therefore attach a dust leg of a collateral whose feed it can kill on demand, making its account permanently unliquidatable and unsocializable.

### Finding Description

The Aquarius LP oracle source fails closed with `InsufficientAquariusLiquidity` whenever the pool's total value drops below the configured `min_pool_value_wad` [5](#0-4) . Pool value is computed live from on-chain reserves, so anyone providing liquidity to that Aquarius pool can withdraw it and push the feed below the floor at will.

Attack sequence by a single unprivileged address:

1. Provide liquidity to a listed Aquarius pool whose LP share token is an accepted collateral.
2. `supply` real collateral + `borrow` to near the limit (standard path).
3. `supply` a dust amount of the Aquarius LP share into a second supply slot — succeeds even while the feed is already failing, because supply never prices the leg (proven in-tree: `t.try_supply(borrower, "WBTC", 0.001)` succeeds with a stale feed) [6](#0-5) .
4. When the account goes underwater, withdraw the Aquarius liquidity. The LP feed now returns `InsufficientAquariusLiquidity`, `cached_price` panics inside the collateral loop, and both `liquidate` and `clean_bad_debt` revert on every attempt.

The in-tree audit test demonstrates exactly this bricking: liquidation and `clean_bad_debt` both revert (`PRICE_FEED_STALE` there; `InsufficientAquariusLiquidity` here) until the feed recovers [7](#0-6) . The dust gate cannot rescue the account either: socialization runs the same `calculate_account_risk_totals` [8](#0-7) , and the leg cannot be removed by anyone but the borrower — third-party top-ups are restricted to existing positions, and nobody else can withdraw another account's leg [9](#0-8) .

### Impact Explanation

Permanent freezing of funds / protocol insolvency: the attacker's debt accrues interest while every liquidation and bad-debt cleanup path reverts. Since seizure is pro-rata across all collateral and valuation is all-or-nothing, even a solvent-priced collateral book cannot be touched. The attacker controls the duration entirely — the feed stays dead only as long as the pool stays below `min_pool_value_wad`, and the attacker can restore liquidity to exit (withdrawing collateral requires the same totals... note `withdraw` also calls `enforce_post_pool_solvency` only when debt remains, so recovery of the healthy portion may require restoring liquidity first, which the attacker is willing to do). Net effect: guaranteed bad-debt socialization cost borne by suppliers whenever the attacker chooses, at the price of one dust LP leg and temporarily parked LP capital.

### Likelihood Explanation

High for any listed Aquarius LP collateral. The attacker needs only a majority of a shallow pool's liquidity (or can pick a pool already near the floor) plus a dust LP position. All steps are unprivileged entrypoints: `supply`, `borrow`, and own Aquarius LP withdrawals — all within the reachable set. The only precondition is that an Aquarius-sourced LP token is listed as collateral, which the market configs show in use [10](#0-9) . The same shield works with any feed an attacker can fail (e.g., waiting for a natural Reflector/RedStone outage and planting the leg during it, since supply never validates the price).

### Recommendation

Isolate per-leg price failures from whole-account valuation:

- In `calculate_account_risk_totals`, treat an unpriceable supply leg as zero-value collateral (skip it) rather than panicking, so liquidation proceeds on the remaining priced legs; or
- In `build_liquidation_plan`/`calculate_seized_collateral`, drop collateral legs whose price fails and seize only across priced legs; and
- In `socialize_bad_debt`, value unpriceable collateral as zero so insolvent accounts can still be cleaned up.
- Alternatively/additionally, gate supply of a new collateral leg on a successful strict price read so a leg with a dead feed can never enter the book.

### Proof of Concept

Adapted from the in-tree audit test `tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs` [11](#0-10) :

```rust
// Setup: markets USDC, ETH, AQUA-LP (Aquarius LP collateral, min_pool_value_wad = M)
// 1. Attacker provides most of the liquidity to the AQUA pool.
t.supply(ALICE, "USDC", 10_000.0);
t.borrow(ALICE, "ETH", 3.0);

// 2. Attacker plants a dust LP leg — supply does not read the price feed.
t.supply(ALICE, "AQUA-LP", 0.001);

// 3. Price move makes the account liquidatable.
t.set_price("USDC", usd_cents(50));

// 4. Attacker withdraws its Aquarius liquidity -> pool_value < M
//    -> aquarius::read returns InsufficientAquariusLiquidity.
aquarius.withdraw_liquidity(ATTACKER_LP_SHARES);

// 5. Both permissionless exit paths brick on the dust leg's feed.
let liq = t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0);
assert_contract_error(liq, errors::INSUFFICIENT_AQUARIUS_LIQUIDITY);

let clean = t.try_clean_bad_debt_by_id(alice_id);
assert_contract_error(clean, errors::INSUFFICIENT_AQUARIUS_LIQUIDITY);
// Account stays unliquidatable and unsocializable until the attacker
// re-adds pool liquidity.
```

Root cause: `calculate_account_risk_totals` requires a successful price for every supply leg [12](#0-11) , `aquarius::read` fails below `min_pool_value_wad` [13](#0-12) , and supply imposes no price check [14](#0-13) .

Severity: **High** — a single unprivileged borrower can indefinitely immunize an underwater account against both liquidation and permissionless bad-debt socialization, converting its debt into guaranteed protocol insolvency at will.

### Citations

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

**File:** contracts/controller/src/positions/supply.rs (L78-97)
```rust
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

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L118-122)
```rust
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
    }
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L4-51)
```rust
fn audit_liquidate_and_clean_bricked_by_unpriceable_dust_leg() {
    let mut t = LendingTest::new()
        .three_asset_usdc_eth_wbtc()
        .with_dust_disabled_all_markets()
        .build();

    t.set_oracle_single_spot("WBTC");

    t.supply(LIQUIDATOR, "USDC", 50_000.0);
    let borrower = test_harness::ALICE;
    t.supply(borrower, "USDC", 10_000.0);
    t.borrow(borrower, "ETH", 3.0);

    let fresh = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    test_harness::assert_contract_error(fresh, errors::HEALTH_FACTOR_TOO_HIGH);

    t.advance_time(5_000);
    let now = t.env.ledger().timestamp();
    let wbtc = t.resolve_asset("WBTC");
    t.mock_reflector_client()
        .set_price_at(&wbtc, &usd(60_000), &(now - 3_600));

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

**File:** configs/mainnet/markets.json (L1-1)
```json
{
```
