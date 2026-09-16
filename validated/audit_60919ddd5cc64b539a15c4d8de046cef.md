### Title
Simplex FXFiller Uniswap V4 venue pricing reads a manipulable spot price with no size/impact term, letting an attacker sandwich a solver's fill to extract value from an intent order - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
Simplex's `FXFiller`, an intent solver that fills `IntentGatewayV2` orders, can price curve-less cross-asset pairs directly off a live Uniswap V4 pool's `sqrtPriceX96` instead of an operator-configured curve [1](#0-0) . The only defense is a static `referencePrice`/`maxDeviationBps` band checked at quote time [2](#0-1) , which — like the AeraVaultV1 spot-price-agnostic deposit/withdraw functions in the referenced report — can be satisfied by an attacker who moves the pool price by less than the allowed deviation in the same block as the fill, extracts value, and reverses the move immediately after (a sandwich), all without tripping the guard.

### Finding Description
When a pair has no `bidPriceCurve`/`askPriceCurve`, Simplex derives the rate directly from the Uniswap V4 pool's current tick via `computeDirectPoolPriceUsd`, which "returns the raw pool mid derived from sqrtPriceX96 ... there is no size or impact term" [3](#0-2) . The docs themselves acknowledge: "Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote" [4](#0-3) .

The only mitigation is `checkPriceGuard`, which rejects a quote only if it deviates from a static `referencePrice` by more than `maxDeviationBps` [5](#0-4) . This is exactly the class of protection the external report calls "add price boundaries ... to ensure the pool's spot price remains within specified boundaries" — but as in the AeraVaultV1 case, a boundary check against instantaneous spot price does not prevent a same-block sandwich: an attacker can move the pool price by up to `maxDeviationBps` (a static, governance-configured percentage that has to be wide enough to tolerate normal volatility) in one direction just before the solver's fill transaction lands, causing the solver to size and fund the fill (via `UniswapV4FundingPlanner.planWithdrawalForToken`, which removes liquidity and computes credited amounts from the same skewed pool state [6](#0-5) ) at the manipulated rate, then reverse the trade immediately afterward to recapture the pool's true price and pocket the difference. Because the resolved price directly determines `targetOutput`/`policyMaxOutput` that gets paid out to the order's beneficiary via `IntentGatewayV2.fillOrder` [7](#0-6) , this is a genuine on-chain fund-transfer vector, not merely an off-chain quoting bug.

### Impact Explanation
A successful sandwich extracts real value from the solver's escrowed capital (Uniswap V4 LP position and/or wallet funds) that is transferred out through `IntentGatewayV2.fillOrder`/`_fillSameChain`/`_fillCrossChain`, i.e., concrete theft of funds reachable by an unprivileged user simply placing an intent order sized to trigger venue pricing, combined with the attacker's own manipulation transactions around it. This matches "High Risk" in the original report's classification since it is a repeatable extraction against any curve-less, pool-priced pair.

### Likelihood Explanation
Likelihood is Medium: it requires (1) a pair configured without curves, relying on pool pricing, (2) sufficient capital to move the specific Uniswap V4 pool's price by up to `maxDeviationBps` within one block/transaction bundle, and (3) an order large enough for the extracted spread to exceed gas + slippage costs. Thinly-liquid "exotic" pools (the intended use case for this feature, e.g., CNGN, ZARP) are the most susceptible, since they are precisely the pools cheapest to move.

### Recommendation
- Do not price fills off an instantaneous `sqrtPriceX96` read; use a manipulation-resistant reference such as a TWAP over multiple blocks, or a Chainlink/oracle cross-check in addition to the static `referencePrice` band.
- Incorporate a size/impact term into `computeDirectPoolPriceUsd`/`computeLegPolicyOutput` so a large notional against a pool cannot be filled at the pre-trade mid price.
- Tighten or make `maxDeviationBps` adaptive to pool depth rather than a single static value, and require `referencePrice`/`maxDeviationBps` to be mandatory (not optional) whenever `[vault.uniswapV4]` pool pricing is enabled.
- Consider requiring the fill transaction to check that the pool's `lastChangeBlock`/tick has not moved within the same block as the fill (as suggested for AeraVaultV1), or encourage private relay (Flashbots-style) submission of fills to reduce sandwichability.

### Proof of Concept
1. Configure a Simplex pair (e.g., USDC/CNGN) with no bid/ask curves and `[vault.uniswapV4]` pool pricing enabled, per `docs/content/developers/evm/simplex/pricing.mdx`.
2. Attacker observes a pending user order on `IntentGatewayV2` (or predicts one) that this filler will fill using pool-based pricing.
3. Attacker front-runs the solver's `fillOrder` transaction with a large swap on the exotic token's Uniswap V4 pool, shifting `sqrtPriceX96` such that `computeDirectPoolPriceUsd` returns a price skewed in the attacker's favor but still within `maxDeviationBps` of `referencePrice`.
4. The solver's fill transaction executes at the manipulated price, sizing `targetOutput` from the skewed rate and withdrawing liquidity/funding via `UniswapV4FundingPlanner`.
5. Attacker back-runs with the reverse swap, restoring the pool price and capturing the spread extracted from the solver's fill.

Note: this analysis is based on documentation and TypeScript solver code (`fx.ts`, `UniswapV4FundingPlanner.ts`) rather than a full byte-for-byte trace of `checkPriceGuard`'s exact implementation and `computeDirectPoolPriceUsd`'s source, which the index did not return in full; a Devin session with full repository access would be needed to confirm exact numeric bounds and any additional guards not surfaced by search.

### Citations

**File:** docs/content/developers/evm/simplex/pricing.mdx (L40-46)
```text
## Pool-Based Pricing

When **`[vault.uniswapV4]`** lists at least one position, cross-asset pairs without curves derive bid/ask prices from **Uniswap V4 pool state** (current tick). The pool acts as the price oracle instead of a static curve. Note this yields a **single** price used in both directions — a venue-priced pair has no bid/ask spread of its own, so its margin comes from `order.fees` alone.

With Uniswap V4 positions configured, you can **omit** `bidPriceCurve` and `askPriceCurve` on the pair. Pool pricing requires the pair's `token0` to be a USD stablecoin, and same-token pairs always need their curve. The optional **`spreadBps`** field (basis points) sets the slippage tolerance for on-chain LP redemptions; defaults to `50` (0.50%).

Uniswap V4 venue pricing uses pools that pair the exotic token with **USDC or USDT** (addresses from your chain config). When multiple positions exist for the same exotic token on a chain, the most-liquid qualifying pool's price is used.
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

**File:** sdk/packages/simplex/src/tests/strategies/fx.price-guard.test.ts (L72-84)
```typescript
	it("passes a quote inside the band", () => {
		const filler = makeFiller({ [CHAIN]: { referencePrice: REFERENCE, maxDeviationBps: 200 } })
		// 1% above and below — within the 2% band
		expect(check(filler, "1590")).toBe(true)
		expect(check(filler, "1560")).toBe(true)
		// exactly at the 2% edge (1575 * 1.02 = 1606.5)
		expect(check(filler, "1606.5")).toBe(true)
	})

	it("rejects a quote above the band", () => {
		const filler = makeFiller({ [CHAIN]: { referencePrice: REFERENCE, maxDeviationBps: 200 } })
		expect(check(filler, "1700")).toBe(false) // ~7.9% above
	})
```

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L325-330)
```typescript
			// Refresh on-chain state for this chain right before planning so
			// liquidity and price data are as fresh as possible.
			await state.refresh()

			const tokenNeed = tokenOutLower.toLowerCase()
			const candidates = state
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L83-93)
```text
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
```
