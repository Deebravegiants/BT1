### Title
Uniswap V4 position weighting in phantom bid aggregation uses live spot price (`slot0`/`sqrtPriceX96`), letting a flash-loan price move inflate a solver's bid weight and force the published `LiquidityPool` rate - (File: `sdk/packages/sdk/src/protocols/intents/uniswap-v4-position.ts`)

### Summary
Hyperbridge's phantom-order price-discovery pipeline lets a solver declare a Uniswap V4 LP position as backing for its bid. The declared position's "withdrawable" value (used as the bid's weight in a weighted-median price selection) is computed with `getAmountsForLiquidity`, which prices the position using the pool's **live, instantaneous `sqrtPriceX96`** read straight off `slot0`/`StateView.getSlot0`, exactly the pattern flagged in the external `UNI_V3Validator` report. Because the weighted-median is a *selection*, not a blend, a solver whose (temporarily inflated) weight exceeds half the leg's total weight can force the published rate to be its own quoted price verbatim — and that rate is what `IntentGateway.quoteIntent`'s default `indexed_rates` strategy uses to price real, user-submitted intent orders.

### Finding Description
`getAmountsForLiquidity` in `sdk/packages/sdk/src/protocols/intents/uniswap-v4-position.ts` mirrors Uniswap's `LiquidityAmounts.getAmountsForLiquidity` and has the exact three-branch structure called out in the report (below/inside/above range), valuing a position purely off `sqrtPriceX96`: [1](#0-0) 

That `sqrtPriceX96` is read live from the pool's `slot0` via `StateView.getSlot0` inside `readV4Position`, with no TWAP or oracle fallback, defaulting to the chain head at read time: [2](#0-1) 

`positionAmountOfToken` (also in `uniswap-v4-position.ts`) feeds this spot-priced amount directly into a bid's weight during phantom bid aggregation: [3](#0-2) 

That weight is what backs the `weightedMedian` leg-price *selection* (not an average) — the documentation for this path is explicit that a solver above 50% of a leg's weight sets the published price verbatim: [4](#0-3) [5](#0-4) 

The resulting per-leg medians are turned into the pair-level `LiquidityPool.sellRate`/`buyRate` by `updateLiquidityPools`: [6](#0-5) 

Finally, `IntentGateway.quoteIntent` prices *real* orders (not just phantom probes) directly from this indexed `buyRate`/`sellRate` by default: [7](#0-6) 

An unprivileged solver can declare an owned Uniswap V4 position (`uniswapV4Positions`) in its phantom-bid `paymasterAndData`: [8](#0-7) 

Since the position is valued from the pool's *spot* price at read time (a variable-latency read after the bid window closes, and re-read again if it later fills a real order), a solver who takes out a flash loan to move `sqrtPriceX96` around the block the indexer/other-consumer reads state can transiently inflate (or deflate) the token amount their declared liquidity is "worth," directly inflating the weight assigned to their quote.

### Impact Explanation
Because the weighted-median is a selection (not a blend), a solver that captures majority weight on a leg via this manipulation sets the exact published `PhantomOrderPriceSnapshotV2`/`LiquidityPool` rate. Since real orders' `quoteIntent` calls consume this indexed rate by default with no other fallback, this can cause end users to construct and sign real IntentGatewayV2 orders priced off a manipulated rate, leading to a real economic loss (users receiving less output than the true market rate, or the manipulating solver's own quotes being unfairly favored in bid selection). This mirrors the medium-severity classification of the original `UNI_V3Validator` report: no direct fund-locking exploit, but a concretely exploitable price-manipulation vector reachable by any solver holding a small Uniswap V4 position and flash-loan capital.

### Likelihood Explanation
Medium. The attack requires: (1) the attacker/solver control (or borrow via flash loan) enough capital to move a chosen pool's spot price meaningfully; (2) their declared position sits in the tick range around the manipulated price so `positionAmountOfToken` reports an inflated amount; (3) timing the price move to coincide with whichever `blockTag`/"latest" read consumes it (phantom snapshot aggregation, or a later real-fill re-read of "declared and still owned" positions, per `LiquidityProviderBalanceV2`'s snapshot-reading doc). This timing dependency lowers reliability somewhat versus a single-transaction atomic exploit, but MEV-style bots routinely achieve this kind of block-level timing against public event triggers, and no code path bounds the read against a TWAP or reference price as a backstop.

### Recommendation
- Value declared Uniswap V4 positions with a time-weighted average price (or Uniswap's built-in oracle observations) rather than raw `slot0.sqrtPriceX96`, consistent with the `UNI_V3Validator` report's core recommendation.
- Alternatively, bound/clamp position-derived weight contributions the same way Simplex's own `[vault.uniswapV4]` funding path optionally does via `referencePrice`/`maxDeviationBps` price guards (currently optional and unused in the phantom-bid weighting path) — apply an equivalent mandatory deviation check before a declared position's valuation is allowed to influence bid weight or the published rate.
- Document this spot-price dependency explicitly wherever `positionAmountOfToken`/`getAmountsForLiquidity` are used for weighting or pricing, so downstream consumers of `LiquidityPool.buyRate`/`sellRate` know manipulation risk exists absent the guard.

### Proof of Concept
1. Solver S owns a small Uniswap V4 LP position P on pool `X/USDC`, positioned so it is out-of-range (or near the edge) under normal market price.
2. When a `PhantomOrderRegistered` event fires for that chain/pair, S submits a phantom bid declaring position P via `paymasterAndData` (`uniswapV4Positions: [tokenId]`), quoting an output amount favorable to S.
3. Shortly before the indexer's `handlePhantomOrderPrices` handler executes `aggregatePhantomBids` → `readV4Position` (which reads `slot0` at "latest"), S takes a flash loan and swaps in pool `X/USDC` to push `sqrtPriceX96` into P's tick range, inflating the token amount `positionAmountOfToken` reports for P.
4. S's declared-position weight is swept into `lpBalances`/leg weight (`sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts`), pushing S's quote above 50% of the leg's total weight.
5. `weightedMedian` returns S's exact quoted price verbatim as `PhantomOrderPriceSnapshotV2.medianPrice`; `updateLiquidityPools` folds it into `LiquidityPool.sellRate`/`buyRate`.
6. S repays the flash loan and restores the pool price.
7. Any subsequent `IntentGateway.quoteIntent` call for that pair (default `indexed_rates` strategy) prices real user orders off the now-skewed `LiquidityPool` rate until the next honest snapshot overwrites it, and/or S's own bids gain an unfair advantage in solver selection on future real orders for that pair.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/uniswap-v4-position.ts (L104-127)
```typescript
export function getAmountsForLiquidity(params: {
	sqrtPriceX96: bigint
	sqrtRatioAX96: bigint
	sqrtRatioBX96: bigint
	liquidity: bigint
}): { amount0: bigint; amount1: bigint } {
	let { sqrtRatioAX96, sqrtRatioBX96 } = params
	const { sqrtPriceX96, liquidity } = params
	if (sqrtRatioAX96 > sqrtRatioBX96) [sqrtRatioAX96, sqrtRatioBX96] = [sqrtRatioBX96, sqrtRatioAX96]

	const amount0For = (from: bigint, to: bigint) => (liquidity * Q96 * (to - from)) / to / from
	const amount1For = (from: bigint, to: bigint) => (liquidity * (to - from)) / Q96

	if (sqrtPriceX96 <= sqrtRatioAX96) {
		return { amount0: amount0For(sqrtRatioAX96, sqrtRatioBX96), amount1: 0n }
	}
	if (sqrtPriceX96 < sqrtRatioBX96) {
		return {
			amount0: amount0For(sqrtPriceX96, sqrtRatioBX96),
			amount1: amount1For(sqrtRatioAX96, sqrtPriceX96),
		}
	}
	return { amount0: 0n, amount1: amount1For(sqrtRatioAX96, sqrtRatioBX96) }
}
```

**File:** sdk/packages/sdk/src/protocols/intents/uniswap-v4-position.ts (L157-180)
```typescript
/**
 * How much of `outputToken` a position is currently worth. Zero when the token is not one of the
 * pool's currencies, or when the price has moved the position entirely onto the other side — both
 * ordinary outcomes, not errors.
 */
export function positionAmountOfToken(params: {
	info: PoolAndPositionInfo
	liquidity: bigint
	sqrtPriceX96: bigint
	outputToken: string
}): bigint {
	const { info, liquidity, sqrtPriceX96 } = params
	const outputToken = params.outputToken.toLowerCase()
	if (outputToken !== info.currency0 && outputToken !== info.currency1) return 0n
	if (liquidity <= 0n || sqrtPriceX96 <= 0n) return 0n

	const { amount0, amount1 } = getAmountsForLiquidity({
		sqrtPriceX96,
		sqrtRatioAX96: getSqrtRatioAtTick(info.tickLower),
		sqrtRatioBX96: getSqrtRatioAtTick(info.tickUpper),
		liquidity,
	})
	return outputToken === info.currency0 ? amount0 : amount1
}
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1070-1131)
```typescript
export async function readV4Position(params: {
	evmRpcUrl: string
	contracts: UniswapV4Contracts
	tokenId: bigint
	keccak: (hex: HexString) => HexString
	/** Block to read at; defaults to the chain head. */
	blockTag?: string
	logger?: AggregationLogger
}): Promise<V4PositionState | null> {
	const { evmRpcUrl, contracts, tokenId, keccak, blockTag = "latest", logger } = params
	const call = async (to: string, data: string): Promise<string | null> => {
		const result = await rpcCall(evmRpcUrl, {
			id: 1,
			jsonrpc: "2.0",
			method: "eth_call",
			params: [{ to, data }, blockTag],
		})
		if (result.result === "0x") return null
		if (typeof result.result !== "string") {
			throw new PhantomRpcError(`eth_call returned no result for ${to} on ${evmRpcUrl}`)
		}
		return result.result
	}

	const arg = uint256Arg(tokenId)
	const [ownerData, infoData, liquidityData] = await Promise.all([
		call(contracts.positionManager, `${SELECTOR_OWNER_OF}${arg}`),
		call(contracts.positionManager, `${SELECTOR_POOL_AND_POSITION_INFO}${arg}`),
		call(contracts.positionManager, `${SELECTOR_POSITION_LIQUIDITY}${arg}`),
	])
	// An empty ownerOf is a tokenId that was never minted or has been burned — a solver may name a
	// stale position, which is its problem and not ours.
	if (!ownerData) return null
	if (!infoData || !liquidityData) {
		logger?.warn(
			{ tokenId: tokenId.toString(), positionManager: contracts.positionManager },
			"Uniswap V4 position exists but its pool info or liquidity did not read back — check the configured PositionManager",
		)
		return null
	}

	const info = decodePoolAndPositionInfo(infoData)
	// The pool id is keccak of the PoolKey exactly as the chain returned it, so no re-encoding of
	// ours can disagree with the hash the pool was registered under.
	const slot0Data = await call(contracts.stateView, `${SELECTOR_GET_SLOT0}${keccak(info.poolKeyEncoded).slice(2)}`)
	// The position resolved, so its pool exists — an empty slot0 means the call went somewhere that
	// is not a StateView, i.e. a misconfigured address. Silence here is what let a wrong address
	// zero out every declared position indefinitely instead of failing where someone would see it.
	if (!slot0Data) {
		logger?.warn(
			{ tokenId: tokenId.toString(), stateView: contracts.stateView, evmRpcUrl },
			"Uniswap V4 slot0 read returned nothing for a live position — the configured StateView address is wrong",
		)
		return null
	}

	return {
		owner: `0x${ownerData.slice(-40)}`.toLowerCase(),
		info,
		liquidity: word(liquidityData, 0),
		sqrtPriceX96: word(slot0Data, 0),
	}
```

**File:** sdk/packages/simplex/docs/ai/flows/phantom-probe-curve-value-published-price.md (L40-42)
```markdown
A quote's weight in that median is the solver's balance of **that leg's output token on the
destination chain** — so a solver holding over half the leg's weight sets the published price
verbatim, and inventory in the wrong token buys no influence on that leg.
```

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L11-13)
```markdown
2. Per leg, a solver's quote is weighted by **its balance of that leg's OUTPUT token on the destination chain** — the inventory that actually backs the leg. Zero-weight quotes are dropped entirely, not down-weighted: they never reach the median, `bidCount`, or the bidder list. A leg where no bidder holds the output token is absent from the result, exactly as if nobody quoted it.

3. The leg's price is `weightedMedian` of the backed quotes — a **selection**, not a blend. It returns one bidder's exact integer, so a solver holding over half the leg's weight sets the published price verbatim, and the result can never be a value nobody quoted. `lowestPrice` and `highestPrice` are deliberately overwritten with the median so consumers cannot read an outlier bid as a tradeable bound.
```

**File:** sdk/packages/indexer/src/services/liquidityPool.service.ts (L256-279)
```typescript

		const quote = pricedByIndex.get(leg.legIndex)
		if (!quote) continue

		const scale = 10n ** BigInt(POOL_RATE_DECIMALS - resolved.outDecimals)
		let depth = 0n
		for (const bidder of quote.bidders) {
			const solver = bidder.solver.toLowerCase()
			const liquidity = bidder.weight * scale
			depth += liquidity
			entry.bidders.set(`${resolved.poolId}-${chain}-${resolved.direction}-${leg.tokenB}-${solver}`, {
				solver,
				liquidity,
				acceptedSources: bidder.acceptedSources,
				outputToken: leg.tokenB,
			})
		}
		entry.samples.push({
			rate: poolRateFromQuote(quote.medianPrice, resolved, leg.standardAmount),
			depth,
		})
		entry.bidCount += quote.bidCount
		entry.quoted = true
	}
```

**File:** sdk/packages/sdk/docs/ai/changelog/2026-08-25-intent-quotes-use-aggregate-indexed-pool-rates-by-default.md (L1-3)
```markdown
# 2026-08-25 — Intent quotes use aggregate indexed pool rates by default

`IntentGateway.quoteIntent` now prices orders from the pair-centric indexer's depth-weighted aggregate `LiquidityPool.buyRate` and `sellRate`. Source and destination chains resolve the configured token deployments, while the quote converts the pool's whole-token rate into raw amounts with configured decimals, applies the source gateway protocol fee, and exposes the selected rate and timestamp in metadata. Reverse sell-rate reciprocals round up so quotes do not overpromise output. Phantom snapshot and Uniswap V4 pricing remain explicit compatibility strategies. Live sequential tests cover exact-input USDC to cNGN and exact-output cNGN to USDC across BSC and Base, including their different token decimal scales. The dead `binance.llamarpc.com` BSC default was replaced with `bsc-rpc.publicnode ... (truncated)
```

**File:** sdk/packages/simplex/src/services/ContractInteractionService.ts (L857-864)
```typescript
			// Every phantom bid carries a declaration. The accepted sources are the chains this filler
			// is configured on, so a bid with none to declare says so explicitly ([]), rather than
			// leaving the field empty for consumers to read as "any chain".
			paymasterAndData: encodePhantomBidDeclaration({
				acceptedSourceChains,
				uniswapV4Positions: uniswapV4PositionIds?.map((id) => BigInt(id)),
			}),
		})
```
