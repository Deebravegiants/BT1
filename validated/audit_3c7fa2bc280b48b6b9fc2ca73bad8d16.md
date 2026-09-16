### Title
Simplex FX filler sizes orders and enforces its reorg/manipulation guard from an un-averaged Uniswap V4 spot pool price - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
The D3X AI incident stemmed from `exchange()` trusting the instantaneous spot price of a UniswapV2 pair, letting an attacker manipulate the pool and profit from the mispriced trade. The `Simplex` intent-filler (used by intent solvers filling Hyperbridge `IntentGateway`/`IntentGatewayV3` orders) contains an analogous pattern: for venue-priced pairs it derives the USD notional and rate used to size and price a fill directly from a Uniswap V4 pool's current `sqrtPriceX96` (raw mid), guarded only by a static `referencePrice`/`maxDeviationBps` deviation check rather than any time-weighted or manipulation-resistant price source.

### Finding Description
`UniswapV4FundingPlanner.computeDirectPoolPriceUsd` reads the pool's live `token0Price`/`token1Price` (derived from spot `sqrtPriceX96`) as the USD price of the exotic token: [1](#0-0) 

This spot price feeds `getExoticTokenPrice`, which is consumed by the FX strategy's `referenceRate` to convert a venue-priced pair's notional and to gate the trade via `checkPriceGuard`: [2](#0-1) 

The documented flow confirms the pool acts as the sole price oracle for the pair, with no execution-size/impact term and only a static-deviation guard as defense: [3](#0-2) 

and the pricing documentation itself acknowledges the pool is trusted live and can return "a manipulated, stale, or thin pool" quote, bounding risk only via `maxDeviationBps` around a static `referencePrice`: [4](#0-3) 

Because the guard checks deviation from a fixed reference rather than execution cost or a TWAP, an attacker who manipulates the pool's spot price by an amount just inside `maxDeviationBps` (or who front-runs order submission with a swap) can cause the filler to size/value a fill using an off-market rate. This is structurally the same bug class as D3X: reliance on an AMM's instantaneous reserve ratio for a pricing decision that gates fund movement (in this case, LP withdrawal/funding of a fill), without a manipulation-resistant price feed (e.g., TWAP, Chainlink) or an execution-price check reflecting the actual swap cost.

### Impact Explanation
If the exotic-token spot price used by the venue pricing path is manipulated, the solver's Uniswap V4 LP position can be priced and withdrawn against a distorted USD notional, allowing an intent submitter (attacker) to construct/trigger an order that a Simplex-operated solver fills at a manipulated rate — causing the solver (and the funds backing the intent settlement) to lose value, analogous to D3X's `exchange()` loss. This affects the intent solver's vault/inventory rather than the core Hyperbridge protocol contracts (`EvmHost`, pallet-ismp, consensus clients), so the blast radius is scoped to Simplex-operated fillers using the `[vault.uniswapV4]` venue-pricing feature, not the protocol's message-passing or state-proof security. Given the docs' explicit acknowledgment of the risk, and that funds (LP-backed inventory) can be drained/mispriced, this is a Medium finding.

### Likelihood Explanation
Likelihood is constrained by preconditions: the vulnerable path only activates for pairs configured with `[vault.uniswapV4]` and no `bidPriceCurve`/`askPriceCurve` (pool-based pricing), and only when a position's pool is thin enough to be moved within `maxDeviationBps` cheaply, or when `referencePrice`/`maxDeviationBps` are left unset ("unguarded" per the docs). An attacker submitting an intent order (an unprivileged action reachable via the `IntentGateway`) combined with a pool-manipulating swap on the same venue is a realistic, low-cost attack pattern mirroring the D3X exploit, but requires a specific filler configuration to be in play.

### Recommendation
Replace or supplement the raw spot `sqrtPriceX96`-derived price with a manipulation-resistant source (TWAP over the position's pool, or a Chainlink/other independent oracle) before using it to size fills or value LP withdrawals. Make `referencePrice`/`maxDeviationBps` mandatory (not optional) for any `[vault.uniswapV4]` position, and incorporate the pool's actual swap-execution cost (fee tier + price impact for the sized trade) into `checkPriceGuard` rather than comparing only the static mid-price deviation.

### Proof of Concept
1. Configure a Simplex filler with a curveless pair priced from a `[vault.uniswapV4]` position on a thinly-liquid Uniswap V4 pool, with `referencePrice`/`maxDeviationBps` unset or set loosely.
2. Attacker swaps against the pool to move `sqrtPriceX96` such that `computeDirectPoolPriceUsd` returns a distorted USD price for the exotic token, still within any configured deviation bound.
3. Attacker submits (or already has pending) an `IntentGatewayV3` order on the pair; the filler's `sizeOrder`/`referenceRate` prices/sizes the fill using the manipulated venue price via `UniswapV4FundingPlanner.getExoticTokenPrice`.
4. The filler withdraws LP liquidity (`planWithdrawalForToken`) and completes the fill at the distorted rate, realizing a loss for the solver analogous to D3X's `exchange()` price-manipulation loss.

Note: I was unable to fully trace `checkPriceGuard`'s exact implementation (only its call sites in `fx.ts` were found; its body did not appear in the indexed excerpts), so the precise bound/behavior of the deviation check could not be fully verified from the available index. A Devin session with full repo access would be needed to confirm the exact guard logic and any additional mitigations (e.g., TWAP usage elsewhere) before treating this as fully validated.

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-275)
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
	}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1339-1364)
```typescript
	/**
	 * Minimum-size reference rate (token1 per token0) for a leg's pair: the
	 * bid curve at 0 (the side token1-input legs trade at), falling back to the
	 * ask curve, then the live venue quote for venue-priced pairs.
	 */
	private async referenceRate(
		leg: ResolvedLeg,
		venueUsdPrice: (chain: string, token1Address: string) => Promise<Decimal | null>,
	): Promise<Decimal | null> {
		const policy = leg.pair.bidPricePolicy ?? leg.pair.askPricePolicy
		if (policy) {
			const rate = policy.getPrice(new Decimal(0))
			return rate.gt(0) ? rate : null
		}
		// Venue-priced pair: token0 is USD-stable (constructor invariant), so the
		// venue's USD-per-token1 quote inverts straight into token1-per-token0.
		const venueUsd = await venueUsdPrice(leg.token1Chain, leg.token1Address)
		if (!venueUsd) return null
		const venueRate = new Decimal(1).div(venueUsd)
		// Same guard as trade pricing: this rate sizes the order's USD notional
		// for confirmation depth, and a manipulated pool understating the value
		// would shrink the reorg protection — the exact attack the guard exists
		// to stop. Refusing to size skips the order, consistent with pricing.
		if (!this.checkPriceGuard(undefined, leg.token1Chain, venueRate)) return null
		return venueRate
	}
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
