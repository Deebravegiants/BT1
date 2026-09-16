Now I have a clear analog: the phantom-order price oracle weights each solver's quote by an **on-chain balance read taken via RPC at the current block ("latest") at the moment the indexer/SDK aggregates the bid window**, not by any block-locked or vesting-committed stake. Exactly like the `Checkpoints#getAtBlock()` flashloan bug, a solver can flashloan the leg's output token onto the EVM chain immediately before the aggregation reads its balance, hold it only for that single read, and thereby seize the majority of `weight` in `weightedMedian`, dictating the published price for that leg — a fake, momentary "stake" bought for the cost of a flashloan fee instead of real capital.

### Title
Phantom-order price oracle can be manipulated by a same-block flashloaned balance to set the published leg price - (File: `sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts`)

### Summary
`aggregatePhantomBids` weights every solver quote for a phantom-order leg by the solver's live on-chain balance of that leg's output token, read via `getTotalSolverBalance`/`getBalance` at the current ("latest") block [1](#0-0) . This weight feeds `weightedMedian`, which is a **selection**, not a blend — the bidder holding the largest weight has its exact quoted price picked verbatim as the published rate [2](#0-1) . Because the balance is read at whatever block the bid window happens to close (`PhantomBidWindowExhausted`, fired in `on_finalize`) rather than at bid-submission time or averaged/locked over a span of blocks [3](#0-2) , a solver can flashloan the output token onto the destination EVM chain for the single block/transaction in which its balance is sampled, inflate its `weight` far beyond its real capital, win the weighted-median selection, and dictate the leg's `medianPrice`, and then repay the flashloan — exactly the "borrow to inflate a snapshot read, exit same block" pattern from the Telcoin `Checkpoints#getAtBlock()` report.

### Finding Description
The root cause mirrors the referenced bug class: a security-critical value (there, staked-token weight for rewards/slashing; here, solver inventory weight for price-setting) is derived from an instantaneous balance read instead of a value that is locked, checkpointed strictly in the past, or averaged over time. `sweepSolverLiquidity`/`getTotalSolverBalance` read `balanceOf`/`maxWithdraw` with a `blockTag` that defaults to `"latest"` [1](#0-0) , and the per-run memo only guards against repeated RPC calls within one aggregation pass, not against a balance manufactured immediately before that pass runs [4](#0-3) . The documentation for this exact code path states plainly: "a solver holding over half the leg's weight sets the published price verbatim" [5](#0-4) . Nothing requires that inventory to be held for more than the instant of the read, nor across multiple blocks, nor to be escrowed/committed the way a real fill requires.

### Impact Explanation
The resulting `PhantomOrderPriceSnapshotV2.medianPrice` feeds `updateLiquidityPools`, which recomputes `LiquidityPool.sellRate/buyRate`, `PoolChainLiquidity.rate`, and route depths that real solvers, the SDK's `quoteOrderFees`, and downstream consumers use to price and route actual cross-chain intents [6](#0-5) . An attacker can therefore, at negligible real cost (a flashloan fee), unilaterally set a manipulated exchange rate for a token pair that real users' orders and other solvers' fill decisions rely on — a forged/unsound price commitment analogous to the fake-stake impact in the original report (winning rewards/influence disproportionate to real capital at risk).

### Likelihood Explanation
The bid window is fixed and governance-configured but short (5–25 blocks on live deployments) [7](#0-6) [8](#0-7) , and the balance read that determines weight happens once, at aggregation time, driven purely by an RPC call to the EVM chain with no minimum holding-period requirement. Any account capable of signing a valid solver bid (an already-required capability for participating fillers/solver accounts) and obtaining a flashloan of the relevant output token on the destination chain can time the flashloan to land in the same block the aggregation reads balances, requiring no privileged access, no validator collusion, and no code-path outside the documented, normal bid-then-aggregate flow.

### Recommendation
Do not weight quotes by an instantaneous "latest" balance read. Require the solver's weighting balance to be sourced from a value that cannot be manufactured within a single block/transaction — e.g., a balance snapshot taken strictly before the bid was submitted (mirroring the report's own recommendation to require the read to be "at least 1 block later" than any state change that could inflate it), an average/TWAP-style balance across the bid window, or a balance backed by an actual on-chain escrow/lock rather than a spot wallet/vault read. At minimum, sample the balance at the block the bid was placed (already known and immutable) rather than at the window-close block, so a flashloan taken after bidding cannot retroactively inflate the weight used to select the price.

### Proof of Concept
1. Governance/normal operation opens a phantom order with a short bid window (e.g. 5–25 blocks) on chain X for pair (tokenA, tokenB).
2. Attacker, as a registered/delegated solver, submits a low-cost `place_bid` quoting an off-market price for the leg, e.g. far above fair value.
3. In the same block the bid window closes (`PhantomBidWindowExhausted` fires in `on_finalize`), the attacker takes a flashloan of `tokenB` (the leg's output token) on chain X, so `getTotalSolverBalance` for the attacker's solver address returns an inflated amount at the "latest" block when `aggregatePhantomBids` runs.
4. The attacker repays the flashloan in the same transaction/block after the balance has already been observed by the indexer's on-chain read.
5. `weightedMedian` selects the attacker's quoted price because its weight now dominates cumulative weight [2](#0-1) , publishing the attacker-chosen `medianPrice` into `PhantomOrderPriceSnapshotV2` and propagating it into `LiquidityPool`/`PoolChainLiquidity` rates that real orders are quoted and routed against.

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

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1022-1037)
```typescript
export async function getTotalSolverBalance(
	evmRpcUrl: string,
	chain: string,
	token: string,
	solver: string,
	yieldVaults: YieldVaultMap,
	blockTag = "latest",
): Promise<bigint> {
	const padded = solver.replace("0x", "").padStart(64, "0")
	const raw = await ethCallUint(evmRpcUrl, token, `0x70a08231${padded}`, blockTag) // balanceOf(address)
	const vaults = yieldVaults[chain]?.[token.toLowerCase()] ?? []
	const vaultBalances = await Promise.all(
		vaults.map((v) => ethCallUint(evmRpcUrl, v, `0xce96cb77${padded}`, blockTag)), // maxWithdraw(address)
	)
	return vaultBalances.reduce((acc, b) => acc + b, raw)
}
```

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1161-1187)
```typescript
export function memoizedSolverBalance(
	yieldVaults: YieldVaultMap,
	/**
	 * Block to read each chain at, keyed by state machine id; anything absent reads the head. Block
	 * numbers are per chain, so a caller handling an event on one chain can pin that chain to the
	 * event's block while the rest of its sweep stays at the head, where the numbers would mean
	 * nothing.
	 */
	blockTags: Record<string, string> = {},
): SolverBalanceReader {
	const cache = new Map<string, Promise<bigint>>()
	return (evmRpcUrl: string, chain: string, token: string, solver: string): Promise<bigint> => {
		const key = `${chain}|${token.toLowerCase()}|${solver.toLowerCase()}`
		let pending = cache.get(key)
		if (!pending) {
			// Evict on rejection. Caching a failure would make it permanent for the memo's lifetime —
			// every retry would replay the same failed read, and a block-scoped memo would carry one
			// blip across every order closing on that block.
			pending = getTotalSolverBalance(evmRpcUrl, chain, token, solver, yieldVaults, blockTags[chain]).catch((err) => {
				cache.delete(key)
				throw err
			})
			cache.set(key, pending)
		}
		return pending
	}
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

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L11-13)
```markdown
2. Per leg, a solver's quote is weighted by **its balance of that leg's OUTPUT token on the destination chain** — the inventory that actually backs the leg. Zero-weight quotes are dropped entirely, not down-weighted: they never reach the median, `bidCount`, or the bidder list. A leg where no bidder holds the output token is absent from the result, exactly as if nobody quoted it.

3. The leg's price is `weightedMedian` of the backed quotes — a **selection**, not a blend. It returns one bidder's exact integer, so a solver holding over half the leg's weight sets the published price verbatim, and the result can never be a value nobody quoted. `lowestPrice` and `highestPrice` are deliberately overwritten with the median so consumers cannot read an outlier bid as a tradeable bound.
```

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L14-21)
```markdown

4. `updateLiquidityPools` (`src/services/liquidityPool.service.ts`) turns those per-leg medians into pool rows. `resolvePoolLeg` maps a leg's tokens to a pool id and direction via the token registry, and the sample's rate is

   ```
   medianPrice * 10 ** (18 - outDecimals) * 10 ** inDecimals / standardAmount
   ```

   i.e. the quote renormalized from the probe size back to one whole input token. This holds for any standard amount the pallet configures; it collapses to `medianPrice * scale` when the probe is exactly one unit. Multiplications happen before the division, so only the last step truncates, by under one unit of 1e18 and downward.
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L106-109)
```rust
parameter_types! {
	pub const IntentStorageDepositFee: Balance = 100 * EXISTENTIAL_DEPOSIT;
	pub const IntentPhantomOrderBidWindow: u32 = 5;
}
```

**File:** parachain/runtimes/nexus/src/ismp.rs (L349-352)
```rust
parameter_types! {
	pub const IntentsStorageDepositFee: Balance = EXISTENTIAL_DEPOSIT * 10;
	pub const IntentsPhantomOrderBidWindow: u32 = 25;
}
```
