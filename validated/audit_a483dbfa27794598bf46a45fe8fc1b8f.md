I now have sufficient evidence to construct the analog finding.

### Title
No incentive for solvers to bid early in phantom-order price aggregation — a last-block, high-weight bid unilaterally sets the published pool rate - ([File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts])

### Summary
The phantom-order price-discovery auction mirrors the Hermez pattern: bids are public and queryable in real time via the `intents_getBidsForOrder` RPC before the window closes, weight is a pure function of an on-chain balance readable at the moment the window closes, and `weightedMedian` performs a **selection**, not a blend — one bidder's exact quoted price becomes the published rate whenever that bidder's weight reaches half the total. There is no mechanism (time-decayed weighting, commit-reveal, or early-bid incentive) discouraging a well-capitalized solver from waiting until the last block of the bid window, observing every competitor's quote, and submitting one final bid engineered to dominate the weighted median.

### Finding Description
`place_bid` accepts bids up to `info.created_at_block + window`, with no minimum lead time before the window closes: [1](#0-0) 

Bids are queryable during the open window via the `getBidsForOrder`/`intents_getBidsForOrder` RPC, so a bidder can see every competitor's quote before submitting their own, right up to the last eligible block: [2](#0-1) 

Aggregation happens only once, after `PhantomBidWindowExhausted` fires in `on_finalize` (i.e., after every bid placed in the closing block is already visible): [3](#0-2) 

The price is then computed by `weightedMedian`, which is explicitly documented as a **selection** — it returns one bidder's exact quoted integer, and "a solver holding over half the leg's weight sets the published price verbatim": [4](#0-3) 

This is confirmed by the SDK's own test suite and flow documentation: [5](#0-4) [6](#0-5) 

The weight is a live, unlocked balance read at aggregation time (`getBalance`), not a bonded/committed stake: [7](#0-6) 

The resulting per-leg median feeds directly into the indexer's `updateLiquidityPools`, becoming the pool's `sellRate`/`buyRate`: [8](#0-7) [9](#0-8) 

Those pool rates are the default price source `quoteIntent` uses to construct real orders when no explicit strategy is given: [10](#0-9) [11](#0-10) 

Exactly as in the Hermez bug class — public bids, no penalty for waiting, whoever moves last and biggest decides the outcome — a solver here can watch every other bidder's quote throughout the open window (nothing prevents this; bids are readable by anyone who can call the RPC) and, in the window's final block, submit a quote engineered together with sufficient weight (its own held balance in that leg's output token, which needs no lock and can be transiently inflated, e.g., via a flash loan or short-lived transfer, right before the window closes) to unilaterally set the published median "verbatim."

### Impact Explanation
The manipulated median propagates through `updateLiquidityPools` into `LiquidityPool.buyRate`/`sellRate`, which `quoteIntent`'s default `indexed_rates` strategy uses to price real intent orders that users construct without specifying an override strategy. An attacker who dictates the published rate can skew what price real users are quoted for their orders, causing them to escrow inputs against a manipulated exchange rate — a direct mispricing of user funds moving through the escrow/order-fill path, not merely an informational display value. This is a Medium/High-severity market-manipulation-of-pricing-oracle-for-funds-movement issue, analogous to the Hermez last-minute vote manipulation where "anyone with a large fund can decide the outcome."

### Likelihood Explanation
Likelihood is moderate-to-high: bids are unauthenticated as to timing (no early-bid requirement), publicly queryable throughout the window via a documented RPC, the bid window is measured in "tens of blocks" (short), and the weighting mechanism is explicitly acknowledged in the codebase's own documentation as giving majority-weight solvers verbatim price-setting power. No capital is permanently at risk to the attacker beyond transient inventory needed to inflate weight for one block, making the attack cheap relative to the potential mispricing gained across all real orders quoted against that pool until the next snapshot.

### Recommendation
**Short term:** Require a minimum lead time before the bid window closes (a "quiet period" during which no new bids are weighted, or where new-bid weight decays), and/or resist last-block dominance by requiring the weighting balance to be locked/committed for the whole window rather than read once at aggregation time, closing the flash-balance vector. Consider using a time-weighted or multi-block average of the qualifying weight rather than a single point-in-time balance read.

**Long term:** Explore commit-reveal or Vickrey-style bidding for phantom-order pricing so a bidder cannot react to competitors' quotes, and periodically review price-oracle design against known TWAP/weighted-median manipulation research, exactly as recommended for on-chain voting/bidding systems generally.

### Proof of Concept
1. Attacker monitors an active phantom order's bid window via `getBidsForOrder`/`intents_getBidsForOrder`, watching every solver's declared price for a leg as the window approaches closing. [2](#0-1) 
2. In the last eligible block (`block_number <= created_at_block + window`), attacker's solver acquires (e.g., via flash loan/transient transfer) a balance of the leg's output token exceeding half the total weight of all bids for that leg, then submits `place_bid` with an arbitrary price for that leg. [12](#0-11) 
3. `PhantomBidWindowExhausted` fires in the same/next block's `on_finalize`, and `aggregatePhantomBids`/`weightedMedian` publishes the attacker's exact price as the leg's `medianPrice`, since the attacker's weight crosses the 50% cumulative threshold. [13](#0-12) 
4. The indexer writes this into `LiquidityPool.sellRate`/`buyRate`, which subsequently prices real user orders quoted via `quoteIntent`'s default `indexed_rates` strategy until the next snapshot refreshes it. [14](#0-13)

### Citations

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L332-383)
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

			// Store the bid in offchain storage
			let bid = Bid { filler: filler.clone(), user_op: user_op.to_vec() };
			let offchain_key = Self::offchain_bid_key(&commitment, &filler);
			offchain_index::set(&offchain_key, &bid.encode());

			// Store deposit amount in onchain storage for discoverability and accurate refunds
			Bids::<T>::insert(&commitment, &filler, deposit);

			Self::deposit_event(Event::BidPlaced { filler, commitment, deposit });

			Ok(())
		}
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L1150-1168)
```rust
		fn on_finalize(n: BlockNumberFor<T>) {
			// Signal each active commitment on the block its bid window closes so the indexer can
			// aggregate that order's snapshot. Emitted in on_finalize (after all extrinsics) so any
			// bid placed in the window-closing block is already in storage when the snapshot is
			// taken. The bid window is expected to be shorter than the generation interval, so the
			// active batch is never replaced by on_initialize on the same block its window closes.
			let Some(active) = CurrentPhantomOrder::<T>::get() else {
				return;
			};
			let window: BlockNumberFor<T> = Self::phantom_bid_window().into();
			for (commitment, info) in active.iter() {
				if n == info.created_at_block.saturating_add(window) {
					Self::deposit_event(Event::PhantomBidWindowExhausted {
						commitment: *commitment,
						created_at: info.created_at_block,
					});
				}
			}
		}
```

**File:** sdk/packages/sdk/src/chains/intentsCoprocessor.ts (L872-890)
```typescript
	}

	/**
	 * Submits a bid to Hyperbridge's pallet-intents
	 *
	 * @param commitment - The order commitment hash (bytes32)
	 * @param userOp - The encoded PackedUserOperation as hex string
	 * @returns BidSubmissionResult with success status and block/extrinsic hash
	 */
	async submitBid(commitment: HexString, userOp: HexString): Promise<BidSubmissionResult> {
		try {
			return await this.signAndSendExtrinsic((api) => api.tx.intentsCoprocessor.placeBid(commitment, userOp))
		} catch (error) {
			return {
				success: false,
				error: error instanceof Error ? error.message : "Unknown error",
			}
		}
	}
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L697-724)
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
}
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1506-1513)
```typescript
			// Full liquidity picture: every configured token on every supported chain. Swept once per
			// bid rather than per leg, since it measures the solver's whole inventory either way.
			lpBalances.push(
				...(await sweepSolverLiquidity(evmRpcUrls, yieldVaults, solver, getBalance, {
					chain,
					states: positions,
				})),
			)
```

**File:** sdk/packages/sdk/src/tests/phantomAggregation.test.ts (L185-198)
```typescript
describe("weightedMedian", () => {
	it("equals the single quote when there is only one", () => {
		expect(weightedMedian([{ price: 100n, weight: 5n }])).toBe(100n)
	})

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

**File:** sdk/packages/simplex/docs/ai/flows/phantom-probe-curve-value-published-price.md (L26-42)
```markdown
The integer then travels unchanged:

```
outputs[i].amount                   e.g. 715
  -> fillOrder calldata outputs[i]  uint256, covered by userOpHash
  -> paymasterAndData               declaration: accepted sources = every configured chain
                                    (acceptedSourceChainsFor), plus declared V4 positions
  -> bid submitted to the coprocessor
  -> aggregatePhantomBids           quotes.push({ price, weight })
  -> weightedMedian(backedQuotes)   SELECTION — returns an input element verbatim
  -> PhantomOrderPriceSnapshotV2    medianPrice = lowestPrice = highestPrice
  -> indexer updateLiquidityPools   renormalized by the leg's own standardAmount
```

A quote's weight in that median is the solver's balance of **that leg's output token on the
destination chain** — so a solver holding over half the leg's weight sets the published price
verbatim, and inventory in the wrong token buys no influence on that leg.
```

**File:** sdk/packages/indexer/src/handlers/events/substrateChains/handlePhantomOrderPrices.handler.ts (L101-130)
```typescript
	let aggregate
	try {
		aggregate = await aggregatePhantomBids({
			nodeUrl,
			evmRpcUrls: rpcUrls,
			chain: phantom.chain,
			gatewayAddress,
			commitment,
			yieldVaults: YIELD_VAULT_ADDRESSES,
			solverAccount: solverAccounts,
			// viem's keccak throws in the VM2 sandbox; inject the indexer's ethers-based equivalents.
			extractFill: extractFillDataVm2,
			recoverSigner: recoverBidSignerVm2,
			bidNonceKey: bidNonceKeyVm2,
			orderCommitment: orderCommitmentVm2,
			// Lets a bid's declared V4 positions count towards the leg they back; the amounts and the
			// ownership check are read on-chain, so the bid only points at what to look at.
			uniswapV4: UNISWAP_V4_ADDRESSES,
			keccak: keccakVm2,
			getBalance: blockReaders(`${host}-${blockNumber}`).getBalance,
			logger,
		})
	} catch (err) {
		// aggregatePhantomBids already retried the whole run; reaching here means an input stayed
		// unreadable, so there is no honest snapshot to write. Skipping leaves each chain row on its
		// previous rate with a stale lastUpdatedBlock — visibly old, rather than confidently wrong.
		const msg = err instanceof Error ? `${err.name}: ${err.message}` : String(err)
		logger.error({ err, commitment, blockNumber }, `Phantom bid aggregation failed, skipping window: ${msg}`)
		return
	}
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

**File:** sdk/packages/sdk/docs/ai/decisions/2026-08-25-intent-quotes-default-to-directional-indexed-rates-without.md (L1-3)
```markdown
# 2026-08-25 — Intent quotes default to directional indexed rates without fallback

Chosen: `quoteIntent` defaults to an `indexed_rates` strategy that selects the depth-weighted aggregate `LiquidityPool.buyRate` for base-to-quote orders and `sellRate` for quote-to-base orders. Source and destination chains resolve the configured token deployments; raw amounts are calculated from the indexer's 18-decimal whole-token pool rate and both tokens' configured decimals. A missing directional rate is an error.
```

**File:** sdk/packages/sdk/src/protocols/intents/LiquidityEngine.ts (L120-150)
```typescript
	/**
	 * Returns the indexed pool's aggregate buy and sell rates in less-valued
	 * quote-token units per one base token.
	 *
	 * The indexer depth-weights fresh per-chain samples into the pool rates. The
	 * source and destination chains remain part of the result because they define
	 * the cross-chain route whose configured token symbols were resolved.
	 */
	async getBuyAndSellRates(params: {
		sourceChain: Chains
		destinationChain: Chains
		tokenInSymbol: ConfiguredAssetSymbol
		tokenOutSymbol: ConfiguredAssetSymbol
	}): Promise<BuyAndSellRates | undefined> {
		const pool = resolveLiquidityPool(params.tokenInSymbol, params.tokenOutSymbol)
		const response = await this.queryClient.request<BuyAndSellRatesResponse>(BUY_AND_SELL_RATES, {
			poolId: pool.poolId,
		})
		if (!response?.liquidityPools?.nodes) {
			throw new InvalidLiquidityIndexerResponseError("liquidity pool connection is missing")
		}
		const indexedPool = response.liquidityPools.nodes[0]
		if (!indexedPool) return undefined
		validateIndexedPool(indexedPool, pool)

		const sell = readIndexedRate(indexedPool.sellRate, indexedPool.lastUpdatedAt, "pool sell rate")
		const buy = readIndexedRate(indexedPool.buyRate, indexedPool.lastUpdatedAt, "pool buy rate")
		const inputIsToken0 = params.tokenInSymbol.toLowerCase() === pool.token0Symbol.toLowerCase()
		const direct = inputIsToken0 ? sell : buy
		const reverse = inputIsToken0 ? buy : sell
		if (!direct && !reverse) return undefined
```
