### Title
Uniswap V4 spot-price venue pricing is manipulable within a single block and can be used to drain solver funds - (File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts)

### Summary
Simplex's `UniswapV4FundingPlanner.getExoticTokenPrice()` derives the USD price used to fill an intent order directly from a Uniswap V4 pool's instantaneous `sqrtPriceX96` (read live via `refresh()` immediately before pricing), exactly the same class of defect as the Sherlock H-9 finding: an on-chain AMM pool's current state is used as a spot price oracle with no time-weighting/manipulation resistance, and the only defense (`checkPriceGuard`) is an optional, operator-configured static-reference deviation check rather than a robust oracle.

### Finding Description
`getExoticTokenPrice()` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`) calls `state.refresh()`, which re-reads `getSlot0`/`getLiquidity` on the `StateView` contract for the exotic/stable pool at the current block (`UniswapV4LiquidityState.refresh`, `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts:139-230`), and rebuilds a `V4Pool` object from that fresh `sqrtPriceX96`/`tick`. `computeDirectPoolPriceUsd()` (`UniswapV4FundingPlanner.ts:246-275`) then returns `sdkPool.token0Price`/`token1Price` — the raw, un-time-averaged pool mid — as the USD price for the exotic token.

This price feeds `resolveLegRates()` in `sdk/packages/simplex/src/strategies/fx.ts:1443-1466`, which is only used for "curveless" pairs (no configured bid/ask curves), and the resulting `rate = 1 / venueUsd` is what actually prices `computeLegPolicyOutput`, i.e., how much of the exotic token the solver hands the taker for a given USDC/USDT input. The only mitigation is `checkPriceGuard()` (`fx.ts:428-448`), which is:
- optional (skipped entirely if `priceGuard` is not configured for the chain, `guard.reference.lte(0)` also skips it),
- compares against a **static** reference price with a configurable `maxDeviationBps`, not a robust/TWAP oracle, and
- as the docs note (`sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md`), it "checks deviation from a static reference, not execution cost," and the pool's fee tier and price impact are never applied — `computeLegPolicyOutput` extends the mid linearly across the whole priced quantity.

This mirrors the root cause of H-9: instead of using pool balances (V3), here a V4 pool's live tick/sqrtPrice is trusted as ground truth for pricing a transaction that immediately moves real solver-owned funds (the exotic token filled to the taker), with no protection against an attacker moving the pool's price within the same block/transaction bundle the order is submitted and filled in.

### Impact Explanation
An attacker who can move the referenced Uniswap V4 pool's spot price (e.g., via a swap immediately preceding, or atomically bundled with, submission/fill of an intent order) can cause the solver to price its exotic-token fill at a manipulated rate. Because the fill is funded from the solver's own LP position (real capital withdrawn via `planWithdrawalForToken`), a manipulated-low `venueUsd` (exotic overpriced in USD, or attacker manipulates the opposite direction depending on which side benefits them) directly translates into the solver giving away more of the exotic token than the order's true market value — a direct theft of solver-owned funds analogous to H-9's "protocol selling a significantly larger amount of collateral assets than intended, at a manipulated price." If `checkPriceGuard` is left unconfigured for a chain/pair (which the code and tests explicitly treat as a supported, valid configuration — "guard is optional"), there is no defense at all.

### Likelihood Explanation
Reachable by an unprivileged intent submitter: a taker only needs to submit an order matching a curveless pair priced from this venue and can manipulate the referenced Uniswap V4 pool cheaply (it need not even be highly liquid — `getExoticTokenPrice` picks "the position with the largest pool liquidity" among the solver's *own* configured positions, but that pool can still be moved with a single large swap since price impact/depth is not itself checked beyond the static-reference guard). The guard being optional and the tests confirming an "unguarded" mode is a first-class, intentional configuration significantly raises likelihood in any deployment that omits `referencePrice`/`maxDeviationBps`.

### Recommendation
- Do not use a single-block instantaneous `sqrtPriceX96` read as the pricing source. Use a manipulation-resistant price (e.g., pool TWAP/oracle observations spanning multiple blocks, or an external price feed) as the primary reference, and treat the live pool spot price only as a bounded-deviation confirmation rather than the priced rate itself.
- Make `checkPriceGuard` mandatory for any curveless/venue-priced pair rather than optional — reject filling instead of silently pricing unguarded when no reference is configured.
- Incorporate the pool's fee tier and a size/impact term into `computeDirectPoolPriceUsd`/`resolveLegRates` so the linear-mid extension cannot understate the true execution cost for larger orders.

### Proof of Concept
Conceptual attack sequence (mirrors the H-9 write-up's manipulation steps):
1. Attacker identifies a `[vault.uniswapV4]`-configured pair (exotic token/USDC or USDT) that is priced solely from the pool (no `bidPriceCurve`/`askPriceCurve`) and either has no `priceGuard` configured for that chain, or one with a wide `maxDeviationBps`.
2. Attacker performs a swap against the referenced Uniswap V4 pool to move `sqrtPriceX96` so that `token0Price`/`token1Price` misprices the exotic token (e.g., understates its USD value).
3. In the same block (or immediately after, before the solver's independent state changes), attacker submits an intent order sized to fill against this pair. `FXFiller.resolveLegRates` calls `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice`, which calls `state.refresh()` and reads the manipulated `sqrtPriceX96` live, producing a mispriced `venueUsd`.
4. If `checkPriceGuard` passes (unconfigured, or deviation within `maxDeviationBps`), the solver fills the order at the manipulated rate, funding it by withdrawing liquidity from its own Uniswap V4 position (`planWithdrawalForToken`), handing the attacker more of the exotic token than the pool's undisturbed value warrants.
5. Attacker reverses their initial swap, restoring the pool price, having extracted value from the solver's position at the manipulated rate. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L139-199)
```typescript
	async refresh(): Promise<void> {
		const client = this.clientManager.getPublicClient(this.chain)
		const chainId = chainIdFromIdentifier(this.chain)

		// Group positions by poolId to avoid duplicate pool state fetches
		const poolIds = new Set(this.tokenIdToPoolId.values())

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

		// Refresh per-position liquidity and rebuild SDK Pool objects
		for (const pos of this.positions.values()) {
			const key = pos.tokenId.toString()
			const poolId = this.tokenIdToPoolId.get(key)
			const poolState = poolId ? poolStateMap.get(poolId) : undefined
			if (!poolId || !poolState) {
				throw new Error(
					`UniswapV4 refresh: missing pool state for tokenId ${key} (poolId=${poolId ?? "undefined"})`,
				)
			}

			// Read current position liquidity
			const liquidity = (await client.readContract({
				address: pos.positionManager,
				abi: UNISWAP_V4_POSITION_MANAGER_ABI,
				functionName: "getPositionLiquidity",
				args: [pos.tokenId],
			})) as bigint

			pos.liquidity = liquidity
			const prevOnChain = this.lastOnChainLiquidity.get(key) ?? liquidity
			const decrease = prevOnChain > liquidity ? prevOnChain - liquidity : 0n
			const prevConsumed = this.consumed.get(key) ?? 0n
			const newConsumed = prevConsumed > decrease ? prevConsumed - decrease : 0n
			this.consumed.set(key, newConsumed)
			this.lastOnChainLiquidity.set(key, liquidity)
			pos.remainingLiquidity = liquidity > newConsumed ? liquidity - newConsumed : 0n
			pos.sqrtPriceX96 = poolState.sqrtPriceX96
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L395-420)
```typescript
	private async getVenueUsdPrice(chain: string, token1Address: string): Promise<Decimal | null> {
		if (this.fundingVenues.length === 0) return null

		// Prefer V4, fall back to others
		const v4 = this.fundingVenues.filter((v) => v.name === "UniswapV4")
		const venues = v4.length > 0 ? v4 : this.fundingVenues

		for (const venue of venues) {
			const usdPrice = await venue.getExoticTokenPrice(chain, token1Address)
			if (usdPrice?.isPositive()) return usdPrice
		}
		return null
	}

	/** Per-evaluation memo over `getVenueUsdPrice`, keyed by (chain, token1). */
	private venuePriceMemo(): (chain: string, token1Address: string) => Promise<Decimal | null> {
		const cache = new Map<string, Decimal | null>()
		return async (chain: string, token1Address: string) => {
			const key = `${chain}:${token1Address}`
			const cached = cache.get(key)
			if (cached !== undefined) return cached
			const price = await this.getVenueUsdPrice(chain, token1Address)
			cache.set(key, price)
			return price
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
