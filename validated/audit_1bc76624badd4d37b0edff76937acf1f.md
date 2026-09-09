### Title
POA bridge misattributes withdrawal status/txHash across same-token batch withdrawals - ([File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts])

### Summary
`PoaBridge.describeWithdrawal` resolves the status of a specific withdrawal (identified by `index`) by matching bridge-reported withdrawals only on `assetId`, not on the withdrawal's index/position/destination. When a batch of withdrawals contains two or more entries for the same token, every index resolves to whichever matching record `findMatchingWithdrawal` returns first, breaking the equality "status reported for withdrawal *i* corresponds to the on-chain outcome of withdrawal *i*."

### Finding Description
`describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does: [1](#0-0) 

This function ignores `index` entirely and returns the first bridge-side record whose `near_token_id` matches the requested `assetId`. The comment on the function explicitly documents that "multiple withdrawals of the same token in a single transaction are not supported," but there is no guard anywhere in the SDK (`sdk.ts`, `createWithdrawalCompletionPromises`, `waitForWithdrawalCompletion`, or `validateWithdrawal`) that rejects or deduplicates batches containing two withdrawals of the same `assetId`. `describeWithdrawal` is invoked per-index via `watchWithdrawal`/`createWithdrawalCompletionPromises`: [2](#0-1) 

So if a caller submits a batch with two same-token withdrawals to two different destination addresses (e.g., withdrawal index 0 to address A, index 1 to address B), and only the first one has actually settled on-chain, both `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` will return the exact same `{status:"completed", txHash: <A's tx>}` result — because `.find()` matches on `assetId` alone and returns the same record for both calls.

### Impact Explanation
An integrator using `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` for a batch would receive a "completed" status and a real destination tx hash for a withdrawal (index 1 → address B) that has not actually executed. If the integrator's off-chain accounting credits/marks the withdrawal as delivered based on this status+hash (a common downstream pattern, matching the "AWS SDK describe pattern" documented in `shared-types.ts`), this constitutes a status/hash misreport that can cause an integrator to prematurely credit or double-credit a withdrawal that has not settled — matching the "High" impact class (status misreport causing credit/refund twice).

### Likelihood Explanation
This requires only a normal SDK caller behavior — submitting a batch withdrawal intent with two entries sharing the same `assetId` (e.g., same token withdrawn to two different addresses in one intent) — no malicious peer, relayer, or bridge cooperation is needed. No validation in the withdrawal creation or completion-polling path prevents or warns against this batch shape, so this is reachable through ordinary integrator usage, not a contrived edge case. Likelihood is moderate: it only manifests for POA-bridge-routed batches with duplicate assetIds, a case the code authors already acknowledged is unhandled.

### Recommendation
- Reject (throw) at withdrawal-creation/validation time (`PoaBridge.validateWithdrawal` or the batch-building path in `sdk.ts`) when a batch contains more than one withdrawal with the same `assetId` routed through POA bridge, until proper per-index matching is implemented.
- Alternatively, implement the ordering-based matching the code comment suggests (sort both the API response and the local `withdrawalParams` by amount for withdrawals sharing an `assetId`) so that `index` correctly binds to a specific bridge-side record instead of the first assetId match.

### Proof of Concept
1. Build a batch withdrawal intent with `withdrawalParams = [{assetId: "nep141:usdc.omft.near", amount: 100, destinationAddress: A}, {assetId: "nep141:usdc.omft.near", amount: 200, destinationAddress: B}]` and submit via `sdk.signAndSendIntent`/execute withdrawal flow.
2. Suppose only the withdrawal to `A` has settled on the POA bridge side (`getWithdrawalStatus` returns one `COMPLETED` record with `near_token_id: "usdc.omft.near"`, `transfer_tx_hash: "txA"`); the withdrawal to `B` is still pending and absent/pending in the bridge response.
3. Call `bridge.describeWithdrawal({..., index: 0, withdrawalParams: paramsA})` and `bridge.describeWithdrawal({..., index: 1, withdrawalParams: paramsB})`.
4. Because `findMatchingWithdrawal` matches only on `assetId`, both calls hit the same record and both return `{status: "completed", txHash: "txA"}`, even though `B`'s withdrawal has not executed on-chain — demonstrated directly by the matching logic at `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts:418-427` and consumed by `watchWithdrawal` per index at `packages/intents-sdk/src/core/withdrawal-watcher.ts:36-53`.

### Citations

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
