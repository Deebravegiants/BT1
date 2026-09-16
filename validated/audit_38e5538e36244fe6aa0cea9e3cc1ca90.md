### Title
Order fills are sized off the pre-swap Uniswap V4 pool mid while the actual withdrawal executes against a different, post-impact price - (File: `sdk/packages/simplex/src/strategies/fx.ts`, `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
For curveless, pool-priced pairs, `FXFiller.resolveLegRates` quotes and sizes an intent fill using the raw Uniswap V4 pool mid price returned by `UniswapV4FundingPlanner.getExoticTokenPrice`/`computeDirectPoolPriceUsd`, which is derived purely from `sqrtPriceX96` with no fee or price-impact term. The actual output tokens are later sourced by `UniswapV4FundingPlanner.planWithdrawalForToken`, which decreases liquidity from the position and pays out at the pool's true execution price (including the fee tier and any price movement from the withdrawal itself). This mirrors the reported bug class: the "bounds"/output amount are computed from a reference price fixed before the swap, while the actual swap/withdrawal happens at a different price, producing an inconsistency between quoted and realized value.

### Finding Description
`resolveLegRates` in `sdk/packages/simplex/src/strategies/fx.ts:1443-1479` prices a curveless, venue-backed leg via:
```
venueUsd = await venueUsdPrice(leg.token1Chain, leg.token1Address)
rate = 1 / venueUsd
```
`venueUsdPrice` ultimately calls `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-275`), which returns `sdkPool.token0Price`/`token1Price` — the pool's instantaneous mid derived from `sqrtPriceX96`, with **no fee tier applied and no price-impact/size term**, as explicitly documented in `sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md:17-22`: *"the pool's fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price, and there is no size or impact term... A venue-priced pair that has to swap through its own pool to source inventory pays a fee tier it never quoted against."*

The only safeguard on this path, `checkPriceGuard` (`sdk/packages/simplex/src/strategies/fx.ts:428-448`), checks deviation of the quoted mid against a **static** `referencePrice`, not the cost of actually executing the withdrawal that funds the fill. This is structurally the same flaw as the reported issue: a price snapshot taken before value transfer is used to fix commitments (bounds / fill sizing), while the mechanism that actually moves the funds (swap / liquidity withdrawal) executes against a different price, and there is no mechanism forcing the two to reconcile.

When the solver's balance is insufficient, `UniswapV4FundingPlanner.planWithdrawalForToken` (lines 293-413) decreases liquidity from the position and computes the credited amount from the SDK `Position` object at the *current* on-chain `sqrtPriceX96` at withdrawal time — which can differ from the mid used to quote/size the fill to the counterparty order. The planner does add a slippage buffer (`slippageBps`) and caps output via `finalOutputAmount`, but this only protects the solver from committing more than it can deliver; it does not correct for the fact that the **fill price quoted to the user** was computed off a mid that ignored the fee tier and any market impact of the withdrawal.

### Impact Explanation
Because the quote given to the order placer is systematically better than what the pool will actually deliver (fee tier omitted, no impact term), every venue-priced fill either:
1. Under-delivers relative to what was promised (if the shortfall isn't otherwise absorbed), risking a reverted fill/wasted gas and paymaster cost, or
2. Silently transfers the omitted fee/impact cost onto the solver's own liquidity position, degrading its LP value on every fill without being reflected in the priced spread.

This is a systemic mispricing on a path an order placer (any unprivileged intent submitter) can trigger by simply constructing a curveless, USD-stable-token0 order against an exotic token that is priced from a Uniswap V4 position, directly reachable from a submitted intent/order.

### Likelihood Explanation
Medium-High: any curveless pair configured for pool-based pricing (`[vault.uniswapV4]` with no `bidPriceCurve`/`askPriceCurve`) is affected on every fill sourced from the LP position, with no attacker action required beyond placing an ordinary order. The `checkPriceGuard` only rejects gross deviation from a static external reference; it does not catch the fee/impact gap, which persists on every normal-sized fill.

### Recommendation
Ensure the price used to size and quote the fill is the same price the withdrawal will actually realize: incorporate the pool's fee tier and a size-dependent price-impact term into `computeDirectPoolPriceUsd`/`computeLegPolicyOutput`, or price the leg directly from the amounts `UniswapV4FundingPlanner` would credit for the exact liquidity decrease needed (as `planWithdrawalForToken` already computes), rather than from the pre-trade pool mid.

### Proof of Concept
Not independently reproducible without live pool state/exec traces; the mismatch is evidenced structurally by the code: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L256-272)
```typescript
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1453-1465)
```typescript
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
