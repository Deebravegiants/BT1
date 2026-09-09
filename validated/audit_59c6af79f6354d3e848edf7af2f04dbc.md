### Title
`describeWithdrawal` misattributes withdrawal status across same-asset withdrawals in a batch, enabling double-credit - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
The PoA bridge's `findMatchingWithdrawal` function matches an on-chain withdrawal status to a caller's `WithdrawalIdentifier` using only `assetId`, discarding any unique per-withdrawal identifier (index, amount, or destination). This is directly analogous to the reported `PendingDepositRefund` bug: an event/status report lacking the identifier needed to disambiguate between multiple similar operations, allowing an off-chain/integrator consumer to attribute a status update to the wrong operation.

### Finding Description
`PoaBridge.describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does: [1](#0-0) 

The comment explicitly acknowledges the limitation: "multiple withdrawals of the same token in a single transaction are not supported," yet the SDK's batch-withdrawal API does not enforce this — it allows any set of `WithdrawalParams[]` (including duplicate `assetId`s) to be submitted together via `processWithdrawal`/`signAndSendWithdrawalIntent`, and `createWithdrawalIdentifiers` assigns each such withdrawal a distinct `index` per bridge route without validating uniqueness of `assetId`: [2](#0-1) 

When `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` later polls status for each `index` independently, both calls to `describeWithdrawal` for the two same-asset withdrawals resolve to `findMatchingWithdrawal`, which does a `.find()` by `assetId` alone and therefore returns the *same* underlying withdrawal record for both indices: [3](#0-2) 

This breaks the equality that "a status reported must correspond to the actual on-chain outcome of the specific withdrawal being queried" — index 0 and index 1 report identical completion status/txHash even though only one of the two underlying withdrawals has actually settled on the destination chain.

### Impact Explanation
If an integrator uses `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` per-index promises to gate crediting a user (e.g., "credit user once destination tx for withdrawal N is confirmed"), both withdrawals in the batch will be reported `completed` with the same `txHash` as soon as one of them settles. This can cause the integrator to credit/release funds for the second, still-pending withdrawal as if it had already landed — a status misreport leading to double credit, matching the "status or hash misreport making an integrator credit or refund twice" impact class.

### Likelihood Explanation
This requires a batch withdrawal containing two or more `WithdrawalParams` entries with the same `assetId` routed through the PoA bridge — nothing in `createWithdrawalIdentifiers`, `processWithdrawal`, or `signAndSendWithdrawalIntent` rejects this input; it is a valid usage of the documented batch-withdrawal API. Any integrator programmatically constructing batches (e.g., multiple withdrawals of the same token to different addresses/amounts for different users) can trigger this without any malicious action, only normal usage.

### Recommendation
**Short term:** In `findMatchingWithdrawal`, disambiguate withdrawals sharing the same `assetId` using amount/destination ordering (as the code comment itself suggests) instead of returning the first match; alternatively, have `PoaBridge` reject/validate duplicate-`assetId` batches at `createWithdrawalIdentifiers`/`validateWithdrawal` time until proper per-item correlation (e.g., nonce or index) is available from the PoA API.
**Long term:** Require the PoA indexer API to expose a per-withdrawal unique identifier (equivalent to a nonce) tied to the NEAR intent, and use that identifier — not just `assetId` — to correlate status responses to specific `WithdrawalIdentifier`s.

### Proof of Concept
1. Submit a batch withdrawal with two `WithdrawalParams` for the same `assetId` (e.g., `nep141:usdc...`) to two different destination addresses/amounts via the PoA bridge route.
2. `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` for the two withdrawals under the `PoaBridge` route. [4](#0-3) 
3. Call `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`; internally each calls `PoaBridge.describeWithdrawal` for its `WithdrawalIdentifier`.
4. Once the PoA API returns exactly one `COMPLETED` record for that `assetId` (the other still pending), `findMatchingWithdrawal` returns that same record for *both* index-0 and index-1 queries, so both are reported `{status: "completed", txHash: ...}` even though only one has actually settled on-chain. [5](#0-4)

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L80-107)
```typescript
export async function createWithdrawalIdentifiers(args: {
	bridges: Bridge[];
	withdrawalParams: WithdrawalParams[];
	intentTx: NearTxInfo;
}): Promise<{ bridge: Bridge; wid: WithdrawalIdentifier }[]> {
	const indexes = new Map<string, number>();
	const results: { bridge: Bridge; wid: WithdrawalIdentifier }[] = [];

	for (const w of args.withdrawalParams) {
		const bridge = await findBridgeForWithdrawal(args.bridges, w);
		if (bridge == null) {
			throw new BridgeNotFoundError();
		}

		const currentIndex = indexes.get(bridge.route) ?? 0;
		indexes.set(bridge.route, currentIndex + 1);

		const wid = bridge.createWithdrawalIdentifier({
			withdrawalParams: w,
			index: currentIndex,
			tx: args.intentTx,
		});

		results.push({ bridge, wid });
	}

	return results;
}
```
