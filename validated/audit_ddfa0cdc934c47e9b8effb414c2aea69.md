## Analog Found

### Title
Uniswap V4 venue pricing for exotic-token intent fills relies on an unprotected spot pool price, enabling flash-loan price manipulation to drain solver liquidity - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Simplex's `FXFiller` prices "curveless" exotic-token pairs (pairs configured without static bid/ask curves) directly off a live Uniswap V4 pool's instantaneous mid-price, derived from `sqrtPriceX96`. This is the same bug class as the reported Ichi vault LP oracle issue: a financial decision (how much of an asset to deliver against a fixed input) is driven by momentary AMM pool state that a flash-loan can push to an extreme within a single block, and the only mitigation (`checkPriceGuard`) is optional, per-position, and checks deviation from a static reference rather than protecting against the manipulation itself.

### Finding Description
When a trading pair has no configured curves and its `token0` is a USD stablecoin, `FXFiller.resolveLegRates` prices the leg from the pool instead of a curve: [1](#0-0) 

`venueUsdPrice` resolves to `UniswapV4FundingPlanner.getExoticTokenPrice`, which iterates the configured V4 positions and calls `computeDirectPoolPriceUsd`, returning `sdkPool.token0Price`/`token1Price` — the **raw pool mid**, computed straight from `sqrtPriceX96`: [2](#0-1) [3](#0-2) 

The pool state itself is read fresh, on demand, immediately before pricing — no TWAP, no averaging window: [4](#0-3) 

The only safeguard is `checkPriceGuard`, which is **optional** (config validation only requires `referencePrice`/`maxDeviationBps` to be set together, never mandates them) and simply compares the manipulated spot quote to a static, operator-configured reference — it does not check execution/price-impact cost of the trade itself: [5](#0-4) [6](#0-5) 

This exact gap is documented internally: [7](#0-6) 

Compounding this, the per-leg overfill protection that would otherwise cap losses from a bad quote has been explicitly disabled (warn-only): [8](#0-7) 

### Impact Explanation
An attacker (an unprivileged intent submitter, exactly the actor class in scope) can flash-loan swap against the configured Uniswap V4 pool immediately before/alongside submitting (or having filled) an intent order on a venue-priced pair. This pushes `sqrtPriceX96` so that `computeDirectPoolPriceUsd` reports the exotic token as cheaper in USD than its true market value. `resolveLegRates` then derives `rate = 1/venueUsd`, causing the solver to compute and deliver an inflated quantity of the exotic token for a fixed USD-stable input — a direct theft of solver-held liquidity (wallet balance and/or Uniswap V4 LP position funds withdrawn to fund the fill). Because the overfill clamp is disabled and the price guard is optional (and even when present, only checks deviation from a static reference, not the trade's price impact), the manipulation is not blocked by any on-chain or off-chain circuit breaker.

### Likelihood Explanation
Any pair configured under `[vault.uniswapV4]` without a price guard (or with a wide `maxDeviationBps`) is immediately exploitable with a single flash-loaned swap on the reference pool, requiring no privileged access — only capital for the flash loan and an intent order that lands in the manipulated block/state.

### Recommendation
Replace the raw `sqrtPriceX96`-derived spot mid with a manipulation-resistant reference, e.g., a TWAP over the pool's observation window, or require the venue price to be cross-checked against an independent oracle before use, in the same way the Ichi report recommends checking hysteresis/TWAP deviation. Make the price guard mandatory for every venue-priced position (not optional), and additionally check post-trade price impact/execution cost rather than only spot deviation from a static reference. Re-enable and enforce the overfill clamp instead of merely warning.

### Proof of Concept
1. Configure (or observe an operator running) a curveless pair, e.g. `USDC/EXOTIC`, funded via `[vault.uniswapV4]` with no `referencePrice`/`maxDeviationBps` guard (this is a valid, explicitly supported configuration per `docs/content/developers/evm/simplex/pricing.mdx`).
2. Attacker takes a flash loan and swaps heavily against the configured Uniswap V4 pool, moving `sqrtPriceX96` so `EXOTIC`'s USD price appears far below its true value.
3. Attacker (or an accomplice) submits/has an intent order filled on this pair in the same block; `FXFiller.resolveLegRates` -> `getVenueUsdPrice` -> `UniswapV4FundingPlanner.getExoticTokenPrice` reads the manipulated `sqrtPriceX96` and returns the depressed USD price.
4. `venueRate = 1/venueUsd` is abnormally high; the solver computes and delivers an inflated `EXOTIC` amount for the attacker's USDC input, funded by withdrawing from the solver's Uniswap V4 LP position(s) (`planWithdrawalForToken`), realizing a loss for the solver equal to the manipulated spread.
5. Attacker repays the flash loan, netting the difference between the manipulated fill and the true market price.

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1443-1466)
```typescript
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

**File:** sdk/packages/simplex/src/config/filler-toml.ts (L413-452)
```typescript
	// Per-position price guard: referencePrice and maxDeviationBps are optional but
	// must be set together. A given chain may not carry conflicting guard values.
	const guardByChain: Record<string, { referencePrice: string; maxDeviationBps: number }> = {}
	for (const position of uniswapV4?.positions ?? []) {
		const hasRef = position.referencePrice !== undefined
		const hasBps = position.maxDeviationBps !== undefined
		if (hasRef !== hasBps) {
			throw new Error(
				"vault.uniswapV4: a position price guard needs both 'referencePrice' and 'maxDeviationBps', or neither",
			)
		}
		if (!hasRef) continue

		const parsedRef = Number(position.referencePrice)
		if (!Number.isFinite(parsedRef) || parsedRef <= 0) {
			throw new Error(
				`vault.uniswapV4: position 'referencePrice' for chain '${position.chain}' must be a positive number`,
			)
		}
		if (
			!Number.isFinite(position.maxDeviationBps!) ||
			position.maxDeviationBps! <= 0 ||
			position.maxDeviationBps! > 10_000
		) {
			throw new Error(
				`vault.uniswapV4: position 'maxDeviationBps' for chain '${position.chain}' must be a number between 0 (exclusive) and 10000`,
			)
		}
		const existing = guardByChain[position.chain]
		if (
			existing &&
			(existing.referencePrice !== position.referencePrice || existing.maxDeviationBps !== position.maxDeviationBps)
		) {
			throw new Error(`vault.uniswapV4: conflicting price guard values for chain '${position.chain}'`)
		}
		guardByChain[position.chain] = {
			referencePrice: position.referencePrice!,
			maxDeviationBps: position.maxDeviationBps!,
		}
	}
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
