### Title
POA Bridge withdrawal status/tx-hash misattribution when batching multiple withdrawals of the same asset - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal()` matches the on-chain withdrawal status by `assetId` only, not by `index`. When a batch withdrawal contains more than one withdrawal of the same asset (the SDK explicitly supports batch withdrawals via `BatchWithdrawalResult`/`createWithdrawalIdentifiers`), all such withdrawals resolve to the *same* status entry, so one withdrawal's completion (and destination `txHash`) is reported for a different withdrawal that has not actually completed (or completed to a different destination).

### Finding Description
`describeWithdrawal` for the POA bridge is: [1](#0-0) 

It calls `findMatchingWithdrawal`, which is explicitly documented to only disambiguate by `assetId`: [2](#0-1) 

`Array.prototype.find()` returns the *first* array element whose `near_token_id` matches, regardless of the caller's `index`. The `WithdrawalIdentifier` passed into `describeWithdrawal` does carry a per-withdrawal `index`: [3](#0-2) 

but that `index` is never used to disambiguate multiple same-asset entries returned by the POA API. The identical logic (and identical limitation) exists in the internal-utils helper used to await withdrawal completion: [4](#0-3) 

The SDK's public surface supports creating and watching multiple withdrawals from one call (`BatchWithdrawalResult`, `createWithdrawalIdentifiers`, `watchWithdrawal`): [5](#0-4) 

If a caller submits two withdrawals of the same `assetId` (e.g. two BTC withdrawals to two different destination addresses) in a single batch, both `WithdrawalIdentifier`s (`index: 0` and `index: 1`) will independently call `describeWithdrawal`, and both calls will match the *same* first entry in `response.withdrawals` whose `near_token_id` equals that `assetId`. Consequently:
- Both withdrawal indices report the same `status` and the same destination `txHash`, even though they are two distinct on-chain transfers to different addresses/amounts.
- The watcher (`watchWithdrawal`) will report "completed" with an identical `txHash` for both logical withdrawals as soon as any one of the two backend entries reaches `COMPLETED`.

This breaks the equality "status/txHash reported == actual on-chain outcome of *that* withdrawal index" — an integrator relying on `WithdrawalStatus.txHash` per withdrawal to mark it credited/refunded would treat the second (still pending or failed) withdrawal as completed with the first withdrawal's transaction hash.

### Impact Explanation
This falls into the "status or hash misreport making an integrator credit or refund twice" class. An integrator (e.g., an exchange, custody backend, or any consumer of `IntentsSDK`) that batches two same-asset withdrawals and watches both indices independently could:
- Mark the not-yet-completed withdrawal as completed using the wrong `txHash` (misattributing which destination actually received funds), or
- Credit/finalize both withdrawal legs based on one on-chain completion event.

### Likelihood Explanation
Requires (a) the caller to submit ≥2 withdrawals of the *same* `assetId` in one batch, and (b) POA API returning multiple entries for that `near_token_id` under the same NEAR transaction hash. The code itself documents this as a known, currently-unhandled scenario ("multiple withdrawals of the same token in a single transaction are not supported"), so the maintainers appear aware this is a real edge case rather than a purely theoretical one — but they have not implemented the disambiguation they describe (sorting by amount). The vulnerability is triggered purely by legitimate, unprivileged use of the SDK's public batch-withdrawal API; no malicious external actor or admin action is required.

### Recommendation
Implement the disambiguation already described in the code comments: when matching withdrawals for the same `assetId`, use `index`-aware ordering (e.g., sort API-returned withdrawals for a token by `amount`/`created` and correlate with the corresponding ordering of requested `withdrawalParams` for that asset in the batch) instead of returning the first match. Apply the fix in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` (`findMatchingWithdrawal`) and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` (`findMatchingWithdrawal`). Until fixed, the SDK should explicitly reject/guard batches containing duplicate `assetId` withdrawals routed through the POA bridge rather than silently returning ambiguous status.

### Proof of Concept
1. Build a batch withdrawal with two `WithdrawalParams` entries, both `assetId: "nep141:btc.omft.near"`, different `destinationAddress`, submitted together (indices 0 and 1).
2. POA backend eventually reports two withdrawal records for the same NEAR tx hash, both with `near_token_id: "btc"`, but only the first (index 0's) is `COMPLETED` with `transfer_tx_hash: "hashA"`; the second is still `PENDING`.
3. Call `bridge.describeWithdrawal` for `index: 1`'s `WithdrawalIdentifier`. `findMatchingWithdrawal` still finds the first `withdrawals` entry matching `assetId` (which is the completed one for index 0) and returns `{ status: "completed", txHash: "hashA" }` for withdrawal index 1, even though index 1 has not actually completed and its destination address never received funds tied to `hashA`. [6](#0-5) 
This existing test only verifies correct behavior when the two same-transaction withdrawals are of *different* assets; there is no test covering the same-`assetId` duplicate case, matching the documented gap.

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
