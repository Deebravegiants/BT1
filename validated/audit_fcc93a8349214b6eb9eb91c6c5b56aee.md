Now I have a clear reachable path: an unprivileged intent solver's phantom bid directly determines the published price used by both the `PhantomSnapshotIntentQuoteStrategy` (SDK quote strategy) and, via the indexer, `LiquidityPool.buyRate`/`sellRate`, which `IntentGateway.quoteIntent`'s `indexed_rates` strategy uses to size real orders (`amountIn`/`amountOut`). This is the BonqDAO analog: a self-reported/attacker-controlled price feed (here, a solver's own quoted output, weighted by that same solver's self-reported/self-controlled inventory) becomes the "oracle" price consumed downstream to price real value transfers — same root-cause shape as BonqDAO's oracle-quote manipulation feeding a lending/liquidation calculation.

### Title
Phantom-order price oracle is manipulable by a single self-funded solver, corrupting real order quotes - ([File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts])

### Summary
The Hyperbridge intents system derives a published market price for a token pair (`PhantomOrderPriceSnapshotV2` → `LiquidityPool.sellRate`/`buyRate`) entirely from unprivileged solver bids on "phantom" (non-real, no-capital) orders. A quote's weight is the bidding solver's own on-chain token balance, and `weightedMedian` is a *selection*, not a blend — so a solver holding just over half the weight for a leg can set the published price to any value it quotes, verbatim. This manipulated price is then consumed by real users' order pricing (`IntentGateway.quoteIntent` with the `indexed_rates` / `phantom_snapshot` strategies), directly determining `amountIn`/`amountOut` for real value transfers.

