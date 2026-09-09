### Title
POA Bridge withdrawal status matched only by `assetId`, allowing cross-withdrawal status/hash misreport within a batch - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` matches the POA indexer's withdrawal record to the caller's `withdrawalParams` using only `assetId`, via `findMatchingWithdrawal`. When a single NEAR transaction contains multiple withdrawals of the same token (same `assetId`) to different destinations/amounts, this matching is ambiguous, and the SDK can report the wrong withdrawal's completion status and `txHash` for the queried index.

### Finding Description
`describeWithdrawal` fetches all withdrawals tied to the NEAR tx hash and then selects one via: [1](#0-0) 

The matching function only compares `assetId`, ignoring `amount`, `destinationAddress`, and `index`: [2](#0-1) 

The code comment explicitly acknowledges the limitation ("multiple withdrawals of the same token in a single transaction are not supported"), but nothing in `describeWithdrawal`, `createWithdrawalIdentifier`, or the SDK layer (`sdk.ts`, `withdrawal-watcher`) enforces or validates that a batch does not contain two withdrawals with the same `assetId`. `WithdrawalIdentifier.withdrawalParams` carries `index`, `amount`, and `destinationAddress`, all of which are available but unused for matching.

If a batch withdrawal has two entries with the same `assetId` but different `destinationAddress`/`amount` (e.g., withdrawing the same token to two different recipients in one signed intent), `Array.find` returns the *first* array element in the API response that matches on `assetId` — regardless of which of the two logical withdrawals (`index` 0 or 1) is actually being queried. Because "Response list is unsorted" (per the code's own comment), the mapping between `promises[i]`/`withdrawalParams[i]` and the actual on-chain withdrawal record is not guaranteed correct.

### Impact Explanation
This breaks the equality "status/hash reported == the on-chain outcome for *this specific* withdrawal call." An integrator polling `describeWithdrawal` for withdrawal index 0 (destination A, still pending) could receive the `COMPLETED` status and `txHash` that actually belongs to withdrawal index 1 (destination B, already completed), or vice versa. This can cause an integrator to:
- Credit/mark as completed a withdrawal that has not actually reached its destination (false-positive completion), or
- Report the wrong `txHash` as proof of a specific withdrawal's completion.

Per the finding rules, "a status or hash misreport making an integrator credit or refund twice" is explicitly listed as a High-impact class.

### Likelihood Explanation
This requires a legitimate SDK caller (not necessarily malicious) to construct a batch withdrawal with two or more `WithdrawalParams` sharing the same POA `assetId` (same token) but different destinations/amounts, and then query `describeWithdrawal` per index while both withdrawals are in-flight/at different completion states. This is a realistic usage pattern for batch withdrawal features (`createWithdrawalCompletionPromises`, `waitForWithdrawalCompletion`) documented in the README, since nothing in validation rejects duplicate `assetId` entries in a batch. The likelihood is moderate — it depends on an integrator batching same-token withdrawals to different addresses, which is not an unusual UX pattern (e.g., paying two different users the same token in one intent).

### Recommendation
Update `findMatchingWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` to disambiguate among withdrawals sharing the same `assetId` — e.g., matching by `(assetId, amount, destinationAddress)` tuple, or, if the POA API can return an ordering/`index`-correlated identifier, use that instead of falling back to the first array match. At minimum, when multiple withdrawals in a batch share the same `assetId`, either throw/reject ambiguous matches instead of silently picking the first one, or validate in `createWithdrawalIdentifier`/upstream batch-creation code that duplicate `assetId` entries are disallowed until the POA API/matching logic supports disambiguation.

### Proof of Concept
1. Caller submits a NEAR intents batch withdrawal with two `WithdrawalParams` entries, both `assetId: "nep141:usdc.omft.near"`:
   - index 0: `destinationAddress: "0xAAA..."`, `amount: 100`
   - index 1: `destinationAddress: "0xBBB..."`, `amount: 200`
2. POA bridge processes withdrawal to `0xBBB` first (completes), while withdrawal to `0xAAA` is still pending.
3. Caller invokes `sdk.describeWithdrawal` (or the underlying `PoaBridge.describeWithdrawal`) for `index: 0` with `withdrawalParams` for `0xAAA`.
4. `findMatchingWithdrawal` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427`) scans the unsorted `withdrawals` array and returns the first entry whose `near_token_id` maps to `"nep141:usdc.omft.near"` — which may be the `0xBBB` record, not `0xAAA`.
5. `describeWithdrawal` returns `{ status: "completed", txHash: <0xBBB's tx hash> }` for a request that was semantically about the withdrawal to `0xAAA`, even though that withdrawal is still pending on-chain.

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
