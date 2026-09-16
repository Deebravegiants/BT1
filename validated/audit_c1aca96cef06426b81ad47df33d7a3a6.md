### Title
Fixed $1 stablecoin anchor lets a USDC/USDT depeg understate order USD value and shrink Simplex's reorg-protection confirmation depth - (File: sdk/packages/simplex/src/strategies/fx.ts)

### Summary
`FXFiller.usdFactors()` in `sdk/packages/simplex/src/strategies/fx.ts` pins `USD_STABLE_SYMBOLS` (USDC/USDT/DAI) at a hardcoded `Decimal(1)` regardless of the stablecoin's real market price, and this factor is used by `getOrderUsdValue()` to size the order's USD notional, which in turn drives the per-chain confirmation-depth curve (`DEFAULT_CONFIRMATION_POLICIES` / `[confirmationPolicies]`) that decides how many source-chain block confirmations a filler waits for before paying out on the destination chain. This mirrors the referenced JOJO bug class: treating a stablecoin's peg as ground truth instead of its true market value when the resulting number feeds into a security/risk decision. [1](#0-0) 

### Finding Description
`getOrderUsdValue()` converts each leg's token0 notional into USD via `usdFactors()`, explicitly documenting that "USD stables are pinned at $1 and never re-priced through a curve": [2](#0-1) [3](#0-2) 

This USD value is the `amount` axis fed to the confirmation-depth curves that gate how long a cross-chain fill waits before the solver commits capital on the destination chain, explicitly to protect against reorgs unwinding the source-chain deposit after payout: [4](#0-3) [5](#0-4) 

Notably, the codebase itself recognizes that an *understated* USD value shrinks reorg protection and is "the exact attack the guard exists to stop" — but this safeguard (`checkPriceGuard`) is only wired up for Uniswap-V4 venue-priced legs, not for the stablecoin $1 anchor itself: [6](#0-5) 

If USDC or USDT depegs upward (trading above $1, which has occurred historically during stress/liquidity events), a fixed nominal amount of stablecoin tokens is actually worth more in real USD terms than the pinned $1-per-token assumption computes. Because `getOrderUsdValue` uses the fixed anchor rather than the live price, it will *understate* the true USD value of a large stablecoin-denominated order. That understated value is then used to look up a lower point on the confirmation-depth curve, causing the filler to require fewer block confirmations than the order's real economic value warrants before it releases destination-chain funds.

### Impact Explanation
Insufficient confirmation depth is exactly the condition the confirmation-policy mechanism exists to prevent: an attacker can place a large source-chain order, wait for the filler to observe it and pay out on the destination chain after only the (miscalculated, too-shallow) confirmation depth, then reorg the source chain to un-include the order-placement transaction. The filler has already paid the destination-chain output with no on-chain safety net to reclaim it (per the documented threat model), so this directly enables theft of solver funds through a shortened reorg window. This is a fund-loss vector reachable from a permissionless, attacker-placed order, matching the required severity bar (Medium+, concrete freezing/theft of funds).

### Likelihood Explanation
Likelihood depends on (a) a stablecoin depeg event (USDC/USDT have depegged above and below $1 during real-world stress, e.g. the March 2023 USDC depeg) coinciding with (b) an attacker capable of executing a chain reorg of sufficient depth on the source chain within the fill window. Reorg capability varies by chain (more feasible on lower-finality chains/L2s the confirmation curves already treat as fast, e.g. Base/Unichain with only 2 blocks at low order sizes). The bug is a latent, systemic pricing-input flaw rather than something exploitable at will, so likelihood is best characterized as low-to-moderate but the resulting impact (loss of filler capital) is severe when the two conditions align.

### Recommendation
Do not pin stablecoin USD factors to a hardcoded `1`. Source live stablecoin prices (e.g., via the same Chainlink/Uniswap price helpers already used elsewhere in the SDK, or via the `referencePrice`/`maxDeviationBps` guard pattern already implemented for Uniswap V4 venue pricing) and apply the same `checkPriceGuard`-style deviation check to stablecoin anchors before using them to size confirmation depth. At minimum, clamp the confirmation-depth USD notional to use `max(nominal_tokens, live_price * nominal_tokens)` so a depeg can only ever *increase* required confirmations, never decrease them.

### Proof of Concept
1. USDT depegs upward to (hypothetically) $1.15 due to a liquidity/redemption event.
2. Attacker places a large cross-chain order with USDT input notionally valued by the filler at, say, $95,000 (just under the Base 90-block/$100k confirmation threshold) via the fixed $1 anchor, while its true USD value is ~$109,250 (which should trigger the higher confirmation tier).
3. `getOrderUsdValue()` returns the understated $95,000 figure; `DEFAULT_CONFIRMATION_POLICIES["8453"]` interpolates to a shallow confirmation depth appropriate for a sub-$100k order rather than the deeper depth its true value warrants.
4. The filler pays out on the destination chain after the shallow confirmation window.
5. The attacker reorgs the source chain to remove the order-placement transaction, and the filler's destination-chain payout cannot be recovered (per the documented "no on-chain safety net" threat model for cross-chain fills). [7](#0-6)

### Citations

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1353-1364)
```typescript
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

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1741-1774)
```typescript
	/**
	 * Returns the order's input basket in **USD** — each leg is sized to its
	 * pair's token0 notional via the pair's own reference rate (curve at
	 * minimum size, or the venue quote), converted to dollars through the
	 * curve-derived anchor factor for that token0, and summed across legs.
	 *
	 * The core filler feeds this to the per-chain confirmation curves, whose
	 * `amount` axis is USD — honest for non-USD pairs too, which is the whole
	 * point of the anchor graph. Returns `null` when a leg matches no pair or
	 * cannot be sized (genuine "can't price").
	 */
	async getOrderUsdValue(order: Order): Promise<{ inputUsd: Decimal } | null> {
		const legs = this.resolveOrderLegs(order)
		if (!legs) return null

		const sized = await this.sizeOrder(order, legs, this.venuePriceMemo())
		if (!sized) return null

		// Leg notionals are in each pair's own token0. Convert to USD through
		// the curve graph before summing — the confirmation curve's amount axis
		// is USD, and a raw token quantity would over-wait for sub-dollar
		// assets and, worse, under-wait for anything above a dollar.
		const factors = this.usdFactors()
		let inputUsd = new Decimal(0)
		for (let i = 0; i < legs.length; i++) {
			const factor = factors.get(normalizeSymbol(legs[i].pair.token0))
			// Unreachable after the constructor's anchor check; refuse to size
			// rather than mislabel a token quantity as dollars.
			if (!factor) return null
			inputUsd = inputUsd.plus(sized.legNotionals[i].mul(factor))
		}
		if (inputUsd.lte(0)) return null
		return { inputUsd }
	}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1776-1817)
