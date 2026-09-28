### Title
Borrower self-inflicts an Aquarius LP price outage to make an underwater account permanently unliquidatable - ([File: contracts/price-aggregator/src/providers/aquarius.rs](contracts/price-aggregator/src/providers/aquarius.rs))

### Summary
A borrower can plant a dust-sized supply leg in an Aquarius LP market, then withdraw their own liquidity from the underlying Aquarius pool to push its value below `min_pool_value_wad`. The LP price then fails with `InsufficientAquariusLiquidity`, and because every valuation-dependent path resolves strict prices for all of the account's legs, `liquidate`, `clean_bad_debt`, and `force_socialize_bad_debt` all revert for that account for as long as the attacker keeps the pool drained. Debt accrues unimpeded into insolvency.

### Finding Description
`supply` accepts new collateral legs without resolving their price, so an unprivileged caller can attach a dust leg of any listed asset to an indebted account at will; the threat model notes supply needs no price and a borrower can therefore "choose which feed outage shields the account" [1](#0-0) . The oracle fails closed: any missing or unusable required price aborts liquidation, bad-debt cleanup, and even owner-only force-socialization [2](#0-1) [3](#0-2) .

For Aquarius LP collateral, the price read rejects the whole feed whenever the computed pool value is below `min_pool_value_wad` [4](#0-3) . Pool value is reserve-driven, so anyone holding LP shares — including the attacker themselves — can drop it below the floor by withdrawing liquidity on Aquarius, an action explicitly within the unprivileged surface. Mainnet LP listings carry this floor (e.g., `AQUAUSDC_LP` with `min_pool_value_wad` of 200,000 USD WAD) [5](#0-4) . Operations alerting acknowledges the impact: "Under 1.0x the LP price is rejected and accounts holding this leg become unliquidatable" [6](#0-5) .

The same fail-closed shape is proven in tests with a stale leg: a planted dust supply leg makes `liquidate` and `clean_bad_debt` revert while a healthy twin account liquidates fine, and the same call succeeds once the price recovers [7](#0-6) .

### Impact Explanation
The attacker gains a toggleable liquidation shield on their own indebted account. While the pool is drained, no liquidator, no permissionless `clean_bad_debt`, and not even the owner-gated `force_socialize_bad_debt` can touch the position, because all of them compute `calculate_account_risk_totals` over strict prices for every leg [8](#0-7) . Interest keeps accruing, so the account can be driven deep into insolvency on the attacker's schedule; when finally cleaned up, the debt is written down against supplier indexes, socializing the loss to suppliers — protocol insolvency borne by users. The attacker retains the option to restore the price at any time by re-adding liquidity (or letting any other LP do so), making this a controlled, reversible DoS rather than a one-way sacrifice.

### Likelihood Explanation
Requires the attacker to be an LP in an Aquarius pool backing a listed collateral market and to post dust of that LP token as a supply leg — all unprivileged, in-scope actions (`supply`, own Aquarius withdrawals). Cost is the dust leg plus temporarily parking liquidity elsewhere. Thinner pools closer to their `min_pool_value_wad` floor (some mainnet listings sit within ~25% of it, hence the dedicated alert) make the drain cheap. Partial mitigation exists: any liquidity provider can heal the price, so the attacker must be willing to dominate or race re-adds; and the shield only helps while the account still has collateral worth shielding, since once insolvent the attacker gains nothing except delaying the write-down.

### Recommendation
- On bad-debt cleanup and liquidation, treat an `InsufficientAquariusLiquidity` (and generally unusable) price for a *collateral* leg as zero-value evidence for that leg's eligibility instead of aborting the whole operation — e.g., price unpriceable supply legs at zero for the HF/collateral-total computation so the dust leg cannot shield real collateral.
- Alternatively, add a liquidation/cleanup path that seizes only priceable legs and writes down debt, skipping unpriceable legs.
- Keep LP collateral leg admission stricter: require the leg to meet the minimum-collateral floor with a *current* valid price at supply time for accounts that have or will have debt.
- Operationally, keep `min_pool_value_wad` floors low relative to realistic pool drainability and monitor the near-floor alert.

### Proof of Concept
1. Attacker provides liquidity to the Aquarius pool behind listed LP collateral `L`, receiving LP shares.
2. Attacker supplies real collateral `C` and borrows to near the limit; then calls `supply(attacker, L, dust)` — succeeds without a price read.
3. Market moves (or attacker waits for accrual) until `HF < 1`.
4. Attacker withdraws their liquidity from the Aquarius pool so `pool_value_wad < min_pool_value_wad`; `aquarius::read` now returns `InsufficientAquariusLiquidity`.
5. Any `liquidate(liquidator, attacker, ...)` call reverts resolving the LP leg's strict price; `clean_bad_debt` and `force_socialize_bad_debt` revert identically.
6. Debt accrues to insolvency under the shield; when eventually cleaned (after the attacker or another LP restores pool value), supplier indexes absorb the write-down.

### Citations

**File:** docs/explanation/threat-model.md (L364-365)
```markdown
| DoS.1 | Price outage blocks valuation-dependent actions, including liquidation; fail-closed availability cost. Supply needs no price, so an indebted borrower can add a dust leg of any listed collateral and choose which feed outage shields the account. For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization. |
| DoS.2 | Selected paused debt or no_seize collateral blocks liquidation; distinct flag policies matter. |
```

**File:** docs/reference/invariants.md (L296-304)
```markdown
### INV-ORACLE-01 — Required valuations fail closed

A missing or unusable required price aborts a valuation-dependent operation,
including liquidation. Strict reads reject resolution errors, stale prices,
source disagreement, nonpositive prices and sanity-band violations.

Diagnostic `quotes` can retain a nonzero candidate with `valid=false`. That
candidate is not accepted for valuation.

```

**File:** docs/reference/runbooks/force-socialize-bad-debt.md (L34-35)
```markdown
3. Check every position's price status. Missing or invalid required prices
   prevent cleanup; listing flags and global pause do not waive pricing.
```

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L118-122)
```rust
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
    }
```

**File:** configs/mainnet/markets.json (L1622-1643)
```json
      "name": "AQUAUSDC_LP",
      "hub_id": 3,
      "asset_address": "CDOY7ILRR7PDGLBXZUPSENB6XOET77PR2JY3HXDGQS3TS4T764OYBUGO",
      "oracle": {
        "asset_decimals": 7,
        "max_price_stale_seconds": 57600,
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

**File:** tests/test-harness/tests/controller/audit_supply_stale_shield.rs (L26-65)
```rust
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
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L222-235)
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
```
