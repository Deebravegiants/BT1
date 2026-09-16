Confirmed: the phantom price snapshot's `getBalance` reads are explicitly documented as pinned to `"latest"` (head) for the phantom sweep path — `blockReaders` comment states "The phantom sweep pins nothing and reads every chain at its head" [1](#0-0) , and `handlePhantomOrderPrices.handler.ts` calls `blockReaders(`${host}-${blockNumber}`).getBalance` for the Hyperbridge (substrate) block, which does not pin any of the EVM destination chains to a specific block [2](#0-1) .

### Title
Phantom price aggregation weights bids by instantaneous, flash-loanable solver balance, letting a solver mint a manipulated `LiquidityPool.buyRate`/`sellRate` that real orders are priced from - (File: `sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts`)

### Summary
`aggregatePhantomBids` weights each solver's quote for a phantom-order leg by that solver's **current, head-block** balance of the leg's output token, read live over RPC (`getBalance`) at the moment the bid window closes. The weighted median of these balance-weighted quotes becomes the leg's published price, which `updateLiquidityPools` folds into the pool's `buyRate`/`sellRate`, which `IntentGateway.quoteIntent`'s default `indexed_rates` strategy then uses to price real user orders. This is structurally the same defect as the reported PID interest-rate bug: a decision-critical value (`_errI` / here, the published market rate) is derived from a balance that is measured "now" rather than from a manipulation-resistant, previously-committed value, so a participant can transiently inflate that balance (e.g., via a flash loan) for the single read, then immediately return it, and skew the derived value in their favor.

