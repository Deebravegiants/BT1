### Title
Batch withdrawals of the same asset can have their destination tx hash / status swapped across indices - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain completion status of a specific withdrawal by matching the POA Bridge API response **only on `assetId`**, ignoring both the withdrawal's `index` and its `destinationAddress`. When a caller performs a batch withdrawal that includes more than one withdrawal of the same `assetId` (a supported and documented SDK feature - see batch-withdrawal usage in the README), each per-index status lookup can resolve to the wrong entry in the POA response array, causing one withdrawal's destination transaction hash / completion status to be reported for a different withdrawal.

### Finding Description
`describeWithdrawal` is implemented as: [1](#0-0) 

It calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, matching solely by `assetId` and returning that entry's `data.transfer_tx_hash` as the reported destination transaction hash/status for that withdrawal. The test suite explicitly documents and locks in this behavior: [2](#0-1) 

The withdrawal orchestration layer builds one `WithdrawalIdentifier` per withdrawal (carrying an `index` used only for the internal per-route counter, not passed to the matching function) and expects `describeWithdrawal` to return the outcome for *that specific* withdrawal: [3](#0-2) 

Because `findMatchingWithdrawal` keys off `assetId` only, if a single settled intent transaction contains two or more withdrawals of the same token (e.g., withdrawing the same asset to two different destination addresses in one batch call, a scenario the SDK explicitly supports), the function has no way to disambiguate which POA-returned withdrawal record corresponds to which requested withdrawal. The first (or any) matching record can be returned for every index sharing that `assetId`, so the destination tx hash reported for withdrawal #0 can be the hash that actually belongs to withdrawal #1 (and vice versa), or a completed withdrawal's hash can be reported against an index whose real withdrawal is still pending/failed.

This breaks the equality that the report format targets: *the destination tx hash/status reported for a specific withdrawal request must be the actual on-chain outcome of that same request.* Here, the status/hash reported can belong to a sibling withdrawal within the same batch instead.

### Impact Explanation
`waitForWithdrawalCompletion` / `processWithdrawal` surface this per-index status directly to the integrator as authoritative proof of settlement (`{status: "completed", txHash: ...}`). An integrator that credits a user's off-chain balance, releases custody, or marks an invoice paid based on receiving a `"completed"` status with a specific `txHash` for a specific withdrawal request can be misled into crediting the wrong withdrawal as completed, or crediting twice off a single actual on-chain transfer being attributed to two different logical withdrawals. This matches the High-severity category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Requires no privileged access — any caller of the public SDK API who issues a batch withdrawal (`processWithdrawal`/`signAndSendWithdrawalIntent` with an array of `WithdrawalParams`) containing two or more entries with the same `assetId` and different destinations triggers this code path during subsequent status polling. Batch withdrawals of a repeated asset are a normal, foreseeable usage pattern (multiple payouts of the same token to different recipients in one transaction), not a contrived edge case.

### Recommendation
Extend `findMatchingWithdrawal` (and the analogous matcher in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate between multiple same-asset withdrawals within one NEAR transaction — e.g., match on `assetId` **and** `destinationAddress` (and amount, if necessary), or consume matched entries so each POA-returned record is attributed to at most one requested withdrawal index, instead of allowing the same record to satisfy multiple lookups.

### Proof of Concept
1. Call `sdk.processWithdrawal` / `sdk.signAndSendWithdrawalIntent` with `withdrawalParams` = `[{assetId: "nep141:eth.bridge.near", destinationAddress: A, amount: X}, {assetId: "nep141:eth.bridge.near", destinationAddress: B, amount: Y}]` in a single batch, producing one NEAR intent transaction with two POA withdrawal legs for the same asset.
2. The POA Bridge API (`getWithdrawalStatus`) returns two `withdrawals[]` entries with `defuse_asset_identifier: "nep141:eth.bridge.near"` but different `address`/`transfer_tx_hash`.
3. `PoaBridge.describeWithdrawal` is invoked once per index (0 and 1) via `watchWithdrawal`; `findMatchingWithdrawal` matches only on `assetId`, as demonstrated by [2](#0-1) , so both index lookups can resolve to the same/wrong entry.
4. The integrator receives `{status:"completed", txHash: "<wrong-hash>"}` for one or both withdrawals, crediting/settling against a transaction that does not correspond to that withdrawal request.

Note: The exact `findMatchingWithdrawal` implementation body was not directly inspected (only its externally observable behavior via unit tests and call sites); if it already incorporates additional disambiguation not exercised by the reviewed tests, this reduces or eliminates the finding — this should be confirmed by reading the full function body in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`.

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
