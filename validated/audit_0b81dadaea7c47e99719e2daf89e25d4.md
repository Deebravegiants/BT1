## Title
Simplex FXFiller trusts an instantaneous, unbounded Uniswap V4 spot price for venue-priced fills, with no manipulation-resistant (TWAP) source and an optional, statically-pinned deviation guard - (File: `sdk/packages/simplex/src/strategies/fx.ts`)

### Summary
The external report describes borrowing against a stale TWAP/reserve price during a swETH depeg because neither oracle updates instantly on a step-function price move. The analogous class in this codebase is price-source freshness/manipulation-resistance for a value that gates fund transfers. In Hyperbridge's Simplex intent solver, `FXFiller` prices "venue" pairs directly from a Uniswap V4 pool's current tick/`sqrtPriceX96` (a single-block spot read), and the only defense is an **optional** `checkPriceGuard` that compares the quote to a static, operator-set `referencePrice` band — not a TWAP, not a liquidity-depth check, and not required to be configured at all.

### Finding Description
`UniswapV4FundingPlanner.getExoticTokenPrice` reads the *current* on-chain pool state (`getSlot0` → `sqrtPriceX96`/tick) via `UniswapV4LiquidityState.refresh()` and derives a spot mid-price with `computeDirectPoolPriceUsd`, picking the highest-liquidity qualifying pool [1](#0-0) . This spot price is fed straight into `FXFiller.resolveLegRates`/`referenceRate`, which price and size an order leg for curveless ("venue-priced") pairs [2](#0-1) [3](#0-2) .

The only safeguard is `checkPriceGuard`, which rejects a quote only if it deviates from a **static** `referencePrice` by more than `maxDeviationBps` [4](#0-3) . Per the code's own documentation, this guard is entirely optional (`referencePrice`/`maxDeviationBps` must be set together, "omit both to leave the chain unguarded") [5](#0-4) , and even when configured it checks *deviation from a fixed number*, not staleness or manipulation: "`checkPriceGuard` is the only defense on this path, and it checks deviation from a static reference, not execution cost" [6](#0-5) . There is no TWAP oracle, no secondary price feed, and no minimum-liquidity/impact check comparable to `SpotOracle`'s `min(TWAP, ReserveOracle)` pattern from the report.

This mirrors the report's root cause precisely: a price used to authorize value transfer is read as an instantaneous on-chain value (here, pool spot tick) with only a coarse, static, optional band as protection — no mechanism that is inherently resistant to a single-transaction price shock (flash-loan pool manipulation) or to a real, fast-moving depeg of the exotic/FX token (e.g., cNGN), since the "reference" itself is a stale, human-configured constant that an operator must remember to update.

### Impact Explanation
An attacker who can move a configured Uniswap V4 pool's spot price within one transaction (e.g., via a flash swap in a thin/whitelisted pool, or simply timing a real market move faster than the operator updates `referencePrice`) can submit a cross-chain/same-chain intent order that the Simplex solver fills using this manipulated/stale spot price. Because the guard is optional and, when present, only bounds deviation from a static constant rather than requiring freshness or minimum liquidity, the solver can be induced to deliver output tokens worth materially more than the input it receives, draining the solver's funded vault/inventory (a concrete theft of solver funds triggered by a single submitted order). Since `side`/pricing here has no bid/ask spread ("a venue-priced pair has no bid/ask spread of its own, so its margin comes from `order.fees` alone" per the docs) [7](#0-6) , there is no cushion beyond fees to absorb a bad quote.

### Likelihood Explanation
Medium-High. The price guard is opt-in and documented as optional, so any deployment that omits it (or sets a stale `referencePrice`) is exposed on every fill. Even with the guard configured, it is a static band with no update mechanism tied to real market conditions, so it either (a) stays wide enough to be useless against a genuine, fast depeg, or (b) requires continuous manual operator maintenance to stay tight — both realistic operational failure modes. The attack is reachable by any unprivileged intent placer submitting a single order; no privileged role is required.

### Recommendation
Replace or augment the raw `getSlot0` spot read with a manipulation-resistant price (e.g., a short Uniswap V4 TWAP/oracle observation, or a Chainlink feed as already used elsewhere in `SimplexPaymaster`'s `_getOraclePrice` with its `StaleOraclePrice`/`maxOracleAge` checks) [8](#0-7) . Make the deviation guard mandatory (not optional) for venue-priced pairs, add a minimum pool-liquidity/impact requirement, and consider bounding the quote against a periodically-refreshed reference rather than a hand-set static constant, or auto-halting (as `recordOrderOutcome`/`isHalted` already do for overfill clamps) on repeated large deviations rather than relying solely on a single-shot check.

### Proof of Concept
1. Configure/observe a `[vault.uniswapV4]` position for an exotic/FX pair (e.g., USDC/cNGN) with no `referencePrice`/`maxDeviationBps` guard set (a supported, documented configuration) [9](#0-8) .
2. Attacker performs a large swap against the configured Uniswap V4 pool in the same block (or during a fast real depeg) to move `sqrtPriceX96`/tick sharply in their favor.
3. Attacker immediately submits an intent order whose leg is priced via `resolveLegRates` → `venueUsdPrice` → `UniswapV4FundingPlanner.getExoticTokenPrice`, which reads the now-skewed spot price with no TWAP smoothing [10](#0-9) .
4. `checkPriceGuard` either does not exist (unguarded chain) or, if present, is bypassed because the static reference was not updated to reflect the new legitimate price — the solver fills the order at the skewed rate, transferring output tokens worth more than the input received, draining solver inventory.

I was not able to fully inspect `computeDirectPoolPriceUsd`'s exact math or confirm whether any additional block-level sanity check exists beyond what's cited (the tool budget was exhausted before reading that function body directly); this should be verified in a follow-up review of `UniswapV4FundingPlanner.ts` if further precision is needed.

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

**File:** sdk/packages/simplex/docs/ai/flows/venue-pricing-uniswap-v4-funded-pairs.md (L17-22)
```markdown
`computeDirectPoolPriceUsd` returns the **raw pool mid** derived from `sqrtPriceX96`. The pool's
fee tier is read and stored on the hydrated position (`pos.fee`) but never applied to the price,
and there is no size or impact term — `computeLegPolicyOutput` extends the mid linearly across the
whole priced quantity. `checkPriceGuard` is the only defense on this path, and it checks deviation
from a static reference, not execution cost. A venue-priced pair that has to swap through its own
pool to source inventory pays a fee tier it never quoted against.
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L42-42)
```text
When **`[vault.uniswapV4]`** lists at least one position, cross-asset pairs without curves derive bid/ask prices from **Uniswap V4 pool state** (current tick). The pool acts as the price oracle instead of a static curve. Note this yields a **single** price used in both directions — a venue-priced pair has no bid/ask spread of its own, so its margin comes from `order.fees` alone.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L660-676)
```text
    /// @dev Fetch a Chainlink price normalized to 8 decimals.
    ///      Reverts on stale or non-positive answers.
    function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) {
            revert StaleOraclePrice(address(oracle), updatedAt);
        }

        if (oracleDecimals < 8) {
            return uint256(answer) * (10 ** (8 - oracleDecimals));
        } else if (oracleDecimals > 8) {
            return uint256(answer) / (10 ** (oracleDecimals - 8));
        }
        return uint256(answer);
    }
```
