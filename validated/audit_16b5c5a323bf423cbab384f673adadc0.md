### Title
Ambiguous withdrawal-status matching in POA bridge causes txHash/status misattribution across same-asset batch withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` resolves the completion status/`txHash` of a withdrawal by matching the bridge indexer's response purely on `assetId`, ignoring `index`, `destinationAddress`, and `amount`. When a caller submits a batch intent containing two or more withdrawals of the *same* token (a legitimately supported feature of `processWithdrawal`/`waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`), the SDK cannot distinguish which on-chain result belongs to which withdrawal entry, and will report the same (first-matching) `txHash`/status for all of them.

### Finding Description
`describeWithdrawal` calls `findMatchingWithdrawal`, which matches solely on `assetId`:

<cite repo="Alyssadaypin/sdk-monorepo--019" path="packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts" start="313\" end="343" /> [1](#0-0) 

The same limitation is duplicated in `internal-utils`: [2](#0-1) 

The comment explicitly documents the gap ("multiple withdrawals of the same token in a single transaction are not supported"), but nothing in the SDK's batch-withdrawal path enforces or validates this constraint. `createWithdrawalIdentifiers`/`createWithdrawalCompletionPromises` builds one polling promise per `withdrawalParams` entry, each carrying its own `destinationAddress`/`amount`, and each independently calls `describeWithdrawal` on the shared indexer response: [3](#0-2) 

Because `findMatchingWithdrawal` returns the *first* array element whose `near_token_id` matches the requested `assetId`, two (or more) withdrawal entries for the same token but different destination addresses/amounts within one NEAR intent transaction both resolve against the same indexer record. The equality broken is: *the status/txHash reported for withdrawal index N is not the on-chain outcome that actually corresponds to withdrawal index N's destination address/amount.*

### Impact Explanation
Batch withdrawals with duplicate assetIds are a realistic, unprivileged, caller-supplied scenario (e.g., an integrator batching several end-users' withdrawals of the same stablecoin into a single NEAR intent to save fees, each with a distinct `destinationAddress`). If the indexer returns the withdrawals unsorted (as the code comment notes) or completes them out of submission order, one destination address's withdrawal can be reported as `completed` with another destination's `txHash`, or a still-`pending`/`failed` withdrawal can be reported as `completed`. An integrator relying on this status to release custody credits, mark an off-chain ledger entry as settled, or stop retry logic could credit or reconcile the wrong user/amount, or double-credit if it later reconciles by chain data and finds a mismatch. This matches the "status or hash misreport making an integrator credit or refund twice" High-impact category.

### Likelihood Explanation
No validation anywhere in `processWithdrawal`, `signAndSendWithdrawalIntent`, or `createWithdrawalCompletionPromises` rejects batches containing duplicate `assetId` entries, so the ambiguous condition is trivially reachable by any caller constructing a batch withdrawal (a documented, supported use case per the SDK's README and RFC docs on batch withdrawals). The bug is deterministic once the underlying indexer returns an unordered array containing more than one matching-asset withdrawal.

### Recommendation
Disambiguate `findMatchingWithdrawal` using more than `assetId`: incorporate `destinationAddress` (and `amount`/relative ordering, per the existing code comment's own suggested fix) to bind each `WithdrawalIdentifier` to its correct on-chain result, or explicitly validate/reject batches with duplicate `assetId` entries at `processWithdrawal`/`signAndSendWithdrawalIntent` time until the indexer/API can disambiguate reliably.

### Proof of Concept
1. Caller (integrator) submits a batch withdrawal intent with two entries of the same token, differing only by `destinationAddress`/`amount`:
```ts
await sdk.processWithdrawal({
  withdrawalParams: [
    { assetId: "nep141:usdt.tether-token.near", amount: 100n, destinationAddress: "0xAAA...", feeInclusive: false },
    { assetId: "nep141:usdt.tether-token.near", amount: 200n, destinationAddress: "0xBBB...", feeInclusive: false },
  ],
});
```
2. Both entries share the same NEAR `intentTx.hash`, so `getWithdrawalStatusWithRetry` fetches one `withdrawals` array containing (unsorted) records for both destination transfers.
3. `describeWithdrawal` for index 0 and index 1 both call `findMatchingWithdrawal(withdrawals, "nep141:usdt.tether-token.near")`, which returns the *same* first-matching record for both calls regardless of which `destinationAddress`/`amount` it actually corresponds to.
4. `createWithdrawalCompletionPromises` resolves both promises with the same `txHash`, even though the on-chain transfers to `0xAAA...` and `0xBBB...` are distinct — the integrator cannot correctly attribute completion per destination.

### Citations

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
