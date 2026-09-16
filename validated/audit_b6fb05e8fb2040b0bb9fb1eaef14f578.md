## Analysis

The Aventa incident is a flash-loan price-manipulation attack. The closest reachable analog in this repo is in the **Simplex intent-solver** pricing path, which is explicitly in scope as "intent solver" logic that prices and executes fills against on-chain proof/state (Uniswap V4 pool state) reachable by any order submitter.

### Title
Flash-loan-manipulable Uniswap V4 spot price with disabled overfill clamp causes solver fund loss on venue-priced fills - (File: sdk/packages/simplex/src/strategies/fx.ts)

### Summary
`FXFiller` prices "venue-priced" pairs directly off a Uniswap V4 pool's instantaneous `sqrtPriceX96` with no TWAP and no size/impact adjustment, guarded only by an optional, static `checkPriceGuard`. The per-leg overfill safety clamp that used to bound loss from a manipulated venue price has been explicitly disabled (warn-only), so an attacker who moves the pool price with a flash loan (or any transient swap) within an unconfigured or wide `maxDeviationBps` window can force the solver to compute and pay out an inflated `policyMaxOutput` on a real fill.

### Finding Description
`resolveLegRates` derives venue prices via `UniswapV4FundingPlanner.getExoticTokenPrice → computeDirectPoolPriceUsd`, which "returns the raw pool mid derived from `sqrtPriceX96`... there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the whole priced quantity," and `checkPriceGuard` is "the only defense on this path, and it checks deviation from a static reference, not execution cost." [1](#0-0) 

The price guard is optional per-position configuration; if `referencePrice`/`maxDeviationBps` are omitted, "the chain is unguarded." [2](#0-1) 

Even where a guard exists, the safety net that historically capped loss from "a bug / stale cache / manipulated venue price" — the overfill clamp — has been explicitly disabled: `fx.ts` computes `overfillCeiling` but only logs a warning when `rawPolicyMaxOutput` exceeds it, then uses the unclamped `rawPolicyMaxOutput` as `policyMaxOutput` regardless. [3](#0-2) 

`targetOutput = policyMaxOutput` is then funded from wallet balance and, when insufficient, from Uniswap V4 LP withdrawals, and paid out via `IntentGateway.fillOrder`, which on-chain accepts any `solverAmount` the solver signs (even above `totalRequired`, splitting only the surplus). [4](#0-3) 

An attacker can therefore: (1) submit/observe an order routed to a venue-priced pair whose chain has no configured `referencePrice`/`maxDeviationBps` guard (or one wide enough to tolerate the swing), (2) transiently swap in the referenced Uniswap V4 pool (flash-loan-funded) to push `sqrtPriceX96` in the direction that inflates the exotic token's USD price, (3) let the solver's phantom-bid/fill pipeline price and execute the fill at the manipulated rate with the overfill clamp disabled, and (4) reverse the swap, having caused the solver to pay out more than the fair value of the order — a direct capital loss to the solver's inventory, mirroring the flash-loan-driven mispricing loss in the Aventa report.

### Impact Explanation
This causes concrete theft/loss of solver funds: the solver overpays real tokens (via wallet balance or LP withdrawal from its declared Uniswap V4 positions) at an attacker-manipulated price, with no on-chain or off-chain clamp left to bound the overpayment once the guard is absent or too permissive. This is a Medium-to-High severity fund-loss vector reachable by any unprivileged order submitter/attacker capable of a flash loan against the referenced pool.

### Likelihood Explanation
Likelihood is meaningful but conditional: it requires (a) an operator running a venue-priced (curveless) pair funded by Uniswap V4 LP without setting `referencePrice`/`maxDeviationBps`, or setting a loose `maxDeviationBps`, and (b) sufficient flash-loan liquidity to move that specific pool's price within the guard band during one block. Given the guard is optional by design and the overfill clamp was deliberately disabled repo-wide (not per-config), the residual protection depends entirely on operator-side price-guard configuration, which the code itself flags as a regression ("this removes the per-leg loss bound that previously protected against ... a manipulated venue price").

### Recommendation
- Re-enable the overfill clamp (or make it non-optional) so `policyMaxOutput` is hard-capped at `overfillCeiling` for venue-priced legs regardless of `maxOverfillBps` warnings.
- Require `referencePrice`/`maxDeviationBps` to be mandatory (not optional) for any `[vault.uniswapV4]` position used for pricing, or fall back to a TWAP/observation-based price instead of the raw instantaneous `sqrtPriceX96` mid.
- Add an execution-cost/size-impact term to `computeDirectPoolPriceUsd` so large fills are not priced at the undiluted mid.

### Proof of Concept
1. Configure (or find deployed) a curveless pair funded via `[vault.uniswapV4]` without `referencePrice`/`maxDeviationBps` set for the target chain, per `pricing.mdx` lines 70–84.
2. Attacker flash-loans the paired asset and swaps against the referenced Uniswap V4 pool to shift `sqrtPriceX96` so `computeDirectPoolPriceUsd` reports an inflated USD price for the exotic token.
3. Submit/route an intent order on that pair; `FXFiller.calculateProfitability`/`resolveLegRates` prices the leg off the manipulated pool state (`venue-pricing-uniswap-v4-funded-pairs.md`), and `fx.ts:678-701` logs but does not clamp the resulting inflated `rawPolicyMaxOutput`.
4. The filler funds and executes the fill via `IntentGateway.fillOrder` (`IntrinsicIntents.sol:79-106`), paying the inflated amount to the beneficiary; attacker reverses the flash-loan swap, netting the solver's overpayment as profit.

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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L70-84)
```text
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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L79-106)
```text
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
            }

            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
            uint256 beneficiaryTotal = fillAmount + beneficiaryShare;

            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
```
