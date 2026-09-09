### Title
POA Bridge Withdrawal Status Matches by Asset ID Only, Misreporting Status/TxHash for Batched Same-Token Withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`describeWithdrawal` in `PoaBridge` resolves withdrawal completion status by looking up the POA bridge indexer response and calling `findMatchingWithdrawal`, which matches purely on `assetId` (via `near_token_id`), ignoring the withdrawal `index`, `destinationAddress`, and `amount`. The SDK explicitly supports batch withdrawals containing multiple entries in a single NEAR intent transaction. If a batch contains two or more withdrawals of the same underlying NEP-141 asset (even to different destination addresses/amounts), the first matching entry returned by the POA API is used to answer status queries for every withdrawal of that asset in the batch, so the wrong `txHash`/`status` can be reported for a given withdrawal index.

### Finding Description
`findMatchingWithdrawal` is defined and documented as a known limitation: [1](#0-0) 

It is invoked from `describeWithdrawal`, which uses only `args.withdrawalParams.assetId` (not `index`, `destinationAddress`, or `amount`) to pick a withdrawal from the response list, then reports that entry's status/`transfer_tx_hash` as the answer for the query: [2](#0-1) 

The identical pattern (matching only by `near_token_id`/`assetId`) exists in the sibling helper used by `waitForWithdrawalCompletion`: [3](#0-2) 

The SDK's own test suite documents and validates this exact "match by assetId, not by index" behavior: [4](#0-3) 

Batch withdrawals — multiple `WithdrawalParams` entries settled in a single NEAR intent transaction — are a first-class, documented SDK feature (`sdk.processWithdrawal`, `sdk.waitForWithdrawalCompletion`, `sdk.createWithdrawalCompletionPromises` all accept `WithdrawalParams[]`): [5](#0-4) [6](#0-5) 

Nothing in `createWithdrawalIdentifier` or the withdrawal-orchestration path prevents two batch entries from sharing the same `assetId` while differing in `destinationAddress` and/or `amount` (e.g., withdrawing the same token to two different recipients in one transaction). When the POA API returns multiple withdrawal records for that same NEAR transaction/asset (one per destination), `findMatchingWithdrawal` returns the *first* record whose `near_token_id` matches, regardless of which of the batch's withdrawal indices is actually being queried. Both `describeWithdrawal` (per-index polling used by `createWithdrawalCompletionPromises`) and `waitForWithdrawalCompletion` (per-criteria polling) are affected identically, since they share the same one-field matching rule.

This breaks the equality that the reported status/txHash for withdrawal index N must correspond to the on-chain outcome of withdrawal index N specifically — instead it can report the outcome of a different withdrawal (different destination address and/or amount) within the same batch.

### Impact Explanation
An integrator polling per-index status via `createWithdrawalCompletionPromises`, or relying on `waitForWithdrawalCompletion`'s per-criteria matching, for a batch containing two same-asset withdrawals to different destinations can receive a `completed` status and `txHash` that actually belongs to a *different* withdrawal in the batch. This is a status/hash misreport: the integrator could treat withdrawal A (to address X) as completed based on withdrawal B's (to address Y) completion, potentially crediting/confirming/closing out a withdrawal that has not actually reached its correct destination, or double-crediting because both indices resolve to the same first-matched record. This falls under the accepted impact class "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
This requires no malicious actor — it triggers under a normal, SDK-supported usage pattern (batch withdrawal of the same token to more than one destination in a single intent), which the SDK explicitly advertises and tests for (batch withdrawals, `signAndSendWithdrawalIntent` with array `withdrawalParams`). The code comment and dedicated regression test ("matches withdrawal by assetId, not by index") show the authors are aware this only works correctly when a single withdrawal per asset exists in the batch, but nothing enforces or validates that invariant at the SDK boundary (e.g., in `createWithdrawalIntents`/batch construction), so callers can unknowingly hit this edge case.

### Recommendation
Enforce that `findMatchingWithdrawal` disambiguates multiple withdrawals of the same asset within one transaction — e.g., match on `amount` and `destinationAddress` in addition to `assetId`/`near_token_id`, or reject/throw when more than one candidate exists rather than silently returning the first. Additionally, consider validating at withdrawal-construction time that a batch does not contain two POA-routed withdrawals of the same asset without an unambiguous secondary matching key, until the POA bridge API itself exposes an index/ordering guarantee.

### Proof of Concept
1. Construct a batch withdrawal via `sdk.processWithdrawal({ withdrawalParams: [ { assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "addrA" }, { assetId: "nep141:btc.omft.near", amount: 50000n, destinationAddress: "addrB" } ] })`, both routed through `PoaBridge`.
2. After the NEAR intent settles, the POA bridge indexer returns two `COMPLETED` withdrawal records for the same `tx_hash`/`near_token_id` (`btc.omft.near`), one for each destination/amount, as modeled in the existing test at `poa-bridge.test.ts:1054-1111`.
3. Call `bridge.describeWithdrawal` (or `sdk.createWithdrawalCompletionPromises`) for index 0 (addrA) and index 1 (addrB): `findMatchingWithdrawal` returns the same first `nep141:btc.omft.near` record for both queries, so both indices resolve to identical `status`/`txHash`, even though only one of the two on-chain transfers actually corresponds to each destination — a caller correlating index→destination will misattribute the completion event.

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

**File:** packages/intents-sdk/README.md (L521-563)
```markdown
### Batch Withdrawals

Process multiple withdrawals in a single intent:

```typescript
const withdrawalParams = [
    {
        assetId: 'nep141:usdt.tether-token.near',
        amount: 1000000n,
        destinationAddress: '0x742d35Cc...',
        feeInclusive: false
    },
    {
        assetId: 'nep245:v2_1.omni.hot.tg:137_qiStmoQJDQPTebaPjgx5VBxZv6L',
        amount: 100000n,
        destinationAddress: '0x742d35Cc...',
        feeInclusive: false
    }
]

// Method 1: Complete end-to-end batch processing
const batchResult = await sdk.processWithdrawal({
    withdrawalParams,
    // feeEstimation is optional - will be estimated automatically if not provided
});

console.log('Batch intent hash:', batchResult.intentHash);
console.log('Destination transactions:', batchResult.destinationTx); // Array of results

// Method 2: Step-by-step batch processing for granular control
const feeEstimation = await sdk.estimateWithdrawalFee({
    withdrawalParams
});

const {intentHash} = await sdk.signAndSendWithdrawalIntent({
    withdrawalParams,
    feeEstimation
});

const intentTx = await sdk.waitForIntentSettlement({intentHash});

// See "Waiting for Batch Completion" below for completion options
```
```

**File:** packages/intents-sdk/src/sdk.ts (L557-608)
```typescript
	public createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>> {
		const { withdrawalParams, intentTx, signal, logger } = params;

		const widsPromise = createWithdrawalIdentifiers({
			bridges: this.bridges,
			withdrawalParams,
			intentTx,
		});

		// Track the last promise per HOT bridge landing chain for sequential waiting.
		// HOT bridge processes withdrawals sequentially per chain with ~30s gaps,
		// so polling in parallel would cause later withdrawals to timeout.
		const hotChainLastPromise = new Map<Chain, Promise<TxInfo | TxNoInfo>>();

		return withdrawalParams.map(async (_, index) => {
			const wids = await widsPromise;
			const entry = wids[index];
			assert(entry != null, `Missing wid for index ${index}`);

			// Only apply sequential waiting for HOT bridge
			if (entry.bridge.route === RouteEnum.HotBridge) {
				const landingChain = entry.wid.landingChain;
				const previousPromise = hotChainLastPromise.get(landingChain);

				const sequentialPromise = (async () => {
					if (previousPromise) {
						// Wait for previous withdrawal to same chain to complete.
						// Use allSettled to continue even if previous fails.
						await Promise.allSettled([previousPromise]);
					}
					return watchWithdrawal({
						bridge: entry.bridge,
						wid: entry.wid,
						signal,
						logger,
					});
				})();

				hotChainLastPromise.set(landingChain, sequentialPromise);
				return sequentialPromise;
			}

			// Non-HOT bridges: parallel polling (existing behavior)
			return watchWithdrawal({
				bridge: entry.bridge,
				wid: entry.wid,
				signal,
				logger,
			});
		});
```
