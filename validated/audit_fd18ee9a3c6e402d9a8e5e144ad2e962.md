### Title
POA Bridge withdrawal status matched by `assetId` only, causing withdrawal hash/status misattribution for batched withdrawals of the same token - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts` allows a caller to submit multiple withdrawals routed through the same bridge inside a single NEAR transaction, assigning each a sequential `index` per bridge route. [1](#0-0)  For the PoA bridge, `describeWithdrawal` never uses that `index`; it instead resolves status by scanning the bridge's returned list for the first entry whose `near_token_id` matches the withdrawal's `assetId` via `findMatchingWithdrawal`. [2](#0-1) [3](#0-2) 

### Finding Description
`Bridge.describeWithdrawal` is documented as returning "the current status" for a specific `WithdrawalIdentifier`, which includes an `index` meant to disambiguate multiple withdrawals created from the same NEAR transaction. [4](#0-3) 

For the PoA bridge, `createWithdrawalIdentifier` builds this identifier but the `index` field is not later consulted by `describeWithdrawal`. [5](#0-4)  Instead, `findMatchingWithdrawal` picks the **first** withdrawal in the (unsorted) API response array whose `near_token_id` matches the requested `assetId`, with no correlation to the specific destination address, amount, or ordinal position of the withdrawal being queried:

```
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
``` [6](#0-5) 

If a caller creates two (or more) withdrawals of the same token (e.g., same `nep141:btc.omft.near`) to two different destination addresses within one NEAR transaction — something `createWithdrawalIdentifiers`/`sdk.ts` explicitly supports since it assigns distinct `index` values per bridge route for exactly this batching use case [7](#0-6)  — both `describeWithdrawal` calls (index 0 and index 1) query the same tx hash and both resolve to the **same matched record**, because the match key (`assetId`) is identical for both and the API response ordering is not guaranteed. This breaks the equality that the `txHash`/`status` reported for withdrawal-at-index-N is the on-chain outcome of withdrawal-at-index-N: the SDK can report withdrawal #1's completion `txHash` as the outcome for withdrawal #0 (or vice-versa), or report both indexes as "completed" with the same `txHash` even though they went to different destination addresses.

The code comment acknowledges this exact limitation: "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." [8](#0-7)  However, nothing in `supports()`, `validateWithdrawal()`, `createWithdrawalIntents()`, or the SDK-level batching path (`createWithdrawalIdentifiers`) actually rejects or prevents this scenario — the "not supported" constraint is undocumented at the API boundary and unenforced in code, so an integrator naturally hits it when batching same-asset withdrawals to multiple recipients in one call.

### Impact Explanation
`watchWithdrawal` consumes `describeWithdrawal`'s output directly to resolve the on-chain settlement hash used by downstream consumers (e.g., for crediting a user, closing an order, or confirming a transfer) [9](#0-8) . Because both withdrawal indexes can resolve to the identical matched record, an integrator polling withdrawal index 0 and index 1 of a same-token batch can be told both completed with the same `txHash`, or that the wrong index's withdrawal is "completed" while the truly-completed one is reported "pending"/mismatched. This is a status misreport that can cause an integrator to credit or refund the wrong withdrawal, or double-credit based on a single real on-chain settlement — matching the "status or hash misreport making an integrator credit or refund twice" High-impact criterion.

### Likelihood Explanation
Likelihood is moderate: it requires an integrator to batch two or more withdrawals of the same underlying PoA-bridged asset (to different destinations) within a single NEAR transaction — a usage pattern the SDK's own batching primitives (`createWithdrawalIdentifiers` assigning per-route indexes) are built to support, but which the PoA bridge adapter silently mishandles rather than rejecting.

### Recommendation
In `poa-bridge.ts`, either (1) reject/throw during `supports()`/`validateWithdrawal()` when a batch contains more than one withdrawal of the same `assetId` within the same tx (fail closed until the POA API supports disambiguation), or (2) implement the deterministic matching strategy referenced in the code comment — sort both the SDK's per-tx withdrawal params and the API's returned withdrawals list by amount (since relayer fees are identical for the same token) and match by position — so that `describeWithdrawal` for a given `index` always returns the outcome of that specific withdrawal, not an arbitrary same-asset entry.

### Proof of Concept
1. Caller submits one NEAR intent transaction containing two POA-bridge withdrawal legs, both for `nep141:btc.omft.near`, to `destinationAddress` A and `destinationAddress` B respectively.
2. `createWithdrawalIdentifiers` assigns `index: 0` to leg A and `index: 1` to leg B, sharing the same `tx.hash`. [7](#0-6) 
3. `watchWithdrawal` calls `bridge.describeWithdrawal({ ...wid_A })` and `bridge.describeWithdrawal({ ...wid_B })`, both hitting `poaBridge.httpClient.getWithdrawalStatus({ withdrawal_hash: tx.hash })`, returning an unsorted list containing both A's and B's records (both with `near_token_id: "btc.omft.near"`).
4. `findMatchingWithdrawal` for both calls filters purely on `nep141:${near_token_id} === assetId`, so `.find()` returns the same first array entry for both index 0 and index 1 queries — regardless of which destination address each entry actually corresponds to. [6](#0-5) 
5. Both watchers report `{ status: "completed", txHash: <A's real tx hash> }`, causing an integrator tracking leg B to believe B settled with A's transaction hash.

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-52)
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

**File:** packages/intents-sdk/src/shared-types.ts (L425-441)
```typescript
	/**
	 * One-shot status check for a withdrawal.
	 * Returns the current status without polling.
	 */
	describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus>;
}

export interface WithdrawalIdentifier {
	/** Actual chain where funds arrive; Near for virtual/internal routes */
	landingChain: Chain;
	/** Per-bridge withdrawal sequence number */
	index: number;
	withdrawalParams: WithdrawalParams;
	tx: NearTxInfo;
}
```
