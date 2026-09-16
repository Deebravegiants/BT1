Based on my research, I found a strong, concrete analog to the Open Oracle median-price report bug within this codebase's phantom-order price aggregation pipeline used by the Intent Gateway's liquidity pools.

### Title
Liquidity-weighted median price for phantom order legs can be set verbatim by a single dominant-inventory solver, with no dispersion signal, letting `quoteIntent` price real orders off a manipulable rate - ([File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts])

### Summary
`aggregatePhantomBids` prices every phantom-order leg by taking the `weightedMedian` of bidding solvers' quotes, weighted by each solver's inventory of the leg's output token [1](#0-0) . `weightedMedian` is a *selection*, not a blend: it returns one bidder's exact quoted integer once cumulative weight crosses half the total weight [2](#0-1) . This is functionally identical to the Open Oracle's median-of-reported-prices design flagged in the external report: the "official" published price is only as trustworthy as the assumption that no single reporter controls ≥50% of the weight behind it, and there is no computed dispersion/standard-deviation metric to warn consumers when that assumption breaks.

### Finding Description
A solver is any permissionless bidder in the phantom-order auction (an "intent solver" in the reachable-attacker list). Per leg, quote weight is the solver's own on-chain balance of the leg's output token, read live at aggregation time [3](#0-2) . The docs explicitly acknowledge the consequence: "a solver holding over half the leg's weight sets the published price verbatim, and the result can never be a value nobody quoted" [4](#0-3) . `lowestPrice`/`highestPrice` are then overwritten with that same median, deliberately destroying any signal a downstream consumer could use to see the true spread of quotes [5](#0-4) . The per-leg median is then renormalized into a per-chain rate (`poolRateFromQuote`) and merged into `LiquidityPool.sellRate`/`buyRate` via `weightedRate`, a depth-weighted mean across chains [6](#0-5) . Nowhere in this chain — leg median, chain sample, or cross-chain merge — is a standard deviation, variance, or confidence interval computed or exposed; the only anomaly detector (`warnOnDivergentSample`) only logs a warning at >5x divergence and still merges the sample anyway [7](#0-6) .

The resulting `sellRate`/`buyRate` is exactly the "trusted source" price that `IntentGateway.quoteIntent` uses by default to size real cross-chain orders — no fallback to another price source exists if this rate is stale or skewed [8](#0-7) [9](#0-8) .

### Impact Explanation
An intent solver that accumulates sufficient inventory in a leg's output token (or an attacker who briefly inflates a wallet's balance of that token during the bid window, since weight is read live from balance rather than a stake/reputation measure) can set the published `medianPrice` for that leg to any value it quotes, verbatim. Because the median/mean chain then feeds `LiquidityPool.sellRate`/`buyRate`, and `quoteIntent` prices real user orders directly from those rates with no alternate source, a manipulated rate can cause users to construct and place orders with mis-sized `amountIn`/`amountOut`, and can distort `queryAvailableLiquidity`/route depth reporting used to gauge fillability. Absent any published dispersion metric, downstream consumers (SDK callers, other solvers evaluating liquidity) have no signal that the "official" rate came from one dominant quoter versus consensus, unlike the Open Oracle's std-dev remediation the external report recommends.

### Likelihood Explanation
Likelihood is inventory-dependent: only a solver (or attacker) who can temporarily hold >50% of the destination-chain output-token weight during a bid window can move the median. This is realistic on thinly-bid pairs/chains (the docs note legs are dropped entirely when nobody holds the output token, implying low-liquidity legs are common), and the aggregation code explicitly documents this as an accepted, known property rather than a defended-against edge case, indicating it is not merely theoretical.

### Recommendation
Compute and expose a dispersion measure (e.g., weighted standard deviation, or the true min/max instead of overwriting them with the median) alongside `medianPrice`/`sellRate`/`buyRate` so that `quoteIntent` and other consumers can detect and reject (or discount) quotes derived from a single-dominant-quoter snapshot, mirroring the Open Oracle's standard-deviation remediation. Consider also weighting median-selection more conservatively (e.g., requiring a minimum number of distinct backing solvers, or capping any single solver's weight contribution) before trusting the leg price for real order pricing.

### Proof of Concept
1. A solver, `0xa`, is the only bidder (or holds >50% of destination inventory) for a thinly-traded leg, e.g., in the test fixture `leg(0, USDC, 660n, [{ solver: "0xa", weight: 100n, ... }])` [10](#0-9) .
2. `weightedMedian` returns `0xa`'s exact quoted price because its weight alone reaches half the total [11](#0-10) .
3. `updateLiquidityPools` writes this as `LiquidityPool.sellRate` with no dispersion metadata [12](#0-11) .
4. A subsequent user calling `quoteIntent` for that pair prices their order strictly from this `sellRate`, with no way to detect that it was set entirely by one solver's self-quoted price [9](#0-8) .

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L702-724)
```typescript
//
// Callers must not hand this an entry set whose weights are all zero: with nothing to weight by it
// can only pick a quote by position, and for an even-sized set that position is the upper of the
// two middles — so "the median" becomes "whoever quoted higher", settable by a solver holding no
// inventory at all. aggregatePhantomBids drops such legs instead of pricing them. The fallback
// below stays only so an unguarded caller gets a number rather than a crash; treat reaching it as
// a caller bug.
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

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1500-1513)
```typescript
				const entry = quotesByLeg.get(legIndex) ?? { outputToken: leg.outputToken, quotes: [], bidders: [] }
				entry.quotes.push({ price: leg.solverAmount, weight })
				entry.bidders.push({ solver: normalizedSolver as HexString, weight, acceptedSources })
				quotesByLeg.set(legIndex, entry)
			}

			// Full liquidity picture: every configured token on every supported chain. Swept once per
			// bid rather than per leg, since it measures the solver's whole inventory either way.
			lpBalances.push(
				...(await sweepSolverLiquidity(evmRpcUrls, yieldVaults, solver, getBalance, {
					chain,
					states: positions,
				})),
			)
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1525-1536)
```typescript
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
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1551-1562)
```typescript
			const medianPrice = weightedMedian(backedQuotes)
			return [
				{
					legIndex,
					outputToken,
					lowestPrice: medianPrice,
					highestPrice: medianPrice,
					medianPrice,
					bidCount: backedQuotes.length,
					bidders: backedBidders,
				},
			]
