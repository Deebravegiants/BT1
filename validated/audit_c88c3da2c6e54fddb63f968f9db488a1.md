### Title
Stale pre-callback oracle price reused for solvency checks after `flash_position` receiver callback — (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
`process_flash_position` snapshots oracle prices into `Context` via `prefetch_strategy_prices` before it invokes the caller-controlled `execute_flash_position` receiver. All post-callback accounting — collateral deposit valuation, health-factor and minimum-collateral checks in `strategy_finalize` — reads only the cached `token_prices` map. For collateral priced through an `AquariusLp` oracle source, the fair price is derived live from the pool's `get_reserves`/`get_total_shares`, so the receiver can move the reported price during the callback (in particular, inflate it by donating one leg's token into the pool, since `fair_lp_price_wad` scales with `sqrt(value_a * value_b)`). The settlement then values the deposited LP collateral at the stale, higher pre-callback price.

### Finding Description
The RISC-V GP bug class is "a trusted base value pinned once, then used to resolve offsets against a region whose contents shifted underneath." Here the pinned base is the `Context` price cache:

- `contracts/controller/src/strategies/flash_position.rs:117` calls `prefetch_strategy_prices(&mut cache, &account, &extra_assets)`, filling `cache.token_prices` for the debt asset and all declared collateral assets before the callback.
- `Context::fetch_prices` (`contracts/controller/src/context.rs:142-151`) skips assets already cached, and `cached_price` (`context.rs:154-160`) never re-reads the aggregator. The same `cache` is threaded through `process_deposit` (line 146) and `strategy_finalize` (line 153), so every risk calculation after the callback uses the pre-callback snapshot.
- Between those two points, `invoke_receiver` (line 131) executes arbitrary attacker code inside `with_flash_guard`. The flash guard blocks re-entry into controller/pool verbs, but not calls to the Aquarius pool that backs the oracle.
- `contracts/price-aggregator/src/providers/aquarius.rs:90-114` derives the LP share price from live `get_reserves()`/`get_total_shares()` and `fair_lp_price_wad` (`common/src/oracle/lp.rs:57-87`), which is proportional to `sqrt(reserve_a * price_a * reserve_b * price_b)`. A receiver that holds most of the pool's LP shares can donate a large amount of one leg's token during the callback, permanently raising the pool's reported fair value; because the price was already memoized, the protocol values the freshly deposited LP collateral at the pre-donation level — or, symmetrically, a donation executed before the call inflates the cached price and the position's real value collapses when the donation is economically recouped. Either way the check uses a price that no longer matches the collateral's realizable value.

The debt leg is minted and forwarded before the callback (`mint_and_forward`, line 123), so the attacker walks away with the debt token while the account retains only overvalued collateral.

### Impact Explanation
The attacker opens a `Multiply`/`Long`/`Short` position whose LP collateral is priced above its true post-callback value, passes `enforce_post_pool_solvency` and the health-factor check on the stale price, keeps the forwarded debt tokens, and abandons the position. Once the real price applies, the account is deeply undercollateralized; liquidation cannot recover the minted debt, producing protocol bad debt and insolvency borne by suppliers. This is theft of user funds / protocol insolvency, reachable by any unprivileged address with a WASM receiver contract and sufficient liquidity share in an Aquarius pool used as an oracle source.

### Likelihood Explanation
Requires a listed collateral whose oracle resolves through `AquariusLp` (such configs exist in `configs/mainnet/markets.json`) and a debt market with `is_flashloanable` set. The manipulation cost scales with `sqrt` of the donated fraction, so it is cheapest when the attacker already dominates pool share supply; sanity bands (`min_sanity_price_wad`/`max_sanity_price_wad`, e.g. a ~10x band for AQUAUSDC) leave ample room for a profitable overstatement, and `min_pool_value_wad` does not limit upward skew. The attack is atomic, single-transaction, and needs no privileged role.

### Recommendation
Do not memoize oracle prices across the receiver callback. Either re-fetch prices for collateral and debt assets after `invoke_receiver` returns (invalidating `cache.token_prices` entries for assets priced from manipulable on-chain reserves), or run the post-callback `process_deposit`/`strategy_finalize` risk checks against a fresh `Context`. Alternatively, treat reserve-derived sources as volatile and re-resolve them at check time inside the price aggregator rather than trusting a session memo.

### Proof of Concept
1. Attacker acquires/controls a large share of an Aquarius constant-product pool whose LP token is a listed, collateralizable asset (`AquariusLp` oracle), and deploys a receiver implementing `execute_flash_position`.
2. Before calling `flash_position`, the attacker donates tokens of leg A into the pool, inflating `fair_lp_price_wad` by `sqrt(1 + donation/value_a)` — e.g., donating ~56% of leg A's value inflates the LP price ~25%, within the configured sanity band.
3. Attacker calls `controller.flash_position` with the debt asset = a flashloanable market, `collaterals = [(LP_hub_asset, min)]`. `prefetch_strategy_prices` caches the inflated LP price.
4. In the callback, the receiver transfers the (overvalued) LP collateral to the controller and keeps the forwarded debt tokens.
5. `process_deposit` and `strategy_finalize` value the LP at the cached inflated price; HF ≥ 1 and the position persists.
6. The LP's realizable value is below the debt. The account is abandoned; liquidation seizes only the real LP value, leaving bad debt in the pool.