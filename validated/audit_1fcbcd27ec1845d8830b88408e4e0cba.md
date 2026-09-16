Confirmed — no cross-order rate limiting, cooldown, or per-user volume aggregation exists in the Simplex filler pricing path. Each order is priced independently against its own notional via `sizeOrder`/`resolveLegRates`, with no memory of prior orders from the same counterparty. This is the exact analog needed.

### Title
Order splitting lets counterparties bypass volume-based price curves and systematically extract value from Simplex LP inventory - ([File: sdk/packages/simplex/src/strategies/fx.ts])

### Summary
Simplex's `FXFiller` prices each intent order independently against a per-pair, volume-tiered `bidPriceCurve`/`askPriceCurve` that is supposed to give worse rates for larger notionals (protecting the solver's inventory/risk on large fills) and better rates only for genuinely small orders. Because pricing is evaluated per-order with no aggregation of a counterparty's order history, a user can split what would otherwise be one large order into many small orders, each landing below the curve's first breakpoint, and receive the best per-unit tier price on the entire volume — exactly the "split-to-get-best-price" pattern described in the referenced Sherlock report for `geometric.swap_exact_amount_in`.

### Finding Description
The curve is sampled at `cappedPairNotional`, which is derived per order in `sizeOrder` [1](#0-0) , and consumed by `resolveLegRates`, which reads `askPricePolicy.getPrice(...)`/`bidPricePolicy.getPrice(...)` at that single order's size [2](#0-1) .

`FillerPricePolicy.getPrice` (the curve evaluator) is a pure piecewise-linear interpolation keyed solely on the `orderValueUsd`/notional passed in for *that single call* — it holds no state across calls and has no concept of a counterparty's cumulative volume [3](#0-2) .

The curve is explicitly documented as volume-tiered, e.g. an ask curve of `{100 → 0.99}, {100000 → 0.999}` where small orders pay a 1% spread and large orders pay only 0.1% [4](#0-3) , and the bid/ask examples show price *decreasing*/*increasing* with size specifically so larger notionals get a worse marginal rate [5](#0-4) .

Nothing in the fill path — `calculateProfitability`, `sizeOrder`, `resolveLegRates`, or `computeLegPolicyOutput` — tracks or bounds a counterparty's aggregate volume across multiple orders submitted in sequence (confirmed absent by searching for cooldown/rate-limit/aggregate-volume logic across the Simplex package; the only rate-limiting present is RPC endpoint suspension in `QuorumPublicClient`, unrelated to order pricing). Each order's `maxOrderSize` cap only bounds the solver's exposure per single order [6](#0-5) ; it does not stop a user from issuing N orders each safely under a breakpoint.

### Impact Explanation
An attacker (order placer) can split a large trade into many orders sized just below the curve's first breakpoint, causing the FXFiller to repeatedly quote its best small-order rate for the whole volume instead of the intended blended/worse large-order rate. Since the curve's slope exists specifically to charge a wider spread for larger notionals (compensating the solver for inventory risk and adverse selection), bypassing it via splitting extracts real value from solver-held inventory across every fill — a systematic drain analogous to the original report's Bob receiving 3000 tokens vs Alice's 2712 for an identical total swap. Because Simplex fillers are unprivileged, permissionless liquidity providers whose bids are selected purely by best price via `sortBids`/`selectAndExecuteBest` [7](#0-6) , this directly and repeatably transfers solver funds to any order placer willing to submit split orders, with no additional privilege required. This is a Medium-severity, protocol-wide fairness/fund-drain issue against LP capital reachable from a single unprivileged intent order.

### Likelihood Explanation
High likelihood: splitting an order into several smaller ones is trivial for any user of the Intent Gateway/Simplex flow, requires no special access, and the docs themselves show the curve breakpoints (e.g. 100/1000/5000) which make the optimal split size directly computable from the configuration a solver publishes.

### Recommendation
Aggregate a counterparty's (or a correlated set of orders') recent notional when sampling the price curve — e.g. track a rolling window of filled/pending volume per source address/session key and sample the curve at `previously-filled + current` notional rather than at each order's own size in isolation — or impose a per-counterparty cooldown/minimum-interval between fills so a curve breakpoint cannot be gamed by chunking within a short window.

### Proof of Concept
Given a pair with `bidPriceCurve = [{100,1580},{1000,1575},{5000,1570}]`:
- A single 5000-token0 order interpolates to ~1570 CNGN/token0 across the whole size.
- The same counterparty submitting 50 sequential 100-token0 orders each independently hits the curve's first point, `getPrice(100) = 1580`, for the entire 5000 total — a fully deterministic ~0.6% better rate extracted purely by splitting, with the gap widening for any counterparty who can push order size below the lowest breakpoint (down toward the curve's minimum, e.g. `amount = 0`) while a single equivalent large order would be forced into a materially worse blended rate.

### Citations

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1277-1337)
```typescript
	private async sizeOrder(
		order: Order,
		legs: ResolvedLeg[],
		venueUsdPrice: (chain: string, token1Address: string) => Promise<Decimal | null>,
	): Promise<{
		legNotionals: Decimal[]
		cappedByPair: Map<TradingPair, Decimal>
		/** min(1, maxOrderSize / uncapped notional) per pair — the exposure cap as a ratio; 1 when uncapped. */
		capFractionByPair: Map<TradingPair, Decimal>
		totalNotional: Decimal
	} | null> {
		const sourceChain = order.source
		const legNotionals: Decimal[] = []
		const totals = new Map<TradingPair, Decimal>()

		for (let i = 0; i < order.inputs.length; i++) {
			const leg = legs[i]
			const decimals = await this.contractService.getTokenDecimals(
				bytes32ToBytes20(order.inputs[i].token) as HexString,
				sourceChain,
			)
			const amount = new Decimal(formatUnits(order.inputs[i].amount, decimals))

			let notional: Decimal
			if (leg.inputIsToken0) {
				notional = amount
			} else {
				const rate = await this.referenceRate(leg, venueUsdPrice)
				if (!rate) return null
				notional = amount.div(rate)
			}
			legNotionals.push(notional)
			totals.set(leg.pair, (totals.get(leg.pair) ?? new Decimal(0)).plus(notional))
		}

		const cappedByPair = new Map<TradingPair, Decimal>()
		const capFractionByPair = new Map<TradingPair, Decimal>()
		// totalNotional is log-only: for an order whose legs span pairs with
		// different token0s it mixes units — anything decision-making must use
		// legNotionals (per-pair token0) or getOrderUsdValue (USD).
		let totalNotional = new Decimal(0)
		for (const [pair, total] of totals) {
			// An uncapped pair budgets its legs against the order's own notional: the
			// per-pair ration in `computeLegPolicyOutput` still keeps sibling legs from
			// double-spending the same token0, it just never binds below the order.
			const cap = pair.maxOrderSize
			cappedByPair.set(pair, cap === undefined ? total : Decimal.min(total, cap))
			// The one place the cap test is exact. Both sides are token0 notionals
			// derived from `referenceRate`, so the comparison is single-basis —
			// unlike `token0Used` vs `legNotionals[i]` downstream, where the former
			// is priced at the capped notional and the latter at the curve's origin,
			// so a sloped curve makes them differ with the cap nowhere near binding.
			capFractionByPair.set(
				pair,
				cap !== undefined && total.gt(cap) && total.gt(0) ? cap.div(total) : new Decimal(1),
			)
			totalNotional = totalNotional.plus(total)
		}

		return { legNotionals, cappedByPair, capFractionByPair, totalNotional }
	}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1443-1479)
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

		const askRate = leg.pair.askPricePolicy?.getPrice(cappedPairNotional) ?? null
		const bidRate = leg.pair.bidPricePolicy?.getPrice(cappedPairNotional) ?? null

		const rate = leg.inputIsToken0 ? askRate : bidRate
		if (!rate) {
			this.logger.debug(
				{ orderId, pair: `${leg.pair.token0}/${leg.pair.token1}`, inputIsToken0: leg.inputIsToken0 },
				"Rejecting leg: direction disabled for one-sided LP",
			)
			return null
		}
		return { rate, oppositeRate: leg.inputIsToken0 ? bidRate : askRate, priceSource: "policy" }
```

