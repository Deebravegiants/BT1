The bug-class hint is availability/DoS via flooding — the on-chain analog is an unprivileged actor forcing a fail-closed pricing path to shield a position. Checking the Aquarius LP pricing and liquidation gating code.### Title
Self-inflicted Aquarius LP price outage shields an underwater account from liquidation and bad-debt cleanup - (File: contracts/price-aggregator/src/providers/aquarius.rs)

### Summary
An unprivileged borrower can add a dust-sized Aquarius LP token as a collateral leg, then withdraw liquidity from that pool (or trade it down) so the pool's WAD value falls below the configured `min_pool_value_wad`. The price aggregator then returns `InsufficientAquariusLiquidity` for that collateral, the controller's strict price read fails closed, and every liquidation plan or `clean_bad_debt` valuation for the account aborts — regardless of how far below 1 the real health factor is. This maps the GMGN incident's flood/availability-attack class onto a permissionless, economically-driven availability failure of the liquidation path.

### Finding Description
The Aquarius LP provider computes a fair LP price from pool reserves and total shares, then rejects the observation when the total pool value is under the source's liquidity floor: [1](#0-0) 

`read` propagates that error to its caller, and any pool-read or leg-resolution failure likewise returns an `OracleError` instead of a stale/zero price [2](#0-1) . On the controller side, `build_liquidation_plan` computes `totals` via `risk::calculate_account_risk_totals` over all supply positions using strict prices, and asserts `health_factor < Wad::ONE` [3](#0-2) . A single failing leg therefore aborts the entire valuation: the liquidation call reverts before any repayment leg is even normalized. Because account collateral must come from listed assets, the only requirement is that some Aquarius LP share token is listed as collateral (mainnet `markets.json` configures LP sources with `min_pool_value_wad`), and that the underlying Aquarius pool is shallow enough for one LP to push its value under the floor. `supply` requires no price check for adding a collateral leg to the attacker's own account, and `clean_bad_debt` similarly needs a valuation that the same leg breaks. The threat model itself registers this scenario: "For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization" [4](#0-3) .

### Impact Explanation
For the duration of the outage the position cannot be liquidated and cannot be bad-debt-cleaned, so the account's debt keeps accruing interest while its real collateral value can fall arbitrarily low — protocol insolvency / unbounded bad debt for that account. The attacker can also cyclically restore and drain the pool (add liquidity back to let their own favorable liquidation through, drain again to block competitors or cleanup), giving controlled denial of liquidation. Cost of attack is bounded by the LP liquidity needed to push pool value below `min_pool_value_wad` plus a dust LP supply leg, both fully within an unprivileged address's reach (`supply` on own account + own Aquarius LP withdrawal/trades).

### Likelihood Explanation
Requires a listed Aquarius LP collateral whose backing pool is shallow relative to `min_pool_value_wad` — plausible for long-tail LP markets. All steps are permissionless entrypoints in scope (`controller::supply`, `controller::liquidate`, `controller::clean_bad_debt`, own Aquarius trades). No privileged role, oracle dishonesty, or off-chain dependency is needed; the outage is self-induced by the attacker's own LP withdrawal. Medium severity: conditional on market listing and pool depth, impact bounded to accounts that carry the LP leg, but repeatability makes it a standing shield.

### Recommendation
Do not let one failing collateral leg abort the whole valuation: treat a leg whose price read fails as zero-valued collateral (weighted contribution zero) inside `calculate_account_risk_totals` for liquidation/cleanup paths, so the LP leg cannot shield genuinely collateralized debt. Alternatively/additionally, allow liquidators to exclude specified supply legs from the plan, or raise `min_pool_value_wad` / restrict LP collateral eligibility to pools with liquidity well above the drain threshold.

### Proof of Concept
1. Governance lists Aquarius LP token `LPS` (pool `P`) as collateral in a spoke; `P` is shallow (value slightly above `min_pool_value_wad`).
2. Attacker supplies real collateral `C` and borrows to near-max LTV on account `A`; additionally supplies a dust amount of `LPS` to `A` (supply needs no price check).
3. Attacker waits for `C`'s price to drop so `HF(A) < 1` (or borrows more). Attacker, an LP of `P`, calls Aquarius `withdraw` pulling reserves so `pool_value_wad < min_pool_value_wad`.
4. Any liquidator calls `controller::liquidate(liquidator, A, ...)`. `build_liquidation_plan` → `risk::calculate_account_risk_totals` → strict price of `LPS` → `aquarius::read` returns `Err(InsufficientAquariusLiquidity)` at `providers/aquarius.rs:120-121` → whole call reverts. Same for `clean_bad_debt(A)` and `force_socialize_bad_debt`.
5. Debt accrues unbounded until the attacker (or anyone) refills `P` above the floor — attacker-controlled insolvency window.

### Citations

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L88-93)
```rust
    let price_a = engine::resolve_nested(session, &lp.key_a, depth + 1)?;
    let price_b = engine::resolve_nested(session, &lp.key_b, depth + 1)?;
    let (reserve_a, reserve_b) =
        aquarius_pool_reserves_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
    let total_shares =
        aquarius_total_shares_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
```

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L118-122)
```rust
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
    }
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

**File:** docs/explanation/threat-model.md (L364-364)
```markdown
| DoS.1 | Price outage blocks valuation-dependent actions, including liquidation; fail-closed availability cost. Supply needs no price, so an indebted borrower can add a dust leg of any listed collateral and choose which feed outage shields the account. For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization. |
```
