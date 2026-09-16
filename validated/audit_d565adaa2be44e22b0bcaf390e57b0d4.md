Confirmed: `findBestProtocolWithAmountIn` selects the single-block instantaneous Uniswap V2 reserves quote or V3/V4 `quoteExactInputSingle` simulate-swap result with no TWAP, no staleness check, and no deviation guard — the same class of manipulable "spot swap simulation" the external report flags.

### Title
Solver-controlled Uniswap spot quotes let a bidder manipulate `executeBest`/`resumeBest` autopilot bid selection into picking an inferior, attacker-favorable fill - (File: sdk/packages/sdk/src/protocols/intents/BidManager.ts)

### Summary
`IntentGateway.executeBest`/`resumeBest` autonomously ranks competing solver bids and executes the top one with no human review. For orders with non-stable or mixed outputs, ranking is driven by `BidManager.sortMixedOutputs`/`sortAllStables` → `computeOutputsUsdValue` → `quoteTokenToUsdc`, which prices each bid's offered tokens using a live, single-block Uniswap V2/V3/V4 spot quote (`ctx.swap.findBestProtocolWithAmountIn`). Any account that can submit a bid to the order (an unprivileged intent solver) can control which pool that quote reads from by naming an obscure/thin-liquidity output token, and can manipulate that pool's spot price within the same block (e.g. via a flash-loan swap) to make its bid appear to be worth more USD than a legitimate competing bid, causing the autopilot to select and execute it.

