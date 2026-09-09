### Title
`PoaBridge.describeWithdrawal()` matches by `assetId` only, misreporting completion status/txHash for batched same-token withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
When a batch of withdrawals contains two or more withdrawals of the **same** `assetId` (e.g. two BTC withdrawals to different destination addresses in one intent), `PoaBridge.describeWithdrawal()` cannot disambiguate between them. It selects the first API entry whose `near_token_id` matches the requested `assetId`, regardless of destination address or amount, so a caller polling for withdrawal #1's status can be told it "completed" with the transaction hash that actually belongs to withdrawal #0 (or vice versa).

### Finding Description
`describeWithdrawal()` fetches all withdrawal records for a NEAR tx hash and calls `findMatchingWithdrawal()`: [1](#0-0) 

`findMatchingWithdrawal` matches solely on `assetId`: [2](#0-1) 

The code's own comment acknowledges the limitation: "multiple withdrawals of the same token in a single transaction are not supported" [3](#0-2) , and a test explicitly documents the intended behavior is "matches withdrawal by assetId, not by index" [4](#0-3) .

This status feeds directly into `watchWithdrawal()`, which treats a `"completed"` status as ground truth and resolves the destination transaction hash to the caller: [5](#0-4) 

That hash is returned all the way up through `sdk.waitForWithdrawalCompletion` / `sdk.processWithdrawal` as the authoritative destination transaction for that specific `withdrawalParams` entry, without any secondary check against destination address or amount. The equality broken is: *the on-chain status/txHash reported for withdrawal index N* is not guaranteed to equal *the on-chain outcome for withdrawal index N* — it can instead be the outcome of a different withdrawal (index M) with the same `assetId` but a different `destinationAddress`/`amount` in the same batch.

### Impact Explanation
An integrator building on top of `intents-sdk` who processes batch withdrawals (`processWithdrawal`/`createWithdrawalCompletionPromises` with multiple `withdrawalParams` entries sharing an `assetId`) can receive a `completed` status with a `txHash` for the wrong leg of the batch. Concretely:
- Withdrawal A (to address X) may be reported as completed using the txHash that actually paid out withdrawal B (to address Y), or vice versa.
- An integrator that credits/marks a user's withdrawal as done based on this status could incorrectly mark A as fulfilled while it is still pending/failed, or double-count a single on-chain payout as fulfilling two different withdrawal requests.

This matches the High-severity criterion "a status or hash misreport making an integrator credit or refund twice." It does not itself move funds (the underlying POA relayer still pays the correct destination), but it corrupts the SDK's completion/status API that integrators rely on for accounting, refund, and support decisions.

### Likelihood Explanation
This triggers whenever a caller submits ≥2 withdrawal legs with the identical `assetId` in one `withdrawalParams` batch — a supported and documented use case (`sdk.processWithdrawal({ withdrawalParams: [...] })` explicitly allows arrays, and nothing in the SDK's type system or `supports()`/`validateWithdrawal()` logic rejects duplicate `assetId`s in a batch). No malicious actor is required; it is a normal, foreseeable usage pattern (e.g., paying two different users the same token in one intent).

### Recommendation
- Disambiguate matching using more of the available fields (e.g., pair sorted API results with sorted local withdrawal params by `amount`/`destinationAddress`, as the existing code comment suggests) instead of matching purely by `assetId`.
- Until the POA bridge API supports per-leg identifiers, either: (a) reject/warn on batches containing duplicate `assetId` entries routed through `PoaBridge`, or (b) require callers to pass an explicit correlation ID and surface a clear "ambiguous" status (rather than a definitive `completed` with a possibly-wrong `txHash`) when duplicates are detected.

### Proof of Concept
1. Build a batch withdrawal with two entries, both `assetId: "nep141:btc.omft.near"`, one to `destinationAddress: "addrX"` (amount 100000n) and one to `destinationAddress: "addrY"` (amount 200000n), submitted in a single NEAR intent tx.
2. The POA bridge relayer executes both, producing two withdrawal records under the same `tx.hash`, e.g.
   - `{ near_token_id: "btc.omft.near", transfer_tx_hash: "tx-for-addrX", amount: 100000 }`
   - `{ near_token_id: "btc.omft.near", transfer_tx_hash: "tx-for-addrY", amount: 200000 }`
3. Call `bridge.describeWithdrawal({ index: 1, withdrawalParams: { assetId: "nep141:btc.omft.near", destinationAddress: "addrY", ... }, tx })`.
4. `findMatchingWithdrawal` (poa-bridge.ts:418-427) returns `withdrawals.find(w => "nep141:"+w.data.near_token_id === assetId)`, which is `Array.prototype.find` — it returns the **first** array element matching the assetId regardless of `index`, i.e. it can return the `addrX` record even though the caller asked about `index: 1`/`addrY`.
5. The SDK reports `{ status: "completed", txHash: "tx-for-addrX" }` for the withdrawal that was actually destined for `addrY`, exactly mirroring the existing unit test's demonstrated behavior at [4](#0-3)  (which only happens to pass because the test uses two *different* `assetId`s — swap them to identical `assetId`s with different destinations to reproduce the misreport).

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1107)
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
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-51)
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
```
