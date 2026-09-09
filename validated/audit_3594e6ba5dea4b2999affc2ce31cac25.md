### Title
Same-token repeated withdrawals in one intent cause status/txHash misattribution across `WithdrawalIdentifier`s - (File: `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts`)

### Summary
`PoaBridge.describeWithdrawal` matches an on-chain withdrawal record to a `WithdrawalIdentifier` solely by `nep141:<near_token_id>` equality via `findMatchingWithdrawal`, ignoring the identifier's `index`. When a single intent contains two withdrawals of the same PoA token (e.g. `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near`), the bridge API returns multiple entries for that token, and `Array.prototype.find` deterministically returns only the first match for both `WithdrawalIdentifier`s, so both callers of `waitForWithdrawalCompletion` observe the same status/`txHash`.

### Finding Description
The broken equality: `WithdrawalIdentifier[i].{status, txHash}` should equal the status of the on-chain withdrawal whose `destinationAddress`/`amount` matches `WithdrawalIdentifier[i].withdrawalParams`, not the status of the first API record sharing the same `near_token_id`.

Code path:
- `describeWithdrawal` calls `getWithdrawalStatusWithRetry` (keyed only by `args.tx.hash`, i.e., the NEAR intent tx hash, shared by all withdrawals in the same intent) — [1](#0-0) .
- The returned `response.withdrawals` list contains all withdrawal records tied to that intent tx.
- `findMatchingWithdrawal` matches purely by `` `nep141:${w.data.near_token_id}` === assetId `` and returns via `.find()`, i.e., the first array match — [2](#0-1) .
- The function's own doc comment admits: "multiple withdrawals of the same token in a single transaction are not supported" and that the POA API doesn't support disambiguation either — [3](#0-2) .
- `args.index` (set per-bridge-route in `createWithdrawalIdentifiers`, see `packages/intents-sdk/src/core/withdrawal-watcher.ts` lines 80-107) is carried in `WithdrawalIdentifier` but is **never used** in `describeWithdrawal`/`findMatchingWithdrawal` to disambiguate — [4](#0-3) .
- `watchWithdrawal` (used by `waitForWithdrawalCompletion`) just calls `bridge.describeWithdrawal({...args.wid, ...})` per identifier and reports whatever `status`/`txHash` comes back as final completion state — [5](#0-4) .

Nothing in `supports()`, `validateWithdrawal()`, or elsewhere in `PoaBridge` rejects or deduplicates a batch containing two withdrawals of the same `assetId` — `supports` only validates the asset ID format, migration status, and route, not batch uniqueness — [6](#0-5) . There's no `assert`/sanity check anywhere in this file preventing duplicate assetIds in a single intent's withdrawal params. Since matching is done exclusively by token id and the API result ordering is explicitly documented as unsorted/undetermined, both `WithdrawalIdentifier`s for the two same-token withdrawals resolve to identical `{status, txHash}}` (whichever the array happens to return first), even though they have different `destinationAddress` and possibly different `amount`.

### Impact Explanation
An integrator polling `waitForWithdrawalCompletion` for two withdrawal identifiers of the same PoA token receives the same `status: "completed"` and same `txHash` for both, even though only one destination actually received funds (or they received different amounts/addresses). This is a status/hash misreport that can cause an integrator to believe both payouts succeeded and credit/refund the user for both legs, i.e., matches "High – a status or hash misreport making an integrator credit or refund twice." The bug is deterministic and repeatable on every same-token multi-withdrawal batch for the affected token (and any other PoA token), not a one-off race.

### Likelihood Explanation
Preconditions: an ordinary user (or integrator forwarding user-controlled withdrawal params) constructs a single intent with two withdrawal legs for the same PoA `assetId` but different destination addresses/amounts — this is fully within attacker/integrator control and requires no privileged access, matching the question's "attacker controls batch composition with repeated assetId" scenario. No special solver or contract permission is needed; the SDK's `supports()`/`validateWithdrawal()` do not reject such batches. This is trivially and repeatably reproducible for any PoA-bridged token, including the base USDC token cited in the question.

### Recommendation
Disambiguate matching using more than `near_token_id`: match candidate withdrawals by `(near_token_id, destination address, amount)` tuple, or use `WithdrawalIdentifier.index` combined with a stable sort of both the API's `withdrawals` array and the batch's withdrawal params (e.g., sort by amount as the existing comment suggests, since relayer fees are equal for same-token legs) before pairing by position. Until the POA API supports a unique identifier per withdrawal, the SDK should reject (throw) when constructing withdrawal identifiers for an intent containing more than one withdrawal with the same `assetId`, rather than silently mismatching results.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (new test)
it("BUG: two same-token withdrawals in one tx get identical status attributed to both identifiers", async () => {
  vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "dest-tx-hash-A", // destined for addressA
          chain: "base",
          defuse_asset_identifier: "nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near",
          near_token_id: "base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near",
          decimals: 6,
          amount: 100,
          account_id: "test.near",
          address: "0xAAAA...",
          created: "2024-01-01T00:00:00Z",
        },
      },
      {
        status: "PENDING", // second withdrawal (destined for addressB) still pending on-chain
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: null,
          chain: "base",
          defuse_asset_identifier: "nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near",
          near_token_id: "base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near",
          decimals: 6,
          amount: 200,
          account_id: "test.near",
          address: "0xBBBB...",
          created: "2024-01-01T00:00:00Z",
        },
      },
    ],
  });

  const bridge = new PoaBridge({
    envConfig: configsByEnvironment.production,
    xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
  });

  const widA = {
    landingChain: Chains.Base,
    index: 0,
    withdrawalParams: {
      assetId: "nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near",
      amount: 100n,
      destinationAddress: "0xAAAA...",
      feeInclusive: false,
    },
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  };
  const widB = {
    ...widA,
    index: 1,
    withdrawalParams: {
      ...widA.withdrawalParams,
      amount: 200n,
      destinationAddress: "0xBBBB...", // different destination, still PENDING on-chain
    },
  };

  const resultA = await bridge.describeWithdrawal(widA);
  const resultB = await bridge.describeWithdrawal(widB);

  // EXPECTED (invariant): each identifier resolves to ITS OWN destination's status.
  // resultA should be completed with dest-tx-hash-A, resultB should be pending.
  //
  // ACTUAL (bug): both calls hit findMatchingWithdrawal which does
  // withdrawals.find(w => `nep141:${w.data.near_token_id}` === assetId)
  // and returns the FIRST match (index 0, "COMPLETED") for BOTH identifiers.
  expect(resultA).toEqual({ status: "completed", txHash: "dest-tx-hash-A" });
  expect(resultB).toEqual({ status: "completed", txHash: "dest-tx-hash-A" }); // WRONG: should be "pending"
});
```
This demonstrates that `resultB` — which per the mocked API is actually `PENDING` (funds not yet delivered to `0xBBBB...`) — is misreported as `completed` with the tx hash belonging to the other destination's payout, confirming the misattribution described in the question.

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