```

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L13-13)
```markdown
3. The leg's price is `weightedMedian` of the backed quotes — a **selection**, not a blend. It returns one bidder's exact integer, so a solver holding over half the leg's weight sets the published price verbatim, and the result can never be a value nobody quoted. `lowestPrice` and `highestPrice` are deliberately overwritten with the median so consumers cannot read an outlier bid as a tradeable bound.
```

**File:** sdk/packages/indexer/src/services/liquidityPool.service.ts (L161-170)
```typescript
// The one rate-merge policy: depth-weighted average, falling back to the unweighted mean when
// the whole sample set carries zero depth (so a price is still reported). Every merge in this
// file — collapsed legs, the cross-chain pool merge, and the divergence alarm's consensus —
// must agree on this, hence the single home.
function weightedRate(samples: { rate: bigint; depth: bigint }[]): bigint {
	const depth = samples.reduce((acc, sample) => acc + sample.depth, 0n)
	return depth > 0n
		? samples.reduce((acc, sample) => acc + sample.rate * sample.depth, 0n) / depth
		: samples.reduce((acc, sample) => acc + sample.rate, 0n) / BigInt(samples.length)
}
```

**File:** sdk/packages/indexer/src/services/liquidityPool.service.ts (L404-433)
```typescript
		for (const [direction, entry] of directions) {
			const id = `${poolId}-${chain}-${direction}`
			if (entry.quoted) {
				const rate = weightedRate(entry.samples)
				const { depth, unrestrictedDepth, unrestrictedBidCount } = bidderDepths([...entry.bidders.values()])
				const row = await PoolChainLiquidity.get(id)
				if (row) {
					row.rate = rate
					row.depth = depth
					row.bidCount = entry.bidCount
					row.unrestrictedDepth = unrestrictedDepth
					row.unrestrictedBidCount = unrestrictedBidCount
					row.lastUpdatedBlock = blockNumber
					row.lastUpdatedAt = snapshotTime
					await row.save()
				} else {
					await PoolChainLiquidity.create({
						id,
						poolId,
						chain,
						direction,
						rate,
						depth,
						bidCount: entry.bidCount,
						unrestrictedDepth,
						unrestrictedBidCount,
						lastUpdatedBlock: blockNumber,
						lastUpdatedAt: snapshotTime,
					}).save()
				}
```

**File:** sdk/packages/indexer/src/services/liquidityPool.service.ts (L498-518)
```typescript
// A pair prices identically across chains, so one sample far off the others' consensus almost
// certainly means a wrong registry decimals entry poisoning that chain's normalization — worth an
// alarm, but the sample still merges: this cannot tell a bad entry from a genuinely dislocated
// market, and silently dropping data would hide the bug the alarm exists to surface.
function warnOnDivergentSample(
	poolId: string,
	direction: string,
	rows: { chain: string; rate: bigint; depth: bigint }[],
): void {
	if (rows.length < 2) return
	for (const row of rows) {
		const consensus = weightedRate(rows.filter((other) => other !== row))
		if (consensus === 0n) continue
		if (row.rate > consensus * 5n || row.rate * 5n < consensus) {
			logger.warn(
				{ poolId, direction, chain: row.chain, rate: row.rate.toString(), consensus: consensus.toString() },
				"Pool chain sample diverges >5x from the other chains — check the token registry decimals",
			)
		}
	}
}
```

**File:** docs/content/developers/sdk/api/intent-gateway.mdx (L178-180)
```text
Quotes an intent from the latest aggregate pool buy or sell rate published by the indexer. The pool rate is depth-weighted from fresh chain samples. Pass token addresses directly—the SDK resolves their configured symbols and decimals. No `strategy` option is needed for indexed-rate quotes.

Indexed-rate quotes require an attached Hyperbridge indexer client. There is no automatic fallback to another price source.
```

**File:** sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts (L146-164)
```typescript
function quoteWithIndexedRate(
	params: QuoteIntentParams,
	tokenIn: ResolvedQuoteAsset,
	tokenOut: ResolvedQuoteAsset,
	selectedRate: SelectedIndexedRate,
	rates: BuyAndSellRates,
	protocolFeeBps: bigint,
): IndexedRateQuoteIntentResult {
	const inputUnit = 10n ** BigInt(tokenIn.decimals)
	const outputUnit = 10n ** BigInt(tokenOut.decimals)
	if (params.amountIn !== undefined) {
		const netAmountIn = deductProtocolFee(params.amountIn, protocolFeeBps)
		const amountOut =
			selectedRate.side === "buy"
				? (netAmountIn * selectedRate.scaledRate * outputUnit) / (inputUnit * INDEXED_RATE_SCALE)
				: (netAmountIn * outputUnit * INDEXED_RATE_SCALE) / (inputUnit * selectedRate.scaledRate)
		if (amountOut <= 0n) throw new InvalidIndexedRateError("quote rounds down to zero output")
		return buildResult("EXACT_INPUT", params.amountIn, amountOut, selectedRate, rates, protocolFeeBps)
	}
```

**File:** sdk/packages/indexer/src/handlers/events/substrateChains/__tests__/phantomOrder.handlers.test.ts (L426-437)
```typescript
	it("merges both directions of a pair into one pool with sell and buy sides", async () => {
		await register([pair(CNGN, USDC, 1_000_000n), pair(USDC, CNGN, 1_000_000n)])
		aggregatePhantomBids.mockResolvedValue({
			legs: [
				// cNGN -> USDC is the SELL side (cNGN sorts first), USDC -> cNGN the BUY side.
				leg(0, USDC, 660n, [{ solver: "0xa", weight: 100n, acceptedSources: null }]),
				leg(1, CNGN, 1_500n, [{ solver: "0xa", weight: 40n, acceptedSources: null }]),
			],
			lpBalances: [],
			positions: [],
			solvers: [],
		})
```
