### Title
Same-token batch withdrawals collapse to a single (wrong) status/tx-hash in `PoaBridge.describeWithdrawal` - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` identifies which withdrawal entry returned by the POA bridge API corresponds to a given `WithdrawalIdentifier` by matching **only on `assetId`**, ignoring the `index` that `createWithdrawalIdentifiers` assigned to disambiguate multiple withdrawals of the same route/type in a batch. When a batch contains two or more withdrawals of the same token (same `assetId`) to different destinations/amounts, both `describeWithdrawal` calls resolve to the very first matching entry in the API response, so the status and `txHash` of one withdrawal get reported for the other as well — exactly the same "shared identifier bleeds across multiple requests" root cause as the `DineroWithdrawRequestManager` batch-ID overlap bug, but here it manifests as a status/hash misreport instead of a token overwithdrawal.

### Finding Description
`createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` assigns a per-bridge-route `index` to each `WithdrawalIdentifier` precisely to distinguish multiple withdrawals that share the same bridge: [1](#0-0) 

`PoaBridge.createWithdrawalIdentifier` stores that `index` on the identifier: [2](#0-1) 

But `describeWithdrawal` never uses `index` — it looks up the withdrawal entries for the shared NEAR tx hash and picks the first one whose `assetId` matches, with an explicit comment acknowledging that same-token duplicates in a batch are not distinguished: [3](#0-2) [4](#0-3) 

Because `getWithdrawalStatusWithRetry` fetches by `args.tx.hash` (the shared batch tx hash) and `findMatchingWithdrawal` uses `Array.prototype.find` keyed only on `assetId`, any two withdrawal legs of the same token in one intent will resolve to the identical response entry regardless of which leg (`index`) is being queried. `watchWithdrawal` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` then reports that resolved status/`txHash` back to the caller as the outcome for a specific `WithdrawalIdentifier`/index: [5](#0-4) 

This breaks the equality "status reported == on-chain outcome for this specific withdrawal": both legs are reported as completed with the *same* destination tx hash the instant the *first* one of them settles, even though the second leg's on-chain settlement may still be pending or resolve to a different destination address/amount.

### Impact Explanation
`waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises` (built on `watchWithdrawal`) are the SDK's primary API for integrators to know when to release/credit funds tied to a withdrawal. If an integrator batches two withdrawals of the same NEP-141 asset (e.g., splitting a payout into `USDC → Address A` and `USDC → Address B`, or a refund + payout of the same token in one intent), both indices will resolve to "completed" using whichever transfer settles first, using the *same* `txHash` as proof for both. This is a concrete status/hash misreport that can make an integrator credit/mark-as-delivered a withdrawal that has not actually completed on-chain yet, or record the wrong destination tx hash for a leg — matching the High-impact category "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
This triggers deterministically any time `withdrawalParams` in a single batch contains two or more entries with the same `assetId` — no attacker action or malicious relayer/bridge is required, this is a straightforward SDK-side identification bug reachable by any caller using the documented batch-withdrawal feature.

### Recommendation
Disambiguate withdrawal API results using more than `assetId`: incorporate `destinationAddress` and `amount` (as the code's own comment suggests — "sorting both API results and withdrawal params by amount") or, ideally, the withdrawal `index`/leg-specific memo if the POA API exposes one, so that `findMatchingWithdrawal` cannot return the same entry for two distinct `WithdrawalIdentifier`s in a batch.

### Proof of Concept
1. Build `withdrawalParams` with two entries for the same `assetId` (e.g., `nep141:usdc.near`), different `destinationAddress`/`amount`, submitted in a single intent so they share one NEAR tx hash.
2. `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` to the two `WithdrawalIdentifier`s (`packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`).
3. Call `sdk.createWithdrawalCompletionPromises`/`watchWithdrawal` for both. Internally each call invokes `PoaBridge.describeWithdrawal` with the shared `tx.hash`.
4. Once the POA bridge processes only one of the two legs, `getWithdrawalStatusWithRetry` returns a `withdrawals` array containing that single completed entry (plus possibly a still-pending entry for the other leg with the same `assetId`).
5. `findMatchingWithdrawal(withdrawals, assetId)` (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427`) returns the *first* match for **both** index-0 and index-1 queries — both promises resolve `{ status: "completed", txHash: <same hash> }` even though only one of the two destinations actually received funds.

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-53)
```typescript
export async function watchWithdrawal(args: {
	bridge: Bridge;
	wid: WithdrawalIdentifier;
	signal?: AbortSignal;
	logger?: ILogger;
}): Promise<TxInfo | TxNoInfo> {
	const stats = getWithdrawalStatsForChain({
		chain: args.wid.landingChain,
		bridgeRoute: args.bridge.route,
	});
	let consecutiveErrors = 0;

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

					if (status.status === "failed") {
						throw new WithdrawalFailedError(status.reason);
					}

					return POLL_PENDING;
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L295-311)
```typescript
	createWithdrawalIdentifier(args: {
		withdrawalParams: WithdrawalParams;
		index: number;
		tx: NearTxInfo;
	}): WithdrawalIdentifier {
		const assetInfo = this.parseAssetId(args.withdrawalParams.assetId);
		assert(assetInfo != null, "Asset is not supported");

		const landingChain = assetInfo.blockchain;

		return {
			landingChain,
			index: args.index,
			withdrawalParams: args.withdrawalParams,
			tx: args.tx,
		};
	}
```

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
