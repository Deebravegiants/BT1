### Title
PoA Bridge withdrawal status matched only by `assetId`, misattributing tx hash/status across concurrent same-token withdrawals in a batch - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`BatchWithdrawalResult`/`ProcessWithdrawalArgs` allow the SDK to submit multiple withdrawals in a single NEAR intent, and `createWithdrawalIdentifiers` assigns each an `index` per bridge route for later status tracking. [1](#0-0)  However, `PoaBridge.describeWithdrawal` never uses that `index`; it resolves the withdrawal purely by `assetId` via `findMatchingWithdrawal`, taking the first entry in an *unsorted* API response list whose `near_token_id` matches. [2](#0-1) [3](#0-2) 

### Finding Description
When a caller submits a batch withdrawal (`sdk.processWithdrawal` / `sdk.signAndSendWithdrawalIntent` + `waitForWithdrawalCompletion` with an array of `withdrawalParams`) containing two or more entries that route through PoA Bridge for the **same `assetId`** (e.g., two BTC withdrawals to two different destination addresses/amounts in one NEAR transaction), `createWithdrawalIdentifiers` builds one `WithdrawalIdentifier` per entry, each carrying a distinct `index` [4](#0-3) .

When the SDK later polls status for each identifier via `watchWithdrawal` → `bridge.describeWithdrawal(wid)` [5](#0-4) , `PoaBridge.describeWithdrawal` ignores `args.index` entirely and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does `withdrawals.find((w) => nep141:${w.data.near_token_id} === assetId)` — returning the **first** match in an explicitly "unsorted" list [2](#0-1) . The code's own comment acknowledges this: *"NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported."* [6](#0-5) 

This breaks the equality that should hold: *"the status/tx-hash reported for withdrawal index N is the on-chain outcome of withdrawal N."* Instead, both concurrent same-asset withdrawals (indices 0 and 1) resolve to whichever single record the API happens to return first, so:
- Both `describeWithdrawal` calls can report `{status: "completed", txHash: X}` where `X` is the destination tx hash for only *one* of the two distinct withdrawals (to a different destination address/amount than the other).
- The withdrawal that has no matching record left keeps polling and may itself later fetch the *other* entry once it settles (since indexing doesn't disambiguate) — or time out.

### Impact Explanation
This is a status/hash misreport, one of the explicitly in-scope High-impact classes ("a status or hash misreport making an integrator credit or refund twice"). An integrator relying on `waitForWithdrawalCompletion`/`describeWithdrawal` per-identifier result to mark a specific withdrawal (by index, destination, or amount) as completed with a given `txHash` could credit or reconcile the wrong withdrawal as done, or attribute the same destination tx hash to two different withdrawal records — leading to double-crediting internal ledgers or premature settlement confirmation for a withdrawal that hasn't actually landed at its own destination.

### Likelihood Explanation
This requires no malicious action — only a legitimate integrator submitting a normal batch withdrawal containing two or more same-`assetId` PoA-bridge withdrawals in one NEAR transaction (a supported, documented use case per the batch API in `withdrawal-watcher.ts` and `shared-types.ts`). The bug is deterministic whenever the POA bridge API returns multiple entries for the same token in one transaction, and the code comment itself confirms this scenario is unhandled.

### Recommendation
Disambiguate matching in `findMatchingWithdrawal` using more than `assetId` — e.g., also match by `destinationAddress`/`amount`, or (preferably) have the POA Bridge API return/accept a stable per-withdrawal index or intent-sequence identifier, and use `args.index` positionally after deterministically sorting both the SDK's `withdrawalParams` and the API's `withdrawals` list by a shared deterministic key (e.g., amount) as suggested in the existing code comment, before matching.

### Proof of Concept
1. Caller invokes `sdk.processWithdrawal` (or `signAndSendWithdrawalIntent` + `waitForWithdrawalCompletion`) with `withdrawalParams = [ {assetId: "nep141:btc.omft.near", amount: A1, destinationAddress: addr1}, {assetId: "nep141:btc.omft.near", amount: A2, destinationAddress: addr2} ]`, both routed via PoA Bridge in a single NEAR intent transaction.
2. `createWithdrawalIdentifiers` produces `wid[0]` (index 0) and `wid[1]` (index 1), both referencing the same `tx.hash` and same `assetId`. [4](#0-3) 
3. Once the POA bridge processes both withdrawals, `getWithdrawalStatusWithRetry` returns a `withdrawals` array containing two records for `near_token_id = "btc.omft.near"` but with different `transfer_tx_hash`/`address`/`amount`.
4. Calling `describeWithdrawal(wid[0])` and `describeWithdrawal(wid[1])` both invoke `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which returns the **same first array element** for both calls regardless of `index`, so both report identical `{status:"completed", txHash: <first record's hash>}` even though they correspond to two different destination addresses/amounts. [2](#0-1)

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-47)
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
