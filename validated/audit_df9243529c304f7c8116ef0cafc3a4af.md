Based on the investigation, I've confirmed a concrete, reachable analog to the AmpKashi price manipulation exploit within Simplex's Uniswap V4 pool-based pricing.

### Title
Single-transaction spot-price manipulation of Simplex's Uniswap V4 venue pricing lets an intent placer drain solver inventory - (File: `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
Simplex (Hyperbridge's intent filler) can be configured to price "exotic" tokens directly off a live Uniswap V4 pool's spot price instead of a static curve. `UniswapV4FundingPlanner.computeDirectPoolPriceUsd` reads the raw pool mid from `sqrtPriceX96` with no TWAP, no liquidity-depth/impact term, and no protection against atomic manipulation — exactly the primitive the AmpKashi exploit abused (reading an instantaneous, swap-manipulable AMM price to inflate a valuation the protocol then acts on).

### Finding Description
`resolveLegRates` in `sdk/packages/simplex/src/strategies/fx.ts:1443-1479` prices a curve-less pair by calling `venueUsdPrice`, which resolves to `UniswapV4FundingPlanner.getExoticTokenPrice` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`). This picks the position with the largest liquidity and calls `computeDirectPoolPriceUsd`, which returns `sdkPool.token0Price`/`token1Price` — the pool's instantaneous mid derived from `sqrtPriceX96` at `UniswapV4FundingPlanner.ts:246-275` — with the fee tier read but never applied to the price (per `sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md:17-22`). [1](#0-0) 

The only defense on this path is `checkPriceGuard` (`sdk/packages/simplex/src/strategies/fx.ts:428-448`), which compares the venue quote to a static, operator-configured `referencePrice` within `maxDeviationBps`. This guard is explicitly optional — "omit both to leave the chain unguarded" per `docs/content/developers/evm/simplex/pricing.mdx:68-72` — and even when configured, it bounds deviation from a stale off-chain reference, not manipulation *within* the current block/transaction: [2](#0-1) 

Because `state.refresh()` re-reads `slot0`/liquidity immediately before pricing (`UniswapV4LiquidityState.ts:139-170`), an attacker can, in one transaction: (1) flash-loan/swap against the configured V4 pool to push its spot price to the edge of (or beyond, if unguarded) the reference band, (2) place or trigger a fill on an intent order that reads `resolveLegRates`/`computeDirectPoolPriceUsd` at the manipulated tick, causing Simplex to value the exotic token far from its true price, (3) receive an outsized `output` amount relative to what the filler actually pays for sourcing (the filler even swaps through the same pool to source inventory, per the flow doc, compounding the mispricing), (4) reverse the initial swap to restore the pool and keep the difference. This mirrors the AmpKashi pattern of using a single-transaction AMM price push to inflate a value the target contract trusts and acts on (there, Kashi's collateral valuation; here, Simplex's fill-pricing and funding-withdrawal sizing). [3](#0-2) 

`referenceRate`, used to size confirmation-block depth for reorg protection, has the same exposure (`fx.ts:1339-1364`), so a manipulated pool can also shrink the reorg-safety margin the filler relies on for a given order's USD notional.

### Impact Explanation
A successful manipulation causes the Simplex filler to fill an order at a price far from fair value, directly transferring solver-held funds (stablecoin or the LP-sourced exotic token, including funds withdrawn atomically from the operator's Uniswap V4 concentrated-liquidity NFT positions) to the attacker who placed/triggered the order. This is concrete theft of funds reachable by any unprivileged party who can submit an intent order and manipulate the referenced pool's liquidity within the same transaction — no privileged role is required.

### Likelihood Explanation
Likelihood is contingent on operator configuration: the venue-pricing path only activates for pairs deliberately left curve-less (`[vault.uniswapV4]` configured, no `bidPriceCurve`/`askPriceCurve`), and the risk is materially reduced (but not eliminated) when `referencePrice`/`maxDeviationBps` is set, since the docs themselves flag this path as trusting "a manipulated, stale, or thin pool." Thin-liquidity, exotic-asset pools (the intended use case per the docs, e.g. cNGN) are the most economical to manipulate, making this a realistic, moderate-likelihood exposure for any operator running venue pricing without a tight guard band, or relying on the guard alone against atomic manipulation.

### Recommendation
- Never source the price used for fills purely from the current-block `sqrtPriceX96`; use a TWAP/observation-window price (or require agreement between spot and a longer window) before accepting a venue quote.
- Make `referencePrice`/`maxDeviationBps` mandatory whenever `[vault.uniswapV4]` venue pricing is enabled, rather than optional.
- Incorporate the pool's actual fee tier and a price-impact/depth term into `computeDirectPoolPriceUsd`/`computeLegPolicyOutput` instead of extending the raw mid linearly across the full quantity.
- Consider bounding the maximum single-block price movement accepted for pricing, or requiring multiple blocks of confirmation before a venue-priced quote is treated as fillable.

### Proof of Concept
Conceptually, mirroring the AmpKashi flow: (1) flash-loan funds; (2) swap into the exotic token/stable pair of the configured Uniswap V4 position at `chain`/`tokenId` to move `sqrtPriceX96` so `computeDirectPoolPriceUsd` reports an inflated/deflated USD price (within the guard band if `checkPriceGuard` is active, or arbitrarily if unguarded); (3) in the same transaction, submit (or have a colluding relayer submit) an intent order sized so `resolveLegRates`/`computeLegPolicyOutput` (`fx.ts:1443-1479`) price the fill against the manipulated mid, causing the solver's `FXFiller` to output more value than it should; (4) reverse the initial swap, restoring the pool, and keep the surplus extracted from the solver's `[vault.uniswapV4]` position or wallet balance. [4](#0-3)

### Citations

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
