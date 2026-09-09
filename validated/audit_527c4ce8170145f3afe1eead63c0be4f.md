### Title
Batch withdrawal status misreport due to index-agnostic matching in PoaBridge.describeWithdrawal - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` matches PoA bridge withdrawal status entries only by `assetId` (via `near_token_id`), ignoring the `index` field that is supposed to disambiguate multiple withdrawals of the same asset created in a single NEAR transaction. When a caller batches two or more PoA-bridge withdrawals of the same underlying token (e.g. two BTC withdrawals to different destination addresses in one `processWithdrawal`/`signAndSendWithdrawalIntent` call), every index resolves to the *same* (first) matching entry in the API response, so the status/txHash reported for withdrawal #2 can actually belong to withdrawal #1.

### Finding Description
`findMatchingWithdrawal` explicitly drops index-based matching: [1](#0-0) 

and `describeWithdrawal` calls it using only `args.withdrawalParams.assetId`: [2](#0-1) 

The `WithdrawalIdentifier.index` field exists specifically to let callers distinguish multiple withdrawals stemming from one NEAR transaction: [3](#0-2) 

but the PoA implementation's own comment concedes it does not use it ("Response list is unsorted, so we match by assetId instead of index... NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported"). The same pattern (and the same caveat) is duplicated in the lower-level `internal-utils` helper used by other consumers: [4](#0-3) 

`Array.prototype.find` returns the *first* element satisfying the predicate. If a batch withdrawal (`sdk.processWithdrawal`/`sdk.signAndSendWithdrawalIntent` with a `WithdrawalParams[]`, see `sdk.ts` lines 689-743 and 793-857) includes two entries with the same PoA `assetId` but different `destinationAddress`/`amount`, both indices' `describeWithdrawal`/`watchWithdrawal` calls converge on the same API record — i.e., the status and destination `transfer_tx_hash` reported for withdrawal index 1 is actually the outcome of withdrawal index 0 (or vice versa), regardless of which one truly completed.

This breaks the equality "status/txHash reported for withdrawal N == on-chain outcome of withdrawal N." An integrator using `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`/`processWithdrawal`'s `destinationTx` array to decide when to credit/refund a user could:
- mark the second (still-pending or failed) withdrawal as "completed" using the first withdrawal's `txHash`, prematurely crediting/confirming an unconfirmed transfer, or
- record the wrong destination transaction hash against the wrong withdrawal, corrupting audit/reconciliation records.

### Impact Explanation
This matches the High-severity class "a status or hash misreport making an integrator credit or refund twice." It doesn't require an attacker; it's triggered by ordinary use of the SDK's supported batch-withdrawal feature with two withdrawals of the same token. Because the mismatch happens purely in the client-side status-tracking logic (not on-chain), integrators relying on the SDK to gate crediting logic could confirm/credit the wrong (or not-yet-executed) leg of a batch withdrawal.

### Likelihood Explanation
Likelihood is moderate: the SDK's public API explicitly supports batching multiple `WithdrawalParams` (see `isBatchMode` and array overloads in `shared-types.ts`), and it is plausible for an integrator to withdraw the same PoA-bridge asset to two different destinations (or amounts) in a single batched call. The bug is deterministic and always occurs when ≥2 withdrawals of the same `assetId` are present, with the developers themselves acknowledging the limitation in code comments.

### Recommendation
Match PoA withdrawal status entries using both `assetId` and disambiguating fields (e.g., `destinationAddress` + `amount`, or sort both the API response and the local `withdrawalParams` list by `amount` as the code comment suggests) rather than by `assetId` alone. At minimum, `describeWithdrawal`/`waitForWithdrawalCompletion` should refuse to report `completed` (or should throw) when more than one candidate entry matches the same `assetId` and cannot be disambiguated, instead of silently returning the first match.

### Proof of Concept
1. Call `sdk.processWithdrawal` (or `signAndSendWithdrawalIntent`) with `withdrawalParams: [w0, w1]` where both `w0` and `w1` use the same PoA-bridge `assetId` (e.g. `nep141:btc.omft.near`) but different `destinationAddress`/`amount`.
2. The resulting NEAR tx triggers two PoA bridge withdrawals; the PoA `getWithdrawalStatus` API eventually returns two entries with `near_token_id: "btc.omft.near"` — one `COMPLETED` (for `w0`) and one `PENDING` (for `w1`).
3. `sdk.waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` calls `describeWithdrawal` for index 0 and index 1; `findMatchingWithdrawal` returns the same (first, `COMPLETED`) entry for both indices via `.find(w => nep141:${near_token_id} === assetId)`.
4. Both promises resolve as `{status: "completed", txHash: <w0's tx hash>}`, even though `w1` has not actually completed (or completed to a different destination), causing the caller to treat `w1` as finished with an incorrect `txHash`.

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-427)
```typescript
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	// POA bridge only supports NEP-141 tokens. The API returns `near_token_id`
	// (e.g., "zec.omft.near") which we prefix with "nep141:" to match assetId format.
	// Note: `defuse_asset_identifier` cannot be used as it contains chain-native
	// format (e.g., "zec:mainnet:native") which differs from the assetId format.
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```

**File:** packages/intents-sdk/src/shared-types.ts (L434-441)
```typescript
export interface WithdrawalIdentifier {
	/** Actual chain where funds arrive; Near for virtual/internal routes */
	landingChain: Chain;
	/** Per-bridge withdrawal sequence number */
	index: number;
	withdrawalParams: WithdrawalParams;
	tx: NearTxInfo;
}
```

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L135-153)
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
