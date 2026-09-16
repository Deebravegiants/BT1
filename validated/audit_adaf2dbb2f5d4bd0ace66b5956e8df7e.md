### Title
Simplex FXFiller sizes fills and LP withdrawals from an unmitigated Uniswap V4 spot price, letting a flash-manipulated pool tick extract solver funds - (File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts)

### Summary
`UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd` derives an exotic token's USD price directly from the live Uniswap V4 pool's current tick/`sqrtPriceX96` (`sdkPool.token0Price`/`token1Price`), with no TWAP. `FXFiller.referenceRate`/trade pricing in `sdk/packages/simplex/src/strategies/fx.ts` uses this spot quote both to price fills for curveless ("venue-priced") pairs and to size confirmation depth, and the funding planner uses it to decide how much LP liquidity to withdraw from the solver's own Uniswap V4 positions to cover a fill (`docs/content/developers/evm/simplex/pricing.mdx`). The only defense is an optional, static `checkPriceGuard` band, which the documentation explicitly says operators may leave unconfigured ("omit both to leave the chain unguarded"), and which — per `sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md` — checks deviation from a static reference, not execution cost or pool depth. This mirrors the reported bug class: using a manipulable spot price instead of a TWAP/robust oracle.

### Finding Description
- `UniswapV4FundingPlanner.getExoticTokenPrice` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`) picks the highest-liquidity pool position and calls `computeDirectPoolPriceUsd`. [1](#0-0) 
- `computeDirectPoolPriceUsd` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:246-276`) returns the pool's raw mid price from `sdkPool.token0Price`/`token1Price`, i.e., the current spot price derived from `sqrtPriceX96`, without TWAP or size/impact adjustment. [2](#0-1) 
- The pricing flow doc confirms this: the pool's spot mid is used linearly across the whole priced quantity, and `checkPriceGuard` — the only defense — checks deviation from a static reference, not execution cost. [3](#0-2) 
- `FXFiller.referenceRate` (`sdk/packages/simplex/src/strategies/fx.ts:1339-1364`) inverts this venue USD quote into the trading rate for a curveless pair and applies `checkPriceGuard` — but only when a `referencePrice`/`maxDeviationBps` pair is actually configured for that chain. [4](#0-3) 
- `checkPriceGuard` (`sdk/packages/simplex/src/strategies/fx.ts:422-448`) returns `true` (pass, unguarded) whenever no guard is configured for the chain. [5](#0-4) 
- The operator docs explicitly document this as optional and warn about manipulation risk while leaving it off by default: "Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote... The two fields must be set together; omit both to leave the chain unguarded." [6](#0-5) 
- When positions are configured, the pool literally is the sole price oracle for the pair, with margin coming only from `order.fees`: "The pool acts as the price oracle instead of a static curve." [7](#0-6) 

### Impact Explanation
An attacker who can move a Uniswap V4 pool's tick before submitting (or having a colluding solver fill) an intent order can force the FXFiller to price a curveless/venue pair at a manipulated spot rate. Because the pair has no bid/ask curve of its own (pool pricing is single-sided) and the guard is optional/off by default, the solver can be induced to (a) fill an order at an unfavorable rate, and (b) withdraw more of its Uniswap V4 LP inventory than the fair market rate justifies (the withdrawal/funding sizing in `pricing.mdx`'s Uniswap V4 LP funding section is driven by the same spot price). This is a direct extraction of solver-held funds (LP positions funding fills) — a concrete theft vector against the intent-fulfillment/solver funds path, exactly the class of bug identified in the external report (spot price usable for price manipulation via flash-loan-style liquidity moves).

### Likelihood Explanation
Likelihood is contingent on operator configuration: if `referencePrice`/`maxDeviationBps` are configured tightly, the guard blocks large deviations (though it still only checks against a static reference, not real-time execution cost/pool depth, so cleverly bounded manipulation within the allowed band is not caught). If the guard is left unconfigured — which the documentation presents as a normal, supported configuration ("omit both to leave the chain unguarded") — there is no protection at all, and any attacker capable of a same-block large swap against the referenced Uniswap V4 pool (a standard flash-loan/large-swap technique) can manipulate the price used for that fill.

### Recommendation
Do not price curveless/venue pairs from the pool's instantaneous `sqrtPriceX96`/tick alone. Use a Uniswap V4 TWAP (time-weighted average, ideally over multiple blocks) or an external oracle (e.g., Chainlink) as the primary reference, and make `referencePrice`/`maxDeviationBps` mandatory (not optional) for any pair relying on pool-based pricing, additionally bounding by real-time pool depth/impact rather than a purely static band.

### Proof of Concept
1. Operator configures a `[vault.uniswapV4]` position for an exotic/stable pair without setting `referencePrice`/`maxDeviationBps` (a documented, supported configuration).
2. Attacker performs a large swap (optionally via flash loan) against that Uniswap V4 pool in the same block, moving its current tick/`sqrtPriceX96` far from fair value.
3. Attacker (or a colluding filler) submits/observes an intent order that FXFiller's `resolveLegRates`/`referenceRate` prices via `getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which reads the manipulated spot price with `checkPriceGuard` returning `true` unconditionally (no guard configured).
4. FXFiller fills the order and/or withdraws Uniswap V4 LP liquidity at the manipulated rate, transferring value from the solver's escrowed funds to the attacker; attacker reverses the initial swap, netting profit at the solver's expense.

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-276)
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L1-22)
```markdown
# Venue pricing (Uniswap V4 funded pairs)

Verified 2026-08-19.

```
resolveLegRates(...)
  curveless pair && token0 is a USD stable
    -> venuePriceMemo() -> getVenueUsdPrice(chain, token1)
         -> UniswapV4FundingPlanner.getExoticTokenPrice
              picks the position with the largest pool liquidity
              -> computeDirectPoolPriceUsd -> sdkPool.token0Price / token1Price
    -> checkPriceGuard(...)   reject if outside maxDeviationBps of the static reference
    -> rate = 1 / venueUsd
  otherwise -> the pair's ask/bid curve at the leg's notional
```

`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L40-46)
```text
## Pool-Based Pricing

When **`[vault.uniswapV4]`** lists at least one position, cross-asset pairs without curves derive bid/ask prices from **Uniswap V4 pool state** (current tick). The pool acts as the price oracle instead of a static curve. Note this yields a **single** price used in both directions — a venue-priced pair has no bid/ask spread of its own, so its margin comes from `order.fees` alone.

With Uniswap V4 positions configured, you can **omit** `bidPriceCurve` and `askPriceCurve` on the pair. Pool pricing requires the pair's `token0` to be a USD stablecoin, and same-token pairs always need their curve. The optional **`spreadBps`** field (basis points) sets the slippage tolerance for on-chain LP redemptions; defaults to `50` (0.50%).

Uniswap V4 venue pricing uses pools that pair the exotic token with **USDC or USDT** (addresses from your chain config). When multiple positions exist for the same exotic token on a chain, the most-liquid qualifying pool's price is used.
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
```
