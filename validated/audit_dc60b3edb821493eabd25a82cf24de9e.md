### Title
Uniswap V4 spot-price venue pricing lets a flash-loan attacker manipulate the exotic-token rate an order fills at - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
When a Simplex trading pair has no static bid/ask curve, its price for the "exotic" leg is read directly from a Uniswap V4 pool's current `sqrtPriceX96` (a single-block spot read), and the only safeguard is an optional, statically-configured `referencePrice`/`maxDeviationBps` guard that operators can simply omit. This mirrors the ATK incident bug class: a strategy/pricing component trusting a manipulable, thin-liquidity spot price that an attacker can move with a flash loan inside one transaction to extract value.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` / `computeDirectPoolPriceUsd` derive the USD price of the exotic token straight from the pool's live `sqrtPriceX96` via `sdkPool.token0Price`/`token1Price`, with no TWAP, no size/impact term, and no fee-tier adjustment: [1](#0-0) 

The venue-pricing flow doc confirms this is the raw pool mid with only one defense layer: [2](#0-1) 

That defense — a static `referencePrice` + `maxDeviationBps` guard — is explicitly optional and, if omitted, leaves the chain "unguarded": [3](#0-2) 

A same-block, single-transaction spot-price read from a concentrated-liquidity pool is exactly the class of on-chain price oracle the ATK attacker exploited via flash loan against ATK's strategy contract: borrow a large amount, swap through the thin pool to push its spot price to an extreme, have the victim logic price/value tokens off that manipulated spot price within the same transaction, extract the mispriced value, then repay the flash loan in the same transaction. Here, the "strategy contract" analog is the FXFiller/UniswapV4FundingPlanner pricing path: `getExoticTokenPrice` is called during order evaluation (`resolveLegRates`/`venuePriceMemo`) to price and fund a fill from the LP position, and `refresh()` re-reads `getSlot0`/`getLiquidity` immediately before planning — always the current, manipulable, on-chain state, not a delayed or averaged one: [4](#0-3) [5](#0-4) 

The order path is reachable by any unprivileged user: they place an intent order on `IntentGatewayV2`/`IntentGatewayV3` with the venue-priced pair (e.g., USDC → CNGN), and the filler's `FXFiller` evaluates and prices the leg from the live pool state before funding/filling via ERC-7821 batched calls, atomically in the same transaction as the LP withdrawal: [6](#0-5) 

### Impact Explanation
If an operator configures a Uniswap V4-priced pair without setting `referencePrice`/`maxDeviationBps` (permitted by the config validator, which only requires the two fields to be set *together*, not that they be set at all): [7](#0-6) 

an attacker can flash-loan-manipulate the venue pool's spot tick immediately before/within the same block as submitting an order, causing the filler to price the exotic-token leg far off its true market value and fund/deliver output tokens from its Uniswap V4 LP position at the manipulated rate. This produces a direct loss of solver/LP funds (the filler either over-delivers the exotic token or under-collects on a reciprocal leg), the same fund-drain mechanism as the ATK flash-loan attack on its strategy contract. This satisfies "concrete theft ... of funds" via a reachable single order from an unprivileged user.

### Likelihood Explanation
Likelihood is Medium: it requires (1) an operator configuring a Uniswap V4-priced pair, (2) omitting the optional price guard (or choosing a wide `maxDeviationBps`), and (3) the underlying pool having thin enough liquidity to be moved profitably with a flash loan within `maxDeviationBps` tolerance (if a guard is set) or unboundedly (if not). Given the guard is opt-in and documented as leaving the chain "unguarded" when omitted, misconfiguration is plausible in production deployments prioritizing simplicity, especially for lower-liquidity "exotic" tokens like the cNGN example used throughout the docs/tests.

### Recommendation
- Make the price guard (`referencePrice`/`maxDeviationBps`) mandatory for all Uniswap V4-priced pairs rather than optional, or default to a conservative built-in deviation cap.
- Replace or supplement the spot `sqrtPriceX96` read with a TWAP (time-weighted average price) over multiple blocks, which cannot be moved with a single-block flash loan.
- Apply a size/impact-aware pricing model (accounting for pool fee tier and the actual amount being withdrawn) instead of extending the spot mid linearly, as already flagged as a known gap in `venue-pricing-uniswap-v4-funded-pairs.md`.
- Add a minimum-liquidity threshold below which venue pricing is refused, independent of the deviation guard.

### Proof of Concept
1. Operator configures `[vault.uniswapV4]` with a position for a low-liquidity USDC/EXOTIC pool and does **not** set `referencePrice`/`maxDeviationBps` (permitted per `validateConfig`).
2. Attacker takes a flash loan, swaps a large amount through the USDC/EXOTIC V4 pool to push `sqrtPriceX96` to an extreme (e.g., making EXOTIC appear far cheaper in USD than its true value).
3. In the same transaction/block, attacker (or a colluding solver bid, or via the intent flow that triggers filler evaluation) causes `FXFiller`/`UniswapV4FundingPlanner.getExoticTokenPrice` to read the manipulated `slot0`/`sqrtPriceX96` via `computeDirectPoolPriceUsd`, pricing the leg far off-market.
4. The filler funds and fills the order using `planWithdrawalForToken`, withdrawing/crediting EXOTIC tokens from its LP position at the manipulated rate — over-delivering value to the attacker.
5. Attacker reverses the pool-price manipulation and repays the flash loan within the same transaction, keeping the mispriced profit — mirroring the ATK flash-loan attack pattern on a strategy contract's price-dependent logic.

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

**File:** docs/content/developers/evm/simplex/pricing.mdx (L16-18)
```text
When the solver's wallet balance on the destination chain is insufficient to fill an order, Simplex can automatically withdraw liquidity from on-chain positions to cover the deficit. Withdrawal calls are prepended to the UserOperation as ERC-7821 batch calls, making the funding atomic with the fill.

Configured under the top-level `[vault.uniswapV4]` block. Decreases liquidity from concentrated Uniswap V4 positions via PositionManager NFTs. Slippage tolerance is set by `spreadBps` (default 50 bps / 0.50%), deadline defaults to the order's deadline. Each position needs a `chain` and a `tokenId` (the ERC-721 position NFT ID); pool details are read on-chain at startup.
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

**File:** sdk/packages/simplex/src/config/filler-toml.ts (L413-424)
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
```
