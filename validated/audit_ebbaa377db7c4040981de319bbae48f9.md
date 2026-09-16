### Title
Uniswap V4 spot-price venue pricing accepts an unverified, manipulable instantaneous pool price with an optional-only guard - (File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts)

### Summary
The auto-roll bug in the external report describes a price-discovery mechanism that trusted an unverified single price point (`estimatedAutoRollUnitPrice`, derived from the last order/last block, without volume/reliability checks), letting an attacker move the published price with a small trade. The closest reachable analog in this codebase is Simplex's Uniswap V4 venue pricing path: `getExoticTokenPrice` → `computeDirectPoolPriceUsd` reads the pool's raw instantaneous `sqrtPriceX96` (spot price, not a TWAP or reliability-checked aggregate) and uses it directly as the USD price basis for sizing and filling cross-chain intents.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` selects the position with the largest pool liquidity and returns `computeDirectPoolPriceUsd(pos, sdkPool, chain)`, which derives price straight from `sdkPool.token0Price`/`token1Price` — themselves computed from the pool's current `sqrtPriceX96` read via `getSlot0` in `UniswapV4LiquidityState.refresh` [1](#0-0) . `computeDirectPoolPriceUsd` returns this raw pool mid with no size/impact term and no fee-tier adjustment [2](#0-1) . Docs explicitly confirm: "computeDirectPoolPriceUsd returns the raw pool mid derived from sqrtPriceX96 ... there is no size or impact term ... checkPriceGuard is the only defense on this path, and it checks deviation from a static reference, not execution cost." [3](#0-2) 

Critically, the only defense — `referencePrice` + `maxDeviationBps` — is optional and unguarded by default: "The two fields must be set together; omit both to leave the chain unguarded." [4](#0-3)  This is structurally identical to the reported bug class: a single unverified price sample (here, one block's spot tick instead of a volume-weighted/reliability-checked block price) is used as the pricing basis for the next action (fill/sizing), and it can be pushed by a manipulative trade in a thin pool, exactly as "a small order of a few wei can set the next auto-rolling price" in the original report.

### Impact Explanation
An attacker can manipulate a thin or low-liquidity Uniswap V4 pool's spot tick (e.g., via a large swap or flash-loan-funded swap in the same or a preceding block) immediately before submitting/triggering an intent fill priced off that pool. Because `computeDirectPoolPriceUsd` reads only the current `sqrtPriceX96` with no TWAP and no mandatory deviation guard, the solver (Simplex filler) will size and fill an order at the manipulated price, causing the solver to either overpay in the exotic token or underdeliver — a direct value-extraction/fund-loss vector against the solver's liquidity, reachable by any unprivileged user submitting an order/intent against a venue-priced pair.

### Likelihood Explanation
Likelihood is Medium: the attack requires operators to configure a venue-priced pair (curveless pair backed by a Uniswap V4 position) without setting `referencePrice`/`maxDeviationBps`, or with a wide tolerance, and requires a pool thin enough to move materially in one/few transactions. Given the guard is explicitly optional ("omit both to leave the chain unguarded") and documented as the sole defense, misconfiguration or thin-liquidity pools are a realistic, low-cost operational state, not a contrived edge case.

### Recommendation
Require `referencePrice`/`maxDeviationBps` (or an internal TWAP-based check) for every Uniswap V4 venue-priced pair rather than making it optional; additionally derive the price from a time-weighted average (multiple blocks) rather than the instantaneous `sqrtPriceX96`, analogous to the original fix's move from "last order price" to a verified, reliability-checked block price.

### Proof of Concept
1. Operator configures `[vault.uniswapV4]` for a pair without `referencePrice`/`maxDeviationBps` (permitted per docs).
2. Attacker executes a swap against the underlying Uniswap V4 pool to move `sqrtPriceX96` favorably (e.g., inflating the exotic token's USD price).
3. Attacker (or accomplice) immediately submits a cross-chain intent order against this pair; `resolveLegRates` → `referenceRate`/`getExoticTokenPrice` reads the manipulated spot price with no guard rejecting it [5](#0-4) .
4. Solver fills at the manipulated rate, transferring value to the attacker at the solver's expense.

Note: I could not fully verify from the index whether `checkPriceGuard` is invoked unconditionally on every venue-priced fill path (only `referenceRate`'s call site was directly confirmed within the tool budget); a Devin session with full repo access would be needed to confirm all call sites of `computeDirectPoolPriceUsd`/`checkPriceGuard` in `fx.ts` and rule out additional protections.

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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L70-72)
```text
Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
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
