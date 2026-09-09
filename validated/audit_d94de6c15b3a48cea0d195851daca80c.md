Based on the code review, this is a confirmed vulnerability, explicitly acknowledged as a known limitation in the code comment itself.### Title
Same-token batch withdrawals via PoaBridge cause status/txHash misreporting between recipients - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts)

### Summary
`PoaBridge.describeWithdrawal()` resolves each withdrawal's status via `findMatchingWithdrawal()`, which matches purely by `assetId` (`nep141:${w.data.near_token_id} === assetId`) using `Array.find()`, ignoring `WithdrawalIdentifier.index`. When a batch intent contains two or more POA withdrawals of the same token to different destinations, both `watchWithdrawal` calls query the same NEAR tx hash and receive the same withdrawals list, and both resolve to the identical (status, txHash) — the first matching record — breaking the guarantee that each withdrawal's reported outcome corresponds to its own on-chain result.

### Finding Description
The equality that must hold is: `describeWithdrawal(wid_i).txHash == on-chain outcome of withdrawal_i` for every `i` in a batch. In `poa-bridge.ts`:

- `describeWithdrawal` (lines 313-343) calls `getWithdrawalStatusWithRetry(args)` which calls `poaBridge.httpClient.getWithdrawalStatus({ withdrawal_hash: args.tx.hash }, ...)` [1](#0-0) . `args.tx.hash` is the shared NEAR intent transaction hash for the whole batch, so both withdrawal 0 and withdrawal 1 make an identical request and get back the identical `response.withdrawals` array.
- `findMatchingWithdrawal` then selects a record purely by `nep141:${w.data.near_token_id} === assetId`, via `Array.prototype.find`, which returns only the *first* match [2](#0-1) . The `index` field of `WithdrawalIdentifier` is never consulted in this matching logic, and the function's own doc comment openly admits the limitation: "multiple withdrawals of the same token in a single transaction are not supported" [3](#0-2) .
- `createWithdrawalIdentifier` (lines 295-311) does correctly assign a per-route `index`, and `createWithdrawalIdentifiers` in `withdrawal-watcher.ts` maintains "separate index counters per bridge route" [4](#0-3) , confirming that a batch with two same-asset PoA withdrawals produces `wid0.index=0` and `wid1.index=1` — but `describeWithdrawal` never uses that index to disambiguate.
- `watchWithdrawal` (in `withdrawal-watcher.ts`) polls `bridge.describeWithdrawal({...args.wid, ...})` per wid independently and resolves to `{hash: status.txHash}` on `"completed"` [5](#0-4) . Both promises created via `sdk.createWithdrawalCompletionPromises` for indices 0 and 1 will independently converge on the same underlying withdrawal record whenever both have the same `assetId`, so both `watchWithdrawal(wid0)` and `watchWithdrawal(wid1)` return the identical `{hash}`.

None of the existing guards (`validateAddress`, `compareAddresses`, `validateWithdrawal`, `supports()`, sanity `assert`s) address this — they operate on withdrawal creation/validation, not on the status-matching step, and the intents contract's own signature/nonce checks are irrelevant here since this is purely an off-chain status-reporting bug in the SDK, not an on-chain execution issue.

### Impact Explanation
An integrator using `sdk.waitForWithdrawalCompletion`/`createWithdrawalCompletionPromises` with a batch of ≥2 same-token PoA withdrawals to different destination addresses will receive the same `txHash` for both, even though the underlying PoA transfers went to different addresses with different amounts. This can cause an integrator to credit or refund a user based on the wrong transaction hash — matching the "High" severity category of "a status or hash misreport making an integrator credit or refund twice." The root cause is entirely within this repo's `poa-bridge.ts`; it does not require a malicious relayer or bridge API — an ordinary user submitting a normal batch withdrawal (all user-authored input) triggers it. Repeatable on every batch containing duplicate `assetId` POA withdrawals.

### Likelihood Explanation
Preconditions: a single intent batch withdrawal with two or more POA-bridge-routed withdrawals sharing the same `assetId` but different `destinationAddress`/`amount`. Nothing prevents an ordinary user/integrator from constructing such a batch — `supports()`/`validateWithdrawal()` validate each withdrawal individually and do not reject duplicate assetIds across the batch. Attacker cost is nil: this is simply normal usage of the public batch-withdrawal API with intentionally duplicated `assetId`. Fully repeatable on demand.

### Recommendation
Fix `findMatchingWithdrawal` to disambiguate using more than `assetId` — e.g., match by `assetId` plus `destinationAddress`/`amount` (and destination chain), or use the POA API's per-withdrawal ordering/index if available, sorting both local withdrawal params and API results by `(assetId, amount)` as suggested in the code's own comment. At minimum, add a check that if multiple withdrawals with the same `assetId` exist in a batch, disambiguate deterministically before returning per-index status, and add a regression test covering same-token batch withdrawals.

### Proof of Concept
```ts
// packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (new test)
it("misreports status when batch has two same-asset withdrawals to different destinations", async () => {
  vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
    withdrawals: [
      {
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "dest-tx-hash-A", // belongs to destinationAddress A
          chain: "btc",
          defuse_asset_identifier: "nep141:btc.omft.near",
          near_token_id: "btc.omft.near",
          decimals: 8, amount: 100,
          account_id: "test.near",
          address: "addrA",
          created: "2024-01-01T00:00:00Z",
        },
      },
      {
        status: "COMPLETED",
        data: {
          tx_hash: "near-tx-hash",
          transfer_tx_hash: "dest-tx-hash-B", // belongs to destinationAddress B
          chain: "btc",
          defuse_asset_identifier: "nep141:btc.omft.near",
          near_token_id: "btc.omft.near",
          decimals: 8, amount: 200,
          account_id: "test.near",
          address: "addrB",
          created: "2024-01-01T00:00:00Z",
        },
      },
    ],
  });

  const bridge = new PoaBridge({
    envConfig: configsByEnvironment.production,
    xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
  });

  const commonTx = { hash: "near-tx-hash", accountId: "test.near" };

  const result0 = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin,
    index: 0,
    withdrawalParams: {
      assetId: "nep141:btc.omft.near",
      amount: 100n,
      destinationAddress: "addrA",
      feeInclusive: false,
    },
    tx: commonTx,
  });

  const result1 = await bridge.describeWithdrawal({
    landingChain: Chains.Bitcoin,
    index: 1,
    withdrawalParams: {
      assetId: "nep141:btc.omft.near",
      amount: 200n,
      destinationAddress: "addrB",
      feeInclusive: false,
    },
    tx: commonTx,
  });

  // BUG: both resolve to the same first-matched withdrawal (dest-tx-hash-A),
  // even though result1 should reflect dest-tx-hash-B for addrB.
  expect(result0).toEqual({ status: "completed", txHash: "dest-tx-hash-A" });
  expect(result1).toEqual({ status: "completed", txHash: "dest-tx-hash-A" }); // WRONG: should be "dest-tx-hash-B"
  expect(result0).toEqual(result1); // demonstrates the broken STATUS TRUTH equality
});
```
This test mocks only the HTTP layer (`poaBridge.httpClient.getWithdrawalStatus`) and demonstrates that `describeWithdrawal` for `index:1`/`destinationAddress:"addrB"` incorrectly returns the txHash belonging to `index:0`/`destinationAddress:"addrA"`.

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L345-358)
```typescript
	private async getWithdrawalStatusWithRetry(
		args: WithdrawalIdentifier & { logger?: ILogger },
	): Promise<WithdrawalStatusResponse> {
		const startTime = Date.now();

		while (true) {
			try {
				return await poaBridge.httpClient.getWithdrawalStatus(
					{ withdrawal_hash: args.tx.hash },
					{
						baseURL: this.getPoaBridgeBaseURL(),
						logger: args.logger,
					},
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
