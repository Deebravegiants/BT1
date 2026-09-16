### Title
Solver-controlled weighted-median price manipulation for low-liquidity legs poisons the default intent quoting oracle - ([File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts])

### Summary
The Moonwell incident inflated the on-chain price of a low-liquidity token and used it as collateral to borrow real assets. Hyperbridge's phantom-order price-discovery pipeline has the same shape: a single intent solver can dictate the published price of a thinly-bid (low-liquidity) leg because that leg's median is weighted only by each solver's *self-reported* destination-chain balance of the output token, and that manipulated price is fed directly into the default quote used to size real orders moving real assets.

### Finding Description
`aggregatePhantomBids` computes, per leg, a `weightedMedian` of solver quotes where each quote's weight is the solver's own balance of that leg's output token on the destination chain [1](#0-0) . The weighted-median selection is documented to return an *exact* quoted value verbatim whenever a single bidder holds over half the leg's weight: "a solver holding over half the leg's weight sets the published price verbatim, and inventory in the wrong token buys no influence on that leg" [2](#0-1) , reiterated in the phantom-probe flow doc [3](#0-2) .

For an exotic/low-liquidity token leg, it is trivial for a single solver to be the only (or dominant) bidder holding that token's destination-chain balance — there is no floor on minimum bidder count or minimum diversity of weight before a median is accepted; a leg with one backed quote still produces a `medianPrice` [4](#0-3) . That per-leg median becomes `PhantomOrderPriceSnapshotV2`, is renormalized by `updateLiquidityPools`, and merged into a pool's canonical `buyRate`/`sellRate` [5](#0-4) .

Critically, as of the 2026-08-25 change, `IntentGateway.quoteIntent` — the SDK's default pricing path for constructing real orders — uses these aggregate `LiquidityPool.buyRate`/`sellRate` values directly, with "no automatic fallback to another price source" [6](#0-5) , and this is now the default strategy rather than an opt-in one [7](#0-6) . Explicit alternatives (Phantom snapshot, Uniswap V4 pool-based pricing) do carry price guards — e.g. `referencePrice`/`maxDeviationBps` deviation checks against a manipulated/thin pool [8](#0-7)  — but the indexed-rate path that `quoteIntent` defaults to has no equivalent sanity bound against the raw solver-set median.

### Impact Explanation
A solver that dominates the (thin) inventory of a low-liquidity token's output leg can set an arbitrary published price for that pair by simply submitting a self-serving bid — the exact "inflate a low-liquidity token's price" step in the Moonwell report. Because `quoteIntent` consumes this rate by default to compute `amountIn`/`amountOut` for real orders, a counterparty using default quoting can be induced to construct an order that escrows/pays out real assets (e.g. USDC) at the manipulated exchange rate against the low-liquidity token, resulting in a direct extraction of real value analogous to the reported $8.7M loss pattern. This crosses from a pricing inconvenience into concrete fund-loss territory once real orders are sized from the poisoned rate.

### Likelihood Explanation
Any account able to act as a filler/solver and quote a phantom order leg can attempt this — solvers are explicitly one of the roles this analysis must consider reachable. Manipulation is easiest and cheapest exactly for the "low-liquidity" tokens the original report targeted, since a single solver naturally holds the majority (or entirety) of destination-chain balance for an obscure token, requiring no flash-loan or governance compromise — only enough capital to appear as the dominant/only quoting solver for that leg.

### Recommendation
Add liquidity/diversity floors before a leg's `weightedMedian` is trusted for the default `indexed_rates` quoting path (e.g., minimum number of independent, uncorrelated bidders per leg, and a cap on any single solver's share of leg weight), and/or apply the same reference-price/max-deviation guard used for Uniswap V4 pool pricing to the indexed aggregate rate consumed by `quoteIntent`, so a rate diverging sharply from an independent reference is rejected rather than silently used to size real orders.

### Proof of Concept
1. Attacker deploys/controls the only meaningful destination-chain balance of exotic token `X` (low liquidity by construction).
2. Attacker runs a solver identity that submits a phantom-order bid quoting an extreme output amount for the `X` leg; per weight logic, its balance of `X` is the leg's dominant (only) weight [9](#0-8) .
3. `weightedMedian` returns the attacker's exact quoted price for the leg [10](#0-9) , which propagates into `LiquidityPool.buyRate`/`sellRate` via `updateLiquidityPools`.
4. A victim calling `IntentGateway.quoteIntent` (default `indexed_rates` strategy, no fallback) for the `X`/USDC pair receives amounts computed from the poisoned rate and constructs a real order that escrows/transfers real assets at the manipulated exchange rate [11](#0-10) .

Note: I was unable to fully confirm within the available exploration whether `isVerifiedSolverBid` restricts bid counting to a permissioned/delegated solver allowlist versus any address running solver software; this affects how "unprivileged" the entry point is in practice and should be verified against `phantom-aggregation.ts`'s `isVerifiedSolverBid` implementation and the solver-registration/delegation logic before treating this as fully permissionless.

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1479-1504)
```typescript
			const weights = await Promise.all(
				// Price influence: the solver's liquidity in THIS leg's output token on the destination
				// chain, so a leg is weighted by the inventory that actually backs it.
				quotedLegs.map(async ([, leg]) => {
					const outputToken = toAddress(leg.outputToken)
					const balance = await getBalance(destUrl, chain, outputToken, solver)
					return positions.reduce(
						(total, state) =>
							total +
							positionAmountOfToken({
								info: state.info,
								liquidity: state.liquidity,
								sqrtPriceX96: state.sqrtPriceX96,
								outputToken,
							}),
						balance,
					)
				}),
			)
			for (const [position, [legIndex, leg]] of quotedLegs.entries()) {
				const weight = weights[position]
				const entry = quotesByLeg.get(legIndex) ?? { outputToken: leg.outputToken, quotes: [], bidders: [] }
				entry.quotes.push({ price: leg.solverAmount, weight })
				entry.bidders.push({ solver: normalizedSolver as HexString, weight, acceptedSources })
				quotesByLeg.set(legIndex, entry)
			}
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1537-1563)
```typescript
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
		})
