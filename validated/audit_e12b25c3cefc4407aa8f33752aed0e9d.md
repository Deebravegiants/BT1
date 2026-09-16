I have sufficient evidence to establish the analog. The Simplex FX filler's venue pricing derives directly from a single-block Uniswap V4 pool spot price with only an optional static-reference deviation guard — architecturally the same weakness as the reported Uniswap V3 TWAP-manipulation bug (spot/short-window price with no execution-cost/liquidity-depth defense).### Title
Simplex venue pricing derives fill rates from unmitigated single-block Uniswap V4 spot price, allowing flash-manipulation of solver fills - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
The reported issue is spot/short-TWAP Uniswap V3 price manipulation used by a lending/collateral protocol. Hyperbridge's Simplex intent-solver has a structurally analogous mechanism: for "curveless" trading pairs, `FXFiller` prices fills directly from a Uniswap V4 pool's instantaneous `sqrtPriceX96`/current tick (no TWAP at all), with the only defense being an *optional* static-reference deviation guard.

### Finding Description
When a Simplex trading pair has no configured bid/ask curves and `token0` is a USD stablecoin, `resolveLegRates` prices the leg entirely from a live Uniswap V4 pool quote: [1](#0-0) 

That quote comes from `UniswapV4FundingPlanner.getExoticTokenPrice`, which reads the pool's current `slot0` (`sqrtPriceX96`, `tick`) on-demand and returns the raw mid-price with no time-weighting whatsoever — it is a pure spot price, more manipulable than even the 36-second short TWAP criticized in the report: [2](#0-1) [3](#0-2) 

The only safeguard is `checkPriceGuard`, which compares the venue quote to a **static, operator-configured `referencePrice`** within `maxDeviationBps` — not a liquidity-depth or execution-cost check, and it is explicitly optional ("omit both to leave the chain unguarded"): [4](#0-3) [5](#0-4) 

Internal documentation confirms the design gap explicitly: the guard only checks deviation from a static reference, not execution cost, and the pool's own fee tier is never applied to the quoted price: [6](#0-5) 

This same unguarded venue rate is also reused to size the order's USD notional for confirmation-depth decisions via `referenceRate`, so manipulating the pool can also shrink reorg protection on a large fill: [7](#0-6) 

### Impact Explanation
An attacker can move the exotic/stable Uniswap V4 pool's tick within a single block (flash swap, no flash loan needed for a thin pool) and then have an intent order filled — or a phantom bid priced — off that manipulated tick. Because the guard is a static reference (if configured at all) rather than a manipulation-resistant TWAP, and because it only bounds *price*, not execution cost or fee, this can:
- Make the solver overpay in the exotic token relative to what it can actually source on-chain (theft of solver funds via a favorable synthetic price that the solver then can't unwind at that rate), or
- Make the solver underpay a legitimate user filling through venue-priced pairs, and
- Distort the confirmation-depth (`referenceRate`) sizing, reducing reorg protection on large fills.

This is High impact (direct loss of solver funds / incorrect settlement) with Low-Medium likelihood, since it requires either an unguarded chain configuration (`referencePrice`/`maxDeviationBps` omitted — explicitly supported and documented as valid) or a guard band wide enough / pool thin enough to still allow profitable manipulation.

### Likelihood Explanation
Likelihood is Low-Medium: it requires a curveless, venue-priced pair (an explicitly supported, documented configuration) with either no price guard configured, or a thin/low-liquidity exotic/stable Uniswap V4 pool where a guard band still allows a profitable deviation — directly mirroring the low-liquidity, short-TWAP conditions the original report identifies as the manipulation precondition. Unlike the original finding, there isn't even a TWAP window here — the price is read fresh via `getSlot0` on every quote, making it strictly easier to manipulate than the reported TWAP-based oracle.

### Recommendation
- Replace the instantaneous `slot0`/current-tick read in `UniswapV4FundingPlanner.computeDirectPoolPriceUsd`/`getExoticTokenPrice` with a TWAP derived from the pool's oracle observations (or a comparable manipulation-resistant price source), sized to the pool's realistic liquidity and typical fill size.
- Make the price guard (`referencePrice`/`maxDeviationBps`) mandatory rather than optional for any venue-priced pair, and/or require a minimum pool liquidity threshold before trusting venue pricing.
- Incorporate the pool's fee tier and price-impact into `computeDirectPoolPriceUsd`/`computeLegPolicyOutput` rather than pricing the whole notional at the raw mid, per the noted gap in `venue-pricing-uniswap-v4-funded-pairs.md`.
- Apply the same hardened price source to `referenceRate`'s confirmation-depth sizing, since it currently shares the same unguarded/spot-price dependency.

### Proof of Concept
Conceptual PoC (mirrors the reported report's structure, adapted to this codebase):
1. Configure (or find deployed) a curveless Simplex pair (`token0` = USDC/USDT, `token1` = exotic token) funded via `[vault.uniswapV4]`, with the pool having relatively low liquidity, and either no `referencePrice`/`maxDeviationBps` guard configured, or one wide enough to admit a profitable deviation.
2. In a single block/transaction, swap through the exotic/stable Uniswap V4 pool to shift `sqrtPriceX96`/`tick` materially.
3. Immediately submit (or have relayed) an intent order for that pair; the Simplex `FXFiller.resolveLegRates` → `UniswapV4FundingPlanner.getExoticTokenPrice` path prices/fills the order off the manipulated spot tick (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`), and `checkPriceGuard` (`sdk/packages/simplex/src/strategies/fx.ts:422-448`) either passes (unguarded chain) or is bypassed within its static band.
4. Reverse the initial swap; net cost is only the pool fee/slippage on the manipulation trade, while the profit is the difference between the manipulated fill price and the pool's unmanipulated fair value — the same economics demonstrated in the original report's Foundry PoC, just applied to Simplex's fill path instead of a lending protocol's liquidation/close path.

Note: I was unable to independently confirm the deployed default configuration (whether `referencePrice`/`maxDeviationBps` is set for currently live venue-priced pairs, e.g. the cNGN/USDC pool referenced in the tests), since that is operator/runtime configuration data not present in the indexed codebase. This affects real-world likelihood but not the validity of the code-level analog.

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
