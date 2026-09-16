## Title
Simplex FXFiller venue pricing trusts an unguarded single-block Uniswap V4 spot price, letting an order submitter manipulate the fill rate - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Vee Finance's exploit hinged on a leveraged-trading protocol that priced assets solely from live Pangolin AMM reserves (a single-source, spot price oracle) with no depth/impact adjustment, letting the attacker create thin pairs and swap against them to move the price and pass slippage checks. The same bug class exists in Simplex's FXFiller `UniswapV4` venue pricing path: curveless pairs are priced directly from a single Uniswap V4 pool's current `sqrtPriceX96` mid, with no size/impact term and only a static-reference deviation guard, no TWAP or liquidity-depth check.

### Finding Description
When a `TradingPair` has no `bidPricePolicy`/`askPricePolicy` configured, FXFiller falls back to venue pricing: `getVenueUsdPrice` calls `UniswapV4FundingPlanner.getExoticTokenPrice`, which "picks the position with the largest pool liquidity" and derives price via `computeDirectPoolPriceUsd -> sdkPool.token0Price / token1Price`, i.e., a raw spot mid read directly from the pool's current tick [1](#0-0) .

This spot mid is used as `rate = 1 / venueUsd` to price the leg's `computeLegPolicyOutput`, which "extends the mid linearly across the whole priced quantity" — there is no size or price-impact term applied [2](#0-1) . The only defense is `checkPriceGuard`, which merely rejects the fill if the quote deviates from a *static* `referencePrice` by more than `maxDeviationBps` [3](#0-2) . This is documented explicitly as insufficient: "`checkPriceGuard` is the only defense on this path, and it checks deviation from a static reference, not execution cost" [2](#0-1) .

An order submitter (an unprivileged intent placer reaching the IntentGateway/Simplex solver path) can, within the same transaction bundle or shortly before submitting an order, execute a swap against the Uniswap V4 pool the solver uses for pricing (the one "with the largest pool liquidity" for that exotic token, which on a thin/mid-cap listing can still be manipulated within `maxDeviationBps`) to push the spot mid to the edge of the allowed deviation band, then submit an order sized to extract value at that skewed rate. Because the fill amount is computed by linearly extending the manipulated spot mid across the "whole priced quantity" with no size-aware slippage/impact modeling, the solver is induced to release more output tokens (from its own liquidity/vault) than the true market rate justifies — the same single-source-price mechanics abused in the Vee Finance exploit (there via Pangolin pool reserves, here via Uniswap V4 tick state).

### Impact Explanation
A profitable manipulation directly drains solver capital (the Simplex filler's on-chain liquidity/vault funds) on any pair configured for venue (pool) pricing, since the exotic token's price is sourced from a single spot AMM read rather than a manipulation-resistant TWAP, and the guard bounds deviation but not execution cost/size-impact. This is a concrete theft-of-funds vector reachable by any unprivileged intent submitter interacting with the solver, consistent in class with the Vee Finance loss driven by manipulable single-source AMM pricing.

### Likelihood Explanation
Likelihood depends on (a) a pair being configured with venue-only pricing (no curves) and Uniswap V4 positions, and (b) the referenced pool having liquidity thin enough, or `maxDeviationBps` set loose enough, to allow a profitable price shift within the guard band, and (c) the solver having enough liquidity in that pool/vault to make the manipulation worthwhile net of gas and its own capital cost. Given `maxDeviationBps` is operator-configured and can be set generously, and pool liquidity is not otherwise vetted by the pricing code, this is plausible but operator-configuration-dependent — Medium-High likelihood assuming realistic operator configs on thinner-liquidity "exotic" pairs (the stated use case, e.g. cNGN/ZARP-style pairs, per the pricing docs).

### Recommendation
Replace the raw single-block `sqrtPriceX96` spot read with a TWAP or multi-observation price over a manipulation-resistant window; add a size/impact-aware quote (e.g., simulate the actual withdrawal/swap against the position rather than linearly extending the mid); and tighten/validate `maxDeviationBps` against pool depth so the guard band cannot be gamed by a pre-trade against thin liquidity.

### Proof of Concept
Not independently executable from the index alone — an end-to-end PoC would require reproducing a live Uniswap V4 pool with configurable liquidity and confirming `computeDirectPoolPriceUsd`'s raw mid moves as expected under a swap, then confirming `computeLegPolicyOutput`'s linear extension pays out more than a depth-aware fill would. This should be validated with a Devin session against `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts` and `sdk/packages/simplex/src/strategies/fx.ts` in a forked-mainnet Foundry/vitest environment, since the exact `getExoticTokenPrice`/`computeDirectPoolPriceUsd` implementation body was not fully retrievable through the index (file content beyond the referenced doc/flow summaries).

### Citations

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
