Based on the investigation, I found a valid analog in the batch withdrawal status-matching logic of the POA bridge integration.

### Title
Withdrawal status matched only by assetId causes destination/tx-hash misreport for batch withdrawals of the same token - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` resolves the completion status of a specific withdrawal by calling `findMatchingWithdrawal()`, which selects a withdrawal record from the POA bridge API purely by `assetId` equality, without verifying that the record actually corresponds to the caller-supplied `destinationAddress`, `amount`, or batch `index`. This breaks the same kind of "identity check" equality as the langflow IDOR (serve/attribute a resource to a caller without validating that the caller is entitled to *that specific* record).

### Finding Description
`describeWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:313-343` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`. The matcher, defined at `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427`, is:

```ts
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```

It uses `Array.find`, which returns the **first** withdrawal record whose token matches, ignoring `destinationAddress`, `amount`, and the withdrawal's `index` within the batch. The code comment above the function explicitly acknowledges this: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." The same unvalidated `assetId`-only matching is used by `waitForWithdrawalCompletion` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts:57-60`.

When `sdk.processWithdrawal`/`sdk.createWithdrawalCompletionPromises` (`packages/intents-sdk/src/sdk.ts`) is used for a batch that contains two or more withdrawals of the same NEP-141 token to different `destinationAddress`es in the same NEAR transaction, each withdrawal's `describeWithdrawal` call queries the POA API with the same `tx.hash` and gets back the full list of withdrawals for that transaction. Because matching only checks `assetId`, both calls converge on the **same** first-matching record, so both index-0 and index-1 withdrawal promises will resolve with the **same** `transfer_tx_hash`/destination — even though the two withdrawals were validated by the caller to go to two different destination addresses.

This breaks the "address paid was not the one validated" equality: the SDK reports a destination/tx completion for withdrawal B using the on-chain outcome that actually belongs to withdrawal A.

### Impact Explanation
An integrator relying on `describeWithdrawal`/`waitForWithdrawalCompletion` to determine which specific withdrawal (by destination) has settled can be told that withdrawal B (to address Y) completed with a transaction hash that actually corresponds to withdrawal A (to address X). This can cause the integrator to mark/credit the wrong withdrawal as complete, potentially crediting/refunding based on a mismatched destination, or reporting settlement for a withdrawal that has not actually reached its intended address — a status misreport that does not match the true on-chain outcome for that specific withdrawal.

### Likelihood Explanation
This requires a batch of withdrawals containing two or more entries with the identical `assetId` (same token) but different destinations/amounts in a single call to `sdk.processWithdrawal` / `signAndSendWithdrawalIntent` with `withdrawalParams` as an array — a reachable, unprivileged usage pattern documented in the SDK's own README (batch withdrawal example). No malicious actor or privileged access is required; it triggers under ordinary batch usage.

### Recommendation
Match withdrawal records deterministically using more than `assetId`: incorporate `destinationAddress` and `amount` (and, if the POA API exposes it, an explicit index/sub-transfer identifier) when selecting the corresponding withdrawal record, and fail/throw (rather than silently return a possibly-wrong match) when multiple withdrawals in the response share the same `assetId` and cannot be disambiguated by additional fields — analogous to the fix pattern already used to compare `near_token_id` instead of `defuse_asset_identifier`.

### Proof of Concept
1. Submit a batch withdrawal with `withdrawalParams = [{assetId: 'nep141:btc.omft.near', destinationAddress: 'addrA', amount: 100000n}, {assetId: 'nep141:btc.omft.near', destinationAddress: 'addrB', amount: 200000n}]` via `sdk.processWithdrawal`.
2. The POA bridge settles both withdrawals in the same NEAR tx; the `withdrawal_status` RPC returns both records in its `withdrawals` array (unsorted, per the existing code comment).
3. Call `describeWithdrawal` for index 1 (`addrB`). `findMatchingWithdrawal` returns the first `withdrawals[]` entry whose `near_token_id` matches `btc.omft.near` — which may be the record belonging to `addrA`.
4. The SDK reports `{status: "completed", txHash: <addrA's transfer_tx_hash>}` for the withdrawal that was supposed to go to `addrB`, misattributing settlement. [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L35-68)
```typescript
export async function waitForWithdrawalCompletion({
	txHash,
	withdrawalCriteria,
	signal,
	baseURL,
	retryOptions = RETRY_CONFIGS.TWO_MINS_GRADUAL,
	logger,
}: {
	txHash: string;
	withdrawalCriteria: WithdrawalCriteria;
	signal: AbortSignal;
	baseURL?: string;
	retryOptions?: RetryOptions;
	logger?: ILogger;
}): Promise<WaitForWithdrawalCompletionOkType> {
	return retry(
		async () => {
			const result = await getWithdrawalStatus(
				{ withdrawal_hash: txHash },
				{ baseURL, fetchOptions: { signal }, logger },
			);

			const withdrawal = findMatchingWithdrawal(
				result.withdrawals,
				withdrawalCriteria,
			);
			if (withdrawal == null) {
				throw new PoaWithdrawalInvariantError(
					"POA Bridge didn't return withdrawal matching criteria",
					result,
					txHash,
					withdrawalCriteria,
				);
			}
```
