### Title
Ambiguous withdrawal-status matching in POA bridge misreports which withdrawal completed when a transaction contains multiple withdrawals of the same asset - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal()` resolves the status of a specific withdrawal (identified by `index` inside a `WithdrawalIdentifier`) by calling `findMatchingWithdrawal()`, which selects an entry from the POA bridge response purely by `assetId`, ignoring both `index` and `amount`/`destinationAddress`. When a single NEAR transaction contains more than one withdrawal of the *same* asset, every `describeWithdrawal()` call for that asset (regardless of which withdrawal index it is checking) resolves to the *same* first-matching API entry, so the reported `status`/`txHash` for one withdrawal index does not correspond to the actual on-chain outcome of that particular withdrawal.

### Finding Description
`describeWithdrawal` looks up the POA bridge status list for the NEAR tx and hands it to `findMatchingWithdrawal`: [1](#0-0) 

`findMatchingWithdrawal` matches solely on `assetId` (via `near_token_id`), explicitly by design/comment, and does not disambiguate by `index`, `amount`, or `destinationAddress`: [2](#0-1) 

The `WithdrawalIdentifier.index` field exists precisely to distinguish multiple withdrawals from the same transaction, and the calling code (`watchWithdrawal`) treats the returned `WithdrawalStatus` as authoritative for that specific index: [3](#0-2) [4](#0-3) 

Because `.find()` always returns the first matching entry, `describeWithdrawal({index: 0, assetId: "nep141:X", ...})` and `describeWithdrawal({index: 1, assetId: "nep141:X", ...})` for two distinct withdrawals of asset `X` in the same NEAR tx both resolve to the *same* underlying POA withdrawal record. The equality broken is: "status reported for withdrawal at index N" should equal "the on-chain outcome of withdrawal N", but instead it equals "the on-chain outcome of whichever same-asset withdrawal appears first in the (explicitly documented as unsorted) API response."

The internal-utils analog `waitForWithdrawalCompletion` has the identical limitation, matching only by `assetId` criteria with no index/amount disambiguation: [5](#0-4) 

The code comments in both places explicitly acknowledge this as a known, unresolved limitation ("multiple withdrawals of the same token in a single transaction are not supported").

### Impact Explanation
If a caller (integrator) submits an intent with two withdrawals of the same token to different destinations/amounts, once the first of the two settles on the POA bridge, `describeWithdrawal` for *both* indices will report `status: "completed"` with the *same* `txHash`, even though the second withdrawal may still be pending or could later fail independently. An integrator polling per-index status (as `watchWithdrawal` does) would falsely conclude both withdrawals succeeded and could release/credit downstream funds or mark both as done, based on a single actual on-chain transfer — a status/hash misreport that can cause a double credit, matching the "High" impact category ("a status or hash misreport making an integrator credit or refund twice").

### Likelihood Explanation
This does not require any malicious actor — it triggers whenever a legitimate user or integrator batches two or more withdrawals of the identical token within one intents.near transaction, a supported and unremarkable usage pattern for the SDK (multiple `WithdrawalParams` entries per intent). The bug is deterministic and always manifests in that scenario, though it is explicitly called out as a known/accepted limitation in code comments, which lowers confidence that this is an unknown or newly discovered issue.

### Recommendation
Disambiguate matching by including `amount` (and/or `destinationAddress`) alongside `assetId`, or, once the POA API sorts/labels withdrawals deterministically, match on `index` after sorting both the withdrawal params and the API response by a stable key (e.g., amount) as already suggested in the existing code comment. At minimum, `findMatchingWithdrawal` should exclude entries already consumed by an earlier-index match within the same call site so distinct indices cannot collapse onto the same record.

### Proof of Concept
1. Build an intent with two withdrawals in the same NEAR tx, both for asset `nep141:eth.omft.near`, but different `destinationAddress`/`amount` (index 0 and index 1).
2. POA bridge processes and completes withdrawal index 0 first; its status list contains one `COMPLETED` entry for `near_token_id: "eth.omft.near"`.
3. Caller invokes `describeWithdrawal({..., index: 0, assetId: "nep141:eth.omft.near"})` → returns `{status:"completed", txHash: "<index0-hash>"}` (correct).
4. Caller invokes `describeWithdrawal({..., index: 1, assetId: "nep141:eth.omft.near"})` before withdrawal 1 is actually processed → `findMatchingWithdrawal` still returns the *same* first `COMPLETED` entry (since `.find` is index-agnostic) → incorrectly returns `{status:"completed", txHash: "<index0-hash>"}` for withdrawal 1, even though it has not settled on-chain. [6](#0-5)

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

**File:** packages/intents-sdk/src/shared-types.ts (L434-457)
```typescript
export interface WithdrawalIdentifier {
	/** Actual chain where funds arrive; Near for virtual/internal routes */
	landingChain: Chain;
	/** Per-bridge withdrawal sequence number */
	index: number;
	withdrawalParams: WithdrawalParams;
	tx: NearTxInfo;
}

/**
 * Represents the current state of a withdrawal as returned by bridge adapters.
 *
 * Error handling follows AWS SDK "describe" API patterns:
 * - **Thrown errors**: Infrastructure failures (network, auth, service unavailable).
 *   Meaning: "I couldn't check the status."
 * - **`failed` status**: Job-level failure reported by the bridge.
 *   Meaning: "I checked, and the withdrawal failed."
 *
 * @see https://docs.aws.amazon.com/AmazonS3/latest/userguide/batch-ops-job-status.html
 */
export type WithdrawalStatus =
	| { status: "pending" }
	| { status: "completed"; txHash: string | null }
	| { status: "failed"; reason: string };
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L33-53)
```typescript
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
