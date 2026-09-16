### Title
Unguarded Uniswap V4 spot-price oracle enables manipulated fills and reorg-protection bypass in Simplex FX solver - (File: `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
Simplex's `FXFiller` can price cross-asset intent legs directly from a Uniswap V4 pool's current tick/`sqrtPriceX96` instead of a static curve. This spot price is read with no TWAP, no size/impact adjustment, and is protected only by an *optional*, per-chain `referencePrice`/`maxDeviationBps` price guard. When the guard is not configured for a chain — which is the default state, since (unlike confirmation policies) there are no built-in guard defaults — the solver trusts the raw pool price unconditionally, mirroring the BonqDAO root cause: a manipulable spot-price feed consumed without a dispute/TWAP window or mandatory bound check.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` scans the solver's configured V4 positions and returns the raw mid-price of the most-liquid pool, computed from `sqrtPriceX96` via `computeDirectPoolPriceUsd`: [1](#0-0) [2](#0-1) 

This price feeds two critical decisions in `FXFiller`:
1. **Trade pricing** (`resolveLegRates`): the venue quote is inverted into the fill rate and applied linearly across the entire order notional, with no size/impact term. [3](#0-2) 
2. **Confirmation-depth (reorg protection) sizing** (`referenceRate`): the same venue quote sizes the order's USD notional that determines how many block confirmations are required before the solver commits capital. [4](#0-3) 

The only defense is `checkPriceGuard`, which is a no-op whenever no guard is configured for the chain (`if (!guard || guard.reference.lte(0)) return true`): [5](#0-4) 

The guard is declared explicitly optional in configuration and docs, and there is no startup-time enforcement requiring it when Uniswap V4 pool pricing is enabled: [6](#0-5) [7](#0-6) 

This is structurally the same bug class as BonqDAO: a single, spot-readable, unauthenticated price source (there, TellorFlex submitted-value with no dispute wait; here, a Uniswap V4 pool tick) is consumed directly to make a high-value financial decision (there, BEUR minting/liquidation collateral value; here, fill rate and reorg-protection depth) without a mandatory bound, TWAP, or dispute window — only an opt-in static reference band that operators may leave unset.

### Impact Explanation
An attacker who can move the price of a thin Uniswap V4 pool the solver has funded (via a flash-loan-backed swap or by trading against low-liquidity concentrated positions) can, within a single block:
- Trick `resolveLegRates` into filling an intent order at a manipulated rate, extracting solver capital directly (same-shape loss as BonqDAO's over-borrow against an inflated collateral price).
- Trick `referenceRate`/`getOrderUsdValue` into under-reporting the order's USD notional, collapsing the required confirmation depth and letting the solver commit capital on a source-chain event that gets reorged out — the exact "shrink the reorg protection" scenario the code comment calls out.
Both outcomes are concrete theft of solver-held funds, reachable purely from a submitted intent order plus an on-chain pool-price manipulation transaction — no privileged role required.

### Likelihood Explanation
Likelihood depends entirely on operator configuration: any Simplex operator running `[vault.uniswapV4]` pool-based pricing without setting `referencePrice`/`maxDeviationBps` for every chain with a position is fully exposed, and nothing in the codebase forces that configuration to exist. Because the guard is opt-in per chain and per position rather than mandatory, misconfiguration (the likely default state for a new deployment) is sufficient to expose the solver, matching BonqDAO's "the cost of manipulating the oracle was far below the attacker's profit" dynamic whenever the backing pool has moderate-to-low liquidity relative to a solver's inventory.

### Recommendation
- Make the Uniswap V4 price guard mandatory (fail startup validation) whenever `[vault.uniswapV4]` pool-based pricing is configured for a pair, rather than optional.
- Replace or supplement the raw `sqrtPriceX96` spot read with a TWAP/observation-window price, and add a minimum-liquidity/size-impact check before trusting `computeDirectPoolPriceUsd`.
- Apply the same guard to the confirmation-depth `referenceRate` path unconditionally (today it reuses `checkPriceGuard`, but only when a guard happens to be configured), so reorg-protection sizing can never be shrunk by an unguarded venue quote.

### Proof of Concept
1. Operator configures a `[vault.uniswapV4]` position for an exotic/USDC pair with no `referencePrice`/`maxDeviationBps` (permitted by `UniswapV4PositionToml`, see `sdk/packages/simplex/src/config/filler-toml.ts:23-36`).
2. Attacker takes a flash loan and swaps heavily against that same low-liquidity V4 pool, moving `sqrtPriceX96` far from fair value.
3. Attacker (or an accomplice) submits a cross-chain intent order matching the manipulated pair. `FXFiller.resolveLegRates` calls `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice`, which reads the manipulated pool state and returns the skewed price with `checkPriceGuard` passing trivially (no guard configured) — `sdk/packages/simplex/src/strategies/fx.ts:1453-1465`.
4. The solver fills the order at the manipulated rate, or under-sizes confirmation depth via `referenceRate` (`sdk/packages/simplex/src/strategies/fx.ts:1355-1363`), and the attacker profits at the solver's expense — or reorgs the source-chain order after the solver already committed the destination-chain fill.
5. Attacker reverses the pool manipulation in the same or a following block, restoring the pool to its prior state while keeping the extracted profit.

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-275)
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
	}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L428-448)
```typescript
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1344-1364)
```typescript
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

**File:** sdk/packages/simplex/src/config/filler-toml.ts (L23-36)
```typescript
/** TOML row for a Uniswap V4 position; only chain + tokenId required. */
export interface UniswapV4PositionToml {
	chain: string
	tokenId: string // bigint as string in TOML
	/**
	 * Optional price guard. When set (alongside `maxDeviationBps`), the filler rejects
	 * orders whenever the pool quote on this chain drifts more than `maxDeviationBps`
	 * from this static reference price (exotic per USD, same units as the bid/ask curves).
	 * Guards against a manipulated, stale, or thin pool.
	 */
	referencePrice?: string
	/** Tolerance in basis points for the price guard. Required when `referencePrice` is set. */
	maxDeviationBps?: number
}
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
```