```typescript
	/**
	 * USD per unit of every priceable symbol, derived from the operator's own
	 * curves: USD stables are $1 anchors and each curve-priced cross-asset
	 * pair's zero-notional mid is an FX edge (token1 per token0). Recomputed
	 * per call so live curve edits through the admin server take effect
	 * immediately; the graph is a handful of pairs, so this is trivial.
	 *
	 * When several pairs could price the same symbol, the **first anchoring
	 * pair in declaration order wins** and later edges are ignored — factors
	 * are never re-derived, which keeps the walk terminating and deterministic
	 * (no averaging across inconsistent routes, no divergence on curve cycles).
	 * USD stables are pinned at $1 and never re-priced through a curve, so a
	 * mis-set stable/stable curve cannot contaminate the anchors. Declare the
	 * pair you want as the reference first if an asset has multiple routes.
	 */
	private usdFactors(): Map<string, Decimal> {
		const factors = new Map<string, Decimal>()
		for (const symbol of USD_STABLE_SYMBOLS) factors.set(symbol, new Decimal(1))

		let grew = true
		while (grew) {
			grew = false
			for (const pair of this.pairs) {
				if (isSameTokenPair(pair)) continue
				const mid = pairMidRate(pair)
				if (!mid) continue
				const token0 = normalizeSymbol(pair.token0)
				const token1 = normalizeSymbol(pair.token1)
				const usd0 = factors.get(token0)
				const usd1 = factors.get(token1)
				if (usd0 && !usd1) {
					// 1 token0 = mid token1 ⇒ usd(token1) = usd(token0) / mid.
					factors.set(token1, usd0.div(mid))
					grew = true
				} else if (usd1 && !usd0) {
					factors.set(token0, usd1.mul(mid))
					grew = true
				}
			}
		}
		return factors
	}
```

**File:** docs/content/developers/evm/simplex/confirmations.mdx (L10-27)
```text
## Confirmation Policy

Before processing a cross-chain order, Simplex waits for enough block confirmations to guard against chain reorganizations. The number of confirmations scales with order value using a curve — small orders are processed quickly, large orders wait longer. Same-chain orders always proceed without additional confirmation delay.

### Built-in Defaults

Simplex ships with default confirmation policies for common chains. These apply automatically when no user-configured policy exists for a chain. User-configured policies override the default for that chain. Every configured chain must be covered by a built-in default or a custom entry — a chain with neither fails at startup rather than silently dropping that chain's cross-chain orders at fill time.

| Chain | Chain ID | Min ($1,000) | Max ($100,000) | Block Time |
|---|---|---|---|---|
| Ethereum | 1 | 2 blocks (~24s) | 15 blocks (~3m) | ~12s |
| BNB Chain | 56 | 2 blocks (~6s) | 3 blocks (~9s) | ~3s |
| Polygon | 137 | 2 blocks (~4s) | 5 blocks (~10s) | ~2s |
| Base | 8453 | 2 blocks (~4s) | 90 blocks (~3m) | ~2s |
| Arbitrum | 42161 | 8 blocks (~2s) | 720 blocks (~3m) | ~0.25s |
| Unichain | 130 | 2 blocks (~2s) | 180 blocks (~3m) | ~1s |

Values between the min and max order amounts are linearly interpolated.
```

**File:** docs/content/developers/evm/simplex/confirmations.mdx (L76-79)
```text
### Why this matters for cross-chain orders

On a cross-chain fill, Simplex observes an `OrderPlaced` (or `PartialFill` / `OrderFilled`) event on the source chain and then commits capital on the destination chain. Unlike same-chain fills — where the destination `fillOrder` call will revert if the source-chain order does not exist — cross-chain bids submitted through Hyperbridge are evaluated from the solver's own reading of source-chain state. A single RPC is therefore both an availability and an integrity choke point: if it lies about which orders were placed, the solver can be induced to pay out against events that never happened, and there is no on-chain safety net to catch it after the fact.

```

**File:** sdk/packages/simplex/src/config/interpolated-curve.ts (L20-26)
```typescript
/**
 * Built-in per-chain confirmation curves for the supported mainnets, merged
 * under any user-supplied `[confirmationPolicies]` entries at startup. The
 * curve amount axis is the order's USD value (derived from the pair curves
 * via the USD anchors); the value is the confirmation depth in blocks.
 */
export const DEFAULT_CONFIRMATION_POLICIES: Record<string, CurveConfig> = {
```