### Finding Description
`aggregatePhantomBids` in [1](#0-0)  weights each solver's quote for a phantom-order leg by "the solver's inventory in THAT leg's output token on the destination chain" — a balance the solver fully controls and can inflate cheaply (buy the output token, or use a wash-traded/self-owned Uniswap V4 position) since a phantom order commits no capital on either side.

`weightedMedian` at [2](#0-1)  then picks one bidder's exact quoted integer as the published price whenever that bidder's weight is ≥ half the total — this is explicitly documented and tested behavior ("weights quotes by balance — the high-liquidity solver pulls the median to its price", [3](#0-2) ).

The resulting `medianPrice` is written into `PhantomOrderPriceSnapshotV2` and folded by the indexer into the pool's `sellRate`/`buyRate` via a depth-weighted mean across chains (`weightedRate` / `mergeChainRowsIntoPool`), [4](#0-3)  — but a single dominant chain sample still dominates that mean since depth (again the solver's own balance) is the weight.

That pool rate is not merely informational: `IntentGateway.quoteIntent`'s default `indexed_rates` strategy prices real orders directly from `LiquidityPool.buyRate`/`sellRate` ( [5](#0-4) ), and the `phantom_snapshot` strategy computes `amountOut = netAmountIn * snapshot.medianPrice / snapshot.standardAmount` directly from the manipulated snapshot ( [6](#0-5) ). A user or automated flow (e.g., `executeBest`) that trusts this quote to size a real cross-chain order — escrowing `amountIn` and expecting `amountOut` — is now pricing real value transfer off a number one uncapitalized solver set unilaterally, exactly analogous to BonqDAO's attacker-submitted oracle price driving a real liquidation/mint calculation.

### Impact Explanation
An unprivileged solver (no special role, no capital requirement beyond the queried leg's output token) can publish an arbitrary exchange rate for a pair. Any real order — placed by a user or an automated agent — that is priced via `quoteIntent`'s `indexed_rates` or `phantom_snapshot` strategy inherits that manipulated rate, causing the placer to escrow too much or receive/expect too little relative to true market value, i.e., a value-extraction/fund-loss vector for the counterparty who fills at the corrupted quote, or for the user who signs an order sized from a bad quote and gets a worse fill than the real market. This matches the severity class of BonqDAO (oracle-driven mispricing directly causing loss), though the loss is bounded to the manipulated pair/quote rather than an unbacked mint.

### Likelihood Explanation
No privileged access, governance, or protocol bug is required — only enough capital in the destination-chain output token (or a self-controlled Uniswap V4 position) to exceed half the weight of the surviving bids in a bid window, which the code and tests explicitly acknowledge as achievable ("a solver holding over half the leg's weight sets the published price verbatim", [7](#0-6) ). Thin pairs (new tokens, low-liquidity chains) are the easiest targets, and phantom orders exist specifically to be low-cost, capital-free probes.

### Recommendation
Do not let a single solver's self-reported/self-controlled inventory both set weight and be gamed as the price selector. Consider: capping any single solver's weight contribution per leg/window (e.g., a percentile cap well below 50%), requiring multiple independent solvers above a minimum bidder count before a snapshot is published, cross-checking the phantom price against an independent reference (e.g., bounded deviation from a DEX TWAP as already done for `referencePrice`/`maxDeviationBps` in `pricing.mdx`), and/or requiring real-fill volume (VWAP via `recordSpread`) rather than zero-capital phantom bids to move the published rate that real orders are quoted from.

### Proof of Concept
1. Attacker controls solver address `S` and funds it with the destination-chain output token for pair (`tokenA`,`tokenB`) such that its balance exceeds the combined balance of all other bidding solvers for that leg.
2. During a phantom order's bid window, `S` submits a signed bid quoting an extreme `amount` for the leg (e.g., far above or below the true market rate) via `fillOrder`/ERC-7821 batch, as covered by `isVerifiedSolverBid`.
3. `PhantomBidWindowExhausted` fires; `aggregatePhantomBids` computes weight for `S`'s quote as its full output-token balance, exceeding 50% of total leg weight; `weightedMedian` returns `S`'s exact quoted price ( [2](#0-1) ).
4. `handlePhantomOrderPrices` persists this as `PhantomOrderPriceSnapshotV2.medianPrice` and `updateLiquidityPools` folds it into `LiquidityPool.sellRate`/`buyRate` ( [8](#0-7) ).
5. A victim calls `IntentGateway.quoteIntent` (default `indexed_rates` strategy) or `PhantomSnapshotIntentQuoteStrategy.quote`, receiving `amountIn`/`amountOut` computed from the manipulated rate, and places/fills a real order at that corrupted price.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L709-724)
```typescript
export function weightedMedian(entries: { price: bigint; weight: bigint }[]): bigint {
	const sorted = [...entries].sort((a, b) => (a.price < b.price ? -1 : a.price > b.price ? 1 : 0))
	const totalWeight = sorted.reduce((acc, e) => (e.weight > 0n ? acc + e.weight : acc), 0n)

	if (totalWeight === 0n) {
		return sorted[Math.floor(sorted.length / 2)].price
	}

	let cumulative = 0n
	for (const entry of sorted) {
		if (entry.weight <= 0n) continue
		cumulative += entry.weight
		if (cumulative * 2n >= totalWeight) return entry.price
	}
	return sorted[sorted.length - 1].price
}
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1526-1536)
```typescript
	// lowestPrice and highestPrice carry that same value rather than the raw min/max of the bid set,
	// so consumers cannot read an outlier bid as if it were a tradeable bound.
	//
	// A quote's weight is the solver's inventory in THAT leg's output token on the destination
	// chain, so a zero-weight quote is one its solver cannot deliver at any price. Those are
	// dropped outright rather than merely down-weighted: they must not reach weightedMedian (with
	// nothing to weight by it picks a quote by position, letting whoever quotes the extreme set the
	// rate on zero capital), and they must not reach bidCount or `bidders`, where they would inflate
	// the solver count behind a price and mint zero-capacity PoolBidder/PoolRoute rows downstream.
	// A leg left with no backed quote at all is therefore absent entirely, exactly as if nobody had
	// quoted it — no snapshot, and its depth zeroes out downstream.
```

**File:** sdk/packages/sdk/src/tests/phantomAggregation.test.ts (L190-198)
```typescript
	it("weights quotes by balance — the high-liquidity solver pulls the median to its price", () => {
		const quotes = [
			{ price: 100n, weight: 1n },
			{ price: 200n, weight: 1n },
			{ price: 300n, weight: 100n },
		]
		// Total weight 102; cumulative reaches half (>=51) only at price 300.
		expect(weightedMedian(quotes)).toBe(300n)
	})
```

**File:** sdk/packages/indexer/src/services/liquidityPool.service.ts (L470-496)
```typescript
function mergeChainRowsIntoPool(pool: LiquidityPool, rows: PoolChainLiquidity[], referenceBlock: bigint): void {
	for (const direction of [SELL, BUY]) {
		const directionRows = rows.filter((row) => row.direction === direction)
		if (directionRows.length === 0) continue

		// Blocks are processed in order, so the difference is non-negative in practice; a row
		// from a "future" block would simply count as fresh, which is the right reading anyway.
		const fresh = directionRows.filter((row) => referenceBlock - row.lastUpdatedBlock <= MAX_SAMPLE_AGE_BLOCKS)
		const merged = fresh.length > 0 ? fresh : directionRows

		warnOnDivergentSample(pool.id, direction, merged)

		const depth = merged.reduce((acc, row) => acc + row.depth, 0n)
		const rate = weightedRate(merged)
		const bidCount = merged.reduce((acc, row) => acc + row.bidCount, 0)

		if (direction === SELL) {
			pool.sellRate = rate
			pool.sellDepth = depth
			pool.sellBidCount = bidCount
		} else {
			pool.buyRate = rate
			pool.buyDepth = depth
			pool.buyBidCount = bidCount
		}
	}
}
```

**File:** sdk/packages/sdk/docs/ai/changelog/2026-08-25-intent-quotes-use-aggregate-indexed-pool-rates-by-default.md (L1-5)
```markdown
# 2026-08-25 — Intent quotes use aggregate indexed pool rates by default

`IntentGateway.quoteIntent` now prices orders from the pair-centric indexer's depth-weighted aggregate `LiquidityPool.buyRate` and `sellRate`. Source and destination chains resolve the configured token deployments, while the quote converts the pool's whole-token rate into raw amounts with configured decimals, applies the source gateway protocol fee, and exposes the selected rate and timestamp in metadata. Reverse sell-rate reciprocals round up so quotes do not overpromise output. Phantom snapshot and Uniswap V4 pricing remain explicit compatibility strategies. Live sequential tests cover exact-input USDC to cNGN and exact-output cNGN to USDC across BSC and Base, including their different token decimal scales. The dead `binance.llamarpc.com` BSC default was replaced with `bsc-rpc.publicnode ... (truncated)

Files: `src/configs/chain.ts`, `src/protocols/intents/IntentGateway.ts`, `src/protocols/intents/LiquidityEngine.ts`, `src/protocols/intents/index.ts`, `src/protocols/intents/quote/index.ts`, `src/protocols/intents/quote/indexedRates.ts`, `src/protocols/intents/quote/types.ts`, `src/tests/sequential/intentGateway.test.ts`, `package.json`, `CHANGELOG.md`, `docs/ai/ChangeLog.md`, `docs/ai/Decisions.md`, `../../../docs/content/developers/sdk/api/intent-gateway.mdx`, `../../../docs/content/developers/evm/intent-gateway/placing-orders.mdx`.
```

**File:** sdk/packages/sdk/src/protocols/intents/quote/phantomSnapshot.ts (L88-94)
```typescript
		if (params.amountIn !== undefined) {
			const netAmountIn = deductProtocolFee(params.amountIn, protocolFeeBps)
			const amountOut = (netAmountIn * snapshot.medianPrice) / snapshot.standardAmount
			if (amountOut <= 0n) {
				throw new InvalidPhantomSnapshotError(snapshot.commitment, "quote rounds down to zero output")
			}
			return this.buildResult("EXACT_INPUT", params.amountIn, amountOut, protocolFeeBps, snapshot)
```

**File:** sdk/packages/indexer/src/handlers/events/substrateChains/handlePhantomOrderPrices.handler.ts (L208-235)
```typescript
		await PhantomOrderPriceSnapshotV2.create({
			id: `${commitment}-${blockNumber}-${leg.legIndex}`,
			commitment,
			legId: `${commitment}-${leg.legIndex}`,
			chain: phantom.chain,
			poolId: registered.resolved?.poolId,
			direction: registered.resolved?.direction,
			tokenA: registered.tokenA,
			tokenB: registered.tokenB,
			// Denormalized from the leg so a rate (medianPrice / standardAmount) is computable
			// from a single snapshot row without joining back to it.
			standardAmount: registered.standardAmount,
			blockNumber,
			lowestPrice: leg.lowestPrice,
			highestPrice: leg.highestPrice,
			medianPrice: leg.medianPrice,
			bidCount: leg.bidCount,
			snapshotTime,
		}).save()
	}

	await updateLiquidityPools({
		chain: phantom.chain,
		blockNumber,
		snapshotTime,
		legs: [...registeredByIndex.values()],
		priced: aggregate.legs,
	})
```