```

**File:** sdk/packages/sdk/docs/ai/flows/how-a-phantom-order-s-bids-become-one-price-per-leg.md (L9-13)
```markdown
5. Weight each quoted leg by the solver's deliverable inventory in *that leg's* output token on the destination chain: ERC-20 balance + redeemable vault shares (`getBalance`) plus the withdrawable side of any declared position the solver actually owns on-chain (`readPosition`, filtered by owner). Then sweep the solver's whole inventory into `lpBalances` once per bid.
6. Per leg: drop every zero-weight quote — from the median, from `bidCount`, and from `bidders` alike — and drop the leg entirely if none is left. Otherwise `weightedMedian` picks the price, and `lowestPrice`/`highestPrice` are set to that same median rather than the raw bid extremes.

A malformed bid is skipped and the rest are priced; a `PhantomRpcError` aborts the whole run instead, because a partial bid set publishes a confident price built from whichever bids happened to be readable.
```

**File:** sdk/packages/simplex/docs/ai/flows/phantom-probe-curve-value-published-price.md (L34-42)
```markdown
  -> aggregatePhantomBids           quotes.push({ price, weight })
  -> weightedMedian(backedQuotes)   SELECTION — returns an input element verbatim
  -> PhantomOrderPriceSnapshotV2    medianPrice = lowestPrice = highestPrice
  -> indexer updateLiquidityPools   renormalized by the leg's own standardAmount
