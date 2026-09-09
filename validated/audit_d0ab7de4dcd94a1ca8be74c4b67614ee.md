### Title
POA Bridge withdrawal status/hash matched only by `assetId`, causing status misreport for batched withdrawals of the same token - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain status of a specific withdrawal (identified by `index` inside a NEAR tx) by matching the POA Bridge API's returned list only on `assetId`, ignoring `index`. When a batch withdrawal (`sdk.processWithdrawal` / `signAndSendWithdrawalIntent` with multiple `withdrawalParams`) contains two or more withdrawals of the same token (same `nep141:` asset) in a single NEAR transaction, every one of those withdrawals resolves to the *same* matched record — typically the first one returned by the API — regardless of which index is being queried.

### Finding Description
`describeWithdrawal` in [1](#0-0)  calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which is implemented as: [2](#0-1) 

This function returns `withdrawals.find(...)` — the first record whose `near_token_id` matches the requested `assetId`. It does **not** use `args.index` (which is carried through `WithdrawalIdentifier`, see [3](#0-2) ) or amount/destination to disambiguate between multiple withdrawals of the same asset within one NEAR transaction.

The equality this breaks is: *status/txHash reported for withdrawal at index i* should equal *the actual on-chain outcome of withdrawal i*. Instead, for a batch containing two same-asset withdrawals (e.g., two USDC withdrawals to different destination addresses submitted via `sdk.processWithdrawal({ withdrawalParams: [w0, w1] })`), both `createWithdrawalCompletionPromises` calls end up invoking `describeWithdrawal` with the same `assetId` but different `index`, per [4](#0-3) . Both calls receive the identical matched record from `findMatchingWithdrawal`, so:
- Withdrawal 1 (still pending on-chain) can be reported as `completed` with withdrawal 0's `transfer_tx_hash`.
- If withdrawal 0 fails, withdrawal 1 would also be reported as `failed` with withdrawal 0's reason, even if it actually completed.

The exact same unguarded pattern also exists in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` at [5](#0-4) , used by `waitForWithdrawalCompletion` (see call site at [6](#0-5) ).

The bug is explicitly acknowledged in a code comment as a known limitation rather than a hardened invariant: "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported." [7](#0-6) 

### Impact Explanation
This maps to the "status or hash misreport making an integrator credit or refund twice" High-impact category. An integrator building on top of `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` for a legitimate batch of same-token withdrawals (e.g. paying out multiple users from one internal batch) could:
- Credit/settle withdrawal 1 as complete using withdrawal 0's destination tx hash, before withdrawal 1 has actually landed on-chain (misreport of on-chain outcome), or
- Mark a still-pending or actually-failed withdrawal as `completed` because it was matched to a sibling withdrawal's completed record.

This is a genuine equality break (reported status ≠ actual on-chain outcome for that specific withdrawal index) reachable through normal, non-malicious use of the batch withdrawal API — no privileged or malicious actor is required, only a caller submitting ≥2 same-asset withdrawals in one batch, which the SDK's public API explicitly supports (`WithdrawalParams[]`, see README batch example).

### Likelihood Explanation
Likelihood is moderate: it requires a batch withdrawal containing two or more withdrawals of the *same* `assetId` routed through the POA bridge. The SDK's public batch API (`processWithdrawal`/`signAndSendWithdrawalIntent`/`createWithdrawalCompletionPromises`) permits this combination without validation or rejection, and nothing in `sdk.ts` deduplicates or blocks same-asset batches. Given batch withdrawal is a documented, supported feature, this is a realistic operational scenario (e.g., paying multiple recipients the same token in one transaction).

### Recommendation
Disambiguate matching in `findMatchingWithdrawal` (both in `poa-bridge.ts` and `waitForWithdrawalCompletion.ts`) beyond `assetId` alone — e.g., track already-consumed matches per `(assetId)` group and assign records positionally/by amount as the existing comment suggests, or reject/require the caller to avoid duplicate-asset batches until the POA API supports disambiguation by index. At minimum, `describeWithdrawal` should refuse to reuse a withdrawal record across two different indices within the same polling cycle (e.g., track consumed matches within one `response.withdrawals` array per call), and documentation/API should explicitly disallow same-asset batches to this bridge until fixed.

### Proof of Concept
1. Call `sdk.processWithdrawal({ withdrawalParams: [ {assetId:'nep141:usdc...near', amount:A, destinationAddress: addrX, feeInclusive:false}, {assetId:'nep141:usdc...near', amount:B, destinationAddress: addrY, feeInclusive:false} ] })` — a single NEAR tx batching two USDC withdrawals to different addresses.
2. On the destination side, suppose withdrawal index 0 (to `addrX`) completes with `transfer_tx_hash = "0xAAA"`, while withdrawal index 1 (to `addrY`) is still `PENDING` in the POA Bridge API response.
3. `createWithdrawalCompletionPromises` calls `describeWithdrawal` separately for index 0 and index 1, both with the same `assetId`.
4. `findMatchingWithdrawal` ( [8](#0-7) ) returns the same `COMPLETED` record (`near_token_id` match) for both calls, so index 1's promise also resolves with `{status: "completed", txHash: "0xAAA"}` — a status/hash that does not correspond to withdrawal index 1's actual on-chain outcome.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-322)
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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L35-87)
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

			throw new PoaWithdrawalPendingError(result, txHash, withdrawalCriteria);
		},
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
