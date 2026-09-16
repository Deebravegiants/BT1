### Title
Hardcoded 1 USDC = 1 USDT = $1 assumption in `BidManager.sortAllStables` causes intent placers to auto-select the wrong (lower-value) solver bid during a stablecoin depeg - ([File: sdk/packages/sdk/src/protocols/intents/BidManager.ts])

### Summary
`BidManager.sortAllStables` and its helper `computeStablesUsdValue` value every USDC/USDT output at a hardcoded $1, ignoring actual market price. This ranking feeds `selectAndExecuteBest` (via `IntentGateway.ts`), the "autopilot" path that automatically picks the bid it believes is worth the most and submits it on-chain on behalf of the order placer — an unprivileged user who placed a cross-chain intent through Hyperbridge's Intent Gateway.

### Finding Description
`sortAllStables` sums each stable output "treating each token as $1" and sorts bids by that sum: [1](#0-0) 

`computeStablesUsdValue` performs the same pinned-$1 normalization used to size the "required" USD value and rank competing bids: [2](#0-1) 

`sortBids` dispatches to this stable-only path whenever an order's outputs are entirely USDC/USDT: [3](#0-2) 

The identical hardcoded-peg assumption is baked into multiple other consumer-facing code paths that price fee tokens and gas costs, e.g. `convertGasToFeeToken`'s fallback (`feeTokenPriceUsd = new Decimal(1)`), showing this is a systemic pattern rather than an isolated bug: [4](#0-3) 

If USDC or USDT depegs (temporarily or permanently) so that 1 USDC ≠ 1 USDT ≠ $1, two competing solver bids offering different actual dollar values can be ranked incorrectly — a bid offering more raw units of a depegged (cheaper) stablecoin could be ranked above a bid offering fewer units of a token still worth $1, even though the latter is worth more.

### Impact Explanation
This ranking result is not merely advisory — `selectAndExecuteBest` (referenced across `IntentGateway.ts` and `BidManager.ts`) consumes `sortBids`'s output to automatically choose and execute the "best" bid without further price verification. During a stablecoin depeg event, this can cause the order placer (an ordinary, unprivileged Hyperbridge Intent Gateway user) to have their escrowed input tokens released to a solver in exchange for a bid that is worth strictly less than an available alternative — a direct, unrecoverable loss of value to the user, matching the "loss of funds from incorrect stablecoin-parity assumptions" bug class in the reported finding.

### Likelihood Explanation
Likelihood is tied directly to stablecoin depeg events, which have occurred historically (USDT/USDC depegs during market stress, e.g., March 2023 USDC depeg during the SVB event) and are explicitly called out as a realistic risk in the original report. Any order whose output set is entirely USDC/USDT, filled via the `selectAndExecuteBest` autopilot path during such an event, is exposed. Because no oracle or live pricing information is consulted for the stable-only path, the bug triggers deterministically whenever a depeg coincides with competing bids denominated differently, without requiring privileged access, malicious actors, or exotic preconditions — it is a normal outcome of ordinary Intent Gateway usage during market stress.

### Recommendation
Do not hardcode $1 for USDC/USDT in `computeStablesUsdValue`/`sortAllStables`. Instead, source live USD pricing (e.g., via the same DEX-quote mechanism already used in `computeOutputsUsdValue`/`sortMixedOutputs`, or a Chainlink-style oracle as used elsewhere in the codebase, e.g. `SimplexPaymaster`'s oracle-backed `getTokenPrice`) for all stable outputs before ranking bids, and apply the same fix to the other hardcoded-$1 fallbacks in `convertGasToFeeToken`/`convertFeeTokenToWei`.

### Proof of Concept
1. An order placer creates a cross-chain intent whose accepted outputs are USDC and USDT (an all-stables output set).
2. Two solvers submit competing bids: Bid A offers 1,000 USDT, Bid B offers 970 USDC, at a moment when USDC has depegged to $0.90 (USDT still ~$1).
3. `sortBids` routes to `sortAllStables` since both outputs are stables; `computeStablesUsdValue` computes Bid A = $1,000 (1000 × 1), Bid B = $970 (970 × 1) — both priced with the hardcoded $1 assumption, so Bid A correctly ranks first in this instance, but the ranking becomes incorrect in the reverse scenario: if Bid A offers 1,000 USDC (real value $900 at $0.90 peg) and Bid B offers 970 USDT (real value $970), `computeStablesUsdValue` still reports Bid A = $1,000 > Bid B = $970, so `sortAllStables` incorrectly ranks the USDC bid first.
4. `selectAndExecuteBest` selects and executes Bid A automatically, releasing the user's escrow to the solver for output actually worth $900 instead of the $970 alternative — a $70 loss on a $1,000 order purely due to the hardcoded peg assumption, with no user recourse since the fill already executed on-chain.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L255-273)
```typescript
	async sortBids(order: Order, bids: Bid[]): Promise<Bid[]> {
		const outputs = order.output.assets

		if (outputs.length <= 1) {
			console.log(`[BidManager] Using single-output sorting (1 output asset)`)
			return this.sortSingleOutput(bids, outputs[0])
		}

		const chainId = this.ctx.dest.config.stateMachineId
		const allStables = outputs.every((o) => this.isStableToken(bytes32ToBytes20(o.token), chainId))

		if (allStables) {
			console.log(`[BidManager] Using all-stables sorting (${outputs.length} stable output assets)`)
			return this.sortAllStables(bids, outputs, chainId)
		}

		console.log(`[BidManager] Using mixed-output sorting (${outputs.length} output assets, some non-stable)`)
		return this.sortMixedOutputs(bids, outputs, chainId)
	}
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

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L519-537)
```typescript
	// ── Basket valuation helpers ──────────────────────────────────────

	/**
	 * Sums the USD value of a basket of stable tokens (USDC/USDT only),
	 * normalising each amount by its decimal count and treating each token as $1.
	 *
	 * @param outputs - List of token/amount pairs where every token is a stable.
	 * @param chainId - State-machine ID used to look up decimals.
	 * @returns Total USD value as a `Decimal`.
	 */
	private computeStablesUsdValue(outputs: TokenInfo[], chainId: string): Decimal {
		let total = new Decimal(0)
		for (const output of outputs) {
			const tokenAddr = bytes32ToBytes20(output.token)
			const decimals = this.getStableDecimals(tokenAddr, chainId)
			total = total.plus(new Decimal(output.amount.toString()).div(new Decimal(10).pow(decimals)))
		}
		return total
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/utils.ts (L206-214)
```typescript
		const nativeCurrency = client.chain?.nativeCurrency
		const chainId = Number.parseInt(evmChainID.split("-")[1])
		const gasCostInToken = new Decimal(formatUnits(gasCostInWei, nativeCurrency?.decimals ?? 18))
		const tokenPriceUsd = await fetchPrice(nativeCurrency?.symbol, chainId)
		const gasCostUsd = gasCostInToken.times(tokenPriceUsd)
		const feeTokenPriceUsd = new Decimal(1)
		const gasCostInFeeToken = gasCostUsd.dividedBy(feeTokenPriceUsd)
		return parseUnits(gasCostInFeeToken.toFixed(feeToken.decimals), feeToken.decimals)
	}
```
