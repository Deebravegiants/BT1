Confirmed: `createWithdrawalIdentifiers` assigns a per-bridge sequential `index` to each withdrawal in a batch (`indexes.get(bridge.route) ?? 0`, incremented per withdrawal on the same bridge route), independent of asset identity [1](#0-0) . This confirms two withdrawals of the same `assetId` to different destinations on the same route legitimately receive different, well-defined indexes (0 and 1). However, `PoaBridge.describeWithdrawal` never uses that `index` — it calls `findMatchingWithdrawal`, which selects the first withdrawal in the (documented "unsorted") API response list whose `near_token_id` matches `assetId`, ignoring `index`, `destinationAddress`, and `amount` entirely [2](#0-1) . The same pattern exists in the standalone `waitForWithdrawalCompletion` helper used by integrators to poll completion by `assetId` alone [3](#0-2) .

### Title
PoA bridge withdrawal-status matching by `assetId` alone causes destination/status/hash cross-assignment for same-token batch withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
When a single NEAR intents transaction contains multiple withdrawals of the *same* token via the PoA bridge (e.g., two withdrawals of `nep141:btc.omft.near` to two different destination addresses, batched in one `signAndSendIntent`/multi-withdraw call — a feature explicitly advertised in the SDK's README under "Batch Intents"/"Batch Processing" [4](#0-3) ), `PoaBridge.describeWithdrawal` cannot distinguish between the two withdrawals. It matches purely by `assetId` via `findMatchingWithdrawal`, ignoring the `index` that `createWithdrawalIdentifiers` assigned per-withdrawal [5](#0-4) .

### Finding Description
`createWithdrawalIdentifiers` builds a `WithdrawalIdentifier` for every withdrawal in a batch, assigning a monotonically increasing `index` per bridge route [6](#0-5) . This `index` is meant to disambiguate multiple withdrawals of the same route/asset within one NEAR transaction. `watchWithdrawal`/`describeWithdrawal` is then called per-`WithdrawalIdentifier`, expected to report the on-chain outcome (`txHash`, `status`) *for that specific withdrawal*.

For the PoA bridge, `describeWithdrawal` fetches the full list of withdrawals for the NEAR tx hash and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does `withdrawals.find((w) => "nep141:" + w.data.near_token_id === assetId)` — the *first* matching entry, irrespective of `index`, `destinationAddress`, or `amount` [2](#0-1) . The code comment explicitly acknowledges: "This means multiple withdrawals of the same token in a single transaction are not supported" [7](#0-6) , and a test titled "matches withdrawal by assetId, not by index" documents this as accepted (not fixed) behavior [8](#0-7) .

Consequently, when two withdrawals of the same token (e.g. two BTC withdrawals to two different addresses/amounts, batched by a normal, unprivileged user) are submitted together:
- Both `watchWithdrawal` calls (index 0 and index 1) resolve to whichever of the two API-returned withdrawal records happens to match first by `assetId`.
- Both calls can report the *same* `txHash`/`completed` status, even though only one of the two on-chain transfers actually reached its destination.
- The reported status is therefore not the true on-chain outcome for the specific withdrawal instance being watched — breaking the equality "status/hash reported == on-chain outcome for this withdrawal."

The same defect exists independently in `internal-utils`' `waitForWithdrawalCompletion`, which matches purely by `assetId` with no index/amount/address disambiguation [3](#0-2) .

### Impact Explanation
An integrator relying on `waitForIntentSettlement`/`createWithdrawalCompletionPromises` to confirm completion of a batch of same-token withdrawals could receive a false "completed" status with a `txHash` for the wrong withdrawal — e.g., crediting/marking-settled a withdrawal that in fact failed or is still pending, or reporting the same destination `txHash` for two distinct user withdrawals. This matches the "High" impact category: "a status or hash misreport making an integrator credit or refund twice." No funds are stolen directly by the caller from someone else's balance, but the misreport can cause an integrator to prematurely release funds, double-count a settlement, or fail to detect a stuck/failed withdrawal for one of two batched same-asset transfers.

### Likelihood Explanation
The trigger requires only routine use of the SDK's advertised batch-withdrawal capability with two withdrawals of the same `assetId` via the PoA bridge in one NEAR transaction — no privileged access, relayer collusion, or malicious peer behavior is needed, and no user-supplied malicious input is required beyond normal batching. Likelihood is limited by (a) needing two same-asset PoA withdrawals in the same batch (a legitimate but not necessarily default usage pattern) and (b) the POA API's list being "unsorted," so the exact incorrect index that gets matched can vary between polls, potentially self-correcting on retry — but during the observation window a wrong/duplicate status can be observed and acted upon.

### Recommendation
Extend `findMatchingWithdrawal` (in both `poa-bridge.ts` and `internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`) to disambiguate same-`assetId` withdrawals using additional fields returned by the API (e.g., `destinationAddress`/`address`, `amount`, and the per-bridge `index`), rather than matching on `assetId` alone. If the API cannot supply a stable per-withdrawal correlation key, the SDK should refuse to support (or explicitly warn/throw for) batches containing more than one withdrawal of the same `assetId` on the PoA route, rather than silently returning a status for an unrelated withdrawal instance.

### Proof of Concept
1. Submit one NEAR intents transaction containing two `ft_withdraw` intents for the same PoA-bridged token (e.g., `nep141:btc.omft.near`), with different destination Bitcoin addresses/amounts, using the SDK's batch withdrawal support.
2. `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` to the two withdrawals for the `poa_bridge` route.
3. Call `watchWithdrawal`/`describeWithdrawal` for both identifiers concurrently while the PoA bridge API has processed only one of the two transfers as `COMPLETED`.
4. Both `describeWithdrawal` calls query `getWithdrawalStatus` and each independently runs `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which returns the *same* (first-matching) completed record for both index-0 and index-1 identifiers.
5. Both watchers resolve to `{ status: "completed", txHash: <same-dest-tx-hash> }`, even though the second withdrawal's actual on-chain transfer has not completed (or went to a different address) — demonstrated directly by the existing test `"matches withdrawal by assetId, not by index"` in `poa-bridge.test.ts`, which asserts this exact same-token matching behavior [8](#0-7) .

### Citations

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

**File:** packages/intents-sdk/README.md (L194-203)
```markdown
### Withdrawals

Complete withdrawal functionality from Near Intents to external chains:

- **Cross-Chain Transfers**: Withdraw to 20+ supported blockchains
- **Multi-Bridge Support**: Hot Bridge, PoA Bridge, Omni Bridge
- **Batch Processing**: Process multiple withdrawals at a time
- **Fee Management**: Automatic fee estimation with quote support
- **Validation**: Built-in validation for withdrawal constraints
- **Status Tracking**: End-to-end monitoring from intent to destination
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
