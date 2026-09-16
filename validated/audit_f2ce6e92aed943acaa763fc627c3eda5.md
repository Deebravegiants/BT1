## Finding

The reported bug class — trusting an AMM's instantaneous spot price as if it can't be manipulated in-block, with no TWAP/observation-freshness check — has a direct analog in Hyperbridge's Simplex filler, which uses live Uniswap V4 `slot0` spot price to price real order fills.

### Title
Uniswap V4 venue pricing uses unprotected instantaneous spot price, allowing flash-swap price manipulation to mis-price solver fills - (File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts)

### Summary
`UniswapV4FundingPlanner.getExoticTokenPrice` derives a token's USD price directly from the pool's current `sqrtPriceX96`/tick (via `computeDirectPoolPriceUsd`), which is read fresh from `getSlot0` on every quote. This is the same class of assumption flagged in the external report: a live/instantaneous AMM price is trusted as manipulation-free with no time-weighted average, no minimum-elapsed-time check, and no verification against a same-block manipulation.

### Finding Description
`UniswapV4LiquidityState.refresh` fetches the pool's current price straight from `StateView.getSlot0` every call: [1](#0-0) 

That raw `sqrtPriceX96` feeds an SDK `V4Pool` whose `token0Price`/`token1Price` becomes the "USD price" of the exotic token with no size/impact/staleness treatment: [2](#0-1) 

This spot price feeds directly into the pricing engine that sizes and prices real intent fills: [3](#0-2) 

The only mitigation is `checkPriceGuard`, an **optional**, static-reference deviation band: [4](#0-3) 

The docs explicitly confirm this guard is opt-in and, when unconfigured, the chain is left completely unguarded against a "manipulated, stale, or thin pool": [5](#0-4) 

Even when configured, the guard only bounds *how far* the manipulated price can be from a static reference — it does not detect or prevent manipulation that stays inside the configured band (analogous to VeloOracle trusting any "already-past" timestamp regardless of how recently the observation moved). There is no TWAP consultation, no check on how many blocks/seconds since the pool's last swap, and no reentrancy/same-block guard: an attacker can flash-swap the pool to shift `sqrtPriceX96` immediately before (or in the same block as) triggering/timing a fill so that `getExoticTokenPrice` returns a manipulated value the filler then prices a real fill against.

### Impact Explanation
A manipulated venue price directly changes the rate (`token1 per token0`) used to size and price a live order fill (`resolveLegRates`, `referenceRate`), and also feeds `checkPriceGuard`'s own reference comparison. An attacker can profit at the filler's expense by moving the pool price with a flash swap, submitting/timing an intent order to be filled by the manipulated rate, and reverting the pool state after — extracting value from the solver's vault/inventory. This is a concrete "theft of funds" impact on the solver's escrowed liquidity via a single submitted order, meeting the Medium-severity bar of the referenced report class.

### Likelihood Explanation
Any unprivileged intent submitter reachable through the public order flow can trigger this: they only need to interact with the same Uniswap V4 pool the filler is configured against (a public AMM) and time their intent so the filler quotes/fills against the manipulated spot price. No `referencePrice`/`maxDeviationBps` guard is required by the code — operators may leave chains "unguarded" per the documented default, and even when configured the guard is static and does not address in-block manipulation, so likelihood is not negligible.

### Recommendation
Do not price fills from a single-block `slot0` read. Require either: (a) a TWAP over the pool's own oracle/observations with a minimum elapsed-time-since-last-update check before trusting the spot value (mirroring the Velodrome fix — only trust the observation once sufficiently more time has passed than one block), or (b) cross-check the spot price against an independent oracle before it is used to size or price a fill, and make the deviation guard mandatory rather than optional for venue-priced pairs.

### Proof of Concept
1. Filler configures a curveless (venue-priced) pair backed by a Uniswap V4 position, per `docs/content/developers/evm/simplex/pricing.mdx`, without setting `referencePrice`/`maxDeviationBps` (explicitly allowed — "omit both to leave the chain unguarded").
2. Attacker flash-swaps the configured V4 pool to move `sqrtPriceX96` favorably for the exotic token.
3. Attacker (or a colluding party) submits an intent order sized to be filled by the FXFiller; `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd` reads the manipulated `slot0` price in the same/adjacent block.
4. `resolveLegRates`/`referenceRate` price the fill at the manipulated rate with no freshness or TWAP check; the filler executes the fill and later reverses the flash swap, realizing profit at the filler's expense.

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L149-170)
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1449-1465)
```typescript
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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
```
