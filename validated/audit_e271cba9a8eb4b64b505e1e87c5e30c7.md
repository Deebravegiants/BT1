### Title
Uniswap V4 pool spot price used as the sole oracle for Simplex venue pricing, with only a static deviation guard and no TWAP/impact protection - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Simplex's `UniswapV4FundingPlanner` prices "venue-priced" (curveless) trading pairs directly from a Uniswap V4 pool's instantaneous `sqrtPriceX96`/tick, exactly the kind of manipulable, single-block spot price that the referenced USSD report shows can be pushed off-equilibrium by a single actor without relying on `balanceOf()`. The only defense is `checkPriceGuard`, a static `referencePrice`/`maxDeviationBps` band that the operator must configure manually and that bounds price *deviation*, not the execution cost or size of the trade behind it.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`) iterates the solver's configured V4 positions and, for the pool with the largest on-chain liquidity, calls `computeDirectPoolPriceUsd` (`:246-275`), which returns `sdkPool.token0Price`/`token1Price` — a value derived purely from the pool's current `sqrtPriceX96` (read live via `StateView.getSlot0` in `UniswapV4LiquidityState.refresh`, `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts:139-229`). This is a single-block spot price with no TWAP, no size/impact term, and — per the project's own flow notes — the pool's fee tier is read but never applied to the quote (`sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md:17-21`).

`FXFiller.resolveLegRates` (`sdk/packages/simplex/src/strategies/fx.ts:1443-1479`) uses this venue price directly as the fill rate for any curveless pair whose `token0` is a USD stable, and `computeLegPolicyOutput` extends that mid linearly across the entire priced quantity. The only mitigation is `checkPriceGuard`, an optional, operator-configured static `referencePrice`/`maxDeviationBps` band (`docs/content/developers/evm/simplex/pricing.mdx:68-84`); if unset, "the chain unguarded" is the documented behavior, and even when set it only rejects deviation from a stale, hand-maintained reference — it does not account for trade size, pool depth, or the cost of the fee tier.

This mirrors the USSD/DAI report's core flaw: an on-chain AMM's instantaneous price/liquidity state is trusted as ground truth by logic that then moves real value (here, the solver's inventory payout), and that state can be manipulated within a single transaction (e.g., via a flashloan swap, or — analogous to the reported tick-position trick — a large, narrow-range or wide-range LP position/swap that shifts `sqrtPriceX96` without requiring sustained capital) immediately before the solver reads it and commits to a fill.

### Impact Explanation
An intent submitter/attacker who can move a thinly-traded V4 pool's spot price by more than the configured guard tolerance (or where no guard/`referencePrice` is configured, which the docs explicitly allow) can cause the solver to size a fill's output using a manipulated rate. Since `computeLegPolicyOutput` extends this manipulated mid linearly with no depth/impact correction, this directly transfers value from the solver's escrowed/vault inventory to the attacker's order — a concrete loss of solver funds triggered by a single submitted intent, fitting the "intent solver" reachable-path criterion.

### Likelihood Explanation
Reaching this path requires only submitting an order that resolves to a curveless, venue-priced pair for which the operator has configured Uniswap V4 pool pricing — a documented, supported configuration (`docs/content/developers/evm/simplex/pricing.mdx`). Manipulating a pool's spot price for one block via a swap or a large temporary liquidity position is a well-understood technique (as demonstrated by the referenced report), and the guard is optional and imprecise (static reference vs. dynamic deviation, no size awareness), so exploitation likelihood is high on any thin/low-liquidity exotic-token pool, and non-zero even on guarded ones if the `maxDeviationBps` tolerance is loose enough to permit profitable manipulation.

### Recommendation
Do not price fills off a single spot read of `sqrtPriceX96`. Use a time-weighted average price (TWAP) over multiple blocks/observations, or cross-check against a second independent oracle/venue before trusting the quote. Incorporate trade size/impact into the quoted rate (e.g., simulate the swap through the pool's actual liquidity depth rather than linearly extending the mid), and treat `referencePrice`/`maxDeviationBps` as mandatory rather than optional for any venue-priced pair, with tighter, size-aware bounds.

### Proof of Concept
Not independently reproducible from static analysis alone — this requires deploying/observing a live Uniswap V4 pool with a Simplex-configured position, executing a price-moving swap (or one-sided liquidity add near the pool's price boundary) in the block immediately preceding an order fill, and demonstrating the solver's `getExoticTokenPrice`/`resolveLegRates` path (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`, `sdk/packages/simplex/src/strategies/fx.ts:1443-1479`) consumes the manipulated spot price to size an over-generous fill. This would need to be verified in a forked-mainnet or testnet integration test with a live Simplex filler instance, which is outside what static code review can confirm. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L139-229)
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
			pos.currentTick = poolState.tick

			// Build SDK Pool (without tick data provider — we only need amount calcs)
			const currency0 = currencyFromHydratedDecimals(chainId, pos.currency0, pos.decimals0)
			const currency1 = currencyFromHydratedDecimals(chainId, pos.currency1, pos.decimals1)

			const sdkPool = new V4Pool(
				currency0,
				currency1,
				pos.fee,
				pos.tickSpacing,
				pos.hooks,
				poolState.sqrtPriceX96.toString(),
				poolState.poolLiquidity.toString(),
				poolState.tick,
			)

			this.sdkPools.set(poolId, sdkPool)

			this.logger.debug(
				{
					tokenId: pos.tokenId.toString(),
					liquidity: liquidity.toString(),
					remainingLiquidity: pos.remainingLiquidity.toString(),
					sqrtPriceX96: poolState.sqrtPriceX96.toString(),
					currentTick: poolState.tick,
				},
				"UniswapV4 position refreshed",
			)
		}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1443-1479)
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

		const askRate = leg.pair.askPricePolicy?.getPrice(cappedPairNotional) ?? null
		const bidRate = leg.pair.bidPricePolicy?.getPrice(cappedPairNotional) ?? null

		const rate = leg.inputIsToken0 ? askRate : bidRate
		if (!rate) {
			this.logger.debug(
				{ orderId, pair: `${leg.pair.token0}/${leg.pair.token1}`, inputIsToken0: leg.inputIsToken0 },
				"Rejecting leg: direction disabled for one-sided LP",
			)
			return null
		}
		return { rate, oppositeRate: leg.inputIsToken0 ? bidRate : askRate, priceSource: "policy" }
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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L40-84)
```text
## Pool-Based Pricing

When **`[vault.uniswapV4]`** lists at least one position, cross-asset pairs without curves derive bid/ask prices from **Uniswap V4 pool state** (current tick). The pool acts as the price oracle instead of a static curve. Note this yields a **single** price used in both directions — a venue-priced pair has no bid/ask spread of its own, so its margin comes from `order.fees` alone.

With Uniswap V4 positions configured, you can **omit** `bidPriceCurve` and `askPriceCurve` on the pair. Pool pricing requires the pair's `token0` to be a USD stablecoin, and same-token pairs always need their curve. The optional **`spreadBps`** field (basis points) sets the slippage tolerance for on-chain LP redemptions; defaults to `50` (0.50%).

Uniswap V4 venue pricing uses pools that pair the exotic token with **USDC or USDT** (addresses from your chain config). When multiple positions exist for the same exotic token on a chain, the most-liquid qualifying pool's price is used.

```toml lineNumbers
[assets.CNGN]
"EVM-8453" = "0x46C85152bFe9f96829aA94755D9f915F9B10EF5F"

[[pairs]]
token0 = "USDC"
token1 = "CNGN"
maxOrderSize = "5000"       # no curves — priced from the pool

[vault.uniswapV4]
spreadBps = 50  # 0.5% slippage tolerance on LP redemptions
positions = [
    { chain = "EVM-8453", tokenId = "2087350" },
]
```

<Callout type="info">
Startup validation requires a pricing source per pair: **either** bid/ask price curves, **or** at least one `[vault.uniswapV4]` position. A pair with neither fails validation.
</Callout>

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
