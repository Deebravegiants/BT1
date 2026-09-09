### Title
POA Bridge Withdrawal Status Matches by `assetId` Only, Causing Cross-Withdrawal Status/Hash Misreport in Batched Withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain destination status/hash for a specific withdrawal by matching entries returned from the POA indexer using only the withdrawal's `assetId`, not its `index`, `destinationAddress`, or `amount`. When a single NEAR transaction contains multiple withdrawals of the *same* asset to *different* destinations (a legitimate batch-withdrawal scenario supported elsewhere in the SDK), this matching breaks the equality between "the withdrawal identifier being queried" and "the withdrawal entry whose status/hash is returned," causing one withdrawal to be reported as completed using another withdrawal's destination transaction hash.

### Finding Description
`describeWithdrawal` retrieves the withdrawal list scoped to a NEAR transaction hash and then calls: [1](#0-0) 

```
// Response list is unsorted, so we match by assetId instead of index
const withdrawal = findMatchingWithdrawal(
    response.withdrawals,
    args.withdrawalParams.assetId,
);
```

The comment explicitly states the design intent: since the POA API returns an unordered list, matching was moved from positional `index` to `assetId`. This fixed the case where entries are reordered, but it does not disambiguate between **multiple withdrawals of the same asset in the same batch transaction** — a case the SDK itself supports, as shown by `createWithdrawalIdentifiers`, which assigns per-route indices to allow several withdrawals routed through the same bridge in one call: [2](#0-1) 

If a user (or integrator on a user's behalf) submits two POA-bridge withdrawals of the same `assetId` (e.g., two BTC withdrawals to different addresses) inside one NEAR transaction, both resulting `WithdrawalIdentifier`s (`index: 0` and `index: 1`) share the same `assetId`. `findMatchingWithdrawal` only keys off `assetId`, so calling `describeWithdrawal` for either identifier returns the *first* matching entry in the unsorted list — regardless of which entry actually corresponds to that index/destination. This is corroborated by the regression tests that intentionally validate assetId-only matching without checking destination address or index: [3](#0-2) 

The equality broken is: *the destination transaction hash reported for withdrawal N* is not guaranteed to be *the destination transaction hash that actually corresponds to withdrawal N's destination address/amount* when duplicates of the same asset exist in a batch.

### Impact Explanation
An integrator relying on `describeWithdrawal`/`waitForWithdrawalCompletion` to confirm delivery and credit a user's off-chain balance could receive a `completed` status with a `txHash` belonging to a *different* withdrawal within the same batch. This can cause the integrator to mark the wrong withdrawal as settled (crediting/closing a support case for a withdrawal that didn't actually go to its intended destination) while the true withdrawal for that identifier remains unconfirmed — a status/hash misreport that can make an integrator credit incorrectly, matching the "High" impact category (status or hash misreport making an integrator credit or refund twice).

### Likelihood Explanation
This requires a fairly specific but realistic condition: a batch of withdrawals in one NEAR transaction containing two or more entries with the identical `assetId` routed through the POA bridge. The SDK's own batch-withdrawal support (`createWithdrawalIdentifiers`) makes this reachable without any privileged action — any caller building multiple same-asset withdrawals into one transaction triggers the ambiguous matching path.

### Recommendation
Disambiguate `findMatchingWithdrawal` using more than `assetId` — include `destinationAddress` (and ideally `amount`) to uniquely identify each withdrawal in a batch, and only fall back to positional matching once entries are proven unique on `assetId` alone. Add tests covering multiple same-asset, different-destination withdrawals in a single transaction to confirm each `WithdrawalIdentifier` resolves to its own correct entry.

### Proof of Concept
1. Submit one NEAR transaction with two POA-bridge withdrawal intents, both `assetId: "nep141:btc.omft.near"`, but `destinationAddress: A` (index 0) and `destinationAddress: B` (index 1).
2. POA indexer completes destination B's transfer first (`transfer_tx_hash: "hashB"`) while A is still pending.
3. Call `describeWithdrawal` for the `WithdrawalIdentifier` with `index: 0` (destination A). Because `findMatchingWithdrawal` only matches on `assetId`, it returns the completed entry for B, yielding `{ status: "completed", txHash: "hashB" }` even though A's transfer has not completed — as demonstrated by the existing test asserting assetId-only matching behavior: [3](#0-2)

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
