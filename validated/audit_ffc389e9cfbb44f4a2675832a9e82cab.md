### Title
Unprivileged reserve donation inflates sole-source Aquarius LP fair-value oracle, enabling undercollateralized borrows - (File: contracts/price-aggregator/src/providers/aquarius.rs)

### Summary

The external report's bug class is "an on-chain price that an unprivileged trader can move cheaply is used for collateral/debt accounting." XOXNO Lending does not consume a Uniswap TWAP, but it exposes the same class through its `AquariusLp` price source: an LP share is valued as `2 * sqrt(value_a * value_b) / total_shares` from the pool's **live reserves** (`fair_lp_price_wad`, common/src/oracle/lp.rs:57-86), read on demand in `aquarius::read` (contracts/price-aggregator/src/providers/aquarius.rs:88-120). LP oracles are forced to be sole-source and are exempt from the dual-leg tolerance and smoothing checks — the sanity band is the only backstop, and it may span a 10x range (`validate_asset_oracle`, contracts/price-aggregator/src/admin.rs:157-197; `MAX_LP_SANITY_BAND_BPS = 8182`, common/src/oracle/observation.rs:40). A user can push the fair value up by transferring token A or B directly into the pool, raising `value_a * value_b` without changing `total_shares`.

### Finding Description

`aquarius::read` resolves both leg prices from external feeds, then calls `aquarius_pool_reserves_call` for the current reserve balances and feeds them into `fair_lp_price_wad` (aquarius.rs:90-114). For a constant-product pool the fair value is proportional to `sqrt(reserve_a * price_a * reserve_b * price_b)`. An attacker who holds the pool's LP shares can donate token A to the pool: if `value_a` grows by factor `k`, the reported LP price grows by `sqrt(k)`, and the donation remains recoverable by redeeming the LP shares afterward — the inflation is therefore low-cost or free for a dominant LP holder. The inflated price is only bounded by the oracle's `min_sanity_price_wad`/`max_sanity_price_wad` band, which mainnet configs set ~10x wide (configs/ops/mainnet/621677611ec5...json:43-44) and which validation caps at a 10x range for LP sources (admin.rs:157-163, validation.rs:201-208). The controller prices collateral with these strict Context-cached prices for health factor and borrow solvency (docs/reference/invariants.md:320-357).

The reachable path for a single unprivileged address: acquire a large fraction of the configured pool's LP shares (or create the position over time), supply the LP token as collateral via `supply`, transfer tokens directly to the Aquarius pool contract to inflate `reserve_a`, then call `borrow` against the inflated collateral value, and finally redeem the LP shares to recover the donation. All steps use only allowed actions (direct token transfers to a venue, own trades on Aquarius, controller supply/borrow).

### Impact Explanation

The borrow leaves the protocol with debt exceeding the true collateral value. After the attacker withdraws the donated liquidity, the LP price reverts and the position is deeply underwater; liquidation cannot recover the shortfall, producing protocol insolvency / theft of pool funds proportional to `(sqrt(k) - 1) * LTV * collateral` within the sanity band.

### Likelihood Explanation

Requires the configured Aquarius pool to be small/concentrated enough that one account can hold a dominant share of LP supply — realistic for the long-tail LP tokens this oracle type is designed to list — plus capital equal to a multiple of one leg's value (recoverable in proportion to pool share owned). The sanity band caps the achievable multiplier at ~10x, but even a modest inflation produces bad debt. No privileged access, timing dependence, or oracle dishonesty is needed, which keeps this in the Medium range rather than High.

### Recommendation

Add a manipulation dampener for `AquariusLp` reads, e.g.: value reserves with a TWAP/historical reserve snapshot or a virtual-price-style bound rather than raw live reserves; tighten `MAX_LP_SANITY_BAND_BPS` for sole-source LP oracles; or require a second independent feed as a deviation check instead of exempting LP oracles from tolerance/smoothing in `validate_asset_oracle`.

### Proof of Concept

1. Governance configures `PriceKey::Token(LP)` with a single `AquariusLp` source on pool P and a ~10x sanity band (as in `configs/ops/mainnet/621677611ec58736619d7f7df4bc00387ecd5d9b50e6ceac47ce2e902e8a1f58.json`).
2. Attacker accumulates ≥ f of pool P's LP shares and supplies them to the lending pool via `supply` as collateral in a spoke where LP is listed with LTV L.
3. Attacker transfers `D` of token A directly to P. `reserve_a` becomes `a + D`, so `fair_lp_price_wad` returns `price * sqrt(1 + D*price_a/value_a)` — e.g. `D ≈ 8 * leg value` gives ~3x price (common/src/oracle/lp.rs:72-84), inside the 10x band.
4. `aquarius::read` returns the inflated observation; `pool_value_wad` exceeds `min_pool_value_wad`, so no `InsufficientAquariusLiquidity` error (aquarius.rs:115-122).
5. Attacker calls `borrow`, drawing assets up to the inflated LTV-weighted collateral value, then redeems LP shares from P to recover `D`.
6. The LP price reverts; the position's real collateral is far below debt. `liquidate`/`clean_bad_debt` can only socialize the loss — protocol insolvency.