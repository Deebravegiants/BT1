This confirms the real fill path (`calculateProfitability`, not just phantom probing) uses `resolveLegRates` → the manipulable Uniswap V4 spot price as the actual quoted/paid rate, and the code's own comment explicitly flags that the overfill clamp is disabled, removing "the per-leg loss bound that previously protected against a bug / stale cache / manipulated venue price." This is a direct, code-acknowledged analog to the Balancer weighted-pool spot-price manipulation report: a spot AMM price (here Uniswap V4 `sqrtPriceX96` mid, not a TWAP) is used to size a real, escrow-releasing fill, guarded only by an optional static-reference band, with the compensating overfill ceiling explicitly disabled.

### Title
Uniswap V4 spot-price venue oracle for curveless pairs is flash-manipulable, and the compensating overfill clamp is disabled - (File: sdk/packages/simplex/src/strategies/fx.ts)

### Summary
`FXFiller` prices curveless (venue-priced) pairs from the live Uniswap V4 pool's spot price (`sqrtPriceX96`-derived mid), used directly to size real order fills that release escrow via `IntentGateway`/`ExtrinsicIntents`. The only protection, `checkPriceGuard`, is optional (must be explicitly configured) and only rejects if the spot price deviates from a static reference by more than `maxDeviationBps`; it does not resist a same-transaction manipulation that stays inside the configured band. The comment at [1](#0-0)  confirms the overfill clamp that used to bound losses from "a bug / stale cache / manipulated venue price" has been disabled, so a manipulated quote is paid out unclamped.

### Finding Description
`resolveLegRates` prices a curveless pair (token0 is a USD stable) from `getVenueUsdPrice`, which calls `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, deriving the price straight from the pool's current `sqrtPriceX96`/tick read via `StateView.getSlot0` [2](#0-1) [3](#0-2) . This is a single spot read of pool state, not a TWAP or execution-cost-aware quote, exactly the manipulable-balance class of oracle described in the reference report (pool balances/price manipulated by a large or flash trade before the read).

The rate is used on the real fill path, not only for phantom price probes: `calculateProfitability` → `resolveLegRates` → `computeLegPolicyOutput` computes `targetOutput`, which is paid out of the filler's wallet/vault and, when a `IntentGateway` order requires it, releases the user's escrowed input pro-rata to the outputs provided [4](#0-3) .

The only defense, `checkPriceGuard`, compares the live pool quote to a static per-chain `referencePrice` within `maxDeviationBps`, and is optional — "omit both to leave the chain unguarded" [5](#0-4) . Even when configured, it only rejects outliers past the band; it does not defend against manipulation that pushes the price to just inside the allowed band, nor does it account for the execution cost/fee tier the filler would actually pay to re-source inventory through the same pool, as the SDK's own docs note [6](#0-5) .

Critically, the code's own comment states the compensating safety net has been removed: `maxOverfillBps`/"Overfill detection is warn-only: the clamp is DISABLED... this removes the per-leg loss bound that previously protected against a bug / stale cache / manipulated venue price. Output is no longer capped; we only emit a warning." [7](#0-6) .

### Impact Explanation
An attacker who can move the Uniswap V4 pool's spot price (a flash swap or large trade before/alongside submitting an intent order) can inflate the `venueUsd` reading `getVenueUsdPrice` returns. Because `resolveLegRates` inverts this directly into the fill rate and `computeLegPolicyOutput`/`targetOutput` scales linearly with no size/impact term, the filler is forced to pay out an inflated amount of the exotic token for the user's stable-token input — directly extracting value from the solver's inventory (wallet balance and/or withdrawn Uniswap V4 LP positions) with each fill. Because the overfill clamp that previously bounded this exact failure mode is explicitly disabled, there is no second line of defense once the (optional) price guard is bypassed or simply left unconfigured for a chain. This is a concrete theft-of-funds vector against the intent solver's capital, an entity the intents/bid protocol depends on to service user orders.

### Likelihood Explanation
Likelihood is high for any deployment where the operator configures a `[vault.uniswapV4]` curveless pair without a `referencePrice`/`maxDeviationBps` guard (explicitly supported and documented as valid configuration), or where the pool used has thin liquidity such that a manipulation within the configured deviation band is cheap relative to the solver capital exposed. Manipulating a single pool's spot price via a flash swap is a standard, well-understood, low-cost attack requiring only a single transaction and no privileged access — well within reach of any user who can submit or influence an intent order on the destination chain.

### Recommendation
Do not price real fills off a single spot read of pool state. Use a manipulation-resistant price source (e.g., a time-weighted average price over multiple blocks, or an external oracle) for `getExoticTokenPrice`, and re-enable a hard per-leg overfill ceiling (rather than warn-only) so a stale/manipulated/buggy venue quote cannot pay out unbounded excess. Make the price guard (`referencePrice`/`maxDeviationBps`) mandatory for any curveless pair rather than optional, and additionally bound the guard window tightly enough that an in-band manipulation cannot exceed the solver's acceptable loss, and factor the pool's own fee tier/execution slippage into the quoted rate rather than using the raw mid.

### Proof of Concept
1. Operator configures a curveless pair (e.g. `USDC/CNGN`) priced from a `[vault.uniswapV4]` position, with no `referencePrice`/`maxDeviationBps` guard set (a supported configuration) [8](#0-7) .
2. Attacker executes a large swap (optionally via flash loan) against that Uniswap V4 pool immediately before submitting an intent order, moving `sqrtPriceX96` so `computeDirectPoolPriceUsd` reports an inflated USD price for the exotic token.
3. Attacker (or a colluding solver-facing order) submits an intent order for that pair; `FXFiller.calculateProfitability` calls `resolveLegRates`, which reads the manipulated venue price with no guard to reject it, then `computeLegPolicyOutput` computes `targetOutput` at that inflated rate [4](#0-3) .
4. Because the overfill clamp is disabled (warn-only), the filler pays out the full unclamped, inflated `targetOutput` from its wallet/LP inventory [7](#0-6) , transferring excess value to the attacker relative to the pool's un-manipulated price, funded by the solver's own capital.
5. Attacker reverses the initial swap (or lets arbitrageurs correct it), pocketing the difference at the solver's expense.

### Citations

**File:** sdk/packages/simplex/src/strategies/fx.ts (L622-634)
```typescript
				const rates = await this.resolveLegRates(order.id, leg, cappedNotional, venueUsdPrice)
				if (!rates) return 0
				legRatesByIndex.set(i, rates)

				const remaining = remainingByPair.get(leg.pair) ?? new Decimal(0)
				const legResult = this.computeLegPolicyOutput(
					input.amount,
					leg.inputIsToken0,
					token0Decimals,
					token1Decimals,
					remaining,
					rates.rate,
				)
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L678-700)
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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-272)
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
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L64-72)
```text
<Callout type="info">
Startup validation requires a pricing source per pair: **either** bid/ask price curves, **or** at least one `[vault.uniswapV4]` position. A pair with neither fails validation.
</Callout>

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
