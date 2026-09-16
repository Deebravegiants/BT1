### Title
Simplex FXFiller venue pricing trusts unmitigated Uniswap V4 spot price, letting an attacker manipulate a thin pool to over-extract solver funds - (File: sdk/packages/simplex/src/strategies/fx.ts)

### Summary
The Simplex intent-filler's `FXFiller` strategy prices "venue" (curveless) trading pairs directly from a Uniswap V4 pool's current spot price (`sqrtPriceX96`-derived `token0Price`/`token1Price`), with no TWAP and only an *optional* static reference-price guard. This mirrors the Paraspace bug class: a spot price read from a possibly thin, single-block-manipulable AMM pool is used to value assets and drive a protocol-level payout decision, without any liquidity/TVL floor.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` iterates the solver's configured V4 positions and returns `computeDirectPoolPriceUsd`, which is just the pool's current mid price (`sdkPool.token0Price`/`token1Price`, derived from live `sqrtPriceX96`): [1](#0-0) [2](#0-1) 

This is consumed by `FXFiller.getVenueUsdPrice` / `venuePriceMemo`, which is the price source for any curveless ("venue-priced") pair when the filler evaluates an order (`calculateProfitability` → `resolveLegRates` → `computeLegPolicyOutput`): [3](#0-2) 

The only defense is `checkPriceGuard`, which is explicitly optional — a chain with no configured `referencePrice`/`maxDeviationBps` is "unguarded": [4](#0-3) 

The project's own internal docs acknowledge the design has no defense against manipulation beyond that static-deviation guard, and that the guard only checks deviation from a fixed reference, not execution cost or pool depth: "Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote," and `checkPriceGuard` "is the only defense on this path, and it checks deviation from a static reference, not execution cost": [5](#0-4) [6](#0-5) 

Additionally, the overfill clamp that historically bounded the loss from a bad/manipulated venue price has been explicitly disabled: "the clamp is DISABLED, so the filler fills the full computed amount even when it exceeds (1 + maxOverfillBps) × user-requested — including venue-priced legs (e.g. Uniswap V4)... Output is no longer capped; we only emit a warning": [7](#0-6) 

This is directly analogous to the ParaSpace report: an oracle reads a live, unweighted (non-TWAP) AMM spot price with no minimum-liquidity/TVL check, and that price is fed straight into a payout/valuation calculation reachable from an ordinary user action (here, submitting a cross-chain intent order that Simplex must price and fill).

### Impact Explanation
If an attacker can move the spot price of the configured Uniswap V4 pool (e.g., a low-liquidity pool for an exotic asset like cNGN, where the solver's own LP position may constitute most of the depth), they can:
1. Manipulate the pool's `sqrtPriceX96` with a swap.
2. Submit (or wait for) an intent order that FXFiller prices as a venue pair; `getExoticTokenPrice` returns the manipulated spot price with no TVL/liquidity floor check and (absent config) no deviation guard.
3. The filler computes an inflated `policyMaxOutput` for the exotic token and, because the overfill clamp is disabled, pays out the full unclamped (manipulated) amount, extracting excess funds from the solver's own inventory/liquidity position for the input token received.
4. The attacker reverses the manipulation afterward, netting a profit funded by the Simplex solver — a concrete loss of funds analogous to Paraspace's Lending Pool being put "in loss."

This can result in direct, sustained fund loss to the solver whenever a `priceGuard` is not configured for the chain, or even when configured but the manipulation stays within the allowed `maxDeviationBps` band (a band chosen for legitimate volatility, not adversarial manipulation resistance).

### Likelihood Explanation
Likelihood is Medium: exploitation requires (a) a venue-priced pair configured without `[vault.uniswapV4].referencePrice`/`maxDeviationBps` (an explicitly optional, "leave the chain unguarded" configuration per the docs), or a guard band wide enough to still allow profitable manipulation, and (b) a Uniswap V4 pool with liquidity thin enough (or dominated by the solver's own LP) to be manipulated profitably relative to gas/swap-fee costs — exactly the scenario the original report demonstrates is realistic and has real-world precedent (thin USDC/USDT-style pools). The attack is reachable by any unprivileged party who can submit an order and perform a public swap; no relayer, governance, or admin privilege is needed.

### Recommendation
- Require a TWAP (time-weighted average price) read from the Uniswap V4 pool rather than the instantaneous `sqrtPriceX96`/`token0Price`/`token1Price` mid, or at minimum use a multi-block observation window.
- Make the `priceGuard` (`referencePrice`/`maxDeviationBps`) mandatory for every venue-priced chain/pair rather than optional, and additionally validate pool depth/TVL against a configured minimum before trusting its quote.
- Re-enable (or add configurable) hard clamping of overfill for venue-priced legs instead of only warning, since the "overfill ceiling exceeded" path currently lets an unclamped, potentially manipulated amount through unconditionally.
- Consider cross-checking the venue price against an independent oracle/off-chain feed before using it to size a fill.

### Proof of Concept
1. Configure (or find) a Simplex `FXFiller` deployment with a curveless pair (e.g., `USDC/CNGN`) priced via `[vault.uniswapV4]`, without `referencePrice`/`maxDeviationBps` set for that chain (an explicitly supported, unguarded configuration per `sdk/packages/simplex/src/config/filler-toml.ts` and the pricing docs).
2. Attacker performs a large swap against the configured Uniswap V4 pool (thin/low-TVL, as in the original report's WETH/DAI example) to push `sqrtPriceX96` far from fair value in the direction that inflates the exotic token's `priceUsd`.
3. Attacker submits (or a bystander's) cross-chain order requesting the exotic token as output; `FXFiller.calculateProfitability` calls `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice`, which reads the manipulated spot price with no TVL check (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`).
4. `resolveLegRates`/`computeLegPolicyOutput` compute an inflated `policyMaxOutput`; since the overfill clamp is disabled (`fx.ts:678-701`), the filler pays the unclamped, manipulated amount out of its own wallet/LP-funded inventory.
5. Attacker reverses the pool manipulation with a second swap, closing the position at a net profit funded by the solver's loss. [1](#0-0) [4](#0-3) [7](#0-6)

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L390-420)
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

	/** Per-evaluation memo over `getVenueUsdPrice`, keyed by (chain, token1). */
	private venuePriceMemo(): (chain: string, token1Address: string) => Promise<Decimal | null> {
		const cache = new Map<string, Decimal | null>()
		return async (chain: string, token1Address: string) => {
			const key = `${chain}:${token1Address}`
			const cached = cache.get(key)
			if (cached !== undefined) return cached
			const price = await this.getVenueUsdPrice(chain, token1Address)
			cache.set(key, price)
			return price
		}
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L678-701)
```typescript
				// Overfill detection is warn-only: the clamp is DISABLED, so the filler
				// fills the full computed amount even when it exceeds
				// (1 + maxOverfillBps) × user-requested — including venue-priced legs
				// (e.g. Uniswap V4). NOTE: this removes the per-leg loss bound that
				// previously protected against a bug / stale cache / manipulated venue
				// price. Output is no longer capped; we only emit a warning.
				const overfillCeiling = (output.amount * (10000n + this.maxOverfillBps)) / 10000n
				const policyMaxOutput = rawPolicyMaxOutput
				if (rawPolicyMaxOutput > overfillCeiling) {
					this.logger.warn(
						{
							orderId: order.id,
							leg: i,
							pair: `${leg.pair.token0}/${leg.pair.token1}`,
							token: output.token,
							userRequested: output.amount.toString(),
							unclamped: rawPolicyMaxOutput.toString(),
							ceiling: overfillCeiling.toString(),
							maxOverfillBps: this.maxOverfillBps.toString(),
							priceSource: rates.priceSource,
						},
						"Overfill ceiling exceeded — clamp disabled, filling unclamped amount",
					)
				}
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-73)
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
