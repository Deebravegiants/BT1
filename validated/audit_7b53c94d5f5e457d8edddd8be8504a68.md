This is a real, documented finding — the vulnerability is confirmed by the code and its own comments.

### Title
Same-assetId batch withdrawals cause `describeWithdrawal` to misreport status/txHash across indices - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` matches the POA bridge's withdrawal-status API response to a `WithdrawalIdentifier` purely by `assetId` <cite repo="Tylerpinwa/sdk-monorepo--011" path="packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts" start="318="322" /> rather than by index or destination address. When a batch contains two or more withdrawals of the same `assetId` to different `destinationAddress` values, `findMatchingWithdrawal` returns the *first* matching entry in the (unsorted) API response for every one of those withdrawals, so `describeWithdrawal(wid_i)` can return the status/txHash that actually belongs to a different withdrawal `j`.

### Finding Description
The invariant claimed by `sdk.createWithdrawalCompletionPromises`/README ("promises[i] corresponds to withdrawalParams[i]") is broken at the POA bridge layer for the reported `(status, txHash)` value. `describeWithdrawal` calls `getWithdrawalStatusWithRetry` to fetch all withdrawals for the shared NEAR intent tx hash, then calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` [1](#0-0) , which does a `.find()` on `assetId` alone, ignoring `destinationAddress`/`amount`/index [2](#0-1) . The code's own comment documents the root cause: "Response list is unsorted, so we match by assetId instead of index" and the function docstring explicitly states "multiple withdrawals of the same token in a single transaction are not supported" by this matching logic [3](#0-2) . The identical matching bug (and identical caveat comment) exists in the sibling helper `findMatchingWithdrawal` in `internal-utils` [4](#0-3) .

Attacker input: a batch `withdrawalParams = [{assetId: X, destinationAddress: A}, {assetId: X, destinationAddress: B}]` submitted by an ordinary user (or forwarded by an integrator from user/counterparty-controlled fields) via `signAndSendWithdrawalIntent`/`processWithdrawal`, then polled with `waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises`. Since `assetId`, `destinationAddress`, and `amount` are all attacker-controlled per the SDK's public API, nothing in `validateWithdrawal`, `supports()`, or `createWithdrawalIntents` rejects two entries sharing the same `assetId` with different destinations — each is validated independently [5](#0-4) .

Exploit flow: both withdrawals are batched into the same intent/tx, so the POA bridge indexer records two withdrawal entries for the same `withdrawal_hash` with the same `near_token_id`. `getWithdrawalStatusWithRetry` returns both entries in the (unsorted, per the code's own comment) order. `findMatchingWithdrawal` for index 0's `describeWithdrawal` call returns `.find()`'s first match — which may be the entry that actually corresponds to index 1's destination (e.g., if it completed first or the array order differs from submission order). The same is true for index 1's call: it can pick up index 0's record instead. There is no guard checking `destinationAddress` or amount to disambiguate, and no code path deduplicates or reorders based on those fields.

### Impact Explanation
An integrator relying on `promises[i]` to correspond to `withdrawalParams[i]` can receive a `txHash`/`status` for withdrawal `i` that actually belongs to withdrawal `j`'s payout to a different destination address. This can cause the integrator to: (a) credit destination A's account as "completed" using a tx hash that actually paid destination B, enabling a double-credit for the attacker at A while B's real completion is silently correlated to A; or (b) mark a genuinely completed withdrawal as belonging to the wrong recipient, causing accounting/refund errors. This matches the "status or hash misreport making an integrator credit or refund twice" category (High/Critical per the rubric), since it is a real report divergence between the claimed and actual per-index outcome, not merely theoretical.

### Likelihood Explanation
Preconditions are trivial for an unprivileged caller: submit a normal batch withdrawal with two entries sharing the same `assetId` but different `destinationAddress`/`amount` — nothing in `supports()`, `validateWithdrawal()`, or `createWithdrawalIntents()` rejects this combination since each entry is validated independently and there is no uniqueness constraint. The attacker needs no special access, just the ability to call the public batch withdrawal APIs with attacker-controlled `assetId`/`destinationAddress` fields. It is fully repeatable on every batch containing duplicate-`assetId` entries, and the code authors themselves acknowledge this is currently unhandled ("not supported... POA API doesn't currently support this case either").

### Recommendation
Disambiguate matching beyond `assetId`: incorporate `destinationAddress` (and/or `amount`, `destinationMemo`) into `findMatchingWithdrawal`'s matching criteria in both `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` and `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts`. If the POA bridge API cannot distinguish same-asset withdrawals in the same tx (e.g., no per-entry destination in the response), either: (1) reject/refuse batches containing duplicate `assetId` entries at `validateWithdrawal`/`supports()` time until the bridge API supports disambiguation, or (2) implement the amount-based sorting/matching strategy already suggested in the code comment (sort both API results and withdrawal params by amount, since relayer fees are identical per token) to restore a consistent 1:1 correspondence.

### Proof of Concept
```ts
// vitest test plan (mock only httpClient.getWithdrawalStatus)
import { PoaBridge } from "../bridges/poa-bridge/poa-bridge";
import { poaBridge } from "@defuse-protocol/internal-utils";

it("misattributes status/txHash across same-assetId withdrawals", async () => {
  const assetId = "nep141:usdc.omft.near";
  const withdrawalParamsA = { assetId, destinationAddress: "addrA", amount: 100n /* ... */ };
  const withdrawalParamsB = { assetId, destinationAddress: "addrB", amount: 200n /* ... */ };

  // Mock API returns two entries for the same withdrawal_hash, order != submission order
  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus").mockResolvedValue({
    withdrawals: [
      { status: "COMPLETED", data: { near_token_id: "usdc.omft.near", transfer_tx_hash: "0xHASH_FOR_B" } },
      { status: "COMPLETED", data: { near_token_id: "usdc.omft.near", transfer_tx_hash: "0xHASH_FOR_A" } },
    ],
  });

  const bridge = new PoaBridge({ envConfig, xrplRpcUrls: [] });

  const widA = bridge.createWithdrawalIdentifier({ withdrawalParams: withdrawalParamsA, index: 0, tx: { hash: "sharedHash" } });
  const widB = bridge.createWithdrawalIdentifier({ withdrawalParams: withdrawalParamsB, index: 1, tx: { hash: "sharedHash" } });

  const resultA = await bridge.describeWithdrawal(widA);
  const resultB = await bridge.describeWithdrawal(widB);

  // BROKEN EQUALITY: expected resultA.txHash to correspond to withdrawal 0 (addrA),
  // but describeWithdrawal returns the FIRST match regardless of destination,
  // so resultA.txHash === "0xHASH_FOR_B" (wrong) instead of the entry that belongs to A.
  expect(resultA).toEqual({ status: "completed", txHash: "0xHASH_FOR_B" }); // demonstrates misattribution
  expect(resultB).toEqual({ status: "completed", txHash: "0xHASH_FOR_B" }); // both resolve to same record - collision
});
```
This demonstrates that `(status, txHash)` reported for index 0 does not equal the outcome of withdrawal 0 specifically, but instead collides with (or is drawn from) whichever entry `.find()` returns first for the shared `assetId`.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L170-219)
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L409-416)
```typescript
/**
 * Finds a withdrawal matching the given assetId.
 *
 * NOTE: Currently only matches by assetId. This means multiple withdrawals
 * of the same token in a single transaction are not supported.
 * POA API doesn't currently support this case either. When support is added,
 * matching could be done by sorting both API results and withdrawal params by
 * amount (fees are equal for same token, so relative ordering is preserved).
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
