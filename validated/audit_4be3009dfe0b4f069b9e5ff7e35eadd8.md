## Analysis

The Sherlock report's bug class is: an aggregation/lookup that fails when an item can't be uniquely identified, causing the wrong on-chain state to be reported. The closest reachable analog in this repo is `findMatchingWithdrawal` in the POA bridge adapter, which matches a withdrawal record by `assetId` alone instead of by index, so when multiple withdrawals of the *same* asset occur inside one NEAR transaction, `describeWithdrawal()` returns the *first* matching record's status/hash for every withdrawal index that shares that asset — misreporting the on-chain outcome for all but one of them.

### Title
Withdrawal status/hash misattributed across same-asset withdrawals in a single transaction due to assetId-only matching - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`findMatchingWithdrawal` (used by both `PoaBridge.describeWithdrawal` and the standalone `waitForWithdrawalCompletion` helper) selects a withdrawal record from the POA bridge API response by matching `assetId` only, via `Array.prototype.find`. When a single NEAR intent transaction contains more than one withdrawal of the same asset (e.g., two separate token withdrawals to two different destination addresses batched in one intent), every `describeWithdrawal` call for that asset — regardless of the caller-supplied `index` — resolves to the same first-matching API record. [1](#0-0) [2](#0-1) 

### Finding Description
`describeWithdrawal` fetches the full withdrawal list for a NEAR tx hash and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which returns the *first* array element whose `near_token_id` maps to `assetId`: [3](#0-2) 

`args.index` (the per-bridge sequence number assigned in `createWithdrawalIdentifiers`/`findBridgeForWithdrawal`) is never used to disambiguate between multiple withdrawals of the same asset: [4](#0-3) 

This breaks the equality that should hold between "status/hash reported for withdrawal at index N" and "the actual on-chain outcome of withdrawal N". If a user (or integrator building a batched withdrawal) submits two withdrawals of the same token in one intent — e.g., to two different destination addresses — both `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` will report the *same* `transfer_tx_hash` and completion status, even though only one of the two transfers may have actually completed, or they landed with different transaction hashes/destinations.

### Impact Explanation
This falls under the "status or hash misreport making an integrator credit or refund twice" category. An integrator polling per-withdrawal status (via `watchWithdrawal`/`waitForWithdrawalCompletion`) for two same-asset withdrawals in one intent could:
- Mark both withdrawals as "completed" with the identical destination `txHash`, even though they are logically distinct transfers to distinct destinations — leading to double-crediting downstream bookkeeping keyed by (withdrawal, txHash), or
- Report the wrong destination transaction hash for one of the two withdrawals, causing reconciliation against the wrong on-chain transfer.

The code's own comment acknowledges the limitation but frames it only as "not supported" without preventing the SDK from returning a confidently-wrong `completed` status per index — it silently returns identical results for both instead of erroring or refusing to resolve status for the ambiguous group.

### Likelihood Explanation
Reachability requires only that a caller batch two withdrawals of the same POA-bridged asset within a single intent/transaction — a legitimate use case explicitly supported by the SDK's batch withdrawal API (`withdrawalParams: WithdrawalParams[]`), not an adversarial action. No malicious relayer, bridge operator, or admin behavior is required.

### Recommendation
Disambiguate `findMatchingWithdrawal` using more than `assetId`: sort/match candidates by `(near_token_id, amount, index)` as the comment itself suggests, or track already-consumed matches per `tx.hash` so subsequent same-asset lookups don't return an already-attributed record. At minimum, throw/return `pending` (rather than a confident `completed`) when multiple candidates match the same `assetId` and cannot be deterministically disambiguated.

### Proof of Concept
1. Build an intent with two withdrawal params for the same POA asset (`nep141:btc.omft.near`) with different `destinationAddress`es; `createWithdrawalIdentifiers` assigns `index: 0` and `index: 1` for the `PoaBridge` route.
2. Submit and get the NEAR intent tx hash.
3. POA bridge processes both withdrawals; API returns two `withdrawals[]` entries with `near_token_id: "btc.omft.near"` but different `transfer_tx_hash`/`address`.
4. Call `bridge.describeWithdrawal({ index: 0, ... })` and `bridge.describeWithdrawal({ index: 1, ... })` — both invoke `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which returns `withdrawals[0]` in both cases (confirmed by the existing test "matches withdrawal by assetId, not by index" at `poa-bridge.test.ts:1054-1111`, which documents this exact same-record-returned-for-different-index behavior, only with differing asset there — with same asset it collapses to the identical record for both indices). [5](#0-4)

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
