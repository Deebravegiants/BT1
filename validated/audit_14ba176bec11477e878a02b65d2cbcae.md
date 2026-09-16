### Title
Uniswap V4 pool mid-price used for both quoting and the price guard ignores swap fee tier and price impact, letting a solver's own LP-funded fills execute worse than the price it accepted - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
In the Sherlock report, a JUSDV1 liquidator's `expectPrice` check is validated against a Chainlink price while the actual liquidation trade executes on Uniswap, so slippage/price movement between the two sources makes the check meaningless. The analogous defect in Hyperbridge's Simplex filler is in the Uniswap V4 venue-pricing path used by `FXFiller`: the price a solver checks and prices a fill against (`computeDirectPoolPriceUsd`, gated only by `checkPriceGuard`) is a raw pool mid computed from `sqrtPriceX96`, while the price the solver will actually realize when it has to withdraw liquidity from its own position to fund the fill is worse by the pool's fee tier plus any size-driven price impact — neither of which is applied anywhere in the pricing path.

### Finding Description
`FXFiller.resolveLegRates` and `referenceRate` price venue-based pairs from `venueUsdPrice` / `getVenueUsdPrice`, which resolves to `UniswapV4FundingPlanner`'s pool state. [1](#0-0) 
The only defense on this quoted price is `checkPriceGuard`, which compares the quote against a static `referencePrice` within `maxDeviationBps` — a deviation check, not an execution-cost check. [2](#0-1) 
The underlying flow documentation states explicitly that the pool's fee tier is read and stored (`pos.fee`) but never applied to the price, and that there is no size/impact term at all — `computeLegPolicyOutput` extends the raw mid linearly across the whole priced quantity, and `checkPriceGuard` "checks deviation from a static reference, not execution cost." [3](#0-2) 
When the solver's wallet balance is insufficient to cover a fill priced at that mid, `UniswapV4FundingPlanner.planWithdrawalForToken` withdraws liquidity from the same pool to source the shortfall, so the fill is priced from a mid quote that never reflected the fee/impact cost of the very withdrawal that funds it. [4](#0-3) 
This mirrors the JUSDV1 root cause precisely: the value used to gate/accept a trade (Chainlink price / pool mid) is a different economic quantity than the value the trade will actually clear at (Uniswap execution price / fee-and-impact-adjusted pool price), and only the mismatch's magnitude — not its existence — is bounded.

### Impact Explanation
An order placer can size orders (or repeatedly place orders) against a venue-priced pair specifically so that the solver's wallet balance is exhausted and it must fund fills by withdrawing LP liquidity from its own Uniswap V4 position. Every such fill is priced using the fee-tier-free, impact-free mid, so the solver systematically pays out more value (in the destination token) than the true cost of sourcing that inventory, realizing a loss on every LP-funded fill. Because `maxOrderSize`/`checkPriceGuard` bound only price deviation from a static reference — not the swap cost of self-funding — this loss is not caught by any existing guard and can be repeated to drain the solver's LP position value over time. This is a direct, repeatable fund-loss vector against an intent solver participating in Hyperbridge's IntentGatewayV2 flow.

### Likelihood Explanation
Likelihood is Medium: the vulnerable path only activates when a curve-less, venue-priced pair is configured (an opt-in configuration) and the solver's wallet balance for the output token is insufficient, forcing the LP-funding branch. An attacker does not need any privileged access — placing ordinary orders sized above the solver's held balance is sufficient to force the mispriced funding path, and this can be done repeatedly against any solver that has adopted the Uniswap V4 LP-funding feature.

### Recommendation
Incorporate the pool's actual fee tier and a size-dependent price-impact term into the price used both by `checkPriceGuard` and by `computeLegPolicyOutput`/`referenceRate` when a leg will be (or might be) LP-funded, rather than using the unadjusted `sqrtPriceX96` mid. Alternatively, price LP-funded legs directly from the simulated `removeCallParameters`/position withdrawal output (the same quantity `planWithdrawalForToken` computes) instead of from the raw pool mid, so the accept/gate check and the executed economics are drawn from the same source, closing the same class of check-vs-execution mismatch identified in the JUSDV1 report.

### Proof of Concept
1. Configure a Simplex filler with a curve-less pair funded via `[vault.uniswapV4]`, per the documented example. [5](#0-4) 
2. Attacker places an `IntentGatewayV2` order in that pair sized larger than the solver's current wallet balance of the output token, forcing `planWithdrawalForToken` to source the deficit from the configured LP position. [6](#0-5) 
3. `FXFiller` prices/accepts the leg using `getExoticTokenPrice`/`computeDirectPoolPriceUsd`'s raw mid (validated only by `checkPriceGuard`'s deviation band), with no deduction for the pool's fee tier or the price impact of the liquidity removal that will actually fund the fill. [7](#0-6) 
4. The solver executes the fill at the accepted (mid) rate while its real cost of sourcing inventory is higher by the fee tier and impact, realizing a loss each time; repeating step 2 against the same solver drains value over multiple fills.

### Citations

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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L6-16)
```markdown
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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L293-330)
```typescript
	async planWithdrawalForToken(
		destChain: string,
		solver: HexString,
		tokenOutLower: string,
		amountNeeded: bigint,
		deadlineTimestamp?: bigint,
	): Promise<FundingPlanResult> {
		const noopResult: FundingPlanResult = { calls: [], credited: 0n }

		this.logger.debug(
			{
				destChain,
				solver,
				tokenOutLower,
				amountNeeded: amountNeeded.toString(),
			},
			"UniswapV4 planWithdrawalForToken called",
		)

		if (amountNeeded <= 0n) return noopResult

		const state = this.stateByChain.get(destChain)
		if (!state || !state.isHydrated()) {
			this.logger.debug(
				{ destChain, hasState: !!state, isHydrated: state?.isHydrated() },
				"UniswapV4 no state or not hydrated",
			)
			return noopResult
		}

		const mutex = this.mutexByChain.get(destChain)!
		return mutex.runExclusive(async () => {
			// Refresh on-chain state for this chain right before planning so
			// liquidity and price data are as fresh as possible.
			await state.refresh()

			const tokenNeed = tokenOutLower.toLowerCase()
			const candidates = state
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L348-418)
```typescript
			let remaining = amountNeeded
			const allCalls: ERC7821Call[] = []
			let totalCredited = 0n

			for (const pos of candidates) {
				if (remaining <= 0n) break

				const availLiq = state.remaining(pos.tokenId)
				if (availLiq === 0n) continue

				const isToken0 = pos.currency0.toLowerCase() === tokenNeed

				// Bump the target by the slippage tolerance (10 bps) so the V4
				// withdrawal overshoots the exact amount needed.  This ensures
				// that even in the worst-case slippage scenario the credited
				// tokens still cover the fill requirement, avoiding a wasted
				// revert on the entire ERC-7821 batch.
				const slippageBps = BigInt(this.slippageTolerance.numerator.toString()) * 10_000n / BigInt(this.slippageTolerance.denominator.toString())
				const bufferedRemaining = remaining + (remaining * slippageBps) / 10_000n

				// Use binary search to find the minimal liquidity that covers the buffered target
				const neededLiq = this.findLiquidityForDeficit(state, pos, isToken0, bufferedRemaining)
				if (neededLiq <= 0n) continue

				const cappedLiq = neededLiq > availLiq ? availLiq : neededLiq

				// Resolve the percentage the calldata will carry *before* pricing the
				// withdrawal, and price it from the liquidity that percentage actually
				// decreases. Pricing `cappedLiq` instead over-credits by the SDK's
				// truncation, and the fill sized against that credit reverts.
				const removal = liquidityRemoval(pos.liquidity, cappedLiq)
				if (!removal) continue

				// Build SDK Position to compute expected amounts
				const sdkPosition = state.buildSdkPosition(pos.tokenId, removal.liquidity)
				if (!sdkPosition) continue

				// The SDK Position computes amounts for the given liquidity
				const amount0 = BigInt(sdkPosition.amount0.quotient.toString())
				const amount1 = BigInt(sdkPosition.amount1.quotient.toString())
				const credit = isToken0 ? amount0 : amount1

				this.logger.debug(
					{
						tokenId: pos.tokenId.toString(),
						isToken0,
						sqrtPriceX96: pos.sqrtPriceX96.toString(),
						neededLiq: neededLiq.toString(),
						availLiq: availLiq.toString(),
						cappedLiq: cappedLiq.toString(),
						removedLiq: removal.liquidity.toString(),
						amount0: amount0.toString(),
						amount1: amount1.toString(),
						credit: credit.toString(),
						requestedDeficit: remaining.toString(),
						bufferedDeficit: bufferedRemaining.toString(),
					},
					"UniswapV4 per-position calculation",
				)

				if (credit === 0n) continue

				// Use V4PositionManager.removeCallParameters to generate the calldata
				// This encodes DECREASE_LIQUIDITY + TAKE_PAIR actions internally
				const call = this.buildRemoveLiquidityCall(state, pos, removal.percentage, deadlineTimestamp)
				if (!call) continue

				allCalls.push(call)
				totalCredited += credit
				remaining -= credit
				state.consume(pos.tokenId, removal.liquidity)
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L40-62)
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
```
