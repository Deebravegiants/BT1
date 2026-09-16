### Title
Simplex Solver Prices Intent Fills Off an Unmanipulation-Resistant Uniswap V4 Spot Price, Enabling Sandwich-Style Value Extraction from the Solver - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
When a Simplex trading pair has no configured bid/ask curves ("venue-priced" pairs), `FXFiller.resolveLegRates` prices intent fills directly from the current Uniswap V4 pool tick (`sqrtPriceX96`) via `UniswapV4FundingPlanner.getExoticTokenPrice` / `computeDirectPoolPriceUsd`, rather than a time-weighted or impact-aware price. This mirrors the reported Blueberry/Ichi bug class: a critical financial calculation (here, the amount a solver pays out to fill a user's cross-chain intent) is derived from a single-block AMM spot price that any unprivileged actor can move with an ordinary swap, with only a static-reference deviation check (`checkPriceGuard`) as a defense — not a TWAP, not an execution-cost/impact model.

### Finding Description
For curveless pairs whose `token0` is a USD stablecoin, `resolveLegRates` fetches `venueUsdPrice(chain, token1)`, which resolves to `UniswapV4FundingPlanner.getExoticTokenPrice`: [1](#0-0) 

That function selects the position with the largest pool liquidity and calls `computeDirectPoolPriceUsd`, which returns `sdkPool.token0Price`/`token1Price` — the **raw pool mid derived from `sqrtPriceX96`** at the current block, with no averaging over time and no depth/impact adjustment: [2](#0-1) 

This is documented explicitly by the project itself: "the raw pool mid derived from `sqrtPriceX96`... there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation from a static reference, not execution cost." [3](#0-2) 

The price is consumed directly in `resolveLegRates` to compute the fill rate that determines the amount of output tokens delivered to (or taken from) the counterparty of an intent: [4](#0-3) 

The only mitigation is `checkPriceGuard`, which rejects a quote only if it deviates from a static, operator-configured `referencePrice` by more than `maxDeviationBps` — and this guard is optional (`priceGuard` map may be empty), and even when present it is a coarse band (documented examples use 200 bps = 2%), not protection against short-term single-block manipulation within the band: [5](#0-4) [6](#0-5) 

The same unguarded/venue-priced value is also used to size the order notional for reorg-protection confirmation depth (`referenceRate`), so manipulation additionally degrades finality-safety sizing, not just the swap rate: [7](#0-6) 

### Impact Explanation
A single unprivileged actor can submit a normal swap on the referenced Uniswap V4 pool (optionally via flash loan) to move `sqrtPriceX96` within (or even outside, if no guard is configured, or the operator's reference is stale/wide) the deviation band, then immediately submit or trigger fill of an intent priced off that pool. Because the fill amount is computed by extending the manipulated mid price linearly across the entire order size with no impact term, the solver either:
- overpays the taker (loses solver-held liquidity/funds), or
- underpays relative to fair value on a leg where the solver is the taker's counterparty,

extracting value from the solver's escrowed/vault liquidity in a single transaction sequence. Since solver liquidity funds the fills that back the IntentGateway's cross-chain settlement, this is a concrete theft-of-funds vector against the intents/solver system, directly analogous to the reported Ichi LP liquidation exploit (spot-price-driven financial decision, single-block manipulable, no TWAP).

### Likelihood Explanation
Likelihood is Medium-High in deployments that configure venue (pool) pricing without a tight `referencePrice`/`maxDeviationBps` guard, or where the guard band (e.g. 2%) is wide relative to the pool's liquidity depth — cheaply movable with a flash-loan swap against thinner V4 pools (the docs explicitly note this is a known, only-partially-mitigated risk: "leaves the solver exposed to a manipulated, stale, or thin pool"). It requires no privileged access — only a swap transaction and an intent submission, both available to any user/order submitter.

### Recommendation
- Replace or augment the raw `sqrtPriceX96` mid with a TWAP/observation-based price (Uniswap V4 truncated oracle observations) for venue pricing, or require multiple block confirmations before trusting a pool quote.
- Apply an actual size/impact term (e.g., simulate the swap through the pool's liquidity) instead of extending the mid price linearly across the whole notional.
- Make `referencePrice`/`maxDeviationBps` mandatory (not optional) for venue-priced pairs, and tighten the default band, or cross-check the quote against a second independent price source (e.g., Chainlink) before pricing a fill.
- Apply the same manipulation-resistant price to the `referenceRate` confirmation-sizing path.

### Proof of Concept
1. Operator configures a Simplex `FXFiller` pair with `token0` a USD stable and no `bidPricePolicy`/`askPricePolicy` (curveless), funded via `[vault.uniswapV4]`, with either no price guard or a `maxDeviationBps` guard (e.g. 200 bps).
2. Attacker executes a large swap (optionally flash-loan funded) against the configured V4 pool moving `sqrtPriceX96`/mid price by up to just under the guard threshold (or unboundedly if unguarded).
3. Attacker (or colluding party) immediately submits an intent order on this pair sized so `resolveLegRates`/`computeDirectPoolPriceUsd` prices the fill off the manipulated mid, with `computeLegPolicyOutput` extending that price linearly with no slippage/impact term.
4. Solver fills the order per `venue-pricing-uniswap-v4-funded-pairs.md`'s documented path (`resolveLegRates` → `checkPriceGuard` → `computeLegPolicyOutput`), paying out (or receiving) tokens valued at the manipulated price rather than a true, manipulation-resistant market price, netting the attacker the difference at the solver's expense.

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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1339-1364)
```typescript
	/**
	 * Minimum-size reference rate (token1 per token0) for a leg's pair: the
	 * bid curve at 0 (the side token1-input legs trade at), falling back to the
	 * ask curve, then the live venue quote for venue-priced pairs.
	 */
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
