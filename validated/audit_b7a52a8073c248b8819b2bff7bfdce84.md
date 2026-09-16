### Title
Unguarded Uniswap V4 spot-price venue pricing enables flash-loan price manipulation against Simplex intent fills - (File: `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
Simplex's intent-solver pricing engine (`FXFiller`) can price curveless cross-asset pairs directly from the instantaneous Uniswap V4 pool spot price (`sqrtPriceX96`) rather than a manipulation-resistant TWAP. The only mitigation, a static `referencePrice`/`maxDeviationBps` guard, is explicitly optional and per-position, leaving any unconfigured chain "unguarded." An unprivileged actor who can flash-loan-manipulate the backing Uniswap V4 pool in the same block as submitting/triggering an order fill can force the solver to value and deliver the exotic token at an attacker-favorable price, draining solver-held liquidity — the same bug class as the SpaceGodzilla incident (flash-loan AMM spot-price manipulation exploited for arbitrage against a project relying on live pool prices).

### Finding Description
When a trading pair has no static bid/ask curves and `token0` is a USD stablecoin, `FXFiller.resolveLegRates` prices the leg from a live venue quote instead of a curve: [1](#0-0) 

The venue quote comes from `UniswapV4FundingPlanner.getExoticTokenPrice`, which reads the pool's current tick/`sqrtPriceX96` via `state.refresh()` and derives the raw pool mid with `computeDirectPoolPriceUsd`: [2](#0-1) [3](#0-2) 

This is a raw spot price (`sdkPool.token0Price`/`token1Price`), not a time-weighted average, and it is refreshed on-demand immediately before pricing/withdrawal planning: [4](#0-3) 

The only defense against a manipulated quote is `checkPriceGuard`, which compares the live quote against a static `referencePrice` within `maxDeviationBps` — but both fields are optional, and the docs state "The two fields must be set together; omit both to leave the chain unguarded": [5](#0-4) [6](#0-5) 

The test suite explicitly documents the unguarded behavior: [7](#0-6) 

Additionally, even when a guard is configured, it only checks deviation from a static reference — it does not detect a fee-tier-unaware, sizeless extrapolation of the mid across the whole quantity, as documented: [8](#0-7) 

### Impact Explanation
An attacker can flash-loan-manipulate the Uniswap V4 pool backing an exotic token that Simplex venue-prices (e.g., the documented USDC/CNGN pool), then within the same or an adjacent block, submit an IntentGateway order sized to exploit the distorted price. If the chain/position has no `referencePrice`/`maxDeviationBps` configured — an explicitly supported, "unguarded" configuration — the solver has no defense and fills the order using `computeDirectPoolPriceUsd`'s manipulated mid, transferring solver-held tokens (from its Uniswap V4 LP position or wallet) to the attacker at a price far from fair value. This is a direct, concrete loss of solver funds, mirroring the SpaceGodzilla flash-loan/AMM-price-manipulation bug class where a manipulated pool price was exploited for arbitrage profit.

### Likelihood Explanation
Reaching this path requires only (1) locating/operating a solver configured for Uniswap-V4 venue pricing without a price guard, or with a guard whose `maxDeviationBps` is wide enough to admit a flash-loan-scale swing, and (2) enough capital/flash-loan access to move the specific pool's price — routine for thin pools such as the CNGN/USDC example used throughout the docs and tests. No privileged access is required; the attacker only needs to submit a normal cross-chain intent order, which is exactly the "unprivileged intent solver" attack surface in scope.

### Recommendation
- Make the price guard (`referencePrice`/`maxDeviationBps`) mandatory for any Uniswap V4 venue-priced pair rather than optional, or better, replace the manual static reference with an automatically-maintained TWAP/oracle cross-check.
- Price from a Uniswap V4 TWAP (multi-block observation) instead of the instantaneous `sqrtPriceX96` slot0 mid in `computeDirectPoolPriceUsd`.
- Incorporate pool liquidity/fee-tier and order-size impact into the guard so thin pools cannot be trivially skewed within the allowed deviation band.
- Add a same-block/same-transaction reentrancy or block-delta check (e.g., reject fills whose pricing pool state changed within N blocks) to blunt atomic flash-loan manipulation.

### Proof of Concept
1. Deploy/observe a Simplex filler configured with `[vault.uniswapV4]` positions for a pair like USDC/CNGN, with no `referencePrice`/`maxDeviationBps` set (a supported configuration per `docs/content/developers/evm/simplex/pricing.mdx`).
2. Attacker takes a flash loan and executes a large swap against the CNGN/USDC Uniswap V4 pool to skew `sqrtPriceX96` favorably.
3. In the same block (or before the price reverts), attacker submits an IntentGatewayV2 order requesting CNGN output priced against USDC input.
4. `FXFiller.resolveLegRates` → `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd` reads the manipulated `sqrtPriceX96` and returns a distorted USD price; with no guard configured, `checkPriceGuard` passes trivially (`fx.ts` lines 429-430: `if (!guard || guard.reference.lte(0)) return true`).
5. The solver fills the order at the manipulated rate, withdrawing liquidity from its V4 position (`UniswapV4FundingPlanner.planWithdrawalForToken`) and delivering more CNGN than the fair-value trade would warrant, realizing a loss equal to the price distortion.

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1449-1465)
```typescript
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
```

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L139-170)
```typescript
	async refresh(): Promise<void> {
		const client = this.clientManager.getPublicClient(this.chain)
		const chainId = chainIdFromIdentifier(this.chain)

		// Group positions by poolId to avoid duplicate pool state fetches
		const poolIds = new Set(this.tokenIdToPoolId.values())

		// Fetch slot0 + liquidity for each unique pool via StateView
		const poolStateMap = new Map<string, { sqrtPriceX96: bigint; tick: number; poolLiquidity: bigint }>()

		for (const poolId of poolIds) {
			const [slot0Result, poolLiquidity] = await Promise.all([
				client.readContract({
					address: this.stateView,
					abi: UNISWAP_V4_STATE_VIEW_ABI,
					functionName: "getSlot0",
					args: [poolId as HexString],
				}) as Promise<[bigint, number, number, number]>,
				client.readContract({
					address: this.stateView,
					abi: UNISWAP_V4_STATE_VIEW_ABI,
					functionName: "getLiquidity",
					args: [poolId as HexString],
				}) as Promise<bigint>,
			])

			poolStateMap.set(poolId, {
				sqrtPriceX96: slot0Result[0],
				tick: slot0Result[1],
				poolLiquidity,
			})
		}
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
```

**File:** sdk/packages/simplex/src/tests/strategies/fx.price-guard.test.ts (L140-144)
```typescript
	it("sizes unguarded when no reference is configured (guard is optional)", async () => {
		const { filler, pair } = makeVenueFiller()
		const rate = await referenceRate(filler, pair, "1400")
		expect(rate?.toFixed(0)).toBe("1400")
	})
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
