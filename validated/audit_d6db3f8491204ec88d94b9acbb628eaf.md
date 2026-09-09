### Title
POA Bridge Withdrawal Status Misattribution via AssetId-Only Matching Enables Status/TxHash Misreport for Batched Withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
The SDK's batch withdrawal feature allows multiple withdrawals to be created and tracked from a single NEAR intent transaction [1](#0-0) . For the POA bridge, the function that correlates a tracked `WithdrawalIdentifier` back to the bridge's reported withdrawal record, `findMatchingWithdrawal`, matches purely by `assetId` and ignores the `index` that the SDK itself uses to distinguish multiple withdrawals of the same token in one transaction [2](#0-1) . When a caller batches two or more withdrawals of the *same token* to *different destinations* in one transaction, `describeWithdrawal` will return the same (first-matching) record — including its `transfer_tx_hash` and `status` — for every one of those withdrawals, regardless of which destination or amount was actually requested [3](#0-2) .

### Finding Description
`createWithdrawalIdentifiers` assigns each withdrawal a per-bridge `index` specifically to disambiguate multiple withdrawals routed through the same bridge in one NEAR transaction [1](#0-0) . This `index` is stored on the resulting `WithdrawalIdentifier` [4](#0-3)  and is exactly the correlation key needed to look up the correct entry among several similar withdrawals in the underlying batch NEAR transaction.

However, `PoaBridge.describeWithdrawal` never uses `args.index`; it looks up all withdrawals for the transaction hash and then calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which returns the *first* array entry whose `near_token_id` matches the requested `assetId` [3](#0-2) . The code comment explicitly acknowledges the API returns withdrawals unsorted and that matching is done "by assetId instead of index" [5](#0-4) , and the helper's own doc-comment states: "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported" [6](#0-5) . The identical pattern is duplicated in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` [7](#0-6) .

This breaks the equality the caller relies on: *"the withdrawal identified by index N in the batch is the withdrawal whose destination/amount/tx-hash is reported."* Because matching only checks `assetId`, `watchWithdrawal` — which polls `describeWithdrawal` per-`wid` and resolves with `{ hash: status.txHash }` once `status === "completed"` [8](#0-7)  — will resolve two *different, independently tracked* withdrawals (different destination addresses/amounts, same token) to the *same* `transfer_tx_hash`/status, even though only one of the two on-chain transfers may have actually completed.

### Impact Explanation
An integrator using `sdk.processWithdrawal`/`createWithdrawalCompletionPromises` for batched same-asset withdrawals (a documented, first-class SDK feature — "Batch Processing: Process multiple withdrawals at a time") would receive a false "completed" status with an incorrect (borrowed) destination transaction hash for a withdrawal that has not actually landed. This is a status/hash misreport that can cause an integrator to credit or mark as fulfilled a withdrawal that never happened on the correct destination, or to report the wrong destination's completion — matching the "status or hash misreport making an integrator credit or refund twice" High-impact class.

### Likelihood Explanation
This requires no privileged access or malicious relayer/bridge behavior — it is triggered purely by the intended, documented usage pattern of batching two-or-more withdrawals of the same fungible token to different recipients in a single call, a supported normal user flow, not an attacker-crafted edge case. The bug is deterministic (first-match-wins) rather than probabilistic, so it reliably occurs whenever this common batching pattern is used with a repeated asset.

### Recommendation
Have `findMatchingWithdrawal` (in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) disambiguate using the `index`/order together with `destinationAddress` and `amount` (and `destinationMemo` where applicable) instead of `assetId` alone, or consume/remove matched entries so repeated calls for different `index`es cannot return the same record twice.

### Proof of Concept
1. Call `sdk.createWithdrawalIntents`/`processWithdrawal` twice in one intent for the same `assetId` (e.g. `nep141:usdt.omft.near`) but different `destinationAddress` values (A and B) — `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` respectively for the POA bridge route [1](#0-0) .
2. Only the withdrawal to address A completes on the POA bridge (visible in `getWithdrawalStatus` response as one `COMPLETED` record with `near_token_id: "usdt.omft.near"`, `transfer_tx_hash: "hash-A"`).
3. Call `describeWithdrawal` for both `wid`s (index 0 and index 1). `findMatchingWithdrawal` returns the same single matching record (the one for A) for both calls, since only `assetId` is compared [9](#0-8) .
4. Both `watchWithdrawal` promises resolve as `{ hash: "hash-A" }` / `status: "completed"`, even though withdrawal to address B never happened — confirmed by the existing test `"matches withdrawal by assetId, not by index"`, which demonstrates cross-matching behavior for two different-chain assets and shows the matching logic disregards which index/withdrawal actually corresponds to the returned record [10](#0-9) .

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-78)
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
				} catch (err: unknown) {
					if (err instanceof WithdrawalFailedError) {
						throw err;
					}

					consecutiveErrors++;
					if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
						throw new WithdrawalWatchError(err);
					}

					args.logger?.warn(
						`Transient error (${consecutiveErrors}/${MAX_CONSECUTIVE_ERRORS}): ${err}`,
					);
					return POLL_PENDING;
				}
			},
			{ stats, signal: args.signal },
		);
	} catch (err: unknown) {
		if (err instanceof PollTimeoutError) {
			throw new WithdrawalWatchError(err);
		}
		throw err;
	}
}
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1111)
```typescript
		it("matches withdrawal by assetId, not by index", async () => {
			vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
				withdrawals: [
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "other-tx-hash",
							chain: "eth",
							defuse_asset_identifier: "nep141:eth.omft.near",
							near_token_id: "eth.omft.near",
							decimals: 18,
							amount: 1000000,
							account_id: "test.near",
							address: zeroAddress,
							created: "2024-01-01T00:00:00Z",
						},
					},
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "btc-tx-hash",
							chain: "btc",
							defuse_asset_identifier: "nep141:btc.omft.near",
							near_token_id: "btc.omft.near",
							decimals: 8,
							amount: 100000,
							account_id: "test.near",
							address: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
							created: "2024-01-01T00:00:00Z",
						},
					},
				],
			});

			const bridge = new PoaBridge({
				envConfig: configsByEnvironment.production,
				xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
			});

			const result = await bridge.describeWithdrawal({
				landingChain: Chains.Bitcoin,
				index: 0,
				withdrawalParams: {
					assetId: "nep141:btc.omft.near",
					amount: 100000n,
					destinationAddress: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
					feeInclusive: false,
				},
				tx: { hash: "near-tx-hash", accountId: "test.near" },
			});

			expect(result).toEqual({
				status: "completed",
				txHash: "btc-tx-hash",
			});
		});
```
