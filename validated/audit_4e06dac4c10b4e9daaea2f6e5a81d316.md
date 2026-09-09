### Title
POA Bridge withdrawal status matched by assetId only, causing wrong destination tx hash to be reported for batched same-asset withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts, packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts)

### Summary
`describeWithdrawal()` in the POA bridge and `waitForWithdrawalCompletion()` in internal-utils both resolve the destination transaction hash for a withdrawal by matching the POA Bridge API's returned `withdrawals` list solely on `assetId` (via `near_token_id`), ignoring the withdrawal's `index` within the originating NEAR transaction and the `destinationAddress`/`amount`. If a single NEAR transaction contains more than one withdrawal of the same underlying asset (e.g. a batched withdrawal to two different destination addresses), both lookups collapse to the same (first) matching entry, so the SDK can report the wrong destination `txHash` and `completed` status for a withdrawal that has not actually settled to its intended destination.

### Finding Description
`findMatchingWithdrawal()` in `poa-bridge.ts` is documented as matching only by `assetId`: [1](#0-0) 

This function is invoked by `describeWithdrawal()`, which is the per-`WithdrawalIdentifier` (including `index`) status query used by `watchWithdrawal()`: [2](#0-1) 

The identical pattern exists in `internal-utils`'s `waitForWithdrawalCompletion()`, whose `findMatchingWithdrawal()` also matches only on `assetId`/`near_token_id`, with the same acknowledged limitation in its docstring: [3](#0-2) 

The `WithdrawalIdentifier` type carries an `index` field precisely to disambiguate multiple withdrawals produced by the same NEAR transaction, and `createWithdrawalIdentifier()` in the same POA bridge file receives and stores that `index`: [4](#0-3) 

However this `index` is never used to select the correct entry from the POA API's `withdrawals` array — the code explicitly states "Response list is unsorted, so we match by assetId instead of index," but doing so means two withdrawals of the same asset (to different destination addresses, in the same NEAR tx) are indistinguishable: `Array.prototype.find()` always returns the first entry whose `near_token_id` matches, regardless of which one actually corresponds to the caller's `index`/`destinationAddress`.

The equality broken here is: *the destination chain / recipient tx hash reported for withdrawal N must correspond to the on-chain transfer that actually paid withdrawal N's destination address*. When two same-asset withdrawals exist in one transaction, `describeWithdrawal()`/`waitForWithdrawalCompletion()` can report `status: "completed"` with the `txHash` belonging to the *other* withdrawal's transfer — i.e., a status/hash is reported that does not match the actual on-chain outcome for that specific withdrawal.

### Impact Explanation
An integrator or the SDK's own `watchWithdrawal()` consumer relies on this reported `txHash`/`status` as the source of truth for confirming a withdrawal has settled to its destination (see `withdrawal-watcher.ts`, which returns `{ hash: status.txHash }` directly from `describeWithdrawal()`'s output as the completion result): [5](#0-4) 

If withdrawal A (to address X) and withdrawal B (to address Y) of the same token are batched in one NEAR transaction, and the POA API completes A first, a caller polling for B's status can be told `completed` with A's `txHash`. This is a "status/hash misreport" that could cause an integrator to mark B as delivered/credited based on a transaction hash that actually paid a different destination — matching the High-impact class of "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
This requires no admin or relayer misbehavior — it is triggerable by any ordinary unprivileged user who batches two or more withdrawals of the same underlying asset (same `nep141:` token) to different destinations within a single signed intent/NEAR transaction, a use case explicitly supported by the SDK's `index`-based `WithdrawalIdentifier` design and the "batch withdrawal" RFC referenced in the repo (`docs/design/rfc-batch-withdrawal-granular-control.md`). The bug is also self-acknowledged in code comments in both locations, confirming the gap is real and currently unmitigated, dependent only on the POA Bridge API not yet supporting index-based disambiguation.

### Recommendation
- Disambiguate withdrawals returned by the POA Bridge API using more than `assetId`: match on `destinationAddress`/`address` and `amount` in addition to `near_token_id`, and only fall back to index/order-based matching (sorted deterministically, e.g. by amount as the code comment suggests) when multiple same-asset entries remain ambiguous.
- Until the POA API supports a stable per-intent identifier, explicitly reject or refuse to batch multiple same-asset POA withdrawals to different destinations within a single transaction in `createWithdrawalIntents`/`validateWithdrawal`, to avoid silently reporting a wrong destination hash.
- Add invariant checks so that if more than one candidate withdrawal matches, the SDK throws (fails closed) rather than returning the first match with a false "completed" status.

### Proof of Concept
1. A user submits a single NEAR transaction containing two POA-bridge withdrawal intents for the same asset (e.g. `nep141:eth.omft.near`), one to address `X` and one to address `Y`, at indices 0 and 1 respectively.
2. The POA Bridge API processes withdrawal to `X` first and returns it as `COMPLETED` with `transfer_tx_hash: "tx-to-X"`, while the withdrawal to `Y` is still pending.
3. The SDK (or an integrator) calls `describeWithdrawal({ index: 1, withdrawalParams: { assetId: "nep141:eth.omft.near", destinationAddress: Y, ... }, tx })`.
4. `findMatchingWithdrawal()` matches purely on `assetId`, finds the first entry (the one destined for `X`), and `describeWithdrawal()` returns `{ status: "completed", txHash: "tx-to-X" }` for the withdrawal that was supposed to go to `Y`, matching the existing test at `poa-bridge.test.ts:1054` ("matches withdrawal by assetId, not by index") which explicitly demonstrates this collapsing behavior — the only difference being that in the shipped test the mismatched entries have different `near_token_id`s (so it "accidentally" resolves correctly), whereas the same code path collapses incorrectly when both entries share the same `near_token_id`.

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L36-47)
```typescript
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
