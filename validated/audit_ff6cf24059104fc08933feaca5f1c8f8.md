Based on the evidence gathered, I have sufficient detail to provide a definitive answer now.

### Title
Solver's Uniswap V4 venue price is manipulable via flash-loan-style pool skew and lacks execution-cost pricing, letting an intent placer drain solver value on curveless pairs - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
`FXFiller` prices "curveless" (venue) trading pairs directly off a live Uniswap V4 pool's spot tick (`getExoticTokenPrice` / `computeDirectPoolPriceUsd`), the same class of bug that let the Elephant Money attacker profit by pushing an AMM-derived spot price and then trading against it in the same window. The only protection is `checkPriceGuard`, a static-reference band check, while `resolveLegRates`/`computeLegPolicyOutput` apply the raw pool mid **linearly across the whole order size**, with no slippage or fee-tier adjustment for what it actually costs the solver to source the tokens from that same pool.

### Finding Description
For a curveless pair (no `bidPriceCurve`/`askPriceCurve`, `token0` a USD stable), `resolveLegRates` fetches the venue's mid price from the configured Uniswap V4 position and, after only a static-deviation `checkPriceGuard` check, uses it verbatim as the fill rate for the entire order size: [1](#0-0) 
`checkPriceGuard` only rejects a quote that has drifted more than `maxDeviationBps` from a static `referencePrice` — it says nothing about whether the current quote reflects an amount the solver can actually fill at, and it does nothing about size/impact: [2](#0-1) 
The docs describe this precisely and flag the two gaps: the pool's own fee tier is read but "never applied to the price," "there is no size or impact term," and the guard "checks deviation from a static reference, not execution cost": [3](#0-2) 
Because a solver sourcing inventory for a large fill has to swap through the *same* pool it just quoted from (`UniswapV4FundingPlanner.planWithdrawalForToken`), an attacker who first skews the pool's tick (e.g. with a large swap or flash-loan-funded swap, staying inside `maxDeviationBps` of the guard's static reference) can then place an intent order sized to consume the manipulated mid, receive a solver quote priced off the stale linear mid, and profit from the gap between that mid and what the solver actually realizes once it pays the pool's real fee tier and slippage to source the tokens — the exact "manipulate the on-chain price used to compute swap output, then trade against it" pattern in the Elephant Money incident.

### Impact Explanation
This directly costs the solver real funds: the solver delivers output tokens priced at a linear, unmanipulated-looking mid, then loses more than expected fee/slippage when actually withdrawing/sourcing liquidity through its own now-skewed pool. Since Simplex fillers are reference solver infrastructure shipped with Hyperbridge's Intent Gateway and are expected to hold real inventory to back fills, a reliably exploitable pricing gap is a concrete solver fund loss reachable by any unprivileged order placer — matching the Medium severity of the analog report (an attacker profiting off a manipulated AMM-derived price during a mint/settlement flow).

### Likelihood Explanation
The attack requires only placing a normal intent order (`IntentGatewayV2.placeOrder` on the destination chain the venue prices from) sized against a thin/low-liquidity Uniswap V4 position, optionally preceded by a swap (flash-loan funded or not) that moves the pool's tick while staying inside the configured `maxDeviationBps` band. No governance, relayer, or privileged role is needed — this is reachable from a single submitted order by any user, and operators are explicitly warned in the docs that price guards do not cover this case, indicating the gap is real and currently unmitigated rather than theoretical.

### Recommendation
- Apply the pool's actual fee tier and a size/impact-aware quote (e.g., simulate the withdrawal swap against current liquidity rather than extending the static mid linearly) in `resolveLegRates`/`computeLegPolicyOutput`.
- Extend `checkPriceGuard` (or add a companion check) to bound the *executable* price (post-fee, post-impact) rather than only the instantaneous mid against a static reference.
- Consider TWAP or multi-block observation of the Uniswap V4 pool instead of the single current tick, and/or cap per-order notional relative to the position's available on-chain liquidity to limit the profitability of single-transaction skew-then-fill attacks.

### Proof of Concept
1. Operator configures a curveless pair (e.g., USDC/CNGN) funded by a `[vault.uniswapV4]` position with a `referencePrice`/`maxDeviationBps` guard, per `sdk/packages/simplex/src/strategies/fx.ts` and `docs/content/developers/evm/simplex/pricing.mdx`.
2. Attacker swaps a moderate amount through the same Uniswap V4 pool (flash-loan funded for capital efficiency) to move the tick just inside the `maxDeviationBps` band, skewing the quoted mid in the attacker's favor.
3. Attacker (or a colluding party) immediately places an `IntentGatewayV2.placeOrder` sized to the pool's now-skewed mid; `checkPriceGuard` passes because the deviation is within band, and `resolveLegRates` prices the whole leg at that mid with no impact term, per `sdk/packages/simplex/src/tests/pairs.test.ts` lines 1067-1090 showing venue legs fill "at the pool mid — gated by fees and the price guard only."
4. Solver fills using inventory sourced by `UniswapV4FundingPlanner.planWithdrawalForToken` against the same skewed pool, realizing worse execution (real fee tier + slippage) than the quoted mid, and the attacker's overall trade (skew swap + intent fill, potentially reversed afterward) nets a profit funded by the solver's loss.

### Citations

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1449-1465)
```typescript
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
