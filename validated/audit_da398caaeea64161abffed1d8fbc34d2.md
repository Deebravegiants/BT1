### Title
Simplex venue pricing uses raw spot pool price with no impact/fee term, letting a sandwich attack force the solver to fill intents at a manipulated price - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Curveless trading pairs priced against a Uniswap V4 venue are quoted from the pool's raw spot mid (`sqrtPriceX96`), with no size/impact term and no slippage-aware execution check. An attacker can sandwich the solver's fill transaction—moving the pool price immediately before the solver reads it (or before the solver's own withdrawal swap executes), extracting value from the solver's fill in a pattern analogous to the sandwich attack against OLY described in the external report.

### Finding Description
`FXFiller.getVenueUsdPrice` / `venuePriceMemo` route curveless, USD-anchored pairs to `UniswapV4FundingPlanner.getExoticTokenPrice`, which selects the most-liquid qualifying pool and calls `computeDirectPoolPriceUsd`: [1](#0-0) 

This returns `sdkPool.token0Price`/`token1Price` — the pool's instantaneous spot price computed directly from live `sqrtPriceX96` fetched from `StateView.getSlot0` at `refresh()` time: [2](#0-1) 

As documented internally, this price has no fee-tier or size/impact adjustment applied — `computeLegPolicyOutput` extends this mid linearly across the full priced notional: [3](#0-2) 

The only defense, `checkPriceGuard`, rejects a quote only if it deviates from a static, operator-configured `referencePrice` by more than `maxDeviationBps`: [4](#0-3) 

This guards against gross oracle staleness/misconfiguration, not against an attacker moving the pool within the guard band (or within the band the operator must set wide enough to accommodate normal volatility) immediately around the solver's price-read and fill. Because the same pool is also the solver's *funding source* (liquidity is withdrawn from this V4 position to source outbound tokens via `planWithdrawalForToken`), an attacker who front-runs with a large swap in one direction, waits for the solver to price and fill the user's intent order against the moved price, then back-runs to restore the pool, extracts the price delta as the solver's fill and its own withdrawal both execute against the manipulated mid.

### Impact Explanation
Any account can place an intent order (`IntentGatewayV2` order) against a curveless, Uniswap-V4-venue-priced pair. The pricing path is reachable from a single submitted order — no privileged role needed. A successful sandwich forces the solver to price/fill at an off-market rate, resulting in direct value loss to the solver's inventory (theft of solver funds via mispriced output) each time it fills against a manipulated venue price, mirroring the "sandwich attack" bug class from the external report where a spot AMM price used for settlement was manipulated within a single block for profit.

### Likelihood Explanation
Uniswap V4 pools without hooks enforcing TWAP or minimum-notional MEV protection are trivially manipulable within a single block by any actor with enough capital/flash liquidity, and BSC/EVM sandwich bots (as referenced in the external OLY report) are common and automated. The `maxDeviationBps` guard must be wide enough to tolerate legitimate price movement, which leaves room for a same-block manipulation within that band. This is a straightforward, repeatable MEV strategy for any curveless venue-priced pair Simplex operators configure.

### Recommendation
Do not price fills off the pool's instantaneous `sqrtPriceX96` alone. Use a TWAP/time-weighted observation (or a short observation window) for `computeDirectPoolPriceUsd`, apply the pool's fee tier and a size/impact term proportional to the priced notional relative to available liquidity (as already noted needed in the internal flow doc), and/or require a minimum on-chain confirmation delay or commit-reveal before executing withdrawal-and-fill, so a single-block sandwich cannot both move the price and have the solver settle against it atomically.

### Proof of Concept
1. Operator configures a curveless pair (e.g. USDC/CNGN) priced from `[vault.uniswapV4]`, with a `maxDeviationBps` guard band wide enough for normal daily volatility (e.g. 200 bps as shown in `docs/content/developers/evm/simplex/pricing.mdx`).
2. Attacker submits a large swap into the configured V4 pool, shifting `sqrtPriceX96` by just under `maxDeviationBps`.
3. Attacker (or a colluding user) immediately places an intent order that the solver's `FXFiller.canFill`/pricing path fills against the now-skewed `getExoticTokenPrice` result, since `checkPriceGuard` passes (deviation is within the configured band).
4. Solver's fill (and any `planWithdrawalForToken` liquidity removal used to fund it) executes at the manipulated mid.
5. Attacker back-runs with the reverse swap, restoring the pool price and capturing the spread as profit extracted from the solver, analogous to the $63,400 OLY sandwich loss cited in the external report.

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L149-170)
```typescript
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
