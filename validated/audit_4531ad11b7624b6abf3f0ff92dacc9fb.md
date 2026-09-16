## Analysis

The external report describes a vault `trade()` function that trusted a caller-supplied `receiveAmtMin` (which could be set to zero) to protect against price manipulation, allowing an attacker to skew an AMM pool and drain funds in one atomic transaction. Once the team added an oracle-derived minimum, the review still flagged that a *live, unguarded* on-chain price read (with no staleness/impact protection) is itself exploitable.

The closest reachable analog in this codebase is in the Simplex intent-solver's Uniswap V4 venue-pricing path, which prices and pays out order fills directly from a manipulable spot price with the loss-bounding clamp explicitly disabled.

### Title
Unbounded fill payout from a manipulable Uniswap V4 spot price with the overfill safety clamp disabled - (File: sdk/packages/simplex/src/strategies/fx.ts)

### Summary
`FXFiller` prices "venue" (curveless) pairs directly from the live Uniswap V4 pool mid-price (`computeDirectPoolPriceUsd`) rather than a curve, and pays out `policyMaxOutput` — a figure derived from that live price — as the actual fill amount to the order's beneficiary. The only defense on this pricing path, `checkPriceGuard`, compares the pool quote to a static `referencePrice` within `maxDeviationBps`; it is optional, and even when configured it bounds *distance from a static number*, not execution/price impact within the same block. Compounding this, the per-leg overfill clamp that used to cap payout at `(1 + maxOverfillBps) × userRequested` has been deliberately disabled — the code now only warns and pays the full unclamped, price-derived amount.

### Finding Description
For curveless pairs where `token0` is a USD stablecoin, `resolveLegRates` (`sdk/packages/simplex/src/strategies/fx.ts:1443-1465`) fetches the exotic token's USD price straight from the largest-liquidity Uniswap V4 pool via `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which returns the **raw pool mid derived from `sqrtPriceX96`** with no TWAP, no fee-tier adjustment, and no size/impact term, as documented in `sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md:17-22`. [1](#0-0) 

The only guard is `checkPriceGuard`, which rejects only if the quote deviates more than `maxDeviationBps` from a static, operator-configured `referencePrice` — it is optional ("omit both to leave the chain unguarded") and does not model execution cost or same-block manipulation: [2](#0-1) 

That priced rate feeds `computeLegPolicyOutput`, whose `policyMaxOutput` is paid out **unclamped**: the code that used to cap payout at `(1 + maxOverfillBps)` of the user's requested amount was intentionally disabled, leaving only a warning log: [3](#0-2) 

and the same figure is committed as the actual amount transferred to the order's beneficiary via `IntrinsicIntents`/`ExtrinsicIntents` `fillOrder`, which pays out `solverAmount` (here, `policyMaxOutput`) directly from the solver's wallet/funding venues to the order's beneficiary — an address the *order placer* (an unprivileged actor) fully controls.

An unprivileged order placer can therefore: (1) flashloan/swap against the specific Uniswap V4 pool used for venue pricing to move its spot price outside its "fair" range but within the configured `maxDeviationBps` band (or when no `referencePrice`/guard is configured at all, per `sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md:70-72`'s explicit "leave the chain unguarded" option); (2) place an intent order on the manipulated pair; (3) have the filler compute an inflated `policyMaxOutput` from the skewed mid-price and pay it out — unclamped — to the attacker's beneficiary; (4) reverse the pool manipulation, all in one transaction/bundle, exactly mirroring the vault sandwich pattern in the external report (skew price → trade at bad rate → unwind).

### Impact Explanation
This directly drains the solver's/filler's on-chain funds (wallet balance and any Uniswap V4 LP inventory withdrawn via `UniswapV4FundingPlanner`) to an attacker-controlled beneficiary in a single atomic transaction, with no per-fill loss bound once the overfill clamp is disabled and only a coarse, optional static-deviation guard in place. This is concrete theft of funds reachable by any unprivileged intent-order placer, matching the bug class and mechanism (unprotected slippage/spot-price trust enabling a same-block sandwich) described in the external report.

### Likelihood Explanation
Likelihood is high wherever a venue-priced (curveless) pair is configured against a Uniswap V4 pool with thin liquidity relative to what an attacker can move in one transaction, or wherever `referencePrice`/`maxDeviationBps` is left unconfigured ("unguarded" per the docs). The overfill clamp being *unconditionally* disabled (not gated behind any config) means this affects every venue-priced fill, not just a misconfigured edge case.

### Recommendation
- Re-enable and enforce the overfill/loss-bound clamp (`maxOverfillBps`) as a hard cap on payout, not a warn-only telemetry check.
- Require `referencePrice`/`maxDeviationBps` (or an equivalent TWAP/impact-aware check) to be mandatory, not optional, for any venue-priced pair.
- Derive the venue price from a manipulation-resistant source (e.g., a TWAP over multiple blocks, or a check against external oracle price) rather than the single-block `sqrtPriceX96` mid.

### Proof of Concept
1. Configure (or find already configured) a venue-priced pair (`token0` = USDC/USDT, `token1` = exotic) sourced from a Uniswap V4 pool with moderate liquidity, per `docs/content/developers/evm/simplex/pricing.mdx`.
2. Attacker executes a large swap against that same pool (flashloan-funded) to move `sqrtPriceX96` so `computeDirectPoolPriceUsd` reports an inflated exotic-token price, while staying within the configured `maxDeviationBps` (or exploiting a pair with no guard configured).
3. In the same transaction/bundle, attacker places an intent order on `IntentGatewayV2` requesting the exotic token, with beneficiary set to itself.
4. The filler's `resolveLegRates`/`computeLegPolicyOutput` prices the fill from the manipulated pool mid, `checkPriceGuard` passes (within band or unguarded), and the disabled overfill clamp lets `policyMaxOutput` — the inflated amount — be paid out in full via `fillOrder`.
5. Attacker reverses the initial swap, unwinding the price manipulation, having extracted the difference between the manipulated and fair-value payout from the solver's funds.

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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
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
