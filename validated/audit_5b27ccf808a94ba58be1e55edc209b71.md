### Title
POA Bridge withdrawal status is matched only by `assetId`, causing cross-withdrawal status/hash misreport in batched withdrawals - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` looks up the on-chain outcome of a specific withdrawal by matching the POA API response list solely on `assetId`, ignoring the `index`/nonce that uniquely identifies which withdrawal in a batch the caller is polling for. When a single intent contains multiple withdrawals of the same asset (a supported use case via `WithdrawalParams[]`), a caller polling for withdrawal #1 can be handed the status/`txHash` of withdrawal #0 (or vice versa), because the matcher can't disambiguate between two pending/completed entries that share the same `assetId`.

### Finding Description
`describeWithdrawal` is:
```
async describeWithdrawal(args) {
    const response = await this.getWithdrawalStatusWithRetry(args);
    // Response list is unsorted, so we match by assetId instead of index
    const withdrawal = findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId);
    ...
}
``` [1](#0-0) 

The comment explicitly states matching is done by `assetId` "instead of index" because the API response is unsorted. But `WithdrawalIdentifier.index` exists precisely to distinguish multiple withdrawals of the same bridge/asset created from one intent transaction: [2](#0-1) 

`createWithdrawalIdentifiers` assigns a per-bridge-route running `index` when multiple `WithdrawalParams` are processed in one batch — this is the only mechanism that keeps parallel same-asset withdrawals distinguishable from each other: [3](#0-2) 
(Note the surrounding sequential-wait logic elsewhere in `sdk.ts` also assumes each `index` maps to a *specific* withdrawal, not just a specific asset.)

Because `findMatchingWithdrawal` never consults `index`, `destinationAddress`, or `amount` to disambiguate, when two (or more) withdrawals in the batch share the same `assetId` (e.g., the same token being sent to two different destination addresses, or two different amounts, in one intent), `watchWithdrawal` polling for withdrawal index 0 and for index 1 can both resolve against the same underlying POA `withdrawals[]` entry — reporting the wrong `status`/`txHash` pairing to the wrong logical withdrawal.

### Impact Explanation
This breaks the equality "status/hash reported == the on-chain outcome for *that specific* withdrawal." A caller (SDK integrator) using `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` for a batch of same-asset withdrawals can:
- Have the wrong `txHash` attributed to the wrong destination/withdrawal, misleading downstream systems on which destination actually received funds.
- Have one withdrawal reported "completed" while it is still pending or targets a different destination, leading an integrator to prematurely credit/finalize a withdrawal that hasn't actually landed for that specific recipient — i.e., a double-credit/misreport scenario matching the "status or hash misreport making an integrator credit or refund twice" impact class.

### Likelihood Explanation
Requires only that a normal (unprivileged) user submit a batch withdrawal (`WithdrawalParams[]`) containing two or more entries with the same `assetId` routed through the POA bridge — a legitimate, SDK-supported flow (batch withdrawals are a first-class feature per `sdk.estimateWithdrawalFee`/`signAndSendWithdrawalIntent` accepting arrays). No malicious relayer/bridge/admin behavior is needed; the ambiguity is purely a client-side matching defect against a normally-functioning (but unsorted) POA API response.

### Recommendation
Disambiguate `findMatchingWithdrawal` using additional fields beyond `assetId` — at minimum `destinationAddress` and `amount` (and, if the POA API exposes it, an index/sequence field per NEAR tx), so that each `WithdrawalIdentifier.index` deterministically maps to exactly one entry in `response.withdrawals`. If the POA API cannot provide a stable per-withdrawal correlation id, this should be tracked as a required API enhancement before batch same-asset withdrawals via POA are considered safe.

### Proof of Concept
1. Caller submits one intent with `withdrawalParams = [{assetId: "nep141:btc.omft.near", destinationAddress: "addrA", amount: 100000n}, {assetId: "nep141:btc.omft.near", destinationAddress: "addrB", amount: 50000n}]`.
2. `createWithdrawalIdentifiers` assigns `index: 0` to addrA's withdrawal and `index: 1` to addrB's withdrawal, both via `PoaBridge` (same `route`).
3. `watchWithdrawal` calls `describeWithdrawal` separately for each `WithdrawalIdentifier`, but both calls pass the same `assetId` ("nep141:btc.omft.near") into `findMatchingWithdrawal`.
4. If the POA API returns entries for both withdrawals (e.g., addrB completed, addrA still pending) `findMatchingWithdrawal` can return the same matched entry (e.g. addrB's completed entry with its `transfer_tx_hash`) for both `index: 0` and `index: 1` lookups, since the function has no way to distinguish them.
5. The caller's promise for addrA's withdrawal resolves as "completed" with addrB's `txHash`, even though addrA's funds have not landed at addrA — a status/hash misreport for a distinct on-chain outcome. [4](#0-3)

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L88-107)
```typescript
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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L580-609)
```typescript

```
