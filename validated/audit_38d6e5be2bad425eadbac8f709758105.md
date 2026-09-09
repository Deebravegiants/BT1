Confirmed: `createWithdrawalIdentifiers` in `withdrawal-watcher.ts` assigns an `index` per withdrawal but PoA Bridge's `describeWithdrawal` ignores that index entirely and matches by `assetId` only via `findMatchingWithdrawal`.

### Title
Batch withdrawals of the same asset are matched by assetId only, causing wrong-withdrawal status/txHash to be reported to the caller - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
For batch withdrawals through the PoA bridge, `describeWithdrawal()` looks up the matching withdrawal from the bridge API response using only `assetId` [1](#0-0) , via `findMatchingWithdrawal` which filters solely by `nep141:${w.data.near_token_id} === assetId` [2](#0-1) . It never uses `amount`, `destinationAddress`, or the `index` that the SDK assigns per-withdrawal in `createWithdrawalIdentifiers` [3](#0-2) .

### Finding Description
When a caller submits a batch withdrawal containing two or more withdrawals of the **same** `assetId` (e.g. two separate USDT withdrawals to two different destination addresses in one intent), `Array.prototype.find` returns the **first** array entry matching that `assetId`, regardless of which of the batch entries it actually corresponds to. Both `watchWithdrawal` (single-withdrawal polling, invoked once per index in `withdrawal-watcher.ts`) and `waitForWithdrawalCompletion` in `internal-utils` exhibit the identical pattern [4](#0-3) . Since the code comment explicitly acknowledges "multiple withdrawals of the same token in a single transaction are not supported" [5](#0-4) , the SDK still allows batch withdrawal params with duplicate assetIds to be created and polled per-index (`createWithdrawalIdentifiers` assigns increasing indexes per bridge route, not deduplicating by assetId+destination) [6](#0-5) , but the description/status lookup silently collapses to one entry.

The equality broken: "the withdrawal identifier (destination + amount) whose status is reported" is not equal to "the withdrawal identifier the caller actually asked about" — the SDK reports the txHash/status of an arbitrary other batch entry with the same asset.

### Impact Explanation
If an integrator relies on `describeWithdrawal`/`waitForWithdrawalCompletion` per withdrawal index to confirm delivery and release/credit downstream funds (e.g., crediting a user account after seeing "completed" with a txHash), a batch containing two same-asset withdrawals to different recipients can cause the integrator to see the same "completed" status/txHash for both entries. This can lead to a double credit: the integrator credits withdrawal #2 believing it's completed (because it matched withdrawal #1's completion), while #2's real transfer might still be pending or might go to a different address than expected. This matches the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
Likelihood is limited by whether callers actually submit batch withdrawals with duplicate `assetId`s to different destinations — the SDK's batch withdrawal API allows arbitrary combinations of `withdrawalParams`, and nothing in `createWithdrawalIntents`/`signAndSendWithdrawalIntent` rejects duplicate assetIds within a batch. The bug is a code-acknowledged limitation rather than a hidden edge case, and it requires no malicious actor — just a normal, unprivileged caller constructing a batch withdrawal with two same-token entries.

### Recommendation
Reject batch withdrawals containing duplicate `assetId`s destined to the PoA bridge until the underlying POA API supports disambiguation, or match returned withdrawals using amount+destinationAddress (or ordinal position, sorted consistently, as suggested in the existing code comment) instead of `assetId` alone, so each `WithdrawalIdentifier.index` maps deterministically to the correct API entry.

### Proof of Concept
1. Caller submits `signAndSendWithdrawalIntent` with `withdrawalParams: [{assetId:"nep141:usdt.omft.near", amount:100, destinationAddress:"0xAAA...", feeInclusive:false}, {assetId:"nep141:usdt.omft.near", amount:100, destinationAddress:"0xBBB...", feeInclusive:false}]`.
2. `createWithdrawalIdentifiers` assigns index 0 and 1 to the two entries, both routed to `PoaBridge` [7](#0-6) .
3. POA bridge processes and completes withdrawal to `0xAAA...` first, returning it as `COMPLETED` with `transfer_tx_hash: "0xtxA"`; `0xBBB...` is still `PENDING`.
4. Caller polls `describeWithdrawal` for index 1 (`0xBBB...`). `findMatchingWithdrawal` filters by `assetId` only and returns the first array element — which may be the `0xAAA...` entry — reporting `{status:"completed", txHash:"0xtxA"}` for the `0xBBB...` withdrawal [8](#0-7) .
5. Integrator credits the user for withdrawal #1 (index 1, intended for `0xBBB...`) based on this false "completed" signal, while the real transfer to `0xBBB...` may still be pending, stuck, or fail — resulting in a double credit or a credit issued for funds not yet delivered to the correct address.

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
