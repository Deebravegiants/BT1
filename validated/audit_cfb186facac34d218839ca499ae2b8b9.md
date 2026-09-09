### Title
Omni Bridge misreports withdrawal completion by trusting positional index instead of validating recipient/asset - (File: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts)

### Summary
`OmniBridge.describeWithdrawal()` selects the withdrawal transfer solely by array index (`getTransfer(...)[args.index]`) and never validates that the returned transfer's recipient/asset actually corresponds to the specific `withdrawalParams` being polled. This is the same bug class that was already identified and fixed in the sibling `PoaBridge` implementation ("Fix POA bridge withdrawal matching to use assetId instead of index" — CHANGELOG `8bbd5c6`), but the fix was never applied to `OmniBridge`.

### Finding Description
In a batch withdrawal, `signAndSendWithdrawalIntent` creates N intents from N `withdrawalParams` in a single NEAR transaction [1](#0-0) . Later, `watchWithdrawal`/`createWithdrawalCompletionPromises` calls `bridge.describeWithdrawal({..., index})` per withdrawal to determine its individual completion status [2](#0-1) .

For `OmniBridge`, the implementation is:
```
const transfer = (await this.omniBridgeAPI.getTransfer({ transactionHash: args.tx.hash }))[args.index];
``` [3](#0-2) 

It then derives `destinationChain` and `txHash` purely from that indexed `transfer` object and returns `{status: "completed", txHash}` without ever comparing `transfer.recipient` or the underlying asset against `args.withdrawalParams.destinationAddress` / `args.withdrawalParams.assetId` [4](#0-3) .

The `PoaBridge` implementation of the identical pattern was already patched to avoid exactly this: it explicitly comments "Response list is unsorted, so we match by assetId instead of index" and performs a `findMatchingWithdrawal` lookup keyed by `assetId` rather than trusting the array position [5](#0-4) . `OmniBridge` has no equivalent matching/validation logic, so if the Omni Bridge indexer API returns transfers for a multi-withdrawal transaction in an order that does not exactly match the on-chain intent creation order (the exact issue that was fixed for POA), `describeWithdrawal` for withdrawal index `i` will return the destination chain and `txHash` belonging to a *different* withdrawal in the batch.

### Impact Explanation
This breaks the equality "a status reported that is not the on-chain outcome" / "an address or chain paid that was not the one validated": the SDK would report withdrawal `i` as `completed` with a `txHash` and destination chain that actually correspond to a sibling withdrawal's transfer. An integrator relying on `createWithdrawalCompletionPromises`/`waitForWithdrawalCompletion` per-index results (as documented in the README's "Index correspondence: `promises[i]` corresponds to `withdrawalParams[i]`" contract [6](#0-5) ) could credit/mark withdrawal `i` as settled using a transaction hash that never paid the destination address configured for withdrawal `i`, or mark two withdrawals both "completed" pointing at the same tx while the other transfer never gets a resolved status, causing a double-credit or a permanently un-settled withdrawal.

### Likelihood Explanation
This is only reachable in batch withdrawals through OmniBridge routes where the `omniBridgeAPI.getTransfer` response ordering does not exactly mirror the order withdrawals were created on-chain — the precise failure mode already observed and fixed for the POA bridge's API. I could not directly verify from the indexed code whether `omniBridgeAPI.getTransfer` (external `@omni-bridge/core` package) guarantees ordering; this is the main uncertainty. Given a sibling bridge sharing the same architectural pattern needed this exact fix, the likelihood that OmniBridge's API has the same non-deterministic ordering is material, but not proven with 100% certainty from the code available in this index.

### Recommendation
In `OmniBridge.describeWithdrawal()`, do not select `transfer` by raw index. Instead, match the transfer to `args.withdrawalParams` using a stable identifying property in the transfer response (e.g., matching `withdrawalParams.assetId`/expected recipient/destination address, mirroring `findMatchingWithdrawal` in `PoaBridge`), and only report `completed` when the located transfer's recipient/asset matches the requested withdrawal.

### Proof of Concept
Not exploitable via a simple standalone script since it depends on the ordering behavior of the external Omni Bridge indexer API (`@omni-bridge/core`'s `BridgeAPI.getTransfer`), which is out of this repo's scope to fully verify. Conceptually: submit a batched `signAndSendWithdrawalIntent` with two withdrawals of different assets/destinations in the same NEAR tx; if `getTransfer(txHash)` returns the two transfers in an order that doesn't match `args.index` (e.g., sorted differently by the indexer), `describeWithdrawal({index: 0})` will return transfer[0], which may actually be the second withdrawal's transfer, yielding a `txHash`/chain that doesn't belong to withdrawal 0.

### Citations

**File:** packages/intents-sdk/src/sdk.ts (L704-715)
```typescript
		const intentsP = zip(withdrawalParamsArray, feeEstimations).map(
			([withdrawalParams, feeEstimation]) => {
				return this.createWithdrawalIntents({
					withdrawalParams,
					feeEstimation,
					referral: args.referral ?? this.referral,
					logger: args.logger,
				});
			},
		);

		const intents = (await Promise.all(intentsP)).flat();
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

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L691-702)
```typescript
	async describeWithdrawal(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatus> {
		const transfer = (
			await this.omniBridgeAPI.getTransfer({
				transactionHash: args.tx.hash,
			})
		)[args.index];

		if (transfer == null || transfer.recipient == null) {
			return { status: "pending" };
		}
```

**File:** packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts (L704-731)
```typescript
		const destinationChain = getChain(transfer.recipient as OmniAddress);
		let txHash = null;
		if (
			isEvmChain(destinationChain) ||
			destinationChain === ChainKind.Sol ||
			destinationChain === ChainKind.Fogo ||
			destinationChain === ChainKind.Strk ||
			destinationChain === ChainKind.Aptos
		) {
			txHash = transfer.finalised?.transaction_hash;
		} else if (isUtxoChain(destinationChain)) {
			// pending_sign_id is not the finalised tx hash. In rare cases, the hash may
			// change if the BTC transfer fails to be submitted. We return fast hash for FE and
			// wait for final one (transfer.finalised?.transaction_hash) for BE.
			txHash =
				typeof window !== "undefined"
					? transfer.utxo_meta?.pending_sign_id
					: transfer.finalised?.transaction_hash;
		} else {
			return { status: "completed", txHash: null };
		}

		if (!txHash) {
			return { status: "pending" };
		}

		return { status: "completed", txHash };
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

**File:** packages/intents-sdk/README.md (L638-640)
```markdown
- Recovery-friendly: recreate promises from saved `{ withdrawalParams, intentTx }`
- Index correspondence: `promises[i]` corresponds to `withdrawalParams[i]`

```
