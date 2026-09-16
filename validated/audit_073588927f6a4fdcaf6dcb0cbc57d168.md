### Title
Simplex FX filler prices intents from a manipulable Uniswap V4 spot price with no TWAP protection - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
`UniswapV4FundingPlanner.computeDirectPoolPriceUsd` / `getExoticTokenPrice` derive a venue price directly from the pool's current `sqrtPriceX96`/tick (a single-block spot read), and `FXFiller.resolveLegRates` / `referenceRate` in `sdk/packages/simplex/src/strategies/fx.ts` use that spot price, unmodified, to size and price intent fills for "venue-priced" pairs. This is the same root cause as the referenced `USSDRebalancer.getOwnValuation()` finding: a critical financial decision (how much output token to release for a given input) is driven by an instantaneous AMM price that any unprivileged actor can move within the same transaction/block, with no TWAP or execution-cost accounting.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`) calls `state.refresh()` immediately before pricing, which re-reads live `slot0` (`sqrtPriceX96`, `tick`) via `StateView.getSlot0` (`UniswapV4LiquidityState.ts:139-230`), then builds an SDK `V4Pool` from that raw, current price and returns `sdkPool.token0Price`/`token1Price` as the USD price of the exotic token (`computeDirectPoolPriceUsd`, lines 246-275). This is a raw pool mid, not a TWAP.

`FXFiller.resolveLegRates` (`sdk/packages/simplex/src/strategies/fx.ts:1436-1480`) consumes this venue price for any curveless pair whose `token0` is a USD stable, inverting it into the leg's trading rate. The only defense applied is `checkPriceGuard`, which — per `docs/content/developers/evm/simplex/pricing.mdx:68-84` and `sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md:12,17-22` — compares the live quote against a **static, optional** `referencePrice`/`maxDeviationBps` pair; if the operator omits those fields ("omit both to leave the chain unguarded"), there is no protection at all, and even when set, the guard only bounds *deviation from a fixed reference*, not *execution cost* or *manipulation within the same block*.

An attacker can therefore, within a single flashswap/large swap against the configured Uniswap V4 pool (executed atomically with, or immediately before, submitting/triggering the intent fill), push the pool's spot price to a favorable extreme, causing the filler to compute an inflated `policyMaxOutput` for a leg (`computeLegPolicyOutput`, `fx.ts:1397-1434`) and release more of the exotic/stable token than the pool's real (undistorted) liquidity-weighted price would justify. The filler's on-chain settlement (`fillOrder` via `IntentGatewayV2`) then transfers those tokens out under the manipulated valuation.

### Impact Explanation
This lets an attacker directly drain filler/solver funds by manipulating a single pool price read used to price and size a real fund transfer, mirroring the "theft of funds via manipulable spot price" class in the source report. Because `checkPriceGuard` is optional and, even when enabled, only screens for drift from a static number rather than transient manipulation or execution slippage, the protection is easily rendered ineffective by choosing a `referencePrice` close to (but tolerant of) the manipulated price, or by operators who leave it unset as the documentation explicitly allows.

### Likelihood Explanation
Reachable by any unprivileged actor: submit a swap against the configured Uniswap V4 pool (a standard, permissionless action) to move `slot0`, then have an order routed to the FX filler for that pair fill at the distorted rate. No privileged role, governance, or off-chain-only condition is required — only a pool with enough tradable depth relative to attacker capital (potentially amplified via flashloans), which is the standard precondition for this bug class.

### Recommendation
- Replace the raw `slot0` spot read with a manipulation-resistant price source: a Uniswap V4/V3 TWAP oracle (observation window), or an external oracle (Chainlink) cross-checked against the pool price.
- Make `checkPriceGuard`'s `referencePrice`/`maxDeviationBps` mandatory for any venue-priced pair rather than optional, and additionally bound the guard against a TWAP rather than only a static reference.
- Add slippage/execution-cost accounting to `computeLegPolicyOutput` so a fill's realized rate reflects the actual liquidity consumed, not a fixed linear extension of the instantaneous mid price.

