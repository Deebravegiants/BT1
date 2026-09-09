### Title
Omni Bridge `describeWithdrawal` matches withdrawal status by raw array index instead of content, risking hash/status misreport for batched withdrawals - (File: `packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`)

### Summary
`OmniBridge.describeWithdrawal` picks the transfer describing a specific withdrawal purely by its positional index in the array returned by `omniBridgeAPI.getTransfer({ transactionHash })`, with no verification that the entry at that index actually corresponds to the withdrawal being polled (recipient, token, amount). This is the same bug class as the reported `observations[pair]` issue: indexing into an externally-supplied array whose length/ordering is not proven to correspond 1:1 with the caller's expectation.

### Finding Description
When a single NEAR intent transaction contains multiple withdrawals routed through the Omni Bridge, `IntentsSDK` assigns each withdrawal a sequential `index` per bridge route (`createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts:80-107`, using a per-route counter). Later, `OmniBridge.describeWithdrawal` retrieves status like this: [1](#0-0) 

```
const transfer = (
    await this.omniBridgeAPI.getTransfer({
        transactionHash: args.tx.hash,
    })
)[args.index];

if (transfer == null || transfer.recipient == null) {
    return { status: "pending" };
}
```

The code assumes the `getTransfer` array is returned in the exact same order the withdrawals were submitted in the intent, and simply indexes it. There is no check that `transfer.recipient`, `transfer.token_id`, or `transfer.amount` match the withdrawal that owns `args.index` (`args.withdrawalParams`).

Contrast this with the POA bridge, which explicitly documents and mitigates this exact class of bug: [2](#0-1) [3](#0-2) 

The POA bridge comment states: "Response list is unsorted, so we match by assetId instead of index," and implements `findMatchingWithdrawal` that matches on `near_token_id`/`assetId` rather than trusting positional order. `OmniBridge.describeWithdrawal` has no equivalent content-based matching — it trusts array order/length unconditionally, exactly like the reported pattern of indexing `observations[pair]` without proving the length/order invariant holds.

### Impact Explanation
If the Omni Bridge indexer's `getTransfer` response is not guaranteed to preserve submission order (e.g., transfers are returned by finalization time, insertion time in the indexer's own storage, or partial results while some transfers are still initializing), a withdrawal at position `index` could receive another withdrawal's transfer object. That means:
- `describeWithdrawal` could return `status: "completed"` with a `txHash` that actually belongs to a *different* withdrawal in the batch.
- A caller (SDK consumer / integrator) relying on this status to mark a withdrawal complete and to credit/refund a user could attribute the wrong destination transaction hash to the wrong withdrawal, or mark a still-pending withdrawal "completed" using a copy of a sibling withdrawal's already-completed status.

This falls under the explicitly listed High-impact category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
This is only reachable for multi-withdrawal intents where at least two withdrawals in the same NEAR transaction route through the Omni Bridge (`createWithdrawalIdentifiers` assigns increasing indexes per route in submission order — see `packages/intents-sdk/src/core/withdrawal-watcher.ts:88-104`). No malicious actor input is required; a benign multi-withdrawal batch is enough to trigger this if the indexer/API does not return transfers in strict submission order. I could not directly verify the ordering guarantees of the external Omni Bridge indexer API (`BridgeAPI.getTransfer`) from within this repository's scope, so the severity depends on that external invariant holding — the root-cause code pattern (unguarded positional indexing without content verification), however, is concretely present and independently confirmed by the fact that the sibling POA bridge implementation had to add explicit protection against exactly this scenario.

### Recommendation
In `OmniBridge.describeWithdrawal` (`packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts`), do not rely solely on `args.index` to select the transfer. Instead, filter/match the transfers returned by `getTransfer` against the specific withdrawal's expected `recipient` (destination address encoded as `OmniAddress`), token, and amount before falling back to positional indexing — mirroring the approach already used in `PoaBridge.describeWithdrawal`/`findMatchingWithdrawal`. If multiple candidate transfers match ambiguously, additional care is needed (as the POA bridge's code comments acknowledge), but any content-based check is stronger than relying purely on array position.

### Proof of Concept
1. Build an intent with two withdrawals, both routed through Omni Bridge, in the same NEAR transaction: withdrawal A (destination `addrA`) submitted first (assigned `index: 0`), withdrawal B (destination `addrB`) submitted second (assigned `index: 1`) — see `createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts:88-104`.
2. Suppose the Omni Bridge indexer processes/returns transfer B before transfer A (e.g., B finalizes on its destination chain faster), so `omniBridgeAPI.getTransfer({ transactionHash })` returns `[transferB, transferA]` instead of `[transferA, transferB]`.
3. When `describeWithdrawal` is called for withdrawal A with `args.index = 0`, it reads `transfer = transfers[0]`, which is actually `transferB` (recipient `addrB`).
4. `OmniBridge.describeWithdrawal` returns `{ status: "completed", txHash: transferB.finalised.transaction_hash }` for withdrawal A, even though withdrawal A's actual funds went (or are still pending) to `addrA`. An integrator polling withdrawal A's status via `sdk.waitForWithdrawalCompletion` would incorrectly mark withdrawal A as completed using withdrawal B's destination transaction hash.

### Citations

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L313-322)
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
