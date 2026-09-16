### Title
Venue-priced Uniswap V4 pairs are filled against a raw, fee-blind spot price with only a static deviation guard - (File: `sdk/packages/simplex/src/strategies/fx.ts`, `sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts`)

### Summary
The external report itself contains no concrete vulnerability (it is a solgraph color-coding complaint), but its bug-class hint — a pricing/index utility (`PoolInfoUtils.sol`, `indexToPrice`/`priceToIndex`) whose correctness the reporter could not verify from a call graph alone — maps onto a real, verifiable pricing weakness in Hyperbridge's Simplex intent solver: the Uniswap V4 venue-pricing path that prices curveless cross-asset pairs directly off a live pool's `sqrtPriceX96` mid, with no fee-tier or size/impact adjustment, defended only by a static-reference deviation check.

### Finding Description
For pairs with no configured bid/ask curves, `resolveLegRates` in `sdk/packages/simplex/src/strategies/fx.ts` (lines 1443-1466) prices the leg from `venueUsdPrice`, which resolves through `UniswapV4FundingPlanner`'s pool lookup to `computeDirectPoolPriceUsd` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:242-276`). That function returns `sdkPool.token0Price`/`token1Price` — the pool's instantaneous mid derived from `sqrtPriceX96` — and nothing else [1](#0-0) .

The project's own AI-generated flow doc states the issue directly: the pool's fee tier is read and stored on the hydrated position but "never applied to the price," there is "no size or impact term," and `computeLegPolicyOutput` extends this raw mid linearly across the whole priced quantity [2](#0-1) . The only defense on this path is `checkPriceGuard`, which compares the live quote to a static `referencePrice` within `maxDeviationBps` [3](#0-2) , and that guard is optional per-chain configuration [4](#0-3) . Even when configured, the guard checks *deviation from a stale, operator-set reference*, not *execution cost* — it does not account for the fee the solver actually pays when it later swaps through that same pool to source inventory, nor for price impact proportional to the order's own size.

### Impact Explanation
Because the venue rate is a single price applied linearly regardless of order size, and the guard tolerance (`maxDeviationBps`, human-configured, e.g. 200 bps in the shipped example config [5](#0-4) ) is independent of the pool's actual fee tier and liquidity depth, a counterparty can submit a large or repeated order against a thin/manipulable pool and have it filled at a price inside the static-reference band that is nonetheless worse than the solver's real cost to acquire the output token (via LP redemption/swap). This directly reduces or negates the "Spread profit" and "Fee profit" the solver's economics rely on (see `docs/content/developers/evm/simplex/pricing.mdx:86-97`), constituting a fund-loss vector against the intent solver on a route it operates unattended.

### Likelihood Explanation
Reachable from a single submitted order: any counterparty can construct an order for a venue-priced pair (curveless, USD-stable `token0`) sized to move the pool's tick within the configured `maxDeviationBps` band (or targeting a chain/position where no guard is configured — the guard is opt-in per position) and profit from the fee/impact the pricing model omits. No privileged access is required; the config comments themselves acknowledge the deviation guard is the only defense and is optional [6](#0-5) .

### Recommendation
Incorporate the pool's actual fee tier and a size-dependent price-impact term into the venue quote (rather than a flat linear mid), and/or tighten `checkPriceGuard` to bound execution cost (e.g., simulate the LP redemption/swap cost) rather than only deviation from a static reference price.

### Proof of Concept
1. Operator configures a curveless pair with `[vault.uniswapV4]` pointing at a low-liquidity pool, with `referencePrice`/`maxDeviationBps` set loosely (or omitted).
2. Attacker moves the pool tick (e.g., via a swap in the same pool) to a level still within `maxDeviationBps` of the stale reference but where the true cost to redeem/swap for inventory (fee tier + impact) exceeds the quoted rate.
3. Attacker submits an intent order sized to this pair; `resolveLegRates` → `checkPriceGuard` passes (quote is within band) → order fills at the manipulated mid, ignoring the fee tier stored in `pos.fee` and the size impact, per `computeDirectPoolPriceUsd` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:246-276`).
4. Solver delivers tokens at a loss relative to its actual funding cost.

### Citations

**File:** sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts (L246-272)
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

**File:** sdk/packages/simplex/src/config/filler-toml.ts (L23-36)
```typescript
/** TOML row for a Uniswap V4 position; only chain + tokenId required. */
export interface UniswapV4PositionToml {
	chain: string
	tokenId: string // bigint as string in TOML
	/**
	 * Optional price guard. When set (alongside `maxDeviationBps`), the filler rejects
	 * orders whenever the pool quote on this chain drifts more than `maxDeviationBps`
	 * from this static reference price (exotic per USD, same units as the bid/ask curves).
	 * Guards against a manipulated, stale, or thin pool.
	 */
	referencePrice?: string
	/** Tolerance in basis points for the price guard. Required when `referencePrice` is set. */
	maxDeviationBps?: number
}
```

**File:** sdk/packages/simplex/filler-config-example.toml (L281-292)
```text
# Uniswap V4 LP positions (optional) — exotic-token funding and pool-based
# pricing for cross-asset pairs without curves (USD-stable token0 only).
# Optional per-position price guard: referencePrice (token1 per USD) +
# maxDeviationBps reject orders when the live pool quote drifts out of band.
# One-sided pool pricing: side = "ask" (sell token1) or "bid" (buy token1).
#
# [vault.uniswapV4]
# spreadBps = 50              # LP redemption slippage tolerance (default 50)
# side = "ask"
# positions = [
#     { chain = "EVM-8453", tokenId = "2087350", referencePrice = "1575", maxDeviationBps = 200 },
# ]
```
