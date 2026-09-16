### Title
Uniswap V4 venue pricing uses manipulable instantaneous pool spot price with no TWAP or impact protection - (File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts)

### Summary
`UniswapV4FundingPlanner.getExoticTokenPrice` / `computeDirectPoolPriceUsd` prices curveless FX pairs directly from a Uniswap V4 position's current tick (`sqrtPool.token0Price`/`token1Price`), exactly the same "instantaneous reserve/price" pattern flagged in the external report's `IchiLpOracle.getPrice`. Both derive a tradeable price straight from live, single-block AMM state with no time-weighting, making the price atomically manipulable with a swap immediately before consumption.

### Finding Description
When a pair has no configured bid/ask curves and `token0` is a USD stable, `resolveLegRates` in `sdk/packages/simplex/src/strategies/fx.ts` prices the leg from `venueUsdPrice`, which resolves to `UniswapV4FundingPlanner.getExoticTokenPrice`: [1](#0-0) 

That function reads the pool's *current* price directly off the hydrated `V4Pool` object (`sdkPool.token0Price` / `token1Price`, derived from `sqrtPriceX96`), with no TWAP oracle, no minimum liquidity/depth check, and no price-impact term: [2](#0-1) 

The project's own flow documentation confirms this is a known-raw spot price with only a static-band guard as mitigation: [3](#0-2) 

The only defense is `checkPriceGuard`, which compares the quote against a **static, operator-configured** `referencePrice` within `maxDeviationBps` — and it is entirely optional (`priceGuard` can be left unset per chain), and even when set it only rejects fills *outside* the band; it does not detect or prevent manipulation *inside* the band, nor does it protect the pool-based sizing used elsewhere: [4](#0-3) 

This mirrors the reported Ichi LP bug precisely: a spot on-chain price (reserves/tick) computed from live state is used directly as the trusted price for a financial decision, with no manipulation-resistant sourcing (TWAP, multiple-block observation, or liquidity-weighted fair pricing).

### Impact Explanation
The Uniswap V4 position funding a pair is the solver's own liquidity, priced by this function both for (a) trade pricing on curveless pairs (`resolveLegRates`) and (b) confirmation-depth sizing (`referenceRate`), which the code explicitly calls out as security-relevant: an attacker who transiently depresses the venue price can shrink the USD notional used for reorg/confirmation-depth protection, weakening finality guarantees for that order — the exact attack the guard comment describes: [5](#0-4) 

An attacker able to move the pool's instantaneous price (e.g., via a large same-block/adjacent-block swap against the exotic-token pool, potentially flash-loan funded, since there is no size or impact term applied to the mid) can (1) get the solver to fill an intent order at a mispriced rate, extracting value from the solver's LP-backed inventory, and/or (2) shrink the computed USD notional used for confirmation-depth sizing, reducing the reorg protection applied to a large fill. Either outcome is a concrete value-extraction / control-bypass vector reachable by any unprivileged actor who can submit a swap and a cross-chain intent order.

### Likelihood Explanation
Likelihood is Medium-High for chains/pairs where `[vault.uniswapV4]` price guard is left unconfigured (explicitly supported/optional per docs), since there is then zero manipulation resistance. Even where a guard is configured, an attacker can still manipulate the price within `maxDeviationBps` (a static tolerance, not derived from pool depth or volatility) to skew fills in their favor across many orders, or push confirmation-depth sizing artificially low. The precondition is simply enough capital/liquidity access to move the specific V4 pool tick — no privileged role is required.

### Recommendation
Replace the raw current-tick price with a manipulation-resistant source: use Uniswap V4's built-in TWAP/observation oracle over a meaningful window instead of `sqrtPriceX96`-derived spot price, and/or require the price guard (`referencePrice`/`maxDeviationBps`) to be mandatory rather than optional for any pair relying on venue pricing. Additionally, incorporate pool depth/liquidity and an execution-cost/impact term into `computeDirectPoolPriceUsd` so a shallow or freshly-manipulated pool cannot dictate the fill or confirmation-sizing price, consistent with the "fair LP/price" remediation recommended for the original Ichi LP oracle bug.

### Proof of Concept
1. Attacker identifies an exotic/USD pair configured with `[vault.uniswapV4]` venue pricing and either no `referencePrice`/`maxDeviationBps` guard, or a guard with a loose `maxDeviationBps`.
2. Attacker swaps a large amount against the exotic token's Uniswap V4 pool (optionally flash-loan funded) to move `sqrtPriceX96` and thus `sdkPool.token0Price`/`token1Price` favorably.
3. Attacker immediately submits (or has pre-submitted) a cross-chain intent order matching that pair; the Simplex solver's `FXFiller.resolveLegRates` prices the fill via `getExoticTokenPrice` → `computeDirectPoolPriceUsd`, picking up the manipulated spot price (guard either absent or satisfied because deviation stays within the static band).
4. The solver fills the order at the skewed rate and/or applies undersized confirmation-depth protection (`referenceRate`), and/or withdraws liquidity via `planWithdrawalForToken` at the distorted rate, letting the attacker extract value from the solver's LP-backed inventory or exploit reduced finality protection on a large fill.
5. Attacker reverses the pool swap, realizing profit at the solver's expense.

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1356-1364)
```typescript
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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L206-275)
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

	/**
	 * Computes the USD price of the non-stable token in a pool.
	 * Returns null if neither currency is USDC/USDT on this chain.
	 */
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
