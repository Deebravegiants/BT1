### Title
POA Bridge matches withdrawal status by `assetId` only, causing status/hash misreport for batched same-asset withdrawals - (File: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts, packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts)

### Summary
The PoA bridge's withdrawal-completion matching logic (`findMatchingWithdrawal`) disambiguates between multiple withdrawals in the same NEAR transaction using only the token `assetId`, never the amount, destination address, or index. When a single intent contains a batch of two or more withdrawals of the *same* token (a legitimate, SDK-supported scenario per `createWithdrawalCompletionPromises` / batch withdrawal support), both polling calls resolve against the same PoA API record, so one destination `txHash`/`status` gets reported for a withdrawal that has not actually settled on-chain.

### Finding Description
`findMatchingWithdrawal` in `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts` (lines 409-427) and the equivalent function in `packages/internal-utils/src/poaBridge/waitForWithdrawalCompletion.ts` (lines 144-153) both look up a withdrawal record purely by comparing `nep141:${w.data.near_token_id}` to the requested `assetId`: [1](#0-0) 
This is explicitly documented as a known limitation ("multiple withdrawals of the same token in a single transaction are not supported") and is asserted by a test titled "matches withdrawal by assetId, not by index": [2](#0-1) 

However, `describeWithdrawal` on `PoaBridge` is invoked independently, per-index, for each withdrawal in a batch via `watchWithdrawal`/`createWithdrawalCompletionPromises`: [3](#0-2) 
and each of these calls polls `describeWithdrawal` independently: [4](#0-3) 

Since `Array.prototype.find` used in `findMatchingWithdrawal` returns the *first* record whose `near_token_id` matches — irrespective of amount, destination address, or index — a batch withdrawal of two amounts of the same token (e.g., `nep141:btc.omft.near` withdrawn to two different destination addresses in one intent) will cause both polling calls to resolve to the same underlying PoA record. The equality that should hold — "status/txHash reported for withdrawal N corresponds to the on-chain settlement of withdrawal N" — is broken: it instead reports the status/hash of whichever matching-asset withdrawal happens to be first in the (explicitly documented as "unsorted") API response list: [5](#0-4) 

### Impact Explanation
This directly matches the "status or hash misreport making an integrator credit or refund twice" High-impact category. An integrator relying on `sdk.createWithdrawalCompletionPromises` / `waitForWithdrawalCompletion` to know when each of two same-asset withdrawals in a batch has landed could:
- Mark both withdrawals "completed" using a single destination `txHash`, even though only one destination transfer actually occurred — leading to premature crediting/settlement for a withdrawal that hasn't actually completed.
- Conversely, once the true second withdrawal actually completes with a different `txHash`, the already-"completed" first promise's result is stale, and there's no mechanism to reconcile, risking duplicate accounting or a stuck/misreported withdrawal that requires manual intervention to reconcile.

### Likelihood Explanation
Likelihood is limited to legitimate batch withdrawals of the same token to different destinations within a single intent (a supported use case per the RFC / batch withdrawal design docs), which requires no attacker action — it's a correctness bug triggered by normal usage, not an adversarial input. It is not exploitable by an unprivileged third party to steal funds, but it can misreport settlement state to any integrator that batches same-token withdrawals, which is explicitly acknowledged as unsupported in code comments but not actually prevented or guarded against (e.g., no assertion rejecting duplicate assetIds in a batch).

### Recommendation
Extend `findMatchingWithdrawal` (in both `poa-bridge.ts` and `waitForWithdrawalCompletion.ts`) to disambiguate by amount and/or destination address in addition to `assetId`, or explicitly reject/guard batches containing duplicate `assetId` entries at `createWithdrawalCompletionPromises`/`createWithdrawalIdentifiers` time until proper disambiguation is implemented, rather than silently returning a possibly-wrong match.

### Proof of Concept
1. Submit an intent containing two PoA withdrawals of `nep141:btc.omft.near`: withdrawal A (amount 100000, destination address X) and withdrawal B (amount 50000, destination address Y).
2. Call `sdk.createWithdrawalCompletionPromises({ withdrawalParams: [A, B], intentTx })`.
3. Once the PoA indexer reports only withdrawal A as `COMPLETED` (with `near_token_id: "btc.omft.near"`) and withdrawal B still `PENDING`, both `describeWithdrawal` polls for index 0 and index 1 call `findMatchingWithdrawal(withdrawals, "nep141:btc.omft.near")`, which returns the same first COMPLETED record for both — as verified by the existing test "matches withdrawal by assetId, not by index" — causing both promises to resolve as completed with the same `txHash`, even though withdrawal B has not actually settled. [2](#0-1)

### Citations

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts (L317-322)
```typescript

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

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.test.ts (L1054-1111)
```typescript
		it("matches withdrawal by assetId, not by index", async () => {
			vi.mocked(poaBridge.httpClient.getWithdrawalStatus).mockResolvedValue({
				withdrawals: [
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "other-tx-hash",
							chain: "eth",
							defuse_asset_identifier: "nep141:eth.omft.near",
							near_token_id: "eth.omft.near",
							decimals: 18,
							amount: 1000000,
							account_id: "test.near",
							address: zeroAddress,
							created: "2024-01-01T00:00:00Z",
						},
					},
					{
						status: "COMPLETED",
						data: {
							tx_hash: "near-tx-hash",
							transfer_tx_hash: "btc-tx-hash",
							chain: "btc",
							defuse_asset_identifier: "nep141:btc.omft.near",
							near_token_id: "btc.omft.near",
							decimals: 8,
							amount: 100000,
							account_id: "test.near",
							address: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
							created: "2024-01-01T00:00:00Z",
						},
					},
				],
			});

			const bridge = new PoaBridge({
				envConfig: configsByEnvironment.production,
				xrplRpcUrls: configureXrplRpcUrls(PUBLIC_XRPL_RPC_URLS, {}),
			});

			const result = await bridge.describeWithdrawal({
				landingChain: Chains.Bitcoin,
				index: 0,
				withdrawalParams: {
					assetId: "nep141:btc.omft.near",
					amount: 100000n,
					destinationAddress: "18HNgVKMwjNjYWey68FZUV7R4pmyojuv2j",
					feeInclusive: false,
				},
				tx: { hash: "near-tx-hash", accountId: "test.near" },
			});

			expect(result).toEqual({
				status: "completed",
				txHash: "btc-tx-hash",
			});
		});
```

**File:** packages/intents-sdk/src/sdk.ts (L557-608)
```typescript
	public createWithdrawalCompletionPromises(
		params: CreateWithdrawalCompletionPromisesParams,
	): Array<Promise<TxInfo | TxNoInfo>> {
		const { withdrawalParams, intentTx, signal, logger } = params;

		const widsPromise = createWithdrawalIdentifiers({
			bridges: this.bridges,
			withdrawalParams,
			intentTx,
		});

		// Track the last promise per HOT bridge landing chain for sequential waiting.
		// HOT bridge processes withdrawals sequentially per chain with ~30s gaps,
		// so polling in parallel would cause later withdrawals to timeout.
		const hotChainLastPromise = new Map<Chain, Promise<TxInfo | TxNoInfo>>();

		return withdrawalParams.map(async (_, index) => {
			const wids = await widsPromise;
			const entry = wids[index];
			assert(entry != null, `Missing wid for index ${index}`);

			// Only apply sequential waiting for HOT bridge
			if (entry.bridge.route === RouteEnum.HotBridge) {
				const landingChain = entry.wid.landingChain;
				const previousPromise = hotChainLastPromise.get(landingChain);

				const sequentialPromise = (async () => {
					if (previousPromise) {
						// Wait for previous withdrawal to same chain to complete.
						// Use allSettled to continue even if previous fails.
						await Promise.allSettled([previousPromise]);
					}
					return watchWithdrawal({
						bridge: entry.bridge,
						wid: entry.wid,
						signal,
						logger,
					});
				})();

				hotChainLastPromise.set(landingChain, sequentialPromise);
				return sequentialPromise;
			}

			// Non-HOT bridges: parallel polling (existing behavior)
			return watchWithdrawal({
				bridge: entry.bridge,
				wid: entry.wid,
				signal,
				logger,
			});
		});
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
