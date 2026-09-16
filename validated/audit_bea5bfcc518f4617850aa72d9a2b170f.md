## Title
Unbounded spot-price manipulation of Simplex's Uniswap V4 venue pricing enables theft from the solver on curveless pairs - (File: `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

## Summary
Simplex's `UniswapV4FundingPlanner` prices "curveless" (venue-priced) trading pairs directly from the live Uniswap V4 pool's spot price (`slot0`/`sqrtPriceX96`), with no TWAP and no execution-cost/size adjustment, mirroring the Predy `Trade`/`UniHelper.getSqrtPrice()` finding where `slot0` spot price is trusted at face value. An attacker who submits an IntentGateway order can flash-loan manipulate the referenced Uniswap V4 pool immediately before or in the same block the solver quotes/fills, causing the solver to systematically mis-price the exotic token and give away more value than intended, or (if `referencePrice`/`maxDeviationBps` guard is left unconfigured) with no bound at all.

## Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice()` calls `computeDirectPoolPriceUsd()`, which returns `sdkPool.token0Price`/`token1Price` computed straight from the pool's current `sqrtPriceX96` read via `StateView.getSlot0()`: [1](#0-0) [2](#0-1) 

The underlying slot0 read happens in `UniswapV4LiquidityState.refresh()`, which fetches `getSlot0` (spot `sqrtPriceX96`/tick) fresh right before pricing/planning, and builds the SDK `Pool` object solely from that spot value — there is no cumulative/TWAP oracle involved: [3](#0-2) 

This price feeds `resolveLegRates`/`referenceRate` in the FX strategy to size and rate orders for curveless pairs, and the only defense on this path is `checkPriceGuard`, which — per the project's own documented flow — checks deviation against a **static** `referencePrice`, not execution cost or manipulation resistance, and is explicitly **optional** (both `referencePrice` and `maxDeviationBps` must be set together, or "leave the chain unguarded"): [4](#0-3) [5](#0-4) 

This is architecturally identical to the Predy `Trade`/`UniHelper` bug class: the raw pool spot price (`slot0` in Predy, `sqrtPriceX96` from `getSlot0` here) is read without a TWAP and used directly to size a trade, making it manipulable by a flash-loaned swap in the block immediately preceding the solver's fill. Even where the guard is configured, it only bounds deviation from a fixed reference, not the actual manipulation window (an attacker can push the price up to just under `maxDeviationBps` and still profit, or push it and pull it back before the guard's next poll, since the guard is evaluated per quote, not per block).

## Impact Explanation
An attacker can flash-loan manipulate the exotic-token/stablecoin Uniswap V4 pool that backs a curveless pair, then submit (or wait for) an IntentGateway order that the Simplex solver prices off that pool. Because `computeDirectPoolPriceUsd` uses the manipulated spot mid with no size/impact term (`computeLegPolicyOutput` extends the mid linearly across the whole quantity, per the flow doc) and the guard is either optional or only checks a coarse static deviation, the solver can be forced to deliver more output tokens than the true market price warrants, or accept less input value than required — a direct loss of solver funds each time an order interacting with a manipulated pool is filled. This is a concrete theft-of-funds vector reachable by a single unprivileged order submission plus a same-block/adjacent-block flash-loan swap, matching the Medium severity assigned to the analogous Predy finding.

## Likelihood Explanation
Likelihood is significant wherever a curveless `[vault.uniswapV4]` pair is configured without `referencePrice`/`maxDeviationBps` (explicitly permitted by the config validation, per the docs), and even when the guard is set, an attacker can size the manipulation to stay just inside `maxDeviationBps` while still extracting value from the mispriced quote, since the guard checks static deviation rather than any TWAP/impact-aware benchmark. Flash loans on the underlying chain make transient pool manipulation cheap and readily available to any address.

## Recommendation
Do not price curveless pairs from a single spot read of `slot0`/`sqrtPriceX96`. Use a TWAP over a meaningful window (e.g., Uniswap V4's truncated oracle observations or an off-chain aggregated feed) instead of the instantaneous pool mid, apply the pool's fee tier and a size/impact-aware quote rather than a linear extension of the mid, and make the `referencePrice`/`maxDeviationBps` guard mandatory (not optional) for any venue-priced pair, with deviation measured against a manipulation-resistant reference rather than a static operator-set value.

## Proof of Concept
1. Operator configures a curveless pair (e.g., `USDC`/`CNGN`) priced solely via `[vault.uniswapV4]` with no `referencePrice`/`maxDeviationBps` (allowed per the docs' guard-is-optional callout).
2. Attacker flash-loans the underlying Uniswap V4 CNGN/USDC pool and swaps heavily to move `slot0`'s `sqrtPriceX96` favorably for themselves.
3. In the same or an adjacent block, attacker submits an IntentGateway order that the Simplex solver evaluates via `resolveLegRates → venuePriceMemo → UniswapV4FundingPlanner.getExoticTokenPrice → computeDirectPoolPriceUsd`, which reads the manipulated `slot0` (`UniswapV4LiquidityState.refresh`) and prices the fill off it.
4. Solver fills the order at the manipulated rate, delivering more value to the attacker than the true market price; attacker reverses the flash-loan swap, unwinding the pool price and repaying the loan, keeping the extracted surplus. [1](#0-0) [3](#0-2)

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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L146-215)
```typescript
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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L6-22)
```markdown
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
