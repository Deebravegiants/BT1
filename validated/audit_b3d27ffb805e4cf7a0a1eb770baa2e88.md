Based on my research, I found a plausible analog in the Hyperbridge Simplex intent-filler codebase, though I was unable to fully read `UniswapV4FundingPlanner.ts` and the full `checkPriceGuard` implementation in `fx.ts` before running out of tool iterations, so some details below are inferred from the documentation flow file rather than directly-verified line-level code.

### Title
Unchecked spot-price validation in Simplex's Uniswap V4 venue pricing allows flash-loan price manipulation to mis-price fills - (File: sdk/packages/simplex/src/strategies/fx.ts, sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts)

### Summary
Simplex's `FXFiller` prices "venue-priced" exotic-token pairs (pairs with no static bid/ask curve) directly from a Uniswap V4 pool's instantaneous `sqrtPriceX96`, with the only safeguard being a static-reference deviation check (`checkPriceGuard`), not an execution-cost/impact-aware check. This mirrors the Stake Nova root cause: an unchecked/insufficiently validated on-chain value (there, a redemption amount; here, a spot price) is trusted directly for a fund-moving decision, allowing a flash-loan-style pool manipulation within the tolerance band to distort pricing.

### Finding Description
The documented flow (verified 2026-08-19) is:
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
``` [1](#0-0) 

`computeDirectPoolPriceUsd` returns the raw pool mid derived from `sqrtPriceX96`; the pool's fee tier is read onto the position object but never applied to the price, and there is no size/impact term — `computeLegPolicyOutput` extends this mid linearly across the whole priced quantity. `checkPriceGuard` is the *only* defense on this path, and it checks deviation from a static reference value, not execution cost or manipulation resistance (e.g. TWAP). [2](#0-1) 

This same raw venue price is also used for **confirmation-depth sizing** via `referenceRate`, which explicitly warns that a manipulated pool understating value would shrink reorg protection — i.e., the code authors were aware the pool price is attacker-influenceable, but the mitigation is only a static-band guard, not a manipulation-resistant oracle: [3](#0-2) 

The guard's test suite confirms the behavior is only a static-reference bound check ("sizes with the pool rate when the quote is inside the band" / "refuses to size when the pool quote breaches the guard band"), and — critically — "sizes unguarded when no reference is configured (guard is optional)": [4](#0-3) 

Because the price is read as the pool's instantaneous spot price (not a TWAP) and the guard is a wide static band (and optional when unconfigured), an attacker can use a flash loan to swap against the thin/target Uniswap V4 pool, push `sqrtPriceX96` to the edge of (or beyond, if unconfigured) the allowed deviation, and cause Simplex to price/fill an order or size its LP withdrawal against the manipulated rate within the same transaction/block, exactly as the Stake Nova incident exploited an unchecked value in `RedeemNovaSol()` to drain the pool via a flash loan.

### Impact Explanation
If exploited, this allows an intent solver/order submitter to force Simplex to fill cross-chain FX orders, or size Uniswap V4 LP withdrawals via `UniswapV4FundingPlanner`, at a manipulated exchange rate — directly transferring value from the vault/solver's inventory to the attacker, analogous to the ~95% pool drain in the referenced incident. This is a concrete theft-of-funds path reachable from a single submitted order (an "intent solver" / order path explicitly in scope).

### Likelihood Explanation
Likelihood is constrained by: (1) the guard band being configurable and (2) it only applies when a static reference price is configured for that chain (per the test "sizes unguarded when no reference is configured (guard is optional)"). Any pair without a configured `priceGuard` reference, or any manipulation that stays within the configured `maxDeviationBps`, is fully exploitable with no additional check. The `spreadBps` LP slippage tolerance on withdrawal (in `pricing.mdx`) provides a secondary, narrow bound but is a fixed tolerance, not a manipulation-resistant price source. Exploitability depends on pool liquidity depth relative to attacker capital (flash loan size), consistent with the "not proof, but a bug-class hint" framing of the external report.

### Recommendation
Replace or supplement the raw spot-price read (`computeDirectPoolPriceUsd` from instantaneous `sqrtPriceX96`) with a manipulation-resistant price source (e.g., a Uniswap V4 TWAP oracle observation window, or an external price feed) before using it to size fills or LP withdrawals. Make the `checkPriceGuard` static-reference check mandatory (not optional per-chain) for all venue-priced pairs, and consider adding same-block/same-transaction manipulation detection (e.g., comparing spot price against a longer-window TWAP and rejecting large single-block divergence) rather than relying solely on a static deviation band.

### Proof of Concept
Not independently verified with a runnable exploit — this assessment is based on the documented pricing flow and guard test behavior described above, since I could not fully read `UniswapV4FundingPlanner.ts` in the available iterations. Conceptually: (1) attacker takes a flash loan; (2) swaps heavily against the target Uniswap V4 pool backing an exotic-token pair configured in Simplex to move `sqrtPriceX96`/mid price toward (or, if no `priceGuard` entry exists for that chain, arbitrarily far from) the true market price; (3) in the same block, submits/triggers an order that causes Simplex's `FXFiller` to price the leg via `venuePriceMemo → getExoticTokenPrice → computeDirectPoolPriceUsd`, filling at the manipulated rate or sizing an LP withdrawal against it; (4) repays the flash loan, keeping the mispriced difference. This would need to be validated on a fork against a concretely configured pair/pool to confirm exploitable depth and guard configuration.

### Citations

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L5-15)
```markdown
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1353-1364)
```typescript
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

**File:** sdk/packages/simplex/src/tests/strategies/fx.price-guard.test.ts (L126-144)
```typescript
	it("sizes with the pool rate when the quote is inside the band", async () => {
		const { filler, pair } = makeVenueFiller({ [CHAIN]: { referencePrice: REFERENCE, maxDeviationBps: 200 } })
		const rate = await referenceRate(filler, pair, "1580")
		expect(rate?.toFixed(0)).toBe("1580")
	})

	it("refuses to size when the pool quote breaches the guard band", async () => {
		const { filler, pair } = makeVenueFiller({ [CHAIN]: { referencePrice: REFERENCE, maxDeviationBps: 200 } })
		// ~11% below reference — a pool understating the exotic's value.
		expect(await referenceRate(filler, pair, "1400")).toBeNull()
		// ~8% above — overstating it (would inflate the notional instead).
		expect(await referenceRate(filler, pair, "1700")).toBeNull()
	})

	it("sizes unguarded when no reference is configured (guard is optional)", async () => {
		const { filler, pair } = makeVenueFiller()
		const rate = await referenceRate(filler, pair, "1400")
		expect(rate?.toFixed(0)).toBe("1400")
	})
```
