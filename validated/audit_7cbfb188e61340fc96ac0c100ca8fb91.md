### Title
Uniswap V4 spot-price venue pricing with unenforced/optional deviation guard lets an attacker manipulate the solver's fill price - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
Simplex's Uniswap-V4 venue pricing prices an entire order leg off the instantaneous pool mid-price (`sqrtPriceX96`/tick), with no TWAP, no depth/size-impact adjustment, and only an *optional* static-reference deviation guard. This is structurally the same flaw as the referenced report: relying on a manipulable spot AMM price to drive an economically consequential on-chain action (here, a solver's fill/fund decision instead of `rebalance()`), enabling a JIT/flash-manipulation attack that extracts value from the solver's committed liquidity.

### Finding Description
`UniswapV4FundingPlanner.computeDirectPoolPriceUsd` derives the USD price of the exotic token directly from the SDK `Pool`'s `token0Price`/`token1Price`, which are computed from the pool's live `sqrtPriceX96` read at refresh time via `UniswapV4LiquidityState.refresh()`: [1](#0-0) 

`UniswapV4LiquidityState.refresh()` reads `getSlot0`/`getLiquidity` from the on-chain `StateView` contract with no cumulative/TWAP observation and no minimum-liquidity/impact check: [2](#0-1) 

The internal flow documentation confirms this is used to price fills without any impact term, and that the only defense is an optional, static-reference deviation guard that checks deviation, not execution cost: [3](#0-2) 

The public docs corroborate that the pool itself "acts as the price oracle instead of a static curve," that the resulting quote is a *single* price used for both directions (no independent bid/ask spread), and that the `referencePrice`/`maxDeviationBps` guard is entirely optional per position — "omit both to leave the chain unguarded": [4](#0-3) 

Configuration validation only enforces internal consistency of the guard fields (both-or-neither), never that a guard is actually configured: [5](#0-4) 

This mirrors the WATCHPUG finding precisely: an unprivileged actor can cheaply move a Uniswap pool's instantaneous price (e.g., via a large swap or JIT liquidity placement in the same block), causing a downstream economically significant on-chain action — venue-funded order fills sized off that price — to execute at an attacker-favorable rate, then reverse the manipulation to profit. Any pair configured under `[vault.uniswapV4]` without `referencePrice`/`maxDeviationBps` is completely unguarded; even guarded pairs are only checked for deviation from a static number, not for the execution cost of sourcing liquidity through the pool's own fee tier (a separate issue the same doc explicitly flags: "the pool's fee tier ... is never applied to the price, and there is no size or impact term").

### Impact Explanation
An attacker who manipulates the Uniswap V4 pool price for an exotic-token pair funded via `[vault.uniswapV4]` (and, worse, for any pair operators left unguarded, which the config explicitly permits) can force the solver to price and fund a fill at a manipulated rate. Combined with placing/timing the intent order itself, this lets the attacker extract solver-held liquidity (the withdrawn LP position tokens) at a discount, causing concrete economic loss to the filler's committed on-chain capital — the same class of "manipulated price triggers protocol/solver to transact at attacker-favorable conditions" impact as the original report, just realized against a Hyperbridge intent-solver instead of USSD's rebalancer.

### Likelihood Explanation
Likelihood is High for unguarded pairs (guard is opt-in per position) and Medium for guarded pairs (guard only bounds against a static reference, not execution/impact cost, and Uniswap V4 pools are well known to be manipulable at low cost with flash loans/JIT liquidity within a single block, as in the original report's PoC). No privileged access is required — any user placing an intent order combined with a pool-price manipulation transaction can trigger this path.

### Recommendation
- Require a TWAP (time-weighted average, sampled across multiple blocks) rather than the instantaneous `sqrtPriceX96`/tick for venue pricing, consistent with the original report's recommendation.
- Make the `referencePrice`/`maxDeviationBps` guard mandatory (not optional) whenever `[vault.uniswapV4]` pool-based pricing is used, rather than allowing operators to "leave the chain unguarded."
- Incorporate pool liquidity depth/size-impact into the priced quantity rather than pricing the whole leg linearly at the mid, and apply the pool's actual fee tier to the quoted rate.

### Proof of Concept
1. Operator configures a `[vault.uniswapV4]` pair (e.g., USDC/CNGN) without `referencePrice`/`maxDeviationBps` (permitted per `docs/content/developers/evm/simplex/pricing.mdx` and unenforced by `validateConfig` in `filler-toml.ts`).
2. Attacker takes a flash-loan-funded swap (or JIT liquidity) against the configured Uniswap V4 pool to move `sqrtPriceX96` sharply in their favor.
3. Attacker submits/holds an intent order sized for the exotic-token leg while the price is manipulated.
4. `UniswapV4LiquidityState.refresh()` reads the manipulated `slot0`; `computeDirectPoolPriceUsd` derives the exotic-token USD price from it; `resolveLegRates`/`computeLegPolicyOutput` (per `venue-pricing-uniswap-v4-funded-pairs.md`) price and fund the fill at that rate, withdrawing solver-held LP liquidity at the distorted price.
5. Attacker reverses the pool manipulation, realizing profit at the solver's expense.

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L242-275)
```typescript
	/**
	 * Computes the USD price of the non-stable token in a pool.
	 * Returns null if neither currency is USDC/USDT on this chain.
	 */
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

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4LiquidityState.ts (L139-217)
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

			this.sdkPools.set(poolId, sdkPool)
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
