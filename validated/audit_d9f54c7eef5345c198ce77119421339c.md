### Title
Cross-chain order confirmation policy defaults to a 2-block reorg window, letting a source-chain reorg strand the solver's destination payout - ([File: sdk/packages/simplex/src/config/interpolated-curve.ts])

### Summary
Hyperbridge's Simplex intent solver decides how many source-chain confirmations to wait for before committing capital on the destination chain using `ConfirmationPolicy`/`DEFAULT_CONFIRMATION_POLICIES`. For every supported chain — including Ethereum mainnet — the minimum confirmation depth for orders is hard-coded to just **2 blocks**, regardless of the chain's actual reorg risk. This mirrors the reported bug class: an "ETHBlockDelay" (here, confirmation depth) that is too small relative to the profitability of reorging makes it economically rational for a block proposer/builder to reorg the chain after the solver has acted on the observed event.

### Finding Description
`DEFAULT_CONFIRMATION_POLICIES` fixes the low end of every chain's curve at 2 blocks for orders around $1,000 USD: [1](#0-0) 

This curve is the sole gate a solver uses before treating a source-chain `OrderPlaced`/fill event as final and committing capital cross-chain: `requiredConfirmations` is derived from `strategy.confirmationPolicy.getConfirmationBlocks(sourceChainId, inputUsdValue)`, and the solver simply polls `getTransactionConfirmations` until that (small) threshold is met before proceeding to `executeOrder`: [2](#0-1) [3](#0-2) 

The docs explicitly frame this 2-block minimum as the reorg-safety mechanism ("Simplex waits for enough block confirmations to guard against chain reorganizations"), yet acknowledge that a cross-chain fill is evaluated purely "from the solver's own reading of source-chain state," with "no on-chain safety net to catch it after the fact": [4](#0-3) [5](#0-4) 

Two blocks on Ethereum mainnet is only ~24 seconds — far short of any meaningful finality margin (Ethereum epoch/Casper-FFG finality is ~12-15 minutes) and well within the range of known low-cost reorg techniques (e.g., proposer-boost-adjacent single/two-slot reorgs by a colluding or MEV-incentivized validator/builder). On BSC it is ~6 seconds; the protocol's own BSC light client design treats a two-consecutive-justified-vote requirement as the bar for true finality precisely because a single justified block is still "reorg-able" — the same standard is not applied here to the solver's own confirmation gate: [6](#0-5) 

An attacker who can influence block production for even a short window (a validator, a colluding builder, or a chain with weaker/no fast finality) can place a qualifying order (any amount priced at or near the curve's minimum), let the solver observe the source-chain event, wait exactly 2 confirmations, get the solver to `executeOrder` and disburse funds on the destination chain, then reorg those 2 blocks away on the source chain so the original order-placing transaction (and the funds backing it) never actually lands. The solver has already paid out; there is no recovery path once the destination payout is made.

### Impact Explanation
This is a direct theft vector against solver capital: the solver commits destination-chain funds based on a source-chain observation that is reversible within the configured confirmation window. Because the 2-block floor applies uniformly regardless of the source chain's true reorg-resistance, it systematically under-prices reorg risk on any chain whose realistic reorg depth exceeds 2 blocks (which includes Ethereum L1 itself). Successful exploitation causes concrete loss of solver funds with no on-chain fallback, matching a Medium-severity "possible incentive for reorgs" finding.

### Likelihood Explanation
Likelihood is bounded by the attacker needing some capability to reorg 1-2 blocks on the source chain (validator/builder collusion, MEV extraction, or weaker consensus chains), which is exactly the profile the original report describes as "not totally out of the question... with MEV at all time highs." The bar to trigger the vulnerable path itself is low: any unprivileged user can place a small cross-chain order that only requires the curve's 2-block minimum, with no special permissions needed.

### Recommendation
Do not let the confirmation floor drop below a chain-appropriate reorg-safety margin. For chains without deterministic fast finality (Ethereum L1, BSC's merely-justified state, general PoS chains), the minimum confirmation depth should be tied to actual finality guarantees (e.g., Casper-FFG epoch finality, or the two-consecutive-justified-vote rule already used for BSC) rather than a flat 2-block floor for small orders. Consider disallowing execution until source-chain finality (not just N confirmations) for any order value, or substantially raising the low end of `DEFAULT_CONFIRMATION_POLICIES` for chains like Ethereum and BSC.

### Proof of Concept
1. Attacker (or a colluding block proposer/builder) submits a small cross-chain order (~$1,000) on Ethereum mainnet, which per `DEFAULT_CONFIRMATION_POLICIES["1"]` requires only 2 confirmations.
2. Simplex's filler observes the `OrderPlaced` event, waits for `getTransactionConfirmations` to reach 2 (`sdk/packages/simplex/src/core/filler.ts` lines 767-811), and calls `executeOrder`, paying out on the destination chain.
3. Within the ~24-second window, the attacker (or colluding proposer) reorgs the 2 blocks containing the order transaction, removing the source-chain deposit/event.
4. The solver has already disbursed destination-chain funds against an order that no longer exists on the source chain, resulting in a net loss to the solver.

### Citations

**File:** sdk/packages/simplex/src/config/interpolated-curve.ts (L26-63)
```typescript
export const DEFAULT_CONFIRMATION_POLICIES: Record<string, CurveConfig> = {
	"1": {
		points: [
			{ amount: "1000", value: 2 },
			{ amount: "100000", value: 15 },
		],
	}, // Ethereum (~12s blocks, ~24s–3min)
	"56": {
		points: [
			{ amount: "1000", value: 2 },
			{ amount: "100000", value: 3 },
		],
	}, // BNB Chain (~3s blocks, fast finality)
	"137": {
		points: [
			{ amount: "1000", value: 2 },
			{ amount: "100000", value: 5 },
		],
	}, // Polygon (~2s blocks; milestone finality lands in ~5s, so 5 blocks ≈ 10s covers it)
	"8453": {
		points: [
			{ amount: "1000", value: 2 },
			{ amount: "100000", value: 90 },
		],
	}, // Base (~2s blocks, L2)
	"42161": {
		points: [
			{ amount: "1000", value: 8 },
			{ amount: "100000", value: 720 },
		],
	}, // Arbitrum (~0.25s blocks, L2)
	"130": {
		points: [
			{ amount: "1000", value: 2 },
			{ amount: "100000", value: 180 },
		],
	}, // Unichain (~1s blocks, OP-stack L2 — time-equivalent to Base's curve)
}
```

**File:** sdk/packages/simplex/src/core/filler.ts (L745-754)
```typescript
					for (const [strategy, canFill] of canFillCache) {
						if (!canFill || !strategy.confirmationPolicy) continue
						requiredConfirmations = Math.max(
							requiredConfirmations,
							strategy.confirmationPolicy.getConfirmationBlocks(
								getChainId(order.source)!,
								inputUsdValue.toNumber(),
							),
						)
					}
```

**File:** sdk/packages/simplex/src/core/filler.ts (L792-820)
```typescript
					while (currentConfirmations < requiredConfirmations) {
						if (abortController.signal.aborted) return
						await new Promise((resolve) => setTimeout(resolve, confirmationPollMs))
						if (abortController.signal.aborted) return
						currentConfirmations = await retryPromise(
							() =>
								sourceQuorumClient.getTransactionConfirmations({
									hash: transactionHash as HexString,
								}),
							{
								maxRetries: 3,
								backoffMs: 250,
								logMessage: "Failed to get transaction confirmations",
							},
						)
						this.logger.debug({ orderId: order.id, currentConfirmations }, "Order confirmation progress")
					}

					this.logger.info({ orderId: order.id, currentConfirmations }, "Order confirmed on source chain")
				}

				// Run confirmation and evaluation in parallel
				const [, evaluationResult] = await Promise.all([
					waitForConfirmations(),
					this.evaluateOrder(order, canFillCache).then((result) => {
						if (!result) abortController.abort()
						return result
					}),
				])
```

**File:** docs/content/developers/evm/simplex/confirmations.mdx (L10-12)
```text
## Confirmation Policy

Before processing a cross-chain order, Simplex waits for enough block confirmations to guard against chain reorganizations. The number of confirmations scales with order value using a curve — small orders are processed quickly, large orders wait longer. Same-chain orders always proceed without additional confirmation delay.
```

**File:** docs/content/developers/evm/simplex/confirmations.mdx (L76-78)
```text
### Why this matters for cross-chain orders

On a cross-chain fill, Simplex observes an `OrderPlaced` (or `PartialFill` / `OrderFilled`) event on the source chain and then commits capital on the destination chain. Unlike same-chain fills — where the destination `fillOrder` call will revert if the source-chain order does not exist — cross-chain bids submitted through Hyperbridge are evaluated from the solver's own reading of source-chain state. A single RPC is therefore both an availability and an integrity choke point: if it lies about which orders were placed, the solver can be induced to pay out against events that never happened, and there is no on-chain safety net to catch it after the fact.
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L101-111)
```rust
	// BEP-126 fast finality only *finalizes* `source_header` once the justified
	// `target_header` is its direct child (two consecutive justified blocks). A
	// supermajority-signed but non-adjacent vote justifies `target_header` yet
	// leaves `source_header` merely justified and still reorg-able, so committing
	// its state root as a finalized BSC state commitment would be unsound.
	if update.target_header.number.low_u64() !=
		update.source_header.number.low_u64().saturating_add(1) ||
		update.target_header.parent_hash.0 != source_header_hash.0
	{
		Err(Error::NonConsecutiveFinalization)?
	}
```
