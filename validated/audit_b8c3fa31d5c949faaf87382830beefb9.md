## Analysis

The reported bug class — a Uniswap spot price used as ground truth for a financial decision, manipulable by flash-loan-driven reserve swings — has a direct analog in the SDK's default bid-selection path for `IntentGatewayV2` orders.

### Title
Bid ranking for intent-fill selection trusts unprotected on-chain DEX spot quotes, letting a solver's flash-loan-manipulated pool make an inferior bid appear best - ([File: sdk/packages/sdk/src/protocols/intents/BidManager.ts])

### Summary
`BidManager.sortMixedOutputs` and its helper `computeOutputsUsdValue`/`quoteTokenToUsdc` price every non-stable output token of a solver's bid by calling live on-chain DEX quoting (`this.ctx.swap.findBestProtocolWithAmountIn`, which reads current pool reserves/spot price) with no TWAP, no deviation guard, and no sanity check against a reference price. This ranking directly determines which solver bid `selectAndExecuteBest`/`selectBid` will simulate and execute on behalf of the order-placing user.

### Finding Description [1](#0-0) 

`sortMixedOutputs` prices the order's required output basket and every competing bid's output basket via `computeOutputsUsdValue`, then sorts descending by that USD value: [2](#0-1) 

For any non-stable output token, the USD value comes from `quoteTokenToUsdc`, which is a straight spot-price read against whichever DEX pool `findBestProtocolWithAmountIn` selects (direct token→USDC, or token→WETH→USDC fallback): [3](#0-2) 

This is the same pattern the report flags: a spot AMM quote, taken instantaneously and trusted as "the real price," with no TWAP oracle and no bound on divergence from a reference. Unlike the Simplex solver's own pricing engine, which explicitly acknowledges this risk and applies a `checkPriceGuard`/`maxDeviationBps` reference check before using a venue quote (`sdk/packages/simplex/src/strategies/fx.ts`), the SDK's bid-ranking path applies no such guard at all — the raw quote directly decides bid ordering, and the top-ranked bid is simulated and executed without ever re-deriving value from a manipulation-resistant source.

The selection result then flows straight into execution: [4](#0-3) 

`selectAndExecuteBest` simulates bids strictly in the order `sortBids` produced and executes the first that passes simulation — it never re-checks that the executed bid's real economic value exceeds a genuinely better competing bid.

### Impact Explanation
Any intent solver (an unprivileged, permissionless actor per the intent-fill flow) that also controls or can transiently manipulate a thin liquidity pool for one of its bid's output tokens (via flash loan) can inflate that pool's spot price for the duration of the caller's quoting/selection call. This makes a bid offering objectively less real value appear to be the highest-USD-value bid, so `selectAndExecuteBest`/`selectBid` — the SDK's documented "autopilot" path with "no per-bid input from the caller" — picks and executes it over a solver's genuinely better-priced bid. The order-placing user's escrowed input is then released against inferior output, a direct value loss functionally identical to the price-manipulation impact described in the source report (broken pricing feeding a financial decision that moves funds).

### Likelihood Explanation
Any account can submit a competing solver bid into the intents flow, and manipulating one thin/exotic-token pool via a flash loan for the single RPC call window that `sortBids`/`computeOutputsUsdValue` executes in is a well-established, low-cost attack pattern (the exact one the external report describes) requiring no special privilege — only that the victim's caller uses the default `selectAndExecuteBest`/`selectBid` autopilot rather than independently verifying bid value through a manipulation-resistant source.

### Recommendation
Do not rank or select bids using a single-block, single-source on-chain spot quote. Either:
- Use a TWAP/depth-weighted price source (as the SDK's own `indexed_rates` intent-quote strategy already does via the indexer's `LiquidityPool.buyRate`/`sellRate`), or
- Apply a `checkPriceGuard`-style bound (reference price + max deviation) before trusting any live DEX quote used for ranking, mirroring the guard already implemented in `sdk/packages/simplex/src/strategies/fx.ts`, or
- Require multiple independent liquidity sources/pools and take a conservative (e.g., minimum) valuation rather than a single spot quote per token.

### Proof of Concept
1. Attacker deploys/identifies a thin Uniswap pool for `TokenX`, one of the tokens it will offer in its bid's `FillOptions.outputs`.
2. Attacker submits a mixed-output bid offering a small real amount of `TokenX` alongside other assets, undercutting a legitimate competing solver's bid in real value.
3. When the order-placing user (or their automated agent) calls `selectAndExecuteBest`/`selectBid`, attacker (in the same block/transaction context, e.g. via a bundled flash loan) drives `TokenX`'s pool reserves so `findBestProtocolWithAmountIn` returns an inflated `amountOut` in USDC terms for the attacker's `TokenX` amount.
4. `computeOutputsUsdValue` for the attacker's bid now exceeds the legitimate bid's USD value; `sortMixedOutputs` ranks the attacker's bid first.
5. `selectAndExecuteBest` simulates and executes the attacker's bid first (it passes simulation since it is a real, executable transfer, just of low real value), releasing the user's escrowed input for genuinely inferior output — the attacker unwinds the flash loan afterward, restoring the pool and pocketing the difference.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L185-230)
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

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L545-582)
```typescript
	private async computeOutputsUsdValue(
		outputs: { token: HexString; amount: bigint }[],
		chainId: string,
	): Promise<Decimal | null> {
		const configService = this.ctx.dest.configService
		const client = this.ctx.dest.client
		const usdcAddr = configService.getUsdcAsset(chainId)
		const usdcDecimals = configService.getUsdcDecimals(chainId)
		const { asset: wethAddr } = configService.getWrappedNativeAssetWithDecimals(chainId)

		let totalUsd = new Decimal(0)

		for (const output of outputs) {
			const tokenAddr = bytes32ToBytes20(output.token)

			if (this.isStableToken(tokenAddr, chainId)) {
				const decimals = this.getStableDecimals(tokenAddr, chainId)
				totalUsd = totalUsd.plus(new Decimal(output.amount.toString()).div(new Decimal(10).pow(decimals)))
				continue
			}

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
```

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L588-641)
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
```
