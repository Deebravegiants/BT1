## #Vulnerability found for this question.

### Title
FXFiller overfill cap (`maxOverfillBps`) is disabled while the venue price guard checks only static deviation, letting an intent order drain solver funds via a stale/manipulated Uniswap V4 quote - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
The Aave V3 incident undervalued an asset by a small percentage inside a capped price oracle and, because the cap was misconfigured, the wrongful valuation flowed straight into liquidation logic that moved real funds. Hyperbridge's `FXFiller` (the unprivileged intent-solver reachable by any order placer) has the direct analog: the per-leg overfill ceiling that used to bound losses from "a bug / stale cache / manipulated venue price" has been explicitly disabled, and the venue price feed backing the payout calculation (`resolveLegRates`/`referenceRate`) is a raw Uniswap V4 pool mid with no size/impact term, guarded only by a static-deviation band (`checkPriceGuard`) that can itself be starved of a `reference` (guard optional) or bypassed within its tolerated band.

### Finding Description
`calculateProfitability` computes `rawPolicyMaxOutput` from a venue or curve rate and compares it against `overfillCeiling = output.amount * (10000 + maxOverfillBps) / 10000`. The code explicitly states the clamp is disabled — it fills the full computed amount and only emits a warning when the ceiling is exceeded: [1](#0-0) 

The rate feeding that computation for venue-priced pairs comes from `resolveLegRates`, which for a curveless USD-stable pair takes the live Uniswap V4 pool mid (`venueUsdPrice`) and validates it only against `checkPriceGuard`, a static `maxDeviationBps` band around an operator-set `reference`: [2](#0-1)  and [3](#0-2) 

The price guard is optional per chain, and even when configured it defends only against gross deviation from a hard-coded reference, not execution/price-impact cost — documented directly in the codebase's own flow notes: [4](#0-3) 

This mirrors the Aave CAPO bug precisely: a capped/bounded price mechanism (the overfill ceiling, analogous to CAPO's price cap) exists specifically to bound loss from a misvalued price, but it has been turned into a warn-only no-op, so any pricing error within the guard's tolerance band (or when no guard is configured for a chain) flows straight into `targetOutput`/`finalOutputAmount`, the amount the filler actually pays out of its own or funding-venue-sourced balance.

### Impact Explanation
Since `targetOutput = policyMaxOutput` is paid without a ceiling, an order that (a) hits a chain/pair with no configured `priceGuard` reference, or (b) is priced from a pool that has drifted just inside the guard's deviation band (e.g. via a large single-block swap or thin-liquidity manipulation), causes the filler to pay out materially more than the order's requested value. This is direct, uncapped fund loss for the solver/vault backing the FXFiller — the same "small undervaluation flows through into full-value financial action" pattern that cost Aave $862k, except here the exploitable party is the solver's own escrowed/vault liquidity rather than borrower collateral.

### Likelihood Explanation
Any order placer (an unprivileged intent submitter) can construct or wait for an order routed through a venue-priced pair; timing it against natural pool drift or a manipulable thin Uniswap V4 pool requires no privileged access — the guard is explicitly "optional," and its band still permits pricing that yields policyMaxOutput above the user's ask, which the disabled clamp no longer restrains. The comment block itself flags this as a known, intentional removal of protection ("this removes the per-leg loss bound that previously protected against a bug / stale cache / manipulated venue price"), indicating high likelihood of triggering under normal market conditions, not just adversarial ones.

### Recommendation
Re-enable the overfill ceiling as a hard cap (reject or clamp to `overfillCeiling`) rather than warn-only, and require `referencePrice`/`maxDeviationBps` guard configuration to be mandatory (not optional) for any curveless venue-priced pair, with the guard also weighted for price impact/size rather than a static mid-price deviation only.

### Proof of Concept
1. Configure (or leave default) a `TradingPair` with no curves and no `[vault.uniswapV4].positions[].referencePrice` set for a given chain — `checkPriceGuard` then returns `true` unconditionally for any quote on that chain per its own logic. [5](#0-4) 
2. Submit (or wait for) an intent order whose leg resolves via `resolveLegRates` to that unguarded venue pool.
3. Move the pool's mid price (a normal swap, or natural drift) so `rawPolicyMaxOutput` exceeds `overfillCeiling` by an arbitrary margin.
4. `calculateProfitability`/`executeOrder` logs a warning but still computes `targetOutput = policyMaxOutput` and funds it from wallet/funding-venue balances — see the unconditional payout path. [6](#0-5)

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L736-754)
```typescript
				const targetOutput = policyMaxOutput

				const walletContribution = targetOutput < usableWallet ? targetOutput : usableWallet

				let credited = 0n
				let needed = targetOutput - walletContribution
				for (const venue of this.fundingVenues) {
					if (needed <= 0n) break
					const planned = await venue.planWithdrawalForToken(destChain, walletAddress, tokenAddress, needed, deadlineTimestamp)
					if (planned.calls.length > 0) {
						fundingCalls.push(...planned.calls)
						credited += planned.credited
						needed -= planned.credited
					}
				}

				const effectiveBalance = walletContribution + credited

				const finalOutputAmount = effectiveBalance > targetOutput ? targetOutput : effectiveBalance
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
