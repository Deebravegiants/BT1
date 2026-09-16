### Title
Simplex intent solver prices exotic tokens from a single Uniswap V4 pool's spot price, exposing solver liquidity to manipulation-driven mispricing - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Hyperbridge's Simplex intent solver, when configured with pool-based ("venue") pricing for a trading pair, derives the USD price of an exotic output token directly from a single Uniswap V4 pool's instantaneous `sqrtPriceX96`/tick state (via `sdkPool.token0Price`/`token1Price`), rather than from a manipulation-resistant, time-weighted, or multi-source oracle. This is structurally the same bug class as the Definer incident: using the point-in-time state of a single liquidity pool as the price source for a financial decision.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` iterates the solver's configured V4 positions and calls `computeDirectPoolPriceUsd`, which reads the pool's current spot price straight off the SDK `Pool` object: [1](#0-0) 

This spot price is used both to price/accept the leg of an intent order (feeding `resolveLegRates` / `venuePriceMemo` in the FX pricing strategy) and, later, to compute how much liquidity to withdraw from the position to fund the fill: [2](#0-1) 

The documentation explicitly acknowledges this is a single-pool, point-in-time price source with an *optional* deviation guard: [3](#0-2) 

and the internal AI-flow note confirms the guard is the *only* defense and only checks deviation from a static `referencePrice`, not execution cost or manipulation resistance, and can be left unconfigured entirely ("omit both to leave the chain unguarded"): [4](#0-3) 

This mirrors the Definer root cause: a DeFi actor (here, the Simplex solver) reads a single liquidity pool's current balance/price ratio as its price oracle instead of a robust, aggregated, or attack-resistant source (e.g. Chainlink), which the report notes Ethereum implementations using ChainLink do not suffer from.

### Impact Explanation
An unprivileged actor who can move the price of the configured Uniswap V4 pool (e.g., via a large swap or flash-loan-funded trade immediately before or during order submission, or by owning/targeting a thin pool) can distort `getExoticTokenPrice`'s output. Since this price feeds directly into whether/how the solver fills an intent order (`fx.ts` pricing strategy) and the size of the on-chain liquidity withdrawal used to fund that fill, an attacker can cause the solver to release more of its escrowed LP-backed exotic tokens than the order's `fees`/spread economically justify, extracting value from the solver's Uniswap V4 position while paying a price set by a manipulated pool. Because pool liquidity and per-pair `maxOrderSize` bound a single order's exposure, the practical loss is capped per fill but is still concrete value extraction from solver-held funds that back user intents — analogous in kind (single-pool spot price as sole oracle) to the Definer loss, even though the guard (`maxDeviationBps`) can mitigate it if configured, and is not mandatory.

### Likelihood Explanation
Likelihood is Medium: exploitation requires (1) a pair configured for venue (pool) pricing without a `referencePrice`/`maxDeviationBps` guard, or with a wide-enough deviation tolerance, and (2) sufficient capital or flash-loan access to move the specific Uniswap V4 pool's spot price meaningfully relative to its depth — thin/low-liquidity pools (which the docs implicitly assume filler-provided positions may be) are realistically manipulable. No privileged access is required; only submitting an intent order and interacting with the public Uniswap V4 pool are needed.

### Recommendation
Do not treat a single pool's live spot price as authoritative pricing input. Require the deviation guard (`referencePrice`/`maxDeviationBps`) to be mandatory rather than optional whenever venue pricing is enabled, source the reference from a TWAP or external oracle instead of a static config value, and/or use a TWAP/observation-based price (rather than raw `sqrtPriceX96`) from the pool itself to reduce single-block manipulation exposure. Additionally, bound the maximum fill size relative to available pool depth so a manipulated quote cannot be scaled up by ordering multiple/larger legs.

### Proof of Concept
Conceptual PoC (solver-side risk, not independently verifiable without a live Simplex deployment configured with unguarded venue pricing):
1. Solver operator configures `[vault.uniswapV4]` for pair `USDC/EXOTIC` with a position on a thin V4 pool, omitting `referencePrice`/`maxDeviationBps` (permitted per docs).
2. Attacker takes a large flash-loan-funded swap against that pool to shift `sqrtPriceX96`, moving `sdkPool.token1Price`/`token0Price` far from the true market rate.
3. Attacker (or colluding party) submits an intent order sized at/near `maxOrderSize` for that pair while the price is skewed.
4. Simplex's `fx.ts` strategy calls `getExoticTokenPrice` → `computeDirectPoolPriceUsd`, accepts the order using the skewed price, and `planWithdrawalForToken` withdraws liquidity from the solver's position priced at the same skewed rate, over-crediting the attacker's counterparty relative to fair value.
5. Attacker reverses the pool-moving swap, realizing the price manipulation profit at the solver's expense. [5](#0-4)

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L206-240)
```typescript
	async getExoticTokenPrice(chain: string, exoticToken: string): Promise<Decimal | null> {
		const state = this.stateByChain.get(chain)
		if (!state || !state.isHydrated()) return null

		try {
			await state.refresh()
		} catch (err) {
			this.logger.error({ err, chain }, "Failed to refresh state for price query")
			return null
		}

		const tokenLower = exoticToken.toLowerCase()
		let bestPrice: Decimal | null = null
		let bestLiquidity = 0n

		for (const pos of state.allPositions()) {
			if (pos.currency0.toLowerCase() !== tokenLower && pos.currency1.toLowerCase() !== tokenLower) continue
			const sdkPool = state.getSdkPool(pos.tokenId)
			if (!sdkPool) continue

			const result = this.computeDirectPoolPriceUsd(pos, sdkPool, chain)
			if (result && result.exoticToken.toLowerCase() === tokenLower) {
				const poolLiquidity = state.getPoolLiquidity(pos.tokenId)
				if (poolLiquidity > bestLiquidity) {
					bestPrice = result.priceUsd
					bestLiquidity = poolLiquidity
				}
			}
		}

		if (bestPrice) {
			this.logger.debug({ chain, token: tokenLower, priceUsd: bestPrice.toString() }, "Exotic token price computed")
		}
		return bestPrice
	}
```

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L293-330)
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

		const state = this.stateByChain.get(destChain)
		if (!state || !state.isHydrated()) {
			this.logger.debug(
				{ destChain, hasState: !!state, isHydrated: state?.isHydrated() },
				"UniswapV4 no state or not hydrated",
			)
			return noopResult
		}

		const mutex = this.mutexByChain.get(destChain)!
		return mutex.runExclusive(async () => {
			// Refresh on-chain state for this chain right before planning so
			// liquidity and price data are as fresh as possible.
			await state.refresh()

			const tokenNeed = tokenOutLower.toLowerCase()
			const candidates = state
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L40-72)
```text
## Pool-Based Pricing

When **`[vault.uniswapV4]`** lists at least one position, cross-asset pairs without curves derive bid/ask prices from **Uniswap V4 pool state** (current tick). The pool acts as the price oracle instead of a static curve. Note this yields a **single** price used in both directions — a venue-priced pair has no bid/ask spread of its own, so its margin comes from `order.fees` alone.

With Uniswap V4 positions configured, you can **omit** `bidPriceCurve` and `askPriceCurve` on the pair. Pool pricing requires the pair's `token0` to be a USD stablecoin, and same-token pairs always need their curve. The optional **`spreadBps`** field (basis points) sets the slippage tolerance for on-chain LP redemptions; defaults to `50` (0.50%).

Uniswap V4 venue pricing uses pools that pair the exotic token with **USDC or USDT** (addresses from your chain config). When multiple positions exist for the same exotic token on a chain, the most-liquid qualifying pool's price is used.

```toml lineNumbers
[assets.CNGN]
"EVM-8453" = "0x46C85152bFe9f96829aA94755D9f915F9B10EF5F"

[[pairs]]
token0 = "USDC"
token1 = "CNGN"
maxOrderSize = "5000"       # no curves — priced from the pool

[vault.uniswapV4]
spreadBps = 50  # 0.5% slippage tolerance on LP redemptions
positions = [
    { chain = "EVM-8453", tokenId = "2087350" },
]
```

<Callout type="info">
Startup validation requires a pricing source per pair: **either** bid/ask price curves, **or** at least one `[vault.uniswapV4]` position. A pair with neither fails validation.
</Callout>

## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
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
