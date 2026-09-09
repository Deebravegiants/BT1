### Title
POA bridge `describeWithdrawal` matches withdrawals by `assetId` only, causing status/hash misreport (double credit) for batch withdrawals of the same token - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
No enforced validation prevents a batch withdrawal (`WithdrawalParams[]`) from containing two or more entries with the same `assetId` routed through the POA bridge. When this happens, `findMatchingWithdrawal` resolves to the **same** on-chain withdrawal record for every index sharing that `assetId`, so `sdk.waitForWithdrawalCompletion` / `createWithdrawalCompletionPromises` reports identical `status`/`txHash` for withdrawals that are actually distinct on-chain outcomes.

### Finding Description
`PoaBridge.describeWithdrawal` looks up the matching remote withdrawal purely by `assetId`, explicitly ignoring index: [1](#0-0) 

The matching helper uses `Array.prototype.find`, which always returns the **first** matching element in the response list, regardless of which withdrawal (index) is being queried: [2](#0-1) 

This is the same bug class as the LiFi `batchRemoveDex` finding: an operation intended to act per-item instead collapses onto the first matching item due to loop/lookup logic that stops at (or only considers) the first match. Here, when a batch withdrawal (`WithdrawalParams[]`) contains multiple entries with the same `assetId` (e.g., two withdrawals of the same token to two different destination addresses in one intent), `createWithdrawalIdentifiers` creates a separate `WithdrawalIdentifier` per index, but each index's watcher calls `describeWithdrawal` with the *same* `assetId`: [3](#0-2) [4](#0-3) 

Both `watchWithdrawal` calls resolve `findMatchingWithdrawal` against the identical response array and therefore both receive the **same** matched record — same `status`, same `transfer_tx_hash` — even though only one of the two on-chain withdrawals may actually be `COMPLETED` while the other is still `PENDING` or has a different (or no) `transfer_tx_hash`. Nothing in `IntentsSDK` (`sdk.ts`) or `PoaBridge.validateWithdrawal` rejects batches with duplicate `assetId`, so this state is reachable via the public, unprivileged `signAndSendWithdrawalIntent` / `processWithdrawal` API surface with normal batch input.

The bug class maps directly onto the required equality: "a status reported that is not the on-chain outcome." The comment in the code even documents the limitation but treats it as informational rather than guarding against it: [5](#0-4) 

### Impact Explanation
An integrator (or the SDK's own `waitForWithdrawalCompletion`/`processWithdrawal` orchestration) resolves two promises for two distinct withdrawal legs, but both resolve with the same `txHash`/`completed` status once only one of the underlying transfers finishes. An integrator that credits/refunds based on the resolved promise per index would credit the second withdrawal as completed using the first withdrawal's transaction hash, effectively reporting completion for funds that have not actually landed at the second destination address — this matches the "High: a status or hash misreport making an integrator credit or refund twice" category. It can also cause silent misdelivery reporting (destination B mistakenly considered settled with destination A's proof), with no on-chain safeguard.

### Likelihood Explanation
Likelihood is limited by the precondition that a caller submits a batch withdrawal where two or more `WithdrawalParams` entries share the same `assetId` routed to the POA bridge — this is a valid, unprivileged usage pattern of `sdk.signAndSendWithdrawalIntent`/`processWithdrawal` (no special permissions required, and nothing in the SDK rejects it), but it is a less common flow than a simple single-asset batch. The bug is deterministic once triggered, not probabilistic.

### Recommendation
- Reject batches containing duplicate `assetId` values routed to the POA bridge at input validation time (e.g., in `PoaBridge.validateWithdrawal` or `IntentsSDK.signAndSendWithdrawalIntent`), until the POA bridge API supports disambiguating same-asset withdrawals.
- Alternatively, once the POA API supports it, match by a more specific identifier (e.g., destination address + amount + assetId, or an explicit correlation id) instead of `assetId` alone, and consume matched entries so repeated lookups don't return the same record for two different logical withdrawals.

### Proof of Concept
1. Prepare `withdrawalParams = [ {assetId: "nep141:usdc.omft.near", destinationAddress: A, amount: X}, {assetId: "nep141:usdc.omft.near", destinationAddress: B, amount: Y} ]` and submit via `sdk.signAndSendWithdrawalIntent({ withdrawalParams, feeEstimation, ... })`.
2. Call `sdk.createWithdrawalCompletionPromises({ withdrawalParams, intentTx })`, which produces two promises via `watchWithdrawal` for index 0 and index 1: [6](#0-5) 
3. Simulate the POA bridge API returning one `COMPLETED` withdrawal (for destination A) and one still `PENDING`/absent (for destination B) with the same `near_token_id`.
4. Observe that `describeWithdrawal` for wid index 1 (destination B) also resolves the `COMPLETED` record with A's `transfer_tx_hash`, because `findMatchingWithdrawal` (`Array.prototype.find`) returns the same first match for both calls: [7](#0-6) 
5. Both promises resolve as `completed` with the identical `txHash`, even though the destination B transfer has not occurred on-chain.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-336)
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

**File:** packages/intents-sdk/src/sdk.ts (L557-609)
```typescript
	public createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>> {
		const { withdrawalParams, intentTx, signal, logger } = params;

		const widsPromise = createWithdrawalIdentifiers({
			bridges: this.bridges,
			withdrawalParams,
			intentTx,
		});

		// Track the last promise per HOT bridge landing chain for sequential waiting.
		// HOT bridge processes withdrawals sequentially per chain with ~30s gaps,
		// so polling in parallel would cause later withdrawals to timeout.
		const hotChainLastPromise = new Map<Chain, Promise<TxInfo | TxNoInfo>>();

		return withdrawalParams.map(async (_, index) => {
			const wids = await widsPromise;
			const entry = wids[index];
			assert(entry != null, `Missing wid for index ${index}`);

			// Only apply sequential waiting for HOT bridge
			if (entry.bridge.route === RouteEnum.HotBridge) {
				const landingChain = entry.wid.landingChain;
				const previousPromise = hotChainLastPromise.get(landingChain);

				const sequentialPromise = (async () => {
					if (previousPromise) {
						// Wait for previous withdrawal to same chain to complete.
						// Use allSettled to continue even if previous fails.
						await Promise.allSettled([previousPromise]);
					}
					return watchWithdrawal({
						bridge: entry.bridge,
						wid: entry.wid,
						signal,
						logger,
					});
				})();

				hotChainLastPromise.set(landingChain, sequentialPromise);
				return sequentialPromise;
			}

			// Non-HOT bridges: parallel polling (existing behavior)
			return watchWithdrawal({
				bridge: entry.bridge,
				wid: entry.wid,
				signal,
				logger,
			});
		});
	}
```
