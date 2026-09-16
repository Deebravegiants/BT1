This confirms it: in the phantom-order price-aggregation path, the balance read that determines a bid's *weight* in `weightedMedian` uses `blockTag = "latest"` (default in `ethCallUint`/`getTotalSolverBalance`), i.e., the **live/current** on-chain balance at aggregation time — not pinned to any earlier or fixed block. This is the confirmed root cause enabling the analog.

### Title
Phantom-order price manipulation via transient solver-balance inflation skewing the liquidity-weighted median rate - ([File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts])

### Summary
`aggregatePhantomBids` derives the published price for each phantom-order leg from `weightedMedian`, where a bid's influence ("weight") is the solver's live ERC-20/ERC-4626 balance of the leg's output token, read via `getBalance`/`getTotalSolverBalance` at `blockTag = "latest"` [1](#0-0) . Because `weightedMedian` is a *selection*, not a blend, a bidder controlling over half the leg's cumulative weight has their exact quoted price become the published `medianPrice` verbatim [2](#0-1) .

### Finding Description
Any delegated solver can submit a real bid for a phantom order, then, right before (or during) the window that the indexer processes `PhantomBidWindowExhausted`, transiently pump its own balance of the leg's output token on the destination chain — e.g., via a flash loan, a large temporary transfer, or a same-block deposit into a configured ERC-4626 vault (`maxWithdraw` counts too) [3](#0-2) . Because the balance read for aggregation defaults to `"latest"` with no block pinning (unlike the later per-event refresh path, which was explicitly hardened to pin reads to the triggering event's block for exactly this kind of replay/consistency reason) [4](#0-3) , the temporarily inflated balance is what the aggregation observes and weights the bid by. If that weight exceeds 50% of total weight for the leg, `weightedMedian` returns that solver's own quoted price outright [5](#0-4) . The manipulated price is then persisted into `PoolChainLiquidity.rate` and merged into the pool's `sellRate`/`buyRate` [6](#0-5) [7](#0-6) , which is exactly the rate the SDK's `indexed_rates` intent-quoting strategy defaults to for pricing subsequent real orders, with no fallback and no sanity check against prior rates [8](#0-7) . The attacker can then withdraw/repay the temporary balance immediately after aggregation completes, leaving the poisoned rate in place until the next phantom-order window closes and re-snapshots it — mirroring the RAAC pattern of a transient state spike feeding an instantaneous calculation whose result is then locked in for a full interval.

### Impact Explanation
A skewed `sellRate`/`buyRate` directly misprices every subsequent order quoted with `indexed_rates` until the next snapshot, letting the manipulating solver (or a colluding taker) execute trades at an off-market rate — extracting value from counterparties or from the protocol's own quoting logic. This is an economic/pricing-integrity issue reachable by any unprivileged, EIP-7702-delegated solver placing a bid, with real fund-loss potential on subsequent fills priced from the poisoned rate.

### Likelihood Explanation
Requires only: (1) being (or controlling) a delegated `SolverAccount` able to submit a verified phantom bid, and (2) the ability to transiently hold a large balance of the output token on the destination chain (flash loan or temporary funding) at the moment the indexer's `getBalance` call runs — no special privilege, no consensus/dispatch-layer access needed. The main constraint is timing the transient balance to overlap with the indexer's read of `"latest"`, which is feasible since `PhantomBidWindowExhausted` processing is asynchronous and not tightly bound to a single attacker-controlled block boundary.

### Recommendation
Pin the balance reads used for `weightedMedian` weighting in `aggregatePhantomBids` to a fixed, non-attacker-influenced block (e.g., the block at which the bid window closed on the destination chain, similar to the `blockTag` pinning already implemented for the per-event refresh path), rather than defaulting to `"latest"`. Additionally, consider bounding how much a single bidder's weight can move the median (a cap or a smoothing/time-weighted balance check), and validate a newly observed price against the pool's recent rate history before accepting it as the new `sellRate`/`buyRate`.

### Proof of Concept
1. Attacker's delegated solver submits a verified phantom bid quoting a favorable price for a leg.
2. Shortly before/while `handlePhantomOrderPrices` runs `aggregatePhantomBids` (triggered by `PhantomBidWindowExhausted`), the attacker flash-loans or otherwise temporarily acquires >50% of the total weight's worth of the leg's output token into the solver's address (or deposits into a configured yield vault, since `maxWithdraw` counts).
3. `getBalance` reads this balance at `"latest"` [9](#0-8) , making the attacker's weight dominate `quotesByLeg`.
4. `weightedMedian` selects the attacker's exact quoted price as `medianPrice` [2](#0-1) .
5. Attacker repays/removes the temporary balance.
6. The manipulated price is written into `PoolChainLiquidity`/`LiquidityPool` and used to quote real intents via `indexed_rates` until the next phantom window closes.

### Citations

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

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L995-1006)
```typescript
async function ethCallUint(evmRpcUrl: string, to: string, data: string, blockTag = "latest"): Promise<bigint> {
	const result = await rpcCall(evmRpcUrl, {
		id: 1,
		jsonrpc: "2.0",
		method: "eth_call",
		params: [{ to, data }, blockTag],
	})
	if (result.result === "0x") return 0n
	if (typeof result.result !== "string") {
		throw new PhantomRpcError(`eth_call returned no result for ${to} on ${evmRpcUrl}`)
	}
	return BigInt(result.result)
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1009-1021)
```typescript
/**
 * Sums the solver's redeemable balance of a single token on one chain: the raw ERC-20 balance plus
 * any ERC-4626 vault positions wrapping it.
 *
 * This is THE definition of "a solver's balance" — the periodic sweep and any per-event re-read
 * must use it rather than a bare `balanceOf`, because simplex funds fills straight out of a vault
 * inside the fill transaction: the wallet ends the block roughly where it started while
 * `maxWithdraw` is what actually moved, so a wallet-only read misses such a fill entirely.
 *
 * `blockTag` reads the balance as of a specific block ("0x..." or a tag), so a caller replaying an
 * event records the balance as of that event rather than stamping today's balance onto a
 * historical row. It defaults to the chain head, which is what a periodic sweep wants.
 */
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

**File:** sdk/packages/indexer/src/services/liquidityPool.service.ts (L470-495)
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
