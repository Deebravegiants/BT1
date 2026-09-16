### Title
Phantom-bid weight is a spot balance snapshot, letting a solver temporarily inflate its own ERC-20/vault balance to dominate `weightedMedian` and publish an arbitrary pool price - ([File: sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts])

### Summary
`aggregatePhantomBids` prices every phantom order leg by taking the **liquidity-weighted median** of solver quotes, where the weight is each solver's spot balance of the leg's output token (`getTotalSolverBalance` = raw `balanceOf` + ERC-4626 `maxWithdraw`) read at a single, un-pinned "latest" `eth_call` when the bid window closes [1](#0-0) . Because "the solver holding over half the leg's weight sets the published price verbatim" [2](#0-1) , an attacker only needs to hold the balance for the instant the RPC snapshot is taken, not for any meaningful duration — the same "spot-balance-as-price-input" root cause that let the Lodestar attacker manipulate the plvGLP oracle by inflating the `GlpDepositor`'s balance with `donate()` just before the oracle read.

### Finding Description
`getTotalSolverBalance(evmRpcUrl, chain, token, solver, yieldVaults, blockTag = "latest")` sums a solver's raw ERC-20 balance and every configured ERC-4626 vault's `maxWithdraw(solver)` [3](#0-2) . This value becomes each quote's `weight` in `weightedMedian`, and the function's own documentation warns that "a solver holding over half the leg's weight sets the published price verbatim" [4](#0-3) , and that `weightedMedian` is a **selection**, not a blend, returning an input element verbatim [5](#0-4) .

The read is triggered asynchronously by the `PhantomBidWindowExhausted` event on Hyperbridge, then `handlePhantomOrderPrices` calls `aggregatePhantomBids`, which reads solver balances at `"latest"` on the destination chain via `memoizedSolverBalance`/`getTotalSolverBalance` [6](#0-5) . There is no time-weighting, no minimum holding period, and no check that the weight reflects durable inventory rather than a balance parked there for one block. A solver (an ordinary, unprivileged Hyperbridge intents actor — anyone who can sign a `UserOperation` bid) can:

1. Move (or briefly borrow) a large amount of the leg's output token into its own wallet or a configured ERC-4626 vault right before the bid window for a phantom order closes.
2. Submit a signed bid quoting an arbitrary, self-chosen `price` for that leg.
3. Because its `weight` now dominates the leg's total weight, `weightedMedian` returns that attacker-chosen price verbatim, which is then written as `medianPrice = lowestPrice = highestPrice` on the `PhantomOrderPriceSnapshotV2` [7](#0-6) .
4. `updateLiquidityPools` renormalizes that manipulated median into the pool's `sellRate`/`buyRate` (`PoolChainLiquidity`) via a depth-weighted mean across chains [8](#0-7) .
5. The attacker then withdraws/returns the temporarily-parked funds; nothing in the pipeline re-verifies that the weight persisted.

This is structurally identical to the Lodestar exploit: Lodestar's `GLPOracle` derived plvGLP's price from the `GlpDepositor` contract's instantaneous asset balance, which the attacker inflated via `donate()` in the same transaction window as the price read, producing an oracle price nobody could actually trade at. Here, the "oracle" is `weightedMedian`, and the manipulable "balance that drives price" is `getTotalSolverBalance`.

### Impact Explanation
The published `medianPrice`/pool `sellRate`/`buyRate` is consumed by downstream liquidity-routing and pricing consumers (`PoolChainLiquidity`, `updateLiquidityPools`) that other solvers, fillers and the intents ecosystem treat as depth-backed market data [8](#0-7) . An attacker able to set this price verbatim can publish a rate that is either abnormally favorable (to lure real intent flow toward liquidity it cannot actually deliver at that rate, i.e., "a route unable to deliver messages/fills") or abnormally unfavorable (to manipulate downstream consumers relying on the published rate). Because the underlying mechanism explicitly documents that weight is meant to prevent "whoever quotes the extreme set[ting] the rate on zero capital" [4](#0-3) , and the codebase elsewhere goes to considerable lengths (decimals-offset, seed-and-burn, streaming yield) to defend against exactly this class of instantaneous-balance-inflation attack in `StreamingYieldVault.sol` [9](#0-8) , the phantom-aggregation weighting path has no equivalent defense against a transient balance top-up.

### Likelihood Explanation
The attack requires no privileged role — any account able to sign a `UserOperation` bid and hold tokens/vault shares for roughly the duration of one RPC read (the balance is read at "latest", not pinned to a specific historical block for this initial snapshot path) can execute it. The cost is only the capital needed to dominate the leg's total weight for that instant, which can be sourced via a flash loan or a brief self-transfer, since no lock-up or minimum holding period is enforced.

### Recommendation
- Pin the phantom-snapshot balance read to a block that predates the bid submission window (or require a minimum holding duration/checkpointed balance) so a same-window balance top-up cannot retroactively dominate the weight.
- Consider capping any single solver's contribution to a leg's total weight (a "weight cap" analogous to the existing haircuts) so no solver can single-handedly set the verbatim median regardless of transient balance size.
- Cross-check the published price against an independent reference (as already done for Uniswap V4 pool quotes via `referencePrice`/`maxDeviationBps` [10](#0-9) ) before it feeds `sellRate`/`buyRate`.

### Proof of Concept
1. Attacker controls `Solver` and deploys/holds no meaningful long-term inventory of `TOKEN_X` on chain `C`.
2. Shortly before a phantom order's bid window closes on `C`, attacker flash-borrows or self-transfers a large amount of `TOKEN_X` into `Solver`'s wallet (or an ERC-4626 vault counted by `yieldVaults`).
3. Attacker signs and submits a `UserOperation` bid quoting an arbitrary `price` for the leg whose output token is `TOKEN_X`.
4. `PhantomBidWindowExhausted` fires; `aggregatePhantomBids` calls `getTotalSolverBalance` at `"latest"`, sees the inflated balance, and `weightedMedian` returns the attacker's `price` verbatim as `medianPrice`/`lowestPrice`/`highestPrice` [11](#0-10) .
5. `updateLiquidityPools` folds this manipulated median into the pool's published `sellRate`/`buyRate`.
6. Attacker returns/repays the borrowed `TOKEN_X`, leaving the published rate manipulated at negligible lasting cost.

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

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1009-1037)
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

**File:** sdk/packages/sdk/src/protocols/intents/phantom-aggregation.ts (L1523-1536)
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

**File:** sdk/packages/indexer/docs/ai/flows/phantom-price-snapshot-to-pool-rates-phantombidwindowexhausted.md (L1-11)
```markdown
# Phantom price snapshot to pool rates (PhantomBidWindowExhausted)

Verified 2026-08-19 against live mainnet data.

1. `PhantomBidWindowExhausted` on Hyperbridge triggers `handlePhantomOrderPrices` (`src/handlers/events/substrateChains/handlePhantomOrderPrices.handler.ts`). It loads the `PhantomOrderV2` and its registered `PhantomOrderLeg` rows, then calls `aggregatePhantomBids` from the SDK, which fetches every bid for the commitment, verifies each one (solver signature over the userOp hash plus an EIP-7702 delegation check), and reduces them per leg.

   A bid's `paymasterAndData` arrives in one of two shapes, and the SDK's `decodePhantomBidPaymasterAndData` reads both before the declaration is used: the bare declaration blob (every bid until simplex moved to Permit2), or the 234-byte EntryPoint v0.8 payload for the Simplex paymaster's PERMIT2 mode with the declaration appended after the permit (a bid built on simplex's real-bid path since #1223). A sponsored bid with nothing appended counts as having declared nothing — null accepted sources, no positions — the same as an empty field. The solver signature covers the whole field in both shapes, so `recoverBidSignerVm2` is unchanged; `phantom-decode.test.ts` checks the ethers digest over the long payload matches viem's.

   The chain ids in a declaration are decoded in the SDK without `TextDecoder`. That matters here specifically: the handler runs inside SubQuery's vm2 sandbox, where `TextDecoder` is not defined and the `util` fallback rejects a sandbox-created `Uint8Array`, so a decoder reaching for it threw inside the per-bid try/catch of `aggregatePhantomBids` — logged as "Failed to process bid for price snapshot", bid dropped, run continues. That was the whole failure behind bids with a source-chain declaration vanishing from the snapshots (verified 2026-09-09 against the live bids and the deployed indexer's data); `phantom-decode.sandbox.test.ts` runs the shipped bundle inside vm2 to keep it from coming back. A chain with a phantom order but no `solverAccount` in `config-mainnet.json` is skipped with  ... (truncated)

2. Per leg, a solver's quote is weighted by **its balance of that leg's OUTPUT token on the destination chain** — the inventory that actually backs the leg. Zero-weight quotes are dropped entirely, not down-weighted: they never reach the median, `bidCount`, or the bidder list. A leg where no bidder holds the output token is absent from the result, exactly as if nobody quoted it.
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

**File:** sdk/packages/core/contracts/vaults/StreamingYieldVault.sol (L23-42)
```text
/// @title StreamingYieldVault
/// @author Polytope Labs (hello@polytope.technology)
/// @notice An ERC-4626 vault whose yield is supplied by the owner via periodic transfers
///         (`addYield`) and recognized linearly over a fixed window (`VEST`). Because yield
///         is streamed rather than recognized instantly, no single block can be sandwiched
///         around a yield event ("yield sniping"): a same-block deposit/withdraw sees an
///         unchanged share price and captures nothing.
///
/// @dev The exchange rate is `(balanceOf(this) - lockedYield) / totalSupply`. Yield that has
///      not yet vested is masked out of `totalAssets`, so it cannot be claimed early.
///
///      Deposits and mints are disabled while a tranche is vesting. New capital may only enter
///      in the window after a tranche fully vests and before the next `addYield`, so no one can
///      join mid-tranche and capture yield meant for the holders present when it began. `addYield`
///      must wait `MIN_WINDOW` past the vest end, guaranteeing that window exists every cycle
///      regardless of keeper timing.
///
///      When the underlying asset is an ERC-1363 token, the owner can fund a tranche in a single
///      transaction with `asset.transferAndCall(vault, amount)` (no separate `approve` + `addYield`)
///      via the `onTransferReceived` hook, subject to the same authorization and guards as `addYield`.
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
