### Title
Manipulatable spot-price DEX quoting lets a malicious solver's bid win the auction with worthless output tokens - ([File: sdk/packages/sdk/src/protocols/intents/BidManager.ts])

### Summary
`BidManager.sortMixedOutputs()` ranks competing solver fills for an `IntentGatewayV2` order by an on-chain DEX spot-price valuation (`computeOutputsUsdValue` → `quoteTokenToUsdc` → `Swap.findBestProtocolWithAmountIn`/`getV2QuoteWithAmountIn`), with no TWAP, no oracle cross-check, and no manipulation guard. This is the same root-cause bug class as the reported "manipulatable oracle breaking slippage protection": a spot AMM quote (`getAmountsOut`) is trusted as ground truth for how much value a payment is worth, and it is trivially manipulable by an attacker who can move the pool price in the same transaction/block the quote is read.

### Finding Description
When an order's output assets are a "mixed" (non-all-stable) basket, `sortMixedOutputs` prices every candidate bid's offered outputs by walking each non-stable token through `quoteTokenToUsdc`, which calls `this.ctx.swap.findBestProtocolWithAmountIn(...)` [1](#0-0) . That helper is backed by `Swap.getV2QuoteWithAmountIn`, a bare Uniswap V2 `getAmountsOut` call against live reserves [2](#0-1) . `sortMixedOutputs` then sorts bids purely by this DEX-derived USD value and feeds the ranking straight into `selectAndExecuteBest`, which simulates and executes the top-ranked bid without any further onchain price check [3](#0-2) [4](#0-3) .

Any unprivileged solver can submit a bid whose output token is a thinly-liquid or attacker-controlled pair. By sandwiching (or simply front-running) the moment `sortBids`/`selectAndExecuteBest` reads the quote — e.g., via a large swap in the same pool right before the coprocessor/relayer computes the ranking — the attacker inflates the AMM spot price of their output token, making `computeOutputsUsdValue` report their bid as the highest-value fill even though the tokens they actually deliver on execution (post price reversion, or a token they hold in bulk and can dump) are worth a fraction of the escrowed input the order is paying out. Because the fallback path (`sortByRawAmountFallback`) only triggers when pricing fails entirely, not when pricing is merely wrong, a manipulated-but-successful quote is never rejected.

This mirrors the external report precisely: an unprotected `getAmountsOut`-style spot quote used to decide "how much is being received" for a value comparison, with no TWAP/oracle and no bound on price impact.

### Impact Explanation
A winning malicious bid causes the `IntentGatewayV2`/`IntentsBase` escrow to release the user's escrowed input tokens to a solver whose actual delivered value is far below the required order value — direct theft of the difference from the order's beneficiary/protocol side. Because bid selection is the mechanism deciding which solver gets paid the input escrow, a manipulated ranking is a fund-loss vector, not merely a UX inefficiency.

### Likelihood Explanation
Likelihood is Medium: it requires (a) an order with mixed, non-stable output assets (so `sortMixedOutputs` is used rather than the single-asset or all-stables paths, which don't rely on DEX spot pricing), and (b) a thin-liquidity pool for the manipulated output token that the attacker can move cheaply within the narrow window between bid submission and selection/execution. Both conditions are realistically achievable by any solver participating in the permissionless bidding process.

### Recommendation
Do not rank or accept solver bids using single-block AMM spot quotes. Use a manipulation-resistant price source (TWAP over multiple blocks, a Chainlink/oracle price, or a price bound cross-checked against a reference price as already implemented for Simplex's Uniswap V4 pool pricing, e.g. `referencePrice`/`maxDeviationBps` guard) before trusting `quoteTokenToUsdc`'s result in `sortMixedOutputs`. Alternatively, require solver bids for mixed-output orders to be denominated only in pre-approved/allow-listed tokens with sufficient deep liquidity, and add a hard deviation check between the read spot quote and a longer-window reference before it can influence bid ranking.

### Proof of Concept
1. Place an `IntentGatewayV2` order whose `output.assets` include at least one non-stable, thin-liquidity token alongside another asset (triggering `sortMixedOutputs`).
2. Attacker (as solver) submits a bid offering a large nominal amount of the thin-liquidity token as output.
3. Immediately before/while `BidManager.sortBids` → `sortMixedOutputs` → `computeOutputsUsdValue` executes its `getAmountsOut`-based quote, the attacker (or an accomplice) executes a large swap in that token's pool, temporarily inflating its spot price.
4. `quoteTokenToUsdc` returns an inflated USDC value for the attacker's bid, causing `sortMixedOutputs` to rank it highest; `selectAndExecuteBest` simulates and executes it, releasing the escrowed order inputs to the attacker for tokens actually worth far less once the price reverts.

Note: this analysis is based on the SDK/off-chain bid-ranking logic reachable by the codebase index; I was not able to trace how the on-chain `IntentGatewayV2`/coprocessor enforces (or fails to enforce) a minimum value at fill time beyond what `BidImpl.simulate()`/`execute()` do, so confirming the full extent of exploitability (e.g., whether on-chain fill checks provide any independent backstop) would require deeper inspection of `BidImpl.sol`/`IntentsBase.sol`'s fill-validation path, which was not fully retrievable from the index.

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

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L588-620)
```typescript
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
```

**File:** sdk/packages/sdk/src/utils/swap.ts (L70-98)
```typescript
	async getV2QuoteWithAmountIn(
		client: PublicClient,
		tokenIn: HexString,
		tokenOut: HexString,
		amountIn: bigint,
		evmChainID: string,
	): Promise<bigint> {
		const v2Router = this.chainConfigService.getUniswapRouterV2Address(evmChainID)

		const wethAsset = this.chainConfigService.getWrappedNativeAssetWithDecimals(evmChainID).asset
		const tokenInForQuote = tokenIn === ADDRESS_ZERO ? wethAsset : tokenIn
		const tokenOutForQuote = tokenOut === ADDRESS_ZERO ? wethAsset : tokenOut

		try {
			const v2AmountOut = await client.simulateContract({
				address: v2Router,
				abi: UniswapRouterV2.ABI,
				// @ts-ignore
				functionName: "getAmountsOut",
				// @ts-ignore
				args: [amountIn, [tokenInForQuote, tokenOutForQuote]],
			})

			return v2AmountOut.result[1]
		} catch {
			console.warn("V2 quote failed:")
			return BigInt(0)
		}
	}
```
