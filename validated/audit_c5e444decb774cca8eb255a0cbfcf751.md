### Title
Spot-price Uniswap V4 oracle in the intent-solver's `FXFiller` is flash-loan manipulable, allowing an attacker to drain solver LP funds via mispriced order fills - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
The Simplex intent-solver's `FXFiller` strategy prices "venue" (curve-less) trading pairs directly from the current tick/`sqrtPriceX96` of a Uniswap V4 pool the solver itself supplies liquidity to, with no TWAP and no execution-size adjustment. This is architecturally the same failure mode as the Nereus exploit ("flash loan → skew reserve → fake pricing → drain"): an attacker can use a flash loan to skew the pool's instantaneous reserves/tick within a single transaction, causing the solver to compute a manipulated exotic-token price, fill an intent order at that bad rate, and extract solver funds.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` computes the exotic token's USD price straight from the pool's live state via `computeDirectPoolPriceUsd`, which is documented as returning "the raw pool mid derived from `sqrtPriceX96`", with the pool's own fee tier "read... but never applied to the price, and there is no size or impact term": [1](#0-0) 

This price feeds `FXFiller.resolveLegRates` (and `referenceRate`) as the pricing rate for any curve-less pair whose `token0` is a USD stable: [2](#0-1) 

The only defense on this path is `checkPriceGuard`, which merely bounds deviation from a static, operator-configured `referencePrice`/`maxDeviationBps` — and is explicitly optional (a chain with no guard configured is left completely unguarded): [3](#0-2) [4](#0-3) 

The project's own internal flow documentation confirms the root cause and the lack of an execution-cost check: [5](#0-4) 

Because the price is read on-demand at fill time (`state.refresh()` immediately before pricing/withdrawal planning) rather than time-averaged, an attacker can:
1. Flash-loan swap heavily against the solver's own Uniswap V4 pool to move `sqrtPriceX96` to a favorable-for-attacker tick, within the guard band if one is configured (or arbitrarily if unguarded).
2. In the same transaction/block, submit (or have already-pending) an intent order that the `FXFiller` prices off that pool.
3. The solver computes `venueRate` from the manipulated mid-price and fills the order, paying out more of the exotic token than the true market rate warrants — or in the reverse pair direction, accepting less input than it should — realizing an immediate loss for the solver equal to the manipulated spread.
4. The attacker reverses the flash-loan swap in the same transaction to restore the pool and repay the loan, keeping the fill's profit — exactly the "flash loan → skew reserve → fake pricing" pattern from the Nereus report.

This exactly mirrors SECURITY.md's own acknowledgment that flash-loan/oracle-manipulation impacts are explicitly **not** excluded from scope: "Note: This does not exclude oracle manipulation/flash-loan attacks." [6](#0-5) 

### Impact Explanation
A successful manipulation directly drains the solver's Uniswap V4 LP position funds through mispriced order fills — a concrete theft of funds reachable by any unprivileged party who can submit/trigger an intent order and flash-loan swap the referenced pool. Severity is Medium: it does not compromise Hyperbridge's core consensus/dispatch layer, but it is a fund-loss vulnerability in the intent-solver component that Hyperbridge ships and documents as a first-class strategy (`FXFiller`/Simplex), directly reachable from a single submitted order plus a public flash loan.

### Likelihood Explanation
Likelihood is realistic for any solver operator who runs `[vault.uniswapV4]` pool-based pricing without a price guard (the docs present this as optional), or even with one configured within a plausible `maxDeviationBps` band (e.g. 200 bps default guidance), since `checkPriceGuard` only bounds deviation from a static reference and not execution/impact cost of the manipulation itself. Flash-loan-based spot-price manipulation of a single pool is a well-established, cheap, atomic attack pattern (as demonstrated by Nereus and numerous other AMM-oracle incidents).

### Recommendation
- Replace the spot `sqrtPriceX96`-derived mid with a time-weighted average price (TWAP) read over multiple blocks/observations for the exotic-token pricing path, so a single-block/single-transaction flash-loan skew cannot move the priced rate.
- Make the price guard (`referencePrice`/`maxDeviationBps`) mandatory whenever `[vault.uniswapV4]` pool-based pricing is enabled, rather than optional, and tighten it or replace it with a size/impact-aware check (compare the fill's realized execution price, not just the resting mid, to the reference).
- Consider requiring the priced pool to have deep, incentive-aligned liquidity or an external price feed cross-check before using it to size the solver's own capital-at-risk fills.

### Proof of Concept
1. Operator configures a `[vault.uniswapV4]` position for pair `USDC/EXOTIC` with either no guard, or `referencePrice`/`maxDeviationBps` (see `sdk/packages/simplex/filler-config-example.toml` lines 281-292 and `pricing.mdx` lines 68-84).
2. Attacker flash-loans a large amount of `USDC` or `EXOTIC` and swaps against the same Uniswap V4 pool referenced by the solver's position (or an interlinked pool feeding the same tick), moving `sqrtPriceX96` to a favorable extreme (within the guard band if configured).
3. In the same block, attacker (or an accomplice) places an intent order routed through `IntentGatewayV3`/the Simplex filler for that pair. `FXFiller.canFill` → `resolveLegRates` → `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice` reads the freshly-skewed pool state (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`) and returns the manipulated price.
4. `checkPriceGuard` (`sdk/packages/simplex/src/strategies/fx.ts:428-448`) either passes (unguarded chain) or passes because the manipulated price is still inside `maxDeviationBps`.
5. The filler fills the order at the manipulated rate, withdrawing/crediting exotic tokens from its V4 position (`UniswapV4FundingPlanner.planWithdrawalForToken`, lines 324-441) at a loss relative to the true market rate.
6. Attacker reverses the initial swap and repays the flash loan in the same transaction, banking the price-manipulation profit extracted from the solver's fill — mirroring Nereus's "flash loan → skew reserve → fake pricing → repay flash loan" sequence.

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1443-1466)
```typescript
	private async resolveLegRates(
		orderId: string | undefined,
		leg: ResolvedLeg,
		cappedPairNotional: Decimal,
		venueUsdPrice: (chain: string, token1Address: string) => Promise<Decimal | null>,
	): Promise<LegRates | null> {
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
		}
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
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

**File:** SECURITY.md (L18-26)
```markdown
### Smart Contracts / Blockchain DLT

- Incorrect data supplied by third-party oracles.
- Impacts requiring basic economic and governance attacks (e.g. 51% attack).
- Lack of liquidity impacts.
- Impacts from Sybil attacks.
- Impacts involving centralization risks.

Note: This does not exclude oracle manipulation/flash-loan attacks.
```
