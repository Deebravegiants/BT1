I now have sufficient evidence to write the analog finding.

### Title
Simplex FXFiller prices exotic-token orders directly from a spot Uniswap V4 pool tick with an optional, easily-bypassed deviation guard, enabling single-trade oracle manipulation to drain solver funds - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
When a `FXFiller` pair is configured without static bid/ask curves (curveless, venue-priced), `resolveLegRates` derives the fill rate directly from a Uniswap V4 pool's current spot price (`sqrtPriceX96` via `computeDirectPoolPriceUsd`/`getExoticTokenPrice`), analogous to how the Blend Pools V2 (YieldBlox) incident used a single-trade-manipulated Reflector price feed from a low-liquidity Stellar DEX market to overvalue collateral (USTRY). The only defense is `checkPriceGuard`, a static-reference deviation check that is explicitly optional per the filler's own configuration/docs, and even when configured, only bounds deviation from a stale reference rather than any manipulation-resistant TWAP or liquidity-depth check.

### Finding Description
`FXFiller.resolveLegRates` (`sdk/packages/simplex/src/strategies/fx.ts:1436-1481`) prices a curveless, venue-priced leg by calling `venueUsdPrice`, which resolves through `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which reads the pool's **raw spot mid** from `sqrtPriceX96` with no TWAP, no size/impact term, and the fee tier is stored but never applied [1](#0-0) .

The only mitigation, `checkPriceGuard`, compares this spot price against a **static** `referencePrice` within `maxDeviationBps` [2](#0-1) . Both fields are optional and must be configured together — omitting them "leaves the chain unguarded" [3](#0-2) , and even when omitted the guard silently passes every quote, confirmed by the filler's own test: `"passes every quote when no guard is configured"` [4](#0-3)  and `"sizes unguarded when no reference is configured (guard is optional)"` [5](#0-4) .

This mirrors the Blend Pools V2 root cause precisely: a protocol-critical valuation (collateral value there, fill rate/notional here) is derived from a single, unbounded, low-liquidity on-chain price source that an attacker can move with one trade, and the only sanity check is either absent or bounds only static drift rather than detecting an atomic single-block manipulation.

### Impact Explanation
An attacker who identifies (or creates) a thinly-liquid Uniswap V4 pool backing a configured exotic-token pair can:
1. Manipulate the pool's spot tick with a single large swap (analogous to the ~100x USTRY manipulation on SDEX).
2. Submit (or wait for) an intent order priced against that manipulated tick via `resolveLegRates`/`computeLegPolicyOutput`, which extends the manipulated mid linearly across the whole priced quantity with no depth check.
3. Extract solver-funded output tokens (or force the solver to overpay) at the manipulated rate, directly analogous to how the Blend attacker borrowed ~$10.2M against artificially overvalued USTRY collateral.

Where no price guard is configured (the documented default/unguarded state), there is zero manipulation resistance. Even where a guard is configured, it only rejects deviation from a stale reference, not the underlying manipulability of an atomic single-trade price movement within the allowed band, so an attacker can still profit up to `maxDeviationBps` per order, repeatably.

### Likelihood Explanation
Reachable by any unprivileged user submitting a same-chain or cross-chain intent order through `IntentGatewayV2`/`IntentsBase` against a curveless, venue-priced pair — no privileged role is required. The precondition (a curveless pair funded by Uniswap V4 LP positions, per `docs/content/developers/evm/simplex/pricing.mdx`) is an explicitly documented, supported, non-experimental configuration, and price guards are explicitly optional. Manipulating a concentrated-liquidity pool's spot tick with a single trade is a well-understood, low-cost attack pattern, directly matching the external report's method.

### Recommendation
- Require a manipulation-resistant price source (TWAP over a sufficient window, or a cross-referenced independent oracle) instead of the raw spot `sqrtPriceX96` for any pair used to fund/price fills.
- Make the price guard mandatory (not optional) for all venue-priced pairs, and reject startup configuration that omits it.
- Incorporate pool liquidity depth/impact into `computeLegPolicyOutput` rather than extending the spot mid linearly across the whole order size.
- Consider bounding orders against multiple independent liquidity venues, or requiring same-block/same-transaction manipulation detection (e.g., comparing spot price against a block-old checkpoint).

### Proof of Concept
1. Configure a Simplex filler with a curveless pair (e.g., `USDC/EXOTIC`) funded solely by a Uniswap V4 position, with no `referencePrice`/`maxDeviationBps` set (the documented "unguarded" state) — per `docs/content/developers/evm/simplex/pricing.mdx:72` and confirmed unguarded behavior in `fx.price-guard.test.ts:65-70`.
2. Attacker swaps a large amount through the same thin Uniswap V4 pool in one transaction, moving `sqrtPriceX96` far from fair value.
3. Attacker (or an accomplice) submits an `IntentGatewayV2.placeOrder` intent that a bidding solver prices via `FXFiller.resolveLegRates`, which reads the now-manipulated spot price with no TWAP/impact adjustment.
4. Solver fills at the manipulated rate — `computeLegPolicyOutput` extends the bad mid linearly across the full order size — transferring an inflated amount of the exotic/output token to the attacker's beneficiary address, or draining the solver's Uniswap V4-backed liquidity at a bad rate.
5. Attacker reverses the pool manipulation (or lets arbitrageurs restore it), retaining the profit extracted from the mispriced fill.

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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
```

**File:** sdk/packages/simplex/src/tests/strategies/fx.price-guard.test.ts (L65-70)
```typescript
describe("FXFiller Uniswap price guard", () => {
	it("passes every quote when no guard is configured", () => {
		const filler = makeFiller()
		expect(check(filler, "1575")).toBe(true)
		expect(check(filler, "5000")).toBe(true)
	})
```

**File:** sdk/packages/simplex/src/tests/strategies/fx.price-guard.test.ts (L140-144)
```typescript
	it("sizes unguarded when no reference is configured (guard is optional)", async () => {
		const { filler, pair } = makeVenueFiller()
		const rate = await referenceRate(filler, pair, "1400")
		expect(rate?.toFixed(0)).toBe("1400")
	})
```
