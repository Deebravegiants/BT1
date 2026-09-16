### Title
Uniswap V4 venue pricing for Simplex fills uses the raw pool spot price, letting a flashloan-manipulated pool drain solver funds or extract value from users - (File: `sdk/packages/simplex/src/strategies/fx.ts` / `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
Simplex's cross-asset order pricing for "venue-priced" pairs derives the fill rate directly from a Uniswap V4 pool's current `sqrtPriceX96` (spot price), the same bug class as the referenced report's `getOwnValuation()` using `slot0().sqrtPriceX96` for `rebalance()` accounting. The only mitigation is a static `maxDeviationBps` band around an operator-set `referencePrice`, not a TWAP — the same weakness the report flags ("Use a TWAP price").

### Finding Description
When a pair has no static curves and `token0` is a USD stablecoin, `resolveLegRates` in `sdk/packages/simplex/src/strategies/fx.ts` prices the leg from the live pool instead of a curve: [1](#0-0) 

`UniswapV4FundingPlanner.getExoticTokenPrice` picks the most-liquid pool and calls `computeDirectPoolPriceUsd`, which reads `sdkPool.token0Price`/`token1Price` — values computed directly from the pool's current `sqrtPriceX96` fetched via `StateView.getSlot0`: [2](#0-1) [3](#0-2) [4](#0-3) 

This spot price is then used to size and price the order fill (`referenceRate`/`resolveLegRates` → `computeLegPolicyOutput` extends it linearly across the whole quantity with no impact/fee term): [5](#0-4) [6](#0-5) 

The only defense is `checkPriceGuard`, which rejects a quote only if it deviates from a static, operator-configured `referencePrice` by more than `maxDeviationBps` — it bounds staleness/manipulation to a fixed percentage band, not zero, and both fields are optional (a chain can be left entirely unguarded): [7](#0-6) 

This is functionally identical to the external report: both read a live `sqrtPriceX96` spot price with no TWAP and use it directly in financial accounting (rebalancing there, order pricing/funding here).

### Impact Explanation
An attacker who can move the pool's spot price within (or even at the edge of) the configured `maxDeviationBps` band using a flashloan-funded swap, atomically with submitting/filling an intent order, can:
1. Push the venue price against the solver so it pays out more of the exotic token than the true fair value, extracting value from the solver's Uniswap V4 LP-backed vault (`UniswapV4FundingPlanner.planWithdrawalForToken` withdraws liquidity and funds the fill at the manipulated rate) — theft of solver funds.
2. Conversely, push the price down when the solver is selling, causing the solver to accept less USD than the exotic tokens are worth, again a real capital loss.
3. Because `checkPriceGuard` only compares against a static reference within a wide bps band (and is optional per chain), a manipulation that stays inside that band bypasses the guard entirely while still being economically profitable for the attacker, especially since `computeLegPolicyOutput` applies the mid price linearly to the whole order size with no slippage/impact term.

This is a Medium-severity, capital-loss issue affecting any Simplex deployment configured with `[vault.uniswapV4]` pool-based pricing, directly reachable by an unprivileged actor (anyone able to submit a flashloan swap plus an intent order/fill in the same block).

### Likelihood Explanation
Likelihood is Medium: it requires (a) a pair configured for pool-based ("venue") pricing rather than static curves, (b) sufficient flashloan liquidity to move the specific Uniswap V4 pool's spot price within the deviation band, and (c) atomic sequencing with an order fill. All three are attacker-controllable and require no special privilege — only capital and correct sequencing, standard for flashloan spot-price attacks on thin pools (e.g., a cNGN/USDC pool as shown in the docs' example configs).

### Recommendation
Replace the direct `sqrtPriceX96`-derived spot price in `computeDirectPoolPriceUsd` with a time-weighted average price (TWAP) sourced from the pool's oracle/observations (or an external oracle), and/or tighten `checkPriceGuard` to require `referencePrice`/`maxDeviationBps` on every venue-priced position (make it mandatory, not optional), and add execution-cost/impact terms (accounting for the pool's fee tier and trade size) to `computeLegPolicyOutput` rather than extending the mid price linearly across the whole quantity.

### Proof of Concept
1. Configure a Simplex filler with a `[vault.uniswapV4]` position pricing an exotic token (e.g., cNGN/USDC) with no `referencePrice`/`maxDeviationBps` set, or a wide band (see `docs/content/developers/evm/simplex/pricing.mdx` example config).
2. Attacker takes a flashloan and performs a large swap on the underlying Uniswap V4 pool to shift `sqrtPriceX96` favorably.
3. In the same block, attacker submits (or has a colluding filler process) an intent order that Simplex prices via `resolveLegRates` → `getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which reads the manipulated spot price.
4. Simplex funds the fill via `UniswapV4FundingPlanner.planWithdrawalForToken`, withdrawing LP liquidity and delivering tokens priced at the manipulated rate.
5. Attacker reverses the flashloan swap, pocketing the difference between the manipulated fill price and the pool's true price, at the solver's expense.

### Citations

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L6-14)
```markdown
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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L146-170)
```typescript
		// Fetch slot0 + liquidity for each unique pool via StateView
		const poolStateMap = new Map<string, { sqrtPriceX96: bigint; tick: number; poolLiquidity: bigint }>()

		for (const poolId of poolIds) {
			const [slot0Result, poolLiquidity] = await Promise.all([
				client.readContract({
					address: this.stateView,
					abi: UNISWAP_V4_STATE_VIEW_ABI,
					functionName: "getSlot0",
					args: [poolId as HexString],
				}) as Promise<[bigint, number, number, number]>,
				client.readContract({
					address: this.stateView,
					abi: UNISWAP_V4_STATE_VIEW_ABI,
					functionName: "getLiquidity",
					args: [poolId as HexString],
				}) as Promise<bigint>,
			])

			poolStateMap.set(poolId, {
				sqrtPriceX96: slot0Result[0],
				tick: slot0Result[1],
				poolLiquidity,
			})
		}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1397-1434)
```typescript
	private computeLegPolicyOutput(
		inputAmount: bigint,
		inputIsToken0: boolean,
		token0Decimals: number,
		token1Decimals: number,
		/**
		 * Token0 left in the pair's per-order exposure budget, or `null` to price the whole
		 * input unbudgeted. Only a price probe passes `null`: it commits no capital, so there
		 * is no exposure to ration, and a clamped quantity would silently misprice it.
		 */
		remainingToken0: Decimal | null,
		rate: Decimal,
	): { token0Used: Decimal; policyMaxOutput: bigint } | null {
		let legMaxToken0: Decimal
		if (inputIsToken0) {
			legMaxToken0 = new Decimal(formatUnits(inputAmount, token0Decimals))
		} else {
			legMaxToken0 = new Decimal(formatUnits(inputAmount, token1Decimals)).div(rate)
		}

		const token0ForLeg = remainingToken0 === null ? legMaxToken0 : Decimal.min(legMaxToken0, remainingToken0)
		if (token0ForLeg.lte(0)) {
			return null
		}

		let policyMaxOutput: bigint
		if (inputIsToken0) {
			// Output is token1: convert the token0 allocation at the pair rate.
			policyMaxOutput = BigInt(
				token0ForLeg.mul(rate).mul(new Decimal(10).pow(token1Decimals)).floor().toFixed(0),
			)
		} else {
			// Output is token0: pay out the token0 equivalent of the token1 input.
			policyMaxOutput = BigInt(token0ForLeg.mul(new Decimal(10).pow(token0Decimals)).floor().toFixed(0))
		}

		return { token0Used: token0ForLeg, policyMaxOutput }
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
