### Title
Aquarius LP fair-value oracle is single-transaction reserve-donation manipulable, enabling over-collateralized borrow against inflated LP shares — (`contracts/price-aggregator/src/providers/aquarius.rs`)

### Summary
The BonqDAO bug class — an unprivileged actor pushing an instant, self-influenced price into the valuation path to borrow inflated collateral — maps onto XOXNO Lending's Aquarius LP pricing source. `providers::aquarius::read` derives the collateral value of an LP share token from the pool's *current* reserves (`aquarius_pool_reserves_call`) and total shares in the same ledger as the controller's borrow. An attacker can inflate `reserve_a`/`reserve_b` by transferring tokens directly to the Aquarius pool (donation without minting shares), raising `fair_lp_price_wad`, then call `controller.borrow` against their LP collateral while the price is inflated, and recover most of the donation afterward via `remove_liquidity` since they hold the shares.

### Finding Description
`read` at `contracts/price-aggregator/src/providers/aquarius.rs:90-114` reads live pool state:

```rust
let (reserve_a, reserve_b) = aquarius_pool_reserves_call(&env, &lp.pool)...
let total_shares = aquarius_total_shares_call(&env, &lp.pool)...
let price_wad = fair_lp_price_wad(&env, &leg_a, &leg_b, &supply)?  // or fair_stable_lp_price_wad
```

Both `fair_lp_price_wad` (constant product: `2·sqrt(r_a·r_b·p_a·p_b)/supply`) and `fair_stable_lp_price_wad` grow monotonically in the raw reserves. Neither function measures a time-weighted or liquidity-weighted reserve — it is an instantaneous spot read, exactly the "instant price feed" failure mode of BonqDAO.

The mitigations present do not close this:

- The tolerance/midpoint check in `engine.rs` only compares the oracle's configured legs against each other (`Outcome::partial`, `within_tolerance_band`). If the Aquarius LP is the sole source (`Legs::One`, `engine.rs:88-100`), there is no second leg to disagree with — the manipulated price is accepted verbatim provided it clears the sanity band (`engine.rs:142-146`). Even for dual-source oracles, `IndependencePolicy::AllowShared` explicitly permits both legs to reference the same provider; two Aquarius reads of the same pool inflate identically, so the midpoint stays manipulated and within tolerance.
- `min_pool_value_wad` (`aquarius.rs:118-122`) is a *lower* bound on pool value — donation only pushes the pool further above it.
- `attest`/`bound_tokens`/`decimals_match` validate pool identity, not reserve integrity.

The controller side consumes this price immediately: `fetch_prices` (`contracts/controller/src/external/price_aggregator.rs:18-29`) pulls the resolved WAD price into the `Context`, and borrow's final solvency gate values collateral at that snapshot — so a supply-LP-then-borrow sequence inside one transaction uses the donated-reserve price.

Attack sequence reachable by any unprivileged address:

1. Acquire a large share fraction of the target Aquarius pool (add liquidity — price per share is unchanged by proportional additions, so this is near cost-free and reversible).
2. `supply` LP shares to the controller as collateral.
3. Direct token `transfer` of token A (and/or B) to the pool address — reserves rise, total shares do not.
4. `borrow` other assets up to the inflated LTV-weighted collateral value.
5. `remove_liquidity` on Aquarius, recovering the donated amount scaled by the attacker's share fraction.

Net cost is roughly `(1 − share_fraction) × donation + pool fees`, while net gain is the excess borrow that becomes protocol bad debt. This is strictly the BonqDAO shape: cheap temporary price inflation → max borrow → unwind → insolvency.

The deflate-and-liquidate half of the BonqDAO attack does *not* port — removing liquidity moves reserves and shares pro-rata and does not lower the per-share fair price, so user positions cannot be pushed under water this way. The inflation/borrow/insolvency half does.

### Impact Explanation
Theft of user funds / protocol insolvency: the attacker exits with borrowed assets backed by collateral whose true value is a fraction of what was borrowed, leaving the pool under-collateralized. `clean_bad_debt` writes the deficit down against the supply index, socializing the loss across suppliers of the borrowed asset. Severity: High.

### Likelihood Explanation
Requires a collateral market whose oracle resolves (at least one leg, or both shared legs) through `FeedSource::Aquarius*`. Such sources are configured in `configs/mainnet/markets.json` (multiple Aquarius entries), though I did not fully verify which markets use them as sole-source or their LTV/sanity-band widths. Manipulation must stay inside `min_sanity_price_wad`/`max_sanity_price_wad` per `engine.rs:142-146`; the achievable inflation scales as `sqrt` of the donation for constant-product pools, so wide bands plus high LTV on an LP collateral market make this profitable. No privileged access, leaked key, or off-chain dependency is needed — only the attacker's own Aquarius trades/transfers and the public `supply`/`borrow` entrypoints.

### Recommendation
- Reject or heavily penalize instantaneous reserve reads: require LP sources to be dual-legged against an independent non-Aquarius anchor (not `AllowShared` with the same pool), and tighten the tolerance band so a donated-reserve midpoint fails the deviation check.
- Cap Aquarius-sourced collateral LTV conservatively and set narrow `min_sanity_price_wad`/`max_sanity_price_wad` bands bounding plausible per-share NAV drift.
- Consider pricing LP shares from a manipulation-resistant per-share NAV (e.g., cumulative/virtual-price accounting) rather than raw spot reserves.

### Proof of Concept
1. Deploy/identify pool `P` on Aquarius whose share token `S` is a listed collateral market with oracle source `AquariusLpSource{ pool: P, ... }` (single source, or dual legs sharing `P` via `IndependencePolicy::AllowShared`).
2. Attacker adds liquidity to `P` until holding fraction `f ≈ 1` of shares; receives `S`.
3. `controller.supply(S)` as collateral.
4. `token_a.transfer(P, D)` with `D` chosen so `fair_lp_price_wad` rises to just under `max_sanity_price_wad` (inflation factor ≈ `sqrt((r_a + D)/r_a)` for constant product).
5. `controller.borrow(borrow_asset, amount)` — solvency gate values the `S` collateral at the inflated price fetched via `fetch_prices`.
6. `P.remove_liquidity` recovers `≈ f·D` plus the attacker's original liquidity.
7. The attacker defaults; the position's true collateral value is below the debt, and `clean_bad_debt` writes the shortfall into the supply index.

Unknown/uncertain: I could not confirm the exact per-market oracle wiring (single-source vs dual independent legs) or LTV/sanity-band values for Aquarius-backed markets in the deployed configs; the finding is conditional on an Aquarius-sourced oracle valuing a borrowable collateral market.