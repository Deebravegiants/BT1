### Title
Simplex FXFiller venue pricing trusts an unguarded single Uniswap V4 pool's instantaneous spot price, letting a flash-loan-style manipulation drain solver funds - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
`FXFiller`'s venue-pricing path prices curveless trading pairs directly off a single Uniswap V4 pool's instantaneous mid-price (`sqrtPriceX96` → `token0Price`/`token1Price`), the same "getPrice() trusts pool reserves like gospel" pattern that let the New Gold Protocol attacker manipulate a PancakeSwap pool with a flash loan to force `getPrice()` to report a bogus value and bypass buy limits. The only mitigation is an *optional* static-reference deviation guard (`checkPriceGuard`) that can be left unconfigured per chain, and even when configured, it bounds deviation against a stale reference rather than detecting same-block manipulation.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` / `computeDirectPoolPriceUsd` derives the USD price of the "exotic" token straight from the pool's current tick (`sdkPool.token0Price` / `token1Price`), picking whichever hydrated position has the largest liquidity: [1](#0-0) [2](#0-1) 

This price feeds directly into `FXFiller.resolveLegRates`, which uses it as the trade execution rate for real fills whenever a pair has no static curves and its `token0` is a USD stablecoin: [3](#0-2) 

The only defense is `checkPriceGuard`, which compares the live quote to a static, operator-configured `referencePrice` within `maxDeviationBps` — and it is explicitly optional and can be left unset per chain ("omit both to leave the chain unguarded"): [4](#0-3) [5](#0-4) 

As the project's own internal documentation states, this raw pool mid has no size/impact term and the guard is the *only* defense on the path, checking deviation from a static reference rather than execution cost or same-block manipulation: [6](#0-5) 

This is structurally identical to the NGP bug class: a single AMM pool's live reserves/price are trusted as ground truth, with no TWAP, no manipulation-resistance, and (when unguarded) no sanity bound at all — allowing an attacker who can move the pool's spot price (e.g. via a large swap, flash loan, or sandwich against the pool) within one block to force the filler to price a real fill at an attacker-favorable rate.

### Impact Explanation
Unlike NGP where the protocol's own contract was drained, here the solver's own inventory (source of the price feed and fill counterparty) is the fund at risk: an order submitter can manipulate the referenced Uniswap V4 pool immediately before/within the same block as submitting an intent order, causing `resolveLegRates`/`computeLegPolicyOutput` to compute an inflated `token1 per token0` rate, and the filler will sign and submit a `PackedUserOperation` that fills the order at that manipulated rate — a real, unbacked transfer of value from the solver to the attacker. Because `checkPriceGuard` can be entirely unconfigured, or bounded only against a stale static reference, the manipulation window is not detected until governance manually re-tunes `referencePrice`. This is a concrete theft-of-funds vector reachable by any unprivileged party who can submit an intent order (the "intent solver" surface explicitly in scope).

### Likelihood Explanation
Medium-High. Exploitation requires: (1) a pair configured with `[vault.uniswapV4]` pool-based pricing and no `priceGuard` (or a guard with a wide `maxDeviationBps`), and (2) sufficient capital/flash-loan access to move the chosen pool's `sqrtPriceX96` beyond the guard band (or with no guard, any move is profitable). Given Uniswap V4 pools for exotic/thin tokens (the documented use case, e.g. cNGN) are typically far less liquid than major pairs, moving the price meaningfully is realistic and cheap, closely mirroring how NGP's attacker cheaply skewed PancakeSwap reserves with a flash loan.

### Recommendation
- Make `priceGuard` (referencePrice + maxDeviationBps) mandatory for every `[vault.uniswapV4]` pool-priced pair rather than optional; reject startup configuration that leaves a chain unguarded.
- Replace or supplement the instantaneous `sqrtPriceX96` mid with a manipulation-resistant price (TWAP over multiple blocks, or cross-referencing an independent oracle/multiple pools) before using it to size real fills.
- Apply the pool's fee tier and a size/impact-aware price to `computeLegPolicyOutput` instead of extending the raw mid linearly, and bound single-block price movement (e.g. reject if the same pool's price shifted materially since the last hydration/refresh).

### Proof of Concept
1. Operator configures a curveless pair (e.g. `USDC/CNGN`) priced via `[vault.uniswapV4]` with no `priceGuard` entry for the chain (a supported and documented configuration).
2. Attacker executes a large swap (optionally flash-loan funded) against the thin Uniswap V4 CNGN/USDC pool to push `sqrtPriceX96` far from its fair value.
3. Attacker immediately submits (or bids on) an intent `Order` on the affected pair.
4. `FXFiller.resolveLegRates` → `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice` reads the manipulated `sqrtPriceX96` and returns a skewed `priceUsd`; `checkPriceGuard` passes trivially because no reference is configured.
5. `computeLegPolicyOutput` prices the fill at the skewed rate, and the filler signs and submits a `PackedUserOperation` that overpays the attacker at the solver's expense — funds are extracted from the solver's on-chain inventory.

(Note: full exploitability against a specific mainnet deployment/config, including whether any deployed pair currently omits `priceGuard`, is a deployment/configuration detail not verifiable from the repository alone; this is a code-level design gap present in the reachable code path regardless of current live configuration.)

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L206-239)
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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
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
