### Title
FXFiller prices Uniswap V4 venue legs off manipulable spot tick with clamp disabled, enabling attacker-manipulated-pool overpayment - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
The reported Vader bug computes impermanent-loss reimbursement from the *current* (spot) pool balance rather than a TWAP, letting an attacker swap to distort the pool, extract an inflated payout, then reverse the swap risk-free. Hyperbridge's `simplex` intent solver (`FXFiller`) has the same root cause: for "venue-priced" pairs it derives the fill rate from the **live Uniswap V4 pool tick** (`computeDirectPoolPriceUsd`, `sdkPool.token0Price`/`token1Price`), and the only defense is a static `maxDeviationBps` band around a fixed `referencePrice` — not a TWAP and not an execution-size/impact term. Worse, the per-leg overfill clamp that historically bounded losses from exactly this scenario ("a bug / stale cache / manipulated venue price") has been deliberately disabled and now only logs a warning, so the filler pays out the unclamped, manipulated-price amount in full.

### Finding Description
`resolveLegRates` chooses venue pricing for curveless pairs whose `token0` is a USD stablecoin, reading the pool's raw mid price via `getVenueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which returns the pool's instantaneous `sqrtPriceX96`-derived price with no TWAP and "no size or impact term" [1](#0-0) .

The only guard is `checkPriceGuard`, which rejects a fill only if the live quote deviates from a static `referencePrice` by more than `maxDeviationBps` — a fixed band, not a time-weighted defense [2](#0-1) [3](#0-2) . The docs explicitly acknowledge "Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote" [4](#0-3) .

Once the (possibly manipulated) rate is chosen, `resolveLegRates` computes `policyMaxOutput` from it, and the code that used to cap output at `(1 + maxOverfillBps) × user-requested` for exactly this "manipulated venue" scenario has been turned into a warn-only no-op: `const policyMaxOutput = rawPolicyMaxOutput` — the unclamped, manipulated-price amount is paid out unconditionally [5](#0-4) . The design doc for this change confirms the clamp is a structural no-op today: "the clamp at the overfill-ceiling block is still a no-op assignment... `maxOverfillBps` and the halt subsystem remain dormant config" [6](#0-5) .

### Impact Explanation
An attacker who can move a configured Uniswap V4 pool's tick (a swap the solver funds no reserve pool for, and the guard only rejects deviations beyond `maxDeviationBps`, so a deviation just under that threshold passes) can place an intent order sized to be filled by `FXFiller` at the manipulated rate. Because the overfill clamp is disabled, the solver's `IntentGatewayV2.fillOrder` transfer (funded either from wallet balance or by withdrawing the configured Uniswap V4 LP position via `UniswapV4FundingPlanner`) pays out the full inflated amount computed from the distorted spot price, directly transferring solver/vault funds to the attacker. The attacker can then reverse the pool manipulation, recovering the manipulation cost and pocketing the difference, mirroring the original Vader exploit's risk-free profit pattern. This is a direct theft of solver-held/vault funds, bounded only by gas cost, the fixed `maxDeviationBps` band, and pool liquidity/fees needed to move the tick.

### Likelihood Explanation
Reachable by any unprivileged actor who can (a) swap in the referenced Uniswap V4 pool and (b) submit an IntentGateway order — no special privilege needed. The attack requires only a single transaction (or tightly sequenced transactions) to move the pool price within the configured deviation band, place the order, get it filled by the automated solver, and reverse the price. Given the docs and decision log explicitly flag the venue price as attacker-manipulable and the loss-bounding clamp as a deliberately disabled no-op, this is a known, currently-live gap rather than a theoretical one.

### Recommendation
- Price venue-sourced legs from a TWAP (or multi-block/multi-sample) Uniswap V4 quote rather than the instantaneous `sqrtPriceX96` mid, consistent with the referenced report's recommendation to use a TWAP for `P1`.
- Re-enable (or replace) the `maxOverfillBps` clamp so a manipulated/stale venue quote cannot produce an unbounded payout; at minimum restore hard capping rather than warn-only logging, per the decision log's own "should be either re-armed or deleted outright" note [6](#0-5) .
- Add a size/impact term to `computeDirectPoolPriceUsd` so large orders against thin liquidity are priced with slippage rather than the flat mid.

### Proof of Concept
1. Attacker identifies a chain/pair configured under `[vault.uniswapV4]` with `referencePrice`/`maxDeviationBps` set (e.g., 200 bps) [7](#0-6) .
2. Attacker swaps in that Uniswap V4 pool to move the tick close to, but within, the `maxDeviationBps` band, inflating the pool's implied exotic-token price.
3. Attacker immediately places an IntentGateway order (stable → exotic, or vice versa) sized so `FXFiller.resolveLegRates` picks the venue rate at the manipulated tick and passes `checkPriceGuard` [8](#0-7) .
4. `computeLegPolicyOutput` derives `policyMaxOutput` from the inflated rate; the overfill-ceiling check only warns and does not clamp, so the filler pays the full unclamped amount [5](#0-4) , funded if needed by withdrawing from the configured Uniswap V4 LP position via `UniswapV4FundingPlanner.planWithdrawalForToken` [9](#0-8) .
5. Attacker reverses the initial swap, restoring the pool price, and keeps the difference between the manipulated payout and fair market value.

### Citations

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L6-22)
```markdown
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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-84)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.

```toml lineNumbers
[vault.uniswapV4]
# referencePrice is the expected cNGN per USD;
# reject if the quote is more than 2% off.
# The two go together — one without the other is rejected.
[[vault.uniswapV4.positions]]
chain           = "EVM-8453"
tokenId         = "2087350"
referencePrice  = "1575"
maxDeviationBps = 200
```
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-08-20-the-curve-amount-is-the-fill-and-the-exposure-cap-does-not.md (L38-43)
```markdown
- _Re-enable `maxOverfillBps` as part of this change._ Deliberately left alone. The clamp at the
  overfill-ceiling block is still a no-op assignment (`const policyMaxOutput = rawPolicyMaxOutput`)
  and `recordOrderOutcome` is still always called with `false`, so `maxOverfillBps` and the halt
  subsystem remain dormant config. Restoring the payout makes that ceiling meaningful again and it
  should be either re-armed or deleted outright — a separate decision from fixing the payout, and
  one that changes the filler's loss bound rather than its price.
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L293-312)
```typescript
	async planWithdrawalForToken(
		destChain: string,
		solver: HexString,
		tokenOutLower: string,
		amountNeeded: bigint,
		deadlineTimestamp?: bigint,
	): Promise<FundingPlanResult> {
		const noopResult: FundingPlanResult = { calls: [], credited: 0n }

		this.logger.debug(
			{
				destChain,
				solver,
				tokenOutLower,
				amountNeeded: amountNeeded.toString(),
			},
			"UniswapV4 planWithdrawalForToken called",
		)

		if (amountNeeded <= 0n) return noopResult
```
