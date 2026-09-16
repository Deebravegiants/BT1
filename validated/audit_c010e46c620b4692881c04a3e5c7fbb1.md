### Title
Any single well-funded solver can unilaterally set the published phantom-bid price, letting it manipulate the quoted rate that downstream pools and users rely on - (File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts)

### Summary
The Dutch-auction report describes an owner artificially inflating perceived market value by self-dealing early purchases, without any check limiting how much a single privileged/well-capitalized participant can skew the crowd's price signal. The closest reachable Hyperbridge analog is the phantom-bid price-discovery mechanism (`aggregatePhantomBids` / `weightedMedian`) used by the Intent Gateway's quote pipeline: it aggregates unprivileged solver "phantom bids" into a single published price using a liquidity-weighted median, but the weighting is unbounded and per-solver, so one solver holding over half the aggregate weight for a leg dictates the published price outright, exactly the "self-dealing distorts the public signal" failure class described in the report.

### Finding Description
`runAggregation` collects phantom bids from arbitrary, unprivileged solvers for an order leg and weights each solver's quote by its own on-chain balance/liquidity of the output token [1](#0-0) . These weighted quotes are then reduced with `weightedMedian`, which is explicitly documented as a **selection, not a blend**: it returns one bidder's exact price verbatim once cumulative weight crosses half the total weight [2](#0-1) . The project's own flow documentation confirms this is a known, accepted property: "a solver holding over half the leg's weight sets the published price verbatim" [3](#0-2) , and is reiterated in the phantom-probe flow doc [4](#0-3) .

The only anti-Sybil control present is deduplication by solver address within a single window (`countedSolvers`), preventing the *same* solver's bid from being counted multiple times [5](#0-4) . There is no cap on a single solver's weight share, no minimum-bidder-count/quorum requirement, and no protection against one deep-pocketed solver (or a solver who funds itself across the required inventory) dominating a leg's weight and thereby dictating the "market" price — directly analogous to the report's owner buying up NFTs early to inflate perceived demand: here, a single actor with sufficient capital deposited into the relevant output token on the destination chain can single-handedly set the published rate.

This published median directly feeds `updateLiquidityPools`, which turns it into pool `sellRate`/`buyRate` rows consumed by other users' `quoteIntent` calls [6](#0-5) , meaning the manipulated price is not confined to a single order but leaks into the broader price-quoting surface that real users/solvers rely on for the Intent Gateway auctions.

### Impact Explanation
The phantom-price mechanism is intended to be a fair, decentralized crowd-sourced estimate of solver liquidity/pricing, feeding both the SDK's `quoteIntent` (used by real users deciding whether/what to trade) and the indexer's pool rate tables. Because a single unprivileged solver can dominate the weighted median and dictate the published price for a leg, it can:
- Publish an artificially favorable or unfavorable rate that misleads users placing real orders into escrowing tokens at a bad implied rate (indirect value extraction via mispriced quotes), and
- Distort `PoolChainLiquidity`/pool `sellRate`/`buyRate` data used more broadly by the ecosystem, undermining the integrity of a signal external integrators treat as trustworthy market data.

This does not directly cause protocol insolvency or forged message delivery, but it is a concrete manipulation of a value used to induce economic decisions by unprivileged users of the Intent Gateway, which is the closest analog to the original "owner runs the auction untruthfully" bug class reachable by an unprivileged intent participant in this codebase.

### Likelihood Explanation
Exploitability requires only holding real inventory in the destination-chain output token backing a leg (the "cost" the phantom-order paper describes as inherent to legitimate demand signaling) and running a delegated `SolverAccount` to submit a signed phantom bid — no special privilege, whitelisting, or protocol-owner role is required. Because weight is purely proportional to on-chain balance with no cap, and quorum/minimum-diversity requirements do not exist, a single sufficiently capitalized actor reliably crosses the 50% weight threshold for lower-liquidity legs, making this readily achievable, especially for less-liquid output tokens/legs where aggregate solver inventory is thin.

### Recommendation
- Cap any single solver's contribution to a leg's total weight (e.g., no solver's weight may exceed some fraction, such as 20-30%, of total weight) before computing the weighted median, so no single actor can unilaterally set the price.
- Require a minimum number of distinct backed bidders (quorum) per leg before publishing a snapshot, rather than allowing a single backed quote to become the leg's price.
- Consider blending (weighted mean with outlier trimming) instead of a pure weighted-median "selection," to prevent any one quote from being read back verbatim as the market price.

### Proof of Concept
1. A solver `S` delegates an EOA to an authorized `SolverAccount` for `chain` (satisfies delegation verification in `isVerifiedSolverBid`).
2. `S` accumulates on-chain balance of the leg's `outputToken` on the destination chain sufficient to exceed 50% of the realistic aggregate liquidity solvers are expected to hold for that token/chain (thin liquidity legs are easiest).
3. `S` submits a single phantom bid quoting an arbitrary favorable/unfavorable `price` for that leg, signed correctly per `isVerifiedSolverBid`.
4. When `aggregatePhantomBids`/`runAggregation` processes the window, `S`'s quote's weight (its balance) crosses `cumulative * 2n >= totalWeight` first in `weightedMedian`, so `S`'s exact quoted price becomes `medianPrice = lowestPrice = highestPrice` for the leg [7](#0-6) .
5. This manipulated price propagates to `PhantomOrderPriceSnapshotV2` and then into `updateLiquidityPools`'s pool `sellRate`/`buyRate`, which real users' `quoteIntent` calls read when deciding order terms [6](#0-5) .

### Citations

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L697-723)
```typescript
// Liquidity-weighted median of solver quotes. Each quote's influence is proportional to `weight` —
// the solver's total balance for the output token across native + vault venues — so a solver that
// can actually deliver size moves the price more than one quoting on thin liquidity. Returns the
// lower weighted median: the smallest price whose cumulative weight reaches half of the total.
// Zero-weight quotes contribute nothing.
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
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1413-1418)
```typescript
			const normalizedSolver = solver.toLowerCase()
			if (countedSolvers.has(normalizedSolver)) {
				logger?.warn({ solver, commitment }, "Skipping phantom bid: solver already counted for this order")
				continue
			}
			countedSolvers.add(normalizedSolver)
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1479-1497)
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
```

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L11-13)
```markdown
2. Per leg, a solver's quote is weighted by **its balance of that leg's OUTPUT token on the destination chain** — the inventory that actually backs the leg. Zero-weight quotes are dropped entirely, not down-weighted: they never reach the median, `bidCount`, or the bidder list. A leg where no bidder holds the output token is absent from the result, exactly as if nobody quoted it.

3. The leg's price is `weightedMedian` of the backed quotes — a **selection**, not a blend. It returns one bidder's exact integer, so a solver holding over half the leg's weight sets the published price verbatim, and the result can never be a value nobody quoted. `lowestPrice` and `highestPrice` are deliberately overwritten with the median so consumers cannot read an outlier bid as a tradeable bound.
```

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L15-21)
```markdown
4. `updateLiquidityPools` (`src/services/liquidityPool.service.ts`) turns those per-leg medians into pool rows. `resolvePoolLeg` maps a leg's tokens to a pool id and direction via the token registry, and the sample's rate is

   ```
   medianPrice * 10 ** (18 - outDecimals) * 10 ** inDecimals / standardAmount
   ```

   i.e. the quote renormalized from the probe size back to one whole input token. This holds for any standard amount the pallet configures; it collapses to `medianPrice * scale` when the probe is exactly one unit. Multiplications happen before the division, so only the last step truncates, by under one unit of 1e18 and downward.
```

**File:** sdk/packages/simplex/docs/ai/flows/phantom-probe-curve-value-published-price.md (L40-42)
```markdown
A quote's weight in that median is the solver's balance of **that leg's output token on the
destination chain** — so a solver holding over half the leg's weight sets the published price
verbatim, and inventory in the wrong token buys no influence on that leg.
```
