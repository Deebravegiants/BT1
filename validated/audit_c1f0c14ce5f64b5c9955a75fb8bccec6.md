### Title
Simplex's Uniswap V4 venue pricing uses unguarded spot price from thin pools, letting an attacker drain solver-funded fills - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Simplex's `UniswapV4FundingPlanner.getExoticTokenPrice` prices curveless intent-gateway pairs directly off a Uniswap V4 pool's instantaneous spot price (derived from `sqrtPriceX96`), with no TWAP, no minimum-liquidity requirement, and only an *optional* static-reference deviation guard. This reproduces exactly the bug class in the referenced report — a pool with too little (or too concentrated) liquidity can be cheaply manipulated to feed a bad price into the pricing/fill pipeline — except here there isn't even a time-weighted average to raise the cost of manipulation; it is a raw spot read.

### Finding Description
`getExoticTokenPrice` selects "the position with the largest pool liquidity" among the solver's *configured* positions and reads its current price via `computeDirectPoolPriceUsd`, which returns `sdkPool.token0Price`/`token1Price` — the pool's current mid, with no size/impact term and no fee-tier adjustment: [1](#0-0) [2](#0-1) 

"Largest liquidity" only compares among the solver's own configured positions — there is no absolute liquidity floor, so a solver with a single thin position (or all of whose configured positions are thin) is not protected at all. The only defense against a manipulated read is `checkPriceGuard`, which compares the quote to a *static* `referencePrice`/`maxDeviationBps` — and that guard is explicitly optional and can be entirely omitted ("omit both to leave the chain unguarded"): [3](#0-2) [4](#0-3) 

The flow this feeds is documented explicitly: the venue price becomes `rate = 1 / venueUsd`, which is then extended linearly across the whole filled quantity with no execution-cost or size term, and `checkPriceGuard` is called out as "the only defense on this path, and it checks deviation from a static reference, not execution cost": [5](#0-4) 

This is a stricter analog of the reported bug class: instead of a manipulation-resistant TWAP over an illiquid UniV3 pool, Simplex reads an unweighted spot price from a UniV4 pool, with no code-level liquidity threshold — precisely the missing control the external report recommends adding ("Set a liquidity threshold that is required from the pool in order to allow it as an oracle").

### Impact Explanation
An attacker who can move the exotic-token/stable pool's spot price (via a flash swap or any single-block trade) can, immediately after, submit an intent-gateway order sized to that pair. The manipulated price flows unguarded (if `priceGuard` is not configured for that chain) or bounded only by a static bps deviation (if it is configured) into `computeLegPolicyOutput`'s linear pricing, causing the solver to deliver more exotic tokens (drawn from its own Uniswap V4 LP position via `planWithdrawalForToken`) than the true market value of the user's input. Because the venue-priced pair "has no bid/ask spread of its own," there is no additional cushion beyond `order.fees` to absorb this — the solver's escrowed liquidity position can be drained at a discount. This is a concrete loss of solver funds (theft of value from the vault position), reachable by any unprivileged party who can trade against the underlying pool and then place/trigger a fill through the IntentGatewayV2 order flow.

### Likelihood Explanation
Likelihood is moderate-to-high wherever a solver configures `[vault.uniswapV4]` pricing for an exotic/thin pair without setting `referencePrice`/`maxDeviationBps` (explicitly documented as a valid, unguarded configuration), or where the configured deviation band is wide enough (or the pool thin enough) that a single-block manipulation still lands inside it. No time-weighting means the attacker does not need to sustain the manipulated price across multiple blocks as in a TWAP-based oracle — a single transaction preceding the fill suffices, which meaningfully lowers cost versus the original report's TWAP-manipulation scenario.

### Recommendation
- Enforce a minimum absolute liquidity/TVL threshold on qualifying Uniswap V4 pools before they may be used as a pricing source (as recommended by the source report), rather than only comparing relative liquidity among configured positions.
- Make the `referencePrice`/`maxDeviationBps` guard mandatory (fail closed) rather than optional for any pool-priced pair.
- Replace or supplement the instantaneous `sqrtPriceX96`-derived spot price with a time-weighted average (analogous to a TWAP) sampled over a window long enough to raise the cost of manipulation, and factor pool fee tier / size impact into `computeLegPolicyOutput` rather than extending the mid price linearly.

### Proof of Concept
1. Solver configures `[vault.uniswapV4]` for pair `USDC/CNGN` on chain `EVM-8453` with a single thin-liquidity position, omitting `referencePrice`/`maxDeviationBps` (a documented, supported configuration): [6](#0-5) .
2. Attacker executes a large swap against that pool to push `sqrtPriceX96` such that `token0Price`/`token1Price` misrepresents CNGN's true USD value.
3. Attacker (or an accomplice) immediately places an IntentGatewayV2 order on the `USDC/CNGN` pair sized within `maxOrderSize`.
4. `FXFiller.resolveLegRates` calls `venuePriceMemo()` → `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice`, which reads the manipulated spot price with no liquidity floor and (absent the guard) no deviation check: [7](#0-6) .
5. Solver fills the order at the manipulated rate, delivering more CNGN (withdrawn from its own V4 LP position) than the true market value of the received USDC, realizing a loss for the solver's vault.

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L390-407)
```typescript
	/**
	 * Queries funding venues for `token1Address`'s USD price on a chain.
	 * Uniswap V4 is preferred; falls back to other venues. Returns null when no
	 * venue can price the token there.
	 */
	private async getVenueUsdPrice(chain: string, token1Address: string): Promise<Decimal | null> {
		if (this.fundingVenues.length === 0) return null

		// Prefer V4, fall back to others
		const v4 = this.fundingVenues.filter((v) => v.name === "UniswapV4")
		const venues = v4.length > 0 ? v4 : this.fundingVenues

		for (const venue of venues) {
			const usdPrice = await venue.getExoticTokenPrice(chain, token1Address)
			if (usdPrice?.isPositive()) return usdPrice
		}
		return null
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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L48-66)
```text
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

<Callout type="info">
Startup validation requires a pricing source per pair: **either** bid/ask price curves, **or** at least one `[vault.uniswapV4]` position. A pair with neither fails validation.
</Callout>
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L1-22)
```markdown
# Venue pricing (Uniswap V4 funded pairs)

Verified 2026-08-19.

```
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

`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
