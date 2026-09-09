### Title
`findMatchingWithdrawal()` matches only by `assetId`, causing duplicate PoA withdrawals in a batch to report the same status/txHash - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal()` resolves the on-chain status of a withdrawal by calling `findMatchingWithdrawal()`, which selects a record from the PoA API response purely by matching `assetId`, ignoring the `WithdrawalIdentifier.index`. When a batch contains two withdrawals of the same `assetId` (e.g., two BTC withdrawals to different addresses), both `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` return the same PoA record, so the caller cannot tell which withdrawal actually completed.

### Finding Description
The claimed equality is: `report(index=0).txHash == outcome(withdrawal at index 0)` AND `report(index=1).txHash == outcome(withdrawal at index 1)`.

The code path:
- `describeWithdrawal()` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` [1](#0-0) .
- `findMatchingWithdrawal()` finds the first withdrawal in the (unsorted) API response whose `near_token_id` matches the given `assetId` — nothing else is used to disambiguate, and the comment explicitly documents that "multiple withdrawals of the same token in a single transaction are not supported" [2](#0-1) .
- `args.index` from `WithdrawalIdentifier` (set via `createWithdrawalIdentifier`) is never consulted in this lookup [3](#0-2) .
- `watchWithdrawal()` in the orchestration layer calls `bridge.describeWithdrawal({...args.wid, ...})` per withdrawal identifier and trusts the returned `status`/`txHash` as the truth for that specific withdrawal [4](#0-3) .

Root cause: when a single NEAR intent contains two withdrawal legs of the same `assetId` but different `destinationAddress`, the PoA bridge indexer API is only queried by `withdrawal_hash` (the shared intent tx hash) and returns a list of withdrawal records for that tx; `findMatchingWithdrawal` collapses this list down using only `assetId`, so both legs resolve to whichever matching record appears first in the (unsorted) list. There is no address-based, amount-based, or index-based disambiguation implemented (the code comment even proposes amount-sorting as a future fix, confirming it is not currently done).

None of the existing guards prevent this: `validateAddress`/`compareAddresses` operate on withdrawal input validation, not on status matching; `supports()` and `validateWithdrawal()` never see the batch as a whole; there is no `assert` checking withdrawal count parity or per-index destination address matching in `describeWithdrawal`.

### Impact Explanation
An integrator building on this SDK for a PoA-bridge batch withdrawal (two same-asset legs to different destination addresses in one intent) will receive `{status:'completed', txHash:'tx-for-A'}` for index 1 (withdrawal to B) even though B's funds never moved. This is a status/hash misreport that leads an integrator to credit or refund the wrong party — matching the "High" impact category (status or hash misreport making an integrator credit or refund twice). The finding is deterministic and repeatable any time a batch contains ≥2 withdrawals of the same `assetId` via the PoA route; it does not require compromising any privileged component — an ordinary user assembling their own batch withdrawal params triggers it.

### Likelihood Explanation
Preconditions: PoA bridge route, and a batch (`processWithdrawal({withdrawalParams:[...]})`) containing two or more entries with the same `assetId`. This is a normal, supported use of the public API (batch withdrawals are a documented feature); no special privileges or malicious infrastructure are needed — a normal user/integrator constructing a batch withdrawal request with two same-asset legs naturally hits it. It's fully repeatable across every such batch, not a one-off, and costs nothing extra to trigger (it's the default codepath, not a documented escape hatch to be misused).

### Recommendation
In `findMatchingWithdrawal()` / `describeWithdrawal()`, disambiguate withdrawals in the batch that share `assetId`, e.g., by also matching on `destinationAddress`/`destinationMemo`, or by sorting both the PoA API response and the batch's same-asset withdrawal params by amount (as the existing comment suggests) and pairing them positionally, or fail closed (throw/return an unresolvable status) when multiple candidates share `assetId` and cannot be disambiguated, rather than silently returning the first match for every index.

### Proof of Concept
Vitest test in `poa-bridge.test.ts` (mocking only `poaBridge.httpClient.getWithdrawalStatus`):
1. Build two `WithdrawalIdentifier`s via `bridge.createWithdrawalIdentifier` with `index:0/1`, same `assetId:'nep141:btc.omft.near'`, `destinationAddress: A` and `B` respectively, both sharing the same `tx.hash`.
2. Mock `poaBridge.httpClient.getWithdrawalStatus` to resolve `{ withdrawals: [{ status:'COMPLETED', data:{ near_token_id:'btc.omft.near', transfer_tx_hash:'tx-for-A', ... } }] }` (a single record, simulating that only A's leg actually settled).
3. Call `await bridge.describeWithdrawal(wid0)` and `await bridge.describeWithdrawal(wid1)`.
4. Assert both calls resolve to `{status:'completed', txHash:'tx-for-A'}` — i.e., `describeWithdrawal(index:1)` (destination B) incorrectly reports A's txHash as completed, proving `report(index=1) != outcome(withdrawal at index 1)`.

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

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L32-47)
```typescript
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
