I have enough evidence to write the finding now.

### Title
FXFiller prices Uniswap V4 exotic-token pairs from the live pool spot price with an optional, off-by-default flash-loan guard - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
When a Simplex `FXFiller` pair has no configured bid/ask curves, `resolveLegRates()` prices the leg directly from the live Uniswap V4 pool's spot mid-price (`sqrtPriceX96`/current tick, read on demand), the same "most recent data point" class of price the original Arrakis report flags as flash-loan manipulable. The only defense, `checkPriceGuard`, is optional and disabled unless the operator explicitly sets `referencePrice` + `maxDeviationBps`; the code and docs both state the pair is "unguarded" without it.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice()` reads the pool's current `sqrtPriceX96`/tick via `StateView.getSlot0()` on every price query (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts` `refresh()`, lines 139-200) and derives a spot USD mid-price with `computeDirectPoolPriceUsd()` (`UniswapV4FundingPlanner.ts` lines 246-274) using `sdkPool.token0Price`/`token1Price` — a pure function of the pool's instantaneous reserves ratio, structurally identical to `slot0` in the original report.

This spot price feeds directly into `resolveLegRates()` for any curveless pair whose `token0` is a USD stable: [1](#0-0) 

The only mitigation is `checkPriceGuard()`, which compares the venue quote to a **static** `referencePrice` within `maxDeviationBps`: [2](#0-1) 

Both the TOML schema comment and the docs explicitly state this guard is optional and the pair is "unguarded" if omitted: [3](#0-2) [4](#0-3) 

The internal flow doc for this path independently documents the same weaknesses: the raw pool mid is used with no size/impact term, and the fee tier the fill will actually pay is never applied to the quoted price: [5](#0-4) 

The resolved venue rate then sets `targetOutput`/`finalOutputAmount`, i.e., the actual amount of the exotic token the solver commits to deliver out of its own Uniswap V4 LP position to fill the user's intent (`fx.ts` lines 736-754), and it also sizes `legNotionals`/confirmation depth (per `fx.price-guard.test.ts`'s `referenceRate` tests). A wrong venue price therefore directly changes real value transferred, not just an internal estimate.

### Impact Explanation
Any unprivileged actor can submit an IntentGateway order against a curveless, Uniswap-V4-funded pair. Immediately before (or via a preceding transaction/flash loan) the filler queries and fills, the attacker can move the pool's spot price with a swap, then unwind it after the solver's fill executes at the stale/manipulated rate:
- Push the pool price so the solver undervalues its own exotic token → solver delivers more exotic tokens than the true market rate justifies for the input received, i.e., a direct drain of solver-held Uniswap V4 LP inventory (loss of funds).
- Push the price the other way to inflate `legNotionals`/`referenceRate`, corrupting confirmation-depth sizing.
Because the guard is off by default ("omit both to leave the chain unguarded"), any operator who does not explicitly configure `referencePrice`/`maxDeviationBps` for a venue-priced chain has zero protection against this — this matches the External Report's core claim that spot-price rebalancing/pricing without a manipulation-resistant oracle is High severity.

### Likelihood Explanation
High for any deployment using pool-based (curveless) pricing without setting the optional guard, since triggering it only requires submitting a normal cross-chain intent order plus a swap against a public Uniswap V4 pool — no privileged access, governance, or protocol-level compromise needed. Even with the guard configured, it only bounds deviation from a static reference and does not account for the fee tier or size impact of the fill itself, per the internal flow doc, so the exposure is only partially closed even for guarded deployments.

### Recommendation
Do not price fills from a single spot read of `sqrtPriceX96`/current tick. Either (a) make the price guard (`referencePrice`/`maxDeviationBps`) mandatory whenever Uniswap V4 pool-based pricing is enabled instead of optional, or (b) replace/augment the spot read with a TWAP-style observation (multiple blocks/checkpoints) and incorporate the pool's fee tier and size/impact into `computeDirectPoolPriceUsd`/`computeLegPolicyOutput`, consistent with the original report's recommendation to use TWAP instead of `slot0`.

### Proof of Concept
1. Operator configures a curveless pair (e.g., `USDC/CNGN`) funded by a `[vault.uniswapV4]` position, without `referencePrice`/`maxDeviationBps` (the documented default/unguarded configuration).
2. Attacker takes a flash loan and swaps against the underlying Uniswap V4 pool to move `sqrtPriceX96` far from fair value.
3. Attacker (or an accomplice) submits an IntentGateway order sized to profit from the skewed rate.
4. `resolveLegRates()` → `getExoticTokenPrice()` reads the manipulated `slot0` state and returns a skewed `venueUsd`; `checkPriceGuard` passes trivially because no guard is configured.
5. The filler computes `targetOutput`/`finalOutputAmount` from the skewed rate and withdraws liquidity from its own Uniswap V4 position (`planWithdrawalForToken`) to pay it out, transferring more value than the true market rate warrants.
6. Attacker reverses the pool manipulation, keeping the arbitrage profit extracted from the solver's LP inventory. [6](#0-5) [7](#0-6)

### Citations

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

**File:** sdk/packages/simplex/src/config/filler-toml.ts (L23-36)
```typescript
/** TOML row for a Uniswap V4 position; only chain + tokenId required. */
export interface UniswapV4PositionToml {
	chain: string
	tokenId: string // bigint as string in TOML
	/**
	 * Optional price guard. When set (alongside `maxDeviationBps`), the filler rejects
	 * orders whenever the pool quote on this chain drifts more than `maxDeviationBps`
	 * from this static reference price (exotic per USD, same units as the bid/ask curves).
	 * Guards against a manipulated, stale, or thin pool.
	 */
	referencePrice?: string
	/** Tolerance in basis points for the price guard. Required when `referencePrice` is set. */
	maxDeviationBps?: number
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
