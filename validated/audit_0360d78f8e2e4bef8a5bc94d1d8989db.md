### Title
Simplex FX solver prices exotic-token fills off an unguarded, single-block Uniswap V4 spot price, letting a flash-loan pool manipulation drain solver funds - (File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts)

### Summary
Hyperbridge's Simplex intent solver (`sdk/packages/simplex`) prices "venue-priced" cross-asset pairs (e.g. USDC↔cNGN) directly from a Uniswap V4 pool's current `sqrtPriceX96`, with no TWAP and no execution-size impact term. This is architecturally identical to the KUB-Split bug class: a spot AMM price used as an on-chain oracle, manipulable within a single transaction/block by a flash loan or large swap, which lets an attacker force a mispriced fill against the solver.

### Finding Description
When a `[[pairs]]` entry omits bid/ask curves and instead relies on `[vault.uniswapV4]`, Simplex derives the exotic token's USD price straight from the pool's instantaneous tick/`sqrtPriceX96`: [1](#0-0) 

`computeDirectPoolPriceUsd` converts that spot price directly into `priceUsd` via `sdkPool.token0Price`/`token1Price`: [2](#0-1) 

This price feeds `referenceRate`/`resolveLegRates` in the trading strategy, which sizes the order's fill amount (`computeLegPolicyOutput` extends the mid price linearly across the whole quantity, with no depth/impact term): [3](#0-2) [4](#0-3) 

The only defense is `checkPriceGuard`, which rejects quotes that deviate more than `maxDeviationBps` from a static, operator-configured `referencePrice`: [5](#0-4) 

This guard is **optional** ("the two go together — one without the other is rejected... omit both to leave the chain unguarded") and, even when configured, only bounds deviation from a stale static reference, not manipulation *within* that band, and does not account for execution/slippage cost: [6](#0-5) [7](#0-6) 

An unprivileged actor able to move the pool's spot price atomically (e.g., a flash-loan swap through the V4 pool in the block/transaction preceding order submission, then reverting the swap after the solver reads the manipulated price) can:
- Push the price up before submitting a USDC→exotic order, forcing the solver to release more exotic tokens than the true market rate warrants, or
- Push the price down before submitting the reverse leg, forcing the solver to accept less USDC than warranted while still delivering the full exotic-token output.

This is the same class of attack as the KUB-Split incident (flash loan → pool reserve manipulation → the victim contract computes a bad price from the manipulated pool and pays out based on it), just with the Simplex solver's wallet as the victim instead of a lending/LP contract.

### Impact Explanation
A successful attack causes concrete theft of solver funds: the solver either overpays the exotic token or underreceives the stable token relative to the true market price, funded from live inventory/liquidity in `[vault.uniswapV4]` positions and the solver's wallet. Given intents can be sized up to `maxOrderSize`, losses scale with pool liquidity/available position depth and the achievable price deviation. This satisfies "concrete theft ... via pool manipulation," matching the report's severity class (Medium).

### Likelihood Explanation
Reachable end-to-end by a single unprivileged intent submitter with a flash loan or capital sufficient to move the configured V4 pool (often a thin exotic/stable pool, as implied by cNGN-style low-liquidity pairs in the docs). No governance/admin access is required; the `checkPriceGuard` is optional and, in the sample config shown in the docs, is only advisory (percentage band), not a hard TWAP or execution-cost check. The precedent of the KUB-Split flash loan (spot-price manipulation of a low-liquidity pool) directly supports feasibility of this attack pattern against a similarly-shaped spot-price consumer.

### Recommendation
- Replace the single-block spot price (`sqrtPriceX96`/tick) with a manipulation-resistant price source (TWAP over multiple blocks, or an external oracle) for venue-priced pairs.
- Make `referencePrice`/`maxDeviationBps` mandatory (not optional) for any `[vault.uniswapV4]`-priced pair, and tighten the guard to reject on same-block/likely-manipulated deviations, not just static-reference drift.
- Incorporate execution-size/price-impact into `computeLegPolicyOutput` rather than pricing the whole notional at the unweighted mid.
- Consider requiring the pool quote to be corroborated by a second independent source (e.g., CEX price feed or another DEX) before sizing large fills.

### Proof of Concept
1. Attacker takes a flash loan and swaps a large amount through the configured Uniswap V4 exotic/USDC pool used by a Simplex `[vault.uniswapV4]` position, moving `sqrtPriceX96` far from the true market price.
2. In the same block (or immediately after, before the pool reverts to equilibrium), attacker submits/triggers a cross-chain intent order on the venue-priced pair.
3. Simplex's `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd` reads the manipulated `sqrtPriceX96` and returns a skewed USD price [1](#0-0) .
4. `resolveLegRates`/`computeLegPolicyOutput` sizes the fill from this skewed price, and (if `checkPriceGuard` is unconfigured or the manipulated price stays within `maxDeviationBps`) the solver fills the order at the bad rate, transferring excess value to the attacker.
5. Attacker reverses the initial swap/repays the flash loan, pocketing the difference extracted from the solver.

Note: I could not fully trace `resolveLegRates`'s complete order-sizing logic in `fx.ts` (only partial excerpts were retrievable via the index), so the exact bound on extractable value per fill (e.g., whether `maxOrderSize` or partial-fill caps limit the blast radius) is not fully confirmed. A Devin session with full repo access would be needed to pin down these limits precisely.

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L206-239)
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1344-1364)
```typescript
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

**File:** sdk/packages/simplex/src/tests/strategies/fx.price-guard.test.ts (L140-144)
```typescript
	it("sizes unguarded when no reference is configured (guard is optional)", async () => {
		const { filler, pair } = makeVenueFiller()
		const rate = await referenceRate(filler, pair, "1400")
		expect(rate?.toFixed(0)).toBe("1400")
	})
```