### Proof of Concept
1. Configure a Simplex FX filler with a curveless, venue-priced pair (`[vault.uniswapV4]`) with no `referencePrice`/`maxDeviationBps` set (permitted per `pricing.mdx`), or with lax bounds.
2. Attacker swaps a large amount into/out of the underlying Uniswap V4 pool to shift `slot0`/`sqrtPriceX96` favorably.
3. Attacker (or an accomplice) submits/triggers an IntentGateway order routed to this pair while the price is distorted; `getExoticTokenPrice` → `computeDirectPoolPriceUsd` returns the manipulated mid, `resolveLegRates`/`computeLegPolicyOutput` size the fill against it, and the filler's `fillOrder` transfers an inflated amount of tokens.
4. Attacker reverses the initial swap (or lets natural arbitrage restore price), retaining the outsized output extracted from the filler at the manipulated rate — net profit funded by the filler's inventory, exactly analogous to the flashswap manipulation described in the source `USSDRebalancer.getOwnValuation()` report. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L139-216)
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

		// Refresh per-position liquidity and rebuild SDK Pool objects
		for (const pos of this.positions.values()) {
			const key = pos.tokenId.toString()
			const poolId = this.tokenIdToPoolId.get(key)
			const poolState = poolId ? poolStateMap.get(poolId) : undefined
			if (!poolId || !poolState) {
				throw new Error(
					`UniswapV4 refresh: missing pool state for tokenId ${key} (poolId=${poolId ?? "undefined"})`,
				)
			}

			// Read current position liquidity
			const liquidity = (await client.readContract({
				address: pos.positionManager,
				abi: UNISWAP_V4_POSITION_MANAGER_ABI,
				functionName: "getPositionLiquidity",
				args: [pos.tokenId],
			})) as bigint

			pos.liquidity = liquidity
			const prevOnChain = this.lastOnChainLiquidity.get(key) ?? liquidity
			const decrease = prevOnChain > liquidity ? prevOnChain - liquidity : 0n
			const prevConsumed = this.consumed.get(key) ?? 0n
			const newConsumed = prevConsumed > decrease ? prevConsumed - decrease : 0n
			this.consumed.set(key, newConsumed)
			this.lastOnChainLiquidity.set(key, liquidity)
			pos.remainingLiquidity = liquidity > newConsumed ? liquidity - newConsumed : 0n
			pos.sqrtPriceX96 = poolState.sqrtPriceX96
			pos.currentTick = poolState.tick

			// Build SDK Pool (without tick data provider — we only need amount calcs)
			const currency0 = currencyFromHydratedDecimals(chainId, pos.currency0, pos.decimals0)
			const currency1 = currencyFromHydratedDecimals(chainId, pos.currency1, pos.decimals1)

			const sdkPool = new V4Pool(
				currency0,
				currency1,
				pos.fee,
				pos.tickSpacing,
				pos.hooks,
				poolState.sqrtPriceX96.toString(),
				poolState.poolLiquidity.toString(),
				poolState.tick,
			)

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1397-1434)
```typescript
	private computeLegPolicyOutput(
		inputAmount: bigint,
		inputIsToken0: boolean,
		token0Decimals: number,
		token1Decimals: number,
		/**
		 * Token0 left in the pair's per-order exposure budget, or `null` to price the whole
		 * input unbudgeted. Only a price probe passes `null`: it commits no capital, so there
		 * is no exposure to ration, and a clamped quantity would silently misprice it.
		 */
		remainingToken0: Decimal | null,
		rate: Decimal,
	): { token0Used: Decimal; policyMaxOutput: bigint } | null {
		let legMaxToken0: Decimal
		if (inputIsToken0) {
			legMaxToken0 = new Decimal(formatUnits(inputAmount, token0Decimals))
		} else {
			legMaxToken0 = new Decimal(formatUnits(inputAmount, token1Decimals)).div(rate)
		}

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
	}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1436-1480)
```typescript
	/**
	 * Resolves the pricing rate (token1 per token0) for a leg: the venue quote
	 * when available (validated against the price guard; USD-stable token0
	 * pairs only), otherwise the pair's curve for the leg's direction at the
	 * pair's capped token0 notional. Returns null when the leg cannot be priced
	 * (guard tripped, or direction disabled).
	 */
	private async resolveLegRates(
		orderId: string | undefined,
		leg: ResolvedLeg,
		cappedPairNotional: Decimal,
		venueUsdPrice: (chain: string, token1Address: string) => Promise<Decimal | null>,
	): Promise<LegRates | null> {
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
		}

		const askRate = leg.pair.askPricePolicy?.getPrice(cappedPairNotional) ?? null
		const bidRate = leg.pair.bidPricePolicy?.getPrice(cappedPairNotional) ?? null

		const rate = leg.inputIsToken0 ? askRate : bidRate
		if (!rate) {
			this.logger.debug(
				{ orderId, pair: `${leg.pair.token0}/${leg.pair.token1}`, inputIsToken0: leg.inputIsToken0 },
				"Rejecting leg: direction disabled for one-sided LP",
			)
			return null
		}
		return { rate, oppositeRate: leg.inputIsToken0 ? bidRate : askRate, priceSource: "policy" }
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
