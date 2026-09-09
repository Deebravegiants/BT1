### Title
`OmniBridge.describeWithdrawal` selects a transfer by raw array position instead of matching it to the withdrawal being tracked, allowing a status/tx-hash misreport for a different withdrawal - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.describeWithdrawal` fetches all transfers for a NEAR transaction hash and picks the entry at `args.index` with no verification that the transfer actually corresponds to the withdrawal being polled (its `destinationAddress`, `amount`, or `assetId`). This is the same class of bug as `Merkle.checkMembership`: a positional/index parameter is trusted without validating it actually maps uniquely and correctly to the claimed data, which lets the equality "reported status/tx-hash == the on-chain outcome of *this* withdrawal" be broken.

### Finding Description
`describeWithdrawal` in `OmniBridge` does: [1](#0-0) 

```
async describeWithdrawal(
    args: WithdrawalIdentifier & { logger?: ILogger },
): Promise<WithdrawalStatus> {
    const transfer = (
        await this.omniBridgeAPI.getTransfer({
            transactionHash: args.tx.hash,
        })
    )[args.index];

    if (transfer == null || transfer.recipient == null) {
        return { status: "pending" };
    }
    ...
```

It indexes directly into the array returned by the external Omni Bridge indexer (`omniBridgeAPI.getTransfer`) using `args.index`, then reports the `finalised.transaction_hash` (or `utxo_meta.pending_sign_id`) of *whatever transfer happens to be at that position* as the completion hash for the withdrawal being tracked — without cross-checking `transfer.recipient` against `args.withdrawalParams.destinationAddress`, or `transfer.amount`/`transfer.token_id` against the expected asset/amount.

This is notably different from the sibling `PoaBridge.describeWithdrawal`, which explicitly avoids trusting array order and instead matches on content: [2](#0-1) 

```
async describeWithdrawal(
    args: WithdrawalIdentifier & { logger?: ILogger },
): Promise<WithdrawalStatus> {
    const response = await this.getWithdrawalStatusWithRetry(args);

    // Response list is unsorted, so we match by assetId instead of index
    const withdrawal = findMatchingWithdrawal(
        response.withdrawals,
        args.withdrawalParams.assetId,
    );
```

The `poa-bridge` code comment ("Response list is unsorted, so we match by assetId instead of index") shows the codebase is already aware that trusting positional order from an external indexer is unsafe — yet `OmniBridge.describeWithdrawal` does exactly that unsafe thing: it trusts `args.index` as a stable, correct pointer into an externally-returned, order-dependent array, with no equivalent content-based disambiguation (e.g., matching `transfer.recipient` to `args.withdrawalParams.destinationAddress`).

For a single NEAR transaction that triggers multiple `ft_withdraw` calls through the Omni Bridge (a realistic scenario supported by the SDK's batch-withdrawal APIs, e.g. `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` which call `describeWithdrawal` once per withdrawal `index` for the same `tx.hash`), the indexer's returned array order is not guaranteed by this client code to match the intra-transaction call order. If the indexer's ordering differs from the SDK's assumed ordering (e.g., due to processing/finalization timing, internal sort keys, or partial results), `describeWithdrawal(index=i)` can silently return a `transfer` belonging to a *different* withdrawal in the same batch.

### Impact Explanation
If the wrong transfer is selected:
- The SDK can report `{status: "completed", txHash: X}` for withdrawal *i* where `X` is actually the destination transaction hash of withdrawal *j* (different recipient/amount/asset). An integrator relying on this status (e.g., to mark a user's withdrawal as settled, release funds, or close out an off-chain balance) would credit/mark-complete the wrong withdrawal, or credit the same on-chain event to two different tracked withdrawals — a status misreport that can cause an integrator to double-credit or wrongly confirm settlement, consistent with the "status or hash misreport making an integrator credit or refund twice" High-impact category in scope.
- It could also cause the actually-completed withdrawal to be reported "pending" indefinitely (masking completion) while another unrelated withdrawal is reported completed, leading to confused reconciliation and potential duplicate payouts by the integrator.

### Likelihood Explanation
Likelihood depends entirely on whether `@omni-bridge/core`'s `BridgeAPI.getTransfer` guarantees a stable, call-order-preserving array for a multi-transfer NEAR transaction. That guarantee lives in the third-party `@omni-bridge/core` package (out of scope for direct code inspection here), so I could not confirm from in-scope code whether the ordering assumption actually holds in production. The in-scope code itself provides **no defense** against a reordering (no recipient/amount/asset cross-check), which is the actionable, in-scope defect — analogous to `Merkle.checkMembership` trusting the caller-supplied index without validating it against the proof/tree structure. Given the project's own comment in `poa-bridge.ts` acknowledging that "the response list is unsorted" for a very similar external status API, it is plausible the Omni Bridge indexer has the same characteristic, making this a realistic risk rather than a purely theoretical one. However, without visibility into the exact `@omni-bridge/core` guarantees, I cannot state with certainty that reordering is currently observed in production — this should be verified against the `@omni-bridge/core` package/API contract.

### Recommendation
In `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`, `describeWithdrawal` should not rely solely on positional indexing into `omniBridgeAPI.getTransfer(...)`. Instead, mirror the `poa-bridge.ts` approach: filter/match the returned transfers by content that uniquely identifies the withdrawal being tracked (e.g., `transfer.recipient` compared against `omniAddress(destinationChain, args.withdrawalParams.destinationAddress)`, and optionally `transfer.amount`/`transfer.token_id` against the expected values), falling back to `args.index` only as a tiebreaker among transfers that already match on content. If no matching transfer is found, return `{status: "pending"}` rather than defaulting to positional selection.

### Proof of Concept
Conceptual reproduction (cannot be executed without access to `@omni-bridge/core`/live indexer behavior, but demonstrated via the existing test structure):
1. A single NEAR transaction contains two batched `ft_withdraw` intents: withdrawal A (destination `0xAAAA...`, amount 100) and withdrawal B (destination `0xBBBB...`, amount 200).
2. The SDK calls `describeWithdrawal({index: 0, tx, withdrawalParams: A...})` and `describeWithdrawal({index: 1, tx, withdrawalParams: B...})` to track each independently (as shown in `sdk.waitForWithdrawalCompletion.test.ts`, which asserts `describeWithdrawal` is called with `index: 0`, `1`, `2` for a batch — see [3](#0-2)  ).
3. `omniBridgeAPI.getTransfer({transactionHash: tx.hash})` returns `[transferB, transferA]` (order swapped relative to the SDK's assumed call order — e.g., due to indexer internal ordering).
4. `describeWithdrawal({index: 0, ...A})` returns `transferB`'s data — reporting withdrawal A as completed with the transaction hash that actually belongs to withdrawal B's destination transfer, because no recipient/amount check is performed at [4](#0-3) .
5. An integrator polling withdrawal A sees `{status: "completed", txHash: <B's hash>}` and marks A settled/credited even though A's own on-chain transfer may still be pending or went elsewhere — a status misreport not backed by the actual on-chain outcome for that specific withdrawal.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-702)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const transfer = (
			await this.omniBridgeAPI.getTransfer({
				transactionHash: args.tx.hash,
			})
		)[args.index];

		if (transfer == null || transfer.recipient == null) {
			return { status: "pending" };
		}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-322)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const response = await this.getWithdrawalStatusWithRetry(args);

		// Response list is unsorted, so we match by assetId instead of index
		const withdrawal = findMatchingWithdrawal(
			response.withdrawals,
			args.withdrawalParams.assetId,
		);
```

**File:** packages/intents-sdk/src/sdk.waitForWithdrawalCompletion.test.ts (L99-123)
```typescript
	it("maintains indexes specific to bridge route", async () => {
		const { sdk, mockBridge } = setupMocks();

		vi.mocked(mockBridge.describeWithdrawal).mockResolvedValue({
			status: "completed",
			txHash: "fake-dest-hash",
		});

		await sdk.waitForWithdrawalCompletion({
			intentTx: { accountId: "foo.near", hash: "fake-hash" },
			withdrawalParams: [withdrawalParams, withdrawalParams, withdrawalParams],
		});

		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			1,
			expect.objectContaining({ index: 0 }),
		);
		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			2,
			expect.objectContaining({ index: 1 }),
		);
		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			3,
			expect.objectContaining({ index: 2 }),
		);
```
