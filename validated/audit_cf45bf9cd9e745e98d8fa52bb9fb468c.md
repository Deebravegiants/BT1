### Title
Uniswap V4 venue pricing in the Simplex intent filler uses raw spot price with no TWAP, exposing solver funds to flash-manipulated fills - (File: `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
The Simplex intent-filler prices "curveless" trading pairs directly off a Uniswap V4 pool's instantaneous `sqrtPriceX96`, with no time-weighted averaging at all — an even weaker construction than the referenced Perp `getPositionValue` bug, which at least used a (too-short) 15-second TWAP. The only mitigation is an *optional* static reference-price guard that can be omitted entirely, and even when present only bounds deviation against a hardcoded reference rather than any robust, manipulation-resistant price source.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` iterates the hydrated LP positions and calls `computeDirectPoolPriceUsd`, which derives the USD price straight from the SDK `V4Pool`'s `token0Price`/`token1Price`, themselves computed from the live `sqrtPriceX96` fetched via `StateView.getSlot0` in `UniswapV4LiquidityState.refresh`: [1](#0-0) 

This price feeds `FXFiller.resolveLegRates`, which uses it directly as the fill rate for curveless pairs (`rate = 1 / venueUsd`): [2](#0-1) 

The only defense is `checkPriceGuard`, which compares the live quote against a **static** `referencePrice` within `maxDeviationBps` — and this guard is explicitly optional per the docs and validation code: [3](#0-2) [4](#0-3) 

An internal design note in the repo itself flags this exact gap: `computeDirectPoolPriceUsd` returns "the raw pool mid derived from `sqrtPriceX96`" with "`checkPriceGuard` [as] the only defense on this path, and it checks deviation from a static reference, not execution cost." [5](#0-4) 

This is the same bug class as the referenced report: a critical financial calculation (here, the fill rate paid out of solver-held funds for an intent order) is derived from a pool price sampled over an unsafe (zero-length) window, rather than a manipulation-resistant TWAP.

### Impact Explanation
Any unprivileged actor able to submit an ISMP/IntentGatewayV2 order routed to a curveless, Uniswap V4-priced pair can first move the referenced pool's spot price (e.g., via a swap or flash loan) and then have the FXFiller fill the order at the manipulated rate. Because the guard is optional (config explicitly allows "omit both to leave the chain unguarded") and, even when present, only bounds against a stale static reference rather than any freshness-resistant averaging, an attacker can extract value from the solver's vault — a direct loss of solver-held funds during order settlement, which is the class of concrete theft the assessment scope calls for ("intents escrow and bids").

### Likelihood Explanation
Medium likelihood: exploitation requires (a) sufficient capital or a flash loan to move the target pool's price, and (b) either an unguarded chain configuration or a guard band wide enough to still yield profitable mispricing. Given the guard is opt-in per the shipped documentation and example config (`filler-config-example.toml` shows it commented out by default), some/most deployments are plausibly unguarded, and the guard's static-reference design does not itself track legitimate price movement, requiring operational upkeep to stay effective.

### Recommendation
Replace or supplement the instantaneous `slot0`/`sqrtPriceX96` read with a Uniswap V4 TWAP (observation-based) price over a meaningfully long window (minutes, not one block), and make the price guard mandatory (not optional) for any pair relying on venue pricing, rather than allowing chains to be "left unguarded." Consider also bounding fills by execution cost/impact (fee tier, size) rather than only comparing the mid-price against a static reference, consistent with the gaps already flagged in `venue-pricing-uniswap-v4-funded-pairs.md`.

### Proof of Concept
1. Configure (or observe) a chain in `[vault.uniswapV4]` without `referencePrice`/`maxDeviationBps` (permitted per `filler-toml.ts` validation, which only requires both-or-neither, not that they be set) — see the commented-out defaults in `filler-config-example.toml` lines 281-292.
2. Attacker swaps in the exotic/USDC(T) Uniswap V4 pool used for pricing to push `slot0.sqrtPriceX96` away from fair value.
3. Attacker (or a colluding party) submits an IntentGatewayV2 order on the curveless pair.
4. `FXFiller.resolveLegRates` → `getExoticTokenPrice` → `computeDirectPoolPriceUsd` reads the manipulated spot price with no TWAP smoothing and no active guard (or a guard whose static reference still tolerates the manipulated quote within `maxDeviationBps`).
5. The filler executes the fill at the manipulated rate, transferring solver-held funds at an unfavorable exchange rate, realizing attacker profit at the solver's expense. [6](#0-5)

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L206-240)
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
	}
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-272)
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
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L422-448)
```typescript
	/**
	 * Validates a live venue quote against the static reference price for the chain.
	 * Returns true (pass) when no guard is configured, or no reference exists for the
	 * chain. Returns false when the quote (token1 per USD) deviates from the reference
	 * by more than `maxDeviationBps`, in which case the order must not be filled.
	 */
	private checkPriceGuard(orderId: string | undefined, chain: string, venueToken1PerUsd: Decimal): boolean {
		const guard = this.priceGuard?.get(chain)
		if (!guard || guard.reference.lte(0)) return true

		const deviationBps = venueToken1PerUsd.minus(guard.reference).abs().div(guard.reference).mul(10000)
		if (deviationBps.gt(guard.maxDeviationBps)) {
			this.logger.warn(
				{
					orderId,
					chain,
					venuePrice: venueToken1PerUsd.toString(),
					referencePrice: guard.reference.toString(),
					deviationBps: deviationBps.toFixed(2),
					maxDeviationBps: guard.maxDeviationBps,
				},
				"Rejecting order: Uniswap venue quote outside price-guard band",
			)
			return false
		}
		return true
	}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1449-1465)
```typescript
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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
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
