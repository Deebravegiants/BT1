### Title
`quoteIntent` prices real orders from a `LiquidityPool.buyRate`/`sellRate` that a single self-serving phantom bid can set to any value — ([File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts])

### Summary
`IntentGateway.quoteIntent` prices real, user-executed intent orders directly from the indexer's `LiquidityPool.buyRate`/`sellRate`, which is itself derived from a `weightedMedian` over permissionless phantom-order bids. When a pool leg has never been bid on by more than one solver — the exact "empty pool" condition of the reported bug class — a single solver's self-quoted bid becomes the published rate verbatim, with no minimum-depth or minimum-bidder-count gate before that rate is trusted to construct a real order.

### Finding Description
`place_bid` on `pallet-intents-coprocessor` is a permissionless, unsigned-caller extrinsic that anyone can call to register a quote for any commitment, phantom or real, subject only to reserving a storage deposit [1](#0-0) . Phantom-order bids from this pallet feed `aggregatePhantomBids`, which weights each solver's quote by that solver's balance of the leg's output token and reduces the surviving quotes with `weightedMedian` [2](#0-1) .

`weightedMedian` is explicitly documented and tested to return the sole bidder's price verbatim when there is only one bid, and — per its own comment — to let "whoever quotes higher" win when there is no real depth behind competing quotes: [3](#0-2) 

This is confirmed by the unit test `"equals the single quote when there is only one"` [4](#0-3) .

The resulting per-leg median is turned into a pool-level `sellRate`/`buyRate` by `updateLiquidityPools`/`poolRateFromQuote`, with no minimum bidder-count or minimum-depth threshold gating the write [5](#0-4) .

`IntentGateway.quoteIntent`'s default `indexed_rates` strategy then reads that rate directly to compute the raw `amountIn`/`amountOut` for a **real, executable** order, validating only that the rate is a positive integer — not that it is backed by meaningful depth or multiple independent solvers: [6](#0-5) 

The documentation for this API confirms callers are expected to use the resulting amounts directly with no additional slippage protection: "Use the returned amounts directly as the order's `inputs` and `output.assets`—no further fee or slippage adjustment is required" [7](#0-6) .

This mirrors the reported bug class precisely: a system state (there, `price_sqrt`; here, `LiquidityPool.sellRate`/`buyRate`) that is trustworthy only once genuine, competing depth exists, but is consumed by downstream logic (there, a swap; here, `quoteIntent`) with no check that such depth exists. A pool/leg pair with zero or thin real liquidity is the exact "empty pool" analog — a single self-serving quote fully determines the published, execution-grade price.

### Impact Explanation
A malicious solver can be the first (or only) bidder for a freshly configured phantom-order pair/leg, quoting an arbitrarily favorable price for itself (bounded only by its own tiny output-token balance, since weight only needs to be `> 0`). That self-quoted price becomes `LiquidityPool.buyRate`/`sellRate` verbatim. Any user who then calls `quoteIntent` to size a real order is quoted amounts computed off this manipulated rate and, per the documented API contract, applies "no further fee or slippage adjustment." If the same (or colluding) solver goes on to fill the resulting real order, it extracts value from the user at the manipulated rate — directly analogous to the reported theft-via-manipulated-price scenario, and reachable by any intent solver with no special privilege.

### Likelihood Explanation
`place_bid` is fully permissionless and requires only a small reservable deposit [8](#0-7) . Any newly configured pair, or a pair whose bidding solvers have temporarily thinned out, is naturally in the "single bidder" state where `weightedMedian` returns that one quote unmodified — this is not a rare edge case but the default state for any less-liquid or newly-onboarded pair, and the SDK does not require a minimum bidder count or depth before trusting the pool rate for real order construction.

### Recommendation
Gate `quoteIntent`'s use of `LiquidityPool.buyRate`/`sellRate` (and the underlying `updateLiquidityPools` write) on a minimum number of independent, verified solvers and/or a minimum aggregate depth for the leg before the rate is considered execution-grade; below that threshold, `quoteIntent` should fail closed (as it already does for a missing rate) rather than silently use a thinly-backed or single-bidder price. Additionally, consider requiring callers of `quoteIntent`/`executeBest` to supply an explicit slippage/maximum-price bound rather than relying solely on the indexed rate with no adjustment.

### Proof of Concept
1. Attacker controls a small balance of `tokenOut` on the destination chain and registers as a solver.
2. Attacker calls `place_bid` on `pallet-intents-coprocessor` with a favorable (to itself) quote for a phantom order leg on a pair that currently has no other competing solver.
3. `PhantomBidWindowExhausted` fires; `aggregatePhantomBids` finds one verified, non-zero-weight bid and `weightedMedian` returns it verbatim (as unit-tested) [4](#0-3) .
4. `updateLiquidityPools` writes this as the pool's `sellRate`/`buyRate` with no depth/bidder-count gate [5](#0-4) .
5. A victim calls `IntentGateway.quoteIntent` for that pair; `IndexedRateIntentQuoteStrategy` computes `amountIn`/`amountOut` directly from the manipulated rate [9](#0-8)  and the victim places a real order using these amounts unmodified, per documented guidance.
6. The attacker (or a colluding solver) fills the order at the manipulated rate, extracting value from the victim exactly as in the reported "swap through an empty pool" scenario.

### Citations

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L332-370)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::place_bid())]
		pub fn place_bid(
			origin: OriginFor<T>,
			commitment: H256,
			user_op: BoundedVec<u8, ConstU32<1_048_576>>,
		) -> DispatchResult {
			let filler = ensure_signed(origin)?;

			// Validate user_op is not empty
			ensure!(!user_op.is_empty(), Error::<T>::InvalidUserOp);

			// Phantom orders have stricter rules: one bid per filler, no updates, and only
			// within the configured acceptance window after the order was registered. Every
			// chain's active order is checked, not just the most recently generated one.
			if let Some(active) = CurrentPhantomOrder::<T>::get() {
				if let Some((_, info)) = active.iter().find(|(c, _)| *c == commitment) {
					let window: BlockNumberFor<T> = Self::phantom_bid_window().into();
					ensure!(
						frame_system::Pallet::<T>::block_number() <= info.created_at_block + window,
						Error::<T>::PhantomOrderBidWindowClosed
					);
					ensure!(
						!Bids::<T>::contains_key(&commitment, &filler),
						Error::<T>::DuplicatePhantomBid
					);
				}
			}

			// If a bid already exists, unreserve the old deposit first
			if let Some(old_deposit) = Bids::<T>::get(&commitment, &filler) {
				<T as Config>::Currency::unreserve(&filler, old_deposit);
			}

			let deposit = Self::storage_deposit_fee();

			// Reserve the new deposit
			<T as Config>::Currency::reserve(&filler, deposit)
				.map_err(|_| Error::<T>::InsufficientBalance)?;
```

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

**File:** sdk/packages/sdk/src/tests/phantomAggregation.test.ts (L185-188)
```typescript
describe("weightedMedian", () => {
	it("equals the single quote when there is only one", () => {
		expect(weightedMedian([{ price: 100n, weight: 5n }])).toBe(100n)
	})
```

**File:** sdk/packages/indexer/src/services/liquidityPool.service.ts (L135-143)
```typescript
export function poolRateFromQuote(
	medianPrice: bigint,
	resolved: Pick<ResolvedPoolLeg, "inDecimals" | "outDecimals">,
	standardAmount: bigint,
): bigint {
	const scale = 10n ** BigInt(POOL_RATE_DECIMALS - resolved.outDecimals)
	const inputUnit = 10n ** BigInt(resolved.inDecimals)
	return (medianPrice * scale * inputUnit) / standardAmount
}
```

**File:** sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts (L120-144)
```typescript
function readIndexedRate(
	side: IndexedRateSide,
	rate: string | null,
	updatedAt: Date | null,
	rates: BuyAndSellRates,
	tokenInSymbol: ConfiguredAssetSymbol,
	tokenOutSymbol: ConfiguredAssetSymbol,
): SelectedIndexedRate {
	if (!rate || !updatedAt) {
		throw new IndexedRateUnavailableError({
			source: rates.sourceChain,
			destination: rates.destinationChain,
			tokenIn: tokenInSymbol,
			tokenOut: tokenOutSymbol,
			side,
		})
	}
	try {
		const scaledRate = parseUnits(rate, INDEXED_RATE_DECIMALS)
		if (scaledRate <= 0n || Number.isNaN(updatedAt.getTime())) throw new Error()
		return { side, rate, scaledRate, updatedAt }
	} catch {
		throw new InvalidIndexedRateError(`${side} rate or timestamp is invalid`)
	}
}
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

**File:** docs/content/developers/sdk/api/intent-gateway.mdx (L230-234)
```text
The result includes `amountIn`, `amountOut`, and strategy-specific quote metadata. Indexed-rate metadata contains the source and destination chains, base and quote symbols, the buy or sell rate used, its update time, and the source-chain protocol fee.

`amountIn` and `amountOut` already account for the IntentGateway protocol fee that the gateway deducts from order inputs. Exact-input quotes price the swap against the post-fee input, so `amountOut` is the snapshot-priced output; exact-output quotes return the gross `amountIn` required to produce the requested `amountOut`. Use the returned amounts directly as the order's `inputs` and `output.assets`—no further fee or slippage adjustment is required.

For exact-input quotes, the SDK deducts the gateway fee before applying the directional rate. For exact-output quotes, it calculates the required net input from that rate and then grosses the input up for the gateway fee. Token decimals are read from SDK chain configuration. A missing indexer, missing directional rate, or invalid rate throws an explicit error.
```
