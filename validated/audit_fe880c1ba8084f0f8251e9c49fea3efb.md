Based on my research, I found a genuine analog to the reported vulnerability class within scope.

### Title
Overfill clamp is a documented no-op, letting a manipulated Uniswap V4 venue price drain filler funds on a single order fill - (File: `sdk/packages/simplex/src/strategies/fx.ts`)

### Summary
The original finding describes a health/threshold check (`_checkLoanIsHealthy`) that lacks a safety margin against price movement, letting an attacker manipulate a market price within a single flow and profit at another party's expense. The closest reachable analog in this repository is Simplex's `FXFiller.calculateProfitability`, whose overfill "safety buffer" (`maxOverfillBps`) — intended to bound loss when a venue price (e.g. a Uniswap V4 pool) is stale, buggy, or manipulated — is explicitly disabled in code while still being documented and configured as an active protection.

### Finding Description
`FXFiller` prices cross-asset legs either from static bid/ask curves or from a live Uniswap V4 pool acting as an oracle (`fxPricing` docs, `sdk/packages/simplex/src/strategies/fx.ts:139-168`). A per-position `priceGuard`/`checkPriceGuard` only rejects a quote that deviates from a *static* `referencePrice` by more than `maxDeviationBps` [1](#0-0) ; it does not bound execution/impact cost from actually swapping through the venue's own pool, as the accompanying flow note states directly [2](#0-1) .

The second line of defense, `maxOverfillBps`, was designed to clamp the computed output to at most `(1 + maxOverfillBps)` × the user's requested amount specifically to bound "per-leg loss when internal pricing is wrong (bug, stale cache, manipulated venue)" [3](#0-2) . However, in `calculateProfitability`, the clamp is a documented no-op: the code computes `overfillCeiling` and compares against it only to emit a **warning**, then unconditionally uses the unclamped `rawPolicyMaxOutput` as `targetOutput`: [4](#0-3) [5](#0-4) 

This was a deliberate, tracked decision [6](#0-5) , which explicitly flags the ceiling as "a no-op assignment" and states it "should be either re-armed or deleted outright." A later, unrelated fix even calls out the same disabled state as a live risk multiplier: a misread token decimal "inflates the computed payout by 10^12" and "since the overfill clamp is disabled, nothing bounds the result back to the user's requested output" [7](#0-6) . Meanwhile, the CLI, docs, and README continue to present `overfillProtection` as an active safety knob a user can tune [8](#0-7) [9](#0-8) .

### Impact Explanation
An unprivileged intent placer can place an order against a pair the operator prices via a thin/manipulable Uniswap V4 position. By moving the pool price (e.g. with a swap immediately before placing the order, or exploiting a stale/cached price feed) so that `resolveLegRates`/`computeLegPolicyOutput` returns an inflated `rawPolicyMaxOutput`, the attacker causes `FXFiller` to fill the order paying out far more than the requested amount — well beyond any intended overfill ceiling, since that ceiling no longer clamps anything. Because `IntrinsicIntents.sol`/`IntentGatewayV2` releases the surplus above the requested amount to the beneficiary (`surplusShareBps`) [10](#0-9) , the attacker (as order beneficiary) directly captures the inflated payout. This is a concrete theft of solver treasury funds triggered by a single dispatched/filled order, directly analogous to the reported loan-health "no safety buffer" bug enabling profit via market manipulation.

### Likelihood Explanation
The precondition (a thin or attacker-influenced Uniswap V4 pool feeding `fx.ts` pricing, or a stale/misread cache) is realistic and already documented as a known risk class by the project itself (see the two cited decision/changelog notes). The clamp exists in configuration and is advertised to operators as protective, so an operator relying on default or configured `maxOverfillBps` values has no actual bound in place — the vulnerability is live in the current codebase, not merely theoretical, and requires only a single order plus a venue-price manipulation to trigger.

### Recommendation
Re-enable the `maxOverfillBps` clamp as an actual ceiling on `targetOutput` (not merely a warning threshold), or explicitly remove the dead configuration and warn-only telemetry to avoid operators believing they are protected. At minimum, extend `checkPriceGuard` to bound realized execution price/impact from swapping through the venue pool itself, not just deviation from a static reference, closing the gap the project's own `venue-pricing-uniswap-v4-funded-pairs.md` note identifies.

### Proof of Concept
1. Operator configures a `[[vault.uniswapV4.positions]]` pair with a thin pool and no (or a stale) `referencePrice`/`maxDeviationBps`, or one loose enough to admit meaningful pool-price movement.
2. Attacker swaps a modest amount through that same Uniswap V4 pool to shift `sqrtPriceX96` favorably, inflating the mid-price `computeDirectPoolPriceUsd` returns.
3. Attacker (or colluding party) immediately places an IntentGateway order requesting a modest `output.amount` for that pair, with themselves as beneficiary.
4. `FXFiller.calculateProfitability` resolves `rates.rate` from the manipulated pool, computes `rawPolicyMaxOutput` far above `overfillCeiling`; the code logs a warning ("Overfill ceiling exceeded — clamp disabled, filling unclamped amount") [11](#0-10)  but still sets `targetOutput = policyMaxOutput` [5](#0-4) .
5. The filler executes `fillOrder` paying the inflated amount; the surplus above `output.amount` is released to the beneficiary per `IntentGatewayV2`'s surplus-split logic, realizing the attacker's profit in a single order fill.

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

**File:** sdk/packages/simplex/filler-config-example.toml (L74-82)
```text
# Overfill protection (optional)
# Bounds per-leg loss when internal pricing is wrong (bug, stale cache, manipulated venue).
# The filler clamps its computed output to at most (1 + maxOverfillBps) × user-requested amount.
# After `maxConsecutiveClamps` consecutive orders where the clamp activated, the strategy
# halts itself — likely a systemic pricing error — and requires operator restart.
# If not provided, defaults will be used (maxOverfillBps = 500, maxConsecutiveClamps = 3)
# [simplex.overfillProtection]
# maxOverfillBps = 500          # 5% ceiling above user-requested output (default: 500)
# maxConsecutiveClamps = 3      # Halt threshold (default: 3)
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

**File:** sdk/packages/simplex/docs/ai/changelog/2026-08-26-decimals-read-failures-fall-back-to-the-asset-registry-instead.md (L1-8)
```markdown
# 2026-08-26 — `decimals()` read failures fall back to the asset registry instead of guessing 18

`ContractInteractionService.getTokenDecimals` previously swallowed a failed on-chain `decimals()`
read and returned a hardcoded 18. That value flows into `computeLegPolicyOutput`, which scales
`policyMaxOutput` by `10 ** decimals` — so a 6-decimal token (USDC/USDT/cNGN) misread as 18
inflates the computed payout by 10^12. Since the overfill clamp is disabled, nothing bounds the
result back to the user's requested output, and the filler would size the leg against its whole
wallet balance.
```

**File:** sdk/packages/simplex/src/cli/init/help-text.ts (L29-30)
```typescript
	overfill:
		"Safety clamp against pricing bugs: output is capped at maxOverfillBps above what the user asked for, and the strategy halts after maxConsecutiveClamps consecutive clamped orders.",
```

**File:** sdk/packages/simplex/src/services/FillerConfigService.ts (L115-120)
```typescript
export interface OverfillProtectionConfig {
	/** Ceiling bps above user-requested output; filler clamps its computed output to this. Default 500 (5%). */
	maxOverfillBps?: number
	/** Consecutive clamped evaluations before the strategy halts itself. Default 3. */
	maxConsecutiveClamps?: number
}
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L43-47)
```text
The solver calls `fillOrder(order, options)` on the **destination chain**. The function verifies the order hasn't expired (`order.deadline >= block.number`), confirms execution is on the correct chain, and checks the order hasn't already been filled. The solver must provide output amounts greater than or equal to the order's required amounts — any amount below the required amount reverts with `InvalidInput()`.

If the solver provides more tokens than required, the excess (surplus) is split according to `surplusShareBps`. If the order includes calldata, 100% of surplus goes to the protocol to prevent manipulation.

After delivering output tokens to the beneficiary, the contract dispatches a cross-chain `RedeemEscrow` message back to the source chain.
```