### Finding Description
`quoteTokenToUsdc` obtains "the current value of a token in USDC" purely from `findBestProtocolWithAmountIn`, which internally calls `getV2QuoteWithAmountIn` (reads live AMM reserves), `getV3QuoteWithAmountIn`/`getV4QuoteWithAmountIn` (calls the on-chain Quoter's `quoteExactInputSingle`, which simulates a swap against the pool's current state) [1](#0-0) . These are exactly the "result of a simulated swap given the current pool state" primitives the external report calls out as manipulable with a flash loan.

`computeOutputsUsdValue` feeds every non-stable bid output through this pricing path [2](#0-1) , and `quoteTokenToUsdc` picks whichever pool/pair (direct token→USDC, or token→WETH→USDC fallback) happens to return liquidity for the attacker-chosen output token [3](#0-2) . `sortMixedOutputs` then ranks bids purely by this computed USD value, descending [4](#0-3) .

`sortBids`'s result is consumed directly by `selectAndExecuteBest`, which simulates and executes ("select bid" + submit the UserOperation via the bundler) the top-ranked bid with no independent value check and no deviation guard against a reference/TWAP price [5](#0-4) . The autopilot entry points `executeBest`/`resumeBest` call this automatically every round with zero caller input beyond signing the placement transaction [6](#0-5) [7](#0-6) .

An unprivileged solver reachable through this path (any account submitting a bid to `IntentGatewayV2`, as documented for `submitBid`/`prepareSubmitBid`) can therefore:
1. Choose to fill the order with a low-liquidity token that it also controls a pool for.
2. Within the same transaction/block window as its bid, push that pool's spot price up via a self-swap (flash-loan sized) so `quoteTokenToUsdc` reports an inflated USDC value for its bid's outputs.
3. Have `sortMixedOutputs`/`sortAllStables` rank its manipulated bid above a legitimate, genuinely-more-valuable competing bid.
4. Get `selectAndExecuteBest` to sign and submit its bid, delivering actual tokens worth far less than the order's required/legitimate value, while the pool price reverts once the attacker unwinds its manipulation swap.

Unlike `SimplexPaymaster`, which correctly sources token/USD prices from Chainlink with staleness checks [8](#0-7) , and unlike Simplex's own pool-based pricing which at least applies an optional `referencePrice`/`maxDeviationBps` guard [9](#0-8) , `BidManager`'s bid-ranking path applies no reference-price sanity check at all against the spot quote it uses to select which solver gets executed.

### Impact Explanation
This directly parallels the reported bug class ("Using Uniswap spot price is subject to manipulation") applied to a critical protocol action: selecting which solver's fill gets executed and settled on behalf of the order placer. A successful manipulation causes the order placer (or anyone relying on `executeBest`/`resumeBest`) to receive a fill worth materially less than a legitimate available bid — a concrete value-theft/loss scenario for users of the autopilot execution path, which the docs explicitly promote as the "batteries-included" recommended flow.

### Likelihood Explanation
Likelihood is High: submitting a bid is permissionless (any solver can call `submitBid`), the attacker fully controls which output token/pool is used to price its own bid, and manipulating a thin-liquidity pool's spot price within one transaction is a well-known, cheap, flash-loan-enabled technique. No staleness/TWAP/deviation defenses exist on this specific pricing path, unlike other pricing surfaces in the same codebase (SimplexPaymaster's Chainlink oracle, Simplex's `checkPriceGuard`).

### Recommendation
Do not rank or select solver bids using a live single-block spot/quoter price. Either:
- Require bid outputs to be restricted to stable/whitelisted tokens for autopilot ranking, or
- Price non-stable outputs via a manipulation-resistant source (Chainlink, a TWAP over multiple blocks, or the same `referencePrice`/`maxDeviationBps` guard Simplex already implements) before comparing `computeOutputsUsdValue` results, rejecting/discounting bids whose implied price deviates materially from the reference, mirroring `checkPriceGuard` used elsewhere in the codebase.

### Proof of Concept
1. Order placer creates an order via `executeBest` requesting mixed non-stable outputs (or attacker crafts an order whose outputs include a token attacker chooses).
2. Legitimate Solver A bids fairly, offering output tokens genuinely worth $X via deep, unmanipulated liquidity.
3. Attacker Solver B bids using a thin-liquidity token T that it also holds a pool for. In the same block, B (or an accomplice) flash-loans and swaps into pool T to spike its spot price.
4. `computeOutputsUsdValue`/`quoteTokenToUsdc` for B's bid reads the manipulated pool via `findBestProtocolWithAmountIn`, computing a USD value > $X even though B's actual token amount is worth far less at the true price.
5. `sortMixedOutputs` ranks B's bid above A's; `selectAndExecuteBest` simulates and executes B's bid.
6. Attacker reverses the pool manipulation after execution; the order placer is left with a fill worth substantially less than Solver A's legitimate offer, which was never selected.

### Citations

**File:** sdk/packages/sdk/src/utils/swap.ts (L1228-1244)
```typescript
	async findBestProtocolWithAmountIn(
		client: PublicClient,
		tokenIn: HexString,
		tokenOut: HexString,
		amountIn: bigint,
		evmChainID: string,
		options?: {
			selectedProtocol?: "v2" | "v3" | "v4"
			generateCalldata?: boolean
			recipient?: HexString
		},
	): Promise<{
		protocol: "v2" | "v3" | "v4" | null
		amountOut: bigint
		fee?: number
		transactions?: Transaction[]
	}> {
```

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

**File:** sdk/packages/sdk/src/protocols/intents/BidManager.ts (L588-642)
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
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/IntentGateway.ts (L609-628)
```typescript
	async *resumeBest(order: Order, options: ResumeIntentOrderOptions): AsyncGenerator<IntentOrderStatusUpdate, void> {
		const gen = this.resume(order, options)
		try {
			let input: SelectBidResult | undefined
			while (true) {
				const { value, done } = await gen.next(input)
				input = undefined
				if (done) break

				yield value
				if (value.status === "BIDS_RECEIVED") {
					input = await this.autoSelect(order, value.bids)
				}
			}
		} finally {
			// Propagate early teardown (consumer break / `.return()`) into the
			// underlying resume() generator so the executor stops polling.
			await gen.return()
		}
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/IntentGateway.ts (L642-653)
```typescript
	private async autoSelect(order: Order, bids: Bid[]): Promise<SelectBidResult | undefined> {
		try {
			return await this.selectAndExecuteBest(order, bids)
		} catch (err) {
			console.warn(
				`[IntentGateway] autoSelect: bid selection failed this round, continuing to poll: ${
					err instanceof Error ? err.message : String(err)
				}`,
			)
			return undefined
		}
	}
```

**File:** evm/src/utils/SimplexPaymaster.sol (L653-676)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }

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
