## Analog Assessment: Status/Withdrawal Misreport Due to Non-Unique Matching Key — `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`

### Mapping the bug class

The external report's core pattern is "a security-relevant equality check that should bind an action to a specific, caller-verified identity/context is missing, so an action executes/reports against the wrong bound target." Translated to this repo's allowed impact list, the closest reachable equality that can be broken here is: **a status reported that is not the on-chain outcome for the specific withdrawal being queried** — i.e., `describeWithdrawal()` must bind its result strictly to the `(tx.hash, index)` pair it was asked about, not to a looser key that can accidentally match a different withdrawal.

### Finding

`PoaBridge.describeWithdrawal()` [1](#0-0)  retrieves all withdrawals for a given NEAR tx hash and then calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` [2](#0-1) , which matches purely by `assetId`, ignoring `args.index` entirely: [3](#0-2) . The code comment openly acknowledges: *"multiple withdrawals of the same token in a single transaction are not supported."*

`createWithdrawalIdentifiers()` in the withdrawal watcher builds one `WithdrawalIdentifier` per withdrawal in a batch and assigns a per-bridge `index` [4](#0-3) , and `watchWithdrawal()` treats whatever `describeWithdrawal()` returns as authoritative for **that specific withdrawal identifier** — reporting `completed` with a `txHash` that the caller may use to credit/settle [5](#0-4) .

If a single NEAR transaction contains two or more `ft_withdraw` intents for the **same token** to different destination addresses (a legitimate, reachable scenario via `signAndSendIntent`'s multi-intent composition or `createWithdrawalIntents` batch withdrawals, both of which are first-class supported features per the README), `findMatchingWithdrawal` will return the **same** underlying withdrawal record (`Array.find` returns the first match) for every `WithdrawalIdentifier` that shares that `assetId`, regardless of `index`. Consequently:
- Both withdrawal slots report the same `status`/`txHash`.
- If withdrawal #0 is `COMPLETED` while withdrawal #1 (same asset, different destination) is still `PENDING` on the bridge side, `describeWithdrawal({index:1,...})` can incorrectly report `completed` with withdrawal #0's `transfer_tx_hash`.

### Impact

This breaks the equality "status/hash reported == on-chain outcome for *this* withdrawal," matching the rule's High-severity bucket: *"a status or hash misreport making an integrator credit or refund twice."* An integrator relying on `waitForWithdrawalCompletion`/`processWithdrawal` per-withdrawal results for batched same-asset withdrawals could mark a still-pending withdrawal as completed (using another withdrawal's destination tx hash), leading to premature crediting/reconciliation or a mismatched settlement record. It does not, however, cause a debit or fund movement itself — the misreport is confined to the SDK's off-chain status polling layer, and exploitation requires no privileged action, only a normal batch withdrawal of the same asset to two destinations, which is an explicitly supported use case (see README "Batch Withdrawals" example using the *same* token twice in `withdrawalParams`).

### Recommendation
`findMatchingWithdrawal` should incorporate a discriminator beyond `assetId` (e.g., destination address, or a stable sequence match reflecting the same order used by the PoA relayer, or amount) so each `WithdrawalIdentifier.index` binds deterministically to a unique record. Barring that, `describeWithdrawal` should refuse to report `completed` when multiple candidate withdrawals of the same asset exist in the response and cannot be disambiguated, falling back to `pending`/erroring instead of guessing.

### Uncertainty
I could not verify how the PoA relayer backend orders/returns withdrawals in `getWithdrawalStatus` (whether it's stable/sortable by amount or creation order), so I cannot confirm this is always exploitable in practice versus only under specific relayer response ordering — the code's own comment suggests this is a known, currently-unresolved limitation rather than a newly discovered defect.

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
