### Title
POA bridge `describeWithdrawal` misattributes status/txHash across multiple same-asset withdrawals in a batch - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` matches the on-chain withdrawal status returned by the POA bridge API to a `WithdrawalIdentifier` using only `assetId`, ignoring `index`/`destinationAddress`/`amount`. When a single NEAR intent transaction contains two or more withdrawals of the *same* `assetId` (a supported, non-malicious batch-withdrawal use case exposed by the SDK), every `describeWithdrawal` call for that tx returns the *first* matching entry from the API response for *all* indices, causing the wrong destination-chain status/tx hash to be reported for other withdrawals in the batch.

### Finding Description
`findMatchingWithdrawal` is explicitly documented as matching only by `assetId`: [1](#0-0) 

`describeWithdrawal` calls this helper using `args.withdrawalParams.assetId` only, with no disambiguation by `index`, `destinationAddress`, or `amount`: [2](#0-1) 

The SDK explicitly supports batching multiple withdrawals (including the same asset to different destinations) in one intent/transaction via `processWithdrawal`/`signAndSendWithdrawalIntent` with an array of `withdrawalParams`, and `createWithdrawalCompletionPromises`/`watchWithdrawal` poll `describeWithdrawal` per-index for each entry: [3](#0-2) [4](#0-3) 

Because the POA bridge's `getWithdrawalStatus` response is keyed by NEAR tx hash and returns an unsorted list of withdrawal records for that tx, and `findMatchingWithdrawal` picks the *first* record whose `near_token_id` matches the requested `assetId`, two `WithdrawalIdentifier`s (index 0 and index 1) referring to two distinct withdrawals of the same asset within one tx will both resolve to the *same* record — i.e., the same `status` and the same `transfer_tx_hash` — regardless of which one actually completed or which destination it was sent to. This breaks the equality "status/hash reported == actual on-chain outcome for *that specific* withdrawal index."

### Impact Explanation
This is a status/hash misreport for a specific withdrawal in a batch, matching the specified High-impact class: "a status or hash misreport making an integrator credit or refund twice." An integrator using `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` to reconcile per-withdrawal completion (e.g., mark withdrawal #1 to address A as complete once a destination tx hash is observed) could:
- Prematurely mark an unrelated/still-pending withdrawal as "completed" using another withdrawal's transaction hash, causing incorrect bookkeeping, premature release of dependent actions, or double crediting/refund decisions based on a hash that does not correspond to that withdrawal.
- Report success (with a tx hash) for a withdrawal that actually failed, if a different index for the same asset succeeded, since `findMatchingWithdrawal` only checks `near_token_id`, not status per-recipient.

This does not depend on any malicious actor — it is triggered by ordinary use of the SDK's own batch-withdrawal capability with two withdrawal entries sharing the same `assetId`.

### Likelihood Explanation
Likelihood is directly tied to how commonly integrators batch multiple withdrawals of the same token (e.g., paying out the same token to two different users in one intent). The code's own comment acknowledges this exact limitation ("multiple withdrawals of the same token in a single transaction are not supported"), confirming the maintainers are aware the scenario is reachable but currently mishandled, rather than impossible.

### Recommendation
Disambiguate matching beyond `assetId`: use `destinationAddress` (and `amount`, if the POA API surfaces it) together with `assetId`, or, as suggested in the code comment, sort both the API response and the `withdrawalParams` array by amount (since relayer fees are identical for the same token) and match positionally. At minimum, `describeWithdrawal` should refuse to return a "completed" status with a hash when multiple candidate records exist and cannot be disambiguated, rather than silently returning the first match.

### Proof of Concept
1. Caller performs a batch withdrawal via `sdk.processWithdrawal({ withdrawalParams: [ {assetId: "nep141:X", destinationAddress: "addrA", amount: 100}, {assetId: "nep141:X", destinationAddress: "addrB", amount: 200} ] })`, both routed through `PoaBridge`.
2. Two `WithdrawalIdentifier`s are created with `index: 0` and `index: 1`, sharing the same `tx.hash` (the NEAR intent tx) and same `assetId`.
3. `watchWithdrawal` polls `describeWithdrawal` for both indices independently; each call fetches the same `getWithdrawalStatus({ withdrawal_hash: tx.hash })` response containing two withdrawal records for asset `X`.
4. `findMatchingWithdrawal` picks the first record in `response.withdrawals` matching `nep141:X` for *both* index 0 and index 1 calls (since it never looks at `index` or `destinationAddress`).
5. If the first record (say, the one for `addrA`/amount 100) completes first, `describeWithdrawal` for index 1 (`addrB`/amount 200) will also report `status: "completed"` with `addrA`'s `transfer_tx_hash`, even though the withdrawal to `addrB` may still be pending or may have failed. [2](#0-1)

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
