### Title
Donation-based inflation of constant-product LP fair price enables under-collateralized borrows - ([File: common/src/oracle/lp.rs](common/src/oracle/lp.rs))

### Summary
The `AquariusLp` oracle source derives an LP share's price from the pool's *live* reserves via `fair_lp_price_wad` = `2 * sqrt(value_a * value_b) / total_shares`. The geometric mean neutralizes reserve *skews* (rebalancing swaps), but not reserve *additions*: a direct token transfer to the Aquarius pool raises `value_a` without minting shares, inflating the LP price by `sqrt(1 + d/reserve_a)`. An unprivileged attacker holding LP collateral can flash-fund such a donation, supply/borrow against the inflated collateral value in a single transaction, and leave the pool with bad debt once reserves normalize.

### Finding Description
- `contracts/price-aggregator/src/providers/aquarius.rs:90-114` reads `aquarius_pool_reserves_call` and `aquarius_total_shares_call` fresh on every `read`, then feeds them into `fair_lp_price_wad`. There is no smoothing, TWAP, or sanity check that reserves are consistent with any prior state.
- `common/src/oracle/lp.rs:57-86` computes `total_value = 2 * sqrt(value_a * value_b)` where `value_a = reserve_a * price_a`. Donating `d` units of token A to the pool multiplies the LP price by `sqrt((r_a + d)/r_a)`.
- Attack path (all unprivileged entrypoints):
  1. Acquire Aquarius LP shares for a constant-product pool configured as collateral (e.g., `XLMAQUA_LP`, `min_pool_value_wad` = 500 XLM-equivalent — `configs/mainnet/markets.json:1575-1605`), supply them via `controller::supply`.
  2. Take `controller::flash_loan` (or `flash_position`) in token A.
  3. Directly transfer token A to the Aquarius pool contract (plain `token.transfer` — no mint, so `total_shares` is unchanged).
  4. Call `controller::borrow` for token B (USDC/XLM) sized against the inflated `Context`-cached collateral price; the `min_sanity_price_wad`/`max_sanity_price_wad` band for these LP markets spans ~10x (`5356670329052813` to `53566703290528136`), leaving ample room to inflate.
  5. Repay the flash loan inside the same transaction (donation capital is flash-funded; flash fee is the only cost).
  6. After the transaction, reserves normalize but the debt remains; `liquidate`/`clean_bad_debt` can only recover the true LP value → bad-debt write-down.
- Profit is roughly `LTV * (f - 1) * LP_value` minus flash/swap costs, where `f` is the inflation factor. Doubling the price costs a donation of `3 * reserve_a`, which is flash-capital, not burned capital — the donation remains in the pool backing the attacker's own LP, partially recoverable by redeeming LP afterward (redeeming returns a pro-rata share of the enlarged reserves, clawing back `attacker_share * donation`).

### Impact Explanation
Theft of user funds / protocol insolvency: borrowed assets exit the protocol backed by LP collateral whose real value is far below the recorded debt. When positions are liquidated or written down via `clean_bad_debt`, the supply-index write-down socializes the loss across suppliers. Impact is bounded by the borrowable liquidity of debt markets against LP-collateral hubs and by the sanity bands' upper bound on price.

### Likelihood Explanation
Requires the attacker to hold meaningful LP collateral (to mint/keep it without inflating `total_shares`, it must be acquired before the attack transaction) and flash-scale capital equal to a few times the target pool's leg reserve — both feasible since `min_pool_value_wad` floors are modest (200k–1M USD WAD in mainnet configs) and the pool's own flash facility funds the donation atomically. The Aquarius venues that set reserves are public (anyone can transfer tokens to the pool), and `RequireDisjoint` independence plus `tolerance` of 0 bps give no second source to cross-check the manipulated reserve snapshot for single-source LP markets.

### Recommendation
- Validate that a pool's reserves are consistent with its share supply *without* relying on raw balances: for constant-product pools use the `k`-invariant relative to a stored/last-seen `k` per unit of total supply, or compute LP value as `2 * sqrt(price_a * price_b * k_implied_by_supply)` rather than from instantaneous reserves.
- Alternatively, read reserves from Aquarius's own accounting state if it distinguishes accrued fees/donations, or require multi-source pricing (e.g., pair `AquariusLp` with an independent source so `tolerance`/`RequireDisjoint` actually binds) for LP collateral markets.
- Tighten `min/max_sanity_price_wad` bands on LP markets so a single-transaction reserve jump pushes the observation outside the band and fails closed.

### Proof of Concept
1. Governance configures an `AquariusLp` oracle for pool P (tokens A/B); market lists P-share as collateral with `ltv = L`.
2. Attacker: acquires `S` LP shares over time (not atomic-minted), calls `controller.supply(S shares)`.
3. Attack tx:
   - `controller.flash_loan(D)` of token A, `D ≈ 3 * reserve_a(P)`.
   - `token(A).transfer(attacker → P, D)` — `aquarius_pool_reserves_call` now reports `4 * reserve_a`; `total_shares` unchanged.
   - Aggregator `read` → `fair_lp_price_wad` returns `2x` prior price (within `max_sanity_price_wad`).
   - `controller.borrow(B_amount)` where `B_amount ≈ L * 2 * value(S)` of token B; send B to attacker-controlled wallet.
   - Repay flash loan `D + fee`.
4. Post-tx, LP price reverts. `liquidate`/`clean_bad_debt` recovers only `value(S)`; the excess `≈ L * value(S)` becomes bad debt written down against suppliers. Attacker optionally redeems LP to recapture a pro-rata slice of the donated `D`, lowering net cost further.