```

A quote's weight in that median is the solver's balance of **that leg's output token on the
destination chain** — so a solver holding over half the leg's weight sets the published price
verbatim, and inventory in the wrong token buys no influence on that leg.
```

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L14-23)
```markdown

4. `updateLiquidityPools` (`src/services/liquidityPool.service.ts`) turns those per-leg medians into pool rows. `resolvePoolLeg` maps a leg's tokens to a pool id and direction via the token registry, and the sample's rate is

   ```
   medianPrice * 10 ** (18 - outDecimals) * 10 ** inDecimals / standardAmount
   ```

   i.e. the quote renormalized from the probe size back to one whole input token. This holds for any standard amount the pallet configures; it collapses to `medianPrice * scale` when the probe is exactly one unit. Multiplications happen before the division, so only the last step truncates, by under one unit of 1e18 and downward.

5. Chain rows (`PoolChainLiquidity`, one per pool/chain/direction) are merged into the pool's single `sellRate`/`buyRate` by `weightedRate` — a depth-weighted **mean**, which unlike the median in step 3 does produce values no filler quoted. Samples older than `MAX_SAMPLE_AGE_BLOCKS` are excluded unless every sample is stale.
```

**File:** docs/content/developers/sdk/api/intent-gateway.mdx (L176-184)
```text
### quoteIntent(params)

Quotes an intent from the latest aggregate pool buy or sell rate published by the indexer. The pool rate is depth-weighted from fresh chain samples. Pass token addresses directly—the SDK resolves their configured symbols and decimals. No `strategy` option is needed for indexed-rate quotes.

Indexed-rate quotes require an attached Hyperbridge indexer client. There is no automatic fallback to another price source.

Use `amountIn` and `amountOut` when constructing the `inputs` and `output.assets` for an IntentGateway V2 order.

```typescript lineNumbers
```

**File:** sdk/packages/sdk/docs/ai/changelog/2026-08-25-intent-quotes-use-aggregate-indexed-pool-rates-by-default.md (L1-5)
```markdown
# 2026-08-25 — Intent quotes use aggregate indexed pool rates by default

`IntentGateway.quoteIntent` now prices orders from the pair-centric indexer's depth-weighted aggregate `LiquidityPool.buyRate` and `sellRate`. Source and destination chains resolve the configured token deployments, while the quote converts the pool's whole-token rate into raw amounts with configured decimals, applies the source gateway protocol fee, and exposes the selected rate and timestamp in metadata. Reverse sell-rate reciprocals round up so quotes do not overpromise output. Phantom snapshot and Uniswap V4 pricing remain explicit compatibility strategies. Live sequential tests cover exact-input USDC to cNGN and exact-output cNGN to USDC across BSC and Base, including their different token decimal scales. The dead `binance.llamarpc.com` BSC default was replaced with `bsc-rpc.publicnode ... (truncated)

Files: `src/configs/chain.ts`, `src/protocols/intents/IntentGateway.ts`, `src/protocols/intents/LiquidityEngine.ts`, `src/protocols/intents/index.ts`, `src/protocols/intents/quote/index.ts`, `src/protocols/intents/quote/indexedRates.ts`, `src/protocols/intents/quote/types.ts`, `src/tests/sequential/intentGateway.test.ts`, `package.json`, `CHANGELOG.md`, `docs/ai/ChangeLog.md`, `docs/ai/Decisions.md`, `../../../docs/content/developers/sdk/api/intent-gateway.mdx`, `../../../docs/content/developers/evm/intent-gateway/placing-orders.mdx`.
```

**File:** docs/content/developers/evm/simplex/pricing.mdx (L68-84)
```text
## Uniswap price guards

Pool-based pricing trusts the live pool, which leaves the solver exposed to a manipulated, stale, or thin pool returning a bad quote. To bound that risk, give a position a **`referencePrice`** and **`maxDeviationBps`**. Whenever the pool quote on that chain drifts more than `maxDeviationBps` above or below the reference, the solver refuses to fill — the order is rejected before any bid is submitted.

`referencePrice` is expressed in **exotic tokens per USD**, the same units as the bid/ask curves. The two fields must be set together; omit both to leave the chain unguarded.

```toml lineNumbers
[vault.uniswapV4]
# referencePrice is the expected cNGN per USD;
# reject if the quote is more than 2% off.
# The two go together — one without the other is rejected.
[[vault.uniswapV4.positions]]
chain           = "EVM-8453"
tokenId         = "2087350"
referencePrice  = "1575"
maxDeviationBps = 200
```
```
