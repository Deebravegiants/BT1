## Title
`selectAndExecuteBest` autopilot ranks stablecoin bids at a hardcoded $1 peg, letting a depegged USDC/USDT bid be auto-selected over a genuinely better offer - ([File: sdk/packages/sdk/src/protocols/intents/BidManager.ts])

### Summary
`BidManager.sortAllStables` and its helper `computeStablesUsdValue` price every USDC/USDT output "treating each stable as $1" with no live oracle check, then feed the resulting ranking into the SDK's autopilot bid-selection path (`selectAndExecuteBest`) used by `IntentGateway.executeBest`. This mirrors the Perennial report's root cause: a hardcoded USD-peg assumption for a stablecoin feeding a value comparison that gates an economic decision, with no mechanism to detect a USDC/USDT depeg event.

### Finding Description
`computeStablesUsdValue` sums output amounts for USDC/USDT bids by dividing by decimals only, explicitly "treating each token as $1": [1](#0-0) [2](#0-1) 

This function is used by `sortAllStables` to rank competing solver bids whenever an order's outputs are all USDC/USDT, and the sorted result is what `selectAndExecuteBest`-style autopilot flows (documented as the auto sort-simulate-execute helper in the class docstring) act on without further value verification: [3](#0-2) 

There is no check anywhere in this path that USDC or USDT is actually trading at $1 (unlike `sortMixedOutputs`, which prices non-stable legs via live DEX quotes). If one of the two competing output tokens depegs (e.g., USDC trading at 87¢ as during the March 2023 event cited in the source report), a bid denominated in the depegged token can nominally out-rank a bid in the still-pegged token while delivering strictly less real value, and the autopilot path will select and execute it.

### Impact Explanation
An order placer or an integrator using `executeBest`/`selectAndExecuteBest` receives a solver-chosen "best" bid that is not actually the best in USD terms during a depeg event, causing a quantifiable economic loss to the order placer that is silently executed without a live-price sanity check. This is analogous to Perennial's overvalued-collateral issue: an on-chain-consequential value comparison assumes a fixed $1 peg for a stablecoin with no fallback or circuit breaker, so a real depeg directly translates into an incorrect, financially consequential decision (bid selection and execution) rather than merely a display/estimate.

### Likelihood Explanation
Likelihood is tied to the same trigger as the source report: a USDC/USDT depeg event, which has occurred historically (March 2023) and is realistically possible again. Any solver (an unprivileged bidder) can submit a bid in the depegged stablecoin at any time; no privileged action is needed to trigger the mispricing — only a real-world depeg plus normal solver competition in `sortAllStables`/autopilot execution.

### Recommendation
Replace the hardcoded $1 assumption in `computeStablesUsdValue` with a live price check (the same DEX-quote or oracle mechanism already used in `sortMixedOutputs`/`computeOutputsUsdValue`) for USDC/USDT, or at minimum add a peg-deviation guard (similar to the `referencePrice`/`maxDeviationBps` guard already implemented for Uniswap V4 pool pricing in the Simplex filler) that refuses to treat a stablecoin as $1 once its live price deviates beyond a configured threshold, falling back to `sortByRawAmountFallback` or rejecting the bid instead.

### Proof of Concept
1. An order requests output in USDC or USDT (case B, "all outputs are USDC/USDT") is placed and multiple solvers bid.
2. Solver A bids `1000` USDT (still pegged, real value ≈ $1000).
3. Solver B bids `1050` USDC, but USDC has depegged to $0.87 (real value ≈ $913.50).
4. `computeStablesUsdValue` reports Solver B's bid as `1050` USD-equivalent (nominal units, no depeg check) versus Solver A's `1000`, per the logic at [4](#0-3) 
5. `sortAllStables` ranks Solver B's bid first; an autopilot caller using the sort-simulate-execute helper (`selectAndExecuteBest`) executes it, delivering the order placer real value below what Solver A actually offered — without any depeg detection.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L21-34)
```typescript
/**
 * Manages the solver bid lifecycle for IntentGatewayV2 orders.
 *
 * Responsibilities include:
 * - Constructing signed `PackedUserOperation` objects that solvers submit to the
 *   Hyperbridge coprocessor as bids (`prepareSubmitBid`).
 * - Decoding raw filler bids into first-class {@link Bid} objects (`buildBids`)
 *   that consumers can rank, simulate, and execute themselves.
 * - Sorting bids by output value (`sortBids`) and providing the autopilot
 *   sort-simulate-execute helper (`selectAndExecuteBest`) for consumers that do
 *   not need custom selection logic.
 * - Pricing bid outputs using on-chain DEX quotes so that the highest-value
 *   solver is preferred.
 */
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L352-386)
```typescript
	/**
	 * Case B: all outputs are USDC/USDT.
	 * Sum normalised USD values (treating each stable as $1) and sort descending.
	 * Partial fill bids are allowed.
	 */
	private sortAllStables(bids: Bid[], orderOutputs: TokenInfo[], chainId: string): Bid[] {
		const requiredUsd = this.computeStablesUsdValue(orderOutputs, chainId)
		console.log(`[BidManager] sortAllStables: required USD value=${requiredUsd.toString()}`)

		const validBids: { bid: Bid; usdValue: Decimal }[] = []

		for (const bid of bids) {
			const bidUsd = this.computeStablesUsdValue(bid.outputs, chainId)

			if (bidUsd === null) {
				console.warn(`[BidManager] Bid from solver=${bid.solverAddress} REJECTED: unable to compute USD value`)
				continue
			}

			if (bidUsd.lt(requiredUsd)) {
				console.log(
					`[BidManager] Bid from solver=${bid.solverAddress}: partial fill candidate ` +
						`(bid=${bidUsd.toString()}, required=${requiredUsd.toString()}, ` +
						`covers=${bidUsd.div(requiredUsd).mul(100).toFixed(2)}%)`,
				)
			} else {
				console.log(`[BidManager] Bid from solver=${bid.solverAddress} ACCEPTED: USD value=${bidUsd.toString()}`)
			}

			validBids.push({ bid, usdValue: bidUsd })
		}

		validBids.sort((a, b) => b.usdValue.comparedTo(a.usdValue))
		return validBids.map(({ bid }) => bid)
	}
```
