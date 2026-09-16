### Title
Uniswap V4 spot-price venue oracle in Simplex `FXFiller` is vulnerable to same-block price manipulation (flash-loan analog) - ([File: sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts])

### Summary
The `MUMUG` exploit succeeded because a bank contract priced a bond off a single AMM pair's spot reserves, which an attacker skewed in the same transaction via a flash-swap before consuming the mispriced quote. The Simplex intent-solver (`FXFiller`) has an analogous pattern: `UniswapV4FundingPlanner.getExoticTokenPrice` / `computeDirectPoolPriceUsd` reads the *current* `sqrtPriceX96` tick of a configured Uniswap V4 pool as the venue price with no TWAP, and that spot price directly drives how much output the filler pays out to fill an order.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` (`sdk/packages/simplex/src/funding/uniswapV4/UniswapV4FundingPlanner.ts:206-240`) iterates the solver's configured V4 positions, picks the most-liquid pool for the exotic token, and calls `computeDirectPoolPriceUsd`, which returns the pool's raw `token0Price`/`token1Price` derived from spot `sqrtPriceX96` (lines 246-275). This is a pure spot read of the pool's current tick — no TWAP oracle, no minimum liquidity depth check beyond "largest liquidity among configured positions."

That spot price feeds `resolveLegRates` in `sdk/packages/simplex/src/strategies/fx.ts:1443-1479`, which for a curveless USD-stable pair uses `venueUsdPrice` (this planner) directly as the fill rate, gated only by `checkPriceGuard` — an *optional*, static-reference band check (`referencePrice` ± `maxDeviationBps`) that a solver may leave unconfigured (`docs/content/developers/evm/simplex/pricing.mdx:70-84`, config in `sdk/packages/simplex/src/config/filler-toml.ts:23-36`). Even when configured, the guard only rejects prices *outside* a static band; it does not detect that the *current* pool tick has been pushed away from its pre-manipulation value by a large swap within the manipulation-capable range, nor does it use any TWAP.

Critically, the sizing path in `fx.ts:678-701` explicitly disables the overfill clamp that used to bound exposure to exactly this class of bug:
```
// Overfill detection is warn-only: the clamp is DISABLED, so the filler
// fills the full computed amount even when it exceeds
// (1 + maxOverfillBps) × user-requested — including venue-priced legs
// (e.g. Uniswap V4). NOTE: this removes the per-leg loss bound that
// previously protected against a bug / stale cache / manipulated venue
// price. Output is no longer capped; we only emit a warning.
```
This comment in the code itself acknowledges the exact bug class from the report: a manipulated venue price is no longer bounded by the overfill ceiling — the filler will "fill the full computed amount" at whatever spot price the pool reports.

An unprivileged order placer (the intent-side counterpart of the flash-loan attacker in the MU&MUG report) can, in the same block/transaction bundle:
1. Execute a large swap against the exact Uniswap V4 pool the solver's `[vault.uniswapV4]` position is configured against (pool addresses/tokenIds are public config, and `getExoticTokenPrice` always selects the highest-liquidity qualifying pool, so the target is deterministic).
2. Push the spot tick so `computeDirectPoolPriceUsd` overstates the exotic token's USD value.
3. Place (or have already placed) an order that the solver's `FXFiller` fills using that inflated venue rate, withdrawing liquidity from the solver's real position (`planWithdrawalForToken`) and handing out output tokens priced at the manipulated rate.
4. Reverse the pool-skewing swap, leaving the solver's LP position devalued relative to what it paid out, and the attacker having received an overpriced payout backed by the solver's real funds.

### Impact Explanation
This is a direct, unbacked-value extraction against solver capital that funds Hyperbridge intent fills — an intent solver's on-chain Uniswap V4 inventory can be drained relative to fair value by manipulating a single spot price read with no TWAP, no manipulation-resistance, and (per the code's own comment) no clamp bounding the resulting overpay. Because `IntrinsicIntents.fillOrder` executes the fill atomically against escrow, a solver operating with venue-priced pairs and no `referencePrice` guard (an explicitly supported, "unguarded" configuration per `docs/content/developers/evm/simplex/pricing.mdx:72`) has no defense at all; even with a guard configured, the check only bounds against a static reference, not against the specific single-block manipulation pattern.

### Likelihood Explanation
Uniswap V4 position `tokenId`s and pool keys used for venue pricing are read from on-chain config at startup and are publicly observable on-chain, so an attacker can target the exact pool. Executing a large swap to move tick and back is a standard flash-swap/atomic-manipulation primitive (as demonstrated by the referenced MUMUG exploit) and requires no privileged access — only capital for the temporary swap, recoverable via reversal. The `maxOverfillBps` clamp being explicitly disabled (a recent, intentional code change per the inline comment) directly removes what the codebase itself identifies as the mitigating control for this exact scenario, and the price guard is optional and reference-static rather than manipulation-aware.

### Recommendation
- Derive venue prices from a manipulation-resistant source (TWAP over a window, or Uniswap V4's own oracle hook if available) instead of instantaneous `sqrtPriceX96`.
- Re-enable and enforce the overfill/loss-bound clamp for venue-priced legs specifically, since the code comment confirms this was previously the intended defense against "a manipulated venue price."
- Make `referencePrice`/`maxDeviationBps` guard mandatory (not optional) for any pair relying on Uniswap V4 spot pricing, and consider deriving the reference dynamically (e.g., recent historical average) rather than a static operator-supplied value.
- Add minimum-liquidity-depth and same-block reorg/manipulation checks (e.g., compare price across multiple recent blocks) before trusting a pool quote for a fill of significant size.

### Proof of Concept
Conceptual, following the MU&MUG pattern, mapped onto the Simplex filler:
1. Attacker identifies the Uniswap V4 pool/tokenId configured under a target solver's `[vault.uniswapV4]` (public TOML/config, and the planner always prefers the highest-liquidity qualifying pool for a given exotic token — `UniswapV4FundingPlanner.getExoticTokenPrice`, lines 221-234).
2. Attacker performs a large swap in that pool to move `sqrtPriceX96` such that `computeDirectPoolPriceUsd`'s `token0Price`/`token1Price` overstates the exotic token's USD value.
3. Attacker (or colluding party) places/wins an intent order on the exotic/USD pair; `FXFiller.resolveLegRates` → `venueUsdPrice` reads the manipulated spot price (fx.ts:1453-1465), and — because `maxOverfillBps` clamping is disabled (fx.ts:678-701) and no `referencePrice` guard is configured — the filler withdraws liquidity via `planWithdrawalForToken` and pays out at the inflated rate.
4. Attacker reverses the initial swap, extracting the difference between the manipulated fill price and the pool's true price, funded by the solver's withdrawn LP position. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1443-1465)
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
