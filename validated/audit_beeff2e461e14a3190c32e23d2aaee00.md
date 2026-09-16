I have enough context now to provide the analysis. This is a well-documented, deliberate design decision in the codebase, not a hidden bug, but it does match the "no ceiling enforcement" bug class from the report.

### Title
Disabled overfill ceiling in FXFiller lets a manipulated venue price or stale cache drain solver funds without bound - (File: sdk/packages/simplex/src/strategies/fx.ts)

### Summary
The Union `AssetManager` bug is a missing check that a deposit does not push a market's total balance past its configured `ceiling`. The direct analog in this repo is in `FXFiller.fill()` (`sdk/packages/simplex/src/strategies/fx.ts`): the filler computes an `overfillCeiling` (`output.amount * (1 + maxOverfillBps) / 10000`) meant to bound how much the solver pays out per leg relative to what the order actually requested, but the clamp is explicitly disabled — the code computes the ceiling, compares against it, and only logs a warning, then unconditionally sets `targetOutput = policyMaxOutput` (the raw, unbounded curve output) regardless of whether it exceeds the ceiling.

### Finding Description
In `_fillLeg`-equivalent logic inside `FXFiller.fill()`: [1](#0-0) 
the comment states plainly: *"Overfill detection is warn-only: the clamp is DISABLED, so the filler fills the full computed amount even when it exceeds (1 + maxOverfillBps) × user-requested... This removes the per-leg loss bound that previously protected against a bug / stale cache / manipulated venue price. Output is no longer capped; we only emit a warning."*

`policyMaxOutput` is then assigned unconditionally as `targetOutput`, which becomes the amount transferred out to fill the order: [2](#0-1) 

For venue-priced pairs (e.g., Uniswap V4), the price feeding `computeLegPolicyOutput` comes from a pool mid-price with no size/impact adjustment and only a static deviation guard (`checkPriceGuard`), not an execution-cost check: [3](#0-2) 

This mirrors the Union bug class exactly: a designed safety ceiling (`ceilingMap`/`maxOverfillBps`) exists in the code and its variable is computed, but the actual state-mutating action (deposit / fill payout) is not gated by it — the check is decorative rather than enforced.

### Impact Explanation
If a pool price used by a venue-priced pair is manipulated (flash-loan swap, thin liquidity, or a stale/cached quote drifts from the true market rate) within the tolerance still allowed by `checkPriceGuard`'s static deviation band, `computeLegPolicyOutput` will compute an inflated `policyMaxOutput`. Because the overfill clamp is a no-op, the filler will pay out that inflated amount from its own wallet/vault funds via `IntentGateway.fillOrder`, with no bound relative to what the order actually requested. This is a direct loss-of-funds vector for the solver operating this strategy — the exact "over the ceiling" failure mode from the reference report, just relocated from a shared money-market ceiling to a per-fill loss-bound ceiling.

### Likelihood Explanation
This is deliberately shipped code (confirmed by an explicit engineering decision doc acknowledging the dormant safety mechanism), not a corner-case bug, so the exposure exists in every fill on every venue-priced or sloped-curve pair for as long as the clamp remains disabled. Any user (or a colluding pair of accounts) who can influence the reference venue's spot price within the existing deviation-guard tolerance, or who can race a stale price cache, can place an order that the solver fills at the inflated, unbounded rate.

### Recommendation
Re-enable the `maxOverfillBps` clamp so that `targetOutput = min(policyMaxOutput, overfillCeiling)`, or explicitly delete the dormant `maxOverfillBps`/`overfillCeiling` machinery if it is intentionally being retired — leaving a computed-but-unenforced ceiling in production is the exact anti-pattern this report targets. If overfilling is to remain a deliberate business feature, it should be bounded by an operator-configured cap enforced in code, not merely logged.

### Proof of Concept
1. Configure a `FXFiller` trading pair as venue-priced against a Uniswap V4 pool with thin liquidity, `maxOverfillBps` set to a normal small value (e.g. 50 bps).
2. An attacker (or the order placer) performs a large swap against that V4 pool immediately before submitting an order through the `IntentGateway`, moving the pool mid-price by an amount that still passes `checkPriceGuard`'s static deviation tolerance but is well above the true market rate.
3. `resolveLegRates` → `computeDirectPoolPriceUsd` returns the manipulated mid-price; `computeLegPolicyOutput` computes `policyMaxOutput` based on it, far exceeding `overfillCeiling = output.amount * (1 + maxOverfillBps)/10000`.
4. At [4](#0-3)  the code detects `rawPolicyMaxOutput > overfillCeiling`, logs a warning, but does not clamp.
5. `targetOutput = policyMaxOutput` (unclamped) is paid out to the order beneficiary through `fillOrder`, draining more of the solver's inventory than the configured overfill tolerance permits, with the attacker able to repeat this against any pool they can move within the deviation-guard band.

### Citations

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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```
