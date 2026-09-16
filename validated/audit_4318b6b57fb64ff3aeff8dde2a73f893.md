This confirms the analog. `Swap.getV2QuoteWithAmountIn`/`getV3QuoteWithAmountIn`/`getV4QuoteWithAmountIn` (`sdk/packages/sdk/src/utils/swap.ts`) are single-block spot AMM quotes — `getAmountsOut` on V2, `quoteExactInputSingle` on V3/V4 — with no TWAP, no liquidity-depth floor, and no minimum-pool-age check. `findBestProtocolWithAmountIn` simply picks whichever protocol/fee-tier returns the largest `amountOut`, so a thin or freshly-created pool with an inflated spot price wins outright.

### Title
Bid-ranking auto-selector trusts unguarded spot-AMM quotes for non-stable outputs, letting a solver win with a price-inflated worthless token - ([File: sdk/packages/sdk/src/protocols/intents/BidManager.ts])

### Summary
`BidManager.sortMixedOutputs`/`computeOutputsUsdValue` (used by `selectAndExecuteBest`, which backs the unprivileged, no-review autopilot paths `executeBest`/`resumeBest`/`selectBid`) values a solver's non-stable output tokens by calling `this.ctx.swap.findBestProtocolWithAmountIn`, which is a bare spot-price quote from Uniswap V2/V3/V4 (`getAmountsOut`, `quoteExactInputSingle`) with no TWAP, no minimum liquidity/depth requirement, and no sanity bound against the requested output value.

### Finding Description
`computeOutputsUsdValue` (`sdk/packages/sdk/src/protocols/intents/BidManager.ts:545-582`) prices each non-stable output token of a bid by calling `quoteTokenToUsdc`, which delegates to `this.ctx.swap.findBestProtocolWithAmountIn` [1](#0-0) . That function (`sdk/packages/sdk/src/utils/swap.ts:1228-1384`) simply queries V2/V3/V4 spot quotes for every configured fee tier and returns whichever yields the largest `amountOut` [2](#0-1) , with each per-protocol quote (`getV2QuoteWithAmountIn`, `getV3QuoteWithAmountIn`, `getV4QuoteWithAmountIn`) reading straight from the pool's current reserves/tick with no liquidity floor and no time-weighting [3](#0-2) .

`sortMixedOutputs` uses this USD figure to rank competing solver bids by descending value and feeds the ranked list straight into `selectAndExecuteBest`, which simulates then executes the top bid with no independent sanity check of the priced value [4](#0-3) [5](#0-4) . This is the exact bug class from the SushiSwap/DIGG incident: an attacker with no special privilege deploys a brand-new low-liquidity pool (or manipulates an existing thin pool) for an arbitrary token pair and mints a tiny amount of tokens into it, producing a wildly inflated spot price for a trivial input amount — precisely the "no WETH pair, attacker creates one and skews the initial price" pattern described in the report.

A malicious solver can bid on an order with a near-worthless custom token it controls the pool for, sized so that `findBestProtocolWithAmountIn` reports an inflated `amountOut` in USDC terms. `computeOutputsUsdValue` accepts that quote at face value, `sortMixedOutputs` ranks the bid highest, and `selectAndExecuteBest`/`executeBest`/`resumeBest` (the exact API path documented for unattended autopilot execution, reachable from any user placing an order via the Intent Gateway) selects and executes it, releasing the user's real escrowed input tokens to the attacker's `SolverAccount` for essentially worthless output.

### Impact Explanation
This directly causes theft of escrowed user funds: the autopilot commits the user's real assets to a solver whose delivered value was fabricated via a manipulable spot price, with no minimum-liquidity or TWAP safeguard. Since this flow is the SDK's advertised "batteries-included" execution path (`executeBest`/`resumeBest`), any user relying on it for mixed-output orders is exposed without any error being surfaced until after settlement.

### Likelihood Explanation
Deploying a new pool and seeding minimal liquidity to skew a single-block spot quote is cheap and requires no special access — any solver participating in the permissionless bid auction can do it, mirroring exactly the low-cost, unprivileged DIGG/WETH pool-creation attack in the report. The only friction is that the bid must still pass `bid.simulate()`, but simulation only proves the calldata executes, not that the priced value is legitimate.

### Recommendation
Do not rely on single-block spot AMM quotes (`getAmountsOut`/`quoteExactInputSingle`) for economic ranking of solver bids. Require a minimum-liquidity/TTL-verified quote source (e.g., TWAP oracle, or a liquidity-depth check ensuring the priced amount is a small fraction of pool reserves), reject tokens with no established/verified market (e.g., unknown or newly-deployed pools), and/or cap the influence of DEX-quoted value with a sanity ceiling tied to the order's own declared/expected value before allowing `selectAndExecuteBest` to auto-execute.

### Proof of Concept
1. Attacker deploys `EvilToken` and a Uniswap V2/V3/V4 pool `EvilToken/USDC` (or `EvilToken/WETH`) with negligible real liquidity (e.g., 1 wei USDC vs. 1 wei EvilToken), mirroring the SushiSwap DIGG/WETH pair creation.
2. A user places a mixed-output Intent Gateway order (e.g., requiring USDC + some other token) via `executeBest`.
3. Attacker's solver bids, offering a tiny amount of `EvilToken` as one of the outputs, sized so `getV2QuoteWithAmountIn`/`quoteExactInputSingle` against the seeded pool reports a USDC-equivalent value exceeding the legitimate solvers' bids (`quoteTokenToUsdc` → `findBestProtocolWithAmountIn`).
4. `sortMixedOutputs` computes `bidUsd` for the attacker's bid as inflated and ranks it first [6](#0-5) .
5. `selectAndExecuteBest` simulates (which succeeds, since the fill only requires transferring the attacker's cheap `EvilToken`) and executes the attacker's bid, releasing the user's real escrowed input tokens to the attacker.

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

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L393-428)
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

**File:** sdk/packages/sdk/src/utils/swap.ts (L70-97)
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
```

**File:** sdk/packages/sdk/src/utils/swap.ts (L1319-1344)
```typescript
		// If no protocol is selected, query all protocols to find the best one
		const amountOutV2 = await this.getV2QuoteWithAmountIn(client, tokenIn, tokenOut, amountIn, evmChainID)

		const { amountOut: amountOutV3, fee: bestV3Fee } = await this.getV3QuoteWithAmountIn(
			client,
			tokenIn,
			tokenOut,
			amountIn,
			evmChainID,
		)

		const { amountOut: amountOutV4, fee: bestV4Fee } = await this.getV4QuoteWithAmountIn(
			client,
			tokenIn,
			tokenOut,
			amountIn,
			evmChainID,
		)

		// If no liquidity found in any protocol
		if (amountOutV2 === BigInt(0) && amountOutV3 === BigInt(0) && amountOutV4 === BigInt(0)) {
			return {
				protocol: null,
				amountOut: BigInt(0),
			}
		}
```
