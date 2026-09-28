### Title
No grace period after an oracle/network outage lets a liquidator seize collateral in the first ledger after prices resume - (File: contracts/controller/src/positions/liquidation/plan.rs)

### Summary
`liquidate` gates only on `health_factor < 1 WAD` computed from the current `Context` prices. The price aggregator fails closed while any required feed is stale, but once a fresh observation lands there is no cooldown or grace period: the very first transaction that sees the new price can liquidate an account that had no opportunity to add collateral or repay during the outage. This is the XOXNO analog of the L2-sequencer-downtime unfair-liquidation class — on Stellar the sequencer equivalent is a ledger/network halt (or an oracle outage during which all valuation-dependent paths revert).

### Finding Description
`process_liquidation` builds a `Context`, calls `plan::build_liquidation_plan`, and only requires the account's health factor to be below `Wad::ONE`. [1](#0-0)  Prices come from `Context`-cached strict reads of the price aggregator, which rejects stale feeds via `is_stale(now, timestamp, max_price_stale_seconds)` and converts any stale outcome into `OracleError::PriceFeedStale`. [2](#0-1) [3](#0-2) 

So the system has exactly two states: all valuation-dependent verbs (liquidate, borrow, withdraw, supply-with-debt gate, `update_account_threshold`, `clean_bad_debt`) revert while a required feed is stale, and all of them are fully live the instant a fresh price exists. Nothing records when a feed transitioned stale→fresh, and nothing delays liquidation relative to that transition. The harness confirms this boundary directly: a NAV exactly at the 26 h staleness budget prices and liquidates, one second more fails closed — there is no post-recovery window. [4](#0-3) 

Attack path (unprivileged liquidator):
1. Stellar ledger halt (or oracle outage exceeding `max_stale_seconds`, up to 93,600 s) freezes the market. Borrowers cannot submit `supply`/`repay`/`repay_debt_with_collateral` because no ledgers close (or because their chosen rescue verb reads prices).
2. Collateral price crashes during the halt; the borrower's HF crosses below 1 off-chain.
3. Chain resumes, ledger timestamp jumps to wall clock, the oracle posts a fresh observation.
4. Liquidator calls `liquidate(liquidator, account_id, debt_payments, SeizeMode::Transfer)` in the same ledger the fresh price lands, collecting the HF-curve bonus, before the borrower can react. [5](#0-4) 

### Impact Explanation
Borrowers lose the liquidation bonus (and liquidation fee share) on collateral they would have kept had they been given even a short window to top up or repay — a direct, forced transfer of user funds to whichever liquidator wins the first-ledger race. The loss is bounded by the configured bonus curve but is repeatable across every account that crossed below HF during the outage.

### Likelihood Explanation
Requires a chain halt or a correlated feed outage plus adverse price movement — infrequent, but it is precisely the scenario the staleness checks acknowledge (26 h budgets exist because outages are expected). Once it occurs, liquidation is guaranteed to be executable immediately since `build_liquidation_plan` has no time-since-recovery condition; exploitation needs only a normal `liquidate` call.

### Recommendation
Track a per-oracle (or global) "freshness recovery" timestamp — e.g., the first ledger time at which all required feeds for an account's collateral resolve non-stale after having been stale/missing — and refuse `liquidate`/`clean_bad_debt` until a configured grace period has elapsed since recovery. Supply and repay must remain allowed during the grace window so borrowers can cure.

### Proof of Concept
1. ALICE supplies USDC and borrows ETH at HF slightly above 1.
2. Advance ledger time past the XLM/USDC feed `max_stale_seconds` without posting new prices: `liquidate` and `borrow` both revert `PriceFeedStale` (mirroring `lqv_params_nav_prices_until_the_26_hour_staleness_budget` and `poc_stale_oracle_blocks_liquidation`).
3. Post a fresh observation at a price where ALICE's collateral value dropped 50% (HF < 1).
4. In the same ledger, LIQUIDATOR calls `liquidate` with the estimated `debt_payments` and `SeizeMode::Transfer`; the call succeeds and seizes collateral at the bonus — no on-chain state distinguishes "first ledger after outage" from steady-state, so no grace is enforced.

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

**File:** contracts/price-aggregator/src/engine.rs (L133-135)
```rust
        if self.stale {
            return Some(OracleError::PriceFeedStale);
        }
```

**File:** contracts/price-aggregator/src/engine.rs (L555-560)
```rust
    let stale = component_stale
        || is_stale(
            session.now_secs(),
            timestamp,
            oracle.max_price_stale_seconds,
        );
```

**File:** tests/test-harness/tests/controller/liqvid_listing_params.rs (L583-603)
```rust
fn lqv_params_nav_prices_until_the_26_hour_staleness_budget() {
    let mut p = setup(100);
    p.t.supply("lender", "USDC", 1_000_000.0);
    let id = p.open_at_max_ltv("alice", 10_000, p.nav_ref);
    p.t.advance_time(2 * 86_400);
    let nav = p.nav_ref * 930 / 1_000;

    p.post_nav_aged(nav, NAV_MAX_STALE_SECONDS + 1);
    assert_eq!(
        p.try_liquidate("liquidator", id),
        Err(contract_error(errors::PRICE_FEED_STALE))
    );
    assert_eq!(
        p.try_borrow("alice", id, USDC_UNIT),
        Err(contract_error(errors::PRICE_FEED_STALE))
    );

    p.post_nav_aged(nav, NAV_MAX_STALE_SECONDS);
    p.try_liquidate("liquidator", id)
        .expect("a NAV exactly 26 hours old prices");
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L36-58)
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
```
