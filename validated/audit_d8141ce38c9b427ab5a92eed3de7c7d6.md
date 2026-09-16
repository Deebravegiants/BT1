## Analysis

The JOJO report's bug class is: **a swap/price-dependent settlement path that computes an output amount from an external price source without enforcing a maximum-loss/slippage bound**, so the caller can lose funds if that price source is stale or manipulated.

The strongest analog in this codebase is in the Simplex filler (an intent-gateway solver bot), where the per-leg fill amount is derived from a venue price (Uniswap V4 pool mid) and the safety clamp that used to bound losses from a bad price has been explicitly disabled.

### Title
Intent-solver fill amount is derived from an unguarded venue price with the overfill loss-bound disabled - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
`FXFiller`'s fill-sizing path pays out `policyMaxOutput` — an amount computed by linearly extending a Uniswap V4 pool's raw mid price (`computeDirectPoolPriceUsd`) across the whole leg notional, with no fee-tier or price-impact term — and the `maxOverfillBps` ceiling that was designed to bound the loss from a stale/manipulated venue price has been turned into a no-op that only logs a warning.

### Finding Description
`resolveLegRates` computes a venue-derived rate for curveless pairs by reading a Uniswap V4 pool's mid price and validating it only against `checkPriceGuard`, which compares to a **static** reference price within `maxDeviationBps` — it does not account for the actual swap execution cost or pool fee tier [1](#0-0) .

`computeLegPolicyOutput` then extends this unguarded mid price linearly across the entire leg notional to produce `policyMaxOutput`, the amount the filler will pay [2](#0-1) .

The `evaluateOrder` fill path computes an `overfillCeiling` (`output.amount * (1 + maxOverfillBps)`) that should reject/clamp fills whose venue-priced payout balloons beyond what the user actually requested, but the code explicitly disables the clamp and only emits a warning log, paying the full unclamped `rawPolicyMaxOutput` regardless: [3](#0-2) 

The final payout is set unconditionally to this unclamped figure: [4](#0-3) 

This is corroborated by the project's own design record, which states the clamp is "a no-op assignment" and that disabling it "changes the filler's loss bound": [5](#0-4) 

### Impact Explanation
Because an order beneficiary can be the same actor who transiently manipulates the referenced Uniswap V4 pool (e.g., via a flash-loan/sandwich), and because `checkPriceGuard` only bounds deviation from a static reference (not execution/impact cost) while the `maxOverfillBps` circuit breaker is disabled, a manipulated or stale venue price can cause the solver to pay out substantially more of the output token than the order is worth, out of its own escrowed inventory, on a single `fillOrder` submission through `IntentGatewayV2`/`IntrinsicIntents`. This is a direct loss of solver funds analogous to the unmitigated slippage loss in the original report.

### Likelihood Explanation
The path is reachable by any order placer/filler interaction on `IntentGatewayV2` (an unprivileged intent-flow entrypoint) whenever a venue-priced (curveless) pair is configured; the only defense (`checkPriceGuard`) is a static-deviation band and is documented as not covering execution cost, and the loss-bound clamp is explicitly disabled rather than merely mis-configured, making this reachable under normal operator configuration rather than only via a misconfiguration.

### Recommendation
Re-enable and enforce `maxOverfillBps` as a hard ceiling on `policyMaxOutput` (reject or clamp, not just log), and extend `checkPriceGuard`/the venue pricing path to account for pool fee tier and price impact rather than only a static-reference deviation band, mirroring how `FlashLoanRepay`/`GeneralRepay`-style flows would require an enforced `amountOutMinimum`/ceiling before committing funds.

### Proof of Concept
1. Configure a curveless, venue-priced pair backed by a Uniswap V4 position (`UniswapV4FundingPlanner`).
2. Attacker briefly manipulates the pool's mid price within the `maxDeviationBps` static-reference band but such that the true execution price (after fee/impact) is materially worse — `checkPriceGuard` passes.
3. Attacker places/fills an order sized so `computeLegPolicyOutput` on the manipulated mid price yields `policyMaxOutput` far above `output.amount * (1 + maxOverfillBps)`.
4. `evaluateOrder` logs the "Overfill ceiling exceeded — clamp disabled" warning but still sets `targetOutput = policyMaxOutput`, so the filler sends the inflated amount to the beneficiary in `fillOrder`, realizing a loss equal to the manipulated overpayment. [6](#0-5)

### Citations

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L736-736)
```typescript
				const targetOutput = policyMaxOutput
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1417-1433)
```typescript
		const token0ForLeg = remainingToken0 === null ? legMaxToken0 : Decimal.min(legMaxToken0, remainingToken0)
		if (token0ForLeg.lte(0)) {
			return null
		}

		let policyMaxOutput: bigint
		if (inputIsToken0) {
			// Output is token1: convert the token0 allocation at the pair rate.
			policyMaxOutput = BigInt(
				token0ForLeg.mul(rate).mul(new Decimal(10).pow(token1Decimals)).floor().toFixed(0),
			)
		} else {
			// Output is token0: pay out the token0 equivalent of the token1 input.
			policyMaxOutput = BigInt(token0ForLeg.mul(new Decimal(10).pow(token0Decimals)).floor().toFixed(0))
		}

		return { token0Used: token0ForLeg, policyMaxOutput }
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
