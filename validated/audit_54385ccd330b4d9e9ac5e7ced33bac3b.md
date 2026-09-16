### Title
FXFiller overpays solver funds against a manipulated, unbounded Uniswap V4 pool-mid price (`UniswapV4FundingPlanner.computeDirectPoolPriceUsd` / `FXFiller.fx.ts` overfill clamp disabled)

### Summary
The wKeyDAO exploit worked because `buy()` derived its price from a spot on-chain value (effectively an AMM-style reserve ratio) with no manipulation resistance, and the sell path then dumped through PancakeSwap using that same manipulable market — an attacker could move the price with capital they controlled (via flashloan) and profit at the protocol's expense, since nothing capped how far the computed output could drift from fair value.

The Hyperbridge Simplex filler's venue-pricing path for Uniswap V4-funded pairs has the same structural weakness: it prices exotic tokens directly off `sqrtPriceX96` and pays out real escrowed/vault funds against that price, and the one safety valve that used to bound the resulting loss (an overfill ceiling) has been explicitly disabled.

### Finding Description
For curve-less pairs, `FXFiller.resolveLegRates` (`sdk/packages/simplex/src/strategies/fx.ts:1443-1479`) sources the trading rate from `venueUsdPrice`, which resolves to `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-275`). [1](#0-0) 

`computeDirectPoolPriceUsd` returns the raw pool mid (`sdkPool.token0Price`/`token1Price`), derived purely from the current `sqrtPriceX96` — the same class of "spot value with no manipulation resistance" that the wKeyDAO `buy()` function relied on. As documented in-repo: [2](#0-1) 

The only mitigation, `checkPriceGuard`, compares the live quote to a *static* reference price within `maxDeviationBps` — it is optional (unset by default), and even when configured it bounds deviation from a stale number, not execution/impact cost: [3](#0-2) 

Critically, the per-leg loss bound that used to cap how far the computed output could exceed the user's requested amount (`overfillCeiling`) has been deliberately disabled — the code now only logs a warning and pays the full, unclamped, price-derived amount: [4](#0-3) 

So an attacker can: (1) submit an intent order on a venue-priced (curve-less, USD-stable-token0) pair whose exotic-token leg is priced from a thin Uniswap V4 pool, (2) sandwich/flashloan-manipulate that pool's `sqrtPriceX96` immediately before the filler evaluates and fills the order, pushing `computeDirectPoolPriceUsd`'s USD-per-exotic-token quote in the direction that inflates the solver's required payout, and (3) collect an output amount from the solver's escrow/vault far beyond fair value, with no ceiling stopping it since the overfill clamp is disabled and the price guard is optional/deviation-only. This is a single order (an "intent" reachable by any unprivileged user) that drives a state-changing, fund-releasing action (`fillOrder`) off an unprotected, spot-priced venue quote — the same root cause as the DeFiHackLabs wKeyDAO report.

### Impact Explanation
A successful attack directly drains real solver/vault funds (USDC/USDT and paired exotic tokens) sourced from Uniswap V4 LP positions and wallet balances, since the fill amount is computed from an attacker-manipulable price and is no longer capped by the overfill ceiling. This is concrete theft of solver capital reachable by a single crafted order plus a pool-price manipulation transaction, which the intents flow (`fillOrder`, `IntrinsicIntents._fillSameChain`) will faithfully pay out per the surplus-splitting logic once the solver commits to the computed `desiredOutput`/`policyMaxOutput`.

### Likelihood Explanation
Any curve-less pair with a `[vault.uniswapV4]` position and no (or a loosely configured) price guard is exposed. Thin or low-liquidity Uniswap V4 pools used for venue pricing are inexpensive to move with a flashloan, and the code comments themselves acknowledge this is the exact scenario the (now-disabled) overfill clamp used to guard against: "this removes the per-leg loss bound that previously protected against a bug / stale cache / manipulated venue price."

### Recommendation
Re-enable and enforce the per-leg overfill ceiling (reject or clamp fills whose `policyMaxOutput` exceeds `(1 + maxOverfillBps) × output.amount`) rather than only warning. Additionally, make the Uniswap V4 price guard mandatory (not optional) for venue-priced pairs, and strengthen it to account for trade size/impact (e.g., a TWAP or impact-aware quote) rather than only comparing the instantaneous mid against a static reference.

### Proof of Concept
1. Configure/attack a filler serving a curve-less pair funded by a thin Uniswap V4 position with no `referencePrice`/`maxDeviationBps` guard set (or one loose enough to pass).
2. Attacker flashloan-swaps in the pool to shift `sqrtPriceX96` so `computeDirectPoolPriceUsd` reports an inflated USD price for the exotic token.
3. Attacker (or accomplice) places an intent order on that pair sized to this leg.
4. `FXFiller.resolveLegRates` → `computeLegPolicyOutput` computes `policyMaxOutput` from the manipulated rate; because the overfill clamp at `fx.ts:678-701` only logs a warning, the filler pays the full unclamped (inflated) amount from its Uniswap V4/wallet funds.
5. Attacker reverses the pool manipulation in the same transaction bundle, pocketing the difference between the manipulated payout and the pool's true value.

### Citations

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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
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
