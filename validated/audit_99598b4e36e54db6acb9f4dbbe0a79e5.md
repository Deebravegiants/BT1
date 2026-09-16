### Title
Solver-controlled weighted-median price feed lets a single bidder set the published intent exchange rate with no deviation guard, enabling oracle-style manipulation of user quotes and fund drain — ([File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts])

### Summary
Blizz Finance was drained because attackers could push a Chainlink-derived price to a level ($0.1) that was accepted uncritically by the lending logic, letting them over-borrow against nearly-worthless collateral before the protocol's timelocked defenses could react. Hyperbridge's Simplex/IntentGateway stack has an analogous single point of price truth: the indexer's `weightedMedian` of solver bids, which becomes `LiquidityPool.buyRate`/`sellRate` and is consumed, unguarded, by `quoteIntent()`'s default `indexed_rates` strategy to construct the raw token amounts of real, fund-moving orders.

### Finding Description
`aggregatePhantomBids` weights each solver's quote for a leg purely by that solver's current balance of the leg's output token on the destination chain, then selects the published price via `weightedMedian`: [1](#0-0) 

The function and its own inline documentation acknowledge that this is winner-take-all, not a blended average: a solver holding more than half of a leg's weighted liquidity sets the price verbatim, with no bound relative to any other reference: [2](#0-1) 

That per-leg median is fed straight into `updateLiquidityPools`, which merges it into the pool's `sellRate`/`buyRate` via a depth-weighted mean (`weightedRate`) across chains — still with no sanity or deviation ceiling on the underlying per-chain rate itself, only a post-hoc, non-blocking `warnOnDivergentSample` log: [3](#0-2) 

`LiquidityPool.buyRate`/`sellRate` are then the sole price source for `IntentGateway.quoteIntent()`'s default `indexed_rates` strategy, which the SDK documents explicitly has **no automatic fallback to another price source**: [4](#0-3) 

The strategy's implementation (`IndexedRateIntentQuoteStrategy.quote` / `quoteWithIndexedRate`) takes the rate as-is and directly computes `amountIn`/`amountOut` used to build the escrowed `order.inputs`/`output.assets`: [5](#0-4) 

No component in this chain — `weightedMedian`, `weightedRate`, `mergeChainRowsIntoPool`, or `IndexedRateIntentQuoteStrategy` — bounds how far a single dominant bidder can move the published rate from its true market value, and there is no circuit breaker analogous to the opt-in, solver-only `referencePrice`/`maxDeviationBps` guard that exists solely for Uniswap V4 venue pricing (which protects the *solver*, not order placers, and is off by default): [6](#0-5) 

### Impact Explanation
An unprivileged intent solver is a permitted, unprivileged actor in this system (explicitly listed as in-scope: "intent solver or bandwidth purchaser"). By temporarily acquiring a large balance of a leg's output token on the destination chain (the only input to bid weight) and submitting the sole or dominant-weight bid during a phantom bid window, a solver can force `LiquidityPool.buyRate`/`sellRate` to an arbitrary value. Any counterparty calling `quoteIntent()` — the SDK's default, fallback-free pricing path — receives a corrupted rate and constructs a real, signed, fund-escrowing `IntentGatewayV2` order from it. The same or a colluding solver can then fill that mispriced order, capturing the victim's over-payment or under-delivery. This is a direct analog of Blizz Finance's core failure mode: an unchecked external price feed, consumed without sanity bounds, drives a fund-moving decision, and the entity that can influence the feed profits at the expense of anyone trusting it — concrete theft of counterparty funds via price manipulation, satisfying the "concrete theft" acceptance bar.

### Likelihood Explanation
Likelihood is High: no privileged role is required, the balance-based weighting can be satisfied transiently, `weightedMedian`'s winner-take-all behavior at >50% weight is an acknowledged, tested property of the code, and `quoteIntent()`'s indexed-rate strategy is the SDK's documented default with no fallback or deviation protection for the party actually moving funds (order placers), unlike the optional, solver-side-only Uniswap guard.

### Recommendation
- Add a deviation/circuit-breaker check in `updateLiquidityPools`/`mergeChainRowsIntoPool` that rejects or discounts a per-chain sample (or the resulting pool rate) that moves beyond a bounded percentage from the prior published rate or from a TWAP/multi-window baseline, rather than only logging via `warnOnDivergentSample`.
- Require a minimum bidder diversity (e.g., minimum `bidCount` or maximum single-bidder weight share) before a leg's `weightedMedian` is allowed to update the published pool rate.
- Surface `bidCount`/weight-concentration metadata to `quoteIntent()` callers (or add an opt-in `maxDeviationBps` guard on the order-placer side, mirroring the Simplex solver's Uniswap guard) so a thin or single-bidder-dominated rate cannot silently price a real order.

### Proof of Concept
1. Attacker controls (or briefly funds) an EOA/solver account and acquires a large balance of token B (leg output token) on the destination chain — sufficient to exceed 50% of the aggregate weight for that leg's phantom bid window.
2. During the `PhantomBidWindowExhausted` window, the attacker submits the only (or dominant-weight) verified bid for that leg with an extreme `solverAmount` (e.g., near-zero output for the same input), per the format `aggregatePhantomBids` accepts (`sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts:1376-1521`).
3. `weightedMedian` (lines 709-724) selects the attacker's extreme quote verbatim because its weight exceeds half of total weight.
4. `updateLiquidityPools` (`sdk/packages/indexer/src/services/liquidityPool.service.ts:227-459`) writes this as the chain sample and merges it into `LiquidityPool.sellRate`/`buyRate` via `mergeChainRowsIntoPool` (lines 470-496); `warnOnDivergentSample` only logs, it does not block the merge.
5. A victim calls `gateway.quoteIntent({ tokenIn, tokenOut, amountIn })` (default `indexed_rates` strategy, `sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts:44-77`), receiving `amountOut` computed from the manipulated rate.
6. The victim signs and places an `IntentGatewayV2` order using these corrupted amounts, escrowing real funds; the attacker (or a colluding solver) fills the order at the manipulated rate, extracting the mispriced difference.

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

**File:** sdk/packages/sdk/docs/ai/flows/how-a-phantom-order-s-bids-become-one-price-per-leg.md (L10-10)
```markdown
6. Per leg: drop every zero-weight quote — from the median, from `bidCount`, and from `bidders` alike — and drop the leg entirely if none is left. Otherwise `weightedMedian` picks the price, and `lowestPrice`/`highestPrice` are set to that same median rather than the raw bid extremes.
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

**File:** docs/content/developers/sdk/api/intent-gateway.mdx (L176-180)
```text
### quoteIntent(params)

Quotes an intent from the latest aggregate pool buy or sell rate published by the indexer. The pool rate is depth-weighted from fresh chain samples. Pass token addresses directly—the SDK resolves their configured symbols and decimals. No `strategy` option is needed for indexed-rate quotes.

Indexed-rate quotes require an attached Hyperbridge indexer client. There is no automatic fallback to another price source.
```

**File:** sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts (L146-163)
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
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-72)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.
```
