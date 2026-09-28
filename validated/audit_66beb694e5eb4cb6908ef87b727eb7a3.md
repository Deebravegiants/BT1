### Title
Borrower permanently escapes liquidation by holding a dust Aquarius-LP collateral leg whose pool they drain below `min_pool_value_wad` - ([File: contracts/price-aggregator/src/providers/aquarius.rs](contracts/price-aggregator/src/providers/aquarius.rs))

### Summary
The MySQL CVE is a remotely triggerable hang/crash — a denial of service on a core operation. The XOXNO Lending analog is an unprivileged borrower-induced DoS of the liquidation path: `calculate_account_risk_totals` requires a strict price for **every** collateral leg of the account, and an Aquarius LP leg fails pricing whenever the underlying pool's total value drops below `min_pool_value_wad`. A borrower who is also an LP in that Aquarius pool can add a dust LP leg as collateral, then withdraw their liquidity to push pool value under the threshold. Every subsequent `liquidate` call reverts while resolving prices, so the underwater account cannot be liquidated until other LPs restore pool value — which may never happen.

### Finding Description
- `liquidate` calls `build_liquidation_plan` (`contracts/controller/src/positions/liquidation/plan.rs:14`), which calls `risk::calculate_account_risk_totals` (`plan.rs:34`).
- `calculate_account_risk_totals_body` loads markets for **all** supply and borrow keys and unconditionally calls `cache.cached_price(&hub_asset.asset)` for every supply position (`contracts/controller/src/risk/totals.rs:163-173`). A failing feed aborts the whole call — there is no skip or zero-price fallback on the strict liquidation path.
- For an Aquarius LP collateral, `providers::aquarius::read` computes `pool_value_wad` and returns `Err(OracleError::InsufficientAquariusLiquidity)` when `pool_value_wad < lp.min_pool_value_wad` (`contracts/price-aggregator/src/providers/aquarius.rs:118-122`). Pool value is derived from live `aquarius_pool_reserves_call`/`aquarius_total_shares_call` reads (`aquarius.rs:90-93`), which any LP can shrink by withdrawing liquidity.
- Supply entry does not require a usable price, so an already-indebted borrower can `supply` a dust amount of the Aquarius LP share token as an extra collateral leg at negligible cost.
- Attack sequence (single unprivileged address, in-scope entrypoints): `supply(lp_share, dust)` on their own borrowing account → `liquidate` attempts now resolve the LP leg → attacker calls the Aquarius pool's `withdraw` to push `pool_value_wad` below `min_pool_value_wad` → `aquarius::read` returns `InsufficientAquariusLiquidity` → strict price resolution fails → `calculate_account_risk_totals` reverts → `liquidate` always reverts. The same leg also blocks `clean_bad_debt` and governed force-socialization paths that evaluate the account, as the threat-model register's DoS.1 row describes (`docs/explanation/threat-model.md`, DoS.1).
- The attacker can restore liquidity at will, wait for their HF to drift further underwater (interest accrual continues), and re-trigger the outage whenever a liquidation is attempted — a repeatable "hang" of the risk-clearing mechanism, matching the CVE's availability-impact class.

### Impact Explanation
The account becomes unliquidatable for as long as the attacker keeps the Aquarius pool under `min_pool_value_wad`. With HF < 1 debt accruing interest, the position matures into bad debt that `clean_bad_debt`/recapitalization cannot cleanly clear while the price read fails, transferring losses to suppliers via supply-index write-down — protocol insolvency, an accepted impact class. Cost to the attacker is a dust LP position plus temporarily parked liquidity, which is recoverable.

### Likelihood Explanation
Requires only: (a) a listed collateral whose oracle source is `AquariusLpSource` over a pool thin enough that the attacker's own LP share is a meaningful fraction of pool value, and (b) the attacker holding a borrow position. Both are ordinary unprivileged actions (supply, borrow, Aquarius liquidity management). No privileged flag, oracle dishonesty, or timing race is needed; the attacker controls the outage switch directly. Medium severity: impact is insolvency-class but bounded by the attacker's debt size per account and requires a listed LP market with reachable `min_pool_value_wad`.

### Recommendation
- On strict risk paths (liquidation, bad-debt cleanup), treat a *collateral* leg with an unavailable price as zero-value rather than aborting the entire valuation, or value unavailable-price collateral at 0 for HF/seizure purposes while still requiring debt-leg prices. A dust-priced-out leg then reduces HF instead of shielding it.
- Alternatively, prevent supply of collateral legs whose price cannot currently be resolved (strict price check at supply entry for collateral-designated positions), and/or omit zero-or-sub-dust planned seizure legs before pricing (already partially done for seizure legs per INV-HALT-02, but not for the HF computation).
- Set `min_pool_value_wad` high enough relative to realistic single-LP withdrawable share that draining below it costs more than the debt being shielded.

### Proof of Concept
1. Attacker account has supply collateral C and borrow debt B, HF currently > 1.
2. Attacker supplies a dust amount of Aquarius LP share token `S` (listed in their spoke, collateralizable) to the same account via `Controller.supply`.
3. Attacker calls the Aquarius pool's `withdraw` for their own LP position until `price_wad * total_shares / share_unit < lp.min_pool_value_wad` (checked in `aquarius.rs:120-122`).
4. Prices move so HF < 1. Liquidator calls `Controller.liquidate(liquidator, attacker_account, payments, SeizeMode::Transfer)`.
5. `build_liquidation_plan` → `calculate_account_risk_totals` → `cached_price(S)` → aggregator `read` → `Err(InsufficientAquariusLiquidity)` → transaction reverts. Repeat for any payment selection, any liquidator, and for `clean_bad_debt`/`update_account_threshold` paths that price the full account.
6. Attacker later re-adds liquidity to restore the price at their convenience — demonstrating attacker-controlled, repeatable liquidation DoS. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

Note: the mechanism is described in threat-model row DoS.1, but that register explicitly "does not assign severity or establish exploitability" and is not an ADR exclusion; the revert-on-missing-price behavior in `calculate_account_risk_totals` combined with LP-controllable `InsufficientAquariusLiquidity` makes it a live, attacker-reachable liquidation DoS.

### Citations

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L118-122)
```rust
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
    }
```

**File:** contracts/controller/src/risk/totals.rs (L163-173)
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

**File:** docs/explanation/threat-model.md (L364-365)
```markdown
| DoS.1 | Price outage blocks valuation-dependent actions, including liquidation; fail-closed availability cost. Supply needs no price, so an indebted borrower can add a dust leg of any listed collateral and choose which feed outage shields the account. For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization. |
| DoS.2 | Selected paused debt or no_seize collateral blocks liquidation; distinct flag policies matter. |
```
