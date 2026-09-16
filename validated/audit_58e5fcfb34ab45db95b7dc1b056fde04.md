Confirmed: `LiquidityPool.buyRate`/`sellRate` (depth-weighted merges of the phantom price snapshots) are the *default* pricing source for real, fund-moving orders — `IndexedRateIntentQuoteStrategy.quote` and `IntentGateway.quoteIntent` use them to compute `amountIn`/`amountOut` for actual `IntentGatewayV2`/`IntentGatewayV3` orders [1](#0-0) , and this is documented as the default, fallback-free quoting strategy [2](#0-1) . This confirms the manipulated median genuinely has fund impact: it prices real orders, not just informational display.

### Title
Whale-solver phantom-bid price manipulation lets a single funded solver set the published pool rate that prices real intents - (File: `sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts`)

### Summary
Hyperbridge's Intent Gateway prices real, fund-moving orders (via `quoteIntent`'s default `indexed_rates` strategy) from `LiquidityPool.buyRate`/`sellRate`, which are depth-weighted aggregates of per-chain `PoolChainLiquidity.rate` samples. Each chain sample comes from `weightedMedian` over phantom-bid quotes, weighted by each solver's on-chain balance of the leg's output token. Because `weightedMedian` is documented and implemented as a **selection, not a blend**, any single unprivileged solver who accumulates slightly over half of the total weight for a leg sets the published rate to their own arbitrarily-chosen quote verbatim — this is analogous to the Numoen finding's core observation that an economic mechanism whose accepted parameter is a function of participants' self-interested inputs (and here, participants' capital size) creates exploitable MEV/economic games rather than a robust market price.

### Finding Description
`aggregatePhantomBids` collects every solver's phantom bid for an order leg, weights each quote by the solver's deliverable inventory (`getBalance`), drops zero-weight quotes, and picks the price with `weightedMedian` [3](#0-2) . `weightedMedian` walks weight-sorted entries and returns the **exact price of the first entry whose cumulative weight crosses half the total weight** [4](#0-3) . This is explicitly acknowledged in the codebase's own documentation: "a solver holding over half the leg's weight sets the published rate verbatim" [5](#0-4)  and "a solver holding over half the leg's weight sets the published price verbatim, and inventory in the wrong token buys no influence on that leg" [6](#0-5) .

Because a phantom bid commits no capital — it is only a signed quote, not a fill (the flow docs confirm "a probe commits no capital, so it passes a `null` budget and prices the whole input" [7](#0-6) ) — the only cost to a would-be manipulator is temporarily holding (not spending) enough of the output token on the destination chain to exceed 50% of the honest bidders' combined balance for that specific token/leg, then submitting one bid with an arbitrary quote. `weightedMedian`'s own test suite documents this failure mode directly: "the high-liquidity solver pulls the median to its price" even against far-off competing quotes [8](#0-7) .

That per-chain rate then feeds `updateLiquidityPools`, which merges chain samples into `LiquidityPool.sellRate`/`buyRate` via a depth-weighted mean (`weightedRate`) [9](#0-8) , and those pool rates are the default source `IntentGateway.quoteIntent` uses to size real orders' `amountIn`/`amountOut` with no fallback to another price source [2](#0-1) , [1](#0-0) .

### Impact Explanation
An attacker who temporarily concentrates >50% of the destination-chain balance of a targeted output token (e.g. via a flash-loan-funded wallet, or simply parking existing capital before a bid window closes) can submit a single phantom bid quoting an extreme price for that leg. This becomes the exact `medianPrice` for that chain/leg, skews the pool's depth-weighted `sellRate`/`buyRate`, and is then used verbatim by `quoteIntent` to construct real orders' input/output amounts — letting the attacker (or an accomplice acting as solver on the real order) extract value from users who place orders priced off the manipulated rate, or from LPs whose liquidity gets mis-quoted against. This is a permissionless, single-transaction-class economic attack (an unprivileged intent-gateway participant / solver) that can produce real fund extraction through mispriced fills, matching the "economical games that can be played to gain MEV" bug class from the source report, where a design that lets self-interested capital dictate the trusted market parameter creates exploitable, non-atomic MEV.

### Likelihood Explanation
Moderate. The attack requires no privileged role — any address can become a delegated "solver" and submit phantom bids — and only requires transient capital concentration in one output token on one chain for the duration of a bid window (documented default ~100 blocks, per `phantom_bid_window_exhausted_fires_once_for_the_active_order`). The system's own internal documentation repeatedly and explicitly calls out this exact "whale sets the rate verbatim" property as expected behavior rather than as a defended-against attack, indicating no additional caps (e.g., a maximum weight share per solver, or blending instead of selecting) currently constrain it.

### Recommendation
Cap any single solver's contribution to a leg's weighted-median weight (e.g., clamp weight at some fraction of total weight before computing the median), or replace the selection-based `weightedMedian` with a blended/interpolated weighted statistic that cannot be forced to equal one participant's arbitrary quote regardless of size. Additionally, consider requiring committed collateral or a fill-simulation guarantee behind a phantom bid before it is allowed to move published prices used for real order sizing, and/or bound how much a single window's snapshot may move `LiquidityPool.buyRate`/`sellRate` versus the prior rate.

### Proof of Concept
1. Identify a phantom-order leg whose output token has thin honest solver inventory on a destination chain (small `sellDepth`/`buyDepth` reported by `PoolChainLiquidity`).
2. Acquire (via purchase, flash loan on a chain that supports it, or existing treasury) enough of that output token to exceed 50% of the combined honest solver balance for that token on that chain.
3. Get EIP-7702 delegated to a `SolverAccount` for that chain (a normal, permissionless solver onboarding step) and submit one phantom bid quoting an arbitrary favorable output amount for the targeted leg before `PhantomBidWindowExhausted` fires.
4. `aggregatePhantomBids` weights this quote above 50% of total leg weight; `weightedMedian` returns it verbatim as `medianPrice` [4](#0-3) .
5. `updateLiquidityPools` folds this into `LiquidityPool.sellRate`/`buyRate`; a subsequent `quoteIntent` call for a real order in that pair returns `amountIn`/`amountOut` computed off the manipulated rate [1](#0-0) , letting the attacker's real fill (or a colluding solver's fill) extract value from the mispriced order.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts (L44-77)
```typescript
	async quote(
		params: QuoteIntentParams,
		source: IntentQuoteChainContext,
		destination: IntentQuoteChainContext,
	): Promise<IndexedRateQuoteIntentResult> {
		validateQuoteParams(params)
		const sourceConfig = getConfigByStateMachineId(source.stateMachineId)
		const destinationConfig = getConfigByStateMachineId(destination.stateMachineId)
		if (!sourceConfig) throw new UnsupportedLiquidityChainError(source.stateMachineId)
		if (!destinationConfig) throw new UnsupportedLiquidityChainError(destination.stateMachineId)

		const tokenIn = this.resolveAsset(sourceConfig.stateMachineId, params.tokenIn)
		const tokenOut = this.resolveAsset(destinationConfig.stateMachineId, params.tokenOut)
		const [protocolFeeBps, rates] = await Promise.all([
			readProtocolFeeBps(this.chainConfigService, source),
			new LiquidityEngine(this.getQueryClient()).getBuyAndSellRates({
				sourceChain: sourceConfig.stateMachineId,
				destinationChain: destinationConfig.stateMachineId,
				tokenInSymbol: tokenIn.symbol,
				tokenOutSymbol: tokenOut.symbol,
			}),
		])
		if (!rates) {
			throw new IndexedRateUnavailableError({
				source: sourceConfig.stateMachineId,
				destination: destinationConfig.stateMachineId,
				tokenIn: tokenIn.symbol,
				tokenOut: tokenOut.symbol,
			})
		}

		const selectedRate = selectIndexedRate(rates, tokenIn.symbol, tokenOut.symbol)
		return quoteWithIndexedRate(params, tokenIn, tokenOut, selectedRate, rates, protocolFeeBps)
	}
```

**File:** sdk/packages/sdk/docs/ai/decisions/2026-08-25-intent-quotes-default-to-directional-indexed-rates-without.md (L1-9)
```markdown
# 2026-08-25 — Intent quotes default to directional indexed rates without fallback

Chosen: `quoteIntent` defaults to an `indexed_rates` strategy that selects the depth-weighted aggregate `LiquidityPool.buyRate` for base-to-quote orders and `sellRate` for quote-to-base orders. Source and destination chains resolve the configured token deployments; raw amounts are calculated from the indexer's 18-decimal whole-token pool rate and both tokens' configured decimals. A missing directional rate is an error.

Alternatives considered:

- **Keep defaulting to the legacy directional Phantom snapshot.** Rejected: those snapshots resolve through a canonical Base market and do not use the pair-centric pool rate, so quotes can disagree with the indexer's current market.
- **Quote directly from one source/destination pair of `PoolChainLiquidity` rows.** Rejected: those rows are inputs to the indexer's pool price. `LiquidityPool.buyRate` and `sellRate` are the maintained depth-weighted merge of fresh chain samples and are the intended market-level quote.
- **Silently fall back to Phantom or Uniswap when a rate is absent.** Rejected: an order would be priced from a different market than the caller requested, hiding stale or incomplete indexer coverage and producing another unfillable quote.
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L709-723)
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
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1523-1551)
```typescript
	if (quotesByLeg.size === 0) return null

	// Each leg reports a single price: the liquidity-weighted median of the quotes for that leg.
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
	const legs = [...quotesByLeg.entries()]
		.sort(([a], [b]) => a - b)
		.flatMap(([legIndex, { outputToken, quotes, bidders }]) => {
			// quotes and bidders are pushed in lockstep above, so the same predicate keeps them aligned.
			const backedQuotes = quotes.filter((quote) => quote.weight > 0n)
			const backedBidders = bidders.filter((bidder) => bidder.weight > 0n)
			if (backedQuotes.length === 0) {
				logger?.warn(
					{ commitment, chain, legIndex, outputToken, quotes: quotes.length },
					"Dropping phantom leg: no bidder holds the output token on this chain, so no quote is backed",
				)
				return []
			}

			const medianPrice = weightedMedian(backedQuotes)
```

**File:** sdk/packages/simplex/docs/ai/flows/phantom-probe-curve-value-published-price.md (L19-21)
```markdown
- **`sizeOrder`'s exposure outputs are unused here.** `cappedByPair` and `capFractionByPair` ration
  real fills; a probe commits no capital, so it passes a `null` budget and prices the whole input.
  Only `legNotionals` is consumed, as the rate sample point. See Decisions.md.
```

**File:** sdk/packages/simplex/docs/ai/flows/phantom-probe-curve-value-published-price.md (L40-42)
```markdown
A quote's weight in that median is the solver's balance of **that leg's output token on the
destination chain** — so a solver holding over half the leg's weight sets the published price
verbatim, and inventory in the wrong token buys no influence on that leg.
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

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L15-23)
```markdown
4. `updateLiquidityPools` (`src/services/liquidityPool.service.ts`) turns those per-leg medians into pool rows. `resolvePoolLeg` maps a leg's tokens to a pool id and direction via the token registry, and the sample's rate is

   ```
   medianPrice * 10 ** (18 - outDecimals) * 10 ** inDecimals / standardAmount
   ```

   i.e. the quote renormalized from the probe size back to one whole input token. This holds for any standard amount the pallet configures; it collapses to `medianPrice * scale` when the probe is exactly one unit. Multiplications happen before the division, so only the last step truncates, by under one unit of 1e18 and downward.

5. Chain rows (`PoolChainLiquidity`, one per pool/chain/direction) are merged into the pool's single `sellRate`/`buyRate` by `weightedRate` — a depth-weighted **mean**, which unlike the median in step 3 does produce values no filler quoted. Samples older than `MAX_SAMPLE_AGE_BLOCKS` are excluded unless every sample is stale.
```
