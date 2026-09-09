### Title
`describeWithdrawal` misreports status/txHash for concurrent same-asset PoA withdrawals due to index-blind, unsorted-array matching - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal` ignores `WithdrawalIdentifier.index` and instead matches the PoA bridge API's withdrawal records purely by `assetId` via `findMatchingWithdrawal`, taking the first array element that matches. Since the API documents that the response list is unsorted, when an intent contains two withdrawals of the same token to different destination addresses, `watchWithdrawal` for index 0 and index 1 can both resolve against the same (or swapped) record, causing the wrong `(status, txHash)` to be reported for a given withdrawal identifier.

### Finding Description
The broken equality: for a `WithdrawalIdentifier` at `index=i` submitted in a batch of withdrawals for the same NEAR tx (`tx.hash`), the value returned by `describeWithdrawal({index: i, ...})` must equal the outcome (`status`, `data.transfer_tx_hash`) of the i-th physical withdrawal (i.e., the one going to `withdrawalParams[i].destinationAddress`).

Code path:
- `createWithdrawalIdentifiers` in [1](#0-0)  assigns a per-bridge-route `index` (0, 1, 2, …) to each `WithdrawalParams` sharing the same `intentTx`, via `bridge.createWithdrawalIdentifier`.
- `watchWithdrawal` at [2](#0-1)  polls `bridge.describeWithdrawal({...args.wid, ...})` for each identifier independently, expecting the `index` to disambiguate multiple withdrawals from the same tx.
- `PoaBridge.describeWithdrawal` at [3](#0-2)  fetches `response.withdrawals` for the shared `args.tx.hash` and calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)` — it never consults `args.index`.
- `findMatchingWithdrawal` at [4](#0-3)  does `withdrawals.find(w => 'nep141:' + w.data.near_token_id === assetId)`, returning the first array element matching the asset, regardless of which physical withdrawal it represents.
- The function's own doc comment at [5](#0-4)  explicitly acknowledges: "multiple withdrawals of the same token in a single transaction are not supported," and the call site comment at [6](#0-5)  states "Response list is unsorted, so we match by assetId instead of index" — but assetId alone cannot disambiguate two same-asset withdrawals, so both `index=0` and `index=1` calls end up querying/matching against the same unsorted list with the same predicate, and (per the `.find` semantics) both resolve to identical/first-matching record.

Root cause: there is no field carrying which destination address / physical withdrawal each API record belongs to that's checked against `withdrawalParams.destinationAddress`; the match key (`assetId` only) is not unique when two same-token withdrawals exist in one intent tx.

Why existing guards don't help: `supports()`, `validateWithdrawal()`, `compareAddresses()` all validate a single withdrawal's asset/address correctness at submission time, but none of them prevent an integrator/attacker from submitting two same-asset PoA withdrawals in one intent, and none of them affect the read path in `describeWithdrawal`. The intents contract's own signature/nonce checks guarantee the on-chain funds move to the correct signed destination addresses — the funds themselves are not misrouted on-chain. The bug is purely in the SDK's off-chain status/txHash reporting layer that an integrator relies on to know which withdrawal (by index) completed and with which txHash.

### Impact Explanation
What is misreported: the `(status, txHash)` pair returned to the integrator for a specific `WithdrawalIdentifier.index` in a multi-withdrawal intent. If an integrator maintains an internal mapping of `index -> user/destinationAddress` (which is the documented purpose of the `index` field) and credits/marks-complete based on the `txHash` returned for that index, it can attribute the wrong `txHash`/completion event to the wrong user when two withdrawals of the same token exist in the same batch. This matches the "High" category: "a status or hash misreport making an integrator credit or refund twice." The underlying on-chain transfer amounts and destinations are correct (funds are not stolen from the contract), but the SDK-reported completion record used for reconciliation/crediting can be wrong — repeatable on every intent containing ≥2 same-asset PoA withdrawals to different addresses.

### Likelihood Explanation
Preconditions: an intent (attacker- or user-constructed via any integrator that forwards `withdrawalParams`) containing two or more PoA-bridge withdrawals of the same `assetId` to different `destinationAddress`es in a single NEAR tx, combined with the PoA bridge API returning withdrawal records not in submission order (explicitly documented behavior, not a hypothetical). No special privileges are needed — any ordinary user/integrator can construct a batch withdrawal with duplicate-asset entries, since nothing in `supports()` or `validateWithdrawal()` rejects duplicate assetIds within one intent. This is deterministically reproducible whenever the two conditions co-occur.

### Recommendation
Disambiguate withdrawal records by more than `assetId` — e.g., match by `(near_token_id, destination_address)` if the API exposes destination address per record, or track amounts (as the code comment itself suggests: sort both the API's withdrawal list and the locally submitted `withdrawalParams` by amount for the same asset, since relayer fees are equal for same-token withdrawals so relative amount ordering is preserved) instead of relying on unsorted array position. Until the API provides a stable/unique key, `supports()`/`validateWithdrawal()` should reject or the SDK should refuse batches containing duplicate `assetId` PoA withdrawals to prevent unreliable status reporting.

### Proof of Concept
```ts
// vitest test plan (mocks poaBridge.httpClient.getWithdrawalStatus only)

it("misattributes txHash between two same-asset withdrawals with different destinations", async () => {
  const assetId = "nep141:zec.omft.near";
  const tx = { hash: "shared-tx-hash", accountId: "acc" };

  const withdrawalA = {
    status: "COMPLETED",
    data: { near_token_id: "zec.omft.near", transfer_tx_hash: "0xAAA...", /* destination A */ },
  };
  const withdrawalB = {
    status: "COMPLETED",
    data: { near_token_id: "zec.omft.near", transfer_tx_hash: "0xBBB...", /* destination B */ },
  };

  // API returns records out of submission order: [B, A]
  vi.spyOn(poaBridge.httpClient, "getWithdrawalStatus")
    .mockResolvedValue({ withdrawals: [withdrawalB, withdrawalA] });

  const bridge = new PoaBridge({ envConfig, xrplRpcUrls: [] });

  const widIndex0 = bridge.createWithdrawalIdentifier({
    withdrawalParams: { assetId, destinationAddress: "addressA", amount: 100n, /* ... */ },
    index: 0,
    tx,
  });

  const result = await bridge.describeWithdrawal({ ...widIndex0 });

  // EXPECTED (equality that should hold): result.txHash === withdrawalA.data.transfer_tx_hash ("0xAAA...")
  // ACTUAL (bug): result.txHash === withdrawalB.data.transfer_tx_hash ("0xBBB...")
  expect(result).toEqual({ status: "completed", txHash: "0xBBB..." }); // demonstrates mismatch vs index-0 → addressA expectation
});
```
This confirms `describeWithdrawal(index:0)`, intended to report the outcome for the withdrawal to `addressA`, instead returns the `txHash` belonging to the withdrawal destined for `addressB`, purely due to array order in the (documented-as-unsorted) API response and the assetId-only match in `findMatchingWithdrawal`.

### Citations

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
