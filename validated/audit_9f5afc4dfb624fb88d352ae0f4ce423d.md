### Title
POA Bridge withdrawal status is matched by `assetId` only, causing wrong withdrawal's completion status/tx hash to be reported when a batch contains multiple withdrawals of the same token - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` and the standalone `waitForWithdrawalCompletion` helper both resolve a specific withdrawal leg (identified by `index` within a batch) by scanning the bridge's unsorted withdrawal list and matching solely on `assetId`, never on `index`, `amount`, or `destinationAddress`. When a caller submits a batch containing two or more withdrawals of the *same* token (a supported, undocumented-as-forbidden usage pattern), `describeWithdrawal({index: 1, ...})` can return the completion record that actually belongs to withdrawal `index: 0` (or vice versa), because `Array.prototype.find` simply returns the first entry whose `near_token_id` matches.

### Finding Description
`findMatchingWithdrawal` in `poa-bridge.ts` is:

```ts
function findMatchingWithdrawal(
	withdrawals: WithdrawalStatusResponse["withdrawals"],
	assetId: string,
): WithdrawalStatusResponse["withdrawals"][number] | undefined {
	return withdrawals.find((w) => `nep141:${w.data.near_token_id}` === assetId);
}
``` [1](#0-0) 

This is invoked from `describeWithdrawal`:

```ts
const withdrawal = findMatchingWithdrawal(
    response.withdrawals,
    args.withdrawalParams.assetId,
);
...
if (withdrawal.status === "COMPLETED") {
    return { status: "completed", txHash: withdrawal.data.transfer_tx_hash };
}
``` [2](#0-1) 

The code explicitly acknowledges this limitation but treats it as merely unsupported rather than fixing the matching logic:

```
// NOTE: Currently only matches by assetId. This means multiple withdrawals
// of the same token in a single transaction are not supported.
// POA API doesn't currently support this case either. When support is added,
// matching could be done by sorting both API results and withdrawal params by
// amount (fees are equal for same token, so relative ordering is preserved).
``` [3](#0-2) 

The identical bug exists independently in the lower-level helper used by `sdk.waitForWithdrawalCompletion`:

```ts
function findMatchingWithdrawal(
	withdrawals: types.WithdrawalStatusResponseOk["result"]["withdrawals"],
	criteria: WithdrawalCriteria,
) {
	return withdrawals.find(
		(w) => `nep141:${w.data.near_token_id}` === criteria.assetId,
	);
}
``` [4](#0-3) 

The equality that should hold is: *"the withdrawal record returned by `describeWithdrawal(index=i)` corresponds to the on-chain withdrawal leg `i` of the batch."* Because matching ignores `index`, `amount`, and `destinationAddress`, this equality breaks whenever a batch has ≥2 legs of the same `assetId` (a case the SDK's public batch-withdrawal API explicitly supports — `sdk.processWithdrawal`/`sdk.createWithdrawalCompletionPromises` accept `WithdrawalParams[]` without any validation rejecting duplicate `assetId`s):

```ts
public processWithdrawal(args: ProcessWithdrawalArgs<WithdrawalParams[]>): Promise<BatchWithdrawalResult>;
``` [5](#0-4) 

`createWithdrawalIdentifiers` assigns per-bridge sequential `index` values purely by counting occurrences of the same route, with no de-duplication or ordering guarantee tied to the underlying POA API response order:

```ts
const currentIndex = indexes.get(bridge.route) ?? 0;
indexes.set(bridge.route, currentIndex + 1);
const wid = bridge.createWithdrawalIdentifier({ withdrawalParams: w, index: currentIndex, tx: args.intentTx });
``` [6](#0-5) 

`watchWithdrawal` (and therefore `createWithdrawalCompletionPromises`) polls per-`wid` until `describeWithdrawal` reports `"completed"`, and immediately resolves with the reported `txHash`:

```ts
if (status.status === "completed") {
    return status.txHash != null ? { hash: status.txHash } : { hash: null };
}
``` [7](#0-6) 

Consequence: if leg 0 (e.g., 100 USDC → address A) completes on-chain first while leg 1 (e.g., 50 USDC → address B, same token) is still pending, `describeWithdrawal` for leg 1 will find the *same* completed withdrawal record (leg 0's) since only `assetId` is checked, and incorrectly report leg 1 as `"completed"` with leg 0's `transfer_tx_hash`. An integrator relying on `createWithdrawalCompletionPromises`/`processWithdrawal` to gate crediting a user account or releasing downstream funds per withdrawal index would then treat leg 1 as settled — potentially crediting/refunding it based on a transaction hash and amount that belongs entirely to a different withdrawal — before leg 1 is actually confirmed on-chain, or possibly never distinguishing it from leg 0 at all if both complete.

### Impact Explanation
This is a status/hash misreport where the value returned for one withdrawal leg is actually the on-chain outcome of a *different* leg. Per the accepted High-impact category, "a status or hash misreport making an integrator credit or refund twice" directly applies: an integrator building on this SDK (e.g., a custodial platform crediting user balances per withdrawal leg as they land, using `createWithdrawalCompletionPromises`) can be misled into crediting a withdrawal as done using another leg's hash/amount, resulting in double-crediting or premature release of funds for the yet-unconfirmed leg.

### Likelihood Explanation
This requires no malicious actor — only a legitimate user/integrator submitting a batch withdrawal (`WithdrawalParams[]`) with two or more entries sharing the same `assetId` (e.g., splitting a large withdrawal across destinations, or a token withdrawal + separate token fee-refund of the same asset). Nothing in `sdk.ts`, `withdrawal-watcher.ts`, or `poa-bridge.ts` validates or rejects duplicate-`assetId` batches, so this is reachable through the normal public API (`processWithdrawal`, `createWithdrawalCompletionPromises`, `waitForWithdrawalCompletion`). The team's own inline comment confirms this scenario is known but currently unhandled.

### Recommendation
Match withdrawals deterministically to their originating leg instead of relying solely on `assetId`. Since POA's response is unsorted, disambiguate using amount ordering (as the code comment already suggests) or, preferably, request/track a leg-specific correlation id from the POA bridge API if available. Until fixed, `describeWithdrawal`/`waitForWithdrawalCompletion` should throw/reject (rather than silently return a possibly-wrong record) when more than one withdrawal in the batch shares the same `assetId`, so integrators are not silently given an incorrect status/hash for the wrong leg.

### Proof of Concept
1. Build a batch with two `WithdrawalParams` for the same `assetId` (e.g., `nep141:usdt.tether-token.near`) but different `amount`/`destinationAddress`, and submit via `sdk.processWithdrawal({ withdrawalParams: [legA, legB] })`.
2. `createWithdrawalIdentifiers` assigns `index: 0` to legA and `index: 1` to legB for the `PoaBridge` route.
3. On the POA bridge side, legA settles first (status `COMPLETED`, `transfer_tx_hash = 0xAAA`), legB is still `PENDING`.
4. Concurrent polling: `watchWithdrawal` for `wid(index=1)` calls `describeWithdrawal`, which calls `findMatchingWithdrawal(response.withdrawals, "nep141:usdt.tether-token.near")` — this returns legA's `COMPLETED` record (first match by `assetId`), so `describeWithdrawal` returns `{status:"completed", txHash:"0xAAA"}` for what the caller believes is legB.
5. `watchWithdrawal`'s promise for legB (`index:1`) resolves with `{hash:"0xAAA"}`, identical to legA's result, even though legB has not settled on-chain yet — the caller's `promises[1]` reports a false "completed" status/hash, breaking the equality between the withdrawal instance polled and the on-chain outcome actually reported.

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-417)
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

**File:** packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts (L144-153)
```typescript
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

**File:** packages/intents-sdk/src/sdk.ts (L789-791)
```typescript
	public processWithdrawal(
		args: ProcessWithdrawalArgs<WithdrawalParams[]>,
	): Promise<BatchWithdrawalResult>;
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L43-47)
```typescript
					if (status.status === "completed") {
						return status.txHash != null
							? { hash: status.txHash }
							: { hash: null };
					}
```

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L94-101)
```typescript
		const currentIndex = indexes.get(bridge.route) ?? 0;
		indexes.set(bridge.route, currentIndex + 1);

		const wid = bridge.createWithdrawalIdentifier({
			withdrawalParams: w,
			index: currentIndex,
			tx: args.intentTx,
		});
```
