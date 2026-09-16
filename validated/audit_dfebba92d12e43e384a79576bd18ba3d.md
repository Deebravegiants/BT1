Based on my investigation, I have enough to produce the final analog analysis.

### Title
Simplex FXFiller prices intents off a manipulable Uniswap V4 spot price with an optional, band-only guard - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
The MBUToken exploit drained funds because a contract valued/settled a trade using a live, single-transaction-manipulable AMM output (`swapExactTokensForTokensSupportingFeeOnTransferTokens`) with no protection against a flash-manipulated price. Hyperbridge's Simplex intent solver (`FXFiller`) has the analogous pattern: for "venue-priced" (curveless) pairs it derives the price it will fill an intent at directly from a Uniswap V4 pool's current spot price (`sqrtPriceX96`/tick), and the only defense — a static `referencePrice`/`maxDeviationBps` band — is optional and, even when configured, does not protect against a same-block spot-price manipulation that stays inside the configured band.

### Finding Description
`resolveLegRates` in `sdk/packages/simplex/src/strategies/fx.ts` prices a curveless pair whose `token0` is a USD stablecoin from `venueUsdPrice(leg.token1Chain, leg.token1Address)`, which resolves to `UniswapV4FundingPlanner.getExoticTokenPrice` [1](#0-0) . That function reads the current pool state via `StateView.getSlot0` and computes the price directly from `sdkPool.token0Price`/`token1Price`, i.e. the pool's current spot price, for the most-liquid qualifying pool [2](#0-1) [3](#0-2) .

The only sanity check is `checkPriceGuard`, which compares the venue quote to a static, operator-configured `referencePrice` within `maxDeviationBps` [4](#0-3) . Per the docs and code, this guard is entirely optional — a chain with no `referencePrice`/`maxDeviationBps` is left completely unguarded [5](#0-4) [6](#0-5) . Even when set, the guard only bounds deviation from a static number and provides no protection against a manipulated spot price that stays within the configured band, nor against a price moved and reverted within a single block/transaction bundle (a flash-loan/flash-swap TWAP-less manipulation), exactly the attack pattern used in the referenced MBUToken exploit against a swap-derived valuation. The project's own internal documentation confirms this is a spot-only, unmitigated read: "`computeDirectPoolPriceUsd` returns the raw pool mid derived from `sqrtPriceX96`... `checkPriceGuard` is the only defense on this path, and it checks deviation from a static reference, not execution cost" [7](#0-6) .

This priced rate directly drives what the solver will accept/deliver for a real user-submitted intent (`quotePhantomFill`/fill sizing), and also feeds `referenceRate`, which sizes the order's USD notional used for reorg/confirmation-depth policy — so a manipulated quote both mis-prices the fill and under-sizes the required confirmations [8](#0-7) .

### Impact Explanation
An attacker who can move the exotic-token/USDC(T) Uniswap V4 pool's spot price within a single transaction/block (a swap large enough relative to the pool's concentrated liquidity, which per the docs can be a "thin pool") can submit or bid on an intent that the solver fills at the manipulated rate. Since venue pricing yields a single price used in both directions with no bid/ask spread of its own, the solver can be made to deliver more exotic tokens (or accept less stablecoin) than fair value, directly draining solver-controlled funds/liquidity positions — concrete theft of solver funds, analogous to the BUSD drained in the MBUToken incident. If no guard is configured (which the code explicitly permits), there is zero on-chain-price sanity check at all.

### Likelihood Explanation
Requires only a single submitted intent/order plus (optionally) a manipulative swap against the referenced Uniswap V4 pool in the same block — no privileged access, governance, or off-chain compromise needed. Thin, exotic-token pools (the exact use case this feature targets, e.g. cNGN) are the most susceptible to this manipulation, and the guard being optional and static-band-only means even guarded deployments only bound — not eliminate — the exploitable range.

### Recommendation
Do not price fills directly off a single spot read (`getSlot0`) of a Uniswap V4 pool. Use a manipulation-resistant price source (e.g., a TWAP over multiple blocks, or a Uniswap V4 truncated/geomean oracle) for venue pricing, or require cross-referencing against an independent oracle. Make `referencePrice`/`maxDeviationBps` mandatory rather than optional for venue-priced pairs, and additionally bound the maximum size fillable in a single block against pool depth so a price stays valid only for size the pool can actually absorb without a large single-tx swap.

### Proof of Concept
Conceptually mirrors the referenced MBUToken PoC: within one bundled/atomic transaction sequence, (1) execute a large swap against the thin exotic/USDC(T) Uniswap V4 pool the solver references to move `sqrtPriceX96` favorably, (2) have the solver's `FXFiller.resolveLegRates`/`getExoticTokenPrice` read that manipulated spot price and fill an intent at the skewed rate (staying inside `maxDeviationBps` if a guard is configured, or unguarded entirely), (3) reverse the initial swap, netting the attacker the spread taken from the solver's inventory — reproducible against the `getExoticTokenPrice` / `checkPriceGuard` logic cited above using a forked-mainnet test similar to `sdk/packages/simplex/src/tests/strategies/fx.mainnet.test.ts`.

### Citations

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1339-1364)
```typescript
	/**
	 * Minimum-size reference rate (token1 per token0) for a leg's pair: the
	 * bid curve at 0 (the side token1-input legs trade at), falling back to the
	 * ask curve, then the live venue quote for venue-priced pairs.
	 */
	private async referenceRate(
		leg: ResolvedLeg,
		venueUsdPrice: (chain: string, token1Address: string) => Promise<Decimal | null>,
	): Promise<Decimal | null> {
		const policy = leg.pair.bidPricePolicy ?? leg.pair.askPricePolicy
		if (policy) {
			const rate = policy.getPrice(new Decimal(0))
			return rate.gt(0) ? rate : null
		}
		// Venue-priced pair: token0 is USD-stable (constructor invariant), so the
		// venue's USD-per-token1 quote inverts straight into token1-per-token0.
		const venueUsd = await venueUsdPrice(leg.token1Chain, leg.token1Address)
		if (!venueUsd) return null
		const venueRate = new Decimal(1).div(venueUsd)
		// Same guard as trade pricing: this rate sizes the order's USD notional
		// for confirmation depth, and a manipulated pool understating the value
		// would shrink the reorg protection — the exact attack the guard exists
		// to stop. Refusing to size skips the order, consistent with pricing.
		if (!this.checkPriceGuard(undefined, leg.token1Chain, venueRate)) return null
		return venueRate
	}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1443-1466)
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
		}
```

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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
```

**File:** sdk/packages/simplex/src/config/filler-toml.ts (L27-35)
```typescript
	/**
	 * Optional price guard. When set (alongside `maxDeviationBps`), the filler rejects
	 * orders whenever the pool quote on this chain drifts more than `maxDeviationBps`
	 * from this static reference price (exotic per USD, same units as the bid/ask curves).
	 * Guards against a manipulated, stale, or thin pool.
	 */
	referencePrice?: string
	/** Tolerance in basis points for the price guard. Required when `referencePrice` is set. */
	maxDeviationBps?: number
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
