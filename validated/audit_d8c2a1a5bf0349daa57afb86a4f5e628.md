### Title
Borrower can shield an underwater account from liquidation by planting an Aquarius LP collateral leg and draining the pool below `min_pool_value_wad` - (File: contracts/price-aggregator/src/providers/aquarius.rs)

### Summary
The DDoS/availability bug class maps onto XOXNO Lending's fail-closed valuation path. An unprivileged borrower can supply a dust amount of an Aquarius LP share token as collateral, borrow against other collateral, and then — as a liquidity provider in that same Aquarius pool — withdraw their own liquidity so the pool value drops below the oracle's configured `min_pool_value_wad`. Every subsequent `liquidate` and `clean_bad_debt` call on the account reverts, because strict price resolution for the account's collateral set fails closed on `InsufficientAquariusLiquidity`. The account's debt keeps accruing while it cannot be liquidated or cleaned, converting a temporary self-inflicted oracle outage into protocol insolvency.

### Finding Description
The price aggregator's Aquarius provider reads pool reserves and total shares live from the pool contract and rejects the observation when the computed pool value is below the configured floor: `if pool_value_wad < lp.min_pool_value_wad { return Err(OracleError::InsufficientAquariusLiquidity) }` [1](#0-0) .

LP-priced markets exist in production configuration, e.g. `AQUAUSDC_LP` on hub 3 with `min_pool_value_wad` of 200,000 USD in WAD [2](#0-1) .

The controller's health-factor and liquidation accounting value every collateral leg of the account with strict prices, and required valuations fail closed: "A missing or unusable required price aborts a valuation-dependent operation, including liquidation" (INV-ORACLE-01) [3](#0-2) . The threat model confirms supply needs no price, so a borrower can plant a dust collateral leg of any listed asset and thereby choose which feed outage shields the account; the same leg blocks bad-debt cleanup and force-socialization (DoS.1) [4](#0-3) .

A live-path test demonstrates the mechanism with a stale feed: planting a 0.001 WBTC dust leg makes `liquidate` and `clean_bad_debt` revert with `PRICE_FEED_STALE` until the price recovers [5](#0-4) . The Aquarius variant is strictly stronger because the attacker controls the outage directly through their own LP withdrawal, rather than waiting for third-party feed staleness.

### Impact Explanation
Protocol insolvency. While the LP price is unpriceable, the account's debt accrues interest and cannot be liquidated (`liquidate` reverts), cannot be cleaned as bad debt (`clean_bad_debt` reverts), and cannot be force-socialized. If the account is already undercollateralized when the outage is triggered, the bad debt persists and grows; on recovery of the oracle the equity may be fully consumed by interest, leaving a write-down borne by suppliers via the supply-index write-down in `seize_positions`/`clean_bad_debt`. The attacker also freezes their own remaining collateral cheaply since the planted leg can be dust-sized — the cost is one LP token deposit plus the LP position, which they can re-add after the fact.

### Likelihood Explanation
Fully reachable by a single unprivileged address:

1. Supply collateral in a normally-priced asset and borrow near the LTV limit (`supply`, `borrow`).
2. Supply a dust amount of an Aquarius LP token listed as collateral in the same hub (`supply` accepts it with no price check).
3. As an LP in the referenced Aquarius pool, call the pool's `withdraw` to pull own liquidity until `fair_lp_price_wad * total_shares < min_pool_value_wad` [1](#0-0) .
4. Every `liquidate(caller, account_id, payments, seize_mode)` on the account reverts because the collateral valuation aborts.

Mainnet `AQUAUSDC_LP` has a 200k USD floor; a pool hovering near the floor makes the attack cheap — the attacker need only own enough LP share fraction to push value under the threshold. Since Aquarius pools are permissionless, any holder of LP shares qualifies. No privileged role, no timing race, no leaked key is required. The only mitigation is that other borrowers' accounts are unaffected — the shield is per-account — and that the attacker must keep the pool drained for the duration, which forfeits their LP yield and exposes them to arbitrage refilling the pool.

### Recommendation
- Price each collateral leg independently in the health-factor/liquidation path and treat an unpriceable dust leg as zero-value rather than aborting the whole account valuation; alternatively, allow `liquidate` to skip collateral legs whose price fails while still repaying debt against priced legs.
- For `clean_bad_debt`/`force_socialize_bad_debt`, do not require live prices for legs that will be written down anyway; the write-down only needs the debt book and the supply index.
- Weight the abort decision by leg value: a leg below the 3-decimal/USD dust floor should be excludable from the required price set, or auto-seizable to revenue.
- Operationally, set `min_pool_value_wad` conservatively below realistic pool value and prefer `AquariusStableLp`/deeper pools for collateral listings so the drain cost exceeds plausible bad-debt gains.

### Proof of Concept
Mirror of `audit_liquidate_and_clean_bricked_by_unpriceable_dust_leg` (tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs:4) with an Aquarius leg instead of a stale Reflector feed:

1. `LendingTest` with USDC debt market and an `AQUAUSDC_LP`-style collateral market whose oracle is a single `AquariusLp` source with `min_pool_value_wad = F`.
2. `t.supply(borrower, "USDC", 10_000)`, `t.supply(borrower, "AQUAUSDC_LP", dust)`, `t.borrow(borrower, "ETH_or_USDC", near-max)`.
3. `MockAquariusPoolClient::set_reserves` (or a real LP withdrawal on a fork) so `price_wad * total_shares / share_unit < F` — simulating the borrower withdrawing their own liquidity.
4. `t.try_liquidate(LIQUIDATOR, borrower, ...)` → `InsufficientAquariusLiquidity` (#235) propagates and the call reverts, identical to the `PRICE_FEED_STALE` revert asserted at lines 36–41.
5. `t.try_clean_bad_debt_by_id(borrower_id)` → same revert.
6. Interest accrues via `update_indexes` (pool accrual does not need prices); the account's true HF keeps falling while no liquidation path succeeds until pool value is restored.

### Citations

**File:** contracts/price-aggregator/src/providers/aquarius.rs (L118-122)
```rust
    let pool_value_wad = try_mul_div_half_up(&env, price_wad, total_shares, share_unit)
        .ok_or(OracleError::InvalidPrice)?;
    if pool_value_wad < lp.min_pool_value_wad {
        return Err(OracleError::InsufficientAquariusLiquidity);
    }
```

**File:** configs/mainnet/markets.json (L1630-1644)
```json
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

**File:** docs/reference/invariants.md (L296-303)
```markdown
### INV-ORACLE-01 — Required valuations fail closed

A missing or unusable required price aborts a valuation-dependent operation,
including liquidation. Strict reads reject resolution errors, stale prices,
source disagreement, nonpositive prices and sanity-band violations.

Diagnostic `quotes` can retain a nonzero candidate with `valid=false`. That
candidate is not accepted for valuation.
```

**File:** docs/explanation/threat-model.md (L364-365)
```markdown
| DoS.1 | Price outage blocks valuation-dependent actions, including liquidation; fail-closed availability cost. Supply needs no price, so an indebted borrower can add a dust leg of any listed collateral and choose which feed outage shields the account. For an Aquarius LP leg, liquidity providers can cause that outage by withdrawing pool value below `min_pool_value_wad`. The same leg blocks bad-debt cleanup and force-socialization. |
| DoS.2 | Selected paused debt or no_seize collateral blocks liquidation; distinct flag policies matter. |
```

**File:** tests/test-harness/tests/controller/audit_liquidate_and_clean_stale_leg.rs (L36-41)
```rust
    let liq = t.try_liquidate(LIQUIDATOR, borrower, "ETH", 1.0);
    test_harness::assert_contract_error(liq, errors::PRICE_FEED_STALE);

    let clean = t.try_clean_bad_debt_by_id(borrower_id);
    test_harness::assert_contract_error(clean, errors::PRICE_FEED_STALE);

```
