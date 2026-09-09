### Title
Withdrawal status matched only by `assetId` causes destination/status misreport for batch withdrawals of the same token - (File: `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`)

### Summary
`findMatchingWithdrawal` resolves the on-chain withdrawal record for a given logical withdrawal index by matching **only** on `assetId`, not on destination address, amount, or any per-item identifier. When a batch intent contains two or more withdrawals of the same token (e.g. two USDT withdrawals to different destination addresses in one intent, a scenario explicitly supported by `sdk.processWithdrawal`/`signAndSendWithdrawalIntent` batch APIs), every index querying the POA bridge for that token converges on the same (first) matching record.

### Finding Description
`waitForWithdrawalCompletion` in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` (lines 35-125) is called once per withdrawal index (via `poa-bridge.ts`, which is invoked from `createWithdrawalCompletionPromises` in `packages/intents-sdk/src/sdk.ts`, lines 557-609) to independently resolve the destination-chain outcome for each withdrawal in a batch. The lookup key is `WithdrawalCriteria = { assetId: string }` (line 31-33), and `findMatchingWithdrawal` (lines 144-153) does:

```ts
return withdrawals.find(
    (w) => `nep141:${w.data.near_token_id}` === criteria.assetId,
);
```

This is an `Array.prototype.find`, which always returns the **first** entry whose `near_token_id` matches the requested `assetId`. The code comment even documents the equality being broken:

"NOTE: Currently only matches by assetId (near_token_id). This means multiple withdrawals of the same token in a single transaction are not supported."

The SDK's batch withdrawal flow does not prevent multiple same-asset withdrawals from being submitted in a single intent (`sdk.signAndSendWithdrawalIntent`, `sdk.processWithdrawal`, `sdk.createWithdrawalCompletionPromises` all accept `WithdrawalParams[]` without asset-uniqueness validation). Each per-index promise created in `createWithdrawalCompletionPromises` (`packages/intents-sdk/src/sdk.ts` lines 573-608) independently calls into the bridge/`waitForWithdrawalCompletion`, and for POA-bridge routed withdrawals, all indices sharing the same `assetId` resolve to the identical bridge-side record — regardless of which index's destination address/amount that record actually corresponds to.

The equality broken: *the status/txHash reported for withdrawal index i must be the on-chain outcome of withdrawal i, not of some other withdrawal in the same batch.* Here, a status is reported that is not necessarily the on-chain outcome for that specific index.

### Impact Explanation
If a caller submits two same-asset withdrawals to different destination addresses (or amounts) in one intent, both `createWithdrawalCompletionPromises` entries resolve to the same underlying withdrawal record's `transfer_tx_hash`/`chain`. An integrator relying on `sdk.waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` results to decide when to credit a user or mark a specific destination as paid could:
- Report the same destination tx hash for two logically distinct withdrawals (double credit / incorrect confirmation for the withdrawal that wasn't actually the one matched).
- Mark a still-pending withdrawal to a different destination address as "completed" using another withdrawal's completion data.

This matches the "status or hash misreport making an integrator credit or refund twice" category (High).

### Likelihood Explanation
This requires no malicious actor — any legitimate user/integrator submitting a batch withdrawal with two entries of the same `assetId` (e.g., splitting one token to two recipients) triggers it deterministically, since `Array.find` always returns the first match for both lookups. The condition is purely structural (same-asset batch withdrawal), which is a normal, documented-as-unsupported-but-not-blocked use case of the public batch withdrawal API.

### Recommendation
Extend `WithdrawalCriteria` to include a discriminating field beyond `assetId` — at minimum destination address, and ideally amount or a per-item sequence identifier returned by the POA bridge — and update `findMatchingWithdrawal` to match on the full criteria tuple, consuming matched entries so repeat lookups for the same asset don't reuse an already-assigned record. Until the POA API supports this, the SDK should explicitly reject/validate batch withdrawals containing duplicate `assetId` entries destined for the POA bridge route (fail fast) rather than silently reporting cross-matched results.

### Proof of Concept
1. Call `sdk.processWithdrawal` (or `signAndSendWithdrawalIntent` + `createWithdrawalCompletionPromises`) with `withdrawalParams = [{ assetId: "nep141:usdt.near", destinationAddress: "alice.near", amount: 100n, ... }, { assetId: "nep141:usdt.near", destinationAddress: "bob.near", amount: 200n, ... }]` routed to the POA bridge.
2. The NEAR intent settles, creating two on-chain POA withdrawal records for `usdt.near`, one for `alice.near`/100 and one for `bob.near`/200.
3. `createWithdrawalCompletionPromises` issues two independent `waitForWithdrawalCompletion` calls, both with `withdrawalCriteria = { assetId: "nep141:usdt.near" }`.
4. `findMatchingWithdrawal` (`packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts:144-153`) returns the **same first entry** in `result.withdrawals` for both calls, so index 1 (bob.near) is reported with the destination tx hash/chain that actually belongs to index 0's (alice.near) transfer, or vice versa depending on array order — an integrator consuming `promises[1]` believes bob's withdrawal completed using alice's transfer hash. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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