### Finding Description
The bid window closes deterministically on-chain (`PhantomBidWindowExhausted` fired in `on_finalize`) [3](#0-2) , but the balance used to weight each solver's bid is not read at any block tied to the order or the window close — it is read at the EVM chain's current head at whatever moment the indexer's off-chain handler happens to run the aggregation:

- `blockReaders(...).getBalance` is documented as: *"The phantom sweep pins nothing and reads every chain at its head."* [4](#0-3) 
- The handler passes `getBalance: blockReaders(`${host}-${blockNumber}`).getBalance` where `blockNumber` is the **Hyperbridge (substrate)** block, not an EVM block/blockTag for any of the destination chains being swept [5](#0-4) .
- In the aggregation itself, weight is fetched per leg via `getBalance(destUrl, chain, outputToken, solver)` and directly determines each quote's weight in `weightedMedian` [6](#0-5) .
- The leg's price is a **selection**, not a blend: `weightedMedian` returns one bidder's exact quoted integer, so "a solver holding over half the leg's weight sets the published price verbatim" [7](#0-6) .
- That price feeds `updateLiquidityPools`, which merges it via depth-weighted mean into `LiquidityPool.buyRate`/`sellRate` [8](#0-7) .
- `IntentGateway.quoteIntent`'s default strategy prices real user orders directly off `LiquidityPool.buyRate`/`sellRate` with no fallback and no sanity bound against a prior/committed value [9](#0-8) .

Because the balance read happens off-chain, asynchronously, after the on-chain window closes, and is explicitly "at the head" with no block pinning, a solver (an unprivileged intent solver — one of the listed reachable actors) can: (1) place a bid during the open window with an arbitrarily favorable price for a leg, (2) immediately before/around the aggregation run, flash-borrow a large amount of that leg's output token into their own address on the destination chain (no need to even touch Hyperbridge — this is a same-chain, same-block flash loan on the EVM destination), (3) let the aggregation read weight it as the majority holder of that leg's inventory so `weightedMedian` selects their bid price verbatim, and (4) return the flash loan. The published market rate is now the attacker's chosen number, exactly analogous to using instantaneous `availableLiquidity`/`totalVariableDebt` in the reported Pi-rate bug instead of a value insulated from same-block manipulation.

### Impact Explanation
The manipulated rate is not just informational — it is consumed by `IntentGateway.quoteIntent`'s `indexed_rates` strategy (the SDK's default pricing path for real orders, per the recorded decision to make it the default with no fallback) [10](#0-9) . Any counterparty who places or fills an intent order priced from this rate can be given a mispriced quote, letting the manipulating solver (or a colluding counterparty) extract value from real cross-chain fills — a concrete theft vector reachable from a single unprivileged phantom-bid submission plus a flash loan, matching the severity class ("medium risk," concrete fund-extraction potential) of the reported analog.

### Likelihood Explanation
Medium-to-high: placing a phantom bid is fully permissionless (any account can `place_bid`) [11](#0-10) ; flash loans of ERC-20 tokens are cheap and routine on EVM chains; and the balance read is explicitly documented as reading "at the head" with no block pinning for the phantom sweep, so there is no defense-in-depth (e.g., averaging over a window, using a historical block, or requiring the balance to persist across blocks) preventing a single-block spike from being counted.

### Recommendation
Do not weight/select phantom-leg prices from an instantaneous, freely-manipulable "current head" balance read. Either: pin the balance read to a block committed before the bid was placed (e.g., the block the phantom order/leg was registered, or the block the bid was placed), analogous to using the "previous" `availableLiquidity`/`totalVariableDebt` in the cited bug's recommendation; or require the balance to be attested/locked (e.g., via a time- or block-averaged reading, or a staked/committed inventory) so a single-block flash loan cannot inflate weight for the read.

### Proof of Concept
1. Attacker's solver account is delegated and eligible to bid (per `isVerifiedSolverBid`).
2. Attacker submits a phantom bid during the open window quoting an extreme price for a leg they want to control, with near-zero real balance of the leg's output token.
3. Attacker waits for `PhantomBidWindowExhausted` (on-chain, deterministic) to be near, then flash-borrows a large balance of the leg's output token on the destination EVM chain into their solver address.
4. When the indexer's `handlePhantomOrderPrices` handler runs `aggregatePhantomBids`, it calls `getBalance(destUrl, chain, outputToken, solver)` at the chain's current head [4](#0-3) , sees the flash-loaned balance, and weights the attacker's quote as majority — `weightedMedian` then returns the attacker's exact quoted price for the leg.
5. Attacker repays the flash loan in the same transaction/block.
6. `updateLiquidityPools` persists the manipulated price into `LiquidityPool.buyRate`/`sellRate`.
7. A victim calls `IntentGateway.quoteIntent` (default `indexed_rates` strategy), receives a quote computed from the manipulated rate, and places/fills an order at a price favorable to the attacker.

Note: I could not fully trace whether any additional safeguard exists purely in the indexer's retry/validation path (`AGGREGATION_ATTEMPTS`, per-bid try/catch) that might reject an obviously anomalous single-block balance spike — the available index did not show such a check, but a full audit of `aggregatePhantomBids`'s error-handling branches beyond what was retrieved would be needed to rule this out with certainty.

### Citations

**File:** sdk/packages/indexer/src/utils/solverBalance.ts (L55-61)
```typescript
/**
 * The readers for `key`, which must identify one block of one chain (handlers for different chains
 * run in separate processes, so the key only has to be unique within one).
 *
 * `blockTags` pins a chain to a specific block, so an event's re-read returns the same value on a
 * replay as it did live. The phantom sweep pins nothing and reads every chain at its head.
 */
```

**File:** sdk/packages/indexer/src/handlers/events/substrateChains/handlePhantomOrderPrices.handler.ts (L101-122)
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
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L332-357)
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
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L1150-1167)
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
```

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

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L11-13)
```markdown
2. Per leg, a solver's quote is weighted by **its balance of that leg's OUTPUT token on the destination chain** — the inventory that actually backs the leg. Zero-weight quotes are dropped entirely, not down-weighted: they never reach the median, `bidCount`, or the bidder list. A leg where no bidder holds the output token is absent from the result, exactly as if nobody quoted it.

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

**File:** sdk/packages/sdk/src/protocols/intents/quote/indexedRates.ts (L55-76)
```typescript
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
