### Title
PoA Bridge withdrawal status is matched only by `assetId`, causing tx-hash misattribution in batched same-asset withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`IntentsSDK` explicitly supports submitting multiple withdrawals in a single batch/intent, including duplicate `assetId`s to different destination addresses, and exposes per-index tracking via `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` [1](#0-0) . For PoA-bridge withdrawals, `PoaBridge.describeWithdrawal` resolves the status/tx hash for a given index by matching on `assetId` alone, ignoring the caller-supplied `index` [2](#0-1)  via `findMatchingWithdrawal` [3](#0-2) . When a single NEAR transaction contains two or more withdrawals of the same underlying token to different recipients, every index resolves to the first matching record returned by the PoA indexer, so the SDK reports the same status/`txHash` for logically distinct withdrawals.

### Finding Description
`findMatchingWithdrawal` is documented as matching purely by `assetId` and explicitly notes it does not support "multiple withdrawals of the same token in a single transaction" [4](#0-3) . However, the SDK's own public, documented batch API (`createWithdrawalCompletionPromises`, `waitForWithdrawalCompletion`) is designed precisely to let a caller submit an array of `WithdrawalParams` (including multiple entries with the same `assetId` but different `destinationAddress`) in one NEAR transaction and independently track completion per index [5](#0-4) . The equality that should hold — "status/txHash reported for withdrawal at index N is the on-chain outcome of withdrawal N" — is broken: `describeWithdrawal` for index 0 and index 1 (same `assetId`, different recipients) both call `getWithdrawalStatusWithRetry` and then `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which returns the same array element via `.find()` for both indices [6](#0-5) .

### Impact Explanation
If a caller batches two same-asset withdrawals to different destinations (e.g., a real user withdrawal plus a refund/fee-sweep of the same token, or two independent user withdrawals of the same token in one settled intent), and one of them completes while the other is still pending/fails, the SDK will report the completed one's `status: "completed"` and `txHash` for **both** indices. An integrator relying on per-index promises to mark a specific withdrawal as delivered (a pattern the SDK's own README/RFC explicitly recommends, e.g. `promises[0].then(tx => saveUsdc(tx))`) would credit/mark-delivered a withdrawal that never actually reached its destination address, using a transaction hash that belongs to a different recipient. This is a status/hash misreport that can cause an integrator to falsely credit a withdrawal as completed, matching the "status or hash misreport making an integrator credit or refund twice" High-impact class.

### Likelihood Explanation
This requires no privileged or malicious actor — any regular user or integrator constructing a batch withdrawal that happens to include the same PoA-bridged asset more than once (a legitimate, supported use case per the SDK's batch design) will trigger the mismatch as soon as the withdrawals complete at different times, which is the common case for cross-chain transfers.

### Recommendation
Match withdrawals using a criterion that uniquely identifies each entry (e.g., pair `assetId` with `destinationAddress`/amount ordering, or have the PoA indexer return a stable per-intent index/identifier) instead of `assetId` alone, so that `describeWithdrawal` returns the correct status/`txHash` for each index in a batch, even when multiple withdrawals share the same asset.

### Proof of Concept
1. Submit a single NEAR intent containing two `ft_withdraw` intents for the same PoA-bridged token (e.g., `nep141:eth.omft.near`) to two different destination EVM addresses, using `sdk.createWithdrawalIntents`/batch submission.
2. Call `sdk.createWithdrawalCompletionPromises({ withdrawalParams: [w0, w1], intentTx })` where `w0.destinationAddress !== w1.destinationAddress` but `w0.assetId === w1.assetId`.
3. Wait until the first withdrawal (to address A) completes on-chain while the second (to address B) is still pending or fails.
4. Observe that `PoaBridge.describeWithdrawal` for index 1 (address B) also returns `{ status: "completed", txHash: <A's tx hash> }` because `findMatchingWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427` matches only by `assetId` and returns the first matching entry from the indexer response for every index sharing that asset.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L557-608)
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
