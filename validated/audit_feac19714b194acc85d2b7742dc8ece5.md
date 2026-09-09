### Title
POA Bridge Withdrawal Status Matched Only by `assetId`, Not Withdrawal Identity — Cross-Withdrawal Status/Hash Misreport in Batches - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` resolves the completion status/hash of a specific withdrawal by matching the POA Bridge API response solely on `assetId`, ignoring the withdrawal's index, destination address, and amount. When a single NEAR intent settlement contains multiple withdrawals of the *same* asset (a very common batch pattern — e.g., paying two different recipients the same token in one intent), this matching can attach the wrong record's `transfer_tx_hash`/status to a given `WithdrawalIdentifier`, causing a status/hash misreport for at least one of the withdrawals in the batch.

### Finding Description
`describeWithdrawal` is documented as a "One-shot status check for a withdrawal" that returns the status for a specific `WithdrawalIdentifier` [1](#0-0) . In `PoaBridge`, the implementation explicitly abandons index-based matching in favor of `assetId`-based matching because "Response list is unsorted":

```
async describeWithdrawal(...) {
    const response = await this.getWithdrawalStatusWithRetry(args);
    // Response list is unsorted, so we match by assetId instead of index
    const withdrawal = findMatchingWithdrawal(
        response.withdrawals,
        args.withdrawalParams.assetId,
    );
    ...
    if (withdrawal.status === "COMPLETED") {
        return { status: "completed", txHash: withdrawal.data.transfer_tx_hash };
    }
    ...
}
``` [2](#0-1) 

The same single-field criteria pattern (`WithdrawalCriteria = { assetId: string }`) is used at the lower-level `waitForWithdrawalCompletion` helper in `internal-utils`, confirming that matching is intentionally scoped to `assetId` alone rather than to a unique withdrawal identity (amount, destination address, or index): [3](#0-2) 

`createWithdrawalIdentifiers()` / `watchWithdrawal()` in `withdrawal-watcher.ts` call `bridge.describeWithdrawal(args.wid)` per withdrawal in a batch, trusting that the returned status/hash corresponds to *that* specific `wid` [4](#0-3) . Multiple withdrawals with distinct `destinationAddress`/`amount` but identical `assetId` can legitimately exist in the same batch (e.g., `createWithdrawalIdentifiers` explicitly supports several withdrawals routed to the same bridge, tracked only by a per-route counter) [5](#0-4) . Since the POA API's response ordering is not guaranteed (per the code comment) and the match key is only `assetId`, when two same-asset withdrawals are outstanding, `findMatchingWithdrawal` can return either record for either identifier — reporting withdrawal A's `transfer_tx_hash`/`COMPLETED` status against withdrawal B's identifier (and vice versa), or reporting one as `completed` while it is actually withdrawal A that completed and B is still pending.

This breaks the equality the report's bug class targets: **a status reported that is not the on-chain outcome for the specific withdrawal being queried.**

### Impact Explanation
An integrator relying on `describeWithdrawal`/`watchWithdrawal`/`waitForWithdrawalCompletion` per-withdrawal result to decide when a specific destination has been paid could:
- Mark the wrong withdrawal (wrong destination address) as `completed` with a `transfer_tx_hash` that actually belongs to a different recipient's transfer, causing the integrator to release/credit downstream funds or mark an off-chain order as fulfilled for the wrong leg.
- Conversely, treat a genuinely completed withdrawal as still pending indefinitely (stuck-until-manual-intervention) if the mismatched record is picked up first.

This matches the "High" impact category: a status/hash misreport making an integrator credit or refund incorrectly.

### Likelihood Explanation
No privileged access or malicious relayer is required — batching multiple withdrawals of the same asset (e.g., same token, different destination addresses/amounts) in a single `sdk.processWithdrawal`/`signAndSendWithdrawalIntent` call is a normal, documented usage pattern of this SDK (batch withdrawals). Any consumer performing batch withdrawals of the same token via the POA route is exposed whenever the bridge's response ordering doesn't align 1:1 with the requested order (the code itself acknowledges "Response list is unsorted").

### Recommendation
Match withdrawal identifiers using a composite key that uniquely identifies the requested withdrawal — e.g., `assetId` + `destinationAddress` + `amount` (and/or the underlying `account_id`/order index provided by the POA API), instead of `assetId` alone, in both `findMatchingWithdrawal` implementations (`packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`). If the POA API cannot disambiguate multiple same-asset withdrawals from one NEAR tx, that must be treated as an unresolvable/pending status rather than silently attaching a possibly-wrong record.

### Proof of Concept
1. Caller submits `sdk.processWithdrawal` with two withdrawal params in the same intent: same `assetId` (`nep141:usdc.token.near`), different `destinationAddress` (`A` and `B`) and different `amount`.
2. `createWithdrawalIdentifiers` creates two `WithdrawalIdentifier`s for the same POA bridge route, indices 0 and 1, both sharing `assetId` [5](#0-4) .
3. `watchWithdrawal` calls `describeWithdrawal` separately for each identifier; both calls hit `getWithdrawalStatusWithRetry` and then `findMatchingWithdrawal(response.withdrawals, "nep141:usdc.token.near")`, which returns the *first* record in the (unsorted) list matching only the asset, regardless of which of the two records actually corresponds to identifier 0 vs identifier 1 [2](#0-1) .
4. If withdrawal to `B` completes first but withdrawal to `A` is still pending, both `describeWithdrawal({wid: A})` and `describeWithdrawal({wid: B})` can resolve to the same matched record (`B`'s completed status/hash), so the caller believes withdrawal `A` also completed with `B`'s `transfer_tx_hash`.

### Citations

**File:** packages/intents-sdk/src/shared-types.ts (L425-431)
```typescript
	/**
	 * One-shot status check for a withdrawal.
	 * Returns the current status without polling.
	 */
	describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus>;
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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L31-33)
```typescript
export type WithdrawalCriteria = {
	assetId: string;
};
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-47)
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
