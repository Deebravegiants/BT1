I have enough evidence to establish the strongest reachable analog. Simplex's `UniswapV4FundingPlanner`/`FXFiller` venue-pricing path derives the fill price directly from the current pool tick/`sqrtPriceX96` (a single spot read), which is exactly the bug class from the report (`getOwnValuation` reading `slot0` as the price). This is reachable by an unprivileged order placer (the intent-order submitter), and the only defense is a static-reference deviation guard, not a TWAP or execution-cost check — an attacker who can move the pool's spot tick within one transaction can manipulate the fill price the solver commits real escrowed inventory against.

### Title
Venue-priced FX legs are quoted off a single manipulable Uniswap V4 spot price (`slot0`/tick), not a TWAP - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
`UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd` derives the USD price of an exotic token straight from `sdkPool.token0Price`/`token1Price`, which are computed from the pool's *current* `sqrtPriceX96` read via `StateView.getSlot0` on every refresh [1](#0-0) [2](#0-1) . `UniswapV4LiquidityState.refresh` fetches this spot value fresh right before it is used [3](#0-2) . `FXFiller.resolveLegRates`/`referenceRate` invert that spot USD price into the trade rate used both to size fills and to price the order for any curve-less pair whose `token0` is a USD stable [4](#0-3) [5](#0-4) . This is exactly the report's bug class: pricing critical, fund-moving logic off a single most-recent AMM spot read (`slot0`) instead of a time-weighted average.

### Finding Description
The only defense on this path is `checkPriceGuard`, which compares the live venue quote to a static, operator-configured `referencePrice` within `maxDeviationBps` — it does not check execution cost, pool depth, or price history, and it is entirely optional ("omit both to leave the chain unguarded") [6](#0-5) . The project's own internal flow notes confirm this is the *only* defense and that it checks deviation from a static reference, not execution cost, and that the raw pool mid is extended linearly across the whole quantity with no size/impact term [7](#0-6) . The docs likewise acknowledge: "Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote" [8](#0-7) .

Any unprivileged actor who can move the pool's spot tick within the guard's tolerance band (or on a chain left unguarded, arbitrarily) can submit an IntentGateway order sized to exploit that skewed rate. Because `resolveLegRates`'s venue price is a single number with "no bid/ask spread of its own" [9](#0-8) , and `computeLegPolicyOutput` linearly extends the manipulated mid across the whole order size, the solver's real escrowed inventory is priced entirely off a value the order-placer's own preceding transaction (or same-block sandwich) can influence.

### Impact Explanation
An attacker moving the Uniswap V4 pool's spot price (e.g. via a large swap or flash-loan-funded trade) immediately before placing/bidding on an IntentGateway order forces the solver to fill at the skewed rate, causing the solver's on-chain inventory (real ERC-20/vault funds committed to fills) to be transferred out at a manipulated exchange rate — a direct value-extraction/theft vector against the solver's escrowed capital, reachable from a single attacker-controlled transaction sequence.

### Likelihood Explanation
Likelihood is high on any thinly-liquid or newly-listed pool (the documented use case, e.g. cNGN/USDC), because moving `sqrtPriceX96` within a `maxDeviationBps` band (or on unguarded chains, with no bound at all) is cheap, and the guard is optional and static rather than adaptive to the manipulation itself.

### Recommendation
Replace or supplement the single `slot0`/current-tick read with a TWAP (Uniswap V4 truncated oracle observations) or require multi-block price confirmation before using a venue quote to size/price a fill; make `checkPriceGuard` mandatory for all venue-priced pairs rather than optional; and add a size/impact term (consulting `pos.fee` and pool depth) so `computeLegPolicyOutput` does not linearly extend a spot mid across the full order notional.

### Proof of Concept
1. Attacker observes a Simplex-operated pair configured with `[vault.uniswapV4]` venue pricing and either no `referencePrice`/`maxDeviationBps` guard, or a wide band [10](#0-9) .
2. Attacker swaps in the underlying Uniswap V4 pool to move `sqrtPriceX96`/tick so `computeDirectPoolPriceUsd` reports a favorable USD price for the exotic token [2](#0-1) .
3. Attacker immediately submits an IntentGateway order sized within `maxOrderSize`; `resolveLegRates` reads the skewed spot price (passes the static guard if configured loosely or absent) and prices the entire order notional at that rate [4](#0-3) .
4. Solver fills at the manipulated rate, transferring real inventory to the attacker at a loss; attacker reverses the pool-price manipulation (or lets arbitrageurs restore it), keeping the extracted spread.

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1344-1363)
```typescript
	private async referenceRate(
		leg: ResolvedLeg,
		venueUsdPrice: (chain: string, token1Address: string) => Promise<Decimal | null>,
	): Promise<Decimal | null> {
		const policy = leg.pair.bidPricePolicy ?? leg.pair.askPricePolicy
		if (policy) {
			const rate = policy.getPrice(new Decimal(0))
			return rate.gt(0) ? rate : null
		}
		// Venue-priced pair: token0 is USD-stable (constructor invariant), so the
		// venue's USD-per-token1 quote inverts straight into token1-per-token0.
		const venueUsd = await venueUsdPrice(leg.token1Chain, leg.token1Address)
		if (!venueUsd) return null
		const venueRate = new Decimal(1).div(venueUsd)
		// Same guard as trade pricing: this rate sizes the order's USD notional
		// for confirmation depth, and a manipulated pool understating the value
		// would shrink the reorg protection — the exact attack the guard exists
		// to stop. Refusing to size skips the order, consistent with pricing.
		if (!this.checkPriceGuard(undefined, leg.token1Chain, venueRate)) return null
		return venueRate
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L42-42)
```text
When **`[vault.uniswapV4]`** lists at least one position, cross-asset pairs without curves derive bid/ask prices from **Uniswap V4 pool state** (current tick). The pool acts as the price oracle instead of a static curve. Note this yields a **single** price used in both directions — a venue-priced pair has no bid/ask spread of its own, so its margin comes from `order.fees` alone.
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
