### Title
POA Bridge `describeWithdrawal` misattributes withdrawal status across same-asset withdrawals in a batch - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain outcome for a specific withdrawal index by matching the POA Bridge API response purely by `assetId`, ignoring the `index`/position of the withdrawal within the batch. When a single NEAR transaction contains two or more withdrawals of the same token (e.g. a batch withdrawal splitting the same asset to two different destination addresses), the lookup returns the first matching entry regardless of which withdrawal it actually corresponds to.

### Finding Description
`describeWithdrawal` calls `findMatchingWithdrawal`, which searches the unsorted `withdrawals` array returned by the POA Bridge API for the first entry whose `near_token_id` matches the requested `assetId`: [1](#0-0) 

The lookup helper itself has no notion of the withdrawal's `index` within the batch — it only compares `assetId`: [2](#0-1) 

The code even documents this limitation explicitly: [3](#0-2) 

Because `describeWithdrawal` is invoked once per `WithdrawalIdentifier` (which carries an `index`), but the matching logic disregards that index, two withdrawals of the same `assetId` submitted in one NEAR transaction (a normal, unprivileged batch-withdrawal flow supported by `sdk.createWithdrawalCompletionPromises`, see `docs/design/rfc-batch-withdrawal-granular-control.md`) will both resolve against the same API record. This breaks the equality "the status/tx hash reported for withdrawal N corresponds to the on-chain transfer that actually executed withdrawal N": both promises can report `status: "completed"` with the identical `transfer_tx_hash`, even though only one of the two distinct destination transfers actually happened (or the second is still pending while being reported completed).

### Impact Explanation
An integrator relying on `describeWithdrawal`/`waitForWithdrawalCompletion` to gate crediting/reconciliation per withdrawal index could credit or mark as settled two logically distinct withdrawals (different destination addresses) based on a single actual transfer, i.e., a status/hash misreport causing a double credit — matching the High-impact category "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Requires only that a caller submit a batch of withdrawals containing two or more entries with the same `assetId` in one NEAR transaction — a legitimate, unprivileged usage pattern explicitly supported by the SDK's batch-withdrawal design, not an adversarial precondition. However, the code base already flags this as a known constraint of the current POA API (comment noting "POA API doesn't currently support this case either"), which somewhat limits novelty but does not eliminate the practical risk for any integrator batching same-token withdrawals today.

### Recommendation
Extend `findMatchingWithdrawal` (and the POA API/SDK protocol) to disambiguate withdrawals of the same `assetId` within a batch — e.g., by sorting both the API response and the input `withdrawalParams` by amount as the existing comment suggests, or by requiring the POA API to return a stable per-withdrawal identifier that the SDK can match against `index`, before allowing `describeWithdrawal` to report `completed` for a specific index.

### Proof of Concept
1. Build a NEAR intent transaction with two POA-bridge withdrawal legs for the same `assetId` but different `destinationAddress` (e.g., withdraw 100 USDC to address A and 50 USDC to address B in one tx), using `createWithdrawalCompletionPromises`.
2. Call `bridge.describeWithdrawal` for `index: 0` and `index: 1` with the same `tx.hash`.
3. `getWithdrawalStatusWithRetry` returns both withdrawal records in `response.withdrawals`; `findMatchingWithdrawal` (matching only by `near_token_id`) returns the same first entry for both calls.
4. Both `describeWithdrawal` calls resolve to `{ status: "completed", txHash: <first entry's transfer_tx_hash> }`, even though the second withdrawal to address B is a distinct on-chain transfer that may still be pending or have a different tx hash — the reported status for index 1 does not reflect its actual on-chain outcome.

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L135-143)
```typescript
/**
 * Finds a withdrawal matching the given criteria.
 *
 * NOTE: Currently only matches by assetId (near_token_id). This means multiple
 * withdrawals of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
```

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L144-153)
```typescript
function findMatchingWithdrawal(
	withdrawals: types.WithdrawalStatusResponseOk["result"]["withdrawals"],
	criteria: WithdrawalCriteria,
):
	| types.WithdrawalStatusResponseOk["result"]["withdrawals"][number]
	| undefined {
	return withdrawals.find(
		(w) => `nep141:${w.data.near_token_id}` === criteria.assetId,
	);
}
```
