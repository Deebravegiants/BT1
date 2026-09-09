### Title
`describeWithdrawal()` matches withdrawal status by `assetId` alone, allowing an unrelated withdrawal's completion/tx-hash to be reported for the wrong request - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
This is the strongest reachable analog to the M-28 bug class in scope: a boundary/matching condition is under-constrained, so an outcome (here, a settlement/status report) can be attributed to the wrong request, breaking the equality "the status reported == the on-chain outcome of *this* withdrawal."

### Finding Description
`PoaBridge.describeWithdrawal()` retrieves the list of withdrawals for a NEAR transaction and looks up the one that applies to the current `WithdrawalIdentifier` using `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, matching purely on `assetId`: [1](#0-0) 

The comment explicitly states: "Response list is unsorted, so we match by assetId instead of index" [2](#0-1) . This means that if a single NEAR transaction (or the underlying tx hash used for lookup) produces multiple withdrawals of the **same asset** (e.g. a batch withdrawal with two outputs of the same token, or overlapping withdrawal identifiers being polled with the same `tx.hash`), the function cannot distinguish between them — it will return the first entry whose asset matches, regardless of destination address, amount, or actual index/order. The same weak-matching pattern (`assetId`-only, or its equivalent `withdrawalCriteria`) is used again in `internal-utils`'s `waitForWithdrawalCompletion` / `findMatchingWithdrawal`, which is used to resolve `transfer_tx_hash` and `chain` for a specific withdrawal [3](#0-2) .

In the nouns-builder report, the root cause was a comparison that was insufficiently strict (`<` instead of `<=`), letting a state transition (Defeated vs Succeeded) occur based on an incomplete condition. Here, the analogous flaw is a matching condition that is insufficiently specific (asset only, not the full identity of the withdrawal), letting a "completed" status/tx-hash belonging to a *different* withdrawal request be reported as the outcome for the identifier under test.

### Impact Explanation
If two or more pending withdrawals for the same asset are outstanding at the same time and share (or are queried against) the same underlying `tx.hash`, `describeWithdrawal()`/`watchWithdrawal()` can report the destination tx hash of the wrong withdrawal as `completed` for the identifier being polled: [4](#0-3) . An integrator relying on `waitForWithdrawalCompletion`/`processWithdrawal` to confirm a specific withdrawal's completion (and to release funds, mark an order complete, or refund) could be misled into crediting/confirming completion for a withdrawal that never actually settled — or double-report the same destination hash for two different withdrawal requests. This matches the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
Likelihood depends on the specific shape of the POA Bridge API response (whether it truly can return multiple entries of the same `assetId` for one `tx.hash`/index set) — a detail not fully verifiable from the SDK source alone without the actual bridge API/backend behavior, which is out of scope. Given the code comment acknowledging the list is "unsorted" and explicitly falling back to asset-based matching instead of index-based matching, the maintainers appear aware that index-based matching alone was insufficient, but the replacement (asset-based matching) is still not a full-identity match (no destination address / amount check), leaving the ambiguity only partially resolved.

### Recommendation
Match withdrawals using the full identifying tuple (destination address, amount, and asset) rather than `assetId` alone, or have the POA Bridge API return a client-supplied withdrawal index/ID that is preserved and returned verbatim, ensuring `describeWithdrawal()` binds each reported status/tx-hash unambiguously to the exact withdrawal request that was submitted.

### Proof of Concept
Not independently reproducible from the SDK repository alone since it depends on backend/API response shape (multiple entries for the same asset for a given tx hash) — this would need to be validated against the actual POA Bridge API behavior, which lies outside `packages/intents-sdk` and `packages/internal-utils` source. The code path demonstrating the weak match is: [5](#0-4) .

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-343)
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

		return {
			status: "failed",
			reason: withdrawal.status,
		};
	}
```

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L52-84)
```typescript
			const result = await getWithdrawalStatus(
				{ withdrawal_hash: txHash },
				{ baseURL, fetchOptions: { signal }, logger },
			);

			const withdrawal = findMatchingWithdrawal(
				result.withdrawals,
				withdrawalCriteria,
			);
			if (withdrawal == null) {
				throw new PoaWithdrawalInvariantError(
					"POA Bridge didn't return withdrawal matching criteria",
					result,
					txHash,
					withdrawalCriteria,
				);
			}

			if (withdrawal.status === "COMPLETED") {
				if (withdrawal.data.transfer_tx_hash == null) {
					throw new PoaWithdrawalInvariantError(
						"POA Bridge didn't return transfer_tx_hash for COMPLETED withdrawal",
						result,
						txHash,
						withdrawalCriteria,
					);
				}

				return {
					destinationTxHash: withdrawal.data.transfer_tx_hash,
					chain: withdrawal.data.chain,
				};
			}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L32-47)
```typescript
	try {
		return await poll(
			async () => {
				try {
					const status = await args.bridge.describeWithdrawal({
						...args.wid,
						logger: args.logger,
					});

					consecutiveErrors = 0;

					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}
```
