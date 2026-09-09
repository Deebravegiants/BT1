### Title
POA Bridge withdrawal status matched only by `assetId` misattributes destination tx hash across multiple same-token withdrawals in one transaction - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain destination status for a specific withdrawal (identified by `{ tx, index, withdrawalParams }`) by calling `findMatchingWithdrawal()`, which selects a withdrawal record from the POA indexer's response using only the token `assetId`, ignoring `destinationAddress` and `amount` that are already present both in the caller's `withdrawalParams` and in the indexer's response (`withdrawal.data.address`, `withdrawal.data.amount`). When a single NEAR transaction contains multiple withdrawal intents for the same token (e.g., two `ft_withdraw` intents for the same `token` to different `receiver_id`/amounts, which the SDK explicitly supports via batched intents), `.find()` returns the first matching record for every index that shares that `assetId`.

### Finding Description
`findMatchingWithdrawal` is defined as: [1](#0-0) 

and is invoked from `describeWithdrawal`: [2](#0-1) 

The comment on `findMatchingWithdrawal` itself acknowledges: "Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported" [3](#0-2) . The identical pattern (and identical caveat) exists in the sibling implementation used elsewhere in the SDK: [4](#0-3) .

Both `WithdrawalIdentifier` (which carries `index`) and `withdrawalParams` (which carries `destinationAddress` and `amount`) are available at the call site: [5](#0-4) , yet none of `destinationAddress` or `amount` are used to disambiguate between multiple indexer records sharing the same `assetId`. Consequently, `describeWithdrawal()` for withdrawal index 1 (destined to address B) can return `status: "completed", txHash: <hash belonging to withdrawal index 0, destined to address A>`, because both entries satisfy `nep141:${w.data.near_token_id} === assetId`.

This breaks the equality that the reported completion status/hash must correspond to the on-chain outcome of the specific withdrawal being tracked (its own `destinationAddress`/`amount`), not merely to "some withdrawal of the same token in the same NEAR transaction."

### Impact Explanation
The polling logic (`watchWithdrawal`) and the SDK's public completion API (`createWithdrawalCompletionPromises`) treat a `"completed"` status with a `txHash` as definitive proof of settlement for that specific withdrawal: [6](#0-5) [7](#0-6) . If an integrator uses the returned `txHash`/status per withdrawal index to confirm delivery (e.g., to release custody, mark an order complete, or reconcile against a specific destination address), a misattributed hash can cause the wrong withdrawal to be marked "completed" while its actual counterpart is still pending or has a different destination hash. This matches the "status or hash misreport making an integrator credit or refund twice" impact class (High): one destination-address withdrawal is falsely reported as fulfilled using a transaction hash that actually paid a different address/amount.

### Likelihood Explanation
This requires no privileged access and no external actor: any user of the SDK who batches two or more `ft_withdraw` intents for the same token to different destinations/amounts in a single NEAR transaction (a normal, supported use case per the SDK's batching feature) will trigger this code path. The bug is deterministic given the POA indexer returns an unordered list — it is not a hypothetical or admin-triggered scenario, and the code's own comment confirms this "is not supported" without any guard rejecting the unsupported case.

### Recommendation
Disambiguate `findMatchingWithdrawal` using more than `assetId`: additionally match on `destinationAddress` (`w.data.address`) and `amount` (`w.data.amount`), or, if the POA API cannot yet distinguish identical concurrent withdrawals of the same token/amount/destination, fail closed (throw / keep `pending`) rather than returning a possibly-mismatched record, instead of returning the first token match for every index.

### Proof of Concept
1. User submits one NEAR transaction with two `ft_withdraw` intents for the same `token` (`usdc.omft.near`): index 0 → `receiver_id: A`, `amount: 100`; index 1 → `receiver_id: B`, `amount: 200`.
2. POA indexer eventually returns two withdrawal records for that tx hash, both with `near_token_id: "usdc.omft.near"`, one `COMPLETED` with `transfer_tx_hash: "0xA"` (to address A), the other still `PENDING` (to address B).
3. Calling `describeWithdrawal({ tx, index: 1, withdrawalParams: { assetId: "nep141:usdc.omft.near", destinationAddress: B, amount: 200n } })` reaches `findMatchingWithdrawal(withdrawals, "nep141:usdc.omft.near")`, which returns the first array entry — the `COMPLETED` record for address A — via `.find()` at [8](#0-7) .
4. The SDK reports `{ status: "completed", txHash: "0xA" }` for the withdrawal to address B, even though the funds have not actually reached B.

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
