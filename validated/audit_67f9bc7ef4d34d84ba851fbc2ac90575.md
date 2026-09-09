Confirmed: no deduplication or validation exists anywhere in `createWithdrawalIdentifiers` [1](#0-0)  or in `PoaBridge.describeWithdrawal` [2](#0-1)  that prevents two withdrawals with the same `assetId` in one intent, and `findMatchingWithdrawal` matches purely by `assetId`/`near_token_id`, ignoring `index` and `destinationAddress` entirely [3](#0-2) .

### Title
Same-assetId withdrawals in one intent collapse to the same POA status/txHash, breaking STATUS TRUTH - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`findMatchingWithdrawal` in `poa-bridge.ts` matches a POA bridge withdrawal record only by `nep141:${near_token_id} === assetId`, with no use of `index` or `destinationAddress`. When a single intent contains two withdrawals of the same PoA-bridged asset, `describeWithdrawal({index:0,...})` and `describeWithdrawal({index:1,...})` both resolve against `.find()`'s first match, so `watchWithdrawal` reports withdrawal 1 as completed with withdrawal 0's `transfer_tx_hash`. The bug is explicitly acknowledged in the code's own comment as unhandled.

### Finding Description
The claimed invariant is `(status_i, txHash_i) == outcome_i` for each withdrawal `i` in a batch. Trace:
- `createWithdrawalIdentifiers` assigns `WithdrawalIdentifier.index` per bridge route counter, with no check for duplicate `assetId` within the same route [4](#0-3) .
- `watchWithdrawal` calls `bridge.describeWithdrawal({...wid, ...})` independently per index, polling until `completed`/`failed` [5](#0-4) .
- `PoaBridge.describeWithdrawal` calls `findMatchingWithdrawal(response.withdrawals, args.withdrawalParams.assetId)`, explicitly commenting "Response list is unsorted, so we match by assetId instead of index" [6](#0-5) .
- `findMatchingWithdrawal` does `withdrawals.find((w) => \`nep141:${w.data.near_token_id}\` === assetId)` — the FIRST matching entry, regardless of `destinationAddress`, `amount`, or `index` [7](#0-6) .
- The function's own docstring states: "NOTE: Currently only matches by assetId. This means multiple withdrawals of the same token in a single transaction are not supported. POA API doesn't currently support this case either." [8](#0-7) 
- The test suite confirms matching is index-agnostic across *different* assets ("matches withdrawal by assetId, not by index") but there is no test, guard, or code path handling two entries sharing the same `assetId` [9](#0-8) .

Attacker input: submit one intent with two `nep141:btc.omft.near` withdrawal intents to different `destinationAddress`. When both land on the POA bridge and the bridge processes withdrawal 0 to completion while withdrawal 1 is still pending, `describeWithdrawal(index:1)` will still hit `.find()` and return the completed entry for the withdrawal-0 asset match (since `.find()` returns the first COMPLETED entry with matching `near_token_id`, irrespective of which physical withdrawal it corresponds to). Both `describeWithdrawal(index:0)` and `describeWithdrawal(index:1)` return identical `{status:"completed", txHash: transfer_tx_hash}` even if withdrawal 1's own on-chain transfer has not happened.

No existing guard (`supports()`, `createWithdrawalIdentifier`, `validateAddress`, contract-level checks) prevents an ordinary user from constructing this intent, and no dedup/sort-by-amount logic (mentioned as a future TODO in the comment) currently exists to disambiguate same-asset withdrawals.

### Impact Explanation
An integrator polling per-index withdrawal completion via `watchWithdrawal`/`createWithdrawalCompletionPromises` will receive a `completed` status and `txHash` for withdrawal 1 that actually belongs to withdrawal 0's on-chain transfer. This is a status/hash misreport that can cause the integrator to credit or release funds for withdrawal 1 (to its own destination address) as if it landed, when it may still be pending or could ultimately go to a different destination address, or double-credit using the same `txHash` for two logically distinct withdrawals. This matches the High severity category: "a status or hash misreport making an integrator credit or refund twice."

### Likelihood Explanation
Preconditions: attacker just needs to submit one intent containing two withdrawal legs of the same PoA-bridged `assetId` (e.g., two `nep141:btc.omft.near` withdrawals to different addresses) — a normal, permissionless operation requiring no special privilege, cost, or timing beyond ordinary intent construction. This is fully attacker-controlled and repeatable on every such intent. The condition happens automatically for any batch withdrawal of the same PoA token; no cooperation from a relayer/bridge admin is needed.

### Recommendation
Disambiguate `findMatchingWithdrawal` results per withdrawal index, e.g., by tracking indices already consumed by prior calls (stateful matching), or by matching on the tuple `(assetId, destinationAddress, amount)`; alternatively, sort the response entries by amount to align with the sorted order of the original withdrawal params (as the code's own comment already suggests) and consume matches without replacement across concurrent `describeWithdrawal` calls for the same tx.

### Proof of Concept
```ts
// poa-bridge.test.ts
it("BUG: describeWithdrawal collapses two same-assetId withdrawals to the same entry", async () => {
  vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "withdrawal-0-tx-hash", // belongs to withdrawal index 0
          chain: "btc",
          defuse_asset_identifier: "nep141:btc.omft.near",
          near_token_id: "btc.omft.near",
          decimals: 8,
          amount: 100000,
          account_id: "test.near",
          address: "addr-0",
          created: "2024-01-01T00:00:00Z",
        },
      },
      // withdrawal index 1's own entry is still PENDING or not yet indexed
    ],
  });

  const bridge = new PoaBridge({ envConfig: configsByEnvironment.production, xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}) });

  const result0 = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin, index: 0,
    withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 100000n, destinationAddress: "addr-0", feeInclusive: false },
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  });

  const result1 = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin, index: 1,
    withdrawalParams: { assetId: "nep141:btc.omft.near", amount: 50000n, destinationAddress: "addr-1", feeInclusive: false },
    tx: { hash: "near-tx-hash", accountId: "test.near" },
  });

  // Both sides of the claimed equality (status_i, txHash_i) == outcome_i
  expect(result0).toEqual({ status: "completed", txHash: "withdrawal-0-tx-hash" });
  // BUG: result1 should NOT equal result0's outcome, since withdrawal 1 (addr-1) never landed.
  expect(result1).toEqual({ status: "completed", txHash: "withdrawal-0-tx-hash" }); // incorrectly reported as completed
});
```

### Citations

**File:** packages/intents-sdk/src/core/withdrawal-watcher.ts (L20-53)
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

					if (status.status === "failed") {
						throw new WithdrawalFailedError(status.reason);
					}

					return POLL_PENDING;
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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L1054-1111)
```typescript

```
