### Title
Self-planted unpriceable dust supply leg bricks `liquidate` and permissionless `clean_bad_debt`, letting an underwater account evade liquidation while debt accrues - (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary
Risk totals (`calculate_account_risk_totals`, used by both the liquidation gate and `socialize_bad_debt`) price *every* supply and debt leg with strict, fresh oracle prices. `supply` accepts a dust position in an asset whose feed is about to go (or already is) stale, so a borrower can plant a near-worthless collateral leg in a fragile-feed asset. Once that feed goes stale, every `liquidate` and every permissionless `clean_bad_debt` on the account reverts with `PriceFeedStale` until the feed recovers — the account cannot be liquidated or socialized at all. The repository contains a dedicated harness test reproducing exactly this bricking.

### Finding Description
- `calculate_ltv_collateral_wad` / the risk-total path loads a cached price for every key in `account.supply_positions` and `account.borrow_positions` via `cache.cached_price(&hub_asset.asset)`, with no skip for dust or zero-value legs (`contracts/controller/src/risk/totals.rs:22-38,48-60,81-90`). [1](#0-0) 
- `socialize_bad_debt` runs the same totals before its insolvency gate, so cleanup inherits the same all-legs-must-be-priced requirement (`contracts/controller/src/positions/liquidation/mod.rs:212-238`). [2](#0-1) 
- `supply` on the controller accepts a dust deposit into any listed asset without requiring a fresh price at admission; the harness PoC supplies `0.001` WBTC while the Reflector feed is already an hour stale and the call succeeds. [3](#0-2) 
- After the real collateral (USDC) price crashes and the account goes underwater, both `try_liquidate` and `try_clean_bad_debt_by_id` revert with `PRICE_FEED_STALE` purely because of the planted WBTC leg, and only succeed again once the WBTC feed is refreshed (`tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs:32-51`). [4](#0-3) 

The analog to CVE-2019-2502 is the repeatable-crash/hang class: a single unprivileged address can put its own account into a state where the protocol's only unprivileged remediation paths (`liquidate`, `clean_bad_debt`) deterministically revert, while borrow interest keeps accruing.

### Impact Explanation
Temporary freezing of funds trending toward protocol insolvency. While the planted feed is stale: no liquidator can touch the account, and no one can permissionlessly socialize it, so the debt compounds unbounded. If the feed never recovers (delisted feed, permanently stalled signer set), the account stays unliquidatable indefinitely and eventual forced cleanup is owner-only, so the protocol absorbs the grown bad debt. This is worse than a simple fail-closed pause because the attacker *manufactures* the condition after borrowing, at near-zero cost (one dust deposit), rather than relying on an external outage — they choose an asset with a fragile feed and supply dust of it.

### Likelihood Explanation
Reachable by any unprivileged address via `supply(account_id, assets)` (own account) + `borrow`, then letting/planting staleness on the chosen asset's feed. Cost is one dust deposit and the borrowed principal is already extracted. The constraint is that the asset's oracle must go stale; attackers will prefer the least-reliable listed feed, and feed outages are a recurring operational event on oracle-backed markets. Medium likelihood, matching a Medium-severity analog.

### Recommendation
- Price supply legs lazily in the liquidation/cleanup gates: treat a supply leg whose floor value is provably dust (e.g. below the bad-debt threshold contribution) as zero for pricing instead of requiring a fresh strict price, or allow `liquidate`/`clean_bad_debt` to seize/write down legs that cannot be priced rather than aborting.
- Alternatively, require a valid strict price at `supply` admission for every listed asset so an unpriceable leg can never enter an account.
- At minimum, let `clean_bad_debt` proceed when the unpriceable legs' combined share of collateral is below the dust gate, since cleanup writes the whole position off anyway.

### Proof of Concept
```rust
// tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs
let mut t = LendingTest::new().three_asset_usdc_eth_wbtc().with_dust_disabled_all_markets().build();
t.set_oracle_single_spot("WBTC");
t.supply(borrower, "USDC", 10_000.0);
t.borrow(borrower, "ETH", 3.0);
// plant the poison leg while the feed is already stale — supply accepts it
t.mock_reflector_client().set_price_at(&wbtc, &usd(60_000), &(now - 3_600));
t.try_supply(borrower, "WBTC", 0.001).unwrap();
t.set_price("USDC", usd_cents(50));                 // account now underwater
assert_contract_error(t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0), errors::PRICE_FEED_STALE);
assert_contract_error(t.try_clean_bad_debt_by_id(borrower_id), errors::PRICE_FEED_STALE);
```

Uncertain: whether this is intentionally retained behavior (the file is an `audit_`-prefixed characterization test, and the threat model notes missing prices as a known obstacle to cleanup [5](#0-4) ). If that documentation is treated as a documented design choice, this finding weakens to a known limitation rather than a novel bug; the exploit path and root cause above stand regardless.

### Citations

**File:** contracts/controller/src/risk/totals.rs (L22-38)
```rust
pub(crate) fn account_price_assets(
    env: &Env,
    account: &Account,
    extras: &Vec<Address>,
) -> Vec<Address> {
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
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L212-238)
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
}
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L20-31)
```rust
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

```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L32-51)
```rust
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

**File:** docs/explanation/threat-model.md (L271-275)
```markdown
paused debt blocks a repayment leg that selects it. Seizure uses its own
no_seize flag across nonzero planned collateral legs; one such flag can abort
a pro-rata liquidation. It does not prevent new supply by itself. Interest
continues while a listing is paused. Missing prices and liquidity limits remain
independent obstacles even when an entrypoint is not pause-gated.
```
