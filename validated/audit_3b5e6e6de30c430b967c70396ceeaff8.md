## Title
Uniswap V4 spot-price venue oracle lets a flash-loan tick manipulation mis-price and drain solver-funded intent fills - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Hyperbridge's Simplex solver prices "curveless" cross-asset intent legs directly off a live Uniswap V4 pool's current tick rather than a manipulation-resistant TWAP, exactly the bug class from the Inverse Finance exploit ("misuses the balances/state of assets in a pool to directly calculate the price"). `UniswapV4FundingPlanner.getExoticTokenPrice`/`computeDirectPoolPriceUsd` reads `sqrtPriceX96` from the pool's current `slot0` and derives `priceUsd` from it verbatim [1](#0-0) , and this price feeds the amount the solver commits to deliver for an intent fill and the liquidity it withdraws from its own position to fund it.

### Finding Description
`resolveLegRates`'s venue-priced path (documented in `sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md`) calls `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice`, which iterates the solver's configured V4 positions and picks "the position with the largest pool liquidity", then calls `computeDirectPoolPriceUsd`, returning `sdkPool.token0Price`/`token1Price` computed straight from the pool's live `sqrtPriceX96` [2](#0-1) . This is confirmed by the flow doc: *"computeDirectPoolPriceUsd returns the raw pool mid derived from sqrtPriceX96... there is no size or impact term... checkPriceGuard is the only defense on this path, and it checks deviation from a static reference, not execution cost."*

The only mitigation, `checkPriceGuard`, is entirely optional per position — the docs state: *"The two fields [referencePrice, maxDeviationBps] must be set together; omit both to leave the chain unguarded."* An operator can (and per the docs example, by default) run with no guard at all. Even when configured, the guard only checks deviation from a stale static number set at config time, not against manipulation happening within the same block/transaction as the fill.

`UniswapV4LiquidityState.refresh()` re-reads `getSlot0`/`getLiquidity` immediately before pricing/withdrawal planning [3](#0-2) , meaning the price used to plan a fill is read fresh from chain state that an attacker fully controls within the same transaction window (a large swap or flash loan against the pool moves `sqrtPriceX96`/tick before the solver's read).

### Impact Explanation
An attacker who transiently manipulates the tick/price of the Uniswap V4 pool backing a solver's exotic-token position (via a large swap, optionally flash-loaned) can cause `computeDirectPoolPriceUsd` to report a favorable-to-attacker price for `getExoticTokenPrice`. Downstream, this feeds `computeLegPolicyOutput`'s linear extension of the manipulated mid price across the full quoted quantity (per the flow doc), sizing how much of the exotic token the solver commits to deliver and how much liquidity is withdrawn from the V4 position to fund it. A manipulated low price could make the solver deliver more of a valuable token than intended relative to what it receives, or accept intents at a rate priced off a distorted pool, transferring solver-held funds (LP-backed inventory) to the attacker's benefit — the same mechanism (spot pool price used as an oracle for a lending/pricing decision, exploited via reserve-moving trades) that drained Inverse Finance's DOLA market. This is a concrete pathway to loss of solver-funded intent-fill inventory, reachable by any party able to submit ordinary swap transactions against the referenced pool plus an intent that the manipulated price would misprice.

### Likelihood Explanation
Exploitability depends on: (1) an operator running a `[vault.uniswapV4]` pair without `referencePrice`/`maxDeviationBps` configured (explicitly permitted and the documented default posture), or with thin/imprecise guard bounds; (2) the referenced pool having tractable enough liquidity/depth for the attacker to move the tick meaningfully within the solver's read window. Because the guard is opt-in and keyed to a static reference rather than a robust TWAP or execution-cost-aware pricing, likelihood is moderate-to-high for any venue-priced pair deployed without careful operator configuration, and the flow doc itself flags this as a known, currently-unaddressed gap ("no size or impact term ... pays a fee tier it never quoted against").

### Recommendation
- Require `referencePrice`/`maxDeviationBps` (or an equivalent guard) unconditionally for any curveless Uniswap-V4-priced pair rather than allowing it to be omitted.
- Replace or supplement the instantaneous `sqrtPriceX96` read with a TWAP/time-weighted observation resistant to single-block manipulation.
- Incorporate the pool's fee tier and a size/impact term into `computeDirectPoolPriceUsd`/`computeLegPolicyOutput` so quoted rates reflect realistic execution cost, not just a static mid.
- Consider re-validating the price guard at the moment of on-chain execution (not only at planning time) to defend against manipulation introduced between planning and fill submission.

### Proof of Concept
Conceptual (validated via code/doc inspection, not executed):
1. Operator configures a `[vault.uniswapV4]` position for an exotic/USD pair without `referencePrice`/`maxDeviationBps` (permitted per docs).
2. Attacker submits a large swap (optionally via flash loan) against the underlying Uniswap V4 pool to move `sqrtPriceX96`/tick.
3. Attacker (or a colluding party) submits/bids on an intent whose leg is priced via this venue.
4. Simplex's `UniswapV4LiquidityState.refresh()` re-reads the manipulated `slot0`, and `getExoticTokenPrice`/`computeDirectPoolPriceUsd` returns the distorted price with no guard rejecting it.
5. `resolveLegRates`/`computeLegPolicyOutput` sizes the fill and the LP withdrawal off this distorted price, and the solver delivers an unfavorable amount funded from its own Uniswap V4 position.
6. Attacker reverses the initial swap (or lets arbitrageurs do so), pocketing the difference while the solver's position is drained relative to fair value.

I was unable to fully trace `computeLegPolicyOutput`/`checkPriceGuard`'s exact numeric bounds-check logic (only inferred from the flow doc and partial `fx.ts` grep hits), so the precise guard behavior when configured could not be fully verified within the available tool budget — a Devin session with full file access would be needed to confirm exact edge-case handling in `checkPriceGuard` and `fx.price-guard.test.ts`.

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-272)
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
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L139-170)
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
```