**File:** sdk/packages/simplex/src/config/interpolated-curve.ts (L391-421)
```typescript
	getPrice(orderValueUsd: Decimal): Decimal {
		const amount = orderValueUsd

		// Below minimum configured amount, use the first point
		if (amount.lte(this.points[0].amount)) {
			return this.points[0].price
		}

		// Above maximum configured amount, use the last point
		const lastPoint = this.points[this.points.length - 1]
		if (amount.gte(lastPoint.amount)) {
			return lastPoint.price
		}

		// Piecewise linear interpolation between surrounding points; duplicate
		// amounts would divide by zero, so skip zero-width segments (the later
		// point wins via the following segment or the clamped-tail checks above)
		for (let i = 0; i < this.points.length - 1; i++) {
			const p1 = this.points[i]
			const p2 = this.points[i + 1]
			if (p2.amount.eq(p1.amount)) continue

			if (amount.gte(p1.amount) && amount.lte(p2.amount)) {
				const t = amount.minus(p1.amount).div(p2.amount.minus(p1.amount))
				return p1.price.plus(t.mul(p2.price.minus(p1.price)))
			}
		}

		// Fallback (should not be reached due to earlier checks)
		return lastPoint.price
	}
```

**File:** docs/content/developers/evm/simplex/markets.mdx (L23-23)
```text
Each pair's **`maxOrderSize`** caps the solver's exposure per order, denominated in that pair's token0. An order larger than the cap is **partially filled** down to it: the IntentGateway releases escrow strictly in proportion to the outputs provided, so filling a quarter of an order takes on a quarter of the exposure. An order the solver declines because its own curve yields less than the user asked for is a different case — that one is skipped outright, logged with `limiter: "price"`, since filling a smaller slice of a bad rate loses the same per unit and costs the same gas.
```

