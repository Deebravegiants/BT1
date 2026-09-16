### Title
Single-block Uniswap V4 pool spot price with only a static-band guard enables manipulated-price intent fills - (File: `sdk/packages/simplex/src/strategies/fx.ts`)

### Summary
For curveless FX pairs, the Simplex filler prices fills directly from a Uniswap V4 pool's current `sqrtPriceX96` (a single spot reading), guarded only by an optional static `referencePrice`/`maxDeviationBps` band. This mirrors the GMX report's bug class exactly: execution price is derived from an unaggregated, single-source spot read rather than a TWAP or liquidity/impact-aware price, so it is economically exploitable by an attacker who can move the pool price (e.g., via a flash-loan swap) within the tolerated band and then submit an intent order that the filler prices off that manipulated spot value.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` selects the most-liquid position for a token and derives its USD price purely from `sdkPool.token0Price`/`token1Price`, computed from the pool's live `sqrtPriceX96` fetched in `UniswapV4LiquidityState.refresh` — one on-chain read, no time-weighting: [1](#0-0) [2](#0-1) 

This value flows into `FXFiller.resolveLegRates` (and `referenceRate`) as the leg's trading rate (`venueRate = 1/venueUsd`), which is then extended linearly across the full order quantity by `computeLegPolicyOutput` — no size or price-impact term is applied on this path: [3](#0-2) 

The only defense is `checkPriceGuard`, which rejects a quote only if it deviates from a static, operator-configured `referencePrice` by more than `maxDeviationBps` — a fixed tolerance band, not a manipulation-cost or liquidity-depth check: [4](#0-3) 

As documented in-repo, the pool's fee tier is read but never applied to the price, and there is no size/impact term at all — "a venue-priced pair that has to swap through its own pool to source inventory pays a fee tier it never quoted against": [5](#0-4) 

This is the same class of risk called out in the external report: pricing execution off spot readings (here, a single DEX pool) instead of a TWAP, with only a coarse failsafe (a static deviation band) rather than a liquidity/impact-aware calculation.

### Impact Explanation
An attacker can move the exotic token's Uniswap V4 pool price within the configured `maxDeviationBps` band (or entirely, if a pair is left unguarded — "omit both to leave the chain unguarded") using a flash-loan-funded swap, then immediately submit a curveless-pair intent order sized against that skewed pool. Because `computeLegPolicyOutput` linearly extends the manipulated mid price with no depth/impact adjustment, the filler pays out at the manipulated rate, transferring value from the solver's on-chain inventory/vault to the attacker. Since these vault balances back real user liquidity (LP positions withdrawn atomically per fill), this is a concrete path to fund loss for the filler/vault operator, reachable from a single unprivileged intent order plus an on-chain swap — matching the "concrete theft of funds" bar.

### Likelihood Explanation
Medium. Exploitability depends on: (a) the pair being curveless/venue-priced (no `bidPricePolicy`/`askPricePolicy`), (b) the guard band being wide enough or unconfigured (`referencePrice`/`maxDeviationBps` are optional — "omit both to leave the chain unguarded"), and (c) sufficient capital/flash-loan access to move the specific pool within the tolerated window relative to the fill size. Thinly liquid exotic-token pools (the documented use case, e.g. cNGN/USDC) are the most susceptible, since moving a low-liquidity pool's price is cheap relative to the fill notional it can extract.

### Recommendation
- Replace or supplement the single spot `sqrtPriceX96` read with a TWAP (e.g., multiple blocks/observations) before using it as the execution rate.
- Make `referencePrice`/`maxDeviationBps` mandatory for venue-priced pairs rather than optional, and/or size the guard band relative to the fill's notional and the pool's actual liquidity depth (impact-aware), not a fixed bps tolerance.
- Apply the pool's fee tier and a price-impact term in `computeLegPolicyOutput` when the fill must itself swap through the same pool to source inventory, instead of extending the mid price linearly.
- Consider capping per-order/per-pair notional relative to on-chain pool depth (an open-interest-style cap) as an additional failsafe.

### Proof of Concept
1. Operator configures a curveless pair (e.g., USDC/EXOTIC) priced via `[vault.uniswapV4]` with no `referencePrice`/`maxDeviationBps`, or a wide band (e.g., 200 bps).
2. Attacker takes a flash loan and swaps against the exotic token's Uniswap V4 pool, moving `sqrtPriceX96` so that `token0Price`/`token1Price` shifts within the tolerated band (or fully, if unguarded) — see `UniswapV4LiquidityState.refresh` reading `getSlot0`/`getLiquidity` live: `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts:139-229`.
3. In the same or an adjacent block, attacker submits an intent order on the curveless pair. `FXFiller.resolveLegRates` calls `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which reads the now-skewed pool price (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-274`), passes `checkPriceGuard` (band not tripped), and prices the leg via `venueRate = 1/venueUsd` (`sdk/packages/simplex/src/strategies/fx.ts:1443-1465`).
4. `computeLegPolicyOutput` extends this manipulated rate linearly across the whole order quantity with no impact term, so the filler withdraws/delivers output tokens at the skewed rate.
5. Attacker unwinds the flash-loan swap, restoring the pool and reverting the skew, having captured the difference between the true market price and the manipulated fill price from the solver's vault.

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L206-239)
```typescript
	async getExoticTokenPrice(chain: string, exoticToken: string): Promise<Decimal | null> {
		const state = this.stateByChain.get(chain)
		if (!state || !state.isHydrated()) return null

		try {
			await state.refresh()
		} catch (err) {
			this.logger.error({ err, chain }, "Failed to refresh state for price query")
			return null
		}

		const tokenLower = exoticToken.toLowerCase()
		let bestPrice: Decimal | null = null
		let bestLiquidity = 0n

		for (const pos of state.allPositions()) {
			if (pos.currency0.toLowerCase() !== tokenLower && pos.currency1.toLowerCase() !== tokenLower) continue
			const sdkPool = state.getSdkPool(pos.tokenId)
			if (!sdkPool) continue

			const result = this.computeDirectPoolPriceUsd(pos, sdkPool, chain)
			if (result && result.exoticToken.toLowerCase() === tokenLower) {
				const poolLiquidity = state.getPoolLiquidity(pos.tokenId)
				if (poolLiquidity > bestLiquidity) {
					bestPrice = result.priceUsd
					bestLiquidity = poolLiquidity
				}
			}
		}

		if (bestPrice) {
			this.logger.debug({ chain, token: tokenLower, priceUsd: bestPrice.toString() }, "Exotic token price computed")
		}
		return bestPrice
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-274)
```typescript
	private computeDirectPoolPriceUsd(
		pos: HydratedV4Position,
		sdkPool: V4Pool,
		chain: string,
	): { exoticToken: string; priceUsd: Decimal } | null {
		const usdc = this.configService.getUsdcAsset(chain).toLowerCase()
		const usdt = this.configService.getUsdtAsset(chain).toLowerCase()
		const c0 = pos.currency0.toLowerCase()
		const c1 = pos.currency1.toLowerCase()

		if (c0 === usdc || c0 === usdt) {
			// currency0 is stable → exotic is currency1
			// token1Price = "token0 per token1" = USD per exotic
			return {
				exoticToken: c1,
				priceUsd: new Decimal(sdkPool.token1Price.toFixed(18)),
			}
		}

		if (c1 === usdc || c1 === usdt) {
			// currency1 is stable → exotic is currency0
			// token0Price = "token1 per token0" = USD per exotic
			return {
				exoticToken: c0,
				priceUsd: new Decimal(sdkPool.token0Price.toFixed(18)),
			}
		}

		return null
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1443-1465)
```typescript
	private async resolveLegRates(
		orderId: string | undefined,
		leg: ResolvedLeg,
		cappedPairNotional: Decimal,
		venueUsdPrice: (chain: string, token1Address: string) => Promise<Decimal | null>,
	): Promise<LegRates | null> {
		// Explicitly configured curves always win — the venue only prices pairs
		// with no curves at all (and never same-token pairs, where a venue quote
		// would just be the asset's own USD price, not a spread).
		const curveless = !leg.pair.bidPricePolicy && !leg.pair.askPricePolicy
		if (curveless && !isSameTokenPair(leg.pair) && USD_STABLE_SYMBOLS.has(normalizeSymbol(leg.pair.token0))) {
			const venueUsd = await venueUsdPrice(leg.token1Chain, leg.token1Address)
			if (venueUsd) {
				// Guard compares the venue's token1-per-USD quote against the static reference.
				if (!this.checkPriceGuard(orderId, leg.token1Chain, new Decimal(1).div(venueUsd))) {
					return null
				}
				// A pool mid is ONE price, not a book: there is no opposite side
				// to report a round-trip margin against. The price guard above is
				// the venue-specific defense.
				const venueRate = new Decimal(1).div(venueUsd)
				return { rate: venueRate, oppositeRate: null, priceSource: "venue" }
			}
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-84)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.

```toml lineNumbers
[vault.uniswapV4]
# referencePrice is the expected cNGN per USD;
# reject if the quote is more than 2% off.
# The two go together — one without the other is rejected.
[[vault.uniswapV4.positions]]
chain           = "EVM-8453"
tokenId         = "2087350"
referencePrice  = "1575"
maxDeviationBps = 200
```
```

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
