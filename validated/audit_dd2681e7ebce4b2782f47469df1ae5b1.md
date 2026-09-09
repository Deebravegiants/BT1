### Title
Withdrawal status/tx-hash misreported when a batch contains multiple withdrawals of the same asset - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the completion status of a specific withdrawal by matching entries returned from the POA bridge API using only the `assetId`, not the withdrawal's index or destination address. When a caller submits multiple withdrawals of the *same* asset within a single batch (a legitimate use case explicitly supported by `IntentsSDK.waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`, which process arrays of `WithdrawalParams` and correlate results by array index), the matching logic can attribute the wrong entry's status and destination transaction hash to a given withdrawal.

### Finding Description
`describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` and returns the status/hash of whichever entry matches that `assetId` [1](#0-0) . The accompanying comment and test confirm the design intent is only to disambiguate by asset, explicitly stating matching is "by assetId, not by index" [2](#0-1) .

This is safe when a batch contains at most one withdrawal per `assetId` (as in all the observed test cases: distinct `chain`/`assetId` per entry). However, `WithdrawalWatcher`/`createWithdrawalCompletionPromises` iterate over an array of `WithdrawalParams` and call `describeWithdrawal` once per entry, correlating results strictly by array `index` [3](#0-2) [4](#0-3) . If two withdrawals in the same batch share the same `assetId` (e.g., withdrawing the same token to two different destination addresses in one intent), `findMatchingWithdrawal` has no way to distinguish which POA API entry corresponds to which requested withdrawal, since it filters only on `assetId`/`near_token_id`, not `destinationAddress`, `amount`, or an equivalent per-item identifier.

This breaks the equality: "status/hash reported for withdrawal N == the on-chain outcome for withdrawal N." A caller polling `describeWithdrawal`/`waitForWithdrawalCompletion` for withdrawal index 1 could instead receive the `COMPLETED` status and `transfer_tx_hash` belonging to withdrawal index 0 (or vice versa), while its own withdrawal is still pending or has gone to a different destination.

### Impact Explanation
An integrator relying on the reported status/tx hash to confirm a specific withdrawal (to a specific destination address) has completed could act on a hash that actually belongs to a different withdrawal in the same batch. This matches the "status or hash misreport making an integrator credit or refund twice" impact category — e.g., crediting a user's off-platform record as settled based on the wrong transaction, or releasing funds/finalizing an off-chain obligation for withdrawal B using proof that only demonstrates withdrawal A completed.

### Likelihood Explanation
Requires the caller to batch multiple withdrawals of the identical `assetId` (same token) to different destinations within one intent — a pattern the SDK's public batch APIs (`waitForWithdrawalCompletion`, `createWithdrawalCompletionPromises`) do not prevent. Whether the underlying POA API can actually return multiple entries for the same `near_token_id` within one `withdrawal_hash` response, and the exact matching predicate inside `findMatchingWithdrawal` (its full implementation was not available for inspection in this session), could not be fully confirmed — this is a caveat on likelihood.

### Recommendation
Have `findMatchingWithdrawal` disambiguate using additional fields present in the POA response (e.g., `destinationAddress`/`address`, and/or an explicit per-item ordinal if the API provides one) in addition to `assetId`/`near_token_id`, rather than assetId alone. If the POA API cannot support per-item disambiguation for same-asset batch withdrawals, the SDK should either reject/warn on same-asset batches routed through POA, or clearly document this limitation so integrators avoid relying on per-index correctness in that scenario.

### Proof of Concept
1. Submit a batch withdrawal intent containing two `WithdrawalParams` with the same `assetId` (e.g., `nep141:btc.omft.near`) but different `destinationAddress` values, routed via `PoaBridge`.
2. Call `sdk.waitForWithdrawalCompletion({ withdrawalParams: [w0, w1], intentTx })`, which internally calls `bridge.describeWithdrawal` once per index, each looking up `findMatchingWithdrawal(response.withdrawals, assetId)` [5](#0-4) .
3. When the POA bridge API (`getWithdrawalStatus`) returns two `COMPLETED` entries for the same `near_token_id`/`assetId` (one per destination), `findMatchingWithdrawal` matching purely on assetId will return the same (or an arbitrarily ordered) entry for both index-0 and index-1 lookups, causing at least one of the two calls to report a `transfer_tx_hash` that does not correspond to that withdrawal's actual destination.

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

**File:** packages/intents-sdk/src/sdk.waitForWithdrawalCompletion.test.ts (L99-124)
```typescript
	it("maintains indexes specific to bridge route", async () => {
		const { sdk, mockBridge } = setupMocks();

		vi.mocked(mockBridge.describeWithdrawal).mockResolvedValue({
			status: "completed",
			txHash: "fake-dest-hash",
		});

		await sdk.waitForWithdrawalCompletion({
			intentTx: { accountId: "foo.near", hash: "fake-hash" },
			withdrawalParams: [withdrawalParams, withdrawalParams, withdrawalParams],
		});

		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			1,
			expect.objectContaining({ index: 0 }),
		);
		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			2,
			expect.objectContaining({ index: 1 }),
		);
		expect(mockBridge.describeWithdrawal).toHaveBeenNthCalledWith(
			3,
			expect.objectContaining({ index: 2 }),
		);
	});
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-47)
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
```
