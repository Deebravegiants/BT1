## Title
PoA Bridge withdrawal status matches only by `assetId`, misreporting destination tx hash for batched same-token withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` and `internal-utils`'s `waitForWithdrawalCompletion()` both resolve which withdrawal record from the PoA bridge API corresponds to a given `WithdrawalIdentifier`/`txHash` by matching **only on `assetId`** (via `near_token_id`), ignoring the withdrawal's `index` and `destinationAddress`. When a batch intent contains two or more withdrawals of the *same* token (e.g., two `nep141:eth.omft.near` withdrawals to two different destination addresses in one NEAR tx), both lookups resolve to the *same* array entry (`Array.prototype.find` returns the first match), so the SDK can report the wrong destination `transfer_tx_hash` for a given withdrawal index/address.

### Finding Description
`findMatchingWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` is: [1](#0-0) 

and it is called from `describeWithdrawal`: [2](#0-1) 

The identical pattern exists in `internal-utils`: [3](#0-2) [4](#0-3) 

Both functions receive the full (unsorted) `withdrawals` list from the PoA API for a given NEAR `txHash` and pick the *first* entry whose `near_token_id` matches the requested `assetId`. The `WithdrawalIdentifier.index` (assigned per-bridge-route in `createWithdrawalIdentifiers`, see `packages/intents-sdk/src/core/withdrawal-watcher.ts` lines 80-107) and `destinationAddress` are never used to disambiguate. The code comment explicitly acknowledges this: "multiple withdrawals of the same token in a single transaction are not supported."

This breaks the equality the caller relies on: *the txHash returned for withdrawal index N, destined to address A, is the txHash of the on-chain transfer to address A* — not the txHash of some other withdrawal in the same batch that happens to share the token.

### Impact Explanation
A legitimate (non-malicious) batch withdrawal — e.g., withdrawing the same token to two different destination addresses in a single intent, which the SDK's own batch-withdrawal feature and `createWithdrawalIntents`/`createWithdrawalCompletionPromises` explicitly support — causes `describeWithdrawal()` to report the same first-matching record's `transfer_tx_hash`/status for both withdrawal indices. An integrator polling per-index via `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` can be told that withdrawal #1 (to address B) is "completed" with the destination tx hash that actually corresponds to withdrawal #0 (to address A). This is exactly the "status or hash misreport making an integrator credit or refund twice" category: the integrator could mark both withdrawals as settled using one real on-chain transaction, double-crediting internal ledgers, or associate a customer's payout with the wrong on-chain transaction.

### Likelihood Explanation
This does not require an attacker to compromise the relayer, bridge, or RPC — it is triggered purely by ordinary batch-withdrawal usage of the SDK (two withdrawals of the same token in one intent), which is a documented supported feature (`README.md` "Batch Withdrawals" section). Any integrator building on `IntentsSDK.processWithdrawal`/`waitForWithdrawalCompletion` with PoA-bridged assets can hit this without any malicious input.

### Recommendation
Disambiguate matching by including `destinationAddress` (and/or `amount`) in addition to `assetId` when multiple entries share the same token, or fail/throw (rather than silently pick the first match) when more than one candidate matches for a given assetId, forcing the caller to handle the ambiguity explicitly instead of getting a plausible-but-wrong hash.

### Proof of Concept
1. Build a batch withdrawal intent with two `WithdrawalParams` entries: both `assetId: "nep141:eth.omft.near"`, one with `destinationAddress: "0xAAA..."` and another with `destinationAddress: "0xBBB..."`.
2. Submit via `sdk.processWithdrawal`/`signAndSendWithdrawalIntent`; the PoA bridge processes both, resulting in two `withdrawals` entries under the same NEAR `tx_hash`, both with `near_token_id: "eth.omft.near"` but different `transfer_tx_hash`/`address`.
3. Call `bridge.describeWithdrawal({ index: 0, withdrawalParams: { assetId: "nep141:eth.omft.near", destinationAddress: "0xBBB..." }, tx })` (as `withdrawal-watcher.ts` / `createWithdrawalCompletionPromises` do per-index).
4. `findMatchingWithdrawal` returns `withdrawals.find(w => nep141:${w.data.near_token_id} === assetId)` — the *first* array entry, which may be the one destined to `0xAAA...`, not `0xBBB...`. The returned `transfer_tx_hash` is reported as "completed" for the withdrawal to `0xBBB...`, even though it is actually the hash of the transfer to `0xAAA...`. This is directly demonstrated by the existing regression test `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts:1054` titled "matches withdrawal by assetId, not by index", which currently only checks the assetId-only path but shows that `index` is not used at all to select the correct entry.

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L35-84)
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

			if (withdrawal.status === "COMPLETED") {
				if (withdrawal.data.transfer_tx_hash == null) {
					throw new PoaWithdrawalInvariantError(
						"POA Bridge didn't return transfer_tx_hash for COMPLETED withdrawal",
						result,
						txHash,
						withdrawalCriteria,
					);
				}

				return {
					destinationTxHash: withdrawal.data.transfer_tx_hash,
					chain: withdrawal.data.chain,
				};
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
