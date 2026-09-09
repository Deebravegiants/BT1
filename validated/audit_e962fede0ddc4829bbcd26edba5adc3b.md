## Analog Vulnerability Found

### Title
POA Bridge withdrawal status matches by `assetId` only, ignoring `index`, causing wrong status/txHash to be reported for batched same-asset withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` and the underlying `waitForWithdrawalCompletion` helper resolve the on-chain outcome of a specific withdrawal by matching bridge API records solely on `assetId`, discarding the `index` that uniquely identifies which withdrawal within a batch a caller is asking about. When a single NEAR intent transaction contains two or more withdrawals of the same token to different destination addresses, every `WithdrawalIdentifier` for that token resolves to the same (first) matching record, so the reported `status`/`txHash` for one withdrawal is silently substituted for another.

### Finding Description
`describeWithdrawal` looks up the withdrawal record with: [1](#0-0) 
and the matcher itself: [2](#0-1) 

The comment explicitly acknowledges the limitation ("multiple withdrawals of the same token in a single transaction are not supported"), but nothing in `Bridge.createWithdrawalIntents`, `createWithdrawalIdentifiers`, or the public `processWithdrawal`/`waitForWithdrawalCompletion` APIs rejects or warns against this input shape — a caller can legitimately submit `WithdrawalParams[]` with two entries sharing the same `assetId` but different `destinationAddress`, and the SDK will happily create two `WithdrawalIdentifier`s (`index: 0` and `index: 1`) for them via: [3](#0-2) 

Both identifiers carry the *same* `assetId`, but `findMatchingWithdrawal` (used both in `poa-bridge.ts` and again in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) uses `Array.prototype.find`, which always returns the *first* array element matching the asset — the `index` field on `WithdrawalIdentifier` is never consulted: [4](#0-3) 

Consequently, when `watchWithdrawal`/`waitForWithdrawalCompletion` is invoked once per withdrawal identifier (as the batch orchestration in `sdk.ts` does), the call for `index: 1` receives the exact same API record (same `status`, same `transfer_tx_hash`) as the call for `index: 0`, even though they represent two distinct withdrawals going to two different destination addresses/amounts.

### Impact Explanation
This breaks the equality "status/hash reported == the actual on-chain outcome for *that specific* withdrawal." An integrator that batches two same-token withdrawals in one intent (e.g., paying out two different customers/addresses the same asset) will see both withdrawals reported as `completed` with the identical `txHash` once the *first* one lands on-chain, even though the second one may still be pending or use a different destination. This can cause an integrator to prematurely mark the second withdrawal as settled/credited based on a transaction that actually paid the first destination — a status/hash misreport that can lead to double-crediting or under-payment reconciliation errors, matching the "status or hash misreport making an integrator credit or refund twice" impact class.

### Likelihood Explanation
No privileged or malicious actor is required — this triggers purely from a normal, permitted SDK usage pattern (batch withdrawal of the same asset to different destinations in a single call), which the public `WithdrawalParams[]` API and `Bridge` interface do not prevent. The bug is deterministic whenever such a batch is used and POA bridge is the resolved route for that asset.

### Recommendation
Match withdrawal records using an unambiguous key that accounts for the intra-transaction `index` (e.g., pair `near_token_id`/`assetId` with `destinationAddress` and `amount`, or require the POA bridge API to return an ordinal/nonce per withdrawal within a transaction and match against `WithdrawalIdentifier.index`). Until the POA API supports this, `PoaBridge.supports`/`validateWithdrawal` (or the SDK's batch orchestration) should detect and reject/flag batches containing multiple withdrawals of the same `assetId` in one transaction rather than silently returning a possibly-wrong status.

### Proof of Concept
1. Caller submits a batch withdrawal via `sdk.processWithdrawal`/`signAndSendWithdrawalIntent` with `withdrawalParams = [{assetId: "nep141:usdc.omft.near", destinationAddress: "0xAAA", amount: 100}, {assetId: "nep141:usdc.omft.near", destinationAddress: "0xBBB", amount: 200}]`.
2. `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` to the two withdrawals for the `PoaBridge` route: [5](#0-4) 
3. The POA bridge processes the two withdrawals and, once the first (to `0xAAA`) completes, the API returns one `COMPLETED` record with `near_token_id = usdc.omft.near` and `transfer_tx_hash = 0xfinal1`, while the second (to `0xBBB`) is still `PENDING`.
4. `watchWithdrawal` is called separately for `index: 0` and `index: 1`; both calls invoke `PoaBridge.describeWithdrawal`, which calls `findMatchingWithdrawal(response.withdrawals, "nep141:usdc.omft.near")` — for **both** identifiers this returns the *same* completed record (`0xfinal1`) because matching ignores `index`.
5. The integrator's completion promise for withdrawal index 1 (destined for `0xBBB`) resolves as `{status: "completed", txHash: "0xfinal1"}` even though `0xBBB` never received funds — a misreport that could cause the integrator to credit/settle the wrong withdrawal.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-326)
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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L144-152)
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
```
