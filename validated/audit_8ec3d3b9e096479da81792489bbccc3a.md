### Title
Simplex FXFiller's Uniswap V4 venue pricing uses unprotected spot price, exposing intent solvers to sandwich attacks on order fills - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
For curveless ("venue-priced") trading pairs, the Simplex `FXFiller` prices intent-order fills directly off a Uniswap V4 pool's current spot price (`sqrtPriceX96`/tick via `slot0`), with no TWAP or execution-cost check — only an optional, wide static-band `checkPriceGuard`. An attacker can manipulate the pool's spot price with a swap immediately before submitting/timing an intent order fill, forcing the filler to price the fill off the manipulated spot rate, then reverse the swap to profit — the same "manipulate spot price → sandwich the liquidity-sourced quote → reverse trade" pattern described in the referenced Multipool.sol report.

### Finding Description
`resolveLegRates` and `referenceRate` in `sdk/packages/simplex/src/strategies/fx.ts` price curveless pairs from a live venue quote obtained via `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which returns "the raw pool mid derived from `sqrtPriceX96`" read via `getSlot0` at the time of evaluation. [1](#0-0) [2](#0-1) 

The only defense against a manipulated quote is `checkPriceGuard`, which compares the live venue quote to a static, manually configured `referencePrice` within `maxDeviationBps`. This guard is optional — "The two fields must be set together; omit both to leave the chain unguarded" — and even when configured, it accepts any price within the deviation band (e.g. up to ~2% at the documented default of 200 bps), which is enough room for an attacker to profit from a swap-and-reverse around the fill. [3](#0-2) [4](#0-3) 

The project's own internal analysis confirms this is a live gap: "`checkPriceGuard` is the only defense on this path, and it checks deviation from a static reference, not execution cost." There is no size/impact term or TWAP comparison at all — `computeLegPolicyOutput` extends the pool mid linearly across the whole quantity. [5](#0-4) 

This is priced at `resolveLegRates`, which is called from `calculateProfitability` on the real order-fill path (not just a probe), meaning the manipulated rate directly determines `policyMaxOutput` — the actual amount of tokens the solver commits to deliver via `fillOrder` on the `IntentGatewayV2`/`IntrinsicIntents` contracts. [6](#0-5) 

An attacker who is also the order placer (or colludes with one) can:
1. Front-run: swap in the exotic-token pool to push spot price away from fair value, remaining within the configured guard band (or beyond it if unguarded).
2. Have their own intent order priced by the manipulated venue rate, causing the solver to compute an inflated `policyMaxOutput` and deliver more value than fair, or (in the case of `referenceRate`'s use for confirmation sizing) mis-size confirmation depth.
3. Back-run: reverse the pool swap to restore price and realize profit, extracting value from the solver's escrowed/committed liquidity.

### Impact Explanation
The solver (an unprivileged, permissionless actor reachable via order placement — matching "intent solver" in scope) suffers real economic loss: it delivers output tokens priced from a manipulated spot rate rather than a fair market rate, and the manipulation cost to the attacker is a single swap plus reversal, profitable whenever the guard band (or absence of a guard) permits sufficient deviation. This is a direct funds-loss analog to the original Multipool `rebalanceAll` sandwich: single-block spot-price manipulation feeding directly into an economic commitment (liquidity add there; order fill pricing here) with no TWAP protection.

### Likelihood Explanation
Likelihood is High for deployments using pool-based (curveless) pricing without a configured guard (explicitly supported and documented as valid config), and Medium for guarded deployments, since the guard's band (commonly 100–200 bps per the shipped example config) is a static tolerance, not a TWAP or execution-cost check, and can be sized to permit profitable sandwiches especially on thinner pools. The attack requires only a standard swap transaction and order placement — no privileged access, exactly the "single submitted transaction/dispatched request" reachability required.

### Recommendation
Replace or supplement the raw `slot0` spot price in `computeDirectPoolPriceUsd` with a TWAP (time-weighted average price) read from the pool's oracle observations, and compare the spot quote against the TWAP (not only a static operator-configured reference) before accepting it in `checkPriceGuard`. Additionally, consider making the price guard mandatory for venue-priced pairs (removing the "omit both to leave unguarded" option) and factoring the position's fee tier / trade size into the quoted rate to reduce mispricing from thin liquidity.

### Proof of Concept
Conceptual PoC (cannot be executed against the indexed snippets alone, but follows directly from the code paths cited):
1. Configure/observe a Simplex filler running a curveless `[[pairs]]` (e.g. USDC/CNGN) funded via `[vault.uniswapV4]` with no `referencePrice`/`maxDeviationBps` guard, or a wide one.
2. Attacker swaps a large amount into the CNGN/USDC V4 pool, moving `sqrtPriceX96` so `computeDirectPoolPriceUsd` returns a price favorable to the attacker (e.g., CNGN understated in USD terms).
3. Attacker immediately places an Intent Gateway order (`IntentGatewayV2.placeOrder`) requesting CNGN for USDC sized to this manipulated rate; `resolveLegRates`/`referenceRate` price the fill from the manipulated `getVenueUsdPrice` result within the same or next block, since `checkPriceGuard` passes (guard absent or within band).
4. Filler's `calculateProfitability`/`executeOrder` commits to `fillOrder` at the manipulated rate, delivering more CNGN than fair value.
5. Attacker reverses the initial swap, restoring the pool price and net profiting the value overpaid by the solver, mirroring the front-run/add-liquidity/back-run pattern in the referenced report.

### Citations

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L601-634)
```typescript
			for (let i = 0; i < order.inputs.length; i++) {
				const input = order.inputs[i]
				const output = order.output.assets[i]
				const leg = legs[i]

				const inputDecimals = await this.contractService.getTokenDecimals(
					bytes32ToBytes20(input.token) as HexString,
					sourceChain,
				)
				const outputDecimals = await this.contractService.getTokenDecimals(
					bytes32ToBytes20(output.token) as HexString,
					destChain,
				)

				const token0Decimals = leg.inputIsToken0 ? inputDecimals : outputDecimals
				const token1Decimals = leg.inputIsToken0 ? outputDecimals : inputDecimals

				// `sizeOrder` populates an entry for every pair these legs resolve to, so
				// the fallback is defensive only — the leg's own notional, never a cap
				// that may not exist.
				const cappedNotional = cappedByPair.get(leg.pair) ?? legNotionals[i]
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1443-1465)
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
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L150-163)
```typescript
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
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
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
