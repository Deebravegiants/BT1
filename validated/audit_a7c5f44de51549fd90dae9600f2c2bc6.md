### Title
Reserve inflation of Aquarius LP pools inflates LP-share collateral price and enables over-borrowing - ([File: contracts/price-aggregator/src/providers/aquarius.rs](contracts/price-aggregator/src/providers/aquarius.rs))

### Summary
The price-aggregator prices Aquarius LP share tokens (usable as collateral) by reading the pool's live reserves via `get_reserves()` inside the same transaction, then deriving a fair-value share price from those reserves and external leg prices. The formula is invariant to swaps (for a constant-product pool, `reserve_a * reserve_b` is constant), but it is not invariant to reserve *inflation*: an unprivileged attacker can transfer tokens directly to the Aquarius pool contract — an action explicitly reachable by any address — inflating one leg's reserve without minting LP shares, which raises the computed per-share price. The manipulated price is consumed by the controller's Context-cached strict pricing for collateral valuation, health factor, and `min_borrow_collateral_usd`, so an LP holder can borrow far more than their collateral is worth and default, leaving the pool with bad debt. This is the direct analog of the `slot0` spot-price manipulation finding: spot pool state read in the same transaction as the critical accounting decision.

### Finding Description
`aquarius::read` in `contracts/price-aggregator/src/providers/aquarius.rs` fetches reserves and total shares synchronously at lines 90–93:

```rust
let (reserve_a, reserve_b) =
    aquarius_pool_reserves_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
let total_shares =
    aquarius_total_shares_call(&env, &lp.pool).ok_or(OracleError::NoLastPrice)?;
```

`aquarius_pool_reserves_call` is a direct cross-contract call to `AquariusPoolClient::try_get_reserves()` (`common/src/oracle/providers/aquarius.rs:45-57`), the pool's current spot reserves — the same "most recent data point" class as Uniswap `slot0`.

For constant-product pools, `fair_lp_price_wad` (`common/src/oracle/lp.rs:57-87`) computes `2 * sqrt(value_a * value_b) * WAD / share_supply`. Since `value_i = reserve_i * price_i / 10^decimals`, inflating `reserve_a` by a factor `k` multiplies the LP price by `sqrt(k)` — doubling one reserve via a direct token transfer raises the share price ~41%.

For stable pools, `fair_stable_lp_price_wad` (`common/src/oracle/lp_stable.rs:80-110`) computes `D * min(price_a, price_b) / supply`, where `D` grows roughly proportionally with total reserves — direct inflation scales the LP price nearly linearly, an even stronger lever.

The mitigations present do not close this:
- The swap-resistance test (`lp_stable.rs:179-198`) only covers trades along the invariant, not exogenous reserve additions.
- `min_pool_value_wad` is a floor, not a ceiling — inflation only raises pool value.
- Sanity bands (`min_sanity_price_wad`/`max_sanity_price_wad`, e.g. `engine.rs:142-146`) are wide (production configs show bands spanning ~2-5x the mid price), leaving ample room for profitable manipulation within the band.
- Dual-leg tolerance only helps if a *second independent source* exists; production configs (e.g. `configs/ops/mainnet/c55e9f73...json`) use a single `AquariusLp` source with zero-width tolerance, so there is no anchor leg to deviate against.

### Impact Explanation
Theft of user funds / protocol insolvency. An attacker holding LP shares of an Aquarius pool (which is a listed collateral asset) executes in one transaction:

1. Deposit LP shares as collateral via `supply`.
2. Directly transfer a large amount of `token_a` to the Aquarius pool address (plain token `transfer`, no pool interaction needed — pool `get_reserves` reads balances).
3. Call `borrow` (or `multiply`/`flash_position`) — the controller resolves the LP price through the aggregator, sees the inflated `reserve_a`, computes an inflated LP price, and the attacker's collateral value and `min_borrow_collateral_usd` check pass at the manipulated level.
4. Withdraw borrowed assets and abandon the position; the LP collateral is worth less than the debt, and `clean_bad_debt`/`recapitalize` socialize the loss to suppliers.

The attacker recovers most of the donated tokens by redeeming their LP shares afterward (donations pro-rata to all LP holders), so the net cost is the fraction of the pool they don't own plus swap fees — small if they dominate LP supply, which is plausible for thin LP markets (`min_pool_value_wad` floors as low as ~$2.5k in testnet configs).

### Likelihood Explanation
All steps are unprivileged single-transaction actions in scope: own token transfers to the pool, own `supply`/`borrow`. No oracle honesty assumption is violated — the manipulation is against on-chain pool state the contract itself reads, not against Reflector/RedStone feeds. Profitability requires the inflated borrow to exceed the unrecovered donation share; with concentrated LP ownership this is straightforward.

### Recommendation
- Use manipulation-resistant reserve readings: prefer pool-tracked reserve state over raw token balances if Aquarius exposes `get_reserves` distinct from balances, or price LP shares via the pool's own `virtual_price`/invariant where it cannot be moved by donations.
- Add a sanity *ceiling* check on reserve-derived pool value relative to a recent snapshot, or require a second independent source leg (tolerance cross-check) for every LP-backed collateral market so a manipulated single source trips `UnsafePriceNotAllowed` (`engine.rs:136-138`).
- Tighten `max_sanity_price_wad` bands for LP collateral markets to bound maximum inflation-induced over-borrow to below the liquidation threshold margin.

### Proof of Concept
```
1. Attacker acquires ≥99% of Aquarius pool P's LP shares (pool holds token_a/token_b,
   external leg prices pa, pb from Reflector).
2. supply(attacker, hub, lp_share_token, amount)        // collateral = shares
3. TokenClient(token_a).transfer(attacker, P, X)         // reserve_a := reserve_a + X,
                                                        // no shares minted
4. borrow(attacker, hub, token_out, max_amount)
   // controller → price-aggregator → aquarius::read → get_reserves() sees
   // inflated reserve_a → fair price = 2*sqrt((a+X)*pa * b*pb)/supply
   // → collateral USD inflated ~sqrt(1 + X/a) → borrow passes HF check.
5. redeem LP shares to recover ~attacker_share * X of the donation;
   abandon under-collateralized debt.
```
Relevant code: `contracts/price-aggregator/src/providers/aquarius.rs:90-119` (spot reserves → fair price → only `min_pool_value_wad` floor), `common/src/oracle/lp.rs:72-86` (`sqrt(va*vb)` pricing), `common/src/oracle/providers/aquarius.rs:45-57` (raw `get_reserves` read), `contracts/price-aggregator/src/engine.rs:126-148` (only staleness/deviation/sanity-band rejection).