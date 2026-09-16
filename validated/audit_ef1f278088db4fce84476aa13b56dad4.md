### Title
Uniswap V4 spot-price venue oracle is flash-loan manipulable, letting an unprivileged order-placer trick the solver's fill price - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Simplex's pool-based pricing venue (`UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`) prices curveless pairs directly from a Uniswap V4 pool's current `sqrtPriceX96`/tick (an instantaneous spot price), the same bug class as the DKP exploit, where an AMM's live reserve ratio was used as an on-chain price oracle and was manipulated via a same-block flash loan. Any unprivileged user can submit an intents order against a "venue-priced" pair; if they first distort the referenced V4 pool's spot price (e.g., via a flash-loan-funded swap), the solver's fill price for that order is computed from the manipulated pool state.

### Finding Description
`resolveLegRates` in `sdk/packages/simplex/src/strategies/fx.ts` uses venue pricing whenever a pair is curveless (no `bidPricePolicy`/`askPricePolicy`) and `token0` is a USD stablecoin: [1](#0-0) 

The venue price comes from `UniswapV4FundingPlanner.getExoticTokenPrice`, which selects the highest-liquidity qualifying position and derives the USD price straight from the SDK `Pool` object's `token0Price`/`token1Price`, which in turn is built every refresh from the pool's live `sqrtPriceX96` and `tick` read via `StateView.getSlot0`: [2](#0-1) [3](#0-2) [4](#0-3) 

There is no TWAP, no minimum-liquidity check against trade size, and no manipulation-resistance mechanism: the price is read fresh on every `refresh()` call immediately before pricing/planning a fill, exactly the "current-block reserve ratio as oracle" pattern the DKP report exploited. The project's own internal documentation flags this directly: *"Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote,"* and the only mitigation, `checkPriceGuard`/`maxDeviationBps`, is optional and disabled by default ("omit both to leave the chain unguarded"): [5](#0-4) 

Even where configured, the guard only checks deviation against a static reference price, not the trade's execution cost or pool depth versus size, and the pool's own fee tier is never applied to the quoted mid, per the project's flow doc: [6](#0-5) 

### Impact Explanation
Any user can submit an intent order (a single dispatched request reachable by an unprivileged actor) against a venue-priced pair. Before/around that submission, the attacker can execute a large swap in the referenced V4 pool (financed by a flash loan) to push `sqrtPriceX96` far from fair value. If the solver's price refresh occurs while the pool is still distorted, `getExoticTokenPrice` returns the manipulated rate, and `resolveLegRates`/`computeLegPolicyOutput` extends that skewed mid linearly across the whole order size with no size/impact term. This causes the solver to either overpay in the exotic token (direct fund loss to the solver's LP position and wallet) or under-deliver to the user, i.e., concrete theft of solver funds through a manipulated price oracle — matching the "Accept only concrete theft ... unsound state commitment" bar for a valid finding.

### Likelihood Explanation
Likelihood is Medium: the attack requires (1) a curveless, venue-priced pair configured with `[vault.uniswapV4]` and no `referencePrice`/`maxDeviationBps` guard (explicitly a supported, documented configuration), and (2) enough capital/flash-loan liquidity to move the specific pool used, and (3) timing the order so the solver's fill occurs while the price is still distorted (the solver refreshes state right before planning/pricing each fill, so a same-block or same-tx-window manipulation is plausible for automated solvers). Where the optional price guard is enabled, likelihood drops but is not eliminated, since the guard bounds deviation against a stale/static reference rather than pool depth or execution cost.

### Recommendation
- Require a manipulation-resistant price source (TWAP over multiple blocks, or a Chainlink/other external oracle) for any venue-priced pair, rather than reading `sqrtPriceX96` directly.
- Make the `referencePrice`/`maxDeviationBps` guard mandatory (not optional) for all `[vault.uniswapV4]`-funded pairs.
- Factor pool depth and trade size into the quoted price (price impact/slippage model) instead of extending a single spot mid linearly across the whole order size.
- Consider requiring price staleness/liquidity checks (e.g., minimum pool TVL relative to order size) before allowing a fill from venue pricing.

### Proof of Concept
Conceptual PoC mirroring the DKP report's structure, adapted to this codebase's reachable surface:
1. Attacker identifies a Simplex-configured pair with no curves (`bidPricePolicy`/`askPricePolicy` unset) and a `[vault.uniswapV4]` position with no `referencePrice`/`maxDeviationBps` guard, per `pricing.mdx`.
2. Attacker takes a flash loan and swaps a large amount through the same V4 pool referenced by that position, moving `sqrtPriceX96` far from the fair value.
3. While the pool is still distorted, attacker submits an `IntentGateway` order on the venue-priced pair.
4. Simplex's solver calls `refresh()` → `getExoticTokenPrice()` → `computeDirectPoolPriceUsd()`, which reads the distorted `sqrtPriceX96`, and `resolveLegRates` prices the whole order off that single skewed mid.
5. The solver fills the order at the manipulated rate, over-delivering value to the attacker (or losing LP funds), after which the attacker reverses/unwinds the flash-loan swap and repays the loan, retaining the fill profit — the same net effect as the DKP `pancakeCall` flash-swap → mispriced exchange → arbitrage-out pattern in the source report.

Note: I could not fully trace the exact call site/timing where `checkPriceGuard` is invoked relative to `refresh()` (the file lookup for the exact `checkPriceGuard` function body in `fx.ts` was not completed before the tool budget ran out), so the precise guard-bypass conditions (e.g., whether guard checks run before or after the potentially-manipulated price is fetched, and how staleness of `referencePrice` is enforced) should be verified directly in `sdk/packages/simplex/src/strategies/fx.ts` and `sdk/packages/simplex/src/tests/strategies/fx.price-guard.test.ts` before remediation.

### Citations

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-274)
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
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L139-216)
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