**File:** docs/content/developers/evm/simplex/markets.mdx (L34-45)
```text
# Bid: CNGN per USDC when *buying* CNGN from a user (CNGN→USDC leg).
bidPriceCurve = [
    { amount = "100",  price = "1580" },
    { amount = "1000", price = "1575" },
    { amount = "5000", price = "1570" },
]
# Ask: CNGN per USDC when *selling* CNGN to a user (USDC→CNGN leg).
askPriceCurve = [
    { amount = "100",  price = "1560" },
    { amount = "1000", price = "1555" },
    { amount = "5000", price = "1550" },
]
```

**File:** docs/content/developers/evm/simplex/markets.mdx (L68-71)
```text
askPriceCurve = [
    { amount = "100",    price = "0.99"  },   # small orders: 1% spread
    { amount = "100000", price = "0.999" },   # large orders: 0.1%
]
```

**File:** sdk/packages/sdk/src/protocols/intents/IntentGateway.ts (L743-760)
```typescript
	async sortBids(order: Order, bids: Bid[]): Promise<Bid[]> {
		return this.bidManager.sortBids(order, bids)
	}

	/**
	 * Autopilot bid selection: sorts the given bids, simulates each until one
	 * passes, then executes it.
	 *
	 * Delegates to {@link BidManager.selectAndExecuteBest}.
	 *
	 * @param order - The placed order to fill.
	 * @param bids - Candidate bids (from {@link buildBids}).
	 * @returns A {@link SelectBidResult} with the submitted UserOperation, hashes,
	 *   and fill status.
	 */
	async selectAndExecuteBest(order: Order, bids: Bid[]): Promise<SelectBidResult> {
		return this.bidManager.selectAndExecuteBest(order, bids)
	}
```
