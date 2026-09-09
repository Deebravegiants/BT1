### Title
POA Bridge withdrawal status matched only by `assetId`, causing cross-withdrawal status/hash misattribution for batched same-asset withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain status/hash of a specific withdrawal by looking up the POA indexer's response using only the `assetId`, ignoring the withdrawal `index` that was assigned to disambiguate multiple withdrawals created in the same NEAR transaction. When a single NEAR transaction contains two or more withdrawal intents for the same asset (e.g., a batch withdrawal splitting the same token to two different destination addresses), the lookup returns the wrong indexer record, and the SDK reports one withdrawal's completion status/transaction hash for a different, distinct withdrawal.

### Finding Description
`createWithdrawalIdentifier` builds a `WithdrawalIdentifier` that stores a per-bridge `index` specifically to disambiguate multiple withdrawals batched into the same NEAR transaction: [1](#0-0) 

However, `describeWithdrawal` never consults that `index` — it only matches by `assetId` via `findMatchingWithdrawal`, and the code's own comment acknowledges the resulting limitation: [2](#0-1) [3](#0-2) 

`findMatchingWithdrawal` uses `Array.prototype.find`, which always returns the *first* matching entry for the given `assetId` in `response.withdrawals` — regardless of which of the (possibly several) same-asset withdrawals in that NEAR transaction the caller is actually asking about. `createWithdrawalIdentifiers` in the watcher confirms multiple withdrawals to the same bridge route within one NEAR tx are a supported, expected case (it explicitly increments a per-route `index`): [4](#0-3) 

`watchWithdrawal` then treats whatever `describeWithdrawal` returns as authoritative and finalizes the tx hash it reports: [5](#0-4) 

Equality broken: the withdrawal-status/tx-hash reported for withdrawal *N* is not guaranteed to be the on-chain outcome of withdrawal *N* — it can be the outcome of a different withdrawal *M* (same asset, same NEAR tx, different destination address and/or amount) that happens to appear first in the unsorted indexer response.

### Impact Explanation
If a NEAR transaction batches two withdrawal intents for the same token to two different destination addresses (e.g., address A receives 100 USDC, address B receives 200 USDC), polling the status for the withdrawal to B can return the `COMPLETED` status and `transfer_tx_hash` that actually belongs to the transfer to A (or vice versa), simply because `find()` picked the first matching record. An integrator/caller relying on the SDK's `describeWithdrawal`/`watchWithdrawal` result to confirm delivery and finalize (e.g., mark an off-chain order complete, release custody, or trigger a refund) would associate the wrong destination/transaction with a given withdrawal. This matches the "status or hash misreport" class of impact — it can cause an integrator to credit/consider-complete a withdrawal that has not actually reached its expected destination, or duplicate the crediting of the same completion evidence against two different logical withdrawals.

### Likelihood Explanation
This is triggered purely by normal usage patterns (no malicious actor needed): any batch of withdrawals containing two or more entries for the same underlying POA asset within a single NEAR transaction. The code comment in `findMatchingWithdrawal` itself documents that this exact scenario ("multiple withdrawals of the same token in a single transaction") is known to be unhandled, indicating this is a real, reachable gap rather than a theoretical edge case.

### Recommendation
Disambiguate matching using more than `assetId`: correlate indexer records to the specific withdrawal by additionally matching on `receiver_address`/`destinationAddress` and `withdraw_amount`, or, if the POA indexer response can be deterministically ordered, sort both the local withdrawal params list and the indexer's response consistently (as suggested in the existing code comment) and match by `index` after sorting. At minimum, detect the ambiguous case (more than one candidate record sharing the same `assetId` in a given NEAR tx) and fail closed (treat as `pending`/error) rather than silently returning a possibly-wrong match.

### Proof of Concept
1. Submit a NEAR transaction containing two POA withdrawal intents for the same `assetId` (e.g., `nep141:usdc.omft.near`), one to `destinationAddress = A`, one to `destinationAddress = B`.
2. `createWithdrawalIdentifiers` assigns `index = 0` to the withdrawal to A and `index = 1` to the withdrawal to B (per `packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`).
3. Call `bridge.describeWithdrawal` for the `index = 1` (destination B) identifier.
4. Inside `describeWithdrawal`, `findMatchingWithdrawal(response.withdrawals, "nep141:usdc.omft.near")` returns the first indexer record with that `near_token_id` — which may be the record for destination A's completed transfer, not B's.
5. The caller (`watchWithdrawal`) receives `{ status: "completed", txHash: <A's transfer hash> }` for what it believes is B's withdrawal, misreporting the outcome of a withdrawal the destination it never actually validated against.

### Citations

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L32-53)
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
