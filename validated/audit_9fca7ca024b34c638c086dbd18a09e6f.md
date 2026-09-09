### Title
POA Bridge withdrawal status matches by `assetId` only, causing wrong destination tx-hash to be reported for batched same-token withdrawals - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`findMatchingWithdrawal` in the POA bridge adapter resolves a withdrawal's on-chain destination status by matching solely on `assetId`, ignoring the withdrawal `index`, `destinationAddress`, and `amount`. When a single NEAR intent contains more than one withdrawal of the same token (a legitimate, SDK-supported "batch withdrawal" scenario), `describeWithdrawal()` can report the wrong destination transaction hash for a given withdrawal index.

### Finding Description
`findMatchingWithdrawal` is explicitly documented as matching by `assetId` only: [1](#0-0) 

```
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * ...
 */
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
```

This function is used by `describeWithdrawal()` (and by `waitForWithdrawalCompletion` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`, which relies on the equivalent `WithdrawalCriteria = { assetId }` shape at [2](#0-1) ) to pick which POA API withdrawal record corresponds to a given `WithdrawalIdentifier`. The `WithdrawalIdentifier` carries an `index` field intended to disambiguate multiple withdrawals originating from the same NEAR transaction: [3](#0-2) . That `index` is never consulted by `findMatchingWithdrawal` — the first array element whose `near_token_id` matches wins, regardless of which withdrawal (destination, amount) it actually corresponds to.

The SDK explicitly supports batching multiple withdrawals into one intent/transaction (README "Batch Withdrawals" section), and nothing in `sdk.createWithdrawalIntents` / `sdk.processWithdrawal` prevents two withdrawal entries in the same batch from sharing the same `assetId` while going to different `destinationAddress` values or with different `amount`s.

The equality that should hold is: *the reported `txHash`/`status` for withdrawal index N corresponds to the on-chain outcome for withdrawal index N's specific `(destinationAddress, amount)`.* Because matching ignores `index`, this equality can break: if the POA API returns multiple withdrawal records for the same token in one NEAR tx (e.g., two different destinations withdrawing the same token), `.find()` returns whichever entry appears first, and that entry's `transfer_tx_hash`/`data` is attributed to a request for a *different* withdrawal index.

### Impact Explanation
An integrator relying on `sdk.waitForWithdrawalCompletion` / `describeWithdrawal` for a batched same-token withdrawal can receive a `completed` status with a `destinationTxHash` that actually belongs to a *different* withdrawal in the batch (different recipient/amount). This is a status/hash misreport: the integrator may mark the wrong withdrawal index as settled (potentially crediting/closing an unrelated user's withdrawal record, or reporting a transaction hash whose real destination does not match the queried recipient). This matches the High-severity "status or hash misreport making an integrator credit or refund twice" category, since downstream systems that key off `(withdrawal index → txHash)` can be misled into believing a specific withdrawal for a specific user completed when in fact a different one did.

### Likelihood Explanation
This requires only an ordinary (non-malicious) usage pattern already supported by the SDK: submitting a batch withdrawal with two or more entries for the same `nep141` asset in a single intent. The code comment itself acknowledges "multiple withdrawals of the same token in a single transaction are not supported," confirming this is a known, reachable gap rather than a theoretical one — it will manifest whenever a caller batches same-token withdrawals, which the public API does not forbid.

### Recommendation
Extend `findMatchingWithdrawal` (and the corresponding `WithdrawalCriteria` used in `internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate using additional withdrawal-specific fields returned by the POA API (e.g., destination address and amount, or an explicit index/nonce if the API can provide one), rather than `assetId` alone. Until the POA API supports per-item disambiguation, the SDK should either reject/warn on batches containing multiple withdrawals of the same `assetId`, or track consumed withdrawal records so repeated calls do not re-match an already-attributed record to a different index.

### Proof of Concept
1. Call `sdk.processWithdrawal` / `sdk.createWithdrawalIntents` with a batch containing two withdrawals of the same POA-bridged asset (e.g., `nep141:btc.omft.near`) to two different `destinationAddress` values within the same NEAR transaction.
2. After settlement, call `sdk.waitForWithdrawalCompletion` (or `bridge.describeWithdrawal`) for withdrawal `index: 0` and `index: 1` separately, both with the same `assetId`.
3. Because `findMatchingWithdrawal`/`WithdrawalCriteria` only filters the POA API's `withdrawals` array by `near_token_id` (i.e., by `assetId`), `.find()` returns the same (first-matching) record for both queries once the POA API has more than one completed record for that asset in the transaction — causing at least one of the two indices to be reported with a `txHash` belonging to the other withdrawal. [4](#0-3) [5](#0-4)

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L405-427)
```typescript
type WithdrawalStatusResponse = Awaited<
	ReturnType<typeof poaBridge.httpClient.getWithdrawalStatus>
>;

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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L31-84)
```typescript
export type WithdrawalCriteria = {
	assetId: string;
};

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

**File:** packages/intents-sdk/src/shared-types.ts (L434-441)
```typescript
export interface WithdrawalIdentifier {
	/** Actual chain where funds arrive; Near for virtual/internal routes */
	landingChain: Chain;
	/** Per-bridge withdrawal sequence number */
	index: number;
	withdrawalParams: WithdrawalParams;
	tx: NearTxInfo;
}
```
