### Title
Simplex Uniswap V4 venue pricing uses manipulable pool spot price with only a static-deviation guard, allowing solver funds to be drained via flash-loan-style price manipulation - (File: `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
`UniswapV4FundingPlanner.getExoticTokenPrice()` prices curveless intent pairs directly from the current Uniswap V4 pool tick (`sqrtPriceX96`), the same class of bug as the reported `V3Oracle::getValue()` finding: a value used to settle real economic transfers is derived from a spot price that can be distorted within a single block, and the only protection (`checkPriceGuard`) merely checks that the manipulated price stays within a static tolerance band — it does not protect the amount/notional actually paid out.

### Finding Description
`UniswapV4FundingPlanner.computeDirectPoolPriceUsd()` reads `sdkPool.token0Price`/`token1Price`, which is derived straight from the pool's live `sqrtPriceX96` fetched in `refresh()` [1](#0-0) . `getExoticTokenPrice()` picks the highest-liquidity position and returns this **raw pool mid price** with no execution/size adjustment [2](#0-1) .

This price feeds `resolveLegRates()` in the solver's fill-pricing engine, which uses it directly as the fill rate for curveless pairs and only defends it with `checkPriceGuard`, a static deviation check against an operator-configured `referencePrice`/`maxDeviationBps` [3](#0-2) .

As the project's own flow documentation states: `computeDirectPoolPriceUsd` returns the raw pool mid derived from `sqrtPriceX96`; the pool's fee tier is stored but never applied to the price, and there is no size or price-impact term — the rate is extended linearly across the whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks *deviation from a static reference*, not execution cost [4](#0-3) .

This mirrors the `V3Oracle` root cause exactly: a validated bound (Chainlink-vs-TWAP deviation there; `maxDeviationBps` here) is applied only to the *price*, while the *amount/value actually paid* is computed from the manipulable current pool state without any TWAP or execution-price safeguard. An order placer can move the qualifying pool's tick toward the edge of the configured `maxDeviationBps` band (e.g. via a flash-loan swap in the same block as submitting/bidding on an intent order), causing the solver to size and fill the order at the manipulated mid price — extracting value from the solver's escrowed inventory — while the deviation guard still passes because it was designed to catch stale/thin-pool errors, not an attacker deliberately parking the price at the boundary of the tolerated range.

### Impact Explanation
A successful manipulation causes the solver (acting as the honest counterparty in the Hyperbridge intents flow) to release output tokens against a distorted price, resulting in **concrete theft of escrowed/solver funds** on a per-fill basis, scaled by `maxOrderSize` and the pool's available depth. Because pricing also lacks any fee-tier or slippage term, even non-adversarial "at the edge of the band" pricing already loses value on every trade through this venue; a deliberate single-transaction manipulation compounds it into a direct extraction of value comparable to the original Revert Finance finding (favorable borrow/repay ↔ favorable fill price).

### Likelihood Explanation
Reachable by any unprivileged order placer/user interacting with `IntentGateway` and choosing a curveless pair configured with `[vault.uniswapV4]` pricing — no special privilege needed, only capital to move the qualifying pool's tick within one transaction (flash loans make this capital-free). Likelihood depends on `maxDeviationBps` being set loosely enough (or `referencePrice`/`maxDeviationBps` being omitted entirely, "leaving the chain unguarded" per the docs) and on the targeted pool having thin enough liquidity to move within the allowed band, both realistic misconfigurations acknowledged in the project's own docs.

### Recommendation
Replace or supplement the raw spot-price read with a manipulation-resistant reference (e.g., a TWAP over a sufficiently long window, or deriving priced amounts from a liquidity/impact-aware quote rather than a linear extension of the mid), matching the confirmed Revert Finance mitigation: compute traded amounts from a validated oracle-consistent price rather than the current pool tick. Additionally, apply the pool's actual fee tier and a size/impact term when computing the venue quote instead of extending the raw mid linearly, and make `referencePrice`/`maxDeviationBps` mandatory (not optional) for any Uniswap V4-priced pair.

### Proof of Concept
1. Operator configures `[vault.uniswapV4]` with a position for pair USDC/CNGN and either omits `referencePrice`/`maxDeviationBps` or sets a loose band (per `docs/content/developers/evm/simplex/pricing.mdx` lines 68-84, this is an explicitly supported/left-unguarded configuration).
2. Attacker takes a flash loan and swaps against the CNGN/USDC V4 pool in the same block, moving `sqrtPriceX96` to the edge of the tolerated deviation (or unboundedly if unguarded).
3. Attacker (or their own bid/order) submits/triggers an `IntentGateway` order priced off this pair; `resolveLegRates` → `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice` reads the manipulated `slot0`/`sqrtPriceX96` and returns the distorted mid price [5](#0-4) .
4. `checkPriceGuard` passes because the distorted price stays inside `maxDeviationBps` (or no guard exists) [6](#0-5) .
5. Solver computes and executes the fill at the manipulated price, transferring output tokens from its own inventory/LP position at an unfavorable rate; attacker reverses the flash-loan swap in the same transaction, banking the difference — the same pattern of "distort spot price, extract value, check-passes-because-it-only-bounds-price-not-amount" documented in the original `V3Oracle` report.

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L149-169)
```typescript
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
