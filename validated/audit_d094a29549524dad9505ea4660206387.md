### Title
`describeWithdrawal` in `PoaBridge` matches withdrawal status by `assetId` only, misreporting `txHash`/status for batch withdrawals containing multiple transfers of the same asset - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` resolves the status/destination-tx-hash of a specific withdrawal within a NEAR intent by looking up the POA Bridge's `getWithdrawalStatus` response and selecting the first entry whose `near_token_id` matches the requested `assetId` — without checking `destinationAddress` or `amount`. In a batch withdrawal (`WithdrawalParams[]`) containing two or more withdrawals of the same asset (e.g., two USDC-to-different-addresses withdrawals settled in one NEAR intent transaction), every `describeWithdrawal` call for that assetId returns the same (first-matching) withdrawal record, regardless of which index/destination it was actually invoked for.

### Finding Description
`findMatchingWithdrawal` is defined as: [1](#0-0) 

and is used unconditionally in `describeWithdrawal`: [2](#0-1) 

The code comment itself documents the limitation: "Currently only matches by assetId... This means multiple withdrawals of the same token in a single transaction are not supported," the same limitation and matching function also exists in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`: [3](#0-2) 

The SDK explicitly supports batch withdrawals with independent per-index tracking via `createWithdrawalCompletionPromises`, where the caller supplies an array of `WithdrawalParams` (each with its own `destinationAddress`/`amount`) and expects each array index to resolve to the correct on-chain outcome for that specific withdrawal: [4](#0-3) [5](#0-4) 

Nothing in `WithdrawalParams` or the batch-withdrawal flow prevents two entries in the same batch from sharing the same `assetId` but differing `destinationAddress` (e.g., splitting a withdrawal to two different recipient wallets, or a partial refund plus a payout of the same token). When that happens, `describeWithdrawal` for withdrawal index 0 and index 1 both call into `findMatchingWithdrawal(response.withdrawals, assetId)`, which returns the *same* array entry (`.find()` returns the first match) for both calls — so both `describeWithdrawal` invocations report the same `status`/`txHash`, even though only one of the two withdrawals may have actually completed, and even though the two withdrawals go to two different destination addresses.

### Impact Explanation
This breaks the equality "status reported == the on-chain outcome for that particular withdrawal." An integrator (or the SDK's own `createWithdrawalCompletionPromises`) tracking a batch of two same-asset withdrawals to different addresses will:
- Have both promises resolve to `{ status: "completed", txHash: X }` using the transfer hash of only one of the two transfers, even though the second withdrawal may still be pending, may fail, or may land at a different destination address with a different hash.
- This can cause an integrator to credit/mark both withdrawals as complete based on a single actual completion (double credit), or to report a wrong `txHash` for the withdrawal that has not actually settled yet.

This matches the specified High-severity impact class: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
The condition (batch of ≥2 withdrawals of the identical `assetId` via POA Bridge, e.g. two BTC/USDC/etc payouts to different addresses in one intent) is a normal, unprivileged user flow explicitly supported by `createWithdrawalCompletionPromises`/`processWithdrawal`/`signAndSendWithdrawalIntent` batch APIs — no malicious or privileged actor is required. It only requires that both withdrawal legs of the batch use the POA Bridge route with the same underlying token. The bug is acknowledged in the code's own comments as a known limitation rather than mitigated, and there is no validation anywhere in the SDK rejecting or warning about duplicate `assetId` entries in a batch.

### Recommendation
Extend `findMatchingWithdrawal` (in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate among multiple withdrawals of the same asset — at minimum by also matching on `destinationAddress` (and `amount` where possible), and by not allowing a single withdrawal entry from the API response to be matched more than once across concurrently-tracked indices (e.g., track and exclude entries already claimed by another index in the same batch). Until POA Bridge's API supports precise per-transfer identification, the SDK should either reject/validate batches with duplicate `assetId` entries at build time, or clearly document/guard against relying on `describeWithdrawal`/`createWithdrawalCompletionPromises` for such batches so integrators don't silently double-credit or misreport withdrawal status.

### Proof of Concept
1. Build a batch withdrawal intent with two `WithdrawalParams` entries, both `assetId: "nep141:usdc.omft.near"`, but `destinationAddress: "0xAAA..."` for index 0 and `destinationAddress: "0xBBB..."` for index 1.
2. Submit via `sdk.signAndSendWithdrawalIntent` / `sdk.processWithdrawal`, then call `sdk.createWithdrawalCompletionPromises({ withdrawalParams, intentTx })`.
3. Assume only the withdrawal to `0xAAA...` has completed on the destination chain (POA relayer's `getWithdrawalStatus` response contains one `COMPLETED` entry with `near_token_id: "usdc.omft.near"`, `address: "0xAAA..."`, `transfer_tx_hash: "0xreal-hash"`), while the withdrawal to `0xBBB...` is still pending.
4. Both `describeWithdrawal` calls (index 0 and index 1) invoke `findMatchingWithdrawal(response.withdrawals, "nep141:usdc.omft.near")`, which returns the single `COMPLETED` entry for both, per: [6](#0-5) 
5. Consequently, `promises[1]` (destined for `0xBBB...`) incorrectly resolves as `{ hash: "0xreal-hash" }` even though the actual withdrawal to `0xBBB...` has not settled — an integrator relying on this would mark the `0xBBB...` payout as completed and could, e.g., release/credit funds twice or record the wrong transaction hash for that leg.

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L418-427)
```typescript
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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L135-153)
```typescript
/**
 * Finds a withdrawal matching the given criteria.
 *
 * NOTE: Currently only matches by assetId (near_token_id). This means multiple
 * withdrawals of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
 */
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

**File:** packages/intents-sdk/src/shared-types.ts (L246-259)
```typescript
export interface WithdrawalParams {
	assetId: string;
	amount: bigint;
	destinationAddress: string;
	/**
	 * Optional memo attached to the withdrawal.
	 * - XRP Ledger: included in the transaction memo field
	 * - Internal transfers (intents): passed as memo in the transfer intent
	 * - Stellar, TON: NOT SUPPORTED (will throw error)
	 */
	destinationMemo?: string | undefined;
	feeInclusive: boolean;
	routeConfig?: RouteConfig | undefined;
}
```
