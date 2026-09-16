### Title
Uniswap V4 venue pricing reads live pool spot price with no TWAP protection, letting a flash-loan-manipulated pool drain a Simplex solver's inventory - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
`UniswapV4FundingPlanner.getExoticTokenPrice` and `computeDirectPoolPriceUsd` price an intent-order leg directly from the pool's current `sqrtPriceX96` (a spot read), the same class of bug as the reported USSD `getOwnValuation` issue that read a Uniswap spot price instead of a TWAP. An attacker can flash-loan-manipulate the referenced Uniswap V4 pool, then place an IntentGateway order sized against the manipulated rate, causing the Simplex filler (`FXFiller`) to fill at an off-market price using its own token inventory.

### Finding Description
`computeDirectPoolPriceUsd` derives the USD price of the exotic token straight from `sdkPool.token0Price`/`token1Price`, which is computed from the pool's current `sqrtPriceX96`: [1](#0-0) 

`getExoticTokenPrice` calls `state.refresh()` (a live on-chain read of `getSlot0`) immediately before pricing and just picks the pool with the largest liquidity among configured positions — no TWAP, no multi-block average, no minimum observation window: [2](#0-1) 

This price feeds `FXFiller.resolveLegRates` for curveless pairs, where the pool acts as the sole price oracle for both bid and ask: [3](#0-2) 

The project's own documentation acknowledges the pool is trusted as-is and can return a "manipulated, stale, or thin" quote, and that the only defense (`checkPriceGuard`/`referencePrice`/`maxDeviationBps`) is optional and configured per operator: [4](#0-3) [5](#0-4) 

Even when `referencePrice`/`maxDeviationBps` is configured, the guard only rejects when the manipulated price drifts more than `maxDeviationBps` from a *static* reference value — a manipulation kept inside that band (or an operator running with a wide band, or none at all, since it is explicitly optional) still reaches `resolveLegRates` and prices the fill: [6](#0-5) 

An unprivileged user (intent placer) can therefore, within one atomic transaction bundle: (1) flash-loan and swap in the referenced V4 pool to move `sqrtPriceX96` in their favor, (2) submit an IntentGateway order whose leg is priced from that manipulated pool via `getExoticTokenPrice`, (3) have the honest Simplex solver evaluate and fill the order at the manipulated rate (worse for the solver / better for the attacker), (4) unwind the flash loan and pool position in the same transaction, keeping the arbitrage profit extracted from the solver's inventory.

### Impact Explanation
This directly causes theft of solver-held funds: the solver is a value-holding, unprivileged (from the protocol's perspective) participant that fills IntentGateway orders using its own on-chain inventory, valued and released based on the manipulated spot price. Since `computeLegPolicyOutput` extends the manipulated mid price linearly across the whole quantity with no size/impact term, a large order against a thin pool can extract disproportionate value in a single block. This qualifies as concrete theft of funds from a value-holding participant in the Hyperbridge intents ecosystem.

### Likelihood Explanation
Likelihood is High for any deployment where `[vault.uniswapV4]` pool-based pricing is used without a `referencePrice`/`maxDeviationBps` guard (explicitly an optional, unguarded configuration per the documentation), and Medium where the guard is configured but its static band and pool-liquidity-agnostic checks leave room for in-band manipulation. Flash-loan price manipulation against a single AMM pool within one transaction is a well-established, low-cost attack technique, and the code path is reachable by any address that can place an IntentGateway order and interact with the referenced pool — no special privilege required.

### Recommendation
- Replace the direct `sqrtPriceX96`/spot-price read in `computeDirectPoolPriceUsd` with a time-weighted average price (TWAP) sourced from the pool's oracle observations (or an external oracle), sampled over a window resistant to single-block manipulation.
- Make the `referencePrice`/`maxDeviationBps` guard mandatory (not optional) for any curveless, venue-priced pair, and tighten it to also account for pool liquidity depth relative to the leg's notional (a size/impact-aware check), not just static deviation.
- Consider requiring multi-block confirmation (e.g., comparing the price across N consecutive blocks) before treating a venue quote as tradeable, and capping per-block leg size, especially for thin pools.

### Proof of Concept
1. Solver operator configures `[vault.uniswapV4]` with a position on a thin USDC/EXOTIC pool and no `referencePrice`/`maxDeviationBps` guard (a supported, documented configuration — see `pricing.mdx` lines 40-66).
2. Attacker takes a flash loan and swaps a large amount into/out of the same V4 pool, pushing `sqrtPriceX96` far from the pool's normal mid price.
3. In the same transaction bundle, attacker places (or has already placed) an IntentGateway order whose output leg is the venue-priced exotic token.
4. The Simplex filler's `FXFiller.evaluateOrder`/`quotePhantomFill` calls `resolveLegRates` → `venueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which reads the manipulated `sqrtPriceX96` and returns a favorable rate to the attacker.
5. The solver fills the order at the manipulated rate using its own wallet/LP-backed inventory (`computeLegPolicyOutput`), handing the attacker more output tokens than a fair mid price would justify.
6. Attacker reverses the pool manipulation and repays the flash loan within the same transaction, keeping the difference as profit extracted from the solver.

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L206-234)
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
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-263)
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
