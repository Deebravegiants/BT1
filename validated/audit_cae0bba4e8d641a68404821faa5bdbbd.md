### Title
Uniswap V4 spot-price venue pricing has no TWAP/manipulation resistance, letting a single flash-loan-manipulated pool drain solver funds through mispriced fills - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
The Channels Finance report describes a Compound v2 fork drained because its price oracle read a manipulable, unprotected on-chain spot value used directly to value collateral/borrow capacity. The closest reachable analog in this codebase is FXFiller's Uniswap V4 "venue pricing" path: `UniswapV4FundingPlanner.computeDirectPoolPriceUsd` derives the USD price of the exotic token straight from the pool's current `sqrtPriceX96`-derived mid (`sdkPool.token0Price`/`token1Price`), a single-block spot price with no TWAP, and this price is used to size and price actual order fills.

### Finding Description
`getExoticTokenPrice` iterates the solver's configured V4 positions and, for each pool containing the exotic token, calls `computeDirectPoolPriceUsd`, which returns the pool's instantaneous mid price with no manipulation resistance: [1](#0-0) 

That price feeds `getVenueUsdPrice` → `resolveLegRates`, which is the function that computes the actual `rate` (token1 per token0) used to size a real fill for a curveless (venue-priced) pair: [2](#0-1) 

The only defense is `checkPriceGuard`, which compares the venue quote against a **static, manually-configured** `referencePrice` and rejects only if deviation exceeds `maxDeviationBps`. Critically, the guard is optional — if no reference is configured for the chain, the check passes unconditionally: [3](#0-2) 

The documented flow confirms the root cause explicitly: the price is the "raw pool mid" from `sqrtPriceX96`, with "no size or impact term," and the guard checks "deviation from a static reference, not execution cost": [4](#0-3) 

An attacker who takes a flash loan to move the configured V4 pool's spot price, then submits (or fronts) an intent order routed to this venue-priced pair, causes the solver to compute an inflated/deflated `rate` from the manipulated pool and fill the order (or size confirmation depth) against that bad price — extracting value from the solver's real inventory, directly analogous to Compound v2's spot-price collateral manipulation that drained Channels Finance.

### Impact Explanation
A manipulated venue price directly changes the token amount released by the filler for a real (non-phantom) fill on a curveless pair, or inflates/deflates the USD notional used for confirmation-depth sizing (weakening reorg protection), both computed via `referenceRate`/`resolveLegRates`: [5](#0-4) 
This can result in concrete theft of solver-held liquidity (Uniswap V4 LP positions withdrawn at a mispriced rate), satisfying the "concrete theft ... of funds" bar. Severity is bounded by pair configuration (only curveless pairs, USD-stable token0 required) and by whether an operator has configured `referencePrice`/`maxDeviationBps`.

### Likelihood Explanation
Likelihood is Medium: exploitation requires (1) a curveless pair configured to be priced purely from the V4 venue with no or a loosely-set `maxDeviationBps` guard, and (2) sufficient capital/flash-loan access to move that specific pool's spot price within one block, which is generally accessible to any unprivileged actor on public AMMs. The `checkPriceGuard`'s optionality and reliance on a static reference (not continuously validated against a robust independent oracle or TWAP) make this a real, reachable gap rather than a purely theoretical one.

### Recommendation
- Replace the instantaneous `sqrtPriceX96`-derived mid with a TWAP (time-weighted average price) sourced from the pool's oracle observations, or cross-check against an independent oracle (e.g., Chainlink) before use.
- Make the price guard (`checkPriceGuard`) mandatory for all venue-priced pairs rather than optional, and tighten `maxDeviationBps` defaults.
- Incorporate size/impact terms so a large fill cannot be priced off a thin/manipulated pool's mid alone, consistent with the existing internal audit note about missing execution-cost pricing.

### Proof of Concept
1. Operator configures a curveless pair (e.g., USDC/EXOTIC) priced solely via `[vault.uniswapV4]`, without setting `referencePrice`/`maxDeviationBps` (guard unguarded, per lines 428-430 of `fx.ts`).
2. Attacker flash-loans into the configured V4 pool and swaps to push `sqrtPriceX96` far from fair value.
3. Attacker (or an accomplice) submits an intent order matching this pair while the pool is skewed.
4. `getExoticTokenPrice` → `computeDirectPoolPriceUsd` returns the skewed mid; `resolveLegRates` prices the fill at that rate; `checkPriceGuard` passes (no reference configured), and the solver fills the order at the manipulated rate, transferring more value than it should.
5. Attacker reverses the pool manipulation in the same transaction, keeping the arbitrage profit extracted from the solver's real Uniswap V4 inventory.

### Citations

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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
