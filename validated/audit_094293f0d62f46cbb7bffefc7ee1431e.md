### Title
`findMatchingWithdrawal` matches by assetId only, causing status/txHash cross-attribution for same-token batch withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` calls `findMatchingWithdrawal`, which matches a POA bridge withdrawal record to a `WithdrawalIdentifier` solely by `nep141:<near_token_id> === assetId`, ignoring `destinationAddress`, `amount`, and the batch `index`. When a batch contains two or more withdrawals of the same token (e.g., two `nep141:bch.omft.near` withdrawals to different destination addresses in one intent), both `describeWithdrawal` calls resolve to the same (first-found) entry in the unsorted `withdrawals` array from the POA bridge API.

### Finding Description
The broken equality: for withdrawal index `i`, `describeWithdrawal(args[i])` should return the status/`txHash` corresponding to the withdrawal whose actual on-chain destination address and amount match `args[i].withdrawalParams`. Instead the code guarantees only `nep141:<near_token_id> === args[i].withdrawalParams.assetId`.

Code path:
- `describeWithdrawal` fetches all withdrawals for the intent's NEAR tx via `getWithdrawalStatusWithRetry` (`{ withdrawal_hash: args.tx.hash }`) [1](#0-0) .
- It then calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, which does `withdrawals.find((w) => \`nep141:${w.data.near_token_id}\` === assetId)` — a `.find()` that returns the **first** matching element in an **unsorted** array, with no use of `destinationAddress`, `amount`, or `args.index` [2](#0-1) .
- The code's own comment admits this: *"multiple withdrawals of the same token in a single transaction are not supported"* [3](#0-2) . The identical caveat and matching logic is duplicated in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` [4](#0-3) .
- Nothing in the SDK's batch-construction path (`IntentsSDK.createWithdrawalCompletionPromises`, `createWithdrawalIdentifiers` in `packages/intents-sdk/src/core/withdrawal-watcher.ts`) rejects or deduplicates batches containing repeated `assetId` values for the PoA route; `supports()`/`validateWithdrawal()` in `poa-bridge.ts` validate each withdrawal independently (address format, min amount, migrated-token check) but never check for assetId collisions across the batch [5](#0-4) [6](#0-5) .

Exploit flow: An unprivileged user (or an integrator forwarding user-supplied `withdrawalParams`) submits a batch with two `nep141:bch.omft.near` withdrawals — one to destination A, one to destination B — via `sdk.waitForWithdrawalCompletion({ withdrawalParams: [w1, w2], intentTx })`. Once the POA relayer processes and reports both withdrawals via `getWithdrawalStatus`, both `describeWithdrawal(index=0)` and `describeWithdrawal(index=1)` independently call `findMatchingWithdrawal` with the same `assetId`; both resolve to whichever entry is first in the (unsorted) `withdrawals` array. If that entry is COMPLETED with `transfer_tx_hash` to destination A, both `WithdrawalIdentifier`s (for A and B) report `{status: "completed", txHash: <A's hash>}`, even though B's actual payout to its own destination may still be pending, failed, or completed with a different hash.

### Impact Explanation
An integrator relying on `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` per-index results would receive a misreported status/txHash for withdrawal index `i` — either falsely marking a still-pending or failed payout as `completed` with someone else's `txHash`, or (transiently, before B's own entry appears) reporting A's hash for B. This matches the "status or hash misreport" High-impact category: an integrator could prematurely credit/reconcile a user's withdrawal as complete using a txHash that does not correspond to that user's actual destination, or fail to detect that the true payout for that index is still pending/failed. This is deterministically repeatable any time a batch contains ≥2 withdrawals of the same PoA token.

### Likelihood Explanation
Preconditions: caller must construct a batch with two or more PoA-route withdrawals sharing the same `assetId` (fully attacker/integrator-controlled input; no privileged access needed) and the underlying relayer/API must process and report multiple entries for that token under the same NEAR tx hash. Cost is a single ordinary batch withdrawal transaction. This is explicitly acknowledged as unhandled by the code's own comments, indicating high feasibility and confirmed absence of any guard (no dedup check, no per-destination/amount disambiguation).

### Recommendation
In `findMatchingWithdrawal` (and its duplicate in `waitForWithdrawalCompletion.ts`), disambiguate same-assetId withdrawals using additional available fields (e.g., match on destination address/amount when the POA API exposes them, or sort both the API response and local withdrawal params deterministically by amount as the existing comment suggests) before consuming them; alternatively, reject/flag batches with duplicate `assetId` for the PoA route at `supports()`/`validateWithdrawal()` time until proper disambiguation is implemented.

### Proof of Concept
Vitest plan (mock only the HTTP client `poaBridge.httpClient.getWithdrawalStatus`):
1. Mock `getWithdrawalStatus` to return two withdrawals for `nep141:bch.omft.near`: entry 1 `{status: "COMPLETED", data: {near_token_id: "bch.omft.near", transfer_tx_hash: "hashA"}}` (intended for destination A) and entry 2 `{status: "PENDING", data: {near_token_id: "bch.omft.near"}}` (intended for destination B).
2. Call `poaBridge.describeWithdrawal` twice with two `WithdrawalIdentifier`s that both have `assetId: "nep141:bch.omft.near"` but different `destinationAddress` (A and B) and `index: 0` / `index: 1`.
3. Assert the broken equality: both calls return `{status: "completed", txHash: "hashA"}` — i.e., `result[1]` incorrectly equals `result[0]` — instead of `result[1]` reflecting B's own `PENDING` status.
4. Assert this violates the invariant "each WithdrawalIdentifier resolves to the withdrawal with the same destination address and amount."

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L81-106)
```typescript
	async supports(
		params: Pick<WithdrawalParams, "assetId" | "routeConfig">,
	): Promise<boolean> {
		if (params.routeConfig != null && !this.is(params.routeConfig)) {
			return false;
		}

		const assetInfo = this.parseAssetId(params.assetId);
		const isValid = assetInfo != null;

		if (!isValid && params.routeConfig != null) {
			throw new UnsupportedAssetIdError(
				params.assetId,
				"`assetId` does not match `routeConfig`.",
			);
		}

		if (
			assetInfo != null &&
			POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE[assetInfo.contractId] !== undefined
		) {
			return false;
		}

		return isValid;
	}
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L170-230)
```typescript
	async validateWithdrawal(args: {
		assetId: string;
		amount: bigint;
		destinationAddress: string;
		logger?: ILogger;
		skipMinAmountValidation?: boolean;
		destinationMemo?: string;
	}): Promise<void> {
		const assetInfo = this.parseAssetId(args.assetId);
		assert(assetInfo != null, "Asset is not supported");

		if (
			validateAddress(args.destinationAddress, assetInfo.blockchain) === false
		) {
			throw new InvalidDestinationAddressForWithdrawalError(
				args.destinationAddress,
				assetInfo.blockchain,
			);
		}

		// Use cached getSupportedTokens to avoid frequent API calls
		const { tokens } = await this.getCachedSupportedTokens(
			[toPoaNetwork(assetInfo.blockchain)],
			args.logger,
		);

		const tokenInfo = tokens.find(
			(token) => token.intents_token_id === args.assetId,
		);

		if (tokenInfo == null) {
			throw new UnsupportedAssetIdError(
				args.assetId,
				"`assetId` is not supported in PoA bridge.",
			);
		}

		if (
			tokenInfo.origin_chain_address !== "native" &&
			compareAddresses(
				tokenInfo.origin_chain_address,
				args.destinationAddress,
				assetInfo.blockchain,
			)
		) {
			throw new DestinationAddressMatchesTokenAddressError(
				tokenInfo.origin_chain_address,
				args.assetId,
			);
		}

		if (!args.skipMinAmountValidation) {
			const minWithdrawalAmount = BigInt(tokenInfo.min_withdrawal_amount);
			if (args.amount < minWithdrawalAmount) {
				throw new MinWithdrawalAmountError(
					minWithdrawalAmount,
					args.amount,
					args.assetId,
				);
			}
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
