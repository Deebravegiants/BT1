### Title
Uniswap V4 spot-price venue pricing lets an attacker flash-loan manipulate the exotic-token fill rate and drain Simplex solver funds - (File: `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
Simplex's venue-based FX pricing for cross-asset pairs (`[vault.uniswapV4]`) derives the price of an "exotic" token directly from a Uniswap V4 pool's instantaneous `sqrtPriceX96` (spot price from `slot0`), the same class of vulnerability as the reported Mav oracle issue where spot reserves/price are used unguarded as an oracle. This price feeds directly into how much the solver pays out (or accepts) when filling a user's intent order.

### Finding Description
When a trading pair has no static bid/ask curve, Simplex prices it from a live Uniswap V4 position/pool instead:

`UniswapV4FundingPlanner.getExoticTokenPrice` -> `computeDirectPoolPriceUsd` reads the pool's raw mid price straight from `sqrtPriceX96`: [1](#0-0) 

That live `sqrtPriceX96`/`slot0` state is refreshed straight from the chain with no TWAP or averaging: [2](#0-1) 

This price is used as the venue rate for the pair in `referenceRate`/`sizeOrder`, converting user order amounts into the notional the solver will fill at: [3](#0-2) 

The project's own documentation acknowledges this is unguarded by default: pool-based pricing "trusts the live pool," and the only defense (`referencePrice`/`maxDeviationBps`) is optional — "omit both to leave the chain unguarded": [4](#0-3) 

Exactly like the Mav `getReserves()` spot-price issue, an attacker can flash-loan a large swap through the same Uniswap V4 pool immediately before submitting (or racing) an intent order, moving `sqrtPriceX96`/tick so that `computeDirectPoolPriceUsd` returns a manipulated USD price for the exotic token. Because `checkPriceGuard` is the only mitigation and is opt-in per position (`referencePrice`/`maxDeviationBps` must both be configured; otherwise the chain is "unguarded"), any pool-priced pair without that guard configured is fully exposed. Even guarded, `maxDeviationBps` bounds by a static reference, not execution cost, and the guard checks only against the manipulated spot value itself (no minimum liquidity / depth or TWAP requirement), so a large-enough single-block manipulation within the tolerance still succeeds.

### Impact Explanation
A manipulated spot price directly controls how much of the exotic token the solver delivers to (or takes from) a user filling a cross-asset intent order, and also feeds `positionAmountOfToken`-based inventory valuation logic used elsewhere in intent bid aggregation. In the funding/pricing path, an attacker who moves the pool price before an order is filled can force the solver to pay out far more value than it receives (or acquire the user's input for far less than it's worth), directly draining solver-held funds — concrete theft of funds reachable by a single unprivileged actor issuing a flash-loan swap plus a normal intent order fill. This satisfies the "concrete theft of funds" impact bar.

### Likelihood Explanation
Likelihood is high for any deployment that configures Uniswap V4 venue pricing without the optional `referencePrice`/`maxDeviationBps` guard (explicitly called out in the docs as a supported, unguarded configuration), and thinly-liquid "exotic" token pools (e.g., a new stablecoin-like asset such as cNGN, the example used throughout the docs) are exactly the kind of pool cheap to move with a flash loan. The attack requires only capital for one flash loan/swap plus a normally-permitted intent order — no privileged access.

### Recommendation
Do not use the raw, single-block `sqrtPriceX96`/spot pool price as the sole pricing input. Use a TWAP (time-weighted average price) over a manipulation-resistant window, require a minimum on-chain liquidity/depth threshold before trusting a pool, and make the `referencePrice`/`maxDeviationBps` guard mandatory (not optional) for every venue-priced pair, with the deviation check also bounding against a liquidity-depth-aware price impact rather than only a static reference.

### Proof of Concept
1. Attacker identifies a `[vault.uniswapV4]`-priced pair (e.g., USDC/cNGN) configured without `referencePrice`/`maxDeviationBps` (a supported configuration per the docs).
2. Attacker takes a flash loan and swaps a large amount through the pool backing that position, shifting `sqrtPriceX96` sharply in the attacker's favor.
3. In the same block (or before the solver's next `refresh()`), attacker submits an intent order that Simplex fills using `UniswapV4FundingPlanner.getExoticTokenPrice` → `computeDirectPoolPriceUsd`, which reads the now-manipulated `slot0` price via `UniswapV4LiquidityState.refresh`.
4. `referenceRate`/`sizeOrder` in `fx.ts` price the leg using this manipulated rate, causing the solver to fill at a price far from fair value.
5. Attacker repays the flash loan, reverses the swap, and keeps the difference extracted from the solver's funded position.

I was unable to fully verify runtime enforcement of the "mandatory" nature of `checkPriceGuard` across all code paths (e.g., whether every call site of `getExoticTokenPrice`/`referenceRate` unconditionally applies it), since the guard's call sites and exact implementation body were only partially retrievable from the index; a full review of `sdk/packages/simplex/src/strategies/fx.ts` (the `checkPriceGuard` function body) would be needed to confirm whether any pool-priced call path bypasses the guard entirely versus merely lacking the optional reference values.

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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
```
