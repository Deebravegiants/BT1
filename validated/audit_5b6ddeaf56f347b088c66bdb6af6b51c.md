### Title
Status/hash misattribution when batching multiple withdrawals of the same asset - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` resolves the on-chain status of a specific withdrawal by matching entries returned from the POA Bridge status API purely by `assetId`, ignoring the withdrawal's `index`, `amount`, or `destinationAddress`. When a caller batches two or more withdrawals of the same asset within one signed intent/transaction (a supported flow via `IntentsSDK.signAndSendWithdrawalIntent` batch mode and `createWithdrawalIdentifier`), each `describeWithdrawal` call for a distinct withdrawal index can resolve to the wrong entry in the unsorted API response, so the caller can receive a `status`/`txHash` for a withdrawal that does not correspond to the one it actually asked about.

### Finding Description
`createWithdrawalIdentifier` builds a `WithdrawalIdentifier` that carries an `index` (the withdrawal's position within a batch) alongside `withdrawalParams` and the originating NEAR `tx`: [1](#0-0) 

`describeWithdrawal` then calls `findMatchingWithdrawal`, passing only `args.withdrawalParams.assetId`, deliberately discarding `index`: [2](#0-1) 

`findMatchingWithdrawal` itself is documented as matching *only* by `near_token_id`/`assetId`, explicitly acknowledging that "multiple withdrawals of the same token in a single transaction are not supported": [3](#0-2) 

The same pattern (matching by `assetId` alone, ignoring any per-withdrawal disambiguator) exists in the sibling helper used elsewhere in `internal-utils`: [4](#0-3) 

Because `Array.prototype.find` returns the *first* array element satisfying the predicate, and the POA API response is unsorted (`response list is unsorted, so we match by assetId instead of index` — the code's own comment at line 318), calling `describeWithdrawal` for withdrawal index `0` and withdrawal index `1` of the same asset in the same NEAR transaction will both resolve to the same single entry: whichever completed withdrawal of that asset happens to appear first in the API's array. Consequently:
- The status (`completed`/`pending`/`failed`) and destination `txHash` returned for index `1` can actually be the outcome of the withdrawal for index `0` (or vice versa), an equality break between "status/hash reported" and "the actual on-chain outcome for that specific withdrawal."
- This is reachable through the SDK's normal batch withdrawal API (`IntentsSDK.signAndSendWithdrawalIntent` in batch mode, which creates one `ft_withdraw` intent per array entry, followed by per-withdrawal `describeWithdrawal`/`waitForWithdrawalCompletion` polling), i.e., no malicious relayer, RPC, or bridge operator action is required — only two legitimate withdrawals of the same asset issued together by the SDK's own consumer.

### Impact Explanation
This falls under the High-impact category "a status or hash misreport making an integrator credit or refund twice." An integrator that batches two withdrawals of the same token (e.g., to different destination addresses, or the same address with different amounts) and polls per-withdrawal completion via `describeWithdrawal`/`waitForWithdrawalCompletion` can be told that withdrawal #2 is "completed" with a `txHash` that actually belongs to withdrawal #1, while withdrawal #1's real status is misreported to a different caller/observer. Downstream systems that gate crediting, releasing held funds, or marking an off-chain ledger entry as settled based on this status/hash can act on the wrong on-chain event — e.g., crediting a user twice against a single real destination transfer, or believing a withdrawal has landed for an address that never received it.

### Likelihood Explanation
Likelihood is moderate: it requires the caller to submit ≥2 withdrawals of the *same* underlying asset within a single batched intent/transaction — a normal, supported usage pattern for this SDK (batch withdrawal mode exists explicitly), not an adversarial or privileged action. The bug is deterministic once that precondition is met and does not depend on race conditions, external actors behaving maliciously, or RPC unreliability.

### Recommendation
Disambiguate `findMatchingWithdrawal` beyond `assetId`: use additional fields returned by the POA status API (e.g., destination `address`, `amount`, and stable ordering/index) to bind each `WithdrawalIdentifier.index` to the correct API record, or explicitly reject/guard batches containing multiple withdrawals of the same asset until the POA API supports disambiguation, rather than silently returning a plausible-but-wrong match. At minimum, `describeWithdrawal` should validate that the matched record's `amount`/`address` are consistent with `args.withdrawalParams` before trusting its `status`/`txHash`, and throw/return `pending` instead of a misattributed `completed` result when ambiguity is detected.

### Proof of Concept
1. Caller uses `IntentsSDK.signAndSendWithdrawalIntent` in batch mode with two `withdrawalParams` entries for the same `assetId` (e.g., `nep141:btc.omft.near`) but different `destinationAddress`/`amount`, producing two `ft_withdraw` intents in a single NEAR transaction.
2. For each entry, the SDK (or the integrator) calls `bridge.createWithdrawalIdentifier({ withdrawalParams, index, tx })`, producing `WithdrawalIdentifier`s with `index: 0` and `index: 1` respectively, sharing the same `tx.hash`. [1](#0-0) 
3. Both withdrawals complete on the POA bridge; the status API returns both as `COMPLETED` with distinct `transfer_tx_hash` values, in array order that does not correspond to `index`.
4. Calling `bridge.describeWithdrawal(identifier_index0)` and `bridge.describeWithdrawal(identifier_index1)` both invoke `findMatchingWithdrawal(withdrawals, assetId)`, which returns the same first-matching array element for both calls (as confirmed by the existing test `"matches withdrawal by assetId, not by index"`, which demonstrates the match ignoring index): [5](#0-4) 
5. Result: the second withdrawal's `describeWithdrawal` result reports the `txHash` and completion status of the first withdrawal (or vice versa depending on array order), an unauthorized equality break between the reported outcome and the actual on-chain outcome for that specific withdrawal identifier.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L295-311)
```typescript
	createWithdrawalIdentifier(args: {
		withdrawalParams: WithdrawalParams;
		index: number;
		tx: NearTxInfo;
	}): WithdrawalIdentifier {
		const assetInfo = this.parseAssetId(args.withdrawalParams.assetId);
		assert(assetInfo != null, "Asset is not supported");

		const landingChain = assetInfo.blockchain;

		return {
			landingChain,
			index: args.index,
			withdrawalParams: args.withdrawalParams,
			tx: args.tx,
		};
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
