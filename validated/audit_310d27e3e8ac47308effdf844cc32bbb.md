### Title
POA Bridge withdrawal status/hash misreport for batched same-asset withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain withdrawal status by matching the POA Bridge API response solely on `assetId`, ignoring the withdrawal's `index` and `destinationAddress`. When a single intent transaction contains more than one withdrawal of the same asset (e.g., two `nep141:btc.omft.near` withdrawals to two different destination addresses), the lookup returns the first API record whose `near_token_id` matches, regardless of which of the two withdrawals it actually belongs to.

### Finding Description
`describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does `withdrawals.find((w) => \`nep141:${w.data.near_token_id}\` === assetId)` [1](#0-0) . The function's own comment acknowledges the limitation: "multiple withdrawals of the same token in a single transaction are not supported" [2](#0-1) .

Higher up, the SDK's withdrawal-completion path explicitly supports batches of withdrawals sharing the same route and dispatches `describeWithdrawal` per-index without any assetId-uniqueness constraint enforced at that layer [3](#0-2) . The test `"maintains indexes specific to bridge route"` demonstrates the SDK calling `describeWithdrawal` with `index: 0`, `index: 1`, `index: 2` for withdrawals that can carry the same `assetId` [4](#0-3) , yet `PoaBridge.describeWithdrawal` never uses that `index` to disambiguate — the same `assetId`-matched record is returned for all of them.

The equality broken is: *the withdrawal status/hash reported for withdrawal N must correspond to withdrawal N's own on-chain outcome*. Instead, when N ≥ 2 withdrawals share an `assetId`, all of them get matched to whichever API record `.find()` happens to return first, which is actually keyed to a different `destinationAddress`/withdrawal in the batch.

The identical matching function (`findMatchingWithdrawal` by `near_token_id` only) exists in `internal-utils`'s `waitForWithdrawalCompletion`, used for a related sync-wait flow [5](#0-4) , showing the flaw is systemic across both bridge status-check paths.

### Impact Explanation
If an integrator submits one NEAR intents transaction containing two POA-bridge withdrawals of the same token to two different destination addresses (a legitimate, unprivileged batching scenario the SDK's own withdrawal-watcher explicitly supports), `describeWithdrawal` will report the same `completed`/`txHash` for both withdrawal identifiers once the first of the two settles on the bridge. An integrator relying on this status to confirm delivery could:
- Mark both withdrawals as `completed` using one destination's tx hash while the second withdrawal's funds have not actually reached its own destination address yet (misdelivery/no-recovery risk from the integrator's perspective), or
- Credit/refund logic keyed off the reported hash could be triggered twice for what the bridge considers a single transfer.

This matches the "status or hash misreport making an integrator credit or refund twice" High-severity impact class.

### Likelihood Explanation
No malicious actor is required — this triggers under normal, documented SDK usage (batched withdrawals of the same asset in one transaction), which the withdrawal-watcher and per-bridge index-tracking code are explicitly designed to support [3](#0-2) . The bug is acknowledged in code comments as a known gap rather than a hypothetical edge case [2](#0-1) , indicating it is reachable whenever an integrator batches ≥2 same-asset POA withdrawals.

### Recommendation
Disambiguate matching using more than `assetId`: incorporate `destinationAddress` (and/or per-asset ordering by `amount`/`index` as the existing comment suggests) so that each `WithdrawalIdentifier`'s `describeWithdrawal` call maps to its own API record rather than the first same-asset record found. Until the POA API supports a stable per-withdrawal correlation ID, the SDK should either reject/serialize batched same-asset POA withdrawals or fall back to conservative "pending" status when ambiguity is detected (i.e., more than one same-asset withdrawal record is unresolved) rather than reusing another withdrawal's hash.

### Proof of Concept
1. Build one intents transaction with two `ft_withdraw` entries, same `assetId: "nep141:btc.omft.near"`, but two distinct `destinationAddress` values (A and B), submitted via `sdk.createWithdrawalIntents`/batched `withdrawalParams`.
2. Call `sdk.waitForWithdrawalCompletion` (or `PoaBridge.describeWithdrawal` directly) for both resulting `WithdrawalIdentifier`s (`index: 0` for A, `index: 1` for B).
3. Once the POA Bridge API reports one of the two transfers (say, to B) as `COMPLETED` with `transfer_tx_hash: "btc-tx-hash-B"`, both `describeWithdrawal({..., index:0, withdrawalParams:{assetId:"nep141:btc.omft.near", destinationAddress:A}})` and `describeWithdrawal({..., index:1, withdrawalParams:{assetId:"nep141:btc.omft.near", destinationAddress:B}})` will return `{status:"completed", txHash:"btc-tx-hash-B"}` because `findMatchingWithdrawal` only checks `assetId` [1](#0-0) , incorrectly reporting withdrawal-to-A as completed with B's transaction hash.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-417)
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
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L418-427)
```typescript
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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L144-153)
```typescript
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
