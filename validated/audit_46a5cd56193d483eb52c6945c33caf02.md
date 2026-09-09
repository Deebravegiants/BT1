### Title
`OmniBridge.describeWithdrawal` reports withdrawal status by array index instead of matching recipient/amount, allowing a status/txHash misreport for batched withdrawals - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
The external report describes a class of bug where an unvalidated/untrusted value (a future slot number) is accepted and later causes a mismatch between what was requested and what is actually applied, corrupting downstream state. The same equality-breaking pattern exists in `OmniBridge.describeWithdrawal`: it indexes into the bridge indexer's `getTransfer()` result array positionally, and reports "completed" with a `txHash` without ever verifying that the returned transfer's `recipient`/amount corresponds to the specific withdrawal (`args.withdrawalParams.destinationAddress`, `amount`) being queried.

### Finding Description
In `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`, `describeWithdrawal` does: [1](#0-0) 

It fetches all transfers for a given NEAR transaction hash and picks one purely by array position (`[args.index]`), then reports `status: "completed"` together with the on-chain `txHash` as soon as a `finalised?.transaction_hash` (or `pending_sign_id`) is present — with no check that `transfer.recipient` equals `args.withdrawalParams.destinationAddress`, nor that any amount matches the requested withdrawal.

This is significant because a single NEAR transaction can batch multiple withdrawal intents (multiple `ft_withdraw`/`mt_withdraw` calls), each tracked by its own `WithdrawalIdentifier.index`. The indexer's returned array is not guaranteed to preserve the exact submission order the SDK assumed when it created the `WithdrawalIdentifier` — e.g., if the indexer omits a still-pending/failed transfer, reorders entries, or a batch is partially processed, the array positions shift. This is the same equality-omission bug class as `ProcessProposal` failing to check `req.Height >= blk.Slot`: an externally supplied value (the indexer's transfer array ordering) is trusted as if it corresponds 1:1 to the caller's expectations, with no explicit correlation check.

Contrast this with `PoaBridge.describeWithdrawal`, which explicitly matches by `assetId` rather than by index, with an inline comment stating exactly why: [2](#0-1) 

This shows the codebase authors were aware that index-based matching for multi-transfer NEAR transactions is unsafe, yet `OmniBridge.describeWithdrawal` still relies on positional indexing without any recipient/amount correlation check.

### Impact Explanation
If `describeWithdrawal` reports `status: "completed"` with a `txHash` belonging to a different transfer within the same batched NEAR transaction (wrong recipient/amount), an integrator using this SDK method to decide when a withdrawal has landed on the destination chain could:
- Mark the wrong withdrawal as completed and release/credit funds or clear a pending state for a withdrawal that has not actually landed (mismatch between reported outcome and actual on-chain outcome).
- In the worst case, if two withdrawals in the same batch are both eventually indexed, an integrator polling `describeWithdrawal` per index could momentarily see the same `txHash` reported for the wrong index, or see completion status attached to the wrong destination/amount pairing, matching the "status reported that is not the on-chain outcome" impact category (crediting/finalizing based on a false completion signal).

### Likelihood Explanation
This requires the SDK caller to have submitted a batched NEAR transaction with multiple withdrawal intents processed by the Omni Bridge, and for the indexer's transfer list to not align 1:1, in order, with the intents as submitted (e.g., differing finalization timing, indexer re-ordering, or omission of transfers still pending). No malicious actor input is required — this is a data-integrity/correlation gap reachable by any user who batches multiple Omni Bridge withdrawals in one transaction, similar in spirit to how the original slot-number report required no special privilege beyond normal block proposal.

### Recommendation
In `OmniBridge.describeWithdrawal`, do not rely solely on `args.index` into the `getTransfer()` array. Correlate the picked transfer against `args.withdrawalParams` (destination address, asset/token, and amount) the same way `PoaBridge.findMatchingWithdrawal` does by `assetId`, and only report `status: "completed"` when the transfer's recipient/amount actually corresponds to the withdrawal being described. If no matching transfer is found, return `{ status: "pending" }` instead of assuming positional correspondence.

### Proof of Concept
Conceptual PoC (based on `omni-bridge.test.ts` patterns already in the repo, e.g. lines 371-454):
1. Submit one NEAR transaction containing two Omni Bridge withdrawal intents in a batch: index 0 → destination A / amount X, index 1 → destination B / amount Y.
2. Have the Omni Bridge indexer's `getTransfer({transactionHash})` return the two transfers in reversed order (or with one entry temporarily missing then appearing later in a different slot), which is plausible since the indexer response ordering is not contractually guaranteed to match submission order (as acknowledged by the analogous fix already present in `PoaBridge.describeWithdrawal`'s comment "Response list is unsorted, so we match by assetId instead of index").
3. Call `describeWithdrawal({ index: 0, withdrawalParams: { destinationAddress: A, amount: X, ... }, tx })`.
4. Because `describeWithdrawal` in `omni-bridge.ts` only does `(await this.omniBridgeAPI.getTransfer(...))[args.index]` and checks `transfer.recipient == null` — never comparing `transfer.recipient` to `A` or any amount to `X` — it returns `{ status: "completed", txHash: <hash for B's transfer> }`, misreporting completion/txHash for withdrawal A using the outcome that actually belongs to withdrawal B.

### Citations

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-731)
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

		const destinationChain = getChain(transfer.recipient as OmniAddress);
		let txHash = null;
		if (
			isEvmChain(destinationChain) ||
			destinationChain === ChainKind.Sol ||
			destinationChain === ChainKind.Fogo ||
			destinationChain === ChainKind.Strk ||
			destinationChain === ChainKind.Aptos
		) {
			txHash = transfer.finalised?.transaction_hash;
		} else if (isUtxoChain(destinationChain)) {
			// pending_sign_id is not the finalised tx hash. In rare cases, the hash may
			// change if the BTC transfer fails to be submitted. We return fast hash for FE and
			// wait for final one (transfer.finalised?.transaction_hash) for BE.
			txHash =
				typeof window !== "undefined"
					? transfer.utxo_meta?.pending_sign_id
					: transfer.finalised?.transaction_hash;
		} else {
			return { status: "completed", txHash: null };
		}

		if (!txHash) {
			return { status: "pending" };
		}

		return { status: "completed", txHash };
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-337)
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

		if (withdrawal == null) {
			return { status: "pending" };
		}

		if (withdrawal.status === "PENDING") {
			return { status: "pending" };
		}

		if (withdrawal.status === "COMPLETED") {
			return {
				status: "completed",
				txHash: withdrawal.data.transfer_tx_hash,
			};
		}
```
