### Title
Solver bid ranking relies on single-block, unguarded on-chain DEX spot quotes, letting a solver front-run its own bid to win the auction with less real value than competing bids - (File: `sdk/packages/sdk/src/protocols/intents/BidManager.ts`)

### Summary
`BidManager` prices mixed-output solver bids for the IntentGateway V2 auction by calling live Uniswap spot quoters (`findBestProtocolWithAmountIn`) once, in the same call, with no TWAP, no second oracle, and no deviation guard. This is the exact bug class from the external report: an on-chain, single-sample spot price feeding a value comparison that gates which party's funds get moved, manipulable by a front-run in the same block.

### Finding Description
`sortMixedOutputs` (used whenever an order's required output basket contains a non-stable token) ranks competing solver bids by `computeOutputsUsdValue`, which for every non-stable token calls `quoteTokenToUsdc`: [1](#0-0) 

`quoteTokenToUsdc` obtains the USD value purely from `this.ctx.swap.findBestProtocolWithAmountIn`, a single live on-chain DEX quote (direct pair, or via WETH fallback), with no fallback oracle, no time-weighted average, and no sanity/deviation check: [2](#0-1) 

`sortMixedOutputs` then compares each bid's `bidUsd` against the order's `requiredUsd` computed the same way, and sorts bids purely by this manipulable value, picking the top bid for `selectAndExecuteBest` to simulate and execute: [3](#0-2) [4](#0-3) 

Elsewhere in the same codebase (Simplex's `FXFiller`), the project already recognizes this exact risk for venue-priced pairs and mitigates it with an explicit `checkPriceGuard`/`maxDeviationBps` reference check before trusting a live pool quote: [5](#0-4) 

No equivalent guard exists on the `BidManager` valuation path used for auction bid selection — it is the unmitigated analog of the `calc_withdraw_one_coin` spot-price issue: an unprivileged actor (any solver bidding on the order, or anyone able to trade against the relevant pool right before the selector runs) can manipulate the pool's spot price in the same block/transaction window to make its own bid appear to carry more USD value than it truly does, or to make a competitor's bid appear worthless (quoter throwing/returning near-zero on a moved pool), thereby winning selection.

### Impact Explanation
While `IntentGatewayV2.fillOrder` enforces that a solver deliver at least the exact per-token amounts declared in its `FillOptions.outputs` (the base requirement cannot be spoofed on-chain), the auction/bid-selection layer that decides which solver captures the order — and how any output-basket surplus/value comparison is made across a mixed-token basket — is entirely driven by this manipulable off-chain-computed, on-chain-sourced spot price. A solver can pay a small amount to skew a thin pool immediately before `sortBids`/`sortMixedOutputs` runs, causing:
- A genuinely worse bid (lower true USD value, e.g., more of a token it just inflated) to rank above a genuinely better bid, diverting fill economics (surplus, exchange rate on the mixed basket) away from the order's beneficiary and toward the manipulating solver.
- A competing, honestly-priced bid to be rejected (`REJECTED: unable to price mixed outputs`) if the manipulation causes the quoter call to revert or return degenerate output for its tokens, unfairly excluding it from the auction.

This is a value-extraction vector against intent placers within the "intents escrow and bids" surface, directly reachable by any unprivileged solver competing in the auction, without needing any elevated permission.

### Likelihood Explanation
Any account that can submit a bid to the coprocessor can also submit a DEX trade in the same block to move the spot price of a thinly-liquid pool used to value one of the order's output tokens, then let the selector run its Uniswap quote (`findBestProtocolWithAmountIn`) against the manipulated pool state. Because there is no deviation check, no TWAP, and no secondary oracle on this specific valuation path, the manipulation succeeds deterministically for any pool with insufficient depth relative to the attacker's capital — which is realistic for the non-stable, "exotic" tokens this path is specifically designed to price (single-output/all-stable orders bypass this code entirely and are unaffected).

### Recommendation
- Do not rank/accept bids using a single live spot quote for value comparison. Use a liquidity/time-weighted price (TWAP) or the indexer's already-existing depth-weighted `LiquidityPool` rates (as used by `IndexedRateIntentQuoteStrategy`) for basket valuation instead of `quoteTokenToUsdc`'s raw spot quoter call.
- Add the same `checkPriceGuard`/`maxDeviationBps`-style reference-price sanity check that `FXFiller` already applies for venue pricing, and reject bids/order valuations whose spot quote deviates too far from a reference.
- Where possible, prefer amount-in-kind (per-token) comparisons already enforced on-chain over a single blended USD figure computed from a manipulable source.

### Proof of Concept
1. Order `O` requires output basket `{tokenA: X, tokenB: Y}` where `tokenB` trades in a thin Uniswap pool.
2. Attacker (solver S1) submits Bid1 offering `{tokenA: X, tokenB: Y}` (fair value).
3. Honest solver S2 submits Bid2 offering `{tokenA: X, tokenB: Y*1.1}` (better value).
4. Immediately before/alongside bid selection, S1 (or an accomplice) trades against `tokenB`'s pool to inflate its quoted USD price via `findBestProtocolWithAmountIn`.
5. `computeOutputsUsdValue` for Bid1 now returns an inflated `bidUsd` exceeding Bid2's true, unmanipulated `bidUsd` (S2's larger token amount is quoted at the pre-manipulation, lower price if evaluated after the price reverts, or S1's manipulated call captures the distorted price at evaluation time).
6. `sortMixedOutputs` ranks Bid1 first; `selectAndExecuteBest` simulates and executes Bid1, giving the beneficiary less real value than Bid2 would have provided, despite Bid2 being objectively superior. [3](#0-2)

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L185-237)
```typescript
	async selectAndExecuteBest(order: Order, bids: Bid[]): Promise<SelectBidResult> {
		const commitment = order.id as HexString
		console.log(`[BidManager] selectAndExecuteBest called for commitment=${commitment}, ${bids.length} bid(s)`)

		if (!this.ctx.bundlerUrl) {
			throw new Error("Bundler URL not configured")
		}
		if (!this.ctx.intentsCoprocessor) {
			throw new Error("IntentsCoprocessor required")
		}

		const sortedBids = await this.sortBids(order, bids)
		console.log(`[BidManager] ${sortedBids.length}/${bids.length} bid(s) passed validation and sorting`)
		if (sortedBids.length === 0) {
			throw new Error("No valid bids found")
		}

		console.log(`[BidManager] Simulating ${sortedBids.length} sorted bid(s) to find a valid one`)
		let simulationFailures = 0
		let executionFailures = 0
		for (let idx = 0; idx < sortedBids.length; idx++) {
			const bid = sortedBids[idx]
			console.log(`[BidManager] Simulating bid ${idx + 1}/${sortedBids.length} from solver=${bid.solverAddress}`)

			try {
				await bid.simulate()
			} catch (err) {
				simulationFailures += 1
				console.warn(
					`[BidManager] Bid ${idx + 1} from solver=${bid.solverAddress}: simulation FAILED: ` +
						`${err instanceof Error ? err.message : String(err)}`,
				)
				continue
			}

			console.log(`[BidManager] Bid ${idx + 1} from solver=${bid.solverAddress}: simulation PASSED`)
			try {
				return await bid.execute()
			} catch (err) {
				executionFailures += 1
				console.warn(
					`[BidManager] Bid ${idx + 1} from solver=${bid.solverAddress}: execution FAILED: ` +
						`${err instanceof Error ? err.message : String(err)}; trying next bid`,
				)
			}
		}

		console.error(
			`[BidManager] No executable bids for commitment=${commitment}: ` +
				`${simulationFailures} simulation failure(s), ${executionFailures} execution failure(s)`,
		)
		throw new Error("No bids passed simulation and execution")
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L393-429)
```typescript
	private async sortMixedOutputs(bids: Bid[], orderOutputs: TokenInfo[], chainId: string): Promise<Bid[]> {
		const requiredUsd = await this.computeOutputsUsdValue(orderOutputs, chainId)

		if (requiredUsd === null) {
			console.warn("[BidManager] sortMixedOutputs: output tokens unpriceable, falling back to raw-amount sort")
			return this.sortByRawAmountFallback(bids, orderOutputs)
		}

		console.log(`[BidManager] sortMixedOutputs: required USD value=${requiredUsd.toString()}`)
		const validBids: { bid: Bid; usdValue: Decimal }[] = []

		for (const bid of bids) {
			const bidUsd = await this.computeOutputsUsdValue(bid.outputs, chainId)

			if (bidUsd === null) {
				console.warn(`[BidManager] Bid from solver=${bid.solverAddress} REJECTED: unable to price mixed outputs`)
				continue
			}

			if (bidUsd.lt(requiredUsd)) {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress}: partial fill candidate ` +
						`(bid=${bidUsd.toString()}, required=${requiredUsd.toString()}, ` +
						`covers=${bidUsd.div(requiredUsd).mul(100).toFixed(2)}%)`,
				)
			} else {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress} ACCEPTED: mixed USD value=${bidUsd.toString()}`,
				)
			}

			validBids.push({ bid, usdValue: bidUsd })
		}

		validBids.sort((a, b) => b.usdValue.comparedTo(a.usdValue))
		return validBids.map(({ bid }) => bid)
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L566-608)
```typescript
			try {
				const usdcAmount = await this.quoteTokenToUsdc(
					tokenAddr,
					output.amount,
					wethAddr,
					usdcAddr,
					chainId,
					client,
				)
				totalUsd = totalUsd.plus(new Decimal(usdcAmount.toString()).div(new Decimal(10).pow(usdcDecimals)))
			} catch {
				return null
			}
		}

		return totalUsd
	}

	/**
	 * Gets the USDC-equivalent amount for a non-stable token using on-chain DEX quotes.
	 * Tries direct token→USDC first, then falls back to token→WETH→USDC.
	 */
	private async quoteTokenToUsdc(
		tokenAddr: HexString,
		amount: bigint,
		wethAddr: HexString,
		usdcAddr: HexString,
		chainId: string,
		client: IntentGatewayContext["dest"]["client"],
	): Promise<bigint> {
		const isWethOrNative = tokenAddr.toLowerCase() === wethAddr.toLowerCase() || tokenAddr === ADDRESS_ZERO

		if (isWethOrNative) {
			const { amountOut, protocol } = await this.ctx.swap.findBestProtocolWithAmountIn(
				client,
				wethAddr,
				usdcAddr,
				amount,
				chainId,
			)
			if (protocol === null || amountOut === 0n) throw new Error("No WETH→USDC liquidity")
			return amountOut
		}
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L609-642)
```typescript

		// Try direct: token → USDC
		try {
			const { amountOut, protocol } = await this.ctx.swap.findBestProtocolWithAmountIn(
				client,
				tokenAddr,
				usdcAddr,
				amount,
				chainId,
			)
			if (protocol === null || amountOut === 0n) throw new Error("No direct liquidity")
			return amountOut
		} catch {
			// Fallback: token → WETH → USDC
			const { amountOut: wethOut, protocol: p1 } = await this.ctx.swap.findBestProtocolWithAmountIn(
				client,
				tokenAddr,
				wethAddr,
				amount,
				chainId,
			)
			if (p1 === null || wethOut === 0n) throw new Error("No token→WETH liquidity")

			const { amountOut: usdcOut, protocol: p2 } = await this.ctx.swap.findBestProtocolWithAmountIn(
				client,
				wethAddr,
				usdcAddr,
				wethOut,
				chainId,
			)
			if (p2 === null || usdcOut === 0n) throw new Error("No WETH→USDC liquidity")
			return usdcOut
		}
	}
```

**File:** sdk/packages/simplex/src/strategies/fx.ts (L1449-1465)
```typescript
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
